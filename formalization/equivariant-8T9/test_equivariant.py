import unittest
from equivariant import (star, inverse, character, left_pullback, right_pullback,
                         conjugate_pullback, load_source, conjugacy_orbits, incidence)


class EquivariantAlgebraTests(unittest.TestCase):
    def test_central_law_matches_all_model_compositions(self):
        records = load_source()
        self.assertEqual(len(records), 16)
        by_code = {code: perm for code, perm, row in records.values()}
        self.assertEqual(len(by_code), 16)
        for x, px in by_code.items():
            for y, py in by_code.items():
                actual = tuple(px[py[i] - 1] for i in range(8))
                self.assertEqual(by_code[star(x, y)], actual)

    def test_hadamard_basis_and_defect(self):
        for a in range(16):
            for b in range(16):
                for x in range(16):
                    self.assertEqual(character(a ^ b, x), character(a, x)*character(b, x))
        hom, twisted = [], []
        for a in range(16):
            defects = {character(a, star(x, y))*character(a, x)*character(a, y)
                       for x in range(16) for y in range(16)}
            (hom if defects == {1} else twisted).append(a)
            if defects != {1}:
                self.assertEqual(defects, {1, -1})
        self.assertEqual(len(hom), 8)
        self.assertEqual(len(twisted), 8)

    def test_left_right_and_conjugation_formulas(self):
        for g in range(16):
            for mask in range(16):
                sign, shifted = left_pullback(g, mask)
                sign_r, shifted_r = right_pullback(g, mask)
                sign_c, shifted_c = conjugate_pullback(g, mask)
                for x in range(16):
                    self.assertEqual(character(mask, star(inverse(g), x)), sign*character(shifted, x))
                    self.assertEqual(character(mask, star(x, inverse(g))), sign_r*character(shifted_r, x))
                    self.assertEqual(character(mask, star(star(inverse(g), x), g)), sign_c*character(shifted_c, x))

    def test_conjugation_fixed_algebra_has_dimension_ten(self):
        orbits = conjugacy_orbits()
        self.assertEqual(sorted(map(len, orbits)), [1]*8+[4]*2)
        classes = []
        unseen = set(range(16))
        while unseen:
            x = min(unseen)
            cls = {star(star(inverse(g), x), g) for g in range(16)}
            self.assertTrue(cls <= unseen)
            unseen -= cls
            classes.append(cls)
        self.assertEqual(len(classes), len(orbits))

    def test_source_trait_columns_are_hadamard_characters(self):
        records = load_source()
        for name, (code, perm, row) in records.items():
            self.assertEqual(len(row), 16)
        rows = [r[2] for r in records.values()]
        self.assertTrue(all(sum(a*b for a,b in zip(x,y)) == (16 if i == j else 0)
                            for i,x in enumerate(rows) for j,y in enumerate(rows)))
        counts = []
        for j in range(16):
            col = {code: row[j] for code, perm, row in records.values()}
            n = sum(col[star(x,y)] != col[x]*col[y]
                    for x in range(16) for y in range(16))
            counts.append(n)
        self.assertEqual(counts.count(0), 8)
        self.assertEqual(counts.count(64), 8)
    def test_carefree_third_generation_incidence_and_covariance(self):
        records = load_source()
        base = ('ЧИ','БЛ','ЧС','БЭ','БС','ЧЭ','БИ','ЧЛ')
        D1 = {base.index(a) for a in ('ЧИ','БС')}
        D0 = {base.index(a) for a in ('ЧС','БИ')}
        B1, B0 = {0,3,4,7}, {1,2,5,6}  # function numbers minus one
        for name, (code, perm1, row) in records.items():
            p = tuple(i - 1 for i in perm1)
            positive = incidence(p, D1, B1) and incidence(p, D0, B0)
            negative = incidence(p, D1, B0) and incidence(p, D0, B1)
            self.assertEqual((positive, negative), (row[2] == 1, row[2] == -1), name)
            # Simultaneous transport of domain, codomain and the model.
            u = (1,0,2,3,4,5,6,7)
            v = (0,1,2,3,5,4,6,7)
            inv_u = tuple(u.index(i) for i in range(8))
            transported = tuple(v[p[inv_u[i]]] for i in range(8))
            self.assertEqual(incidence(p, D1, B1),
                             incidence(transported, {u[i] for i in D1}, {v[i] for i in B1}))


if __name__ == '__main__':
    unittest.main()
