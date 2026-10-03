"""Check the literal tables of the generations chapter against primary data.

This checks recognition on the supplied 16 models, not reconstruction.
"""
from itertools import product
from pathlib import Path
import re
import unittest

import test_base_hadamard as primary


CHAPTER = (Path(__file__).resolve().parents[1] / 'formalization' / 'base'
           / '02-generations-and-invariant-formulas.md')


class BaseGenerationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        primary.BaseHadamardTests.setUpClass()
        cls.aspects = primary.BaseHadamardTests.aspect_rows
        cls.functions = primary.BaseHadamardTests.function_rows
        cls.traits = primary.BaseHadamardTests.trait_rows
        cls.models = {
            name: {aspect: p for p, aspect in enumerate(row, 1)}
            for name, row in primary.BaseHadamardTests.model_rows.items()
        }
        cls.text = CHAPTER.read_text(encoding='utf-8')

    def table(self, header, section=None):
        text = self.text
        if section is not None:
            text = text.split(section, 1)[1]
        text = text.split(header, 1)[1]
        lines = text.splitlines()
        result = []
        started = False
        for line in lines:
            if line.startswith('|'):
                cells = [c.strip() for c in line.strip('|').split('|')]
                if all(re.fullmatch(r':?-+:?', c) for c in cells):
                    started = True
                elif started:
                    result.append(cells)
            elif started:
                break
        self.assertTrue(result, header)
        return result

    def aspect_set(self, text):
        return frozenset(re.findall(r'ЧИ|БС|ЧЭ|БЛ|ЧЛ|БЭ|ЧС|БИ', text))

    def partition(self, text, aspect=False):
        blocks = [self.aspect_set(s) if aspect
                  else frozenset(map(int, re.findall(r'[1-8]', s)))
                  for s in text.split(';')]
        self.assertEqual(len(blocks), 4)
        self.assertTrue(all(len(b) == 2 for b in blocks))
        flat = [v for b in blocks for v in b]
        expected = set(primary.ASPECTS) if aspect else set(range(1, 9))
        self.assertEqual(len(flat), len(set(flat)))
        self.assertEqual(set(flat), expected)
        return frozenset(blocks)

    def images(self, model, blocks):
        return frozenset(frozenset(model[a] for a in b) for b in blocks)

    def test_three_feature_diad_classes_match_literal_chapter(self):
        for header, columns in [
            ('| $\\partial_3^{I}$ | $\\partial_5^{I}$ | $\\partial_7^{I}$ | Диада |', (3, 5, 7)),
            ('| $\\partial_4^{I}$ | $\\partial_6^{I}$ | $\\partial_7^{I}$ | Диада |', (4, 6, 7)),
        ]:
            records = self.table(header)
            self.assertEqual(len(records), 4)
            expected = {tuple(map(int, r[:3])): self.aspect_set(r[3]) for r in records}
            actual = {}
            for aspect, values in self.aspects.items():
                signature = tuple(values[c - 1] for c in columns)
                actual.setdefault(signature, set()).add(aspect)
            self.assertEqual({k: frozenset(v) for k, v in actual.items()}, expected)
            for a, b in product(primary.ASPECTS, repeat=2):
                agrees = all(self.aspects[a][c - 1] == self.aspects[b][c - 1]
                             for c in columns)
                same_block = any(a in block and b in block for block in expected.values())
                self.assertEqual(agrees, same_block)

    def test_all_eleven_pointwise_formulas_both_poles(self):
        four = self.table('| Признак | $m$ в Соционе | $c$ в Аспектоне и Функционе |')
        two = self.table('| Признак | $m$ | Тетрахотомия | $n$ | $c$ | Диада полюса 1 | Диада полюса 0 |')
        self.assertEqual(len(four), 3)
        self.assertEqual(len(two), 8)
        for record in four:
            _, trait, column = record
            trait, column = int(trait), int(column)
            for name, model in self.models.items():
                for p in (0, 1):
                    holds = all((self.aspects[a][column - 1]
                                 == self.functions[model[a]][column - 1]) == bool(p)
                                for a in primary.ASPECTS)
                    self.assertEqual(holds, self.traits[name][trait - 1] == p,
                                     (name, record, p))
        for record in two:
            _, trait, kind, nality, column, positive, negative = record
            trait, nality, column = int(trait), int(nality), int(column)
            pos, neg = self.aspect_set(positive), self.aspect_set(negative)
            actual_pos = frozenset(a for a, row in self.aspects.items()
                                  if row[6] == nality and row[column - 1] == 1)
            actual_neg = frozenset(a for a, row in self.aspects.items()
                                  if row[6] == nality and row[column - 1] == 0)
            self.assertEqual(pos, actual_pos)
            self.assertEqual(neg, actual_neg)
            for name, model in self.models.items():
                for p in (0, 1):
                    holds = all((self.aspects[a][column - 1]
                                 == self.functions[model[a]][column - 1]) == bool(p)
                                for a in pos | neg)
                    self.assertEqual(holds, self.traits[name][trait - 1] == p,
                                     (name, record, p))

    def test_functional_tetrads_match_source(self):
        records = self.table('| $c$ | Полюс 1 | Полюс 0 |')
        self.assertEqual(len(records), 4)
        for column, positive, negative in records:
            column = int(column)
            for p, field in [(1, positive), (0, negative)]:
                listed = set(map(int, re.findall(r'[1-8]', field)))
                expected = {f for f, row in self.functions.items() if row[column - 1] == p}
                self.assertEqual(listed, expected)

    def test_democracy_partition_triples_and_both_poles(self):
        header = '| Тройка столбцов Аспектона и Функциона | Аспектные пары | Функциональные пары при полюсе 1 | Функциональные пары при полюсе 0 |'
        records = self.table(header)
        self.assertEqual(len(records), 4)
        specifications = []
        for columns, aspect, positive, negative in records:
            columns = tuple(map(int, columns.split(',')))
            aa = self.partition(aspect, aspect=True)
            fp, fn = self.partition(positive), self.partition(negative)
            for data, expected in [(self.aspects, aa), (self.functions, fp)]:
                groups = {}
                for obj, row in data.items():
                    bits = tuple(row[c - 1] for c in columns)
                    self.assertEqual(sum(v == 0 for v in bits) % 2, 0)
                    groups.setdefault(bits, set()).add(obj)
                self.assertEqual(frozenset(frozenset(b) for b in groups.values()), expected)
            specifications.append((aa, fp, fn))
        for name, model in self.models.items():
            for p in (0, 1):
                holds = all(self.images(model, aa) == (fp if p else fn)
                            for aa, fp, fn in specifications)
                self.assertEqual(holds, self.traits[name][4] == p, (name, p))

    def test_composite_partitions_both_poles(self):
        header = '| Аспектные пары | Функциональные пары при полюсе 1 | Функциональные пары при полюсе 0 |'
        for section, trait in [('### Позитивизм/негативизм', 6),
                               ('### Квестимность/деклатимность', 12)]:
            records = self.table(header, section=section)
            self.assertEqual(len(records), 2)
            specs = [(self.partition(a, aspect=True), self.partition(pos), self.partition(neg))
                     for a, pos, neg in records]
            for name, model in self.models.items():
                for p in (0, 1):
                    holds = all(self.images(model, aa) == (fp if p else fn)
                                for aa, fp, fn in specs)
                    self.assertEqual(holds, self.traits[name][trait - 1] == p,
                                     (name, trait, p))
                if trait == 6:
                    self.assertEqual(self.traits[name][4] == self.traits[name][1],
                                     bool(self.traits[name][5]))
                else:
                    self.assertEqual(self.traits[name][4] == self.traits[name][15],
                                     bool(self.traits[name][11]))

    def test_macroaspect_signatures_and_cycle_both_poles(self):
        records = self.table('| Значения столбцов 4, 6, 7 | Макроаспект | Полутакт |')
        self.assertEqual(len(records), 4)
        for values, aspects, functions in records:
            sig = tuple(map(int, values.split(',')))
            aa = self.aspect_set(aspects)
            ff = frozenset(map(int, re.findall(r'[1-8]', functions)))
            self.assertEqual(aa, frozenset(a for a, row in self.aspects.items()
                                         if tuple(row[c - 1] for c in (4, 6, 7)) == sig))
            self.assertEqual(ff, frozenset(f for f, row in self.functions.items()
                                         if tuple(row[c - 1] for c in (4, 6, 7)) == sig))
        source_cycle = tuple(frozenset(x) for x in [('ЧИ', 'БИ'), ('ЧЛ', 'БЛ'),
                                                    ('ЧС', 'БС'), ('ЧЭ', 'БЭ')])
        target_cycle = tuple(frozenset(x) for x in [(1, 7), (2, 8), (3, 5), (4, 6)])
        for name, model in self.models.items():
            images = tuple(frozenset(model[a] for a in block) for block in source_cycle)
            for p in (0, 1):
                target = target_cycle if p else tuple(reversed(target_cycle))
                rotations = {target[k:] + target[:k] for k in range(4)}
                self.assertEqual(images in rotations, self.traits[name][10] == p,
                                 (name, p))


if __name__ == '__main__':
    unittest.main()
