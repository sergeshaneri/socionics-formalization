"""Exact pair-relation formulas for generation four; no S8 enumeration."""
from itertools import product
from pathlib import Path
import re
import unittest

import test_base_hadamard as primary
import test_base_generations as generations
import test_base_newman as newman

APPENDIX = Path(__file__).resolve().parents[1] / 'formalization' / 'base' / '02a-fourth-generation-algebra.md'
HEADER = r'| $m$ | $\ell$ | $\varepsilon$ | Тройка признаков |'
EXPECTED_SPECS = {
    (5, 1, 1): (4, 5, 8), (5, 1, 0): (3, 6, 8),
    (5, 2, 1): (2, 5, 6), (5, 2, 0): (2, 3, 4),
    (6, 1, 1): ('vert', 'phi', 'rho'),
    (6, 1, 0): ('vert', 'pi', 'omega'),
    (12, 1, 1): ('tal', 'phi', 'pi'),
    (12, 1, 0): ('tal', 'rho', 'omega'),
}


def records(text, header, test):
    test.assertTrue(header in text, f'Missing literal table: {header}')
    result, started = [], False
    for line in text.split(header, 1)[1].splitlines():
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells):
                started = True
            elif started:
                result.append(cells)
        elif started:
            break
    test.assertTrue(result)
    return result


def transpose(matrix):
    return tuple(zip(*matrix))


def matmul(left, right):
    return tuple(tuple(sum(a*b for a, b in zip(row, column))
                       for column in transpose(right)) for row in left)


class BaseFourthAlgebraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generations.BaseGenerationsTests.setUpClass()
        cls.source = generations.BaseGenerationsTests()
        cls.aspects = generations.BaseGenerationsTests.aspects
        cls.functions = generations.BaseGenerationsTests.functions
        cls.traits = generations.BaseGenerationsTests.traits
        cls.models = generations.BaseGenerationsTests.models

    def appendix(self):
        self.assertTrue(APPENDIX.is_file(), 'Strict generation-four appendix is missing')
        return APPENDIX.read_text(encoding='utf-8')

    def specs(self, text):
        result = {}
        for m, layer, epsilon, triple in records(text, HEADER, self):
            key = tuple(map(int, (m, layer, epsilon)))
            values = []
            for value in triple.strip('$').split(','):
                value = value.strip().replace('\\operatorname{', '').replace('}', '').replace('\\', '')
                values.append(int(value) if value.isdigit() else value)
            self.assertNotIn(key, result)
            result[key] = tuple(values)
        self.assertEqual(result, EXPECTED_SPECS)
        return result

    def relation(self, triple, carrier, poles):
        points = primary.ASPECTS if carrier == 0 else tuple(range(1, 9))
        classic = self.aspects if carrier == 0 else self.functions
        def bit(name, point):
            return classic[point][name-1] if isinstance(name, int) else int(point in poles[name][carrier])
        return tuple(tuple(int(x != y and all(bit(name, x) == bit(name, y) for name in triple))
                           for y in points) for x in points)

    def partition_relation(self, blocks, points):
        return tuple(tuple(int(x != y and any(x in b and y in b for b in blocks))
                           for y in points) for x in points)

    def model_matrix(self, model):
        # Rows are functional positions 1..8; columns are named aspects.
        return tuple(tuple(int(model[a] == f) for a in primary.ASPECTS) for f in range(1, 9))

    def test_pair_matrices_match_full_literal_schemes_both_poles(self):
        text = self.appendix()
        self.assertIn(r'P_t(f,i)=', text)
        self.assertIn(r'P_tR^I_{m,\ell,\varepsilon}P_t^{\mathsf T}', text)
        self.assertIn(r'R^F_{m,\ell,\varepsilon\odot p}', text)
        self.assertIn(r'L_5=\{1,2\}', text)
        self.assertIn(r'L_6=L_{12}=\{1\}', text)
        specs = self.specs(text)
        poles = newman.literal_tables(self)
        literal = {5: self.source.table('| Тройка столбцов Аспектона и Функциона | Аспектные пары | Функциональные пары при полюсе 1 | Функциональные пары при полюсе 0 |')}
        header = '| Аспектные пары | Функциональные пары при полюсе 1 | Функциональные пары при полюсе 0 |'
        for m, section in [(6, '### Позитивизм/негативизм'), (12, '### Квестимность/деклатимность')]:
            literal[m] = self.source.table(header, section)
        relations = {}
        legacy = {}
        for (m, layer, epsilon), triple in specs.items():
            row = literal[m][2*(layer-1) + (1-epsilon)]
            a, pos, neg = row[-3:]
            aa = self.source.partition(a, aspect=True)
            fp = self.source.partition(pos)
            fn = self.source.partition(neg)
            ri = self.relation(triple, 0, poles)
            rf = self.relation(triple, 1, poles)
            self.assertEqual(ri, self.partition_relation(aa, primary.ASPECTS))
            self.assertEqual(rf, self.partition_relation(fp, tuple(range(1, 9))))
            self.assertTrue(all(sum(row) == 1 for row in ri))
            self.assertTrue(all(sum(row) == 1 for row in rf))
            self.assertEqual(ri, transpose(ri))
            self.assertEqual(rf, transpose(rf))
            relations[m, layer, epsilon] = (ri, rf)
            legacy[m, layer, epsilon] = (aa, fp, fn)
        for key, (_, _, fn) in legacy.items():
            m, layer, epsilon = key
            self.assertEqual(relations[m, layer, 1-epsilon][1],
                             self.partition_relation(fn, tuple(range(1, 9))))
        for name, model in self.models.items():
            pt = self.model_matrix(model)
            self.assertEqual(matmul(pt, transpose(pt)), tuple(tuple(int(i == j) for j in range(8)) for i in range(8)))
            for m, p in product((5, 6, 12), (0, 1)):
                keys = [key for key in relations if key[0] == m]
                matrix_holds = all(matmul(matmul(pt, relations[key][0]), transpose(pt))
                                   == relations[m, key[1], int(key[2] == p)][1] for key in keys)
                partition_holds = all(self.source.images(model, legacy[key][0])
                                      == legacy[key][1 if p else 2] for key in keys)
                self.assertEqual(matrix_holds, partition_holds, (name, m, p))
                self.assertEqual(matrix_holds, self.traits[name][m-1] == p, (name, m, p))
    def test_main_chapter_named_triples_match_strict_specification(self):
        text = self.source.text
        header = r'| $m$ | Строка парной схемы | Тройка Гуленко–Ньюмана |'
        rows = records(text, header, self)
        self.assertEqual(len(rows), 4)
        self.assertIn(r'\{t(B):B\in\mathcal P_{I,k}\}=\mathcal P_{F,k,p}', text)
        self.assertIn('02a-fourth-generation-algebra.md', text)
        specs = self.specs(self.appendix())
        actual = {}
        for m, k, triple in rows:
            key = (int(m), int(k))
            self.assertNotIn(key, actual)
            values = tuple(v.strip().replace('\\operatorname{', '').replace('}', '').replace('\\', '')
                           for v in triple.strip('$').split(','))
            actual[key] = values
            self.assertEqual(values, specs[int(m), 1, 2-int(k)])
        self.assertEqual(set(actual), {(6, 1), (6, 2), (12, 1), (12, 2)})

    def test_cycle_matrix_matches_complete_cycle_both_poles(self):
        text = self.appendix()
        header = r'| $r$ | Блок аспектов $I_r$ | Блок функций $F_r$ |'
        rows = records(text, header, self)
        self.assertEqual(len(rows), 4)
        self.assertIn(r'P_tC^IP_t^{\mathsf T}=C^F_p', text)
        self.assertIn(r'C^F_0=(C^F)^{\mathsf T}', text)
        ic, fc = [], []
        for r, aa, ff in rows:
            self.assertEqual(int(r), len(ic))
            ic.append(self.source.aspect_set(aa))
            fc.append(frozenset(map(int, re.findall(r'[1-8]', ff))))
        self.assertEqual(tuple(ic), tuple(map(frozenset, [('ЧИ', 'БИ'), ('ЧЛ', 'БЛ'), ('ЧС', 'БС'), ('ЧЭ', 'БЭ')])))
        self.assertEqual(tuple(fc), tuple(map(frozenset, [(1, 7), (2, 8), (3, 5), (4, 6)])))
        for r, signature in enumerate(((1, 1, 1), (1, 0, 0), (0, 0, 1), (0, 1, 0))):
            for blocks, data in [(ic, self.aspects), (fc, self.functions)]:
                self.assertEqual(blocks[r], frozenset(x for x, bits in data.items()
                                                      if tuple(bits[c-1] for c in (4, 6, 7)) == signature))
        def adjacency(blocks, points):
            return tuple(tuple(int(any(x in blocks[r] and y in blocks[(r+1)%4] for r in range(4)))
                               for y in points) for x in points)
        ci = adjacency(ic, primary.ASPECTS)
        cf = adjacency(fc, tuple(range(1, 9)))
        for matrix in (ci, cf):
            self.assertTrue(all(sum(row) == 2 for row in matrix))
            self.assertNotEqual(matrix, transpose(matrix))
        phases = {0: set(), 1: set()}
        for name, model in self.models.items():
            pt = self.model_matrix(model)
            transported = matmul(matmul(pt, ci), transpose(pt))
            images = tuple(frozenset(model[a] for a in b) for b in ic)
            for p in (0, 1):
                target = cf if p else transpose(cf)
                matching_phases = [h for h in range(4)
                                   if all(images[r] == fc[(h + (r if p else -r)) % 4]
                                          for r in range(4))]
                holds = transported == target
                self.assertEqual(holds, bool(matching_phases), (name, p))
                self.assertEqual(holds, self.traits[name][10] == p, (name, p))
                phases[p].update(matching_phases)
        self.assertEqual(phases, {0: set(range(4)), 1: set(range(4))})
        # A concrete non-model bijection can satisfy neither explicit pole.
        outside = dict(self.models['ИЛЭ'])
        outside['ЧИ'], outside['БС'] = outside['БС'], outside['ЧИ']
        self.assertNotIn(outside, self.models.values())
        pt = self.model_matrix(outside)
        transported = matmul(matmul(pt, ci), transpose(pt))
        self.assertNotEqual(transported, cf)
        self.assertNotEqual(transported, transpose(cf))


if __name__ == '__main__':
    unittest.main()
