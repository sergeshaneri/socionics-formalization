"""Finite equivariant algebra for the supplied H16 / 8T9 table.

Coordinates (e,d,r,z) are bits for introversion, aristocracy,
rationality and foresight. Composition is p(q(i)).
"""
from pathlib import Path

SOURCE = Path(__file__).parent / 'project_sources' / '09-markdown-1-.md'


def bit(x, i):
    return (x >> i) & 1


def star(x, y):
    """UT_3(F2) x C2, central coordinate z in bit 3."""
    return x ^ y ^ (8 if bit(x, 1) and bit(y, 2) else 0)


def inverse(x):
    return x ^ (8 if bit(x, 1) and bit(x, 2) else 0)


def character(mask, x):
    return -1 if (mask & x).bit_count() % 2 else 1


def left_pullback(g, mask):
    """f(x) -> f(g^{-1} star x): signed permutation of H16 basis."""
    q = inverse(g)
    return character(mask, q), mask ^ (4 if bit(mask, 3) and bit(g, 1) else 0)


def right_pullback(g, mask):
    """f(x) -> f(x star g^{-1}): signed permutation of H16 basis."""
    q = inverse(g)
    return character(mask, q), mask ^ (2 if bit(mask, 3) and bit(g, 2) else 0)


def conjugate_pullback(g, mask):
    """f(x) -> f(g^{-1} star x star g)."""
    if not bit(mask, 3):
        return 1, mask
    return 1, mask ^ (2 if bit(g, 2) else 0) ^ (4 if bit(g, 1) else 0)


def conjugacy_orbits():
    unseen = set(range(16))
    orbits = []
    while unseen:
        seed = min(unseen)
        orb = {conjugate_pullback(g, seed)[1] for g in range(16)}
        assert orb <= unseen
        unseen -= orb
        orbits.append(orb)
    return orbits


def incidence(perm, domain_subset, codomain_subset):
    """Whether a permutation maps a source subset inside a target subset."""
    return all(perm[i] in codomain_subset for i in domain_subset)


def load_source():
    """Return name -> (coordinate code, permutation, H16 row)."""
    lines = SOURCE.read_text(encoding='utf-8').splitlines()

    def parts(line):
        return [x.strip().replace('\\*', '*').strip('*') for x in line.strip().strip('|').split('|')]

    model_rows = [parts(line) for line in lines[5:24] if line.startswith('|')]
    models = {row[0]: row[1:] for row in model_rows if len(row) == 9 and row[0] not in ('ТИМ', '')}
    trait_rows = [parts(line) for line in lines[27:43] if line.startswith('|')]
    traits = {row[0]: tuple(1 if x == '1' else -1 for x in row[1:])
              for row in trait_rows if len(row) == 17 and row[0] not in ('ТИМ', '')}
    if len(models) != 16 or set(models) != set(traits):
        raise ValueError('Source table lacks 16 matched models and character rows')
    base = models['ИЛЭ']
    if len(set(base)) != 8 or any(set(m) != set(base) for m in models.values()):
        raise ValueError('Invalid aspect permutations in source')
    result = {}
    for name, m in models.items():
        row = traits[name]
        bits = (row[1], row[4], row[14], row[2])
        code = sum(1 << i for i, sign in enumerate(bits) if sign == -1)
        perm = tuple(m.index(aspect) + 1 for aspect in base)
        result[name] = (code, perm, row)
    return result
