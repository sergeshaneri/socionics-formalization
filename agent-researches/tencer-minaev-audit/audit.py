#!/usr/bin/env python3
"""Finite audit of Tencer--Minaev invariants. Python 3.10+, standard library.

All subset/partition predicates are evaluated directly on phi_T (functions to
aspects); mirror counts from the earlier Reinin audit are independent checks.
Run python3 audit.py; no external files or packages required beyond inputs.json.
"""
from pathlib import Path
from itertools import combinations
from collections import defaultdict, Counter
from fractions import Fraction
import json

ROOT = Path(__file__).resolve().parent
src = json.loads((ROOT/'inputs.json').read_text(encoding='utf-8'))
A = src['aspects']; N = src['type_order']; FULL = (1 << 16)-1

def bits(m, n=8):
    return [i for i in range(n) if m >> i & 1]

def compose(p, q):
    return tuple(p[q[i]] for i in range(8))

def inverse(p):
    return tuple(p.index(i) for i in range(8))

def mask_image(p, m):
    return sum(1 << p[i] for i in bits(m))

psi = [tuple(src['models'][t].index(a) for a in A) for t in N]
phi = [inverse(p) for p in psi]
theta = psi[0]
ref = phi[0]
g = [compose(theta, p) for p in phi]  # group on function labels; g_ILE=id
index = {p:i for i,p in enumerate(g)}
mul = [[index[compose(p,q)] for q in g] for p in g]
iota = [index[inverse(p)] for p in g]
assert len(index) == 16 and g[0] == tuple(range(8))
assert all(compose(theta, compose(phi[t], theta)) == psi[iota[t]] for t in range(16))
assert all(iota[iota[t]] == t for t in range(16))

def mirror(m):
    return sum(1 << iota[t] for t in bits(m,16))

R = [[src['traits'][t][j] for j in range(16)] for t in N]
TM = [R[iota[t]] for t in range(16)]
rmasks = [sum(R[t][j] << t for t in range(16)) for j in range(16)]
tmasks = [sum(TM[t][j] << t for t in range(16)) for j in range(16)]
shared = [j for j in range(1,16) if rmasks[j] == tmasks[j]]
assert shared == [1,4,5,10,11,14,15]
assert all((FULL ^ tmasks[i] ^ tmasks[j]) in tmasks for i,j in combinations(range(1,16),2))
basis = [1,14,4,2]  # e, n, d, c; positive pole is 0 in ordinary F_2 coordinates
rcodes = [sum((1-R[t][j]) << k for k,j in enumerate(basis)) for t in range(16)]
tcodes = [sum((1-TM[t][j]) << k for k,j in enumerate(basis)) for t in range(16)]
assert len(set(tcodes)) == 16
assert all(tcodes[t] == c ^ ((((c >> 1) & 1)*((c >> 2) & 1)) << 3) for t,c in enumerate(rcodes))
vectors = [next(v for v in range(16) if all((v & tcodes[t]).bit_count()%2 == 1-TM[t][j]
            for t in range(16))) for j in range(16)]

# Independent operational definitions of the eight new traits.
named_sets = {
    'delta':['ЧИ','БС','ЧЛ','БЭ'], 'alpha':['ЧИ','БС','ЧЭ','БЛ'],
    'abstract':['ЧИ','БЛ','ЧЛ','БИ'], 'implicit':['ЧИ','ЧЭ','БЭ','БИ']}
amasks = {k:sum(1 << A.index(a) for a in v) for k,v in named_sets.items()}
op_defs = {2:(1,amasks['delta']),3:(1,amasks['abstract']),
           6:(2,255 ^ amasks['delta']),7:(2,amasks['abstract']),
           8:(2,amasks['alpha']),9:(2,255 ^ amasks['implicit']),
           12:(1,amasks['alpha']),13:(1,amasks['implicit'])}
for j,(f,s) in op_defs.items():
    assert tmasks[j] == sum(1 << t for t in range(16) if s >> phi[t][f-1] & 1)

classes = []
refs = {c['id']:c for c in src['reference_classes']}
for old in src['reference_classes']:
    m = mirror(old['mask'])
    assert m == sum(1 << t for t in range(16) if all(TM[t][j] == v
                    for j,v in zip(old['traits'],old['values'])))
    c = {k:old[k] for k in ['id','kind','number','traits','values'] if k in old}
    c.update({'mask':m,'types':[N[t] for t in bits(m,16)],
              'reinin_mirror_mask':old['mask'],
              'mirror_types':[N[iota[N.index(t)]] for t in old['types']]})
    classes.append(c)
assert len(classes) == len({c['mask'] for c in classes}) == 290
by_mask = {c['mask']:c for c in classes}
by_id = {c['id']:c for c in classes}

families = []
for j in range(1,16):
    families.append({'id':f'D{j:02d}','kind':'dichotomy','number':j,'traits':[j],
                     'basis':[j],'class_ids':[f'D{j:02d}+ ',f'D{j:02d}- ' ]})
    families[-1]['class_ids'] = [x.strip() for x in families[-1]['class_ids']]
for n in range(1,36):
    js = src['section_traits'][str(n)]
    families.append({'id':f'T{n:02d}','kind':'tetrad','number':n,'traits':js,
                     'basis':js[:2],'class_ids':[f'T{n:02d}.{k}' for k in range(1,5)]})
for old in src['reference_octochotomies']:
    n = old['number']; js = old['fixed_traits']
    triples = [list(z) for z in combinations(js,3) if len({
        0,vectors[z[0]],vectors[z[1]],vectors[z[2]],vectors[z[0]]^vectors[z[1]],
        vectors[z[0]]^vectors[z[2]],vectors[z[1]]^vectors[z[2]],
        vectors[z[0]]^vectors[z[1]]^vectors[z[2]]}) == 8]
    assert triples == old['bases'] and len(triples) == 28
    families.append({'id':f'O{n:02d}','kind':'pair','number':n,'traits':js,
        'basis':old['chosen_basis'],'bases':triples,'delta':old['delta'],
        'reference_pair':[N[iota[N.index(t)]] for t in old['reference_pair']],
        'reinin_reference_name':old['name'],'class_ids':[f'O{n:02d}.{k}' for k in range(1,9)]})
for family in families:
    masks = [by_id[i]['mask'] for i in family['class_ids']]
    assert sum(masks) == FULL and all(a & b == 0 for a,b in combinations(masks,2))

images = [[mask_image(p,k) for k in range(256)] for p in phi]
inclusions = defaultdict(list)
counts = defaultdict(list); spectra = defaultdict(list); observations = []
for k in range(256):
    for s in range(256):
        truth = sum(1 << t for t in range(16) if images[t][k] & ~s == 0)
        inclusions[truth].append([k,s])
        buckets = defaultdict(int)
        for t in range(16):
            buckets[(images[t][k] & s).bit_count()] |= 1 << t
        observations.append([k,s,[[r,m] for r,m in sorted(buckets.items())]])
        unions = [(0,[])]
        for r,m in sorted(buckets.items()):
            if m in by_mask: counts[m].append([k,s,r])
            unions += [(v | m,rs+[r]) for v,rs in unions]
        for m,rs in unions:
            if m in by_mask: spectra[m].append([k,s,rs])

def all_partitions():
    blocks = []
    def rec(i):
        if i == 8:
            yield tuple(sorted(blocks)); return
        for j in range(len(blocks)):
            blocks[j] |= 1 << i
            yield from rec(i+1)
            blocks[j] ^= 1 << i
        blocks.append(1 << i)
        yield from rec(i+1)
        blocks.pop()
    return list(rec(0))

partitions = all_partitions()
assert len(partitions) == len(set(partitions)) == 4140
partition_maps = defaultdict(list)
for part in partitions:
    buckets = defaultdict(int)
    for t in range(16):
        target = tuple(sorted(images[t][k] for k in part))
        buckets[target] |= 1 << t
    for target,m in buckets.items():
        partition_maps[m].append([list(part),list(target)])

def generated(seed):
    H = {0} | set(seed); todo = list(H)
    while todo:
        a = todo.pop()
        for b in list(H):
            for c in [mul[a][b],mul[b][a]]:
                if c not in H:
                    H.add(c); todo.append(c)
    return sorted(H)

subgroups = {1:[0]}; todo = [[0]]
while todo:
    H = todo.pop()
    for t in range(16):
        K = generated(H+[t]); m = sum(1 << h for h in K)
        if m not in subgroups:
            subgroups[m] = K; todo.append(K)
cosets = {sum(1 << mul[t][h] for h in H) for H in subgroups.values() for t in range(16)}
assert len(subgroups) == 35 and len(cosets) == 179

def form_score(f):
    k,s = f
    size = k.bit_count()+s.bit_count()
    domain,codomain = (k,s) if size <= 8 else (255 ^ s,255 ^ k)
    return (min(size,16-size),domain.bit_count(),codomain.bit_count(),domain,codomain,k,s)

def partition_score(form):
    p,q = form
    sizes = sorted(x.bit_count() for x in p)
    return (len(p),max(sizes)-min(sizes),p,q)

def minimum_meet(candidates, target):
    representatives = {}
    for m,f in candidates:
        if m != FULL and m not in representatives: representatives[m] = f
    states = {FULL:[]}
    for depth in range(1,9):
        nxt = dict(states)
        for old,ws in states.items():
            for m,f in representatives.items():
                new = old & m
                if new not in nxt: nxt[new] = ws+[f]
        states = nxt
        if target in states: return states[target]
    return None

canonical = [(p[0],p[1]) for p in phi]
assert len(set(canonical)) == 16
for c in classes:
    q = c['mask']; ts = bits(q,16)
    supports = [sum(1 << a for a in {phi[t][f] for t in ts}) for f in range(8)]
    closure = sum(1 << t for t in range(16)
                  if all(supports[f] >> phi[t][f] & 1 for f in range(8)))
    c['unary_support'] = supports
    c['inclusion_closure'] = closure
    exact = inclusions.get(q,[])
    c['inclusion_exact_count'] = len(exact)
    c['inclusion_shapes'] = {f'{k}->{s}':v for (k,s),v in Counter(
        (k.bit_count(),s.bit_count()) for k,s in exact).items()}
    if exact:
        c['inclusion_witness'] = [min(exact,key=form_score)]
    elif closure == q:
        common = [(m,min(fs,key=form_score)) for m,fs in inclusions.items() if m & q == q]
        c['inclusion_witness'] = minimum_meet(common,q)
        assert c['inclusion_witness']
    else:
        c['inclusion_witness'] = []
    c['minimal_inclusion_conjunction'] = len(c['inclusion_witness']) or None
    if c['inclusion_witness']:
        check = FULL
        for k,s in c['inclusion_witness']:
            check &= sum(1 << t for t in range(16) if images[t][k] & ~s == 0)
        assert check == q

    image_constraints = []
    for k in range(1,255):
        allowed = sorted({images[t][k] for t in ts})
        truth = sum(1 << t for t in range(16) if images[t][k] in allowed)
        image_constraints.append([k,allowed,truth])
    c['image_family_constraints'] = image_constraints
    c['fixed_subset_exact_maps'] = [[k,ss[0]] for k,ss,m in image_constraints if len(ss)==1 and m==q]
    c['image_family_exact_count'] = sum(m == q for k,ss,m in image_constraints)

    common_parts = [(m,min(fs,key=partition_score)) for m,fs in partition_maps.items() if m & q == q]
    part_hull = FULL
    for m,_ in common_parts: part_hull &= m
    c['partition_closure'] = part_hull
    c['partition_conjunction_witness'] = minimum_meet(common_parts,q) if part_hull == q else []
    balanced = [(m,min([f for f in fs if len({b.bit_count() for b in f[0]})==1],key=partition_score))
                for m,fs in partition_maps.items() if m & q == q
                and any(len({b.bit_count() for b in f[0]})==1 for f in fs)]
    bhull = FULL
    for m,_ in balanced: bhull &= m
    c['balanced_partition_closure'] = bhull
    c['balanced_partition_witness'] = minimum_meet(balanced,q) if bhull == q else []
    c['balanced_partition_minimum'] = len(c['balanced_partition_witness']) or None
    for field,container in [('intersection',counts),('spectrum',spectra),('partition',partition_maps)]:
        fs = container.get(q,[])
        c[field+'_exact_count'] = len(fs)
        if field == 'partition':
            c[field+'_witness'] = min(fs,key=partition_score) if fs else None
        else:
            c[field+'_witness'] = min(fs,key=lambda f:(f[0].bit_count()+f[1].bit_count(),f)) if fs else None

    base = ts[0]
    H = generated(mul[iota[base]][t] for t in ts)
    hull = sum(1 << mul[base][h] for h in H)
    source_orbit = sorted({(g[h][0],g[h][1]) for h in H})
    target_orbit = sorted({(phi[base][a],phi[base][b]) for a,b in source_orbit})
    truth = sum(1 << t for t in range(16)
                if sorted({(phi[t][a],phi[t][b]) for a,b in source_orbit}) == target_orbit)
    assert truth == hull
    c.update({'transport_exact':hull == q,'transport_hull':hull,
              'relative_base_type':base,'relative_subgroup':H,
              'transport_orbit_source':[[a+1,b+1] for a,b in source_orbit],
              'transport_orbit_target':[list(ab) for ab in target_orbit],
              'canonical_ordered_pairs':[list(canonical[t]) for t in ts]})
    c['fourier_numerators'] = [sum(2*TM[t][j]-1 for t in ts) for j in range(16)]
    c['indicator_degree'] = 2 if any(c['fourier_numerators'][j] for j in [4,5,10,11]) else 1
    old = refs[c['id']]
    for field in ['inclusion_exact_count','intersection_exact_count','spectrum_exact_count',
                  'partition_exact_count','minimal_inclusion_conjunction','transport_exact','indicator_degree']:
        assert c[field] == old[field], (c['id'],field,c[field],old[field])
    if c['kind'] == 'pair':
        assert c['balanced_partition_minimum'] == old['balanced_partition_minimum']
        assert part_hull == hull

# Linear and quadratic observables: exact rational rank, no numerical tolerance.
X = [[int(p[f] == a) for f in range(8) for a in range(8)] for p in phi]
mat = [[Fraction(v) for v in row] for row in X]; rank = 0
for col in range(64):
    pivot = next((i for i in range(rank,16) if mat[i][col]),None)
    if pivot is None: continue
    mat[rank],mat[pivot] = mat[pivot],mat[rank]
    den = mat[rank][col]; mat[rank] = [v/den for v in mat[rank]]
    for i in range(16):
        if i != rank and mat[i][col]:
            factor = mat[i][col]
            mat[i] = [v-factor*w for v,w in zip(mat[i],mat[rank])]
    rank += 1
missing = [j for j in range(16) if all(
    sum((2*TM[t][j]-1)*X[t][k] for t in range(16)) == 0 for k in range(64))]
assert rank == 12 and missing == [4,5,10,11]
# The other twelve characters actually lie in the linear span (checked by their
# orthogonality to all four missing characters, plus the equal dimension 12).
for c in classes:
    ts = bits(c['mask'],16)
    for t in range(16):
        quadratic = sum(int(phi[t][0] == phi[u][0])*int(phi[t][1] == phi[u][1]) for u in ts)
        assert quadratic == ((c['mask'] >> t) & 1)

# Single-observation complete invariants for a full partition when available.
for family in families:
    qs = [by_id[i] for i in family['class_ids']]
    target = {q['mask'] for q in qs}
    candidates = []
    for k in range(1,255):
        buckets = defaultdict(int)
        for t in range(16): buckets[images[t][k]] |= 1 << t
        if set(buckets.values()) == target:
            candidates.append((k,{'kind':'phi_subset','function_mask':k},
                {m:im for im,m in buckets.items()}))
    # Also test a fixed aspect domain in the direct direction.
    for s in range(1,255):
        buckets = defaultdict(int)
        for t in range(16): buckets[mask_image(psi[t],s)] |= 1 << t
        if set(buckets.values()) == target:
            candidates.append((s,{'kind':'psi_subset','aspect_mask':s},
                {m:im for im,m in buckets.items()}))
    if candidates:
        k,desc,values = min(candidates,key=lambda z:(z[0].bit_count(),z[1]['kind'],z[0]))
        family['complete_invariant'] = desc
        for c in qs: c['complete_invariant_value'] = values[c['mask']]
    else:
        family['complete_invariant'] = {'kind':'binary_trait_code','basis':family['basis']}
        for c in qs: c['complete_invariant_value'] = [TM[bits(c['mask'],16)[0]][j] for j in family['basis']]
    # A block containing one observed aspect, or a pair of such block values.
    # These give the natural quotient invariant without coding all sixteen types.
    if not candidates:
        block_observations = []
        for f in range(8):
            blocks = sorted({q['unary_support'][f] for q in qs})
            if len(blocks) > 1 and sum(blocks) == 255 and all(
                    x & y == 0 for x,y in combinations(blocks,2)):
                values = [next(b for b in blocks if b >> phi[t][f] & 1) for t in range(16)]
                block_observations.append((f,blocks,values))
        choices = [(z,) for z in block_observations] + list(combinations(block_observations,2))
        for zs in choices:
            buckets = defaultdict(int)
            for t in range(16):
                buckets[tuple(z[2][t] for z in zs)] |= 1 << t
            if set(buckets.values()) == target:
                family['complete_invariant'] = {'kind':'aspect_blocks',
                    'functions':[z[0]+1 for z in zs],'aspect_partitions':[z[1] for z in zs]}
                vals = {m:list(v) for v,m in buckets.items()}
                for c in qs: c['complete_invariant_value'] = vals[c['mask']]
                break
    # Mirror of the Newman containment construction: one fixed function set
    # contains precisely one of the four aspect blocks in each model.
    if (family['complete_invariant']['kind'] == 'binary_trait_code' or
            (family['complete_invariant']['kind'] == 'aspect_blocks'
             and len(family['complete_invariant']['functions']) == 2)):
        for k in sorted(range(1,255),key=lambda k:(k.bit_count(),k)):
            blocks = []
            for q in qs:
                common = 255
                for t in bits(q['mask'],16): common &= images[t][k]
                blocks.append(common)
            if not all(blocks) or len(set(blocks)) != len(qs) or sum(blocks) != 255:
                continue
            if any(x & y for x,y in combinations(blocks,2)): continue
            truths = [sum(1 << t for t in range(16) if b & ~images[t][k] == 0) for b in blocks]
            if truths == [q['mask'] for q in qs]:
                family['complete_invariant'] = {'kind':'contained_aspect_block',
                    'function_mask':k,'aspect_partition':blocks}
                for q,b in zip(qs,blocks): q['complete_invariant_value'] = b
                break
    if family['complete_invariant']['kind'] == 'binary_trait_code':
        found = None
        # Both orientations are part of the same finite transport class.
        for orientation,pp in [('phi_partition',phi),('psi_partition',psi)]:
            for part in sorted(partitions,key=lambda p:(len(p),max(b.bit_count() for b in p)-min(b.bit_count() for b in p),p)):
                buckets = defaultdict(int)
                for t in range(16):
                    val = tuple(sorted(mask_image(pp[t],b) for b in part))
                    buckets[val] |= 1 << t
                if set(buckets.values()) == target:
                    found = (orientation,part,{m:list(v) for v,m in buckets.items()})
                    break
            if found: break
        if found:
            direction,part,vals = found
            family['complete_invariant'] = {'kind':direction,'source_partition':list(part)}
            for q in qs: q['complete_invariant_value'] = vals[q['mask']]
    for c in qs:
        c['basis_signs'] = [TM[bits(c['mask'],16)[0]][j] for j in family['basis']]
    family['summary'] = {
        'inclusion_minima':dict(Counter(str(c['minimal_inclusion_conjunction']) for c in qs)),
        'count_exact':sum(bool(c['intersection_exact_count']) for c in qs),
        'spectrum_exact':sum(bool(c['spectrum_exact_count']) for c in qs),
        'partition_exact':sum(bool(c['partition_exact_count']) for c in qs),
        'transport_exact':sum(c['transport_exact'] for c in qs)}

# Audit original numeric rows, preserving original labels, then derive corrected
# TM rows by the proved mirror of the corresponding Reinin formula.
section_indices = dict(zip(
    ['Carefree / Farsighted','Intuition / Sensory','Yielding / Obstinacy','Logic / Ethics',
     'Merry / Serious','Constructivism / Emotivism','Judiciousness / Decisiveness','Tactics / Strategy'],
    [2,3,6,7,8,9,12,13]))
source_audit = []; direct = {}; seen = Counter()
for block in src['tencer_minaev_source_blocks']:
    j = section_indices[block['section']]
    direction = block['formulas'][0]['direction']
    pos = seen[(block['section'],direction)] == 0
    seen[(block['section'],direction)] += 1
    rows = []
    for f in block['formulas']:
        s = sum(1 << A.index(a) for a in f['aspects'])
        k = sum(1 << (x-1) for x in f['functions'])
        if direction == 'direct':
            truth = sum(1 << t for t in range(16) if mask_image(psi[t],s) & ~k == 0)
        else:
            truth = sum(1 << t for t in range(16) if images[t][k] & ~s == 0)
        rows.append({**f,'truth_mask':truth})
    if direction == 'direct':
        direct[(j,pos)] = rows
        assert all(f['truth_mask'] == (rmasks[j] if pos else FULL ^ rmasks[j]) for f in rows)
    else:
        replacements = []
        for f in direct[(j,pos)]:
            b = sum(1 << A.index(a) for a in f['aspects'])
            c = sum(1 << (x-1) for x in f['functions'])
            k = mask_image(theta,b); s = mask_image(inverse(theta),c)
            truth = sum(1 << t for t in range(16) if images[t][k] & ~s == 0)
            assert truth == (tmasks[j] if pos else FULL ^ tmasks[j])
            replacements.append({'function_mask':k,'aspect_mask':s,'truth_mask':truth})
        correct_label = src['tm_trait_names'][j].split(' / ')[0 if pos else 1]
        source_audit.append({'section':block['section'],'trait':j,'value':int(pos),
            'original_label':block['label'],'correct_label':correct_label,
            'original_formulas':rows,'mirror_corrected_formulas':replacements})
assert Counter(f['truth_mask'].bit_count() for b in source_audit for f in b['original_formulas']) == {8:24,0:8}

# Explicit process relation: phi_T(2) = sigma^{+/-1}(phi_T(1)).
rho = (1,2,3,0,5,6,7,4)
sigma = compose(inverse(theta),compose(rho,theta))
for t in range(16):
    assert (phi[t][1] == sigma[phi[t][0]]) == bool(TM[t][10])
    assert (phi[t][1] == inverse(sigma)[phi[t][0]]) == (not TM[t][10])

overlap = {}
for kind in ['dichotomy','tetrad','pair']:
    fs = [f for f in families if f['kind']==kind]
    old = {refs[i]['mask'] for f in fs for i in f['class_ids']}
    new = {by_id[i]['mask'] for f in fs for i in f['class_ids']}
    oldparts = {tuple(sorted(refs[i]['mask'] for i in f['class_ids'])) for f in fs}
    newparts = {tuple(sorted(by_id[i]['mask'] for i in f['class_ids'])) for f in fs}
    overlap[kind] = {'shared_classes':len(old & new),'shared_partitions':len(oldparts & newparts),
        'new_classes':len(new-old),'new_partitions':len(newparts-oldparts),
        'shared_class_ids':[c['id'] for c in classes if c['kind']==kind and c['mask'] in old],
        'shared_partition_ids':[f['id'] for f in fs if tuple(sorted(by_id[i]['mask'] for i in f['class_ids'])) in oldparts]}

stats = {'dichotomies':15,'tetrachotomies':35,'octochotomies':15,'classes':290,
    'subset_pairs_examined':65536,'partitions_examined':4140,'subgroups':35,'cosets':179,
    'independent_triples':420,'bases_per_octochotomy':28,'linear_observable_rank':rank,
    'missing_linear_characters':missing,'shared_traits':shared,'overlap':overlap,
    'source_inverse_formulas':32,'source_empty_inverse_formulas':8,
    'mirror_checks':{'classes':290,'fields_per_class':7,'octochotomy_balanced_checks':120}}
for kind in ['dichotomy','tetrad','pair']:
    qs = [c for c in classes if c['kind']==kind]
    stats[kind] = {
        'classes':len(qs),'single_inclusion':sum(bool(c['inclusion_exact_count']) for c in qs),
        'two_inclusions':sum(c['minimal_inclusion_conjunction']==2 for c in qs),
        'inclusion_impossible':sum(c['inclusion_closure']!=c['mask'] for c in qs),
        'single_count_equality':sum(bool(c['intersection_exact_count']) for c in qs),
        'single_count_spectrum':sum(bool(c['spectrum_exact_count']) for c in qs),
        'single_partition':sum(bool(c['partition_exact_count']) for c in qs),
        'partition_conjunction':sum(c['partition_closure']==c['mask'] for c in qs),
        'single_fixed_structure':sum(c['transport_exact'] for c in qs),
        'single_image_family':sum(bool(c['image_family_exact_count']) for c in qs),
        'single_fixed_subset_equality':sum(bool(c['fixed_subset_exact_maps']) for c in qs),
        'balanced_minima':dict(Counter(str(c['balanced_partition_minimum']) for c in qs)),
        'linear_indicators':sum(c['indicator_degree']==1 for c in qs),
        'quadratic_indicators':sum(c['indicator_degree']==2 for c in qs)}

out = {'schema_version':1,'input':src,
    'encoding':{'function_mask':'bit f-1 is classical function f',
      'aspect_mask':'bit a is aspects[a], zero based',
      'type_mask':'bit t is type_order[t], zero based',
      'predicate_direction':'phi_T: functions -> aspects',
      'ordered_aspect_pairs':'zero-based aspect indices; first is phi_T(1), second phi_T(2)',
      'fourier_numerators':'divide by 16 to obtain real-character Fourier coefficients'},
    'statistics':stats,'iota':iota,'theta':[f+1 for f in theta],
    'tm_traits':dict(zip(N,TM)),'reinin_codes':dict(zip(N,rcodes)),
    'tm_codes':dict(zip(N,tcodes)),'basis_traits':basis,'trait_vectors':vectors,
    'operational_definitions':{str(j):{'function':f,'aspect_mask':s} for j,(f,s) in op_defs.items()},
    'group_elements_on_functions':g,'group_multiplication':mul,'group_inverses':iota,
    'subgroups':subgroups,'classes':classes,'families':families,
    'inclusion_predicates':dict(sorted(inclusions.items())),
    'intersection_observations':observations,
    'exact_intersection_predicates':dict(sorted(counts.items())),
    'exact_spectrum_predicates':dict(sorted(spectra.items())),
    'partition_transport_predicates':dict(sorted(partition_maps.items())),
    'source_audit':source_audit,'process_aspect_cycle_permutation':sigma}
(ROOT/'catalogue.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(ROOT/'statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in stats.items() if k!='overlap'},ensure_ascii=False,indent=2))
print('All 290 classes and all mirrored reference metrics verified.')
