#!/usr/bin/env python3
"""
Supabase -> Mileage OS feedback bridge.

Queries Supabase for feedback on a campaign, writes structured markdown
into the client's copy folder, and stamps pulled_at on exported rows.

Usage: python pull-feedback.py confluence-fp
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from supabase import create_client
except ImportError:
    print("Error: supabase-py not installed. Run: pip install supabase")
    sys.exit(1)

MILEAGE_OS = Path.home() / "Projects" / "mileage-os"


def load_env():
    """Load .env files from standard Mileage locations."""
    for env_path in [
        Path.home() / "Projects" / "mileage" / ".env",
        Path.home() / "Projects" / "mileage-os" / ".env",
    ]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())


def pull_feedback(campaign_id: str) -> None:
    """Pull feedback from Supabase and write to Mileage OS."""
    load_env()

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        sys.exit(1)

    sb = create_client(url, key)

    # Query only rows that haven't been pulled yet
    result = (
        sb.table("feedback")
        .select("*")
        .eq("campaign_id", campaign_id)
        .is_("pulled_at", "null")
        .order("ad_num")
        .order("created_at")
        .execute()
    )

    rows = result.data
    if not rows:
        print(f"No new feedback for campaign: {campaign_id}")
        return

    # Group by ad_num
    by_ad: dict[int, list[dict]] = {}
    for row in rows:
        ad_num = row["ad_num"]
        by_ad.setdefault(ad_num, []).append(row)

    # Build markdown
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = len(rows)
    verdicts = {"approve": 0, "request_changes": 0, "comment_only": 0}
    for row in rows:
        v = row.get("verdict", "comment_only")
        verdicts[v] = verdicts.get(v, 0) + 1

    lines = [
        "# External Review Feedback — Meta Ads Campaign",
        "",
        f"**Pulled:** {now}",
        "**Source:** Ad Preview (GitHub Pages) -> Supabase",
        f"**Total reviews:** {total} across {len(by_ad)} ads",
        "",
        "---",
        "",
    ]

    verdict_labels = {
        "approve": "Approve",
        "request_changes": "Request Changes",
        "comment_only": "Comment Only",
    }

    for ad_num in sorted(by_ad.keys()):
        ad_rows = by_ad[ad_num]
        # Get ad title from first row if available
        lines.append(f"## Ad {ad_num}")
        lines.append("")

        for row in ad_rows:
            name = row.get("reviewer_name", "Anonymous")
            role = row.get("reviewer_role", "Unknown")
            verdict = verdict_labels.get(row.get("verdict", ""), row.get("verdict", ""))
            comment = row.get("comment", "").strip()

            lines.append(f"### {name} ({role}) — {verdict}")
            if comment:
                # Preserve multi-line comments as blockquotes
                for cline in comment.splitlines():
                    lines.append(f"> {cline}")
            else:
                lines.append("> (No comment)")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Write the feedback file
    copy_dir = MILEAGE_OS / "clients" / campaign_id / "copy"
    copy_dir.mkdir(parents=True, exist_ok=True)
    output_path = copy_dir / "feedback-meta-ads-external.md"

    # If file already exists, append new feedback
    if output_path.exists():
        existing = output_path.read_text(encoding="utf-8")
        # Add separator and new feedback
        content = existing.rstrip() + "\n\n---\n\n# New Feedback Pull\n\n" + "\n".join(lines[2:])
    else:
        content = "\n".join(lines)

    output_path.write_text(content, encoding="utf-8")
    print(f"Written: {output_path}")

    # Stamp pulled_at on all exported rows
    row_ids = [row["id"] for row in rows]
    pulled_at = datetime.now(timezone.utc).isoformat()
    for row_id in row_ids:
        sb.table("feedback").update({"pulled_at": pulled_at}).eq("id", row_id).execute()

    print(f"\nSummary: {total} reviews across {len(by_ad)} ads")
    print(f"  Approve: {verdicts['approve']}")
    print(f"  Request Changes: {verdicts['request_changes']}")
    print(f"  Comment Only: {verdicts['comment_only']}")
    print(f"  Stamped pulled_at on {len(row_ids)} rows")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pull-feedback.py <campaign-id>")
        print("Example: python pull-feedback.py confluence-fp")
        sys.exit(1)

    pull_feedback(sys.argv[1])
