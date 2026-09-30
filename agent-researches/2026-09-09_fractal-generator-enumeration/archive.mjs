import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const ROOT=path.dirname(fileURLToPath(import.meta.url));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const original=path.resolve(ROOT,'../../Источник истины');
const comparison=fs.readdirSync(path.join(ROOT,'inputs')).map(name=>{
 const same=hash(path.join(ROOT,'inputs',name))===hash(path.join(original,name));
 assert(same,'Original changed: '+name);return{name,originalMatchesSnapshot:same};
});
fs.writeFileSync(path.join(ROOT,'results','source_original_comparison.json'),JSON.stringify(comparison,null,2)+'\n');
const files=[];function walk(p){for(const e of fs.readdirSync(p,{withFileTypes:true})){const full=path.join(p,e.name);if(e.isDirectory())walk(full);else if(full!==path.join(ROOT,'SHA256SUMS.json'))files.push({path:path.relative(ROOT,full).replaceAll('\\','/'),bytes:fs.statSync(full).size,sha256:hash(full)});}}walk(ROOT);
files.sort((a,b)=>a.path.localeCompare(b.path));
fs.writeFileSync(path.join(ROOT,'SHA256SUMS.json'),JSON.stringify({files,totalBytes:files.reduce((n,f)=>n+f.bytes,0)},null,2)+'\n');
console.log(JSON.stringify({files:files.length,totalBytes:files.reduce((n,f)=>n+f.bytes,0),originalFilesUnchanged:true}));

