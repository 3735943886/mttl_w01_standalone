/* Shared timer editor; zero minutes means unregistered. */
(function(root){
 'use strict';
 function valid(minutes,schedule){
  if(!Array.isArray(minutes)||minutes.length!==4||minutes.some(m=>!Number.isInteger(m)||m<0||m>1440))throw Error('Timer');
  if(schedule.rules.some(r=>(r.mode&127)&&minutes.some((m,i)=>m&&(r.channel===4||r.channel===i))))throw Error('Conflict');
 }
 function mount({language,save,available,schedule}){
  const box=document.getElementById('timer-editor'),form=document.getElementById('timer-form'),status=document.getElementById('timer-status');let values=[0,0,0,0],loaded=false,busy=false,dirty=false;const liveNodes=[],liveTexts=[];
  const text=(ko,en)=>language()==='en'?en:ko;
  function render(){box.replaceChildren();const hint=document.createElement('p');hint.className='muted';hint.textContent=text('ON부터 자동 OFF · 1분~24시간. 재부팅 후 ON 채널은 처음부터 시작합니다. 예약과 같은 채널은 등록할 수 없습니다.','Auto OFF after ON: 1 minute–24 hours. ON channels restart the full timer after reboot. A channel cannot also have a schedule.');box.append(hint);
   values.forEach((value,i)=>{const card=document.createElement('div');card.className='name-editor';const title=document.createElement('b');title.textContent=text('채널 ','Channel ')+(i+1);card.append(title);
    const conflict=schedule().rules.some(r=>(r.mode&127)&&(r.channel===4||r.channel===i));const row=document.createElement('div');row.className='row';const hours=document.createElement('input'),minutes=document.createElement('input');
    [[hours,24,Math.floor(value/60),text('시간','Hours')],[minutes,59,value%60,text('분','Minutes')]].forEach(([input,max,v,label])=>{input.type='number';input.min=0;input.max=max;input.step=1;input.value=v;input.required=true;input.disabled=busy||!loaded||conflict;input.style.width='85px';input.setAttribute('aria-label',title.textContent+' '+label);const l=document.createElement('label');l.textContent=label;l.append(input);row.append(l);});
    const update=()=>{dirty=true;values[i]=Number(hours.value)*60+Number(minutes.value);};hours.oninput=minutes.oninput=update;
    const remove=document.createElement('button');remove.type='button';remove.textContent=text('삭제','Delete');remove.disabled=busy||!loaded;remove.onclick=()=>{values[i]=0;dirty=true;render();};row.append(remove);card.append(row);
    const note=document.createElement('p');note.className='muted';note.textContent=conflict?text('예약에 등록된 채널입니다. 예약을 삭제한 후 설정하세요.','Registered in scheduler. Delete its schedules first.'):value?text('등록됨 · 저장 후 적용','Registered · save to apply'):text('미등록 · 시간 0으로 저장하면 삭제됩니다.','Unregistered · save zero to remove.');card.append(note);
    const live=document.createElement('div');live.className='muted';live.textContent=liveTexts[i]||text('타이머 00:00:00','Timer 00:00:00');liveNodes[i]=live;card.append(live);box.append(card);
   });const apply=document.createElement('button');apply.type='submit';apply.className='primary';apply.textContent=text('기기에 저장','Save to device');apply.disabled=busy||!loaded||!available();box.append(apply);
  }
  form.onsubmit=async e=>{e.preventDefault();if(busy||!loaded||!available())return;try{valid(values,schedule());busy=true;render();await save([...values]);dirty=false;status.textContent=text('저장했습니다.','Saved.');}catch(_){status.textContent=text('저장 실패 · 최대 24시간, 예약 중복 및 연결을 확인하세요.','Save failed. Check 24-hour limit, schedule conflicts and connection.');}finally{busy=false;render();}};
  render();return {load(v){if(dirty||busy)return;values=[...(v||[0,0,0,0])];loaded=true;render();},show(texts){liveNodes.forEach((n,i)=>{liveTexts[i]=texts[i]||text('타이머 00:00:00','Timer 00:00:00');n.textContent=liveTexts[i];});},translate:render,ready(){const b=box.querySelector('button[type=submit]');if(b)b.disabled=busy||!loaded||!available();}};
 }
 root.MttlTimer={valid,mount};if(typeof module==='object'&&module.exports)module.exports=root.MttlTimer;
})(globalThis);
