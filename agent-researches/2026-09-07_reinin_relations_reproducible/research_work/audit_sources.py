from pathlib import Path
from collections import Counter,defaultdict
import json,re
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'normalized_data.json').read_text())
models=D['models'];code=D['code'];aspects=D['aspects'];T={x:t for t,x in code.items()}
TI='|'.join(models)
def strip(s):return s.replace('\\','').replace('*','')
def canon_cycle(c):return min(c[i:]+c[:i] for i in range(len(c)))
def parse_formula(l):
 c=strip(l)
 m=re.search(r'\[([^\]]+)\]\s*→\s*\((.*)\)',c)
 if not m:return None
 a,f=m.groups();a=a.split('|')[0]
 # Some numeric sets follow a dimension descriptor before the first |.
 parts=f.split('|')
 f=next((s.strip() for s in parts if re.fullmatch(r'[\d\s~<>]+',s.strip())),None)
 if not f:return None
 kind='subset'
 sep=None
 if '~' in a or '~' in f:kind='partition';sep='~'
 elif any(s in a or s in f for s in ['>','<']):kind='cycle';sep='>' if '>' in a else '<'
 def nums(s):
  ns=re.findall(r'\d+',s)
  return tuple(sorted(int(d) for n in ns for d in (list(n) if len(n)>1 else [n])))
 if sep:
  aa=tuple(tuple(sorted(re.findall(r'Ч[ИЭСЛ]|Б[ИЭСЛ]',x))) for x in re.split(r'[~<>]',a))
  ff=tuple(nums(x) for x in re.split(r'[~<>]',f))
  # Reverse one sequence if arrow directions differ.
  if kind=='cycle' and (('>'in a and '<'in f) or ('<'in a and '>'in f)):ff=tuple(reversed(ff))
 else:
  aa=tuple(re.findall(r'Ч[ИЭСЛ]|Б[ИЭСЛ]',a));ff=nums(f)
 if not aa or not ff:return None
 flatf=ff if kind=='subset' else sum(ff,())
 if any(not 1<=v<=8 for v in flatf):return None
 return kind,aa,ff

def evaluate(F,t):
 kind,aa,ff=F;row=models[t]
 if kind=='subset':return set(row.index(a)+1 for a in aa)<=set(ff)
 im=tuple(tuple(sorted(row.index(a)+1 for a in pair)) for pair in aa)
 if kind=='partition':return sorted(im)==sorted(ff)
 return canon_cycle(im)==canon_cycle(ff)

res=[];blocks=[];skipped=[]
for fname in ['04-4-svezhak.md','05-oktohotomii.md']:
 active=[];sec='';secn=0
 for ln,line in enumerate((ROOT/(fname+'.clean.txt')).read_text().splitlines(),1):
  cl=strip(line).strip()
  if re.match(r'^\d+\.\s',cl) and ('#'in cl or '='in cl or fname.startswith('05')):
   sec=cl;secn=int(re.match(r'^(\d+)',cl)[1]);active=[]
  ts=re.findall(TI,cl)
  if '→' not in cl and not cl.startswith('|') and len(ts) in [2,4] and ('—'in cl or cl.startswith('#')):
   active=ts;blocks.append({'file':fname,'line':ln,'section':sec,'section_num':secn,'types':ts,'distinct':len(set(ts))==len(ts)})
  if '→'in line:
   fm=parse_formula(line)
   if fm and active:
    bad=[t for t in active if not evaluate(fm,t)]
    alltypes=[t for t in models if evaluate(fm,t)]
    res.append({'file':fname,'line':ln,'section_num':secn,'types':active,'kind':fm[0],'formula':cl,'satisfying_types':alltypes,'counterexamples':bad,'status':'fails' if bad else 'passes'})
   else:skipped.append({'file':fname,'line':ln,'reason':'no active block' if not active else 'unparsed syntax','formula':cl[:240]})
# Determine block affine directions
for b in blocks:
 xs=[code[t] for t in b['types']];U={x^xs[0] for x in xs}
 b['direction']=sorted(U);b['affine']=len(U)==len(xs) and all(x^y in U for x in U for y in U)
 if b['affine']:b['constant_traits']=[n for n,h in D['trait_masks'].items() if h and len({(x&h).bit_count()%2 for x in xs})==1]
 else:b['constant_traits']=[]
summary={'formulas':dict(Counter((r['status'] for r in res))),'by_file':{f:dict(Counter((r['status'] for r in res if r['file']==f))) for f in ['04-4-svezhak.md','05-oktohotomii.md']},'parsed_formula_count':len(res),'skipped_count':len(skipped),'block_headers':len(blocks),'invalid_block_headers':[b for b in blocks if not b['affine']]}
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('First errors',json.dumps([r for r in res if r['counterexamples']][:6],ensure_ascii=False,indent=2))
(ROOT/'source_audit.json').write_text(json.dumps({'summary':summary,'formulas':res,'blocks':blocks,'skipped':skipped},ensure_ascii=False,indent=2))
