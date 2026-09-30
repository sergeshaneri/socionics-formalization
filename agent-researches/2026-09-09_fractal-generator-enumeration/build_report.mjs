import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=path.dirname(fileURLToPath(import.meta.url)),R=path.join(ROOT,'results');
const get=n=>JSON.parse(fs.readFileSync(path.join(R,n),'utf8'));
const s=get('summary.json'),g=get('global_formula_compatibility.json'),c=get('coupled_summary.json');
const nf=n=>n.toLocaleString('ru-RU');
const row=a=>'| '+a.join(' | ')+' |';
const resultRows=Object.entries(s.aggregates).map(([k,r])=>row([k,nf(r.type_bases),nf(r.aspect_bases),nf(r.cases),nf(r.first_alignment),nf(r.full_identity),nf(g.summary[k].global_success)])).join('\n');
const globalRows=g.successes.map(w=>row([w.first_type,w.first_aspect,w.B.join(', '),w.C.join(', '),w.generator_positive_bits.join(''),w.full_original_projection?'да':'нет',w.b_id+':'+w.c_id+':'+w.z])).join('\n');
const coupledRows=Object.entries(c).map(([k,r])=>row([k,nf(r.type_bases),nf(r.cases),nf(r.first_alignment),nf(r.full_identity)])).join('\n');
let report=fs.readFileSync(path.join(ROOT,'REPORT_TEMPLATE.md'),'utf8').replace(/^\uFEFF/,'');
report=report.replace('{{RESULT_ROWS}}',resultRows).replace('{{GLOBAL_ROWS}}',globalRows).replace('{{COUPLED_ROWS}}',coupledRows);
if(report.includes('{{'))throw Error('Unresolved report placeholder');
fs.writeFileSync(path.join(ROOT,'README.md'),report);
let witness='# Раскладки глобально согласованных вариантов\n\nПорядок функций для аспектных строк: $1,5,6,2,8,4,3,7$. Знаки указаны в порядке $B$.\n\n';
for(const w of g.successes){
 witness+='## '+w.first_type+' — '+w.first_aspect+'\n\nID: $'+w.b_id+':'+w.c_id+':'+w.z+'$. $B=('+w.B+')$, $C=('+w.C+')$, знаки $'+w.generator_positive_bits.join('')+'$.\n\nГенераторы типов: '+w.source_type_trait_names.join('; ')+'.\n\nТипы по строкам $4\\times4$:\n\n';
 for(let i=0;i<4;i++)witness+=w.type_order.slice(4*i,4*i+4).join(' · ')+'  \n';
 witness+='\nАспекты по строкам $2\\times4$:\n\n'+w.aspect_order.slice(0,4).join(' · ')+'  \n'+w.aspect_order.slice(4).join(' · ')+'\n\nИсходная проекция родительства: '+(w.full_original_projection?'сохраняется':'меняется')+'. Все $240$ условий $G$ выполнены.\n\n';
}
fs.writeFileSync(path.join(ROOT,'WITNESSES.md'),witness);
console.log('README.md and WITNESSES.md saved');

