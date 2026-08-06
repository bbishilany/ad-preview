const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 1600 } });
  await ctx.addInitScript(() => sessionStorage.setItem('md_organic_gate_ok','1'));
  const p = await ctx.newPage();
  await p.goto('http://localhost:8899/mileage-organic/', { waitUntil: 'networkidle' });
  await p.evaluate(() => Promise.all([...document.images].map(i => i.decode().catch(()=>{}))));
  await p.waitForTimeout(700);
  await p.screenshot({ path: process.argv[2], fullPage: true });
  await b.close();
})();
