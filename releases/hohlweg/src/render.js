const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + process.cwd() + '/hohlweg.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.chapter .inner')].map(e => e.scrollHeight - e.clientHeight));
  console.log('overflow px per chapter:', over);
  console.log('fonts:', await p.evaluate(() => [...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family+' '+f.weight).join(', ')));
  await p.pdf({ path: 'HOHLWEG.pdf', width: '720px', height: '1280px', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
