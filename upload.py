#!/usr/bin/env python3
"""
Upload ad creative images to Supabase Storage + ad_images table.

Reads files from a source directory, matches them to ads by filename pattern,
uploads to Supabase Storage, and inserts rows into the ad_images table.

Filename patterns supported:
  "Ad 1 - Feed.jpg"            → ad_num=1, slot=feed
  "Ad 1 - Feed_v1.jpg"         → ad_num=1, slot=feed  (version 1)
  "Ad 1 - Feed_v2.jpg"         → ad_num=1, slot=feed  (version 2)
  "Ad 3 - Stories.jpg"         → ad_num=3, slot=story
  "Ad 4 - Stories_v1.jpg"      → ad_num=4, slot=story (version 1)

The last version per (ad, slot) is marked is_active=true.
All previous versions are inserted as is_active=false.

Usage:
    python3 upload.py <campaign-id> <source-dir>
    python3 upload.py confluence-fp-naples "~/Dropbox/Safari Downloads/output (17)/"

Requires: 1Password CLI (op) for Supabase service key resolution.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────

SUPABASE_URL = "https://byuxmsohwsvnqfirgeit.supabase.co"
BUCKET = "ad-creatives"


def get_service_key() -> str:
    """Resolve Supabase service role key from 1Password."""
    try:
        result = subprocess.run(
            ["op", "read", "op://Mileage/Supabase - Ad Preview Feedback/credential"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        print("Error: 1Password CLI (op) not installed. Run: brew install --cask 1password-cli")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: Could not read Supabase key from 1Password: {e.stderr}")
        sys.exit(1)


# ── File Parsing ──────────────────────────────────────────────────────────

# Pattern: "Ad 1 - Feed_v2.jpg" or "Ad 1 - Feed.jpg"
FILE_PATTERN = re.compile(
    r"^Ad\s+(\d+)\s*-\s*(Feed|Stories|Story|Reel)(?:_v(\d+))?\.(jpg|jpeg|png|webp)$",
    re.IGNORECASE,
)

SLOT_MAP = {
    "feed": "feed",
    "stories": "story",
    "story": "story",
    "reel": "reel",
}


def parse_filename(name: str) -> dict | None:
    """Parse an ad image filename into structured metadata."""
    m = FILE_PATTERN.match(name)
    if not m:
        return None
    ad_num = int(m.group(1))
    slot = SLOT_MAP.get(m.group(2).lower(), m.group(2).lower())
    version = int(m.group(3)) if m.group(3) else 1
    ext = m.group(4).lower()
    return {"ad_num": ad_num, "slot": slot, "version": version, "ext": ext}


def scan_source_dir(src: Path) -> list[dict]:
    """Scan a directory and return parsed upload entries sorted by (ad, slot, version)."""
    entries = []
    for f in sorted(src.iterdir()):
        if not f.is_file():
            continue
        parsed = parse_filename(f.name)
        if not parsed:
            continue
        parsed["path"] = f
        parsed["filename"] = f.name
        entries.append(parsed)

    # Sort by ad_num, slot, version
    entries.sort(key=lambda e: (e["ad_num"], e["slot"], e["version"]))
    return entries


# ── Supabase Operations ──────────────────────────────────────────────────

def upload_to_storage(service_key: str, storage_path: str, file_bytes: bytes, content_type: str) -> str:
    """Upload a file to Supabase Storage, return public URL."""
    import urllib.request

    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}"
    req = urllib.request.Request(url, data=file_bytes, method="POST")
    req.add_header("apikey", service_key)
    req.add_header("Authorization", f"Bearer {service_key}")
    req.add_header("Content-Type", content_type)
    req.add_header("x-upsert", "true")

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status not in (200, 201):
                raise Exception(f"Storage upload returned {resp.status}")
    except Exception as e:
        raise Exception(f"Storage upload failed: {e}")

    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_path}"


def insert_ad_image(service_key: str, row: dict) -> dict:
    """Insert a row into ad_images via PostgREST."""
    import urllib.request

    url = f"{SUPABASE_URL}/rest/v1/ad_images"
    body = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("apikey", service_key)
    req.add_header("Authorization", f"Bearer {service_key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=representation")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise Exception(f"Insert failed: {e}")


def deactivate_slot(service_key: str, campaign_id: str, ad_num: int, slot: str):
    """Deactivate all active images for a slot."""
    import urllib.request

    url = (
        f"{SUPABASE_URL}/rest/v1/ad_images"
        f"?campaign_id=eq.{campaign_id}&ad_num=eq.{ad_num}&slot=eq.{slot}&is_active=eq.true"
    )
    body = json.dumps({"is_active": False}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH")
    req.add_header("apikey", service_key)
    req.add_header("Authorization", f"Bearer {service_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req):
            pass
    except Exception:
        pass  # Non-critical if nothing to deactivate


# ── Content Type ──────────────────────────────────────────────────────────

CONTENT_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 upload.py <campaign-id> <source-dir>")
        print("       python3 upload.py confluence-fp-naples ~/Dropbox/...")
        sys.exit(1)

    campaign_id = sys.argv[1]
    src = Path(sys.argv[2]).expanduser().resolve()

    if not src.exists() or not src.is_dir():
        print(f"Error: source directory not found: {src}")
        sys.exit(1)

    entries = scan_source_dir(src)
    if not entries:
        print(f"No matching ad image files found in: {src}")
        print("Expected pattern: 'Ad N - Feed.jpg', 'Ad N - Stories_v2.png', etc.")
        sys.exit(1)

    print(f"Campaign: {campaign_id}")
    print(f"Source:   {src}")
    print(f"Found:    {len(entries)} images\n")

    service_key = get_service_key()

    # Determine which entry is the last per (ad, slot) — that one gets is_active=true
    last_index = {}
    for i, e in enumerate(entries):
        last_index[f"{e['ad_num']}_{e['slot']}"] = i

    for i, entry in enumerate(entries):
        key = f"{entry['ad_num']}_{entry['slot']}"
        is_last = (last_index[key] == i)
        tag = " (active)" if is_last else ""

        print(f"[Ad {entry['ad_num']}] {entry['slot']} v{entry['version']}{tag} — {entry['filename']}")

        try:
            file_bytes = entry["path"].read_bytes()
            ts = int(datetime.now(timezone.utc).timestamp() * 1000)
            storage_path = f"{campaign_id}/ad{entry['ad_num']}_{entry['slot']}_v{entry['version']}_{ts}.{entry['ext']}"
            content_type = CONTENT_TYPES.get(entry["ext"], "image/jpeg")

            public_url = upload_to_storage(service_key, storage_path, file_bytes, content_type)
            print(f"  stored: {storage_path}")

            # Deactivate previous active images before setting the last one active
            if is_last:
                deactivate_slot(service_key, campaign_id, entry["ad_num"], entry["slot"])

            row = {
                "campaign_id": campaign_id,
                "ad_num": entry["ad_num"],
                "slot": entry["slot"],
                "filename": "",
                "storage_path": storage_path,
                "public_url": public_url,
                "uploaded_by": "mileage",
                "is_active": is_last,
            }
            inserted = insert_ad_image(service_key, row)
            row_id = inserted[0]["id"] if inserted else "?"
            print(f"  inserted: id={row_id}, active={is_last}")

        except Exception as e:
            print(f"  FAILED: {e}")

    print("\nDone.")


if __name__ == "__main__":
    main()
