import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const ROOT=path.dirname(fileURLToPath(import.meta.url));
const IN=path.join(ROOT,'inputs'),OUT=path.join(ROOT,'results');
fs.mkdirSync(OUT,{recursive:true});
const read=n=>fs.readFileSync(path.join(IN,n),'utf8').replace(/^\uFEFF/,'');
const write=(n,x)=>fs.writeFileSync(path.join(OUT,n),typeof x==='string'?x:JSON.stringify(x,null,2)+'\n');
const lines=read('markdown таблицы.md').split(/\r?\n/);
const clean=s=>s.replace(/[\\*]/g,'').trim();
const cells=l=>l.split('|').slice(1,-1).map(clean);
const models=lines.map(cells).filter(c=>c.length===9&&/^[ИЛЭСБЧ][ИЛЭСЭЧ]{2}$/.test(c[0])&&c.slice(1).every(x=>/^[ЧБ][ИЛСЭ]$/.test(x))).map(c=>({name:c[0],model:c.slice(1)}));
assert.equal(models.length,16);
const A=['ЧИ','БС','ЧЭ','БЛ','ЧЛ','БЭ','ЧС','БИ'];
for(const m of models)assert.equal(new Set(m.model).size,8);
const aspectRows=lines.map(cells).filter(c=>c.length===9&&A.includes(c[0])&&c.slice(1).every(v=>['+','-'].includes(v)));
assert.equal(aspectRows.length,8);
const aspectSigns=Object.fromEntries(aspectRows.map(c=>[c[0],c.slice(1).map(v=>v==='+'?1:0)]));
const functionRows=lines.map(cells).filter(c=>c.length===9&&/\([1-8]\)/.test(c[0])&&c.slice(1).every(v=>['+','-'].includes(v)));
assert.equal(functionRows.length,8);
const functionSigns=Object.fromEntries(functionRows.map(c=>[Number(c[0].match(/\(([1-8])\)/)[1]),c.slice(1).map(v=>v==='+'?1:0)]));
const Fslots=[1,5,6,2,8,4,3,7];
const parity=x=>{let r=0;for(;x;x>>=1)r^=x&1;return r;};
const bits=(vs)=>vs.reduce((v,x,i)=>v|(x<<i),0);
const sections=read('spisok-formul-arp.md').split(/^### /m).slice(1).map(s=>({name:clean(s.split('\n')[0]),lines:s.split('\n').filter(l=>l.includes('→'))})).filter(s=>s.lines.length);
function parseRule(line){const [a,f]=line.split('→');const aa=a.match(/ЧИ|БС|ЧЭ|БЛ|ЧЛ|БЭ|ЧС|БИ/g); const ff=(f.match(/\b[1-8]\b/g)||[]).map(Number);return{aspects:aa,functions:ff,kind:line.includes('\\>')?'cycle':line.includes('\\~')?'matching':'inclusion',source:line.trim()};}
const rules=sections.map((s,i)=>({id:i,name:s.name,positive:s.lines.slice(0,s.lines.length/2).map(parseRule),negative:s.lines.slice(s.lines.length/2).map(parseRule)}));
assert.equal(rules.length,15);
const pairKeys=v=>Array.from({length:v.length/2},(_,i)=>v.slice(i*2,i*2+2).sort().join(','));
function satisfies(mu,r,fixedCycle=false){const image=r.aspects.map(a=>mu[A.indexOf(a)]);
 if(r.kind==='inclusion')return image.every(f=>r.functions.includes(f));
 const pp=pairKeys(image),qq=pairKeys(r.functions);
 if(r.kind==='matching')return [...pp].sort().join('|')===[...qq].sort().join('|');
 return (fixedCycle?[0]:[0,1,2,3]).some(k=>pp.every((p,i)=>p===qq[(i+k)%4]));
}
for(const r of rules)for(const pol of ['positive','negative'])for(const q of r[pol]){
 assert(q.aspects.every(a=>A.includes(a)));assert(q.functions.every(f=>f>=1&&f<=8));
 assert.equal(new Set(q.aspects).size,q.aspects.length);
 assert.equal(new Set(q.functions).size,q.functions.length);
}
for(const m of models){m.mu=A.map(a=>m.model.indexOf(a)+1);m.signs=rules.map(r=>{const p=r.positive.every(q=>satisfies(m.mu,q)),n=r.negative.every(q=>satisfies(m.mu,q));assert.notEqual(p,n,m.name+' '+r.name);return Number(p);});}
const canonicalT=[0,1,7,11]; // E, irrationality, merry, democracy
for(const m of models)m.x=bits(canonicalT.map(i=>1-m.signs[i]));
assert.equal(new Set(models.map(m=>m.x)).size,16);
const modelByX=Object.fromEntries(models.map(m=>[m.x,m]));
const traitByMask={0:{id:-1,name:'Существование',mask:0,generation:0}};
for(const r of rules){const matches=Array.from({length:15},(_,i)=>i+1).filter(mask=>models.every(m=>(1-parity(mask&m.x))===m.signs[r.id]));assert.equal(matches.length,1,r.name);r.mask=matches[0];r.generation=r.id<3?(r.id===0?1:2):r.id<11?3:4;traitByMask[r.mask]={id:r.id,name:r.name,mask:r.mask,generation:r.generation};}
const AX=Object.fromEntries(A.map(a=>[a,bits([1,6,4].map(i=>1-aspectSigns[a][i]))]));
const FX=Object.fromEntries(Fslots.map(f=>[f,bits([1,6,4].map(i=>1-functionSigns[f][i]))]));
assert.equal(new Set(Object.values(AX)).size,8);assert.equal(new Set(Object.values(FX)).size,8);
const aspectByX=Object.fromEntries(A.map(a=>[AX[a],a]));
const sourceTraitOrder=[0,1,14,15,8,9,6,7,4,5,10,11,12,13,2,3];
const sourceAspectTraitOrder=[0,1,6,7,4,5,2,3];
const typeSlots=models.map(m=>m.x);
const aspectSlots=A.map(a=>AX[a]);
assert.deepEqual(aspectSlots,Fslots.map(f=>FX[f]));
for(let col=0;col<8;col++)for(const a of A)assert.equal(aspectSigns[a][col],1-parity(sourceAspectTraitOrder[col]&AX[a]));
for(let col=0;col<8;col++)for(const f of Fslots)assert.equal(functionSigns[f][col],1-parity(sourceAspectTraitOrder[col]&FX[f]));
const tableSigns=lines.map(cells).filter(c=>c.length===17&&models.some(m=>m.name===c[0])&&c.slice(1).every(v=>v==='0'||v==='1'));
assert.equal(tableSigns.length,16);
const mismatches=[];
for(const row of tableSigns){const m=models.find(m=>m.name===row[0]);row.slice(1).forEach((s,i)=>{const expected=1-parity(sourceTraitOrder[i]&m.x);if(Number(s)!==expected)mismatches.push({type:m.name,column:i,trait:traitByMask[sourceTraitOrder[i]].name,source:Number(s),formulaDerived:expected});});}
const span=B=>B.reduce((S,b)=>S.concat(S.map(s=>s^b)),[0]);
function bases(n){const out=[];function rec(B,S){if(B.length===n){out.push(B);return}for(let b=1;b<1<<n;b++)if(!S.includes(b))rec([...B,b],S.concat(S.map(s=>s^b)));}rec([],[0]);return out;}
const TB=bases(4),AB=bases(3);assert.equal(TB.length,20160);assert.equal(AB.length,168);
const evalB=(B,x)=>bits(B.map(b=>parity(b&x)));
const combine=(B,c)=>B.reduce((r,b,i)=>r^((c>>i&1)?b:0),0);
const modes=['strict_generations','ancient_first','unrestricted'];
const isTstrict=B=>B[0]===1&&[2,3].includes(B[1])&&traitByMask[B[2]].generation===3&&traitByMask[B[3]].generation===4;
const isTancient=B=>B.slice(0,2).every(b=>[1,2,3].includes(b))&&traitByMask[B[2]].generation===3&&traitByMask[B[3]].generation===4;
const isAstrict=C=>C[0]===1&&[2,3].includes(C[1])&&C[2]>=4;
const isAancient=C=>C.slice(0,2).every(c=>[1,2,3].includes(c))&&C[2]>=4;
const tref=TB.map((B,id)=>{const inv=Array(16);for(let x=0;x<16;x++)inv[evalB(B,x)]=x;
 return{id,B,strict:isTstrict(B),ancient:isTancient(B),inverse:inv,
 trait_order:sourceTraitOrder.map(mask=>combine(B,mask)),
 unsigned_type_order:typeSlots.map(s=>modelByX[inv[s]].name),
 level_subgroups:[1,2,3,4].map(n=>span(B.slice(0,n)).sort((a,b)=>a-b))};});
const aref=AB.map((C,id)=>{const inv=Array(8);for(let x=0;x<8;x++)inv[evalB(C,x)]=x;
 return{id,C,strict:isAstrict(C),ancient:isAancient(C),inverse:inv,
 trait_order:sourceAspectTraitOrder.map(mask=>combine(C,mask)),
 orders:Array.from({length:8},(_,z)=>aspectSlots.map(s=>aspectByX[inv[s^z]]))};});
write('normalized_data.json',{models,aspectSigns,functionSigns,aspectCoordinates:AX,functionCoordinates:FX,traits:traitByMask,rules,typeSlots,aspectSlots,functionSlots:Fslots,canonicalTypeBasis:canonicalT.map(i=>rules[i].mask),sourceTraitOrder,sourceAspectTraitOrder});
write('source_audit.json',{rawSourceSignMismatches:mismatches,notes:['The computation derives type signs from the 15 explicit formula predicates and validates XOR closure independently.','Long formula source has repeated BI and missing BL in democracy matching; see line 679. Canonical predicates are parsed from spisok-formul-arp.md.','Cycle predicate allows cyclic rotation, preserves orientation; fixed-start sensitivity is also computed.']});
write('type_bases.jsonl',tref.map(x=>JSON.stringify(x)).join('\n')+'\n');
write('aspect_bases.json',aref);
// Reproduce the preceding turn: all 8! bijections, no restriction to Model A.
const permutations=[];function perms(v,left){if(!left.length){permutations.push(v);return}for(const x of left)perms([...v,x],left.filter(y=>y!==x));}perms([],Fslots);
const positiveCounts=rules.map(()=>0),joint=[],jointFixed=[],first11=[];
const domains=Object.fromEntries(A.map(a=>[a,Fslots.filter(f=>rules.slice(0,11).flatMap(r=>r.positive).filter(r=>r.aspects.includes(a)).every(r=>r.functions.includes(f)))]));
for(const mu of permutations){const ok=rules.map(r=>r.positive.every(q=>satisfies(mu,q)));ok.forEach((v,i)=>{if(v)positiveCounts[i]++;});if(ok.slice(0,11).every(Boolean))first11.push(mu);if(ok.every(Boolean))joint.push(mu);if(rules.every(r=>r.positive.every(q=>satisfies(mu,q,true))))jointFixed.push(mu);}
assert.equal(joint.length,1);assert.deepEqual(joint[0],modelByX[0].mu);
write('formula_verification.json',{permutations:permutations.length,formulaLines:rules.flatMap(r=>r.positive).length,positiveCounts:rules.map((r,i)=>({name:r.name,count:positiveCounts[i]})),joint,first11,jointFixed,domains,allModelsClassified:true});
// All outcomes are stored exactly in a factorized form. A row refers to 168 aspect bases.
// Bit c_id in hexadecimal masks denotes the corresponding successful aspect basis.
// z is shared on inherited generators; its fourth bit is new at level four.
const cached=Array.from({length:16},()=>Array.from({length:8},()=>null));
for(const m of models)for(let z3=0;z3<8;z3++){
 let first=0n,full=0n;const countByMode={};
 for(const mode of modes)countByMode[mode]={total:0,first:0,full:0,byFirstAspect:{},witness:null};
 const detail=[];
 for(const c of aref){const order=c.orders[z3],a0=order[0],f=m.mu[A.indexOf(a0)],ok1=f===1,okFull=order.every((a,k)=>m.mu[A.indexOf(a)]===Fslots[k]);
  if(ok1)first|=1n<<BigInt(c.id);if(okFull)full|=1n<<BigInt(c.id);
  detail.push({c_id:c.id,first_aspect:a0,function_of_first_aspect:f,full_identity:okFull,function_pole_bits:functionSigns[f].slice(1).join('')});
  for(const mode of modes){if(mode==='strict_generations'&&!c.strict||mode==='ancient_first'&&!c.ancient)continue;
    const s=countByMode[mode];s.total++;s.first+=Number(ok1);s.full+=Number(okFull);s.byFirstAspect[a0]=(s.byFirstAspect[a0]||0)+1;
    if(okFull&&s.witness===null)s.witness=c.id;
  }
 }
 cached[m.x][z3]={first:first.toString(16).padStart(42,'0'),full:full.toString(16).padStart(42,'0'),countByMode};
 write('identity_'+m.name+'_'+z3+'.json',detail);
}
const aggregates={};
for(const mode of modes)for(const signs of ['fixed','all'])aggregates[mode+'_'+signs]={type_bases:0,aspect_bases:aref.filter(c=>mode==='unrestricted'||(mode==='strict_generations'?c.strict:c.ancient)).length,cases:0,first_alignment:0,full_identity:0,fixed_original_15_formulas:0,full_identity_and_original_15:0,by_first_type:{},first_aspect_counts:{},witnesses:[]};
const fd=fs.openSync(path.join(OUT,'outcomes.csv'),'w');
fs.writeSync(fd,'b_id,z,first_type,x,z3,first_alignment_c_mask,full_identity_c_mask\n');
let buffer='';
for(const b of tref){
 for(const mode of modes)if(mode==='unrestricted'||(mode==='strict_generations'?b.strict:b.ancient))for(const signs of ['fixed','all'])aggregates[mode+'_'+signs].type_bases++;
 for(let z=0;z<16;z++){const x=b.inverse[z],m=modelByX[x],z3=z&7,cc=cached[x][z3];
  buffer+=[b.id,z,m.name,x,z3,cc.first,cc.full].join(',')+'\n';
  for(const mode of modes){if(mode==='strict_generations'&&!b.strict||mode==='ancient_first'&&!b.ancient)continue;
   const ss=cc.countByMode[mode];
   for(const signs of (z===0?['fixed','all']:['all'])){const s=aggregates[mode+'_'+signs];s.cases+=ss.total;s.first_alignment+=ss.first;s.full_identity+=ss.full;
    if(m.signs.every(v=>v===1)){s.fixed_original_15_formulas+=ss.total;s.full_identity_and_original_15+=ss.full;}
    const t=s.by_first_type[m.name]??={cases:0,first_alignment:0,full_identity:0};
    t.cases+=ss.total;t.first_alignment+=ss.first;t.full_identity+=ss.full;
    for(const [a,n]of Object.entries(ss.byFirstAspect))s.first_aspect_counts[a]=(s.first_aspect_counts[a]||0)+n;
    if(ss.full&& !s.witnesses.some(w=>w.first_type===m.name))s.witnesses.push({b_id:b.id,B:b.B,c_id:ss.witness,C:aref[ss.witness].C,z,first_type:m.name,aspect_order:aref[ss.witness].orders[z3]});
   }
  }
 }
 if(buffer.length>1024*1024){fs.writeSync(fd,buffer);buffer='';}
}
fs.writeSync(fd,buffer);fs.closeSync(fd);
// Compatibility with the original parent projection pi0(mask)=mask & 7.
// Full preservation requires c_i=pi0(b_i), and pi0(b4)=0.
// For arbitrary B,C the induced new projection is pi_BC(sum v_i b_i)=sum_{i<3}v_i c_i.
const parent=[];
for(const b of tref){const projected=b.B.slice(0,3).map(x=>x&7);const c=aref.find(c=>c.C.every((v,i)=>v===projected[i]));
 parent.push({b_id:b.id,projected_prefix_rank:Math.log2(new Set(span(projected)).size),c_id:c?.id??null,
 new_generator_is_old_kernel:b.B[3]===8,preserves_entire_original_parent_map:!!c&&b.B[3]===8,
 first_type_pair:b.level_subgroups[2].length===8?[modelByX[b.inverse[0]].name,modelByX[b.inverse[8]].name]:null});
}
write('parent_compatibility.json',parent);
write('summary.json',{schema:1,definition:'B: ordered basis of type characters; C: ordered basis of aspect characters; shared inherited sign z[0:3]; new sign z[3]. Fixed function labels and order.',
generationDefinitions:{strict:'b1=E,b2 in {N,E+N},b3 in gen3,b4 in gen4; c1=E,c2 in {N,E+N},c3 outside ancient plane',ancient:'first two are distinct elements of ancient plane minus zero; later as strict',unrestricted:'all ordered independent bases'},aggregates,
parentCompatibleCounts:Object.fromEntries(modes.map(mode=>[mode,parent.filter(p=>{const b=tref[p.b_id];return p.preserves_entire_original_parent_map&&(mode==='unrestricted'||(mode==='strict_generations'?b.strict:b.ancient));}).length])),
rawSourceSignMismatchCount:mismatches.length,allFormulaPositiveType:modelByX[0].name,
totalFactorizedRows:tref.length*16,totalExpandedCases:tref.length*16*aref.length,
assertions:'All independent-basis counts, source model bijections, character closure, predicate exclusivity, H8 tables, and formula joint uniqueness checked with Node assert.'});
const manifests=[];
for(const n of fs.readdirSync(IN)){const b=fs.readFileSync(path.join(IN,n));manifests.push({path:'inputs/'+n,bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')});}
write('source_manifest.json',manifests);
console.log(JSON.stringify({aggregates,parentCompatibleCounts:JSON.parse(fs.readFileSync(path.join(OUT,'summary.json'))).parentCompatibleCounts,rawSourceSignMismatchCount:mismatches.length},null,2));

