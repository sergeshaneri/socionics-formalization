from pathlib import Path
from itertools import product,combinations,permutations
from collections import Counter,defaultdict
import json,re,hashlib,csv
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent
src=PARENT/'project_sources/03-markdown-.md'
def clean(s): return s.replace('\\','').replace('*','').strip()
rows=[[clean(x) for x in l.strip().strip('|').split('|')] for l in src.read_text().splitlines() if l.startswith('|')]
models={r[0]:r[1:] for r in rows if len(r)==9 and r[0] in ['ИЛЭ','СЭИ','ЭСЭ','ЛИИ','ЭИЭ','ЛСИ','СЛЭ','ИЭИ','ЛИЭ','ЭСИ','СЭЭ','ИЛИ','ИЭЭ','СЛИ','ЛСЭ','ЭИИ']}
traits_header=next(r[1:] for r in rows if len(r)==17 and r[0]=='ТИМ')
bits={r[0]:list(map(int,r[1:])) for r in rows if len(r)==17 and r[0] in models}
aspects=['ЧИ','БС','ЧЭ','БЛ','ЧЛ','БЭ','ЧС','БИ']
AS={r[0]:[1 if x=='+' else -1 for x in r[1:]] for r in rows if len(r)==9 and r[0] in aspects}
FN={int(re.search(r'\((\d)\)',r[0])[1]):[1 if x=='+' else -1 for x in r[1:]] for r in rows if len(r)==9 and re.search(r'\((\d)\)',r[0])}
assert len(models)==len(bits)==16 and len(AS)==len(FN)==8
assert all(set(r)==set(aspects) for r in models.values())
basis_names=['Экстраверсия','Иррациональность','Интуиция','Логика']
basis_cols=[traits_header.index(x) for x in basis_names]
code={t:sum((1-bits[t][col])<<i for i,col in enumerate(basis_cols)) for t in models}
assert len(set(code.values()))==16 and code['ИЛЭ']==0
T={x:t for t,x in code.items()}
def dot(x,y): return (x&y).bit_count()%2
trait_mask={}
for j,name in enumerate(traits_header):
 m=[m for m in range(16) if all(dot(code[t],m)==1-bits[t][j] for t in models)]
 assert len(m)==1,(name,m)
 trait_mask[name]=m[0]
# M_t maps aspects to functions; P_t=M_t M_0^-1, function permutation
base=models['ИЛЭ']
P={code[t]:tuple(row.index(a) for a in base) for t,row in models.items()}
invP={p:x for x,p in P.items()}
def comp(p,q):return tuple(p[q[i]] for i in range(len(p)))
G=[[invP[comp(P[x],P[y])] for y in range(16)] for x in range(16)]
def mul(x,y):return G[x][y]
def anf(vals):
 vals=list(vals);n=(len(vals)-1).bit_length()
 for i in range(n):
  for m in range(len(vals)):
   if m>>i&1: vals[m]^=vals[m^(1<<i)]
 return [m for m,v in enumerate(vals) if v]
def expr(ms,vs):return ' + '.join('*'.join(vs[i] for i in range(len(vs)) if m>>i&1) or '1' for m in ms) or '0'
anfs=[]
for j in range(4):
 a=anf([(mul(z&15,z>>4) ^ (z&15) ^ (z>>4))>>j&1 for z in range(256)])
 anfs.append(a)
 print('c',basis_names[j],expr(a,['e','r','n','l','E','R','N','L']))
inv={x:next(y for y in range(16) if mul(x,y)==0) for x in range(16)}
orders={}
for x in range(16):
 z=x;n=1
 while z: z=mul(z,x);n+=1
 orders[x]=n
Z=[x for x in range(16) if all(mul(x,y)==mul(y,x) for y in range(16))]
comm=lambda x,y:mul(mul(inv[x],inv[y]),mul(x,y))
print('traits',trait_mask)
print('codes',[(T[x],x,P[x],orders[x]) for x in range(16)])
print('center',[T[x] for x in Z], 'commutators', sorted({comm(x,y) for x in range(16) for y in range(16)}))
print('image correction',sorted({mul(x,y)^x^y for x in range(16) for y in range(16)}))
assert all(mul(mul(x,y),z)==mul(x,mul(y,z)) for x,y,z in product(range(16),repeat=3))
DATA={'models':models,'bits':bits,'traits_header':traits_header,'aspects':aspects,'aspect_signs':AS,'function_signs':FN,'basis_names':basis_names,'code':code,'trait_masks':trait_mask,'permutations':P,'cayley':G,'correction_anfs':anfs,'center':Z,'inverse':inv,'orders':orders}
(ROOT/'normalized_data.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2))
manifest=json.loads((ROOT/'input_manifest.json').read_text())
manifest=[x for x in manifest if not Path(x['path']).name.startswith('.')]
(ROOT/'input_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# function-coordinate form and exact Hadamard tests
AC={a:sum((AS[a][1<<i]<0)<<i for i in range(3)) for a in aspects}
FC={f:sum((FN[f][1<<i]<0)<<i for i in range(3)) for f in FN}
ACi={v:k for k,v in AC.items()};FCi={v:k for k,v in FC.items()}
M=[[FC[models[T[x]].index(ACi[u])+1] for u in range(8)] for x in range(16)]
print('M_type_aspect', [expr(anf([M[z&15][z>>4]>>i&1 for z in range(128)]),['e','r','n','l','u','v','w']) for i in range(3)])
for signs in [AS,FN]:
 mat=list(signs.values());assert all(sum(mat[t][i]*mat[t][j] for t in range(8))==8*(i==j) for i in range(8) for j in range(8))
# W Fourier of types, support transforms on aspect characters
HF=[]
for x in range(16):
 mat=[[sum((-1)**(dot(j,M[x][u])+dot(i,u)) for u in range(8)) for i in range(8)] for j in range(8)]
 HF.append(mat)
print('HF value counts',Counter(v for m in HF for row in m for v in row))
# coefficient functions on types: list their nonzero Fourier spectra over V
CF={}
for j in range(8):
 for i in range(8):
  vals=[HF[x][j][i] for x in range(16)]
  if any(vals):
   specs={h:sum(vals[x]*(-1)**dot(h,x) for x in range(16))//8 for h in range(16)}
   CF[str((j,i))]={k:v for k,v in specs.items() if v}
print('HF character coefficients',CF)
# linear subspaces V and dual, all via closure
subs={frozenset([0])}
for dim in range(4):
 for U in [u for u in list(subs) if len(u)==2**dim]:
  for v in range(1,16):
   if v not in U:subs.add(frozenset(list(U)+[u^v for u in U]))
subs=sorted(subs,key=lambda u:(len(u),sorted(u)))
def cosets(U):
 rem=set(range(16));out=[]
 while rem:
  t=min(rem);S=frozenset(t^u for u in U);out.append(S);rem-=S
 return out
def perms_group(gens,n):
 ident=tuple(range(n));seen={ident};queue=[ident]
 for g in queue:
  for h in gens:
   gh=comp(g,h)
   if gh not in seen:seen.add(gh);queue.append(gh)
 return seen
A=[tuple(x^v for x in range(16)) for v in range(16)]
L=[tuple(mul(v,x) for x in range(16)) for v in range(16)]
R=[tuple(mul(x,v) for x in range(16)) for v in range(16)]
J=perms_group(A+L,16);JR=perms_group(A+R,16);JLR=perms_group(A+L+R,16)
print('joint',len(J),len(JR),len(JLR),'intersection',[T[x] for x in range(16) if L[x] in set(A)],[T[x] for x in range(16) if R[x] in set(A)])
# common GL preserving both operations / ring automorphisms
GL=[];AUT=[]
for cols in permutations(range(1,16),4):
 mat=tuple(__import__('functools').reduce(int.__xor__,[cols[i] for i in range(4) if x>>i&1],0) for x in range(16))
 if len(set(mat))!=16:continue
 GL.append(mat)
 if all(mat[mul(x,y)]==mul(mat[x],mat[y]) for x,y in product(range(16),repeat=2)):AUT.append(mat)
print('GL',len(GL),'ringAut',len(AUT))
def orbits(items,acts,action):
 rem=set(items);out=[]
 while rem:
  x=min(rem,key=str);o={action(a,x) for a in acts};out.append(o);rem-=o
 return out
dual_acts=[tuple(next(h for h in range(16) if all(dot(m,a[x])==dot(h,x) for x in range(16))) for m in range(16)) for a in AUT]
print('dual Aut orbits',orbits(range(1,16),dual_acts,lambda a,x:a[x]))
# Every additive partition properties and ring ideals
PART=[]
for U in subs:
 C=cosets(U);cs=set(C)
 stableL=all(frozenset(L[g][x] for x in S) in cs for g in range(16) for S in C)
 stableR=all(frozenset(R[g][x] for x in S) in cs for g in range(16) for S in C)
 subgroup=all(mul(x,y) in U for x in U for y in U)
 allleft=all(frozenset(mul(g,u) for u in U) in cs for g in range(16)) if subgroup else False
 allright=all(frozenset(mul(u,g) for u in U) in cs for g in range(16)) if subgroup else False
 idealL=all((mul(g,u)^g^u) in U for g in range(16) for u in U)
 idealR=all((mul(u,g)^u^g) in U for g in range(16) for u in U)
 assert stableL==idealL and stableR==idealR
 annih=[m for m in range(1,16) if all(dot(m,u)==0 for u in U)]
 PART.append({'direction':sorted(U),'dual':annih,'blocks':[sorted(S) for S in C],'L_invariant':stableL,'R_invariant':stableR,'subgroup':subgroup,'left_cosets':allleft,'right_cosets':allright,'ring_ideal':idealL and idealR})
print('subspace categories',Counter((len(p['direction']),p['L_invariant'],p['R_invariant'],p['subgroup']) for p in PART))
print('Aut orbits partitions',{dim:[len(o) for o in orbits([frozenset(U) for U in subs if len(U)==2**dim],AUT,lambda a,U:frozenset(a[x] for x in U))] for dim in range(1,4)})
# list all subgroups by group closure
sgs={frozenset([0])}
def closure(vals):
 S=set(vals)|{0};old=-1
 while len(S)!=old:
  old=len(S);S|={mul(x,y) for x in list(S) for y in list(S)}
 return frozenset(S)
while True:
 new={closure(list(U)+[x]) for U in sgs for x in range(16)}
 if new<=sgs:break
 sgs|=new
print('all subgroups',Counter(len(u) for u in sgs),'nonadditive',len(sgs-set(subs)))
# normal/core-free order2 stabilizer etc
stab0=[x for x in range(16) if P[x][0]==0]
print('degree8 point stabilizer',[T[x] for x in stab0])
# degree8 blocks; subgroups containing point stabilizer
BLOCKS=[]
for H in sgs:
 if not set(stab0)<=H or len(H) in [2,16]:continue
 B=frozenset(P[x][0] for x in H)
 partition={frozenset(p[i] for i in B) for p in P.values()}
 BLOCKS.append({'H':sorted(H),'blocks':[[i+1 for i in sorted(b)] for b in sorted(partition,key=lambda b:sorted(b))]})
print('degree8 block systems',BLOCKS)
DATA.update({'M_coordinates':M,'aspect_codes':AC,'function_codes':FC,'HF8_numerators':HF,'HF8_type_spectra_times16':CF,'ring_automorphisms':AUT,'subspaces':PART,'subgroups':[sorted(u) for u in sorted(sgs,key=lambda u:(len(u),sorted(u)))],'function_block_systems':BLOCKS,'joint_sizes':[len(J),len(JR),len(JLR)]})
(ROOT/'normalized_data.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2))
# Common automorphisms retaining degree8 representation equivalence
conjugate_H={frozenset(mul(mul(g,h),inv[g]) for h in stab0) for g in range(16)}
AUTrep=[a for a in AUT if frozenset(a[h] for h in stab0) in conjugate_H]
repdual=[tuple(next(h for h in range(16) if all(dot(m,a[x])==dot(h,x) for x in range(16))) for m in range(16)) for a in AUTrep]
print('Aut rep',len(AUTrep),'orbits',orbits(range(1,16),repdual,lambda a,x:a[x]))
# Unique exact atomic subset conditions for cardinalities up to4
Amasks=[sum(1<<i for i in C) for k0 in range(1,5) for C in combinations(range(8),k0)]
Fmasks=Amasks[:]
Mpos=[[models[T[x]].index(a) for a in aspects] for x in range(16)]
def imask(x,A):return sum(1<<Mpos[x][i] for i in range(8) if A>>i&1)
ATOMS=[];byS=defaultdict(list)
for am in Amasks:
 images=[imask(x,am) for x in range(16)]
 for fm in Fmasks:
  if am.bit_count()>fm.bit_count():continue
  S=sum(1<<x for x in range(16) if images[x]&fm==images[x])
  if S in [0,65535]:continue
  obj=(am,fm);byS[S].append(obj)
# Minimal per same truth set, cardinality Pareto (first minimise total locations)
minimal={s:sorted(v,key=lambda p:(sum(q.bit_count() for q in p),max(q.bit_count() for q in p),p)) for s,v in byS.items()}
DIC=[]
for name,h in trait_mask.items():
 if h==0:continue
 S=sum(1<<x for x in range(16) if dot(h,x)==0)
 pairs=minimal.get(S,[])
 entry={'name':name,'mask':h,'positive_types':[T[x] for x in range(16) if S>>x&1],'atom_count':len(pairs)}
 if pairs:
  entry['minimal_atom']={'aspects':[aspects[i] for i in range(8) if pairs[0][0]>>i&1],'functions':[i+1 for i in range(8) if pairs[0][1]>>i&1]}
 DIC.append(entry)
print('dichotomy minimal',[{k:d[k] for k in ['name','atom_count','minimal_atom'] if k in d} for d in DIC])
# First-order full occupancy closure: all binary cells individually allowed by S
RECT=[]
for part in PART:
 if len(part['direction']) not in [2,4,8]:continue
 blockdata=[]
 for C in part['blocks']:
  S=sum(1<<x for x in C)
  allowed=[set(Mpos[x][a] for x in C) for a in range(8)]
  cl=[x for x in range(16) if all(Mpos[x][a] in allowed[a] for a in range(8))]
  atoms=minimal.get(S,[])
  blockdata.append({'types':C,'support_closure':cl,'minimal_atomic_formula':atoms[0] if atoms else None})
 part['block_details']=blockdata
 printline=False
RECTsummary=Counter((len(p['direction']),tuple(sorted(len(b['support_closure']) for b in p['block_details']))) for p in PART if 'block_details'in p)
print('rectangle closure counts',RECTsummary)
# Minimal equality transporter via arbitrary unordered partitions of 8
# Instead of all Bell partitions, use all perfect matchings (105) as meaningful pair-block invariants
matchings=[]
def match_rec(left,cur):
 if not left:matchings.append(tuple(sorted(cur)));return
 a=min(left)
 for b in sorted(left-{a}):match_rec(left-{a,b},cur+[tuple(sorted([a,b]))])
match_rec(set(range(8)),[])
match_sets={m:i for i,m in enumerate(matchings)}
matchPred={}
for ai,pa in enumerate(matchings):
 groups=defaultdict(list)
 for x in range(16):
  pf=tuple(sorted(tuple(sorted(Mpos[x][a] for a in pair)) for pair in pa))
  groups[pf].append(x)
 for pf,C in groups.items():
  s=sum(1<<x for x in C)
  if s!=65535:matchPred.setdefault(s,[]).append((pa,pf))
for d in DIC:
 s=sum(1<<code[t] for t in d['positive_types'])
 if s in matchPred:
  pa,pf=matchPred[s][0]
  d['pair_partition_formula']={'aspects':[[aspects[a] for a in pair] for pair in pa],'functions':[[f+1 for f in pair] for pair in pf]}
print('dichotomy matching counts',[(d['name'],len(matchPred.get(sum(1<<code[t] for t in d['positive_types']),[]))) for d in DIC])
DATA.update({'dichotomy_minimal':DIC,'ring_aut_representation':AUTrep,'subspaces':PART,'atomic_truth_sets':len(byS),'pair_partition_truth_sets':len(matchPred)})
(ROOT/'normalized_data.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2))
# Preserve exact indexed atom catalogue for subsequent canonical conjunction calculation
(ROOT/'atoms.json').write_text(json.dumps({s:v for s,v in minimal.items()}))
(ROOT/'matching_predicates.json').write_text(json.dumps(matchPred))
# Catalog 8T9: official hulpke/transgrp data/trans8.grp ninth entry (retrieved 2026-09-07)
def from_cycles(cs,n=8):
 p=list(range(n))
 for cyc in cs:
  for a,b in zip(cyc,cyc[1:]+cyc[:1]):p[a-1]=b-1
 return tuple(p)
GAPgens=[from_cycles(cs) for cs in [[[1,8],[2,3],[4,5],[6,7]],[[1,3],[2,8],[4,6],[5,7]],[[1,5],[2,6],[3,7],[4,8]],[[4,5],[6,7]]]]
GAP8=perms_group(GAPgens,8)
conjugator=None
for f in permutations(range(8)):
 fi=tuple(f.index(i) for i in range(8))
 if all(comp(comp(f,p),fi) in GAP8 for p in [P[1],P[2],P[8]]):
  conjugator=f;break
assert conjugator is not None and len(GAP8)==16
print('8T9 conjugator',[i+1 for i in conjugator])
# Correct explicit cyclic-order formulas for every otherwise-unseen trait
cyclicPred={}
for match in matchings:
 for tail in permutations(match[1:]):
  cyc=(match[0],)+tail
  def canon(c):return min(c[i:]+c[:i] for i in range(4))
  groups=defaultdict(list)
  for x in range(16):
   pf=canon(tuple(tuple(sorted(Mpos[x][a] for a in pair)) for pair in cyc))
   groups[pf].append(x)
  for pf,C in groups.items():
   s=sum(1<<x for x in C)
   if s!=65535:cyclicPred.setdefault(s,(cyc,pf))
for d in DIC:
 s=sum(1<<code[t] for t in d['positive_types'])
 if not d.get('minimal_atom') and not d.get('pair_partition_formula') and s in cyclicPred:
  pa,pf=cyclicPred[s]
  d['cyclic_formula']={'aspects':[[aspects[a] for a in pair] for pair in pa],'functions':[[f+1 for f in pair] for pair in pf]}
print('cyclic formula',[(d['name'],d.get('cyclic_formula')) for d in DIC if 'cyclic_formula' in d])
# TM formulae evaluated on the supplied Model-A slots
TMdefs=[('1-delta',[1,5],['ЧИ','БС','ЧЛ','БЭ']),('1-detached',[1,7],['ЧИ','БИ','ЧЛ','БЛ']),('2-beta',[2,6],['ЧЭ','БЛ','ЧС','БИ']),('2-detached-literal',[2,6],['ЧИ','БИ','ЧЛ','БЛ']),('2-detached-corrected',[2,8],['ЧИ','БИ','ЧЛ','БЛ']),('2-alpha',[2,6],['ЧИ','БС','ЧЭ','БЛ']),('2-implicit',[2,6],['ЧИ','БИ','ЧЭ','БЭ']),('1-alpha',[1,5],['ЧИ','БС','ЧЭ','БЛ']),('1-implicit',[1,7],['ЧИ','БИ','ЧЭ','БЭ'])]
TM=[]
for name,fs,aa in TMdefs:
 vals=[int(not all(models[T[x]][f-1] in aa for f in fs)) for x in range(16)]
 v=anf(vals)
 TM.append({'name':name,'functions':fs,'aspects':aa,'negative_anf':v,'positive_types':[T[x] for x in range(16) if not vals[x]]})
 print(name,expr(v,['e','r','n','l']),len(TM[-1]['positive_types']))
# Alternative coordinate map is inversion, check all 15
TMcoords=[inv[x] for x in range(16)]
TMpartitions=[]
for p in PART:
 U=p['direction'];blocks=[sorted(inv[x] for x in C) for C in p['blocks']]
 TMpartitions.append({'coordinate_direction':U,'blocks':blocks})
# common partitions by unordered blocks
canonpart=lambda pp:frozenset(frozenset(C) for C in pp)
intercounts={size:sum(canonpart(p['blocks']) in {canonpart(q['blocks']) for q in TMpartitions if len(q['coordinate_direction'])==size} for p in PART if len(p['direction'])==size) for size in [2,4,8]}
print('Reinin-TM common partitions',intercounts)
# Full GN function system under Model-A numbering read from Newman 2023
GNsets={'Mental':[1,2,3,4],'Accepting':[1,3,5,7],'Bold':[1,3,6,8],'Energetic':[1,2,5,8],'Excitable':[1,2,6,7],'Impressionable':[1,4,5,6],'Tensioned':[1,4,7,8]}
GNpolys={name:anf([int(FCi[u] not in fs) for u in range(8)]) for name,fs in GNsets.items()}
print('GN function formula',{name:expr(ms,['u','v','w']) for name,ms in GNpolys.items()})
# derive GN aspect structure by Ile matching (no guess external ModelG numbering)
GNcodeF={f:sum(int(f not in GNsets[n])<<i for i,n in enumerate(['Bold','Accepting','Energetic'])) for f in range(1,9)}
GNcodeA={a:GNcodeF[models['ИЛЭ'].index(a)+1] for a in aspects}
GNinvA={u:a for a,u in GNcodeA.items()}
GM=[[GNcodeF[models[T[x]].index(GNinvA[u])+1] for u in range(8)] for x in range(16)]
print('GN maps anf', [expr(anf([GM[z&15][z>>4]>>i&1 for z in range(128)]),['e','r','n','l','u','v','w']) for i in range(3)])
DATA.update({'gap8T9_generators':GAPgens,'gap8T9_conjugator':[i+1 for i in conjugator],'TM_formula_checks':TM,'TM_partitions':TMpartitions,'Reinin_TM_common_partition_counts':intercounts,'GN_function_sets':GNsets,'GN_function_anfs':GNpolys,'GN_aspect_codes_ILE_normalized':GNcodeA,'dichotomy_minimal':DIC})
(ROOT/'normalized_data.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2))
