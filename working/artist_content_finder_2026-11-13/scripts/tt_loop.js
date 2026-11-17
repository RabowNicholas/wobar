// Step 2d: TikTok reader. Paste into a tiktok.com tab (Nick's Chrome), re-paste after any full page load.
// localStorage: acf_tt_list = [[artist, mode, value]], acf_tt = results. READ ONLY, never follows/likes/messages.
// mode h = known TikTok handle; g = try the artist's Instagram handle on TikTok; s = search by artist name.
// Records followers, likes, display name, view counts of the first 12 grid videos, bio music-keyword flag,
// bio link host. Never bio text or contacts. Stops on captcha / "too many attempts".
(async()=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));const go=p=>{history.pushState({},'',p);dispatchEvent(new PopStateEvent('popstate'))};
const num=s=>{const m=(s||'').replace(/,/g,'').match(/([\d.]+)\s*([KMB])?/i);return m?Math.round(+m[1]*({K:1e3,M:1e6,B:1e9}[(m[2]||'').toUpperCase()]||1)):null};
const norm=s=>(s||'').normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'');
const blocked=()=>!!document.querySelector('.captcha_verify_container,#captcha-verify-container-main-page,[class*="captcha-verify"]')||/too many attempts|maximum number of attempts/i.test(document.body.innerText.slice(0,3000));
const MUS=/\b(dj|producer|music|dubstep|bass|beats?|booking|bookings|mgmt|management|records|soundcloud|spotify|tour|140|grime|riddim|dnb)\b/i;
async function profile(h){go('/@'+h);let st=null,t0=Date.now();
 while(Date.now()-t0<12000){await sl(300);if(blocked())return{st:'BLOCKED'};
  if(document.title.toLowerCase().includes('(@'+h.toLowerCase()+')')&&document.querySelector('[data-e2e="followers-count"]')){st='ok';break}
  if(location.pathname.toLowerCase()==='/@'+h.toLowerCase()&&/couldn't find this account|this account is private/i.test(document.querySelector('main')?.innerText||document.body.innerText.slice(0,2000))){st='missing';break}}
 if(st!=='ok')return{st:st||'timeout'};
 await until(()=>document.querySelectorAll('[data-e2e="video-views"]').length,3000);
 const bio=document.querySelector('[data-e2e="user-bio"]')?.innerText||'';const link=document.querySelector('[data-e2e="user-link"]')?.innerText||'';
 return{st:'ok',display:document.title.split(' (@')[0],followers:num(document.querySelector('[data-e2e="followers-count"]')?.innerText),
  likes:num(document.querySelector('[data-e2e="likes-count"]')?.innerText),music:MUS.test(bio+' '+link),link:(link.match(/[a-z0-9.-]+\.[a-z]{2,}/i)||[''])[0],
  views:[...document.querySelectorAll('[data-e2e="video-views"]')].slice(0,12).map(e=>num(e.innerText))}}
async function until(fn,ms){const t0=Date.now();while(Date.now()-t0<ms){if(fn())return true;await sl(250)}return false}
async function search(n){go('/search/user?q='+encodeURIComponent(n));let t0=Date.now();
 while(Date.now()-t0<12000){await sl(400);if(blocked())return'BLOCKED';if(document.title.includes(n)&&document.querySelectorAll('a[href^="/@"]').length>3)break}
 await sl(800);const seen=new Set(),out=[];
 for(const a of document.querySelectorAll('a[href^="/@"]')){const h=a.getAttribute('href').split('?')[0].slice(2);if(!h||seen.has(h))continue;seen.add(h);
  let c=a;for(let k=0;k<4&&c.parentElement&&!/Followers/.test(c.innerText);k++)c=c.parentElement;const t=c.innerText.split('\n').map(x=>x.trim()).filter(Boolean);
  const fi=t.findIndex(x=>x==='Followers');out.push({h,display:t[0],followers:fi>0?num(t[fi-1]):null})}
 return out}
const L=JSON.parse(localStorage.acf_tt_list);const done=new Set(JSON.parse(localStorage.acf_tt||'[]').map(r=>r.name));const todo=L.filter(x=>!done.has(x[0]));
const S=window.__tt={n:todo.length,i:0,err:null};
for(;S.i<todo.length;S.i++){const[n,mode,v]=todo[S.i];const r={name:n,mode,tried:v};
 if(mode==='s'){const res=await search(n);if(res==='BLOCKED'){S.err='blocked at search '+n;break}
  const c=res.filter(x=>norm(x.display)===norm(n)||norm(x.h)===norm(n)).sort((a,b)=>(b.followers||0)-(a.followers||0));
  r.cands=c.slice(0,3).map(x=>[x.h,x.followers]);
  if(c.length&&(c[0].followers||0)>=1000){r.handle=c[0].h;await sl(3000);Object.assign(r,await profile(c[0].h))}else r.st='no match'}
 else{r.handle=v;Object.assign(r,await profile(v))}
 if(r.st==='BLOCKED'){S.err='blocked at '+n;break}
 if(mode==='g'&&r.st==='ok')r.name_match=norm(r.display)===norm(n)||norm(r.display).includes(norm(n))||norm(n).includes(norm(r.display));
 const o=JSON.parse(localStorage.acf_tt||'[]');o.push(r);localStorage.acf_tt=JSON.stringify(o);
 await sl(5000+Math.random()*4000)}S.done=true})();
