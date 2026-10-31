import assert from 'node:assert/strict';
import {readFileSync,readdirSync,statSync,existsSync} from 'node:fs';
import path from 'node:path';
const root=path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'));
const base=decodeURIComponent(root);
function walk(dir){return readdirSync(dir).filter(n=>n!=='.git').flatMap(n=>{const p=path.join(dir,n);return statSync(p).isDirectory()?walk(p):[p];});}
const files=walk(base);
const html=readFileSync(path.join(base,'index.html'),'utf8');
const js=readFileSync(path.join(base,'explorer.js'),'utf8');
const readme=readFileSync(path.join(base,'README.md'),'utf8');
const overview=readFileSync(path.join(base,'PROJECT-OVERVIEW.md'),'utf8');
const strings=Function(js.slice(0,js.indexOf('const components='))+';return copy;')();
assert.deepEqual(Object.keys(strings.en).sort(),Object.keys(strings.es).sort());
for(const [,key] of html.matchAll(/data-i="([^"]+)"/g))assert(strings.en[key]&&strings.es[key],key);
assert.equal(strings.en.contactLink,"Let's talk");
assert.equal(strings.en.contactButton,"Let's talk");
assert.equal(strings.en.closingTitle,"Let's talk");
assert.equal(strings.es.contactLink,'Hablemos');
assert.equal(strings.es.contactButton,'Hablemos');
assert.equal(strings.es.closingTitle,'Hablemos');
assert.equal(strings.en.eyebrow,'DOCUMENTS · MEMORY · AI');
assert.equal(strings.es.eyebrow,'DOCUMENTOS · MEMORIA · IA');
assert.equal(strings.en.headlineSuffix,'Your Local Digital Second Brain');
assert.equal(strings.es.headlineSuffix,'Tu segundo cerebro digital local');
assert.equal(strings.en.practicalTitle,'What does this mean in practice?');
assert.equal(strings.es.practicalTitle,'¿Y esto cómo se traduce en el día a día?');
for(const [,link] of html.matchAll(/(?:href|src)="([^"]+)"/g)){
 if(link.startsWith('https://')||link.startsWith('#'))continue;
 assert(existsSync(path.join(base,link)),`Missing local link: ${link}`);
}
const ids=new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(([,id])=>id));
assert.equal(ids.size,[...html.matchAll(/\bid="([^"]+)"/g)].length,'Duplicate HTML id');
for(const [,link] of html.matchAll(/href="#([^"]+)"/g))assert(ids.has(link),`Missing page anchor: ${link}`);
assert(html.includes('https://ezequielgomez.net/index-en.html#contacto'));
assert(js.includes('https://ezequielgomez.net/index-es.html#contacto'));
assert(readme.includes('https://ezequielgomez.net/index-en.html#contacto'));
assert(readme.includes('https://ezequielgomez.net/index-es.html#contacto'));
for(const text of [html,js,readme,overview]){
 assert(!/Discuss a solution|Hablemos de una solución/i.test(text),'Previous contact wording remains');
 assert(!/github\.com\/ezequiel-gb\/Celious\/releases/i.test(text),'Application release link remains');
 assert(!/Celious-Windows-x64|Download for Windows|Get Celious|Descargar para Windows|Obtener Celious|download.{0,30}Windows|descargar.{0,30}Windows/i.test(text),'Public application download call-to-action remains');
 assert(!/[A-Z]:[\\/](?:Users|Documents)[\\/]/i.test(text),'Personal filesystem path');
 assert(!/sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{25,}/.test(text),'Credential-shaped text');
}
assert(!/Fresh installation|Configure Celious\.cmd|MCP Server\.cmd|--approval-mode/.test(overview),'Self-service application deployment instructions remain');
assert(!existsSync(path.join(base,'INSTALLATION.md')),'Public installation guide remains');
for(const file of files){
 assert(!/\.(?:py|pyd|pyc|zip|exe|lnk|docx|xlsx|pdf)$/i.test(file),'Unexpected implementation, package or project file');
 if(file.endsWith('.png')){assert.equal(path.basename(file),'celious-logo.png','Only approved logo is permitted');continue;}
 const s=readFileSync(file,'utf8');
 assert(!/[A-Z]:[\\/](?:Users|Documents)[\\/]/i.test(s),'Personal filesystem path');
 assert(!/sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{25,}/.test(s),'Credential-shaped text');
}
assert(!/fetch\(|XMLHttpRequest|WebSocket|localStorage/.test(js),'Explorer must not access accounts or persist local data');
for(const id of ['stage','pan-mode','view-toggle','zoom-in','zoom-out','reset-view','workflow','step-next','step-back'])assert(html.includes(`id="${id}"`),id);
for(const id of ['contact-nav','contact-hero','contact-closing'])assert(html.includes(`id="${id}"`),id);
console.log(`Showcase verified: ${files.length} files, matching EN/ES translations, live contact destinations, local links, interactive controls, no public app downloads or application source.`);
