const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const source=name=>fs.readFileSync(path.join(__dirname,'../ui',name),'utf8');
async function run(){
 const scripts=[],timers=[],notices=[];
 const document={documentElement:{lang:'en'},createElement:tag=>({tag,style:{},setAttribute(){},remove(){this.removed=true;}}),body:{appendChild:n=>(n.tag==='script'?scripts:notices).push(n)}};
 vm.runInNewContext(source('device-loader.js'),{document,setTimeout:(fn,ms)=>timers.push({fn,ms})});
 assert.equal(scripts.length,1);assert.equal(scripts[0].src,'/i18n.js');
 scripts[0].onerror();assert.equal(timers[0].ms,3000);assert.match(notices[0].textContent,/Retrying/);
 timers.shift().fn();assert.equal(scripts[1].src,'/i18n.js');scripts[1].onload();
 assert.equal(notices[0].removed,true);assert.equal(scripts[2].src,'/live.js');
 scripts[2].onerror();timers.shift().fn();scripts[3].onload();assert.equal(scripts.length,4);
 const ids=['ota-hint','ota-file-label','firmware-update','firmware-status','firmware-picker','firmware-selected','firmware-file','language','firmware-form','current-build-id'];
 const nodes=Object.fromEntries(ids.map(id=>[id,{files:[],click(){}}]));nodes.language.onclick=()=>{};
 let tab,visible,calls=0,fail=true,pending=false;
 const jobs=new Map();let seq=0;
 const doc={documentElement:{lang:'en'},getElementById:id=>nodes[id],querySelector:()=>({addEventListener:(event,fn)=>tab=fn}),addEventListener:(event,fn)=>visible=fn};
 vm.runInNewContext(source('ota-live.js'),{document:doc,localStorage:{getItem:()=>null},MttlI18n:{text:()=>''},AbortController,
  setTimeout:(fn,ms)=>{jobs.set(++seq,{fn,ms});return seq;},clearTimeout:id=>jobs.delete(id),fetch:async()=>{calls++;if(fail)throw Error('offline');if(pending)return new Promise(()=>{});return {ok:true,json:async()=>({ota_ready:true,build_id:'0123456789abcdef'})};}});
 await new Promise(setImmediate);assert.equal(calls,1);assert.equal(nodes['firmware-update'].textContent,'Update');assert.equal(nodes['firmware-update'].disabled,true);
 const retry=[...jobs.values()].find(x=>x.ms===3000);assert.ok(retry);fail=false;await retry.fn();
 assert.equal(calls,2);assert.equal(nodes['current-build-id'].textContent,'0123456789abcdef');assert.equal(nodes['firmware-update'].disabled,false);
 await tab();assert.equal(calls,3);doc.hidden=true;visible();assert.equal(calls,3);doc.hidden=false;await visible();await new Promise(setImmediate);assert.equal(calls,4);
 pending=true;tab();tab();assert.equal(calls,5);assert.ok([...jobs.values()].some(x=>x.ms===8000));
 console.log(JSON.stringify({passed:true,scope:'Sequential script retries, status failure recovery, tab/visibility refresh, single flight and timeout; mocked DOM/network'}));
}
run().catch(e=>{console.error(e);process.exitCode=1;});
