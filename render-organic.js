const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const outDir = process.argv[2];
  fs.mkdirSync(outDir, { recursive: true });
  const data = JSON.parse(fs.readFileSync('mileage-organic/data.json', 'utf8'));
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  let ok = 0, bad = [];
  for (const post of data.posts) {
    const url = `http://localhost:8899/mileage-organic/render.html?slot=${post.slot}`;
    await p.goto(url, { waitUntil: 'domcontentloaded' });
    try {
      await p.waitForFunction(() => window.ready === true, { timeout: 20000 });
    } catch (e) {
      bad.push(post.slot + ' (not ready)');
      continue;
    }
    const el = await p.$('.shot');
    const box = await el.boundingBox();
    if (Math.round(box.width) !== 1080 || Math.round(box.height) !== 1350) {
      bad.push(`${post.slot} (${box.width}x${box.height})`);
      continue;
    }
    await el.screenshot({ path: path.join(outDir, `${post.slot}.png`) });
    ok++;
  }
  await b.close();
  console.log(`rendered ${ok}/${data.posts.length}`);
  if (bad.length) console.log('FAILED:', bad.join(', '));
})();
