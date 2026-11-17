// Step 3c post reader: Instagram post pages (/p/<id>/). Read only; videos muted and paused.
// localStorage: acf_posts_list = [[artist, handle, id, views]], acf_posts = results. Re-paste after any full page load.
// Records owner line (collab flag), audio label, date, caption (owner's text only). No commenter names or comments.
(async()=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));const go=p=>{history.pushState({},'',p);dispatchEvent(new PopStateEvent('popstate'))};
const AGE=/^\d+[smhdwy]$/;
const L=JSON.parse(localStorage.acf_posts_list);const done=new Set(JSON.parse(localStorage.acf_posts||'[]').map(r=>r.id));const todo=L.filter(x=>!done.has(x[2]));
const S=window.__po={n:todo.length,i:0,err:null};
for(;S.i<todo.length;S.i++){const[a,h,id,views]=todo[S.i];
 const old=document.querySelector('main time[datetime]');if(old)old.setAttribute('data-acf','old');
 go('/p/'+id+'/');let st=null,t0=Date.now();
 while(Date.now()-t0<12000){await sl(400);const t=document.body.innerText.slice(0,4000);
  if(/try again later|suspicious activity|confirm it's you|help us confirm|we restrict certain activity/i.test(t)||/\/challenge\/|\/accounts\/login/.test(location.pathname)){st='BLOCKED';break}
  if(/sorry, this page isn't available/i.test(document.querySelector('main')?.innerText||'')){st='missing';break}
  const tm=document.querySelector('main time[datetime]');if(location.pathname.includes(id)&&tm&&!tm.hasAttribute('data-acf')){st='ok';break}}
 if(st==='BLOCKED'){S.err='blocked at '+id;break}
 const r={artist:a,handle:h,id,views,status:st||'timeout'};
 if(st==='ok'){await sl(700);document.querySelectorAll('video').forEach(v=>{v.muted=true;v.pause()});
  const m=document.querySelector('main');const ls=m.innerText.split('\n').map(s=>s.trim());
  r.date=document.querySelector('main time[datetime]').getAttribute('datetime');
  const au=document.querySelector('main a[href*="/audio/"]');r.audio=au?au.innerText.trim():null;
  r.owner=ls[0];r.collab=/^and \d+ others?$/.test(ls[1]||'')?ls[1]:null;
  const ages=ls.map((x,i)=>AGE.test(x)?i:-1).filter(i=>i>=0);
  if(ages.length){const s=ages[0]+1,e=ages.length>1?ages[1]-2:s+8;r.caption=ls.slice(s,Math.max(s,e)).filter(Boolean).join('\n').slice(0,600)}
  r.own_post=r.owner.toLowerCase()===h.toLowerCase()}
 const o=JSON.parse(localStorage.acf_posts||'[]');o.push(r);localStorage.acf_posts=JSON.stringify(o);
 if(r.status!=='ok')continue;await sl(4000+Math.random()*4000)}S.done=true})();
