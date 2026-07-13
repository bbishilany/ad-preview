# Ad Preview — QA smoke test

Playwright click-through that exercises every interactive control on a campaign
preview (placement tabs, A/B/C copy pills, design-direction toggle, approve,
mockup zoom, theme toggle, nav), verifies all feed + story images load, and
separates real bugs from expected backend (Supabase) calls.

```bash
npm i playwright          # once (installs the browser too, or: npx playwright install chromium)

# against the local build server (python3 -m http.server 8899 from repo root):
node qa/smoke.mjs christmas-in-aruba

# against live GitHub Pages:
BASE=https://bbishilany.github.io/ad-preview node qa/smoke.mjs christmas-in-aruba
```

Exit code 0 = no real bugs, 1 = bugs found. Backend calls (feedback, image
versions) abort against a static host — that is expected and reported separately.
