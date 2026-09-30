import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=path.dirname(fileURLToPath(import.meta.url)),R=path.join(ROOT,'results');
const get=n=>JSON.parse(fs.readFileSync(path.join(R,n),'utf8'));
const d=get('normalized_data.json'),cs=get('aspect_bases.json'),g=get('global_formula_compatibility.json'),parents=get('parent_compatibility.json');
const bs=fs.readFileSync(path.join(R,'type_bases.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
const [bid,cid,z]=process.argv.slice(2).map(Number);
if(!Number.isInteger(bid)||!bs[bid]||!Number.isInteger(cid)||!cs[cid]||!Number.isInteger(z)||z<0||z>15)throw Error('Usage: node inspect.mjs b_id c_id z (z=0..15)');
const b=bs[bid],c=cs[cid],byX=Object.fromEntries(d.models.map(m=>[m.x,m])),A=Object.keys(d.aspectCoordinates);
const parity=x=>{let p=0;for(;x;x>>=1)p^=x&1;return p;};
const combine=(B,v)=>B.reduce((s,b,i)=>s^((v>>i&1)?b:0),0);
const first=byX[b.inverse[z]],order=c.orders[z&7],fn=order.map(a=>first.model.indexOf(a)+1);
const typeOrder=d.typeSlots.map(s=>byX[b.inverse[s^z]]);
const typeColumns=d.sourceTraitOrder.map(v=>({template_mask:v,source_mask:combine(b.B,v),source_trait:d.traits[combine(b.B,v)].name,selected_source_sign:1-parity(v&z)}));
const aspectColumns=d.sourceAspectTraitOrder.map(v=>({template_mask:v,source_mask:combine(c.C,v),selected_source_sign:1-parity(v&(z&7))}));
const prefix=[1,2,3].map(n=>Array.from({length:1<<n},(_,p)=>({code:p,
 types:d.models.filter(m=>b.B.slice(0,n).every((v,i)=>(parity(v&m.x)^(z>>i&1))===(p>>i&1))).map(m=>m.name),
 aspects:A.filter(a=>c.C.slice(0,n).every((v,i)=>(parity(v&d.aspectCoordinates[a])^(z>>i&1))===(p>>i&1)))})));
const out={b_id:bid,c_id:cid,z,B:b.B,C:c.C,type_generator_names:b.B.map(v=>d.traits[v].name),
selected_generator_signs:b.B.map((_,i)=>1-(z>>i&1)),first_type:first.name,first_aspect:order[0],
actual_first_aspect_function:fn[0],function_positive_poles:d.functionSigns[fn[0]].slice(1),
first_alignment:fn[0]===1,first_model_full_identity:fn.every((v,i)=>v===d.functionSlots[i]),
original_15_positive_invariants:first.signs.every(v=>v===1),
original_trait_values:d.rules.map((r,i)=>({trait:r.name,sign:first.signs[i]})),
global_transported_formula_compatibility:g.successes.some(s=>s.b_id===bid&&s.c_id===cid&&s.z===z),
original_parent_map:parents[bid].c_id===cid&&parents[bid].preserves_entire_original_parent_map,
type_order:typeOrder.map(m=>m.name),aspect_order:order,actual_functions_in_aspect_order:fn,reference_function_order:d.functionSlots,
type_columns:typeColumns,aspect_columns:aspectColumns,
type_matrix:typeOrder.map(m=>({type:m.name,signs:typeColumns.map(q=>1-(parity(q.source_mask&m.x)^(1-q.selected_source_sign)))})),
aspect_matrix:order.map(a=>({aspect:a,signs:aspectColumns.map(q=>1-(parity(q.source_mask&d.aspectCoordinates[a])^(1-q.selected_source_sign)))})),
abstract_levels:prefix};
const dir=path.join(R,'cases');fs.mkdirSync(dir,{recursive:true});const target=path.join(dir,bid+'_'+cid+'_'+z+'.json');fs.writeFileSync(target,JSON.stringify(out,null,2)+'\n');console.log(target);console.log(JSON.stringify({first:out.first_type,aspect:out.first_aspect,first_alignment:out.first_alignment,first_model_full_identity:out.first_model_full_identity,original_15_positive_invariants:out.original_15_positive_invariants,global:out.global_transported_formula_compatibility}));

