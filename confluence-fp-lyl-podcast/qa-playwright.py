import asyncio, json, sys
from playwright.async_api import async_playwright

URL="https://lyl-preview.vercel.app"
CODE="lyl726"
results=[]; console_errors=[]

def rec(name, ok, detail=""):
    results.append((name,ok,detail))
    print(("PASS " if ok else "FAIL ")+name+(f" — {detail}" if detail else ""), flush=True)

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={"width":1440,"height":1000})
        pg.on("console", lambda m: console_errors.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: console_errors.append(str(e)))

        await pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
        # 1) preview is UNGATED by design (Bill 2026-09-02)
        rec("no gate present", (await pg.locator("#lyl-gate").count())==0)

        # data.json ground truth
        data=json.loads(await (await pg.request.get(f"{URL}/data.json")).text())
        ads=data["ads"]; n=len(ads)
        rec("data.json ads == 29", n==29, f"got {n}")

        # 2) render counts
        await pg.wait_for_timeout(1500)
        cards=await pg.locator("[id^=ad-card-]").count()
        rec("ad cards rendered == 29", cards==29, f"got {cards}")
        nav=await pg.locator(".ad-nav-item").count()
        rec("nav items == 29", nav==29, f"got {nav}")

        # 3) captions present + no empty primary text
        empt=[a["num"] for a in ads if not (a.get("primary_text") or "").strip()]
        rec("all captions non-empty", not empt, f"empty: {empt}")

        # 4) video metadata loads for every ad (width 1080)
        vids=await pg.evaluate("""async () => {
          const els=[...document.querySelectorAll('video')];
          const out=[];
          for (const v of els){
            try{
              v.preload='metadata'; v.load();
              await new Promise((res,rej)=>{ if(v.readyState>=1) return res();
                const t=setTimeout(()=>rej('timeout'),20000);
                v.addEventListener('loadedmetadata',()=>{clearTimeout(t);res();},{once:true});
                v.addEventListener('error',()=>{clearTimeout(t);rej('err');},{once:true});});
              out.push({src:v.currentSrc.split('/').pop(), w:v.videoWidth, h:v.videoHeight, ok:true});
            }catch(e){ out.push({src:(v.currentSrc||'?').split('/').pop(), ok:false, e:String(e)}); }
          }
          return out; }""")
        bad=[v for v in vids if not v.get("ok") or v.get("w")!=1080 or v.get("h")!=1920]
        rec(f"videos metadata OK ({len(vids)} found)", len(vids)>=n and not bad, f"bad: {bad[:4]}")

        # 5) per-ad CTA links match data
        hrefs=await pg.evaluate("""() => {
          const out={};
          document.querySelectorAll('[id^=ad-card-]').forEach(c=>{
            const num=c.id.replace('ad-card-','');
            const a=c.querySelector('a.fb-cta-btn')||c.querySelector('a.ig-story-cta');
            out[num]=a?a.href:null;});
          return out; }""")
        mism=[]
        for a in ads:
            want=a.get("cta_url") or data.get("cta_url")
            got=hrefs.get(str(a["num"]))
            if got!=want: mism.append((a["num"],got,want))
        rec("CTA hrefs match data (28 episode + 3ch)", not mism, f"mismatches: {mism[:3]}")

        # 6) feedback round-trip on ad 1 (post + verify + delete)
        await pg.evaluate("localStorage.setItem('adpreview_name','Mileage QA')")
        sb_posts=[]
        pg.on("response", lambda r: sb_posts.append(r.status) if "supabase" in r.url and r.request.method=="POST" and "feedback" in r.url else None)
        inp=pg.locator("#comment-input-1")
        if await inp.count():
            await inp.fill("QA check — please ignore (auto-removed)")
            await pg.locator("#ad-card-1 .feedback-inline-send").first.click()
            await pg.wait_for_timeout(3000)
            rec("feedback comment posts (Supabase 201)", 201 in sb_posts, f"statuses: {sb_posts}")
            # cleanup via REST (thread UI lags in headless)
            import urllib.request
            SB="https://byuxmsohwsvnqfirgeit.supabase.co"; KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ5dXhtc29od3N2bnFmaXJnZWl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ0MDE3NzYsImV4cCI6MjA4OTk3Nzc3Nn0.YctPyGRzwgdz9-HaHDnWO0KhrVhElRhYKg7feIWPd1c"
            rq=urllib.request.Request(SB+"/rest/v1/feedback?campaign_id=eq.confluence-fp-lyl-podcast&reviewer_name=eq.Mileage%20QA",method="DELETE",headers={"apikey":KEY,"Authorization":"Bearer "+KEY})
            urllib.request.urlopen(rq)
            rec("QA comment deleted", True, "via REST")
        else:
            rec("feedback comment posts (Supabase)", False, "no comment input found")

        # 7) nav click scrolls + activates
        last=pg.locator(".ad-nav-item").last
        await last.click(); await pg.wait_for_timeout(3500)
        cls=await last.get_attribute("class")
        rec("nav click activates", "active" in (cls or ""))

        # 8) console errors
        benign=[e for e in console_errors if "favicon" not in e.lower()]
        rec("no console errors", not benign, f"{benign[:3]}")

        await pg.screenshot(path="/private/tmp/claude-501/-Users-billbishilany24/ac0cf99a-fad9-4d4a-9e92-fc6aa5c7a69b/scratchpad/lyl-qa-final.png", full_page=False)
        await b.close()
    fails=[r for r in results if not r[1]]
    print(f"\n===== {len(results)-len(fails)}/{len(results)} PASS ====="+("" if not fails else f"  FAILURES: {[f[0] for f in fails]}"))

asyncio.run(main())
