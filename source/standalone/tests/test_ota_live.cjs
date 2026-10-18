const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ids=['ota-hint','ota-file-label','firmware-update','firmware-status','firmware-picker','firmware-selected','firmware-file','language','firmware-form','firmware-expected','ota-token','current-build-id'];
const elements=Object.fromEntries(ids.map(id=>[id,{textContent:'',value:'',files:[],click(){this.clicked=true;}}]));
const document={documentElement:{lang:'ko'},getElementById:id=>elements[id]};
elements.language.onclick=()=>{document.documentElement.lang=document.documentElement.lang==='ko'?'en':'ko';};
let posts=[],valid=true,confirmed=true,responseText=null,networkError=null,statusBuild='0123456789abcdef';
const storage=new Map();
const context={document,localStorage:{setItem:(k,v)=>storage.set(k,v),getItem:k=>storage.get(k),removeItem:k=>storage.delete(k)},MttlI18n:{text:()=>document.documentElement.lang==='en'?'No file selected':'선택된 파일 없음'},confirm:()=>confirmed,AbortController,setTimeout:()=>1,clearTimeout(){},fetch:async(url,options={})=>{
 if(url.endsWith('/status'))return {ok:true,json:async()=>({ota_ready:true,build_id:statusBuild})};
 posts.push({url,options});if(networkError)throw networkError;return {ok:valid,status:valid?200:400,text:async()=>responseText??JSON.stringify({written:valid,activated:valid})};
}};
async function run(){
 vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);
 await new Promise(resolve=>setImmediate(resolve));assert.equal(elements['firmware-update'].disabled,false);
 elements.language.onclick();assert.match(elements['ota-hint'].textContent,/power/);assert.equal(elements['firmware-update'].textContent,'Update');
 await elements['firmware-form'].onsubmit({preventDefault(){}});assert.equal(posts.length,0);assert.match(elements['firmware-status'].textContent,/Select a valid/);
 elements['firmware-file'].files=[{name:'image.bin',size:100}];
 await elements['firmware-form'].onsubmit({preventDefault(){}});assert.equal(posts.length,0);
 elements['firmware-file'].files=[{name:'image.fwr',size:100}];confirmed=false;
 await elements['firmware-form'].onsubmit({preventDefault(){}});assert.equal(posts.length,0);
 confirmed=true;await elements['firmware-form'].onsubmit({preventDefault(){}});
 assert.equal(posts.length,1);assert.equal(posts[0].url,'/api/firmware/upload');assert.equal(posts[0].options.headers['Content-Type'],'application/x-mttl-fwr');assert.equal(posts[0].options.headers['X-MTTL-SHA256'],undefined);assert.equal(posts[0].options.headers['X-MTTL-OTA-Token'],undefined);
 assert.equal(elements['firmware-update'].disabled,true);assert.match(elements['firmware-status'].textContent,/completed/);
 // Failure stays disabled: no blind retry after uncertain activation.
 valid=false;vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 await elements['firmware-form'].onsubmit({preventDefault(){}});assert.equal(elements['firmware-update'].disabled,true);assert.match(elements['firmware-status'].textContent,/uncertain/);
 assert.match(elements['firmware-status'].textContent,/HTTP 400/);
 responseText='<html><body>Owner checkpoint/hold failed</body></html>';
 vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 await elements['firmware-form'].onsubmit({preventDefault(){}});assert.match(elements['firmware-status'].textContent,/HTTP 400.*Owner checkpoint\/hold failed/);assert.ok(!elements['firmware-status'].textContent.includes('<html>'));
 valid=true;responseText='';vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));await elements['firmware-form'].onsubmit({preventDefault(){}});assert.match(elements['firmware-status'].textContent,/HTTP 200.*Empty response/);
 networkError=new Error('Failed to fetch');vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));await elements['firmware-form'].onsubmit({preventDefault(){}});assert.match(elements['firmware-status'].textContent,/Network\/connection error: Failed to fetch/);
 networkError=new Error('Aborted');networkError.name='AbortError';vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));await elements['firmware-form'].onsubmit({preventDefault(){}});assert.match(elements['firmware-status'].textContent,/Timeout \(180 s\)/);
 assert.equal(elements['current-build-id'].textContent,statusBuild);
 storage.set('mttl.ota.pending-build',statusBuild);vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));assert.match(elements['firmware-status'].textContent,/Build verification: OK/);assert.equal(storage.has('mttl.ota.pending-build'),false);
 storage.set('mttl.ota.pending-build','ffffffffffffffff');vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));assert.match(elements['firmware-status'].textContent,/NOT MATCHED/);assert.equal(storage.has('mttl.ota.pending-build'),true);
 elements['firmware-file'].files=[{name:'comMTTL-W01_2.0.8-build-1122334455667788.fwr',size:100}];await elements['firmware-form'].onsubmit({preventDefault(){}});assert.equal(storage.get('mttl.ota.pending-build'),'1122334455667788');
 networkError=null;responseText=JSON.stringify({written:true,activated:true,restore_version:'1.0.68'});
 vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 assert.match(elements['ota-hint'].textContent,/stock 1.0.66.*1.0.68/);
 await elements['firmware-form'].onsubmit({preventDefault(){}});assert.match(elements['firmware-status'].textContent,/Restore completed.*1.0.68/);assert.equal(storage.has('mttl.ota.pending-build'),false);
 responseText=JSON.stringify({already_installed:true,activated:false,rebooting:false});
 vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../ui/ota-live.js'),'utf8'),context);await new Promise(resolve=>setImmediate(resolve));
 await elements['firmware-form'].onsubmit({preventDefault(){}});assert.match(elements['firmware-status'].textContent,/already installed/);assert.equal(elements['firmware-update'].disabled,false);assert.equal(storage.has('mttl.ota.pending-build'),false);
 elements.language.onclick();assert.match(elements['firmware-status'].textContent,/이미 설치된 펌웨어/);
 console.log(JSON.stringify({checks:31,failed:0,scope:'Mock OTA dashboard form; no device writes'}));
}
run().catch(e=>{console.error(e);process.exitCode=1;});
