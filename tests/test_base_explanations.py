"""Regression checks for the clarified explanations and finite correspondence.

Primary model tables remain inputs; no all-bijection reconstruction is claimed.
"""
from functools import reduce
from itertools import product
from pathlib import Path
import re
import unittest

import test_base_hadamard as primary


BASE = Path(__file__).resolve().parents[1] / 'formalization' / 'base'


class BaseExplanationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        primary.BaseHadamardTests.setUpClass()
        cls.data = primary.BaseHadamardTests

    def test_literal_type_relation_code_permutation_table_matches_primary(self):
        text = (BASE / '01-hadamard-and-correspondence.md').read_text(encoding='utf-8')
        header = '| Тип | Отношение относительно ИЛЭ | Код столбцов 1–16 | Образы аспектов в порядке Чурюмова |'
        self.assertIn(header, text, 'The finite type/relation/code/permutation table is missing')
        rows = []
        started = False
        for line in text.split(header, 1)[1].splitlines():
            if line.startswith('|---'):
                started = True
            elif line.startswith('|') and started:
                rows.append([v.strip() for v in line.strip('|').split('|')])
            elif started:
                break
        self.assertEqual(len(rows), 16)
        self.assertEqual([r[0] for r in rows], list(primary.TYPES))
        relations = {}
        for line in primary.SOURCE.read_text(encoding='utf-8-sig').splitlines():
            if not line.lstrip().startswith('|'):
                continue
            cells = [s.strip().replace('\\', '').strip('*').strip()
                     for s in line.strip().strip('|').split('|')]
            if len(cells) == 9 and all(re.fullmatch('[1-8]', v) for v in cells[1:]):
                permutation = tuple(map(int, cells[1:]))
                self.assertNotIn(permutation, relations)
                relations[permutation] = cells[0]
        self.assertEqual(len(relations), 16)
        codes, permutations, labels = set(), set(), set()
        for name, relation, bits, values in rows:
            self.assertRegex(bits, r'^[01]{16}$')
            self.assertEqual(tuple(map(int, bits)), self.data.trait_rows[name])
            model = {aspect: p for p, aspect in enumerate(self.data.model_rows[name], 1)}
            expected = tuple(model[a] for a in primary.ASPECTS)
            actual = tuple(map(int, values.split(',')))
            self.assertEqual(actual, expected)
            self.assertEqual(relation, relations[expected])
            codes.add(bits)
            permutations.add(actual)
            labels.add(relation)
        self.assertEqual(len(codes), 16)
        self.assertEqual(len(permutations), 16)
        self.assertEqual(len(labels), 16)

    def test_technical_material_is_optional_and_separated(self):
        appendix = BASE / '01a-hadamard-technical.md'
        self.assertTrue(appendix.is_file(), 'The explanatory technical appendix is missing')
        technical = appendix.read_text(encoding='utf-8')
        main = (BASE / '01-hadamard-and-correspondence.md').read_text(encoding='utf-8')
        self.assertIn('(01a-hadamard-technical.md)', main)
        self.assertIn('Утверждение H-01', technical)
        self.assertNotIn('Утверждение H-01', main)
        self.assertIn(r'\sigma(a)=2a-1', technical)
        self.assertNotIn(r'\sigma(a)=2a-1', main)
        self.assertIn(r'\lambda(c)', technical)
        self.assertNotIn(r'\lambda(c)', main)

    def test_dependency_and_diad_membership_have_distinct_truth_sets(self):
        signatures = {
            a: tuple(row[c - 1] for c in (3, 5, 7))
            for a, row in self.data.aspect_rows.items()
        }
        self.assertEqual(set(signatures.values()), {(1, 1, 1), (0, 0, 1),
                                                   (1, 0, 0), (0, 1, 0)})
        for signature in signatures.values():
            self.assertEqual(reduce(lambda a, b: int(a == b), signature), 1)
        self.assertEqual(signatures['ЧИ'], (1, 1, 1))
        self.assertEqual(signatures['ЧЛ'], (1, 0, 0))
        self.assertNotEqual(signatures['ЧИ'], signatures['ЧЛ'])
        for a, b in product(primary.ASPECTS, repeat=2):
            comparisons = tuple(int(x == y) for x, y in zip(signatures[a], signatures[b]))
            self.assertEqual(reduce(lambda x, y: int(x == y), comparisons), 1)
            self.assertEqual(all(comparisons), signatures[a] == signatures[b])
        for rows in (self.data.aspect_rows, self.data.function_rows):
            for row in rows.values():
                self.assertEqual(reduce(lambda a, b: int(a == b), row[1:]), 1)

    def test_appendix_index_and_sign_tables_match_primary(self):
        text = (BASE / '01a-hadamard-technical.md').read_text(encoding='utf-8')
        header = '| Номер строки или столбца | Номер минус один | Биты от младшего к старшему |'
        self.assertIn(header, text)
        records = re.findall(r'^\| ([1-8]) \| ([0-7]) \| \$\(([^)]+)\)\$ \|$', text, re.M)
        self.assertEqual(len(records), 8)
        for number, zero_index, bits in records:
            number, zero_index = int(number), int(zero_index)
            self.assertEqual(number - 1, zero_index)
            self.assertEqual(tuple(map(int, bits.split(','))),
                             tuple((zero_index >> j) & 1 for j in range(3)))
        for objects, rows in [(primary.ASPECTS, self.data.aspect_rows),
                              (primary.TYPES, self.data.trait_rows)]:
            n = len(objects)
            m = (n - 1).bit_length()
            for r, obj in enumerate(objects):
                for c in range(n):
                    parity = sum(((r >> j) & 1) * ((c >> j) & 1)
                                 for j in range(m)) % 2
                    self.assertEqual((1 + parity) % 2, rows[obj][c])
                    self.assertEqual((-1) ** parity, 2 * rows[obj][c] - 1)
        sign_records = re.findall(r'^\| ([01]) \| ([01]) \| ([01]) \| (-?1) \|$', text, re.M)
        self.assertEqual(len(sign_records), 4)
        for a, b, xnor, signed in sign_records:
            a, b, xnor, signed = map(int, (a, b, xnor, signed))
            self.assertEqual(xnor, int(a == b))
            self.assertEqual(2 * xnor - 1, signed)
            self.assertEqual((2 * a - 1) * (2 * b - 1), signed)
        self.assertEqual(self.data.aspect_rows['БС'][3], 0)

    def test_complete_condition_system_identifies_each_primary_model(self):
        # Reuse the literal-table parser, not the trait labels as predicate inputs.
        import test_base_generations as generations
        generations.BaseGenerationsTests.setUpClass()
        chapter = generations.BaseGenerationsTests()
        four = chapter.table('| Признак | $m$ в Соционе | $c$ в Аспектоне и Функционе |')
        two = chapter.table('| Признак | $m$ | Тетрахотомия | $n$ | $c$ | Диада полюса 1 | Диада полюса 0 |')
        pair_header = '| Аспектные пары | Функциональные пары при полюсе 1 | Функциональные пары при полюсе 0 |'
        pair_tables = {
            5: chapter.table('| Тройка столбцов Аспектона и Функциона | Аспектные пары | Функциональные пары при полюсе 1 | Функциональные пары при полюсе 0 |'),
            6: chapter.table(pair_header, '### Позитивизм/негативизм'),
            12: chapter.table(pair_header, '### Квестимность/деклатимность'),
        }
        cycle_records = chapter.table('| Значения столбцов 4, 6, 7 | Макроаспект | Полутакт |')
        source_cycle = tuple(chapter.aspect_set(r[1]) for r in cycle_records)
        target_cycle = tuple(frozenset(map(int, re.findall('[1-8]', r[2])))
                             for r in cycle_records)
        truth = {}
        for name, model in chapter.models.items():
            conditions: dict[int, tuple[bool, ...]] = {1: (False, True)}
            for _, trait, column in four:
                trait, column = int(trait), int(column)
                aspects = [{a for a, row in chapter.aspects.items() if row[column - 1] == b}
                           for b in (0, 1)]
                functions = [{f for f, row in chapter.functions.items() if row[column - 1] == b}
                             for b in (0, 1)]
                values = []
                for p in (0, 1):
                    block_holds = all({model[a] for a in aspects[b]}
                                      == functions[int(b == p)] for b in (0, 1))
                    point_holds = all((chapter.aspects[a][column - 1]
                                       == chapter.functions[model[a]][column - 1]) == bool(p)
                                      for a in primary.ASPECTS)
                    self.assertEqual(block_holds, point_holds)
                    values.append(block_holds)
                conditions[trait] = tuple(values)
            for _, trait, _, nality, column, positive, negative in two:
                trait, nality, column = int(trait), int(nality), int(column)
                diads = [chapter.aspect_set(negative), chapter.aspect_set(positive)]
                functions = [{f for f, row in chapter.functions.items() if row[column - 1] == b}
                             for b in (0, 1)]
                values = []
                for p in (0, 1):
                    block_holds = all({model[a] for a in diads[b]}
                                      <= functions[int(b == p)] for b in (0, 1))
                    point_holds = all((chapter.aspects[a][column - 1]
                                       == chapter.functions[model[a]][column - 1]) == bool(p)
                                      for a, row in chapter.aspects.items() if row[6] == nality)
                    self.assertEqual(block_holds, point_holds)
                    values.append(block_holds)
                conditions[trait] = tuple(values)
            for trait, records in pair_tables.items():
                specifications = []
                for record in records:
                    aa, positive, negative = record[-3:]
                    specifications.append((chapter.partition(aa, aspect=True),
                                           chapter.partition(positive),
                                           chapter.partition(negative)))
                conditions[trait] = tuple(
                    all(chapter.images(model, aa) == (positive if p else negative)
                        for aa, positive, negative in specifications)
                    for p in (0, 1))
            images = tuple(frozenset(model[a] for a in block) for block in source_cycle)
            cycle_values = []
            for p in (0, 1):
                target = target_cycle if p else tuple(reversed(target_cycle))
                rotations = {target[k:] + target[:k] for k in range(4)}
                cycle_values.append(images in rotations)
            conditions[11] = tuple(cycle_values)
            self.assertEqual(set(conditions), set(range(1, 17)))
            for c, values in conditions.items():
                bit = chapter.traits[name][c - 1]
                self.assertEqual(values, (bit == 0, bit == 1), (name, c))
            truth[name] = conditions
        for name in primary.TYPES:
            profile = chapter.traits[name]
            matches = [candidate for candidate in primary.TYPES
                       if all(truth[candidate][c][bit]
                              for c, bit in enumerate(profile, 1))]
            self.assertEqual(matches, [name])


if __name__ == '__main__':
    unittest.main()
