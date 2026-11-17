// Step 3a reach read: Instagram Reels tab, last 12 reels per artist (views, likes, comments, pinned, reel id).
// Paste into an instagram.com tab; re-paste after any full page load (state in localStorage acf_reels_list / acf_reels).
// Read only. Stops on any block sign.
(async()=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));const go=p=>{history.pushState({},'',p);dispatchEvent(new PopStateEvent('popstate'))};
const num=s=>{const m=(s||'').replace(/,/g,'').match(/([\d.]+)\s*([KM])?/i);return m?Math.round(+m[1]*({K:1e3,M:1e6}[(m[2]||'').toUpperCase()]||1)):null};
const L=JSON.parse(localStorage.acf_reels_list);const done=new Set(JSON.parse(localStorage.acf_reels||'[]').map(r=>r.handle));const todo=L.filter(x=>!done.has(x[1]));
const S=window.__rl={n:todo.length,i:0,err:null};
for(;S.i<todo.length;S.i++){const[n,h]=todo[S.i];go('/'+h+'/reels/');let st=null,t0=Date.now();const pre='/'+h.toLowerCase()+'/reel/';
 const items=()=>[...document.querySelectorAll('main a[href*="/reel/"]')].filter(a=>a.getAttribute('href').toLowerCase().startsWith(pre));
 while(Date.now()-t0<12000){await sl(400);const t=document.body.innerText.slice(0,4000);
  if(/try again later|suspicious activity|confirm it's you|help us confirm|we restrict certain activity/i.test(t)||/\/challenge\/|\/accounts\/login/.test(location.pathname)){st='BLOCKED';break}
  if(/sorry, this page isn't available/i.test(document.querySelector('main')?.innerText||'')){st='missing';break}
  if(items().length>=Math.min(12,3)&&Date.now()-t0>2500){st='ok';break}}
 if(st==='BLOCKED'){S.err='blocked at '+h;break}
 const r={name:n,handle:h,status:st||(items().length?'ok':'no reels')};
 if(items().length){await sl(800);r.reels=items().slice(0,12).map(a=>{const sp=[...new Set([...a.querySelectorAll('span')].map(s=>s.innerText).filter(Boolean))];
   return{id:a.getAttribute('href').split('/reel/')[1].replace(/\//g,''),views:num(a.innerText.split('\n')[0]),likes:num(sp[0]),comments:num(sp[1]),pinned:!!a.querySelector('svg[aria-label*="inned"]')}})}
 const o=JSON.parse(localStorage.acf_reels||'[]');o.push(r);localStorage.acf_reels=JSON.stringify(o);
 if(r.status!=='ok')continue;await sl(5000+Math.random()*4000)}S.done=true})();
