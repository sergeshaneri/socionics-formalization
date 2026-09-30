import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const ROOT=path.dirname(fileURLToPath(import.meta.url)),R=path.join(ROOT,'results');
const get=n=>JSON.parse(fs.readFileSync(path.join(R,n),'utf8'));
const d=get('normalized_data.json'),summary=get('summary.json'),C=get('aspect_bases.json'),P=get('parent_compatibility.json');
const B=fs.readFileSync(path.join(R,'type_bases.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
const byX=Object.fromEntries(d.models.map(m=>[m.x,m]));
const stats={};const selected=[];
for(const scope of ['prefix_coupled','full_original_projection'])for(const stage of ['strict_generations','ancient_first','unrestricted'])for(const signs of ['fixed','all'])stats[scope+'_'+stage+'_'+signs]={type_bases:0,cases:0,first_alignment:0,full_identity:0,by_first_type:{},witnesses:[]};
const detail=Object.fromEntries(d.models.map(m=>[m.name,Array.from({length:8},(_,z)=>get('identity_'+m.name+'_'+z+'.json'))]));
for(const b of B){const p=P[b.id];if(p.c_id===null)continue;
 for(const scope of ['prefix_coupled','full_original_projection']){
  if(scope==='full_original_projection'&&!p.preserves_entire_original_parent_map)continue;
  for(const stage of ['strict_generations','ancient_first','unrestricted']){
   if(stage==='strict_generations'&&!b.strict||stage==='ancient_first'&&!b.ancient)continue;
   const c=C[p.c_id];assert(stage!=='strict_generations'||c.strict);assert(stage!=='ancient_first'||c.ancient);
   for(const signs of ['fixed','all']){const s=stats[scope+'_'+stage+'_'+signs];s.type_bases++;
    for(let z=0;z<(signs==='fixed'?1:16);z++){const m=byX[b.inverse[z]],v=detail[m.name][z&7][c.id];s.cases++;s.first_alignment+=Number(v.function_of_first_aspect===1);s.full_identity+=Number(v.full_identity);
     const t=s.by_first_type[m.name]??={cases:0,first_alignment:0,full_identity:0};t.cases++;t.first_alignment+=Number(v.function_of_first_aspect===1);t.full_identity+=Number(v.full_identity);
     if(v.full_identity&&!s.witnesses.some(w=>w.first_type===m.name))s.witnesses.push({b_id:b.id,c_id:c.id,z,B:b.B,C:c.C,first_type:m.name,first_aspect:v.first_aspect});
     if(scope==='full_original_projection'&&stage==='unrestricted'&&signs==='all'&&v.full_identity)selected.push({b_id:b.id,c_id:c.id,z,first_type:m.name});
    }
   }
  }
 }
}
fs.writeFileSync(path.join(R,'coupled_summary.json'),JSON.stringify(stats,null,2)+'\n');
fs.writeFileSync(path.join(R,'all_full_identity_original_parent_cases.json'),JSON.stringify(selected,null,2)+'\n');
console.log(JSON.stringify(Object.fromEntries(Object.entries(stats).map(([k,s])=>[k,{bases:s.type_bases,cases:s.cases,first:s.first_alignment,full:s.full_identity,types:Object.entries(s.by_first_type).filter(([t,v])=>v.full_identity).map(([t,v])=>t)}])),null,2));

