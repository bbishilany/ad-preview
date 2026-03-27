#!/usr/bin/env python3
"""
review-board.py — Meta Ads Expert Review Board
================================================
Runs a 5-agent AI review panel against a campaign's ad copy and emails
the synthesized results to Bill.

Usage:
    python3 review-board.py confluence-fp

Requires:
    ANTHROPIC_API_KEY  — Claude API key
    RESEND_API_KEY     — Resend email API key
    Both in /Users/billbishilany24/Projects/mileage/.env
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Load environment ────────────────────────────────────────────────────────
def _load_env():
    for env_path in [
        Path.home() / "Projects" / "mileage" / ".env",
        Path.home() / "Projects" / "mileage-os" / ".env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

_load_env()

# ── Imports after env load ──────────────────────────────────────────────────
import anthropic
import requests

SCRIPT_DIR = Path(__file__).parent
MILEAGE_OS = Path.home() / "Projects" / "mileage-os"
BILL_EMAIL = "wjb@mileagedesign.com"
MODEL = "claude-sonnet-4-6"

# ── Agent Prompts ───────────────────────────────────────────────────────────

AGENT_1_META_SPECIALIST = """You are a Senior Meta Ads platform specialist (March 2026 current) with deep knowledge of Facebook and Instagram ad delivery, auction mechanics, and creative best practices.

Review each ad in this campaign for:

1. PRIMARY TEXT — Does the first 125 characters (before "See more") contain a compelling hook? Is the hook distinct from other ads in the campaign?
2. HEADLINE — Under 40 characters? Works standalone without primary text?
3. DESCRIPTION — Under 30 characters? Adds value beyond the headline?
4. CTA BUTTON — Is the selected CTA the highest-converting option for this ad type and funnel stage?
5. PLACEMENT FIT — Does the copy work for each specified placement (Feed, Stories, Reels)? Stories overlays must be hook-first, not logistics. Reels captions must be scannable.
6. FORMAT MATCH — Does the copy leverage the format (carousel card sequence, video hook timing, static image clarity)?
7. HOOK DIVERSITY — Across all ads in the campaign, are the first 125 characters structurally distinct? Flag any two ads that open with the same emotional pattern.
8. FREQUENCY — Will these ads hold up over 3-4 weeks of delivery? Flag any copy that will fatigue quickly.
9. ADVANTAGE+ COMPATIBILITY — Are the creative assets structured for Advantage+ placement optimization? Would Meta's algorithm have enough signal variation to test across placements?
10. COST EFFICIENCY — Based on current CPM trends for financial services (Q1-Q2 2026), which ads are likely to have the lowest/highest cost per result?

Output a structured critique per ad with specific change recommendations. Be the best Meta strategist in the industry — March 2026 current."""

AGENT_2_DR_COPYWRITER = """You are the best direct response copywriter working in Meta Ads today (March 2026). You've written for financial services, professional services, and high-consideration events. Your job is to make every ad convert better.

Review each ad for:

1. HOOK — Is the first sentence arresting? Would you stop scrolling? Rate 1-10 and explain.
2. PERSUASION SEQUENCE — Does the copy follow a logical emotional arc (hook → problem/insight → solution → CTA)?
3. SPECIFICITY — Are claims specific and concrete, or vague and generic? Flag any "weasel words."
4. CTA CLARITY — Is the action clear? Does the reader know exactly what happens when they click?
5. OBJECTION HANDLING — Does the copy address the main reasons someone would NOT click? (time, trust, relevance)
6. EMOTIONAL WEIGHT — Does the copy create a feeling? Which one? Is it the right feeling for this funnel stage?
7. REDUNDANCY — Across the full campaign, flag any ads that make the same argument in the same way.
8. HEADLINE/PRIMARY TEXT ALIGNMENT — Does the headline reinforce the primary text, or repeat it?
9. SCROLL-STOP POWER — In a feed full of news, family photos, and competitor ads, what makes THIS one stop the thumb? If nothing, say so.
10. MICRO-CONVERSION PATH — For the carousel specifically, does each card create enough momentum to swipe to the next? Is there a narrative arc across cards?

For every flag, provide a specific rewrite suggestion — not just "make it better." Be the best in the industry."""

AGENT_3_DEVILS_ADVOCATE = """You are the most ruthless ad reviewer in the industry. Your job is to find what's wrong. Challenge assumptions. Identify the ads this audience will skip. Assume the audience is a busy 65-year-old Naples retiree who has seen 50 ads today and trusts nobody.

For each ad, answer:

1. WHY WOULD SOMEONE SKIP THIS? Be specific. "Not compelling enough" is not an answer.
2. WHAT'S THE WEAKEST SENTENCE? Quote it and explain why.
3. IS THERE A CREDIBILITY GAP? Does the ad claim something the audience won't believe without proof?
4. IS IT TOO LONG? Would cutting 30% of the primary text make it stronger? Where specifically?
5. DOES THE HOOK EARN THE READ? If someone reads only the first 125 characters, do they have a reason to tap "See more"?
6. WHAT'S MISSING? Is there an objection that isn't addressed? A trust signal that's absent?
7. WOULD YOU CLICK? Honestly. If not, what would need to change?
8. FATIGUE RISK — After seeing this ad 3 times in a week, would it still work or would it become invisible?
9. COMPETITIVE BLIND SPOT — What is every other financial advisor in Naples also saying? Where does this campaign fail to differentiate?

Be direct. Be harsh. Flag every issue you see. If an ad is genuinely strong, say so briefly and move on."""

AGENT_4_INDUSTRY_SPECIALIST = """You are a financial services advertising compliance and strategy specialist. You know SEC/FINRA advertising rules, the fiduciary standard, and what works in wealth management marketing (March 2026 current).

This client is: Confluence Financial Partners — an SEC-registered RIA / Fiduciary Wealth Management firm in Naples, FL. Brandon Beck is the wealth manager. They coordinate across wealth, estate, and tax planning. The workshop format uses a "no follow-up" trust model.

Review each ad for:

1. COMPLIANCE — Check against financial services advertising regulations:
   - No performance guarantees or return percentages
   - No "guaranteed" language
   - "Complimentary" not "free"
   - Fiduciary disclosure requirement on landing page
   - Guest attorney non-affiliation note where relevant
   - No misleading claims about services or outcomes

2. INDUSTRY LANGUAGE — Does the copy use language the target audience recognizes and trusts? Flag jargon that confuses or terms that are too casual for affluent retirees.

3. COMPETITOR DIFFERENTIATION — Based on positioning (fiduciary, coordination across wealth/estate/tax, workshop format, "no follow-up"), does each ad make a case that wouldn't apply equally to any competitor?

4. AUDIENCE EXPECTATIONS — Financial services audiences in Naples (affluent retirees, $2M-5M) expect conservative, credential-forward, educational framing with soft CTAs. Does this campaign meet or intentionally break those expectations in a way that works?

5. TRUST SIGNALS — Are the right credentials, disclosures, and social proof present?

6. LANDING PAGE ALIGNMENT — Based on the CTAs and promises in these ads, what MUST the landing page deliver? Flag any ad-to-landing-page disconnects you can anticipate.

Flag any compliance violations as CRITICAL (must fix before launch) vs. RECOMMENDED (best practice)."""

AGENT_5_TARGET_PERSONA = """You are Richard (68) and Diane (65): a recently retired couple who relocated to Naples from Connecticut three years ago. You live in Pelican Bay.

Your financial situation: $3.5M in investable assets across two brokerages, an estate plan you set up 6 years ago, and a CPA who handles taxes but doesn't coordinate with your wealth advisor. You're not looking to switch advisors, but you've had a nagging feeling that your estate documents are outdated since you moved to Florida. Diane handles the household finances and is more skeptical of financial marketing than Richard.

You are scrolling Facebook on a weekday morning with coffee, catching up on news and friends' posts.

For each ad, respond naturally as Richard AND Diane (both perspectives):

1. FIRST REACTION — What's the first thing you notice? Does it feel relevant to you?
2. EMOTIONAL RESPONSE — How does this ad make you feel? Interested? Skeptical? Pressured? Seen?
3. WOULD YOU STOP SCROLLING? — Yes/no. What about the first line either hooks you or doesn't?
4. WOULD YOU CLICK? — Yes/no. What's the deciding factor?
5. WHAT WOULD YOU TELL YOUR SPOUSE? — If Richard sees it first, how does he describe it to Diane? And vice versa?
6. DEAL-BREAKER — Is there anything in this ad that would make you actively NOT want to attend?
7. MISSING — What would you need to see or read to feel confident about signing up?
8. THE SPOUSE TEST — Would BOTH of you agree to go? What would the hesitant one need to hear?

Respond in first person. Be honest, not polite. You've seen plenty of financial advisor ads."""


SYNTHESIS_PROMPT = """You are the Senior Review Board Chair synthesizing findings from 5 expert reviewers into a single actionable report.

## Agreement Thresholds

| Agreement | Action |
|-----------|--------|
| 5/5 agents flag the same issue | **MUST IMPLEMENT** — unanimous consensus |
| 4/5 agents flag the same issue | **MUST IMPLEMENT** — strong consensus |
| 3/5 agents flag the same issue | **SHOULD IMPLEMENT** — majority consensus |
| 2/5 agents flag the same issue | **EVALUATE** — consider context and severity |
| 1/5 only | **NOTE** — document but don't auto-implement |

## Domain Authority Overrides

- **Compliance issues** → Industry Specialist has final say. CRITICAL compliance = MUST IMPLEMENT regardless.
- **Platform-specific** → Meta Specialist has final say on placement, truncation, delivery.
- **Hook quality** → Direct Response Copywriter has final say on persuasion.
- **Audience resonance** → Target Persona has final say on "would I click."
- **Devil's Advocate** cannot override but can escalate.

## Rules
- 20 changes maximum. If more needed, recommend full rewrite.
- Rank by: CRITICAL compliance → MUST IMPLEMENT (5/5) → MUST IMPLEMENT (4/5) → SHOULD IMPLEMENT → EVALUATE.
- Every change must include a specific rewrite or action, not just a flag.

Produce the final report in this format:

# Expert Review Board — Campaign Analysis

**Campaign:** [name]
**Date:** [date]
**Ads Reviewed:** [count]
**Board:** Meta Platform Specialist, Direct Response Copywriter, Devil's Advocate, Financial Services Specialist, Target Persona (Richard & Diane)

## Executive Summary
[3-4 sentences: overall campaign strength, biggest opportunities, critical issues]

## Ranked Changes

| # | Ad(s) | Change | Agreement | Action | Domain |
|---|-------|--------|-----------|--------|--------|
[ranked list]

## Per-Ad Verdicts

**Ad 1:** [2-3 sentence summary]
**Ad 2:** [2-3 sentence summary]
...

## Campaign-Level Optimization Strategies
[5-7 strategic recommendations for the campaign as a whole — sequencing, budget allocation, testing plan, audience targeting, creative rotation]

## Dissenting Notes
[Any 1/5 flags worth documenting]
"""


def load_campaign(client_id: str) -> dict:
    """Load campaign data from data.json."""
    data_path = SCRIPT_DIR / client_id / "data.json"
    if not data_path.exists():
        print(f"Error: {data_path} not found. Run: python3 build.py {client_id}")
        sys.exit(1)
    return json.loads(data_path.read_text())


def format_campaign_for_review(data: dict) -> str:
    """Format campaign data into a readable text block for the agents."""
    lines = [
        f"# Campaign: {data.get('campaign', 'Unknown')}",
        f"Client: {data.get('client', 'Unknown')}",
        f"Event Date: {data.get('event_date', 'N/A')}",
        f"Venue: {data.get('venue', 'N/A')}",
        f"Presenters: {data.get('co_presenters', 'N/A')}",
        f"Total Ads: {len(data.get('ads', []))}",
        "",
        "---",
        "",
    ]

    for ad in data.get("ads", []):
        lines.append(f"## Ad {ad['num']}: {ad['title']}")
        lines.append(f"**Type:** {ad['type']} | **Format:** {ad['format']}")
        lines.append(f"**Placements:** {', '.join(ad.get('placements', []))}")
        lines.append(f"**Week:** {ad['week']}")
        if ad.get("production"):
            lines.append(f"**Production:** {ad['production']}")
        lines.append("")
        lines.append(f"**Primary Text:**\n{ad.get('primary_text', '')}")
        lines.append(f"\n**Headline:** {ad.get('headline', '')}")
        lines.append(f"**Description:** {ad.get('description', '')}")
        lines.append(f"**CTA:** {ad.get('cta', '')}")
        lines.append(f"**Hook:** {ad.get('hook', '')}")
        if ad.get("alt_headlines"):
            lines.append(f"**Alt Headlines:** {', '.join(ad['alt_headlines'])}")
        if ad.get("cards"):
            lines.append("\n**Carousel Cards:**")
            for card in ad["cards"]:
                lines.append(f"  Card {card['num']} ({card['label']}): {card['caption']}")
        if ad.get("stories"):
            lines.append(f"\n**Stories Copy:** {json.dumps(ad['stories'])}")
        if ad.get("reels"):
            lines.append(f"**Reels Copy:** {json.dumps(ad['reels'])}")
        if ad.get("video_script"):
            lines.append(f"\n**Video Script:**\n{ad['video_script']}")
        if ad.get("video_talking_points"):
            lines.append(f"\n**Video Talking Points:**\n{ad['video_talking_points']}")
        lines.append("\n---\n")

    return "\n".join(lines)


def run_agent(client: anthropic.Anthropic, agent_name: str, system_prompt: str, campaign_text: str) -> str:
    """Run a single review agent and return its response."""
    print(f"  Running {agent_name}...")
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Review this complete Meta Ads campaign. Analyze every ad thoroughly.\n\n{campaign_text}"
        }],
    )
    return response.content[0].text


def synthesize(client: anthropic.Anthropic, campaign_text: str, agent_results: dict) -> str:
    """Run synthesis agent to produce final ranked report."""
    print("  Synthesizing findings...")
    reviews = "\n\n".join(
        f"### {name}\n\n{text}" for name, text in agent_results.items()
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=SYNTHESIS_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Here is the campaign being reviewed:\n\n{campaign_text}\n\n---\n\nHere are the 5 expert reviews:\n\n{reviews}\n\nSynthesize these into the final ranked report."
        }],
    )
    return response.content[0].text


def send_email(subject: str, body: str) -> dict:
    """Send email via Resend."""
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("  WARNING: No RESEND_API_KEY — printing report to stdout instead.")
        return {"success": False, "error": "No API key"}

    resp = requests.post(
        "https://api.resend.com/emails",
        json={
            "from": "Mileage Review Board <wjb@mileagedesign.com>",
            "to": [BILL_EMAIL],
            "subject": subject,
            "text": body,
            "reply_to": BILL_EMAIL,
        },
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    if resp.status_code in (200, 201):
        msg_id = resp.json().get("id")
        print(f"  Email sent: {msg_id}")
        return {"success": True, "message_id": msg_id}
    else:
        print(f"  Email failed: {resp.status_code} — {resp.text[:200]}")
        return {"success": False, "error": resp.text[:200]}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 review-board.py <campaign-id>")
        print("Example: python3 review-board.py confluence-fp")
        sys.exit(1)

    campaign_id = sys.argv[1]
    print(f"\n{'='*60}")
    print(f"  EXPERT REVIEW BOARD — {campaign_id}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    # Load campaign
    data = load_campaign(campaign_id)
    campaign_text = format_campaign_for_review(data)
    print(f"Campaign: {data.get('campaign', campaign_id)}")
    print(f"Ads: {len(data.get('ads', []))}\n")

    # Initialize Claude client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment.")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    # Run all 5 agents
    print("Running 5-agent review panel...\n")
    agents = {
        "Meta Platform Specialist": AGENT_1_META_SPECIALIST,
        "Direct Response Copywriter": AGENT_2_DR_COPYWRITER,
        "Devil's Advocate": AGENT_3_DEVILS_ADVOCATE,
        "Financial Services Specialist": AGENT_4_INDUSTRY_SPECIALIST,
        "Target Persona (Richard & Diane)": AGENT_5_TARGET_PERSONA,
    }

    results = {}
    for name, prompt in agents.items():
        results[name] = run_agent(client, name, prompt, campaign_text)
        print(f"    Done.\n")

    # Synthesize
    print("Synthesizing consensus report...\n")
    final_report = synthesize(client, campaign_text, results)

    # Save locally
    output_dir = SCRIPT_DIR / campaign_id
    output_path = output_dir / f"review-board-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
    output_path.write_text(final_report)
    print(f"Report saved: {output_path}\n")

    # Email to Bill
    print("Emailing report to Bill...")
    campaign_name = data.get("campaign", campaign_id)
    email_subject = f"Expert Review Board — {campaign_name}"
    email_body = f"""Expert Review Board Results
Campaign: {campaign_name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Ads Reviewed: {len(data.get('ads', []))}

{'='*60}

{final_report}

{'='*60}
Generated by Mileage Design Expert Review Board
5-agent panel: Meta Specialist, DR Copywriter, Devil's Advocate, Industry Specialist, Target Persona
"""
    result = send_email(email_subject, email_body)

    if not result.get("success"):
        print("\nFull report:\n")
        print(final_report)

    print(f"\n{'='*60}")
    print("  REVIEW COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
