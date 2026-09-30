import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const R=path.join(path.dirname(fileURLToPath(import.meta.url)),'results');
const get=n=>JSON.parse(fs.readFileSync(path.join(R,n),'utf8'));
const d=get('normalized_data.json'),cs=get('aspect_bases.json'),pp=get('parent_compatibility.json');
const bs=fs.readFileSync(path.join(R,'type_bases.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
const A=Object.keys(d.aspectCoordinates),byX=Object.fromEntries(d.models.map(m=>[m.x,m]));
const parity=x=>{let p=0;for(;x;x>>=1)p^=x&1;return p;};
const combine=(B,v)=>B.reduce((s,b,i)=>s^((v>>i&1)?b:0),0);
const pair=v=>Array.from({length:v.length/2},(_,i)=>v.slice(2*i,2*i+2).sort().join(','));
function pred(mu,r){const v=r.aspects.map(a=>mu[A.indexOf(a)]);if(r.kind==='inclusion')return v.every(f=>r.functions.includes(f));const a=pair(v),b=pair(r.functions);if(r.kind==='matching')return [...a].sort().join('|')===[...b].sort().join('|');return [0,1,2,3].some(k=>a.every((p,i)=>p===b[(i+k)%4]));}
const observed={};
for(const first of d.models){
 // L maps old aspect at canonical slot to aspect at that slot in the first model.
 const L=A.map(a=>first.model[byX[0].mu[A.indexOf(a)]-1]);
 const table=d.models.map(t=>{const mu=L.map(a=>t.mu[A.indexOf(a)]);return d.rules.map(r=>{const p=r.positive.every(q=>pred(mu,q)),n=r.negative.every(q=>pred(mu,q));return p&&!n?1:n&&!p?0:-1;});});
 observed[first.x]={L,table};
}
const successes=[],failureExamples=[],summary={};
for(const stage of ['strict_generations','ancient_first','unrestricted'])for(const signs of ['fixed','all'])summary[stage+'_'+signs]={global_success:0,by_first_type:{},prefix_coupled_success:0,full_original_projection_success:0};
let tested=0;
for(const b of bs)for(let z=0;z<16;z++){
 const first=byX[b.inverse[z]],z3=z&7;
 const matchingCs=cs.filter(c=>c.orders[z3].every((a,k)=>first.mu[A.indexOf(a)]===d.functionSlots[k]));
 if(!matchingCs.length)continue;
 assert.equal(matchingCs.length,1);const c=matchingCs[0];tested++;
 let bad=null;
 for(let ti=0;ti<d.models.length&&!bad;ti++){const t=d.models[ti];for(let ri=0;ri<15;ri++){const r=d.rules[ri],expected=1-(parity(combine(b.B,r.mask)&t.x)^parity(r.mask&z)),actual=observed[first.x].table[ti][ri];if(expected!==actual){bad={type:t.name,slot_trait:r.name,expected,actual};break;}}}
 if(bad){if(failureExamples.length<12)failureExamples.push({b_id:b.id,c_id:c.id,z,first_type:first.name,first_failure:bad});continue;}
 const prefix=pp[b.id].c_id===c.id,fullParent=prefix&&pp[b.id].preserves_entire_original_parent_map;
 const record={b_id:b.id,c_id:c.id,z,B:b.B,C:c.C,first_type:first.name,first_aspect:c.orders[z3][0],
  type_order:d.typeSlots.map(s=>byX[b.inverse[s^z]].name),aspect_order:c.orders[z3],
  source_type_trait_names:b.B.map(v=>d.traits[v].name),generator_positive_bits:b.B.map((_,i)=>1-(z>>i&1)),
  prefix_coupled:prefix,full_original_projection:fullParent,
  checked_type_trait_conditions:240};
 successes.push(record);
 for(const stage of ['strict_generations','ancient_first','unrestricted']){if(stage==='strict_generations'&&(!b.strict||!c.strict)||stage==='ancient_first'&&(!b.ancient||!c.ancient))continue;
  for(const signs of z===0?['fixed','all']:['all']){const s=summary[stage+'_'+signs];s.global_success++;s.by_first_type[first.name]=(s.by_first_type[first.name]||0)+1;s.prefix_coupled_success+=Number(prefix);s.full_original_projection_success+=Number(fullParent);}
 }
}
fs.writeFileSync(path.join(R,'global_formula_compatibility.json'),JSON.stringify({testedFirstModelIdentities:tested,criterion:'All 16 types and all 15 signed traits: formula structures transported by L on aspects must equal the transformed character table specified by B,z. Functions fixed.',summary,successes,failureExamples},null,2)+'\n');
console.log(JSON.stringify({tested,summary,successes},null,2));

