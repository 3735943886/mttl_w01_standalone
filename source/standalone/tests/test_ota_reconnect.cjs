const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
async function scenario(mode){
 const ids=['ota-hint','ota-file-label','firmware-update','firmware-status','firmware-picker','firmware-selected','firmware-file','language','firmware-form','current-build-id'];
 const nodes=Object.fromEntries(ids.map(id=>[id,{files:[],click(){}}]));nodes.language.onclick=()=>{};
 let now=0,serial=0,posts=0,reloads=0,build='0123456789abcdef',offline=false;const jobs=new Map();
 const document={documentElement:{lang:'en'},getElementById:id=>nodes[id]};
 const location={reload(){reloads++;}};
 const context={document,location,Date:{now:()=>now},localStorage:{getItem:()=>null,removeItem(){},setItem(){}},MttlI18n:{text:()=>''},confirm:()=>true,AbortController,
  setTimeout:(fn,ms)=>{jobs.set(++serial,{fn,ms});return serial;},clearTimeout:id=>jobs.delete(id),
  fetch:async(url)=>{if(url.includes('/upload')){posts++;return {ok:true,text:async()=>JSON.stringify(mode==='restore'?{written:true,activated:true,restore_version:'1.0.66'}:mode==='same'?{already_installed:true}:{written:true,activated:true})};}
   if(offline)throw Error('offline');return {ok:true,json:async()=>({ota_ready:true,build_id:build})};}};
 const flush=()=>new Promise(setImmediate);
 async function step(ms){const entry=[...jobs.entries()].find(([,job])=>job.ms===ms);assert.ok(entry,'missing timer '+ms);jobs.delete(entry[0]);await entry[1].fn();await flush();}
 vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../ui/ota-live.js'),'utf8'),context);await flush();
 nodes['firmware-file'].files=[{name:'firmware.fwr',size:100}];await nodes['firmware-form'].onsubmit({preventDefault(){}});
 if(mode==='same'||mode==='restore'){assert.equal(jobs.size,0);assert.equal(reloads,0);return;}
 assert.equal(nodes['firmware-picker'].disabled,true);await step(5000);assert.equal(reloads,0,'old build must not trigger reload');
 offline=true;await step(3000);assert.equal(reloads,0);
 if(mode==='timeout'){now=120000;await step(3000);assert.match(nodes['firmware-status'].textContent,/timed out/);assert.equal(nodes['firmware-update'].disabled,true);assert.equal(jobs.size,0);}
 else{offline=false;build='fedcba9876543210';await step(3000);assert.equal(reloads,1);assert.equal(location.hash,'#firmware');assert.equal(jobs.size,0);}
 assert.equal(posts,1,'no automatic upload retry');
}
(async()=>{for(const mode of ['success','timeout','same','restore'])await scenario(mode);console.log(JSON.stringify({passed:true,scenarios:['old-build response','offline reboot','new-build reload','120s timeout','same-image no reboot','stock restore no reload','no repeated upload']}));})().catch(e=>{console.error(e);process.exitCode=1;});
