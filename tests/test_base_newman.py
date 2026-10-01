"""Check the literal Newman tables, using Model A positional numbering."""
from itertools import product
from pathlib import Path
import re
import unittest

import test_base_hadamard as primary

BASE = Path(__file__).resolve().parents[1] / 'formalization' / 'base'
CHAPTER = BASE / '01b-gulenko-newman.md'
HEADER = '| Признак | Полюс 1 на $I$ | Полюс 0 на $I$ | Полюс 1 на $F$ | Полюс 0 на $F$ |'
# Independent transcription of the elemental sets and the Model A positional
# section of Newman's article; Greek names follow the supplied working note.
EXPECTED = {
    'vert': ({'ЧИ', 'ЧЭ', 'ЧЛ', 'ЧС'}, {1, 3, 6, 8}),
    'nal': ({'ЧИ', 'БС', 'ЧС', 'БИ'}, {1, 3, 5, 7}),
    'tal': ({'ЧИ', 'БЛ', 'БЭ', 'ЧС'}, {1, 2, 3, 4}),
    'phi': ({'ЧИ', 'БС', 'БЛ', 'ЧЛ'}, {1, 2, 5, 8}),
    'rho': ({'ЧИ', 'ЧЛ', 'БЭ', 'БИ'}, {1, 4, 7, 8}),
    'pi': ({'ЧИ', 'ЧЭ', 'БЛ', 'БИ'}, {1, 2, 6, 7}),
    'omega': ({'ЧИ', 'БС', 'ЧЭ', 'БЭ'}, {1, 4, 5, 6}),
}


def literal_tables(test):
    test.assertTrue(CHAPTER.is_file(), 'The Newman base chapter is missing')
    text = CHAPTER.read_text(encoding='utf-8')
    test.assertIn(HEADER, text)
    records = []
    started = False
    for line in text.split(HEADER, 1)[1].splitlines():
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                started = True
            elif started:
                records.append(cells)
        elif started:
            break
    test.assertEqual(len(records), 7)
    poles = {}
    for label, ai, ni, af, nf in records:
        name = label.strip('$').replace('\\operatorname{', '').replace('}', '').replace('\\', '')
        test.assertNotIn(name, poles)
        ap = frozenset(re.findall(r'ЧИ|БС|ЧЭ|БЛ|ЧЛ|БЭ|ЧС|БИ', ai))
        an = frozenset(re.findall(r'ЧИ|БС|ЧЭ|БЛ|ЧЛ|БЭ|ЧС|БИ', ni))
        fp = frozenset(map(int, re.findall(r'[1-8]', af)))
        fn = frozenset(map(int, re.findall(r'[1-8]', nf)))
        test.assertEqual(ap | an, set(primary.ASPECTS))
        test.assertFalse(ap & an)
        test.assertEqual(fp | fn, set(range(1, 9)))
        test.assertFalse(fp & fn)
        test.assertEqual(tuple(map(len, (ap, an, fp, fn))), (4, 4, 4, 4))
        poles[name] = (ap, fp)
    return poles


class BaseNewmanTests(unittest.TestCase):
    def test_literal_newman_system_on_both_carriers(self):
        poles = literal_tables(self)
        self.assertEqual(poles, {k: tuple(map(frozenset, v)) for k, v in EXPECTED.items()})
        primary.BaseHadamardTests.setUpClass()
        data = primary.BaseHadamardTests
        ile = {a: f for f, a in enumerate(data.model_rows['ИЛЭ'], 1)}
        for name, (aspects, functions) in poles.items():
            self.assertEqual(frozenset(ile[a] for a in aspects), functions, name)
        dependencies = [('vert', 'nal', 'tal'), ('phi', 'rho', 'vert'),
                        ('pi', 'omega', 'vert'), ('phi', 'pi', 'tal'),
                        ('rho', 'omega', 'tal'), ('phi', 'omega', 'nal'),
                        ('rho', 'pi', 'nal')]
        for carrier, points, classic in [(0, primary.ASPECTS, data.aspect_rows),
                                         (1, tuple(range(1, 9)), data.function_rows)]:
            vectors = {name: tuple(int(x in pair[carrier]) for x in points)
                       for name, pair in poles.items()}
            vectors['1'] = (1,) * 8
            self.assertEqual(len(set(vectors.values())), 8)
            for a, b in product(vectors.values(), repeat=2):
                self.assertIn(tuple(int(x == y) for x, y in zip(a, b)), vectors.values())
                signed_dot = sum((2*x-1)*(2*y-1) for x, y in zip(a, b))
                self.assertEqual(signed_dot, 8 if a == b else 0)
            for a, b, c in dependencies:
                self.assertEqual(tuple(int(x == y) for x, y in zip(vectors[a], vectors[b])), vectors[c])
            for name, column in [('vert', 2), ('nal', 7), ('tal', 8)]:
                self.assertEqual(vectors[name], tuple(classic[x][column-1] for x in points))
            classical_columns = {tuple(classic[x][c] for x in points) for c in range(8)}
            self.assertEqual(set(vectors.values()) & classical_columns,
                             {vectors[n] for n in ('1', 'vert', 'nal', 'tal')})


if __name__ == '__main__':
    unittest.main()
