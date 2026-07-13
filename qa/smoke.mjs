// Ad Preview — Playwright smoke test.
// Clicks every interactive control on a campaign preview, verifies images load,
// and separates real bugs from expected backend (Supabase) calls.
//
// Usage:
//   npm i playwright            # once
//   node qa/smoke.mjs [URL]     # default: http://localhost:8899/christmas-in-aruba/
//   BASE=https://bbishilany.github.io/ad-preview node qa/smoke.mjs christmas-in-aruba
//
// Exit code 0 = no real bugs, 1 = bugs found.
import { chromium } from 'playwright';

const arg = process.argv[2] || 'christmas-in-aruba';
const BASE = process.env.BASE || 'http://localhost:8899';
const TARGET = arg.startsWith('http') ? arg : `${BASE}/${arg}/`;

const bugs = [], offline = [], notes = [];
const isBackend = (u) => /supabase|\/api\/|feedback|\/rest\/|localhost:4242/i.test(u);

const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1280, height: 2200 } })).newPage();
page.on('pageerror', (e) => bugs.push(`UNCAUGHT JS: ${e.message}`));
page.on('console', (m) => { if (m.type() === 'error') {
  const t = m.text();
  (isBackend(t) || /Failed to load resource|net::ERR|status of [45]/i.test(t) ? offline : bugs).push(`console: ${t.slice(0,150)}`);
}});
page.on('requestfailed', (r) => (isBackend(r.url()) ? offline : bugs).push(`requestfailed: ${r.url().slice(0,110)}`));
page.on('response', (r) => { if (r.status() >= 400) (isBackend(r.url()) ? offline : bugs).push(`HTTP ${r.status()}: ${r.url().slice(0,110)}`); });
page.on('dialog', (d) => d.dismiss().catch(()=>{}));
page.on('filechooser', (fc) => fc.setFiles([]).catch(()=>{}));

const resp = await page.goto(TARGET, { waitUntil: 'networkidle' });
if (!resp || resp.status() >= 400) bugs.push(`page load ${resp?.status()}`);
await page.waitForSelector('.ad-card', { timeout: 10000 }).catch(() => bugs.push('no .ad-card rendered'));

const cards = await page.$$('.ad-card');
console.log(`Ad cards: ${cards.length}`);

for (const card of cards) {
  const num = await card.getAttribute('data-ad-num');
  const tag = `Ad${num}`;
  for (const tab of await card.$$('.placement-tab')) {
    const p = await tab.getAttribute('data-placement');
    await tab.click(); await page.waitForTimeout(120);
    const panel = await card.$(`.placement-panel[data-placement="${p}"]`);
    if (!panel || await panel.evaluate((el)=>el.classList.contains('hidden'))) bugs.push(`${tag}: "${p}" panel hidden after click`);
    if (!await tab.evaluate((el)=>el.classList.contains('active'))) bugs.push(`${tag}: tab "${p}" not active`);
    if (panel) { const img = await panel.$('img'); if (img) {
      const ok = await img.evaluate((i)=> (i.complete && i.naturalWidth>0) ? true : new Promise(res=>{ i.addEventListener('load',()=>res(true),{once:true}); i.addEventListener('error',()=>res(false),{once:true}); setTimeout(()=>res(i.complete && i.naturalWidth>0),12000); }));
      if (!ok) bugs.push(`${tag}/${p}: image failed to load`);
    }}
  }
  const pills = await card.$$('.copy-version-pill');
  for (let i=0;i<pills.length;i++){ await pills[i].click(); await page.waitForTimeout(70);
    if (await card.$$eval('.copy-version-pill',(ps)=>ps.findIndex(p=>p.classList.contains('active'))) !== i) bugs.push(`${tag}: copy pill ${i} not active`); }
  const dd = await card.$('.design-direction-toggle');
  if (dd) { await dd.click(); await page.waitForTimeout(100);
    if (!await card.$eval('.design-direction-body',(e)=>e.classList.contains('open')).catch(()=>false)) bugs.push(`${tag}: design direction did not open`);
    await dd.click().catch(()=>{}); }
  const appr = await card.$('.approve-btn');
  if (appr) { await appr.click(); await page.waitForTimeout(120);
    if (!/approved/i.test((await appr.textContent()||'')) || !await appr.evaluate((e)=>e.disabled)) bugs.push(`${tag}: approve did not enter approved state`); }
  else bugs.push(`${tag}: no approve button`);
}

// mockup zoom (ensure a feed panel is visible, then click a non-excluded area)
const feedTab = await page.$('.placement-tab[data-placement="feed"]');
if (feedTab) { await feedTab.click().catch(()=>{}); await page.waitForTimeout(150); }
const safe = await page.$('.fb-feed:visible .fb-feed-text, .placement-panel[data-placement="feed"]:not(.hidden) .fb-feed-text');
if (safe) { await safe.click().catch(()=>{}); await page.waitForTimeout(400);
  const active = await page.$eval('#mockup-zoom-overlay',(e)=>e.classList.contains('active')).catch(()=>false);
  if (active) { notes.push('zoom: opens'); await page.click('.mockup-zoom-close').catch(()=>{});
    if (await page.$eval('#mockup-zoom-overlay',(e)=>e.classList.contains('active'))) bugs.push('zoom: X did not close'); }
  else bugs.push('zoom: did not open on safe-area click'); }

// theme toggle
const tb = await page.$('[onclick*="toggleTheme"]');
if (tb) { const before = await page.evaluate(()=>document.body.classList.contains('light-mode'));
  await tb.click(); await page.waitForTimeout(120);
  if (before === await page.evaluate(()=>document.body.classList.contains('light-mode'))) bugs.push('theme toggle did not change'); else notes.push('theme toggle: ok'); }

for (const n of await page.$$('[onclick*="scrollToAd"]')) { await n.click().catch(()=>{}); await page.waitForTimeout(50); }

console.log(`\nBUGS: ${bugs.length}`); bugs.forEach((b)=>console.log('  x '+b));
console.log(`backend/offline (expected): ${offline.length}`);
console.log('notes: '+notes.join(' | '));
await browser.close();
process.exit(bugs.length ? 1 : 0);
