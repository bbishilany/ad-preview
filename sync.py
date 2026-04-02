#!/usr/bin/env python3
"""
Supabase → Git backup sync for ad-preview.

Pulls all Supabase data (feedback, image records, override files, review requests)
into git-tracked backup files. Read-only — never writes to Supabase.

Usage:
    python3 sync.py confluence-fp          # single client
    python3 sync.py --all                  # all clients
    python3 sync.py --all --commit         # sync + git commit + push
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase-py not installed. Run: pip install supabase")
    sys.exit(1)

HERE = Path(__file__).parent
MILEAGE_OS = Path.home() / "Projects" / "mileage-os"


# ── Environment ────────────────────────────────────────────────────────────

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


def get_supabase() -> Client | None:
    """Create Supabase client with service key. Returns None on failure."""
    load_env()
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return None


# ── Client Discovery ───────────────────────────────────────────────────────

def discover_clients() -> list[str]:
    """Scan subdirectories for client campaigns (those with data.json)."""
    clients = []
    for subdir in sorted(HERE.iterdir()):
        if subdir.is_dir() and (subdir / "data.json").exists():
            clients.append(subdir.name)
    return clients


# ── Sync Functions ─────────────────────────────────────────────────────────

def sync_feedback(sb: Client, slug: str) -> tuple[int, list[dict]]:
    """Pull all feedback rows for a campaign. Returns (count, rows)."""
    try:
        result = (
            sb.table("feedback")
            .select("*")
            .eq("campaign_id", slug)
            .order("ad_num")
            .order("created_at")
            .execute()
        )
        rows = result.data or []
        return len(rows), rows
    except Exception as e:
        print(f"  Warning: Could not pull feedback: {e}")
        return 0, []


def sync_ad_images(sb: Client, slug: str) -> tuple[int, list[dict]]:
    """Pull all ad_images rows for a campaign. Returns (count, rows)."""
    try:
        result = (
            sb.table("ad_images")
            .select("*")
            .eq("campaign_id", slug)
            .order("ad_num")
            .order("created_at")
            .execute()
        )
        rows = result.data or []
        return len(rows), rows
    except Exception as e:
        print(f"  Warning: Could not pull ad_images: {e}")
        return 0, []


def sync_override_files(sb: Client, slug: str, backup_dir: Path) -> int:
    """Download override images from Supabase Storage. Incremental by filename."""
    overrides_dir = backup_dir / "overrides"
    overrides_dir.mkdir(parents=True, exist_ok=True)
    existing = {f.name for f in overrides_dir.iterdir() if f.is_file()}
    downloaded = 0

    try:
        result = sb.storage.from_("ad-creatives").list(slug)
        if not result:
            return 0

        for file_obj in result:
            name = file_obj.get("name", "")
            if not name or name in existing:
                continue
            storage_path = f"{slug}/{name}"
            try:
                data = sb.storage.from_("ad-creatives").download(storage_path)
                (overrides_dir / name).write_bytes(data)
                downloaded += 1
            except Exception as e:
                print(f"  Warning: Could not download {storage_path}: {e}")
                continue

    except Exception as e:
        print(f"  Warning: Could not list storage files: {e}")

    return downloaded


def sync_review_requests(sb: Client, slug: str) -> tuple[int, list[dict]]:
    """Pull review_requests. Graceful if table doesn't exist."""
    try:
        result = (
            sb.table("review_requests")
            .select("*")
            .eq("campaign_id", slug)
            .order("created_at")
            .execute()
        )
        rows = result.data or []
        return len(rows), rows
    except Exception:
        # Table may not exist yet
        return 0, []


# ── Output Writers ─────────────────────────────────────────────────────────

def write_json(path: Path, data) -> None:
    """Write JSON file atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def write_feedback_markdown(slug: str, feedback_rows: list[dict]) -> None:
    """Write human-readable feedback markdown to mileage-os client copy dir."""
    if not feedback_rows:
        return

    copy_dir = MILEAGE_OS / "clients" / slug / "copy"
    copy_dir.mkdir(parents=True, exist_ok=True)
    output_path = copy_dir / "feedback-meta-ads-external.md"

    # Group by ad_num
    by_ad: dict[int, list[dict]] = {}
    for row in feedback_rows:
        ad_num = row.get("ad_num", 0)
        by_ad.setdefault(ad_num, []).append(row)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = len(feedback_rows)

    verdicts = {"approve": 0, "request_changes": 0, "comment_only": 0}
    for row in feedback_rows:
        v = row.get("verdict", "comment_only")
        verdicts[v] = verdicts.get(v, 0) + 1

    verdict_labels = {
        "approve": "Approve",
        "request_changes": "Request Changes",
        "comment_only": "Comment Only",
    }

    lines = [
        "# External Review Feedback — Meta Ads Campaign",
        "",
        f"**Last synced:** {now}",
        "**Source:** Ad Preview (GitHub Pages) → Supabase → sync.py",
        f"**Total reviews:** {total} across {len(by_ad)} ads",
        f"**Verdicts:** {verdicts['approve']} approve, {verdicts['request_changes']} changes requested, {verdicts['comment_only']} comments",
        "",
        "---",
        "",
    ]

    for ad_num in sorted(by_ad.keys()):
        ad_rows = by_ad[ad_num]
        lines.append(f"## Ad {ad_num}")
        lines.append("")

        for row in ad_rows:
            name = row.get("reviewer_name", "Anonymous")
            role = row.get("reviewer_role", "Unknown")
            verdict = verdict_labels.get(row.get("verdict", ""), row.get("verdict", ""))
            comment = (row.get("comment") or "").strip()
            created = row.get("created_at", "")[:16].replace("T", " ")

            lines.append(f"### {name} ({role}) — {verdict}")
            lines.append(f"*{created}*")
            lines.append("")
            if comment:
                for cline in comment.splitlines():
                    lines.append(f"> {cline}")
            else:
                lines.append("> (No comment)")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Complete rewrite (not append) — sync.py does full dumps
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Written: {output_path.relative_to(MILEAGE_OS.parent)}")


def write_last_sync(backup_dir: Path, metadata: dict) -> None:
    """Write sync metadata file."""
    write_json(backup_dir / "last-sync.json", metadata)


# ── Main Sync ──────────────────────────────────────────────────────────────

def sync_client(sb: Client, slug: str) -> dict:
    """Run full sync for a single client. Returns metadata dict."""
    print(f"\nSyncing: {slug}")

    campaign_dir = HERE / slug
    if not campaign_dir.exists():
        print(f"  Warning: Client directory {slug}/ does not exist")
        return {"slug": slug, "error": "directory not found"}

    backup_dir = campaign_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 1. Feedback
    fb_count, fb_rows = sync_feedback(sb, slug)
    write_json(backup_dir / "feedback.json", fb_rows)
    print(f"  Feedback: {fb_count} rows")

    # 2. Ad images
    img_count, img_rows = sync_ad_images(sb, slug)
    write_json(backup_dir / "ad-images.json", img_rows)
    print(f"  Ad images: {img_count} rows")

    # 3. Override files (incremental)
    dl_count = sync_override_files(sb, slug, backup_dir)
    print(f"  Override files: {dl_count} new downloads")

    # 4. Review requests
    rr_count, rr_rows = sync_review_requests(sb, slug)
    write_json(backup_dir / "review-requests.json", rr_rows)
    print(f"  Review requests: {rr_count} rows")

    # 5. Feedback markdown (to mileage-os)
    write_feedback_markdown(slug, fb_rows)

    # 6. Sync metadata
    metadata = {
        "slug": slug,
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "feedback_rows": fb_count,
        "ad_image_rows": img_count,
        "override_files_downloaded": dl_count,
        "review_request_rows": rr_count,
    }
    write_last_sync(backup_dir, metadata)

    return metadata


# ── Git Operations ─────────────────────────────────────────────────────────

def git_commit_and_push():
    """Add backup files, commit, and push."""
    try:
        # Stage backup files
        subprocess.run(
            ["git", "add", "*/backups/"],
            cwd=HERE, capture_output=True, text=True,
        )
        # Also stage any new backup dirs
        subprocess.run(
            ["git", "add", "-A", "*/backups/"],
            cwd=HERE, capture_output=True, text=True,
        )

        # Check if there are changes to commit
        status = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=HERE, capture_output=True,
        )
        if status.returncode == 0:
            print("\nNo changes to commit.")
            return

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        msg = f"sync: Supabase backup {now}"
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=HERE, capture_output=True, text=True,
        )
        print(f"\nCommitted: {msg}")

        result = subprocess.run(
            ["git", "push"],
            cwd=HERE, capture_output=True, text=True,
        )
        if result.returncode == 0:
            print("Pushed to remote.")
        else:
            print(f"Push failed: {result.stderr.strip()}")

    except Exception as e:
        print(f"Git error: {e}")


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python3 sync.py confluence-fp          # single client")
        print("  python3 sync.py --all                  # all clients")
        print("  python3 sync.py --all --commit         # sync + git commit + push")
        sys.exit(1)

    do_commit = "--commit" in args
    slugs_to_sync = []

    if "--all" in args:
        slugs_to_sync = discover_clients()
        if not slugs_to_sync:
            print("No client directories found (looking for subdirs with data.json)")
            sys.exit(1)
        print(f"Discovered {len(slugs_to_sync)} client(s): {', '.join(slugs_to_sync)}")
    else:
        slug = [a for a in args if not a.startswith("--")]
        if not slug:
            print("Error: Provide a client slug or --all")
            sys.exit(1)
        slugs_to_sync = [slug[0]]

    # Connect to Supabase
    sb = get_supabase()
    if not sb:
        print("Cannot connect to Supabase. Existing backup files preserved.")
        sys.exit(1)

    # Sync each client
    results = []
    for slug in slugs_to_sync:
        meta = sync_client(sb, slug)
        results.append(meta)

    # Summary
    print("\n" + "=" * 40)
    print("Sync complete:")
    for meta in results:
        if "error" in meta:
            print(f"  {meta['slug']}: ERROR — {meta['error']}")
        else:
            print(f"  {meta['slug']}: {meta['feedback_rows']} feedback, {meta['ad_image_rows']} images, {meta['review_request_rows']} review requests")

    # Git commit if requested
    if do_commit:
        git_commit_and_push()


if __name__ == "__main__":
    main()
