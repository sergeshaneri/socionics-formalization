"""Independent exhaustive checks of the reconstructed formulas and catalogue."""
from pathlib import Path
from itertools import product
from collections import Counter
import json, csv

ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'normalized_data.json').read_text())
C=json.loads((ROOT/'catalogue.json').read_text())
T={x:t for t,x in D['code'].items()}
M={x:{a:D['models'][T[x]].index(a)+1 for a in D['aspects']} for x in range(16)}
P={int(x):tuple(p) for x,p in D['permutations'].items()}
def a(x): return (x>>1)&1
def b(x): return ((x>>2)^(x>>3))&1
def q(x): return a(x)*b(x)
def dot(h,x): return (h&x).bit_count()%2
def ring(x,y): return 12*b(x)*a(y)
def mul(x,y): return x^y^ring(x,y)
def inv(x): return x^(12*q(x))
def compose(p,r): return tuple(p[r[i]] for i in range(len(p)))
checks={}
checks['model_bijections']=16
assert all(len(set(m.values()))==8 for m in M.values())
for x,y in product(range(16),repeat=2):
    assert P[mul(x,y)]==compose(P[x],P[y])
    assert mul(x,y)==D['cayley'][x][y]
    assert mul(x,inv(x))==0
    assert mul(x,x)==12*q(x)
    assert mul(x,y)^mul(y,x)==12*(b(x)*a(y)^a(x)*b(y))
checks['permutation_products']=256
for x,y,z in product(range(16),repeat=3):
    assert mul(mul(x,y),z)==mul(x,mul(y,z))
    assert mul(x,y^z)==mul(x,y)^x^mul(x,z)
    assert mul(x^y,z)==mul(x,z)^z^mul(y,z)
    assert ring(ring(x,y),z)==ring(x,ring(y,z))==0
checks['associativity_and_two_brace_identities']=4096
for p,r,s in product(range(8),repeat=3):
    phi=lambda u,v: ((u>>1)&1)*(v&1)
    assert phi(p,r)^phi(p^r,s)==phi(r,s)^phi(p,r^s)
checks['central_cocycle_triples']=512
for x,y in product(range(16),repeat=2):
    u=x^y
    assert mul(y,inv(x))==u^12*(b(u)*a(x))
    for h in range(16):
        assert dot(h,mul(x,y))==dot(h,x)^dot(h^(2*dot(h,12)*b(x)),y)
        assert dot(h,mul(y,x))==dot(h,x)^dot(h^(12*dot(h,12)*a(x)),y)
checks['relative_operator_pairs']=256
checks['fourier_action_entries']=8192

def canon_cycle(parts):
    p=tuple(tuple(sorted(s)) for s in parts)
    return min(p[i:]+p[:i] for i in range(len(p)))
def eval_clause(clause,x):
    aa,ff=clause['A'],clause['F']
    if clause['kind']=='subset': return {M[x][v] for v in aa}<=set(ff)
    images=[tuple(sorted(M[x][v] for v in pair)) for pair in aa]
    if clause['kind']=='partition': return sorted(images)==sorted(tuple(sorted(pair)) for pair in ff)
    if clause['kind']=='cycle': return canon_cycle(images)==canon_cycle(ff)
    raise ValueError(clause)

block_count=0
for p in C['parts']:
    blocks=p['blocks_detail']
    assert sorted(x for s in blocks for x in s['codes'])==list(range(16))
    for s in blocks:
        for cl in s['clauses']:
            assert [x for x in range(16) if eval_clause(cl,x)]==cl['truth_set'],(p['id'],cl)
        truth=[x for x in range(16) if all(eval_clause(cl,x) for cl in s['clauses'])]
        assert truth==s['codes'],(p['id'],s)
        visible=[h for h in p['dual'] if h<=11]
        expected=[x for x in range(16) if all(dot(h,x^s['codes'][0])==0 for h in visible)]
        assert set(expected)=={D['code'][t] for t in s['support_closure']}
        block_count+=1
checks['exact_catalogue_blocks']=block_count
checks['support_closure_theorem_blocks']=block_count

f=tuple(v-1 for v in D['gap8T9_conjugator']);fi=tuple(f.index(i) for i in range(8))
gens=[tuple(p) for p in D['gap8T9_generators']]
group={tuple(range(8))};queue=list(group)
for g in queue:
    for h in gens:
        v=compose(g,h)
        if v not in group: group.add(v);queue.append(v)
assert {compose(compose(f,p),fi) for p in P.values()}==group
checks['8T9_conjugated_elements']=16
assert len(group)==16

# Independent verification of the two affine coordinate formulas on A and F.
oldA=D['aspect_codes'];oldF={int(k):v for k,v in D['function_codes'].items()}
newA=D['GN_aspect_codes_ILE_normalized']
gnsets=D['GN_function_sets']
newF={f:sum(int(f not in gnsets[n])<<i for i,n in enumerate(['Bold','Accepting','Energetic'])) for f in range(1,9)}
for x in range(16):
    e=x&1;r=(x>>1)&1;n=(x>>2)&1;l=(x>>3)&1
    for asp in D['aspects']:
        u=oldA[asp]&1;v=(oldA[asp]>>1)&1;w=(oldA[asp]>>2)&1
        expected=(u^e)+2*(v^e^n^b(x)*(v^w))+4*(w^e^r^n^b(x)*(v^w))
        assert oldF[M[x][asp]]==expected
        u=newA[asp]&1;v=(newA[asp]>>1)&1;w=(newA[asp]>>2)&1
        expected=(u^e)+2*(v^r)+4*(w^e^e*r^n^r*u^(e^n^l)*v)
        assert newF[M[x][asp]]==expected
checks['old_and_GN_affine_model_entries']=256

tm=[]
for h,fs,aa,label,flip in [
    (5,[1,5],['ЧИ','БС','ЧЛ','БЭ'],'1-delta',0),
    (4,[1,7],['ЧИ','БИ','ЧЛ','БЛ'],'1-detached',0),
    (9,[2,6],['ЧЭ','БЛ','ЧС','БИ'],'2-beta',0),
    (8,[2,8],['ЧИ','БИ','ЧЛ','БЛ'],'2-detached corrected',0),
    (11,[2,6],['ЧИ','БС','ЧЭ','БЛ'],'2-alpha',0),
    (10,[2,8],['ЧИ','БИ','ЧЭ','БЭ'],'2-implicit corrected',1),
    (7,[1,5],['ЧИ','БС','ЧЭ','БЛ'],'1-alpha',0),
    (6,[1,7],['ЧИ','БИ','ЧЭ','БЭ'],'1-implicit',0)]:
    good=[]
    for x in range(16):
        holds=all(D['models'][T[x]][j-1] in aa for j in fs)
        assert int(not holds)==dot(h,inv(x))^flip,(label,x)
        if holds: good.append(T[x])
    tm.append({'label':label,'functions':fs,'aspects':aa,'mask':h,'constant_flip':flip,'positive_types':good})
checks['TM_corrected_predicate_entries']=128

# Common automorphisms: explicit five-parameter formula in (a,b,c,d).
def decode(x): return a(x),b(x),x&1,(x>>2)&1
def encode(a0,b0,c0,d0): return c0+2*a0+4*d0+8*(b0^d0)
automorphisms=set()
for al,be,ga,de,ep in product(range(2),repeat=5):
    p=[]
    for x in range(16):
        aa,bb,cc,dd=decode(x)
        p.append(encode(aa,bb,cc^al*aa^be*bb,dd^ga*aa^de*bb^ep*cc))
    automorphisms.add(tuple(p))
assert automorphisms=={tuple(p) for p in D['ring_automorphisms']}
checks['explicit_common_automorphisms']=32

# Subspace criteria verified separately from the original enumeration code.
for p in D['subspaces']:
    u=p['direction'];hasK=12 in u
    assert p['subgroup']==(hasK or all(a(x)==0 for x in u) or all(b(x)==0 for x in u))
    assert p['L_invariant']==(hasK or all(a(x)==0 for x in u))
    assert p['R_invariant']==(hasK or all(b(x)==0 for x in u))
checks['subspace_algebraic_criteria']=67

out={'status':'PASS','checks':checks,'TM_corrected_formulas':tm,
     'catalogue_counts':dict(Counter(p['id'][0] for p in C['parts']))}
(ROOT/'verification_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
