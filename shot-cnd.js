const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 1500 } });
  await ctx.addInitScript(() => sessionStorage.setItem('md_organic_gate_ok','1'));
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push('PAGEERROR ' + e.message));
  p.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE ' + m.text()); });
  await p.goto('http://localhost:8899/mileage-organic/', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);
  const n = await p.evaluate(() => document.querySelectorAll('.post').length);
  console.log('posts rendered:', n, '| errors:', JSON.stringify(errs.slice(0, 4)));
  if (n) {
    await p.evaluate(() => setTheme('CND'));
    await p.waitForTimeout(1500);
    await p.screenshot({ path: process.argv[2] });
    console.log('shot written');
  }
  await b.close();
})().catch(e => { console.log('SCRIPT ERROR', e.message); process.exit(1); });
