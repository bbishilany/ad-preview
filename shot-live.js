const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 1250 } });
  await ctx.addInitScript(() => sessionStorage.setItem('md_organic_gate_ok','1'));
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto('https://md-organic-preview.vercel.app/', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3500);
  const n = await p.evaluate(() => document.querySelectorAll('.post').length);
  await p.evaluate(() => { toggleCadence(); setTheme('SEE'); });
  await p.waitForTimeout(2500);
  console.log('live posts:', n, '| js errors:', errs.length ? errs[0] : 'none');
  await p.screenshot({ path: process.argv[2] });
  await b.close();
})().catch(e => { console.log('ERR', e.message); process.exit(1); });
