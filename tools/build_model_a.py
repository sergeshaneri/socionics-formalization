"""Construct model A from (extraversion, irrationality, intuition, logic).

Only aspect/function signatures are inputs. Type/model tables are not used.
All signature tuples are (vert, nal, strong), in ordinary Model A numbering.
"""
import argparse
import gzip
import hashlib
from itertools import permutations, product
import json
from pathlib import Path

ASPECT_SIGNATURES = {
    'ЧИ': (1, 1, 1), 'БС': (0, 1, 0), 'ЧЭ': (1, 0, 0), 'БЛ': (0, 0, 1),
    'ЧЛ': (1, 0, 1), 'БЭ': (0, 0, 0), 'ЧС': (1, 1, 0), 'БИ': (0, 1, 1),
}
FUNCTION_SIGNATURES = {
    1: (1, 1, 1), 2: (0, 0, 1), 3: (1, 1, 0), 4: (0, 0, 0),
    5: (0, 1, 0), 6: (1, 0, 0), 7: (0, 1, 1), 8: (1, 0, 1),
}


def xnor(a, b):
    return int(a == b)


def construct(v, n, u, l):
    """Return aspect -> position; each pole must equal 0 or 1."""
    if any(p not in (0, 1) for p in (v, n, u, l)):
        raise ValueError('Each pole must be 0 or 1')
    lookup = {signature: f for f, signature in FUNCTION_SIGNATURES.items()}
    model = {}
    for aspect, (av, an, strength) in ASPECT_SIGNATURES.items():
        target = (xnor(av, v), xnor(an, n), xnor(strength, u if an else l))
        model[aspect] = lookup[target]
    if set(model.values()) != set(FUNCTION_SIGNATURES):
        raise AssertionError('Construction must yield a bijection')
    return model


def admissible_profile(perm):
    """Recognize the full four rules, independently of construct()."""
    values = [set(), set(), set(), set()]
    for aspect, f in zip(ASPECT_SIGNATURES, perm):
        av, an, strength = ASPECT_SIGNATURES[aspect]
        fv, fn, fs = FUNCTION_SIGNATURES[f]
        values[0].add(xnor(av, fv))
        values[1].add(xnor(an, fn))
        values[2 if an else 3].add(xnor(strength, fs))
    return tuple(next(iter(s)) for s in values) if all(len(s) == 1 for s in values) else None


def audit(directory):
    """Save every candidate, frozen code/inputs, summary and SHA-256 manifest.

    The copied program is standalone and can replay into a fresh directory.
    Existing run directories are never overwritten.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    profiles = list(product((0, 1), repeat=4))
    counts = {p: 0 for p in profiles}
    solutions = {}
    examined = 0
    ledger = directory / 'candidates.jsonl.gz'
    with gzip.open(ledger, 'wt', encoding='utf-8', newline='\n') as out:
        for perm in permutations(range(1, 9)):
            examined += 1
            profile = admissible_profile(perm)
            out.write(json.dumps({'images': perm, 'profile': profile}, separators=(',', ':')) + '\n')
            if profile is not None:
                counts[profile] += 1
                solutions[profile] = perm
                assert perm == tuple(construct(*profile).values())
    assert examined == 40320 and all(count == 1 for count in counts.values())
    summary = {
        'aspect_order': list(ASPECT_SIGNATURES),
        'profile_order': ['vert', 'nal (irrationality)', 'intuition', 'logic'],
        'candidate_family': 'all bijections from eight aspects to eight positions',
        'examined': examined, 'accepted': sum(counts.values()),
        'profiles': [{'profile': p, 'solutions': counts[p], 'images': solutions[p]} for p in profiles],
    }
    (directory / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (directory / 'inputs.json').write_text(json.dumps({'aspects': ASPECT_SIGNATURES, 'functions': FUNCTION_SIGNATURES}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (directory / 'build_model_a.py').write_bytes(Path(__file__).read_bytes())
    files = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in directory.iterdir() if p.is_file()}
    (directory / 'manifest.json').write_text(json.dumps(files, indent=2) + '\n', encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', nargs=4, type=int, metavar=('VERT', 'NAL', 'INTUITION', 'LOGIC'))
    parser.add_argument('--audit-dir', type=Path)
    args = parser.parse_args()
    if args.profile is not None:
        model = construct(*args.profile)
        print(json.dumps({'profile': args.profile, 'aspect_to_position': model,
                          'positions_1_to_8': [a for f in range(1, 9) for a, pos in model.items() if pos == f]},
                         ensure_ascii=False, indent=2))
    if args.audit_dir is not None:
        summary = audit(args.audit_dir)
        print(json.dumps({'examined': summary['examined'], 'accepted': summary['accepted'],
                          'solutions_per_profile': sorted({p['solutions'] for p in summary['profiles']})}))
    if args.profile is None and args.audit_dir is None:
        parser.error('provide --profile or --audit-dir')


if __name__ == '__main__':
    main()
