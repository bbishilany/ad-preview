// Ad Preview — feedback capture E2E.
// Exercises the REAL feedback pipeline against live Supabase: approve an ad,
// leave a comment, verify both rows persist and render back, then delete the
// test rows through the app's own delete flow so nothing is left behind.
//
// Usage:
//   node qa/feedback-e2e.mjs [URL]   # default: live GitHub Pages CIA preview
//
// Exit 0 = feedback capture verified end-to-end. Exit 1 = capture is broken.
import { chromium } from 'playwright';

const TARGET = process.argv[2] || 'https://bbishilany.github.io/ad-preview/christmas-in-aruba/';
const QA_NAME = 'MILEAGE QA BOT (test row)';
const QA_COMMENT = `QA capture check ${Date.now()} — safe to ignore`;

const fails = [], passes = [];
const ok = (m) => { passes.push(m); console.log('  PASS', m); };
const bad = (m) => { fails.push(m); console.log('  FAIL', m); };

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 2200 } });
const page = await ctx.newPage();

// Track every write/read against the feedback table
const posts = [];
page.on('response', (r) => {
  if (r.url().includes('/rest/v1/feedback') && r.request().method() === 'POST') {
    posts.push({ status: r.status(), url: r.url() });
  }
});
page.on('dialog', (d) => d.accept(d.type() === 'prompt' ? QA_NAME : undefined));

console.log('Target:', TARGET);
await page.goto(TARGET, { waitUntil: 'networkidle' });
await page.evaluate((n) => localStorage.setItem('adpreview_name', n), QA_NAME);

// ── 1. Approve flow (Ad 1) ────────────────────────────────────────────────
const approveBtn = page.locator('#approve-btn-1');
await approveBtn.scrollIntoViewIfNeeded();
const [approveResp] = await Promise.all([
  page.waitForResponse((r) => r.url().includes('/rest/v1/feedback') && r.request().method() === 'POST', { timeout: 15000 }).catch(() => null),
  approveBtn.click(),
]);
if (approveResp && approveResp.status() >= 200 && approveResp.status() < 300) {
  ok(`approve insert reached Supabase (HTTP ${approveResp.status()})`);
} else {
  bad(`approve insert did NOT reach Supabase (${approveResp ? 'HTTP ' + approveResp.status() : 'no request fired'}) — UI shows Approved regardless (silent-failure risk)`);
}
if (await approveBtn.evaluate((el) => el.classList.contains('approved'))) ok('approve button reflects Approved state');
else bad('approve button did not flip to Approved');

// ── 2. Comment flow (Ad 2) ────────────────────────────────────────────────
const input = page.locator('#comment-input-2');
await input.scrollIntoViewIfNeeded();
await input.fill(QA_COMMENT);
const [commentResp] = await Promise.all([
  page.waitForResponse((r) => r.url().includes('/rest/v1/feedback') && r.request().method() === 'POST', { timeout: 15000 }).catch(() => null),
  page.locator('.ad-card[data-ad-num="2"] .feedback-inline-send').click(),
]);
if (commentResp && commentResp.status() >= 200 && commentResp.status() < 300) {
  ok(`comment insert reached Supabase (HTTP ${commentResp.status()})`);
} else {
  bad(`comment insert failed (${commentResp ? 'HTTP ' + commentResp.status() : 'no request fired'})`);
}
if (await input.inputValue() === '') ok('comment input cleared after send (success path ran)');
else bad('comment input not cleared — app treated send as failed');

// ── 3. Read-back: count + thread render ───────────────────────────────────
await page.waitForTimeout(1500);
const countText = await page.locator('#feedback-count-2').innerText().catch(() => '');
if (/[1-9]/.test(countText)) ok(`feedback count visible on Ad 2 ("${countText.trim()}")`);
else bad(`feedback count not showing on Ad 2 ("${countText.trim()}")`);

// Toggle races with async count refresh — ensure the thread ends up open
// with content, retrying the toggle if it landed closed or stayed empty.
async function openThread(adNum) {
  for (let i = 0; i < 3; i++) {
    const wrap = page.locator(`#feedback-thread-${adNum}`);
    if (!(await wrap.evaluate((el) => el.classList.contains('open')).catch(() => false))) {
      await page.locator(`#feedback-count-${adNum}`).click().catch(() => {});
    }
    try {
      await page.waitForFunction((n) => {
        const el = document.getElementById(`feedback-thread-inner-${n}`);
        const w = document.getElementById(`feedback-thread-${n}`);
        return w && w.classList.contains('open') && el && el.innerText.trim() !== '' && !el.innerText.includes('Loading');
      }, adNum, { timeout: 5000 });
      return page.locator(`#feedback-thread-inner-${adNum}`).innerText();
    } catch { /* retry */ }
  }
  return '';
}
const threadText = await openThread(2);
if (threadText.includes(QA_COMMENT)) ok('comment renders back in the thread (server read-back verified)');
else bad('comment missing from thread read-back');
if (threadText.includes(QA_NAME)) ok('reviewer name captured with the comment');
else bad('reviewer name missing in thread');

// ── 4. Cleanup via the app's own delete flow ──────────────────────────────
let cleaned = 0;
for (const adNum of [2, 1]) {
  await openThread(adNum);
  // Delete every entry left by this QA run (matched by name)
  const entries = page.locator(`#feedback-thread-inner-${adNum} .feedback-entry`, { hasText: QA_NAME });
  let n = await entries.count();
  while (n > 0) {
    const [delResp] = await Promise.all([
      page.waitForResponse((r) => r.url().includes('/rest/v1/feedback') && r.request().method() === 'DELETE', { timeout: 10000 }).catch(() => null),
      entries.first().locator('.feedback-delete-btn').click(),
    ]);
    await page.waitForTimeout(1200);
    const left = await entries.count();
    if (left < n && delResp) { cleaned++; n = left; }
    else break;
  }
}
if (cleaned >= 2) ok(`cleanup: ${cleaned} QA rows deleted through the app`);
else console.log(`  NOTE cleanup removed ${cleaned}/2 QA rows — leftovers are name-tagged "${QA_NAME}"`);

await browser.close();
console.log(`\n${fails.length === 0 ? 'FEEDBACK CAPTURE VERIFIED' : 'FEEDBACK CAPTURE BROKEN'} — ${passes.length} passed, ${fails.length} failed`);
if (fails.length) { console.log(fails.map((f) => '  - ' + f).join('\n')); process.exit(1); }
