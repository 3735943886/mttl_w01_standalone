/* Device-only bootstrap: serialize requests and recover transient downloads. */
(function(){
 'use strict';
 let notice;
 function message(){
  if(!notice){notice=document.createElement('p');notice.setAttribute('role','status');notice.style.cssText='margin:16px;color:#b45309';document.body.appendChild(notice);}
  notice.textContent=document.documentElement.lang==='en'?'Loading dashboard. Retrying connection…':'화면을 불러오는 중입니다. 연결을 재시도합니다…';
 }
 function load(path,next){
  const script=document.createElement('script');script.src=path;script.async=false;
  script.onload=()=>{if(notice){notice.remove();notice=null;}next();};
  script.onerror=()=>{script.remove();message();setTimeout(()=>load(path,next),3000);};
  document.body.appendChild(script);
 }
 load('/i18n.js',()=>load('/live.js',()=>{}));
})();
