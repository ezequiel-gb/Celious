import assert from 'node:assert/strict';
import {readFileSync,readdirSync,statSync,existsSync} from 'node:fs';
import path from 'node:path';
const root=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'));
const base=decodeURIComponent(root);
function walk(dir){return readdirSync(dir).filter(n=>n!=='.git').flatMap(n=>{const p=path.join(dir,n);return statSync(p).isDirectory()?walk(p):[p];});}
const files=walk(base);
const html=readFileSync(path.join(base,'index.html'),'utf8');
const js=readFileSync(path.join(base,'explorer.js'),'utf8');
const strings=Function(js.slice(0,js.indexOf('const components='))+';return copy;')();
assert.deepEqual(Object.keys(strings.en).sort(),Object.keys(strings.es).sort());
for(const [,key] of html.matchAll(/data-i="([^"]+)"/g))assert(strings.en[key]&&strings.es[key],key);
for(const [,link] of html.matchAll(/(?:href|src)="([^"]+)"/g)){
 if(link.startsWith('https://')||link.startsWith('#'))continue;
 assert(existsSync(path.join(base,link)),`Missing local link: ${link}`);
}
for(const file of files){
 assert(!/\.(?:py|pyd|pyc|zip|exe|lnk|docx|xlsx|pdf)$/i.test(file),'Unexpected implementation, package or project file');
 if(file.endsWith('.png')){assert.equal(path.basename(file),'celious-logo.png','Only approved logo is permitted');continue;}
 const s=readFileSync(file,'utf8');
 assert(!/[A-Z]:[\\/](?:Users|Documents)[\\/]/i.test(s),'Personal filesystem path');
 assert(!/sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{25,}/.test(s),'Credential-shaped text');
}
assert(!/fetch\(|XMLHttpRequest|WebSocket|localStorage/.test(js),'Explorer must not access accounts or persist local data');
for(const id of ['stage','pan-mode','view-toggle','zoom-in','zoom-out','reset-view','workflow','step-next','step-back'])assert(html.includes(`id="${id}"`),id);
console.log(`Showcase verified: ${files.length} files, matching EN/ES translations, local links, interactive controls, no application source or private identifying text.`);
