"""Audit explicit arrow formulas against the frozen dichotomy research data.
Does not edit sources or archives. Uses only Python standard library.
"""
import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

BASE = ['ЧИ', 'БЛ', 'ЧС', 'БЭ', 'БС', 'ЧЭ', 'БИ', 'ЧЛ']
STARTS = [(72, 'Статика'), (130, 'Экстраверсия'), (167, 'Иррациональность'),
          (192, 'Статика'), (247, 'Беспечность'), (273, 'Уступчивость'),
          (300, 'Интуиция'), (325, 'Логика'), (352, 'Весёлые'),
          (377, 'Рассудительность'), (404, 'Конструктивизм'), (429, 'Тактика'),
          (453, 'Демократизм'), (692, 'Позитивизм'), (815, 'Квестимность'),
          (963, 'Правые')]

def canon(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))

def audit(source_bytes, permutations, profiles):
    poles = {r['trait']: set(r['pole']) for r in profiles}
    rows = []
    for number, line in enumerate(source_bytes.decode('utf-8-sig').splitlines(), 1):
        if '→' not in line or '**' not in line or '\\[' not in line:
            continue
        lhs, rhs = line.split('→', 1)
        lhs, rhs = lhs.split('|')[0], rhs.split('|')[0]
        aspects = [re.findall(r'ЧИ|БС|ЧЭ|БЛ|ЧЛ|БЭ|ЧС|БИ', b)
                   for b in re.split(r'\\[~><]', lhs)]
        aspects = [b for b in aspects if b]
        functions = [[int(f) for f in re.findall(r'[1-8]', b)]
                     for b in re.split(r'\\[~><]', rhs)]
        functions = [b for b in functions if b]
        if not aspects or not functions:
            continue
        trait = [t for start, t in STARTS if start <= number][-1]
        kind = 'matching' if '\\~' in lhs else 'cycle' if '\\>' in lhs else 'inclusion'
        malformed = []
        if kind != 'inclusion':
            if sorted(a for b in aspects for a in b) != sorted(BASE):
                malformed.append('aspect partition is not a bijective cover')
            if sorted(f for b in functions for f in b) != list(range(1, 9)):
                malformed.append('function partition is not a bijective cover')
        support = set()
        for rec in permutations:
            images = [tuple(sorted(rec['images'][BASE.index(a)] for a in block))
                      for block in aspects]
            if kind == 'inclusion':
                holds = set(images[0]) <= set(functions[0])
            elif kind == 'matching':
                holds = canon(images) == canon(functions)
            else:
                target = tuple(tuple(sorted(b)) for b in functions)
                if '\\<' in rhs:
                    target = tuple(reversed(target))
                holds = tuple(images) in {target[j:] + target[:j] for j in range(len(target))}
            if holds:
                support.add(rec['id'])
        sign = '+' if support == poles[trait] else '-' if support == set(range(16)) - poles[trait] else 'MISMATCH'
        rows.append({'line': number, 'trait': trait, 'kind': kind,
                     'matched_pole': sign, 'support': sorted(support),
                     'malformed': malformed, 'text': line})
    return {'sha256': hashlib.sha256(source_bytes).hexdigest(),
            'formula_count': len(rows),
            'matched_poles': dict(Counter(r['matched_pole'] for r in rows)),
            'rows': rows}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True, type=Path)
    ap.add_argument('--archive', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    with zipfile.ZipFile(args.archive) as z:
        pre = '2026-09-29-dichotomy-formalization/'
        permutations = json.loads(z.read(pre + 'data/permutations.json'))
        profiles = json.loads(z.read(pre + 'results/formula_profiles.json'))
        original = z.read(pre + 'originals/author-formulae.md')
    before = audit(original, permutations, profiles)
    after = audit(args.source.read_bytes(), permutations, profiles)
    # Regression bounds are specific to this version. Changed layout needs review.
    assert before['formula_count'] == after['formula_count'] == 82
    assert before['matched_poles'].get('MISMATCH') == 5
    assert not any(r['malformed'] or r['matched_pole'] == 'MISMATCH' for r in after['rows'])
    report = {'baseline': before, 'current': after,
              'scope': 'Explicit text formulas only. Section labels use fixed line boundaries; images, prose and intended polarity labels are not audited.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'baseline': before['matched_poles'], 'current': after['matched_poles'],
                      'formula_count': after['formula_count'], 'output': str(args.output)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
