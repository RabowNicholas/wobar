// Step 2b loop v3 (replaces ig_page_crawl.js). Paste into the instagram.com tab; re-paste after any full page load.
// Instagram does a full page load when a handle doesn't exist, which ends any in-page loop; state lives in
// localStorage (acf_ig_list = handles, acf_ig = results), so a re-paste resumes where it stopped.
// Read only. Records follower / post counts, verified, bio-link targets, TikTok in bio. Never bio text or contacts.
(async()=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));const go=p=>{history.pushState({},'',p);dispatchEvent(new PopStateEvent('popstate'))};
const num=s=>{const m=(s||'').replace(/,/g,'').match(/([\d.]+)\s*([KM])?/i);return m?Math.round(+m[1]*({K:1e3,M:1e6}[(m[2]||'').toUpperCase()]||1)):null};
const dec=x=>{try{let u=new URL(x);if(u.hostname==='l.instagram.com')u=new URL(u.searchParams.get('u'));return(u.hostname.replace(/^www\./,'')+u.pathname).replace(/\/$/,'')}catch(e){return null}};
const L=JSON.parse(localStorage.acf_ig_list);
{const cur=location.pathname.split('/')[1];const o=JSON.parse(localStorage.acf_ig||'[]');const it=L.find(x=>x[1]===cur);
 if(it&&!o.some(r=>r.handle===cur)&&/sorry, this page isn't available/i.test(document.querySelector('main')?.innerText||'')){o.push({name:it[0],handle:cur,status:'missing'});localStorage.acf_ig=JSON.stringify(o)}}
const done=new Set(JSON.parse(localStorage.acf_ig||'[]').map(r=>r.handle));const todo=L.filter(x=>!done.has(x[1]));
const S=window.__ig={n:todo.length,i:0,err:null};
for(;S.i<todo.length;S.i++){const[n,h]=todo[S.i];go('/'+h+'/');let st=null,t0=Date.now();
while(Date.now()-t0<12000){await sl(300);const t=document.body.innerText.slice(0,4000);
if(/try again later|suspicious activity|confirm it's you|help us confirm|we restrict certain activity/i.test(t)||/\/challenge\/|\/accounts\/login/.test(location.pathname)){st='BLOCKED';break}
if(location.pathname==='/'+h+'/'&&/sorry, this page isn't available|profile isn't available/i.test(document.querySelector('main')?.innerText||'')){st='missing';break}
const hd=document.querySelector('header');if(hd&&/followers/i.test(hd.innerText)&&hd.innerText.toLowerCase().split('\n')[0].trim()===h.toLowerCase()){st='ok';break}}
if(st==='BLOCKED'){S.err='blocked at '+h;break}
const r={name:n,handle:h,status:st||'timeout'};
if(st==='ok'){await sl(500);const hd=document.querySelector('header');const ls=hd.innerText.split('\n').map(s=>s.trim()).filter(Boolean);
r.followers=num(ls.find(l=>/followers$/i.test(l)));r.posts=num(ls.find(l=>/posts?$/i.test(l)));r.verified=!!hd.querySelector('svg[aria-label="Verified"]');
r.links=[...new Set([...hd.querySelectorAll('a[href]')].map(a=>dec(a.href)).filter(x=>x&&!/^(instagram\.com|threads\.(com|net))/.test(x)))];r.tt=(hd.innerText.match(/tiktok\.com\/@?([\w.]+)/i)||[])[1]||null}
const o=JSON.parse(localStorage.acf_ig||'[]');o.push(r);localStorage.acf_ig=JSON.stringify(o);
if(st==='missing'||!st)continue; // leave a dead page at once: Instagram reloads it a few seconds later
await sl(6000+Math.random()*4000)}S.done=true})();
