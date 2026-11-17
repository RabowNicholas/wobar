# Step 2b, batch mode: Instagram hard-reloads pages under light throttling, which kills an in-page loop.
# This prints browser_batch actions (navigate + read) for a slice of the handle list; Claude runs them from outside.
# Reader: waits for the profile header, records counts / bio-link targets only, appends to localStorage 'acf_ig'.
import json, sys
TAB = 1189935735
L = json.load(open('/private/tmp/claude-502/-Users-nicholasrabow-Desktop-wobar-wobar/c55dc036-dd5f-4d55-9c54-3a9ef6dc5acb/scratchpad/ig_uniq.json'))
a, b = int(sys.argv[1]), int(sys.argv[2])
READ = r"""(async(n,h)=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));const num=s=>{const m=(s||'').replace(/,/g,'').match(/([\d.]+)\s*([KM])?/i);return m?Math.round(+m[1]*({K:1e3,M:1e6}[(m[2]||'').toUpperCase()]||1)):null};const dec=x=>{try{let u=new URL(x);if(u.hostname==='l.instagram.com')u=new URL(u.searchParams.get('u'));return(u.hostname.replace(/^www\./,'')+u.pathname).replace(/\/$/,'')}catch(e){return null}};
let st=null,t0=Date.now();while(Date.now()-t0<10000){const t=document.body.innerText.slice(0,4000);if(/try again later|suspicious activity|confirm it's you|help us confirm|we restrict certain activity/i.test(t)||/\/challenge\/|\/accounts\/login/.test(location.pathname)){st='BLOCKED';break}if(/sorry, this page isn't available|profile isn't available/i.test(document.querySelector('main')?.innerText||'')){st='missing';break}const hd=document.querySelector('header');if(hd&&/followers/i.test(hd.innerText)){st='ok';break}await sl(300)}
const r={name:n,handle:h,status:st||'timeout'};if(st==='ok'){await sl(500);const hd=document.querySelector('header');const ls=hd.innerText.split('\n').map(s=>s.trim()).filter(Boolean);r.followers=num(ls.find(l=>/followers$/i.test(l)));r.posts=num(ls.find(l=>/posts?$/i.test(l)));r.verified=!!hd.querySelector('svg[aria-label="Verified"]');r.links=[...new Set([...hd.querySelectorAll('a[href]')].map(a=>dec(a.href)).filter(x=>x&&!/^(instagram\.com|threads\.(com|net))/.test(x)))];r.tt=(hd.innerText.match(/tiktok\.com\/@?([\w.]+)/i)||[])[1]||null}
if(st!=='BLOCKED'){const o=JSON.parse(localStorage.getItem('acf_ig')||'[]');if(!o.some(x=>x.handle===h)){o.push(r);localStorage.setItem('acf_ig',JSON.stringify(o))}}
return h+' '+r.status+' '+(r.followers??'')})(%s,%s)"""
acts = []
for n, h in L[a:b]:
    acts.append({'name': 'navigate', 'input': {'tabId': TAB, 'url': f'https://www.instagram.com/{h}/'}})
    acts.append({'name': 'javascript_tool', 'input': {'action': 'javascript_exec', 'tabId': TAB, 'text': READ % (json.dumps(n), json.dumps(h))}})
    acts.append({'name': 'computer', 'input': {'action': 'wait', 'tabId': TAB, 'duration': 4}})
print(json.dumps(acts, ensure_ascii=False))
