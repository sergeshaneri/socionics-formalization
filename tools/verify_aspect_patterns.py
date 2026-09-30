"""Exact checks for aspect-direction patterns, using frozen research inputs."""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = [1, 5, 6, 2, 8, 4, 3, 7]
ASPECTS = ['ЧИ', 'БС', 'ЧЭ', 'БЛ', 'ЧЛ', 'БЭ', 'ЧС', 'БИ']

def verify():
    archive = ROOT / 'agent-researches' / '2026-09-29-dichotomy-formalization.zip'
    with zipfile.ZipFile(archive) as z:
        prefix = '2026-09-29-dichotomy-formalization/'
        permutations = json.loads(z.read(prefix + 'data/permutations.json'))
        profiles = json.loads(z.read(prefix + 'results/formula_profiles.json'))
    democracy = set(next(r['pole'] for r in profiles if r['trait'] == 'Демократизм'))
    direction_checks = switch_checks = nality_checks = 0
    for record in permutations:
        q = int(record['id'] not in democracy)
        image = [ORDER.index(record['images'][f - 1]) for f in ORDER]
        translation = image[0]
        for a in range(1, 8):
            nu = ((a >> 1) ^ (a >> 2)) & 1
            expected = a ^ (6 if q and nu else 0)
            assert {image[x] ^ image[x ^ a] for x in range(8)} == {expected}
            assert image[a] ^ translation == expected
            direction_checks += 1
            if nu:
                assert expected == (a ^ 6 if q else a)
                switch_checks += 1
        for profile in profiles:
            if profile['kind'] != 'incidence':
                continue
            pair = {ASPECTS.index(a) for a in profile['aspects']}
            n = {((a >> 1) ^ (a >> 2)) & 1 for a in pair}
            assert len(n) == 1
            same_nality = {x for x in range(8) if (((x >> 1) ^ (x >> 2)) & 1) in n}
            other_pair = same_nality - pair
            target = set(profile['F'])
            mapped_pair = {ORDER[image[a]] for a in pair}
            mapped_other = {ORDER[image[a]] for a in other_pair}
            mapped_nality = mapped_pair | mapped_other
            assert len(mapped_nality & target) == 2
            assert (mapped_pair <= target) == (mapped_other <= set(range(1, 9)) - target)
            nality_checks += 1
    # Row-XNOR is addition of evaluation vectors; common positive set is {0,a}.
    for a in range(1, 8):
        kernel = {h for h in range(8) if (a & h).bit_count() % 2 == 0}
        assert {x for x in range(8) if all((x & h).bit_count() % 2 == 0 for h in kernel)} == {0, a}
    return {'all_checks_passed': True, 'direction_action_checks': direction_checks,
            'rational_switch_checks': switch_checks, 'nality_pair_checks': nality_checks,
            'other_directions_fixed': [1, 6, 7],
            'direction_rule': 'a -> a + q * nu(a) * CS, nu(a)=a1+a2; CS=6',
            'switched_pairs': [['БЛ', 'БЭ'], ['ЧЭ', 'ЧЛ']],
            'scope': 'Frozen 16 permutations and eight incidence specifications; prose and images excluded.'}

if __name__ == '__main__':
    result = verify()
    out = ROOT / 'audits' / 'aspect-pattern-checks.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result, ensure_ascii=False))
