#!/usr/bin/env python3
"""Append the Hormozi-fingerprint challenger wave to mileage-benchmark/data.json.

New wave group "fp" with three cards (nums 13-15), one per flexible ad. The
round-4 cards (1-12) are untouched. Source of the texts:
mileage-os data-clients/mileage-design/flightdeck/benchmark-meta-500m/copy/challenger-deck-hormozi.md
"""
import json

T1S_H = """Your book says referrals built this firm. Your book is right.

It is also half the data.

The benchmark shows the other half. Your firm, scored next to the four firms covering the most ground in your metro. Two fields, about thirty seconds.

The introductions still happen. The trust still transfers. The name still gets passed along.

50% of investors with $5M+ found their current advisor with no referral involved (Ficomm Partners and Absolute Engagement, 2026).

Half the market chooses an advisor in a way no book records. Not lost. Never counted.

Most of those routes a firm cannot build. One it can: what the market shows when someone looks the firm up.

The report comes back in about ten minutes. Yours either way.

Built for RIAs at and beyond $500M in AUM."""

T2_H = """The site got rebuilt. The search work runs every month. Both send you reporting.

The benchmark is the read neither one is built to give: your firm, scored the same way as the four firms covering the most ground in your metro, plus the condition of the site underneath. Two fields, about thirty seconds.

The relationships still bring people in. Nothing here replaces that engine.

What changed is how people choose. Some of the tools they use now did not exist when most sites were last rebuilt.

25% of investors under 45 used an AI tool while choosing an advisor (Ficomm Partners and Absolute Engagement, 2026).

One new question for the site: can an answer engine read it.

If the read matches what you're seeing, that is worth knowing. If it differs, it is a useful conversation with whoever runs the work.

About ten minutes later you have it, yours either way: an independently measured view of the market you're growing in.

Built for RIAs at and beyond $500M in AUM."""

T3_H = """Your name gets handed to someone who already trusts the person saying it. That part still works, and nothing here changes it.

The benchmark measures what happens next. Your firm, scored next to the four firms covering the most ground in your metro. Two fields, about thirty seconds.

One 2025 Wealthtender study asked two questions. 62% start with a recommendation from friends or family.

And, separately, 96% of prospects research advisors online before they decide who to hire (Wealthtender, 2025).

Both are true at once. Only one of them happens where you can see it.

The introduction earns the first look. The next few minutes decide the meeting. Nobody watches those minutes.

The report comes back in about ten minutes. Yours either way.

Built for RIAs at and beyond $500M in AUM."""

WAVE = {
    "key": "fp",
    "label": "Caption challengers · Hormozi fingerprint",
    "title": "Three challenger captions, DRAFT and ungated",
    "subtitle": ("Same three flexible units, same locked headline, description, images and cards. "
                 "Only the primary text changes: the gated arguments rewritten at the cadence of the "
                 "Alex Hormozi account's measured caption fingerprint (750 active ads, 12 captions). "
                 "Every deck rule held; mechanical checks run clean."),
    "gate": ("Serena's Gate B pass on all three texts, then Bill's pick. Challengers never replace a "
             "gated control silently; if run, they test cadence only, same unit otherwise."),
}


def make_card(num, src, arc_note, text):
    card = {k: src[k] for k in src}
    card["num"] = num
    card["title"] = src["title"].split(" — ")[0] + " H — fingerprint challenger"
    card["wave"] = "fp"
    card["arc"] = arc_note
    card["primary_text"] = [text]
    card["variation"] = "Challenger caption · same 5 image assets"
    card["production"] = ("DRAFT, UNGATED challenger primary text at direct-response cadence. Headline, "
                          "description, CTA, images and on-image cards identical to the control unit. "
                          "Source: flightdeck copy/challenger-deck-hormozi.md.")
    return card


def main():
    d = json.load(open("mileage-benchmark/data.json"))

    assert all(a["num"] != 13 for a in d["ads"]), "challenger cards already present"
    by_num = {a["num"]: a for a in d["ads"]}

    d["waves"].append(WAVE)
    d["ads"].append(make_card(13, by_num[1],
        "T1-S argument at fingerprint cadence — belief conceded then completed, triad as validation", T1S_H))
    d["ads"].append(make_card(14, by_num[2],
        "T2 argument at fingerprint cadence — incumbent validated, scope-gap frame above the figure", T2_H))
    d["ads"].append(make_card(15, by_num[3],
        "T3 argument at fingerprint cadence — visibility reframe, chain and de-nesting devices intact", T3_H))

    json.dump(d, open("mileage-benchmark/data.json", "w"), indent=2, ensure_ascii=False)
    print(f"waves: {[w['key'] for w in d['waves']]}")
    print(f"ads: {[a['num'] for a in d['ads']]}")


if __name__ == "__main__":
    main()
