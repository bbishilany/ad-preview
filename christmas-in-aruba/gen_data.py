#!/usr/bin/env python3
"""Generate data.json for the Christmas in Aruba B2C pre-order ad preview.

Structure mirrors the successful Confluence "Naples" campaign: 6 ads / 3 waves,
each ad carrying an emotional-arc label, 3 copy variations, and full image
direction (feed + stories) grounded in the real brand palette pulled from
christmasinaruba.com.

Emotional arc (adapted from Naples' persuasion-principle waves to e-commerce pre-order):
  Wave 1 Awareness    : 1) feeling/liking   2) product/authority
  Wave 2 Consideration: 3) offer/reciprocity 4) range/self-selection
  Wave 3 Urgency      : 5) island identity/in-group  6) honest scarcity
"""
import json
from pathlib import Path

HERE = Path(__file__).parent

# ── Shared brand system (from christmasinaruba.com CSS + product data) ────────
BRAND = """**Christmas in Aruba — brand system (from live site)**
Palette: Cream #F6F3EC (light bg) · Deep slate #1F2A30 (headings) · Muted green-gray #5E6B6F (body) · Warm white #FFFFFF · **Coral-red #FF5A4F (signature accent + CTA)** · Island green #1F7A5C / #00A653 · Caribbean turquoise #27C4C3 (island-touch accent, use sparingly) · Mint #DFF8EF · warm gold = tree-light glow.
Logo: coral wordmark (images/cia-brandmark.png) — place on cream or over a dark-dimmed photo, never on a busy area.
Fonts: confirm brand fonts with the site/Mayo. Direction: warm editorial serif for headlines (holiday warmth), clean humanist sans for details/CTA.
Photo mood: warm, golden-hour, sun-washed. Tree lights are the glow source. Island touch = palms, ocean, trade-wind light, breezy open interiors. NEVER fake snow. Real Aruban homes/patios where possible.
Meta text rule: keep visible text on the image under ~15% (Low tier) — headline + one line + CTA sticker only. The story lives in the caption."""


def ad1():
    return {
        "num": 1,
        "title": "Christmas comes home to Aruba",
        "format": "Static image, 1080x1080 (square) + 1080x1920 (vertical)",
        "placements": ["Feed", "Stories", "Reels"],
        "primary_text": [
            "There's a certain magic to a Christmas tree glowing in the window — and this year, it belongs in your home in Aruba.\n\nClassic Christmas warmth, with a subtle island touch. Pre-lit, ready in minutes, and made to make the whole family stop and stare.\n\nReserve yours now for delivery before November — and start the season the moment you're ready.\n\nFor a limited time: free island-wide delivery on every pre-order.",
            "Picture it: the lights are on, the music's playing, and the tree is glowing in the corner — no boxes of tangled lights, no hassle. Just Christmas, at home in Aruba.\n\nOur pre-lit trees arrive ready to shine, with color-changing LEDs and a remote in the box.\n\nReserve now for guaranteed delivery before November. For a limited time, pre-orders include free delivery across the island.",
            "The best part of Christmas isn't the day — it's the weeks leading up to it. The glow in the living room. The kids' faces when the lights come on.\n\nBring that home to Aruba this year with a pre-lit tree that's ready in minutes.\n\nPre-order now, pay less, and we'll deliver before November — free, anywhere on the island, for a limited time.",
        ],
        "headline": [
            "Christmas Comes Home to Aruba",
            "A Little Island Magic, Every Christmas Season",
            "The Season Starts at Home",
        ],
        "description": [
            "Pre-Lit · Ready in Minutes",
            "Free Delivery on Pre-Orders",
            "Reserve for November",
        ],
        "cta": "Shop Now",
        "hook": "Christmas comes home to Aruba.",
        "arc": "Emotional atmosphere — the feeling of Christmas at home on the island (liking)",
        "wave": 1,
        "stories": {
            "image": "Warm-lit living room at dusk in an Aruban home — a glowing pre-lit tree beside an open window, palm silhouettes and last light outside. The tree is the only strong light source.",
            "text_overlay": "Christmas Comes Home to Aruba",
            "secondary_text": "Pre-order now · Delivered before November",
            "cta_sticker": "Shop Now",
        },
        "image_direction": IMG_AD1,
    }


def ad2():
    return {
        "num": 2,
        "title": "Lit in minutes — the island's specialist",
        "format": "Static image, 1080x1080 (square) + 1080x1920 (vertical)",
        "placements": ["Feed", "Stories", "Reels"],
        "primary_text": [
            "Aruba's only dedicated Christmas store — and it shows.\n\nEvery tree arrives pre-lit with color-changing LED lights and a remote, shaped and ready in minutes. No lugging home a real tree, no untangling a single strand.\n\nFrom compact 3-footers to statement 9.5-foot pines — reserve yours now for delivery before November.\n\nFor a limited time: free island-wide delivery on every pre-order.",
            "What makes it easy: the lights are already on.\n\nOur pre-lit trees come with color-changing LEDs and a remote right in the box — warm white for dinner, full color for the party, all from the couch.\n\nAs the island's Christmas specialist, we bring in the trees, the wreaths and the garland so you don't have to hunt for them.\n\nPre-order now. Delivered free before November — for a limited time.",
            "One remote. Every color. Zero hassle.\n\nOur trees arrive pre-strung with color-changing LED lights — no boxes of bulbs, no ladders, no frustration. Fluff the branches, plug it in, and you're done in minutes.\n\nAruba's Christmas specialists, with trees, wreaths and garland for every home.\n\nReserve now for free delivery before November — a limited-time pre-order perk.",
        ],
        "headline": [
            "Lit in Minutes, Not Hours",
            "The Island's Christmas Specialist",
            "Pre-Lit. Remote-Ready. Effortless.",
        ],
        "description": [
            "Color-Changing LEDs Included",
            "3ft to 9.5ft · Every Home",
            "Free Pre-Order Delivery",
        ],
        "cta": "Shop Now",
        "hook": "Pre-lit, remote-ready, and up in minutes — the island's only Christmas specialist.",
        "arc": "Product & authority — pre-lit convenience + the island specialist (authority)",
        "wave": 1,
        "stories": {
            "image": "Macro shot of a lit branch, color shifting warm-white → multicolor, a hand holding the remote just in frame. Rich, glowing, tactile.",
            "text_overlay": "Lit in Minutes",
            "secondary_text": "Color-changing LEDs + remote, included",
            "cta_sticker": "Shop Now",
        },
        "image_direction": IMG_AD2,
    }


def ad3():
    return {
        "num": 3,
        "title": "Reserve now, save up to 40%",
        "format": "Static image, 1080x1080 (square) + 1080x1920 (vertical)",
        "placements": ["Feed", "Stories", "Reels"],
        "primary_text": [
            "Reserve now and save 40% on your pre-order — pay in full or pay half, the discount's the same either way.\n\nPrefer to spread it out? Layaway splits it into 4 easy monthly payments.\n\nFor a limited time, every pre-order ships free across Aruba and is delivered before November. And with any purchase over Afl 250, we'll add a free 500-count Color-Changing LED Light Set with remote — a $50 value, while supplies last.\n\nLock in this year's price and let the countdown begin.",
            "Our Christmas in July event is on — 40% off every pre-order when you plan ahead.\n\nPay in full or pay half, you still save 40%. Prefer to spread it out? Layaway splits it into 4 monthly payments.\n\nFor a limited time, every pre-order includes free island-wide delivery before November — plus a free 500-count Color-Changing LED Light Set with remote on any purchase over Afl 250 — a $50 value, while supplies last.\n\nThe best trees go early. Reserve yours today.",
            "Here's how pre-order works, and why it pays to be early:\n\nReserve now and save 40% — pay in full or pay half, your choice. Want to spread it out? Layaway splits it into 4 monthly payments.\n\nFor a limited time, every pre-order ships free before November, and any order over Afl 250 comes with a free 500-count Color-Changing LED Light Set with remote (a $50 value, while supplies last).\n\nNo stress, no last-minute scramble — just your tree, ready when you are.",
        ],
        "headline": [
            "Christmas in July — Up to 40% Off",
            "Pay Ahead, Save More",
            "Up to 40% Off — Reserve Now",
        ],
        "description": [
            "Free Delivery on Pre-Orders",
            "40% Off · Full or Half",
            "Free LED Set Over Afl 250",
        ],
        "cta": "Order Now",
        "hook": "Save 40% on any pre-order — pay in full or half, or spread it with Layaway. Free delivery before November.",
        "arc": "The pre-order offer — value stack + flexible payment (reciprocity)",
        "wave": 2,
        "stories": {
            "image": "Softly lit tree, lower third gives way to a clean cream panel with a coral '40% OFF' typographic treatment and a small gift-tag motif.",
            "text_overlay": "Save Up to 40%",
            "secondary_text": "40% off + free LED set over Afl 250",
            "cta_sticker": "Order Now",
        },
        "image_direction": IMG_AD3,
    }


def ad4():
    return {
        "num": 4,
        "title": "Christmas in July",
        "format": "Static image, 1080x1080 (square) + 1080x1920 (vertical)",
        "placements": ["Feed", "Stories", "Reels"],
        "primary_text": [
            "Christmas in July isn't a gimmick here — it's just how the island plans ahead.\n\nWhile everyone else waits, you can reserve your pre-lit tree now, save up to 40%, and have it delivered before November. No December scramble, no sold-out shelves.\n\nCelebrate Christmas in July with us and let the countdown begin. For a limited time: free island-wide delivery on every pre-order.",
            "Sunshine, blue skies, and a Christmas tree? That's Christmas in July, Aruba style.\n\nOur pre-order event is on now: reserve today, save up to 40%, and we'll deliver before November. Because the best time to think about December is right now.\n\nFor a limited time, pre-orders include free delivery across the island.",
            "Here's the secret to a stress-free December: handle it in July.\n\nReserve your pre-lit tree during our Christmas in July event — save up to 40%, lock in this year's price, and we'll deliver before November. Then you get to enjoy the season instead of scrambling for it.\n\nFor a limited time: free island-wide delivery on every pre-order.",
        ],
        "headline": [
            "Christmas in July",
            "Christmas in July, Aruba Style",
            "Get a Head Start on December",
        ],
        "description": [
            "Christmas in July · Up to 40% Off",
            "Reserve Now · Delivered by Nov",
            "Pre-Order Event On Now",
        ],
        "cta": "Shop Now",
        "hook": "Christmas in July? On an island with no winter, that's just good timing.",
        "arc": "Seasonal hook — Christmas in July, the delightful reason to reserve now (timing + urgency)",
        "wave": 2,
        "stories": {
            "image": "Bright, sunny Aruba poolside: a glowing multicolor pre-lit tree beside a turquoise pool under a blue summer sky, green tree skirt at the base — the delightful contrast of Christmas in July.",
            "text_overlay": "Christmas in July",
            "secondary_text": "Reserve now · Up to 40% off",
            "cta_sticker": "Shop Now",
        },
        "image_direction": IMG_AD4,
    }


def ad5():
    return {
        "num": 5,
        "title": "A Caribbean Christmas, done right",
        "format": "Static image, 1080x1080 (square) + 1080x1920 (vertical)",
        "placements": ["Feed", "Stories"],
        "primary_text": [
            "Christmas in Aruba doesn't need snow — it needs warmth, family, and a tree that glows against the trade winds.\n\nWe're the island's own Christmas store, bringing classic holiday magic home with a subtle island touch.\n\nJoin the families across Aruba making the season shine. Reserve your tree now — free delivery before November, for a limited time.",
            "Palm trees outside. A glowing pine inside. That's Christmas, island-style.\n\nAs Aruba's dedicated Christmas specialists, we know what a holiday here looks like — warm evenings, open doors, and a tree that brings everyone together.\n\nReserve yours now and celebrate the season the way only Aruba can. For a limited time, pre-orders include free delivery before November.",
            "Here, the holidays come with sunshine — and there's nothing wrong with that.\n\nBring home a pre-lit tree made for island living: effortless, glowing, and ready in minutes. Aruba's own Christmas store, for Aruba's homes.\n\nReserve now for guaranteed free delivery before November — a limited-time pre-order perk.",
        ],
        "headline": [
            "A Caribbean Christmas, Done Right",
            "No Snow Required",
            "Made for Island Living",
        ],
        "description": [
            "Aruba's Christmas Specialist",
            "Free Pre-Order Delivery",
            "Reserve Yours Today",
        ],
        "cta": "Shop Now",
        "hook": "No snow required. A Caribbean Christmas, done right.",
        "arc": "Island identity — a tradition made for Aruba homes (in-group bias)",
        "wave": 3,
        "stories": {
            "image": "Glowing tree on a breezy Aruban patio at golden hour, palms and a sliver of ocean beyond; string lights overhead. Warm, aspirational, unmistakably island.",
            "text_overlay": "A Caribbean Christmas",
            "secondary_text": "Aruba's own Christmas store",
            "cta_sticker": "Shop Now",
        },
        "image_direction": IMG_AD5,
    }


def ad6():
    return {
        "num": 6,
        "title": "Pre-orders close soon",
        "format": "Static image, 1080x1080 (square) + 1080x1920 (vertical)",
        "placements": ["Feed", "Stories"],
        "primary_text": [
            "Here's the honest truth about how we work: we're a small island business, not a big-box warehouse. Supplies are limited — and once a tree sells out, it's gone for the season.\n\nDeluxe models sell out early — pre-ordering is how you guarantee the exact one you want, at up to 40% off.\n\nReserve today — for a limited time, every pre-order includes free island-wide delivery before November.",
            "The pre-order window is closing.\n\nPre-ordering is how you lock in the tree you want at the best price of the year — because supplies are limited, and the most-loved styles always sell out first.\n\nReserve now for up to 40% off and free island-wide delivery before November — free delivery is a limited-time pre-order perk.",
            "Fair warning from the island's Christmas store: supplies are limited.\n\nDeluxe models sell out early — and once a style sells out, that's it until next year. Pre-ordering guarantees yours now, at up to 40% off.\n\nReserve today for free island-wide delivery before November, for a limited time.",
        ],
        "headline": [
            "Pre-Orders Close Soon",
            "Once We're Sold Out, That's It",
            "Don't Miss This Season",
        ],
        "description": [
            "Reserve Before the Window Closes",
            "Free Pre-Order Delivery",
            "Save Up to 40% Today",
        ],
        "cta": "Order Now",
        "hook": "Supplies are limited — once we're sold out for the season, that's it.",
        "arc": "Honest scarcity — limited supplies, sell-outs are final; trees stay available in-season but the best go first (scarcity)",
        "wave": 3,
        "stories": {
            "image": "Warm evening room with a lit tree, empty chair nearby; subtle hourglass motif and a restrained 'reserve before it's gone' treatment in coral. Intimate, not loud.",
            "text_overlay": "Pre-Orders Close Soon",
            "secondary_text": "Limited supplies · the best trees go first",
            "cta_sticker": "Order Now",
        },
        "image_direction": IMG_AD6,
    }


# ── Per-ad image direction (feed + stories layouts, grounded in brand) ────────

IMG_AD1 = """**Format:** 1080x1080 (feed) + 1080x1920 (stories) | **Placement:** Feed, Stories, Reels
**Layout:** Photo-hero, full-bleed. The feeling carries this ad — image first, minimal text.
**Emotional job:** Wave 1 opener. Make them *feel* Christmas at home before we sell anything.

```
FEED (1080x1080):
+--------------------------------------+
|  [Full-bleed photo: warm-lit         |
|   Aruban living room at dusk. A       |
|   glowing pre-lit tree beside an      |
|   open window; palm silhouettes +     |
|   last light outside. The tree is     |
|   the hero light source.]             |
|                                       |
|  LOGO (top-center, coral or white     |
|   knockout, small)                    |
|                                       |
|  [Lower gradient → deep slate]        |
|  "Christmas Comes Home to Aruba"      |
|  (serif, warm white, ~60px)           |
|  Pre-order now · Delivered before Nov |
|  (sans, white 80%, 26px)              |
|  [SHOP NOW] (coral #FF5A4F fill)      |
+--------------------------------------+

STORIES (1080x1920):
+--------------------+
| [TOP SAFE ~320px]  |
| [Full-bleed dusk   |
|  room + glowing    |
|  tree, vertical]   |
| LOGO (white)       |
| [gradient → slate] |
| "Christmas Comes   |
|  Home to Aruba"    |
| (serif, white)     |
| Delivered before   |
|  November          |
| [BTM SAFE ~400px]  |
| [SHOP NOW sticker, |
|  coral]            |
+--------------------+
```
**Photo direction:** Golden interior warmth, not clinical. Shoot or source a real island home if possible; the open window + palm light is what makes it Aruba, not a generic catalog room. Tree lights warm-white here (cozy register). If no lifestyle shot exists, a beautifully lit tree in a warm room works — the glow is non-negotiable.
""" + "\n" + BRAND

IMG_AD2 = """**Format:** 1080x1080 (feed) + 1080x1920 (stories) | **Placement:** Feed, Stories, Reels
**Layout:** Product-forward. Two-thirds photo (the lit tree / branch detail), one-third feature panel.
**Emotional job:** Wave 1 credibility. Pre-lit + remote + specialist = "these are the people who do this right."

```
FEED (1080x1080):
+--------------------------------------+
|  [Photo, upper ~65%: a fully lit      |
|   tree in a styled corner OR a macro  |
|   of a branch with the LED glow;      |
|   remote resting in frame.]           |
+--------------------------------------+
|  [Cream #F6F3EC panel, lower ~35%]    |
|  LOGO (coral, left)                   |
|  "Lit in Minutes, Not Hours"          |
|  (serif, deep slate #1F2A30)          |
|   Pre-lit   Color-changing LEDs     |
|   Remote included  (sans, slate)     |
|  [SHOP NOW] (coral fill, white text)  |
+--------------------------------------+

STORIES (1080x1920):
+--------------------+
| [TOP SAFE ~320px]  |
| [Lit tree/branch,  |
|  vertical, glow]   |
| [cream panel base] |
| LOGO (coral)       |
| "Lit in Minutes"   |
| (serif, slate)     |
| Color-changing LEDs|
|  + remote included |
| [BTM SAFE ~400px]  |
| [SHOP NOW sticker] |
+--------------------+
```
**Photo direction:** This is the one ad where product detail earns its place. Show the LED color-change (a warm-white-to-color gradient across the branch reads instantly) and the remote so "effortless" is visible, not just claimed. Keep the feature checklist to 3 items max — under the 15% text rule. Caribbean turquoise (#27C4C3) is allowed as a tiny accent on the checkmarks; coral stays the CTA.
""" + "\n" + BRAND

IMG_AD3 = """**Format:** 1080x1080 (feed) + 1080x1920 (stories) | **Placement:** Feed, Stories, Reels
**Layout:** Offer-forward, typographic. The number does the work: "UP TO 40% OFF."
**Emotional job:** Wave 2 value. The single clearest "reserve now, pay less" beat. This is the most text-forward ad in the set (the one allowed exception).

```
FEED (1080x1080):
+--------------------------------------+
|  [Background: softly lit tree, top    |
|   half, dimmed ~45% over cream/slate] |
|  LOGO (top-center, white/coral)       |
|                                       |
|  "SAVE UP TO"                         |
|  "40% OFF"  (coral #FF5A4F, big,      |
|   serif or heavy display, ~150px)     |
|  when you reserve early               |
|  (sans, white/slate)                  |
|                                       |
|  Free delivery · before November      |
|  Pay in full, 50/50, or layaway       |
|  (sans, 24px)                         |
|  [ORDER NOW] (coral fill)             |
+--------------------------------------+

STORIES (1080x1920):
+--------------------+
| [TOP SAFE ~320px]  |
| [dimmed tree top]  |
| LOGO (white)       |
| "SAVE UP TO"       |
| "40% OFF"          |
| (coral, large)     |
| Free delivery      |
|  before November   |
| Full / 50-50 /     |
|  layaway           |
| [BTM SAFE ~400px]  |
| [ORDER NOW sticker]|
+--------------------+
```
**Design note:** Coral #FF5A4F carries the "40%" — it is the brand's signal color and reads as festive without going full Christmas-red. Keep the payment options small and secondary; the hook is the discount + free delivery + the free LED light set. Offer ladder for reference: 100% upfront = 40% off, 50% upfront = 30% off, Layaway = 4 monthly payments (no discount). GWP: free 500-count Color-Changing LED Light Set with remote ($50 retail value) with any purchase over Afl 250, while supplies last. A subtle gift-tag or ribbon motif in coral is welcome.
""" + "\n" + BRAND

IMG_AD4 = """**Format:** 1080x1080 (feed) + 1080x1920 (stories) | **Placement:** Feed, Stories, Reels
**Layout:** Single-tree hero in a bright, sunny, summery Aruba setting — the delightful contrast IS the concept.
**Emotional job:** Wave 2 "Christmas in July" hook. Turns "why buy a tree in July?" into "of course — reserve now."
**Rescope note:** replaces the old three-tree range ad (the small alpine product couldn't sell a 3ft->9.5ft scale ladder). If a true range/scale visual is still wanted, do it as a Figma composite of the real 3ft/6ft/9.5ft trees.

```
FEED (1080x1080):
+--------------------------------------+
|  [Bright sunny Aruba poolside:        |
|   glowing multicolor pre-lit tree     |
|   beside a turquoise pool, blue        |
|   summer sky, white villa, rattan     |
|   loungers, cactus + aloe. GREEN       |
|   tree skirt at the base.]            |
|                                       |
|  clean sky space upper-left           |
|  "Christmas in July" (serif, white)   |
|  [SHOP NOW] (coral fill)              |
+--------------------------------------+

STORIES (1080x1920):
+--------------------+
| [TOP SAFE 250px]   |
| [sunny poolside,   |
|  tree + pool,      |
|  blue sky]         |
| "Christmas         |
|  in July"          |
| (serif, white)     |
| [BTM SAFE 340px]   |
| [SHOP NOW sticker] |
+--------------------+
```
**Photo direction:** Bright, cheerful, sun-drenched — warm late-afternoon so the tree lights still read against a blue summer sky. Turquoise pool, white-stucco villa, tropical loungers. The joke/hook is a fully-lit Christmas tree in obvious summer sunshine. Keep it believable and premium, not kitschy.
""" + "\n" + BRAND

IMG_AD5 = """**Format:** 1080x1080 (feed) + 1080x1920 (stories) | **Placement:** Feed, Stories
**Layout:** Photo-hero, full-bleed, aspirational lifestyle. Place + belonging.
**Emotional job:** Wave 3 identity. "This is *our* Christmas" — island pride, warmth, the emotional peak before the close.

```
FEED (1080x1080):
+--------------------------------------+
|  [Full-bleed photo: a glowing tree    |
|   on a breezy Aruban patio at golden  |
|   hour — palms, string lights, a      |
|   sliver of ocean. People optional    |
|   but a warm, candid family moment    |
|   lifts it. No snow, ever.]           |
|                                       |
|  LOGO (top-center, white knockout)    |
|                                       |
|  [lower gradient → deep slate]        |
|  "A Caribbean Christmas, Done Right"   |
|  (serif, warm white)                  |
|  Aruba's own Christmas store          |
|  (sans, white 80%)                    |
|  [SHOP NOW] (coral fill)              |
+--------------------------------------+

STORIES (1080x1920):
+--------------------+
| [TOP SAFE ~320px]  |
| [Full-bleed patio  |
|  golden hour +     |
|  glowing tree]     |
| LOGO (white)       |
| [gradient → slate] |
| "A Caribbean       |
|  Christmas"        |
| (serif, white)     |
| Aruba's own        |
|  Christmas store   |
| [BTM SAFE ~400px]  |
| [SHOP NOW sticker] |
+--------------------+
```
**Photo direction:** The most "Aruba" image in the campaign. Trade-wind light, palms, warm dusk, tree glow. This is where the "subtle island touch" is loudest — lean into it. Turquoise (#27C4C3) may appear naturally (ocean/sky) but keep the CTA coral. If a real local family/home is available, use it — authenticity beats stock here.
""" + "\n" + BRAND

IMG_AD6 = """**Format:** 1080x1080 (feed) + 1080x1920 (stories) | **Placement:** Feed, Stories
**Layout:** Intimate photo background + restrained scarcity line. Quiet urgency, not a fire sale.
**Emotional job:** Wave 3 close. The pre-order model *is* the scarcity — and it's honest. Make them act without cheapening the brand.

```
FEED (1080x1080):
+--------------------------------------+
|  [Background: warm evening room, lit   |
|   tree, an empty chair nearby — the    |
|   'your spot is waiting' feeling.      |
|   Dimmed ~40% over deep slate.]        |
|  LOGO (top-center, white)             |
|                                       |
|  "Pre-Orders Close Soon"              |
|  (serif, warm white, ~64px)           |
|  Limited supplies — sold out is       |
|   sold out.                           |
|  (sans, white 80%, 26px)              |
|                                       |
|  [thin coral rule]                    |
|  Free delivery before Nov · up to 40% |
|  [ORDER NOW] (coral fill)             |
+--------------------------------------+

STORIES (1080x1920):
+--------------------+
| [TOP SAFE ~320px]  |
| [Evening room +    |
|  lit tree, dimmed] |
| LOGO (white)       |
| "Pre-Orders        |
|  Close Soon"       |
| (serif, white,     |
|  large)            |
| Limited supplies · |
|  best trees first  |
| [coral rule]       |
| Free delivery ·    |
|  up to 40% off     |
| [BTM SAFE ~400px]  |
| [ORDER NOW sticker]|
+--------------------+
```
**Design note:** Restraint is the whole point — no countdown-clock kitsch, no red "SALE" banners. A subtle hourglass motif in coral is the most it should say visually. The honesty of the scarcity ("supplies are limited — sold out is sold out") is the differentiator; never imply nothing is for sale in-season (trees stay available — sell-outs are per style). Let the calm, warm image carry it. This is the retargeting/closer ad — it should feel like a gentle nudge from a shop you trust.
""" + "\n" + BRAND


# ── Per-ad TEXT & TYPE direction for Mayo (Figma). Type system from brand site:
#    Headlines = Playfair Display (serif); body/CTA = Assistant (sans). ──────────
_SAFE = ("SAFE ZONE (all placements): keep every text element and the CTA inside the central "
         "safe area. Feed 1080x1080/1080x1350 - stay off the outer ~5% margin and clear of the tree/product. "
         "Stories/Reels 1080x1920 - keep text below the top 250px and above the bottom 340px (Meta hides "
         "those behind profile + CTA UI). Type: Playfair Display headline + Assistant CTA. Less is more: "
         "headline + CTA only unless noted.")

TEXT_SPECS = {
    1: """**TEXT & TYPE — Mayo → Figma**
- Headline (Playfair 700, warm white): "Christmas Comes Home to Aruba"
- CTA: **Shop Now** (coral #FF5A4F pill) · small white logo top-center
- NO price/offer on the image — top-funnel, keep it clean.
- Placement: clean upper-left wall. """ + _SAFE,
    2: """**TEXT & TYPE — Mayo → Figma**
- Headline (Playfair 700): "Lit in Minutes, Not Hours"
- CTA: **Shop Now** (coral pill)
- NO price/offer on the image — product-led; offer lives in the caption.
- Placement: clear left third; product stays right. """ + _SAFE,
    3: """**TEXT & TYPE — Mayo → Figma** (OFFER AD — carries the on-image badge)
- On-image offer badge (Playfair 700, coral #FF5A4F, oversized): "Up to 40% Off" (must read "Up to" — tiered 40/30/Layaway)
- One micro line only (Assistant 400): "Free LED set over Afl 250" (full terms in the caption)
- CTA: **Order Now** (coral pill)
- Placement: badge over the sky/upper band with a soft scrim; keep the tree clear. """ + _SAFE,
    4: """**TEXT & TYPE — Mayo → Figma**
- Headline (Playfair 700, top): "Christmas in July"
- CTA: **Shop Now** (coral pill)
- NO price/offer on the image — the Christmas-in-July novelty is the hook.
- Placement: clean sky band up top. """ + _SAFE,
    5: """**TEXT & TYPE — Mayo → Figma**
- Headline (Playfair 700, warm white): "A Caribbean Christmas"
- CTA: **Shop Now** (coral pill, lower-left) · small white logo top-center
- NO price/offer on the image — brand/identity flagship, keep it clean.
- Placement: open warm sky upper-left. """ + _SAFE,
    6: """**TEXT & TYPE — Mayo → Figma** (SCARCITY/RETARGETING — carries the on-image badge)
- Headline (Playfair 700, warm white): "Pre-Orders Close Soon"
- On-image offer badge (Playfair 700, coral #FF5A4F): "Up to 40% Off" — pair with the scarcity, one clean element
- CTA: **Order Now** (coral pill)
- Placement: dark clean band at top. """ + _SAFE,
}


def main():
    data = {
        "campaign": "Christmas in Aruba — Pre-Order 2026 (B2C)",
        "event_date": "Christmas in July Pre-Order Event · Up to 40% off · Free LED set over Afl 250 · Delivered before Nov 1",
        "venue": "",
        "co_presenters": "",
        "page_name": "Christmas in Aruba",
        "ig_handle": "christmasinaruba",
        "brandmark": "images/cia-brandmark.png",
        "cta_url": "https://christmasinaruba.com",
        "compliance_notes": [
            "Offer: full or half pre-order = 40% off; Layaway = 4 equal monthly payments, no discount.",
            "GWP: free 500-count Color-Changing LED Light Set with remote control ($50 retail value) with any purchase over Afl 250, while supplies last.",
            "Free island-wide (Aruba) delivery on all pre-orders — limited time, pre-orders only; delivered before November 1. Copy must never present free delivery as a standing policy.",
            "Scarcity framing (client 2026-07-17): supplies are limited and sell-outs are final PER STYLE — but trees remain for sale in-season. Never imply the store will have nothing available outside the pre-order window.",
            "Wording (client 2026-07-21): don't state 'we'll have trees available all season long' — use the 'deluxe models sell out early' angle instead. Avoid calling the business a 'shop' (sounds like a physical retail location); 'store' or 'small island business' is fine.",
            "Prices/availability to confirm against live Shopify before launch (site currently shows Sold Out placeholders).",
        ],
        "hide_design_direction": False,
        "use_static_images": True,
        "ads": [ad1(), ad2(), ad3(), ad4(), ad5(), ad6()],
        "client": "christmas-in-aruba",
    }
    # Stories animated text — bring the % offer home on every vertical.
    story_offer = {
        1: "Up to 40% Off · Delivered before Nov",
        2: "Up to 40% Off · Free island delivery",
        3: "Save 40% · Pay Full or Half · Free LED set over Afl 250",
        4: "Up to 40% Off · Reserve now",
        5: "Up to 40% Off · Delivered before Nov",
        6: "Up to 40% Off · Free delivery before Nov",
    }
    # Wire feed + story creative into the preview images/ dir, append Mayo direction,
    # and surface the offer in the animated Stories text.
    for ad in data["ads"]:
        ad["images"] = [f"ad{ad['num']}-feed.png", f"ad{ad['num']}-story.png"]
        spec = TEXT_SPECS.get(ad["num"])
        if spec:
            ad["image_direction"] = f"{spec}\n\n---\n\n{ad['image_direction']}"
        if ad["num"] in story_offer and isinstance(ad.get("stories"), dict):
            ad["stories"]["secondary_text"] = story_offer[ad["num"]]
    out = HERE / "data.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out} — {len(data['ads'])} ads")


if __name__ == "__main__":
    main()
