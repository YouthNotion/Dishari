// Browser test for the light/dark theme logic (theme-init.js + site.js), driven over
// the Chrome DevTools Protocol. Node 22+, no dependencies.
//
// It emulates OS colour-scheme changes and checks that:
//   - an invalid saved value (e.g. "auto") is ignored, so the site follows the OS (#6)
//   - a saved "light" or "dark" choice wins over OS changes
//   - with nothing saved, the site follows the OS live
//   - clicking the switch applies, saves and persists the choice, and updates aria-checked
//
// Usage (with the dev server running). Exits non-zero if any check fails:
//   node tools/theme_test.mjs <chrome-binary> http://127.0.0.1:8000/
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs"; import { tmpdir } from "node:os"; import { join } from "node:path";
const [bin, url] = process.argv.slice(2);
const c = spawn(bin, ["--headless=new","--no-sandbox","--disable-gpu","--remote-debugging-port=9336",`--user-data-dir=${mkdtempSync(join(tmpdir(),"th-"))}`,"about:blank"],{stdio:"ignore"});
const sleep=(ms)=>new Promise(r=>setTimeout(r,ms)); let t, failures=0;
try {
  for (let i=0;i<50;i++){try{t=await (await fetch("http://127.0.0.1:9336/json")).json();break;}catch{await sleep(200);}}
  const ws=new WebSocket(t.find(x=>x.type==="page").webSocketDebuggerUrl); await new Promise(r=>ws.addEventListener("open",r,{once:true}));
  let id=0; const pend=new Map(); ws.addEventListener("message",e=>{const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id);}});
  const send=(method,params={})=>new Promise(r=>{const i=++id;pend.set(i,m=>r(m.result));ws.send(JSON.stringify({id:i,method,params}));});
  const ev=async(expr)=>(await send("Runtime.evaluate",{expression:expr,returnByValue:true,awaitPromise:true})).result.value;
  const os=(v)=>send("Emulation.setEmulatedMedia",{features:[{name:"prefers-color-scheme",value:v}]});
  const theme=()=>ev("document.documentElement.dataset.theme");
  const check=(name, got, want)=>{const ok=got===want; if(!ok) failures++; console.log(`${ok?"✓":"✗"} ${name}: got ${got}, want ${want}`);};
  const load=async(saved, osPref)=>{ await os(osPref); await send("Page.navigate",{url}); await sleep(700);
    await ev(saved===null?"localStorage.removeItem('theme')":`localStorage.setItem('theme', ${JSON.stringify(saved)})`);
    await send("Page.reload",{}); await sleep(800); };

  await load("auto","light");
  check('saved "auto" (invalid), OS light → initial', await theme(), "light");
  await os("dark"); await sleep(200);
  check('saved "auto" (invalid), OS switches to dark → follows OS  [the bug]', await theme(), "dark");

  await load("dark","dark");
  await os("light"); await sleep(200);
  check('saved "dark", OS switches to light → keeps choice', await theme(), "dark");

  await load(null,"light");
  await os("dark"); await sleep(200);
  check("no saved value, OS switches to dark → follows OS", await theme(), "dark");

  await ev("document.querySelector('[data-theme-toggle]').click()"); await sleep(100);
  check("click switch → theme", await theme(), "light");
  check("click switch → saved value", await ev("localStorage.getItem('theme')"), "light");
  check("click switch → aria-checked", await ev("document.querySelector('[data-theme-toggle]').getAttribute('aria-checked')"), "false");
  await send("Page.reload",{}); await sleep(800);
  check("after reload → choice persists", await theme(), "light");
  await os("dark"); await sleep(200);
  check("after explicit choice, OS changes → ignored", await theme(), "light");
  ws.close();
} finally { c.kill(); }
process.exitCode = failures ? 1 : 0;
