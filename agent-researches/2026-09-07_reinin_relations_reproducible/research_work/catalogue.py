from pathlib import Path
from collections import Counter,defaultdict
from itertools import combinations
import json,re,heapq
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'normalized_data.json').read_text());A=json.loads((ROOT/'source_audit.json').read_text())
models=D['models'];code=D['code'];T={x:t for t,x in code.items()};G=D['cayley'];P={int(x):v for x,v in D['permutations'].items()};asp=D['aspects']
# Map original numbered tetrachotomies by header trait masks
aliases={'Верт':1,'Бс/Пр':5,'Ит/Сн':4,'Дм/Ар':12,'+/-':13,'Ус/Уп':9,'Лг/Эт':8,'Сб/Об':11,'Кн/Эм':10,'Пц/Рз':14,'?/!':15,'Рс/Рш':7,'Тк/Ст':6,'Наль':2,'Таль':3}
sections={}
for l in (ROOT/'04-4-svezhak.md.clean.txt').read_text().splitlines():
 c=l.replace('\\','').replace('*','').strip();m=re.match(r'^(\d+)\.\s.*=',c)
 if m:
  masks=sorted({v for k,v in aliases.items() if k in c})
  assert len(masks)==3 and masks[0]^masks[1]^masks[2]==0,(c,masks)
  sections[tuple(masks)]=int(m[1])
assert len(sections)==35
# Evaluate and retain minimal representative for each primitive truth set.
ordinary={int(s):[tuple(v) for v in vs] for s,vs in json.loads((ROOT/'atoms.json').read_text()).items()}
matching={int(s):v for s,v in json.loads((ROOT/'matching_predicates.json').read_text()).items()}
pred={}
for s,vs in ordinary.items():
 a,f=vs[0];pred[s]={'kind':'subset','A':[asp[i] for i in range(8) if a>>i&1],'F':[i+1 for i in range(8) if f>>i&1],'cost':(0,a.bit_count()+f.bit_count(),1)}
for s,vs in matching.items():
 if s in pred:continue
 a,f=vs[0];pred[s]={'kind':'partition','A':[[asp[i] for i in pair] for pair in a],'F':[[i+1 for i in pair] for pair in f],'cost':(1,16,1)}
# Add the two cyclic orientations for process/result; sufficient to classify all characters.
a=[['ЧИ','БИ'],['ЧЛ','БЛ'],['ЧС','БС'],['ЧЭ','БЭ']];f=[[1,7],[2,8],[3,5],[4,6]]
for b in [0,1]:
 s=sum(1<<x for x in range(16) if (x&14).bit_count()%2==b)
 pred[s]={'kind':'cycle','A':a if b==0 else [a[0]]+list(reversed(a[1:])),'F':f,'cost':(1,16,1)}

def classify(S):
 goal=sum(1<<x for x in S);cands=[s for s in pred if s&goal==goal]
 # Nontrivial universal state and independent truth masks. Lexicographic Dijkstra.
 q=[((0,0,0),65535,())];best={65535:(0,0,0)}
 while q:
  cost,state,path=heapq.heappop(q)
  if cost!=best[state]:continue
  if state==goal:return [dict(pred[s],truth_set=[x for x in range(16) if s>>x&1]) for s in path],cost
  for s in cands:
   new=state&s
   if new==state:continue
   nc=tuple(x+y for x,y in zip(cost,pred[s]['cost']))
   if nc<best.get(new,(999,9999,999)):
    best[new]=nc;heapq.heappush(q,(nc,new,path+(s,)))
 raise ValueError(S)

parts=[]
for p in D['subspaces']:
 if len(p['direction']) not in [2,4,8]:continue
 p=dict(p);size=len(p['direction'])
 p['id']=('T%02d'%sections[tuple(p['dual'])]) if size==4 else (('O%02d'%p['direction'][1]) if size==2 else 'D%02d'%p['dual'][0])
 p['group_type']=None
 if p['subgroup']:
  o=[D['orders'][str(x)] for x in p['direction']]
  p['group_type']='C4' if size==4 and 4 in o else ('C2^2' if size==4 else ('C2' if size==2 else ('C2^3' if 4 not in o else ('C4xC2' if all(G[x][y]==G[y][x] for x in p['direction'] for y in p['direction']) else 'D8'))))
 p['blocks_detail']=[]
 for C in p['blocks']:
  clauses,cost=classify(C)
  unionf={a:sorted({models[T[x]].index(a)+1 for x in C}) for a in asp}
  closure=[x for x in range(16) if all(models[T[x]].index(a)+1 in unionf[a] for a in asp)]
  row={'types':[T[x] for x in C],'codes':C,'clauses':clauses,'cost':cost,'support_closure':[T[x] for x in closure],'all_positional_bounds':unionf,'relative_operators':{T[x]:{T[y]:T[G[y][D['inverse'][str(x)]]] for y in C} for x in C}}
  p['blocks_detail'].append(row)
 parts.append(p)
parts.sort(key=lambda p:p['id'])
# Correct four erroneous listed blocks by other blocks/section duals and majority membership
corrections=[]
for b in A['blocks']:
 if b['file'].startswith('04') and not b['affine']:
  target=next(p for p in parts if p['id']=='T%02d'%b['section_num'])
  old=set(b['types']);new=max([set(z['types']) for z in target['blocks_detail']],key=lambda z:len(z&old))
  corrections.append({'line':b['line'],'section':b['section_num'],'old':b['types'],'new':sorted(new),'remove':sorted(old-new),'add':sorted(new-old)})
# Mechanical corrected subset targets (minimum union of actual images); preserve where same-cardinality possible
for r in A['formulas']:
 if r['status']!='fails':continue
 if r['kind']=='subset':
  aa=re.findall(r'Ч[ИЭСЛ]|Б[ИЭСЛ]',r['formula'].split(']')[0])
  goodT=r['types']
  for b in corrections:
   if r['file'].startswith('04') and set(r['types'])==set(b['old']):goodT=b['new']
  ff=sorted({models[t].index(a)+1 for t in goodT for a in aa})
  r['corrected_target_union']=ff
# Missing octa blocks by actual pairing directions
existing={frozenset(b['types']) for b in A['blocks'] if b['file'].startswith('05')}
missing=[{'octa':p['id'],'pair':b['types']} for p in parts if p['id'].startswith('O') for b in p['blocks_detail'] if frozenset(b['types']) not in existing]
print('catalogue primitives',len(pred),'parts',len(parts),'clause counts',Counter((p['id'][0],tuple(b['cost'])[0],tuple(b['cost'])[2]) for p in parts for b in p['blocks_detail']))
print('four corrections',corrections)
print('missing',len(missing),missing)
# Source independent report catalogue and audit
(ROOT/'catalogue.json').write_text(json.dumps({'parts':parts,'membership_corrections':corrections,'missing_octa_pairs':missing,'language_cost':'(relational predicates, total A and F cardinalities, clauses) lexicographic'},ensure_ascii=False,indent=2))
(ROOT/'source_audit.json').write_text(json.dumps(A,ensure_ascii=False,indent=2))
