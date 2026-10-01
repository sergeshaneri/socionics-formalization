"""Finite checks for the first theoretical slice, using primary tables.

No generated model family is taken as a construction result here.
"""
from itertools import product
from pathlib import Path
import re
import unittest


SOURCE = Path(__file__).resolve().parents[1] / 'sources' / 'primary' / 'markdown таблицы.md'
ASPECTS = ('ЧИ', 'БС', 'ЧЭ', 'БЛ', 'ЧЛ', 'БЭ', 'ЧС', 'БИ')
POSITIONS = (1, 5, 6, 2, 8, 4, 3, 7)
TYPES = ('ИЛЭ', 'СЭИ', 'ЭСЭ', 'ЛИИ', 'ЭИЭ', 'ЛСИ', 'СЛЭ', 'ИЭИ',
         'ЛИЭ', 'ЭСИ', 'СЭЭ', 'ИЛИ', 'ИЭЭ', 'СЛИ', 'ЛСЭ', 'ЭИИ')


class BaseHadamardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aspect_rows = {}
        cls.function_rows = {}
        cls.trait_rows = {}
        cls.model_rows = {}
        for line in SOURCE.read_text(encoding='utf-8-sig').splitlines():
            if not line.lstrip().startswith('|'):
                continue
            cells = [s.strip().replace('\\', '').strip('*').strip()
                     for s in line.strip().strip('|').split('|')]
            label, values = cells[0], cells[1:]
            if label in ASPECTS and len(values) == 8 and set(values) <= {'+', '-'}:
                cls.aspect_rows[label] = tuple(int(v == '+') for v in values)
            match = re.fullmatch(r'\S+ \(([1-8])\)', label)
            if match and len(values) == 8 and set(values) <= {'+', '-'}:
                cls.function_rows[int(match.group(1))] = tuple(int(v == '+') for v in values)
            if label in TYPES and len(values) == 16 and set(values) <= {'0', '1'}:
                cls.trait_rows[label] = tuple(map(int, values))
            if label in TYPES and len(values) == 8 and set(values) == set(ASPECTS):
                cls.model_rows[label] = tuple(values)
        if (set(cls.aspect_rows) != set(ASPECTS)
                or set(cls.function_rows) != set(POSITIONS)
                or set(cls.trait_rows) != set(TYPES)
                or set(cls.model_rows) != set(TYPES)):
            raise ValueError('Primary source must provide all four complete tables')

    def test_sylvester_recursion_matches_all_three_primary_matrices(self):
        matrix = [[1]]
        for n in (2, 4, 8, 16):
            matrix = ([row + row for row in matrix]
                      + [row + [-v for v in row] for row in matrix])
            if n == 8:
                expected_sets = ([self.aspect_rows[a] for a in ASPECTS],
                                 [self.function_rows[p] for p in POSITIONS])
            elif n == 16:
                expected_sets = ([self.trait_rows[t] for t in TYPES],)
            else:
                continue
            binary = [tuple(int(v == 1) for v in row) for row in matrix]
            for expected in expected_sets:
                self.assertEqual(binary, expected)

    def test_orthogonality_of_primary_h8_and_h16(self):
        for rows in ([self.aspect_rows[a] for a in ASPECTS],
                     [self.trait_rows[t] for t in TYPES]):
            n = len(rows)
            for i, j in product(range(n), repeat=2):
                dot = sum((2 * x - 1) * (2 * y - 1) for x, y in zip(rows[i], rows[j]))
                self.assertEqual(dot, n if i == j else 0)

    def test_xnor_row_and_column_closure_with_exact_index_rule(self):
        for rows in ([self.aspect_rows[a] for a in ASPECTS],
                     [self.trait_rows[t] for t in TYPES]):
            n = len(rows)
            columns = list(zip(*rows))
            for values in (rows, columns):
                for i, j in product(range(n), repeat=2):
                    result = tuple(int(a == b) for a, b in zip(values[i], values[j]))
                    self.assertEqual(result, values[i ^ j])

    def test_churyumov_correspondence_and_ile_identity(self):
        for a, p in zip(ASPECTS, POSITIONS):
            self.assertEqual(self.aspect_rows[a], self.function_rows[p])
            self.assertEqual(self.model_rows['ИЛЭ'][p - 1], a)

    def test_component_xnor_identity_all_binary_inputs(self):
        for a, b, u, v in product((0, 1), repeat=4):
            left = int(int(a == b) == int(u == v))
            right = int(int(a == u) == int(b == v))
            self.assertEqual(left, right)

    def test_vert_nality_xnor_gives_tality_on_all_models(self):
        for name in TYPES:
            traits = self.trait_rows[name]
            self.assertEqual(int(traits[1] == traits[14]), traits[15])
            for position, aspect in enumerate(self.model_rows[name], 1):
                a, f = self.aspect_rows[aspect], self.function_rows[position]
                self.assertEqual(int(a[1] == a[6]), a[7])
                self.assertEqual(int(f[1] == f[6]), f[7])
                self.assertEqual(int(a[1] == f[1]), traits[1])
                self.assertEqual(int(a[6] == f[6]), traits[14])
                self.assertEqual(int(a[7] == f[7]), traits[15])

    def test_carefree_judicious_xnor_gives_nality_on_active_domain(self):
        for name in TYPES:
            traits = self.trait_rows[name]
            self.assertEqual(int(traits[2] == traits[12]), traits[14])
            active_positions = []
            for position, aspect in enumerate(self.model_rows[name], 1):
                a, f = self.aspect_rows[aspect], self.function_rows[position]
                self.assertEqual(int(a[2] == a[4]), a[6])
                self.assertEqual(int(f[2] == f[4]), f[6])
                if a[6] == 1:
                    active_positions.append(position)
                    self.assertEqual(int(a[2] == f[2]), traits[2])
                    self.assertEqual(int(a[4] == f[4]), traits[12])
                    self.assertEqual(f[6], traits[14])
            expected_positions = [p for p, row in self.function_rows.items()
                                  if row[6] == traits[14]]
            self.assertEqual(set(active_positions), set(expected_positions))


if __name__ == '__main__':
    unittest.main()
