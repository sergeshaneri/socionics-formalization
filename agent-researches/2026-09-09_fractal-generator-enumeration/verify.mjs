import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import readline from 'node:readline';
import {fileURLToPath} from 'node:url';
const ROOT=path.dirname(fileURLToPath(import.meta.url)),R=path.join(ROOT,'results');
const get=n=>JSON.parse(fs.readFileSync(path.join(R,n),'utf8'));
const d=get('normalized_data.json'),summary=get('summary.json'),g=get('global_formula_compatibility.json'),cs=get('aspect_bases.json');
const bs=fs.readFileSync(path.join(R,'type_bases.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
const A=Object.keys(d.aspectCoordinates),parity=x=>{let p=0;for(;x;x>>=1)p^=x&1;return p;};
const evalB=(B,x)=>B.reduce((y,b,i)=>y|(parity(b&x)<<i),0);
const byX=Object.fromEntries(d.models.map(m=>[m.x,m])),eta=byX[0].mu;
assert.equal(bs.length,20160);assert.equal(new Set(bs.map(b=>b.B.join(','))).size,20160);
assert.equal(cs.length,168);assert.equal(new Set(cs.map(c=>c.C.join(','))).size,168);
for(const b of bs)for(let z=0;z<16;z++)assert.equal(evalB(b.B,b.inverse[z]),z);
for(const c of cs)for(let z=0;z<8;z++)assert.equal(evalB(c.C,c.inverse[z]),z);
for(const f of get('source_manifest.json'))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT,f.path))).digest('hex'),f.sha256);
const masks={};let directAspectCases=0;
for(const t of d.models)for(let z3=0;z3<8;z3++){
 let p=0n,q=0n;
 for(const c of cs){const sourceOrder=d.aspectSlots.map(s=>A.find(a=>evalB(c.C,d.aspectCoordinates[a])===(s^z3)));
  assert.deepEqual(sourceOrder,c.orders[z3]);
  const f=sourceOrder.map(a=>t.model.indexOf(a)+1);
  if(f[0]===1)p|=1n<<BigInt(c.id);
  if(f.every((v,i)=>v===d.functionSlots[i]))q|=1n<<BigInt(c.id);
  directAspectCases++;
 }
 masks[t.name+'_'+z3]=[p.toString(16).padStart(42,'0'),q.toString(16).padStart(42,'0')];
}
let rows=0;
const reader=readline.createInterface({input:fs.createReadStream(path.join(R,'outcomes.csv')),crlfDelay:Infinity});
for await(const line of reader){if(line.startsWith('b_id'))continue;const [bid,z,name,x,z3,p,q]=line.split(',');assert.equal(+bid,Math.floor(rows/16));assert.equal(+z,rows%16);assert.equal(bs[+bid].inverse[+z],+x);assert.equal(+z3,+z&7);assert.equal(byX[+x].name,name);assert.deepEqual([p,q],masks[name+'_'+z3]);rows++;}
assert.equal(rows,322560);
// Independent global verification: derive affine coordinate maps from relative Model A rows.
// No use of the formula predicate cache and no search over B,C.
function fitAffine(values,n){const offset=values[0],B=[];for(let bit=0;bit<n;bit++){let mask=0;for(let j=0;j<n;j++)mask|=(((values[1<<j]^offset)>>bit&1)<<j);B.push(mask);}
 for(let x=0;x<1<<n;x++)if((evalB(B,x)^offset)!==values[x])return null;return{B,offset};}
const independentlyDerived=[],excluded=[];
for(const first of d.models){
 const L=A.map(a=>first.model[eta[A.indexOf(a)]-1]);
 const invL=Object.fromEntries(L.map((a,i)=>[a,A[i]]));
 const y=Array(16);
 for(const t of d.models){const transformed=t.model.map(a=>invL[a]),target=d.models.find(m=>m.model.join(',')===transformed.join(','));assert(target);y[t.x]=target.x;}
 const tf=fitAffine(y,4);assert(tf);
 const ay=Array(8);
 for(const a of A)ay[d.aspectCoordinates[a]]=d.aspectCoordinates[invL[a]];
 const af=fitAffine(ay,3);assert(af);
 const b=bs.find(b=>b.B.join(',')===tf.B.join(',')),c=cs.find(c=>c.C.join(',')===af.B.join(','));assert(b&&c);
 if((tf.offset&7)!==af.offset){excluded.push({first_type:first.name,B:tf.B,C:af.B,type_offset:tf.offset,required_aspect_offset:af.offset,inherited_type_offset:tf.offset&7,reason:'Inherited signs disagree under the shared-origin convention'});continue;}
 independentlyDerived.push({b_id:b.id,c_id:c.id,z:tf.offset,first_type:first.name});
}
const key=r=>[r.b_id,r.c_id,r.z,r.first_type].join(':');
assert.deepEqual(independentlyDerived.map(key).sort(),g.successes.map(key).sort());
assert.equal(independentlyDerived.length,12);
assert.equal(summary.rawSourceSignMismatchCount,0);
assert.equal(get('formula_verification.json').permutations,40320);
assert.equal(get('formula_verification.json').joint.length,1);
const out={passed:true,source_hashes_verified:true,allTypeBases:bs.length,allAspectBases:cs.length,
directAspectCases,outcomeRowsVerified:rows,factorizedExpandedCases:rows*cs.length,
independentGlobalDerivation:independentlyDerived,excludedBySharedSigns:excluded,
method:'Derived affine transformations directly from relative Model A rows, independently of transported-formula evaluation.'};
fs.writeFileSync(path.join(R,'verification.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));

