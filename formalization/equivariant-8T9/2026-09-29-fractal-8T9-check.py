#!/usr/bin/env python3
"""Reproduce checks against the supplied 16 Model A and Reinin tables.

Run: python3 2026-09-29-fractal-8T9-check.py
No external dependencies. Function permutations are in conventional positions 1..8.
Composition (p*q)(i)=p(q(i)). Signs: table 1 -> +1, table 0 -> -1.
"""
from collections import Counter
from itertools import permutations
from pathlib import Path
import re

SOURCE = Path(__file__).resolve().parent / 'project_sources' / '09-markdown-1-.md'


def rows_between(lines, start, stop):
    return [line for line in lines[start:stop] if line.startswith('|')]


def parts(line):
    return [x.strip().replace('\\*', '*').strip('*') for x in line.strip().strip('|').split('|')]


def compose(p, q):
    return tuple(p[q[i] - 1] for i in range(8))


def order(p):
    identity = tuple(range(1, 9))
    r = identity
    for n in range(1, 17):
        r = compose(p, r)
        if r == identity:
            return n
    raise AssertionError('Unexpected order')


def cycle_type(p):
    unseen = set(range(1, 9))
    sizes = []
    while unseen:
        v = next(iter(unseen))
        cur = v
        n = 0
        while cur in unseen:
            unseen.remove(cur)
            cur = p[cur - 1]
            n += 1
        sizes.append(n)
    return tuple(sorted(sizes))


def parity(p):
    return (-1) ** (8 - len(cycle_type(p)))


def is_hadamard(rows):
    return all(sum(a * b for a, b in zip(x, y)) == (len(x) if i == j else 0)
               for i, x in enumerate(rows) for j, y in enumerate(rows))


def main():
    lines = SOURCE.read_text(encoding='utf-8').splitlines()
    models = {r[0]: r[1:] for l in rows_between(lines, 5, 24)
              if len(r := parts(l)) == 9 and r[0] not in ('ТИМ', '')}
    traits = {r[0]: [1 if x == '1' else -1 for x in r[1:]]
              for l in rows_between(lines, 27, 43)
              if len(r := parts(l)) == 17 and r[0] not in ('ТИМ', '')}
    names = parts(lines[25])[1:]
    assert len(models) == len(traits) == 16
    assert list(models) == list(traits)
    aspect_order = models['ИЛЭ']
    assert len(set(aspect_order)) == 8
    assert all(set(row) == set(aspect_order) for row in models.values())
    h16 = list(traits.values())
    assert is_hadamard(h16)
    assert all(row[i] * row[j] == row[i ^ j] for row in h16
               for i in range(16) for j in range(16))
    assert all(row[0] == 1 for row in h16)
    assert all(h16[0][j] == 1 for j in range(16))

    # Markdown escape backslashes may precede each sign.
    def extract_h8(start, stop):
        out = []
        for l in rows_between(lines, start, stop):
            r = parts(l)
            if len(r) == 9 and all(x in ('\\+', '\\-', '+', '-') for x in r[1:]):
                out.append([1 if x.endswith('+') else -1 for x in r[1:]])
        return out

    aspects = extract_h8(48, 56)
    functions = extract_h8(61, 69)
    assert len(aspects) == len(functions) == 8
    assert is_hadamard(aspects) and is_hadamard(functions)

    # Function permutation carrying the ILE aspect in slot i to its slot in t.
    perms = {t: tuple(row.index(a) + 1 for a in aspect_order) for t, row in models.items()}
    identity = tuple(range(1, 9))
    assert perms['ИЛЭ'] == identity and len(set(perms.values())) == 16
    ps = set(perms.values())
    closure = all(compose(p, q) in ps for p in ps for q in ps)
    orbits = {tuple(sorted({p[i] for p in ps})) for i in range(8)}
    orders = Counter(order(p) for p in ps)
    types = Counter(cycle_type(p) for p in ps)
    parities = Counter(parity(p) for p in ps)
    center = [t for t, p in perms.items() if all(compose(p, q) == compose(q, p) for q in ps)]
    derived = {compose(compose(compose(p, q), inverse(p)), inverse(q)) for p in ps for q in ps}
    # Read relation operator table independently, with its 1,5,6,2,8,4,3,7 input order.
    relation_lines = rows_between(lines, 73, 89)
    inputs = [1, 5, 6, 2, 8, 4, 3, 7]
    relations = {}
    for l in relation_lines:
        r = parts(l)
        if len(r) == 9:
            relations[r[0]] = tuple(int(r[inputs.index(i) + 1]) for i in range(1, 9))
    assert len(relations) == 16
    print('16 TIM, 16 traits; Hadamard 16x16:', len(models), len(names), is_hadamard(h16))
    print('Hadamard aspect/function 8x8:', is_hadamard(aspects), is_hadamard(functions))
    print('Model permutations: closure:', closure, 'orbit(s):', orbits)
    print('Model orders:', dict(sorted(orders.items())))
    print('Model cycle types:', dict(sorted(types.items())))
    print('Model parities:', dict(sorted(parities.items())))
    print('Center:', center, 'commutator subgroup size:', len(derived))
    print('Relation operators closed:', all(compose(p, q) in set(relations.values()) for p in relations.values() for q in relations.values()))
    print('Model set equals supplied relation set:', ps == set(relations.values()))
    print('Relation order distribution:', dict(sorted(Counter(order(p) for p in relations.values()).items())))
    # Compare to the published 8T9 generators on GroupNames, by conjugation in S8.
    def from_cycles(*cycles):
        p = list(range(1, 9))
        for cyc in cycles:
            for a, b in zip(cyc, cyc[1:] + cyc[:1]):
                p[a - 1] = b
        return tuple(p)
    canonical = (
        from_cycles((1, 7), (2, 8), (3, 5), (4, 6)),
        from_cycles((1, 2, 3, 4), (5, 6, 7, 8)),
        from_cycles((1, 4), (2, 3), (5, 8), (6, 7)),
    )
    generated = {identity}
    while True:
        expanded = generated | {compose(g, h) for g in generated for h in canonical}
        if expanded == generated:
            break
        generated = expanded
    assert generated == ps
    witness = None
    for c in permutations(range(1, 9)):
        ci = inverse(c)
        if all(compose(compose(c, g), ci) in ps for g in canonical):
            witness = c
            break
    assert witness is not None
    print('8T9 S8-conjugating map c (canonical to model):', witness)
    print('TIM -> relation:', {t: next(name for name, p in relations.items() if p == q)
                               for t, q in perms.items()})
    relation_by_perm = {p: n for n, p in relations.items()}
    relative, quasi = relations['Родственные'], relations['Квазитождество']
    assert relation_by_perm[compose(relative, quasi)] == 'Передача Заказа'
    assert relation_by_perm[compose(quasi, relative)] == 'Прием Заказа'
    assert relation_by_perm[compose(compose(relative, quasi), compose(relative, quasi))] == 'Суперэго'
    print('Relatives * Quasi:', relation_by_perm[compose(relative, quasi)])
    print('Quasi * Relatives:', relation_by_perm[compose(quasi, relative)])
    print('(Relatives * Quasi)^2:', relation_by_perm[compose(compose(relative, quasi), compose(relative, quasi))])
    perm_to_type = {p: t for t, p in perms.items()}
    coord_cols = (1, 2, 4, 8)
    def bits(t):
        return tuple(0 if traits[t][j] == 1 else 1 for j in coord_cols)
    def xor(a, b):
        return tuple(i ^ j for i, j in zip(a, b))
    difference = Counter()
    defects = Counter()
    homomorphisms = []
    for j, name in enumerate(names):
        failing = sum(traits[perm_to_type[compose(perms[x], perms[y])]][j] != traits[x][j] * traits[y][j]
                      for x in models for y in models)
        defects[name] = failing
        if failing == 0:
            homomorphisms.append(name)
    for x in models:
        for y in models:
            z = perm_to_type[compose(perms[x], perms[y])]
            difference[xor(bits(z), xor(bits(x), bits(y)))] += 1
    print('Homomorphic columns:', homomorphisms)
    print('Defect counts (of 256 pairs):', dict(defects))
    print('Difference of XOR and composition, bit order', coord_cols, ':', dict(difference))
    # Algebraic normal form of the central correction B(x,y), over GF(2).
    type_by_bits = {bits(t): t for t in models}
    values = []
    for mask in range(256):
        xb = tuple((mask >> i) & 1 for i in range(4))
        yb = tuple((mask >> (4 + i)) & 1 for i in range(4))
        z = perm_to_type[compose(perms[type_by_bits[xb]], perms[type_by_bits[yb]])]
        delta = xor(bits(z), xor(xb, yb))
        assert delta in ((0, 0, 0, 0), (0, 1, 0, 1))
        values.append(delta[1])
    anf = values[:]
    for i in range(8):
        for mask in range(256):
            if mask & (1 << i):
                anf[mask] ^= anf[mask ^ (1 << i)]
    symbols = ('x_E', 'x_B', 'x_D', 'x_M', 'y_E', 'y_B', 'y_D', 'y_M')
    terms = ['*'.join(symbols[i] for i in range(8) if mask & (1 << i)) or '1'
             for mask, coefficient in enumerate(anf) if coefficient]
    print('Correction B(x,y) ANF:', ' + '.join(terms))
    assert set(terms) == {'x_D*y_B', 'x_D*y_D', 'x_D*y_M'}
    commutator = next(iter(derived - {identity}))
    print('Nontrivial commutator is TIM:', perm_to_type[commutator], 'permutation:', commutator)
    # Trait array with +/− poles: exact necessary-and-sufficient truth table.
    print('Reconstruction from four coordinate traits:')
    for t, row in traits.items():
        print(t, ''.join('+' if x == 1 else '-' for x in [row[j] for j in (1, 2, 4, 8)]), perms[t])


def inverse(p):
    q = [0] * 8
    for i, j in enumerate(p, 1):
        q[j - 1] = i
    return tuple(q)


if __name__ == '__main__':
    main()
