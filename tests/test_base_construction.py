"""Construction from Jung poles, independently checked against primary tables."""
from itertools import permutations, product
from pathlib import Path
import sys
import unittest

import test_base_hadamard as primary
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_model_a as construction

BASE = Path(__file__).resolve().parents[1] / 'formalization' / 'base'

class JungConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        primary.BaseHadamardTests.setUpClass()
        cls.data = primary.BaseHadamardTests

    def test_signature_inputs_match_primary_carriers(self):
        for aspect, signature in construction.ASPECT_SIGNATURES.items():
            self.assertEqual(signature, tuple(self.data.aspect_rows[aspect][j] for j in (1, 6, 3)))
        for f, signature in construction.FUNCTION_SIGNATURES.items():
            self.assertEqual(signature, tuple(self.data.function_rows[f][j] for j in (1, 6, 3)))
        self.assertEqual(set(construction.ASPECT_SIGNATURES), set(primary.ASPECTS))
        self.assertEqual(set(construction.FUNCTION_SIGNATURES.values()), set(product((0, 1), repeat=3)))

    def test_all_sixteen_models_are_built_without_model_table_input(self):
        results = set()
        for name in primary.TYPES:
            profile = tuple(self.data.trait_rows[name][j] for j in (1, 14, 3, 7))
            model = construction.construct(*profile)
            expected = {a: f for f, a in enumerate(self.data.model_rows[name], 1)}
            self.assertEqual(model, expected, name)
            results.add(tuple(model[a] for a in primary.ASPECTS))
        self.assertEqual(len(results), 16)
        profiles = {tuple(row[j] for j in (1, 14, 3, 7)) for row in self.data.trait_rows.values()}
        self.assertEqual(profiles, set(product((0, 1), repeat=4)))
        # The four code columns generate every H16 column under XNOR.
        columns = list(zip(*(self.data.trait_rows[name] for name in primary.TYPES)))
        generated = set()
        for mask in product((0, 1), repeat=4):
            generated.add(tuple((1 + sum(mask[k] * (1 - row[j])
                                         for k, j in enumerate((1, 14, 3, 7)))) % 2
                                for row in (self.data.trait_rows[name] for name in primary.TYPES)))
        self.assertEqual(generated, set(columns))
        self.assertEqual(construction.construct(1, 0, 1, 0)['ЧЭ'], 1)

    def test_exhaustive_bijections_satisfy_one_solution_per_profile(self):
        counts = {p: 0 for p in product((0, 1), repeat=4)}
        candidates = 0
        for perm in permutations(range(1, 9)):
            candidates += 1
            # Derive four uniform poles directly from the PRIMARY carrier tables.
            values = [set(), set(), set(), set()]
            for a, f in zip(primary.ASPECTS, perm):
                ar, fr = self.data.aspect_rows[a], self.data.function_rows[f]
                values[0].add(int(ar[1] == fr[1]))
                values[1].add(int(ar[6] == fr[6]))
                values[2 if ar[6] == 1 else 3].add(int(ar[3] == fr[3]))
            if all(len(v) == 1 for v in values):
                profile = tuple(next(iter(v)) for v in values)
                counts[profile] += 1
                actual = tuple(construction.construct(*profile)[a] for a in primary.ASPECTS)
                self.assertEqual(perm, actual)
        self.assertEqual(candidates, 40320)
        self.assertEqual(set(counts.values()), {1})

    def test_chapter_records_the_full_basis_and_construction(self):
        text = (BASE / '04-jung-basis-construction.md').read_text(encoding='utf-8')
        for formula in (r'v=\operatorname{vert}(t)', r'n=\operatorname{nal}(t)',
                        r'u=\partial_4^{T}(t)', r'l=\partial_8^{T}(t)',
                        r'\partial_4^{F}(t(i))', r'\partial_7^{I}(i)=1',
                        r'\partial_7^{I}(i)=0'):
            self.assertIn(formula, text)
        self.assertIn('существует ровно одна биекция', text)
        self.assertIn('| ЧЭ | 1 | 1 | 1 | 1 |', text)
        def table_after(header):
            records = []
            for line in text.split(header, 1)[1].splitlines():
                if not line.strip() or line.startswith('|---'):
                    continue
                if not line.startswith('|'):
                    break
                records.append([cell.strip() for cell in line.strip('|').split('|')])
            return records
        aspect_header = r'| Аспект $i$ | $\partial_2^{I}(i)$ | $\partial_7^{I}(i)$ | $\partial_4^{I}(i)$ |'
        function_header = r'| Позиция $f$ | $\partial_2^{F}(f)$ — вертность | $\partial_7^{F}(f)$ — нальность | $\partial_4^{F}(f)$ — сила |'
        for rows, signatures, key in (
                (table_after(aspect_header), construction.ASPECT_SIGNATURES, str),
                (table_after(function_header), construction.FUNCTION_SIGNATURES, int)):
            self.assertEqual(len(rows), 8)
            self.assertEqual({key(row[0]): tuple(map(int, row[1:])) for row in rows}, signatures)
        example_header = '| Аспект | Вертность функции | Нальность функции | Сила функции | Позиция |'
        example = table_after(example_header)
        self.assertEqual(len(example), 8)
        model = construction.construct(1, 0, 1, 0)
        for aspect, *values in example:
            signature = tuple(map(int, values[:3]))
            position = int(values[3])
            self.assertEqual(position, model[aspect])
            self.assertEqual(signature, construction.FUNCTION_SIGNATURES[position])

    def test_invalid_poles_are_rejected(self):
        for p in ((2, 0, 0, 0), (1, -1, 0, 1), (0, 1, 0.5, 1)):
            with self.assertRaises(ValueError):
                construction.construct(*p)

if __name__ == '__main__':
    unittest.main()
