# Consultation v2 — Post-Mortem (ARCHIVED)

**Date:** 2026-08-17
**Verdict (client):** v2 completely missed the mark. "Many of the one-liners simply didn't make sense to them."
**Decision:** Archive the entire v2 platform. Revert to **v1** and iterate from there.
**Preserved by:** git history (branch `claude/cfp-consultation-preview`) + this doc. Nothing about v2 is lost; it is retired, not deleted.

---

## What v2 was
A pivot off v1: 11 concern-led ads (1–8 HNW, 9–11 mass-affluent), one concept per ad, edgier hooks,
the team/coordination arc relocated *into* each ad instead of running across the set, and **green
placeholder creatives** (no photography) carrying a single compressed on-image line + matching feed headline.

## The precise failure — it was the headlines, not the concepts or the captions
The captions were legible. The compressed headlines were not. Same idea, two very different outcomes:

| # | Caption hook (worked — clear in 1 sec) | Headline / on-image (failed — needs the concept already in your head) |
|---|---|---|
| 2 | Is a single stock carrying most of your wealth? | When One Stock Is the Risk. |
| 3 | How do you know when you've saved enough to retire? | The Hard Part? Knowing When. |
| 5 | Is a growing share of your wealth tied up in equity comp? | Vested Equity Isn't a Plan. |
| 8 | Is each part of your financial life managed well on its own? | Managed in Pieces, or as One? |
| 11 | Do you know you're on track, or just hoping you are? | On Track, or Just Hoping? |

The caption asks a question anyone can answer about themselves. The headline is a clever distillation
that only lands *after* you've understood the concept — the wrong order. On a green box with no
photograph, that headline is the only meaning-carrier, so a cryptic line has nothing to lean on.

## Root causes
1. **Compression outran comprehension.** We wrote the headlines to be edgy and distilled. Compression
   that reads as "clever" to a copywriter reads as "cryptic" to a cold HNW 40–80 reader who doesn't
   already hold the concept. The bar for a cold headline is *understood in ~1 second by someone not in
   the headspace* — several of ours required the reader to reconstruct the premise first.
2. **We optimized for edge; the client's actual bar was clarity.** "Edge in the hook" overshot into
   *obliqueness*. Edge should be precision, not indirection. For an advisory brand selling trust to an
   older affluent audience, immediate legibility beats intrigue every time.
3. **Green placeholders doubled the load.** With no photography, the compressed line carried 100% of the
   meaning with zero visual anchor. We shipped the hardest-to-parse copy against the least supportive
   creative. v1's fuller copy + real imagery shared the load; v2 put it all on one cryptic line.
4. **We built the whole platform before validating the core bet.** 11 ads, green boxes, Figma frames,
   favicon, caption toggle — a large build on an unvalidated hypothesis (that compressed one-liners
   would land). We even *predicted* the "it doesn't sound like us" objection — but the real failure was
   more fundamental (the lines weren't parseable at all), and a 2–3 concept A/B against v1 would have
   surfaced it for a fraction of the build.

## What v1 got right (why we're reverting)
- Fuller captions carried context; the reader never had to reconstruct the premise.
- Concepts were legible on first read.
- Copy + imagery shared the meaning load instead of stacking it on one line.

## Transferable rules (institutionalized — see craft reference + CFP playbook)
- **Comprehension gate outranks the scroll-stop/edge gate for advisory + older-affluent audiences.**
  New first gate: a cold reader must be able to say what the ad is about in ~1 second. If not, edge is
  a liability. Run this *before* the fold-test and the edge pass.
- **Edge = precision, not obliqueness.** A hook can be sharp *and* immediately legible. If understanding
  the line requires already holding the concept, it is too compressed — expand it.
- **The headline must be at least as legible as the caption's question.** If the caption reads clean but
  the headline is a cryptic distillation of it, the headline is wrong, not clever.
- **Never ship compressed on-image lines against placeholder creative.** Text-only compression with no
  visual anchor doubles the comprehension load. Either the visual carries context or the line is fuller.
- **Validate the risky creative bet with a small A/B against the incumbent before building the platform.**
  2–3 concepts, not 11. "Doesn't sound like us" was the predicted objection; "doesn't make sense" was
  the real one — comprehension failure is more basic than voice-fit and has to be caught earlier and cheaper.

## The 11 v2 lines (snapshot for the record)
1. Plan the Exit, Not Just the Sale. — *You've thought about the sale. Have you thought about the morning after?*
2. When One Stock Is the Risk. — *Is a single stock carrying most of your wealth?*
3. The Hard Part? Knowing When. — *How do you know when you've saved enough to retire?*
4. Who Sees the Whole Picture? — *Who's looking at your finances beyond your investments?*
5. Vested Equity Isn't a Plan. — *Is a growing share of your wealth tied up in equity comp?*
6. What's Your Plan for the Unplanned? — *How would your plan hold up if something went wrong?*
7. Leave a Plan They Can Follow. — *When it all passes to the people you love, will they inherit a plan, or a puzzle?*
8. Managed in Pieces, or as One? — *Is each part of your financial life managed well on its own?*
9. Will It Last as Long as You Do? — *Will your savings outlast a long retirement?* (mass-affluent)
10. What Is Your Fee Buying? — *You know what you pay. Do you know what you're paying for?* (mass-affluent)
11. On Track, or Just Hoping? — *Do you know you're on track, or just hoping you are?* (mass-affluent)
