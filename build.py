#!/usr/bin/env python3
"""
Bake script: parses ad-copy-draft.md -> campaign folder with index.html + images.

Output structure:
  ad-preview/<client>/
    index.html      ← copy of template with campaign ID baked in
    data.json       ← parsed ad data
    images/         ← ad creative PNGs

Usage: python build.py confluence-fp
Shareable URL: bbishilany.github.io/ad-preview/confluence-fp/
"""

import json
import shutil
import sys
from pathlib import Path

# Paths
MILEAGE_OS = Path.home() / "Projects" / "mileage-os"
WORKBENCH = Path.home() / "Projects" / "mileage" / "workbench"
HERE = Path(__file__).parent

# Add workbench/preview to sys.path so we can import the parser
sys.path.insert(0, str(WORKBENCH / "preview"))
from parser import parse_ad_copy_file  # noqa: E402


def find_draft(client: str) -> Path:
    """Locate the ad copy draft .md file for a client."""
    copy_dir = MILEAGE_OS / "clients" / client / "copy"
    candidates = sorted(copy_dir.glob(f"*ad-copy-draft*.md"))
    if not candidates:
        raise FileNotFoundError(f"No ad copy draft found in {copy_dir}")
    return candidates[0]


def find_images(client: str) -> list[Path]:
    """Find all ad creative PNGs for a client."""
    img_dir = MILEAGE_OS / "clients" / client / "assets" / "meta-ads"
    if not img_dir.exists():
        return []
    return sorted(img_dir.glob("*.png"))


def assign_images(data: dict, images: list[Path]) -> None:
    """Assign image filenames to ads based on naming convention (ad1-*, ad2-*, etc.)."""
    img_map: dict[int, list[str]] = {}
    for img in images:
        name = img.name
        for ad in data["ads"]:
            prefix = f"ad{ad['num']}-"
            if name.startswith(prefix):
                img_map.setdefault(ad["num"], []).append(name)
                break

    for ad in data["ads"]:
        ad["images"] = sorted(img_map.get(ad["num"], []))


def build(client: str) -> None:
    """Run the full build for a client campaign folder."""
    print(f"Building ad preview for: {client}")

    # Campaign output directory
    campaign_dir = HERE / client
    campaign_dir.mkdir(parents=True, exist_ok=True)

    # 1. Parse the draft
    draft_path = find_draft(client)
    print(f"  Parsing: {draft_path.name}")
    data = parse_ad_copy_file(draft_path)
    data["client"] = client

    # 2. Copy images into campaign folder
    images = find_images(client)
    img_dest = campaign_dir / "images"
    img_dest.mkdir(parents=True, exist_ok=True)

    for img in images:
        dest = img_dest / img.name
        shutil.copy2(img, dest)
        print(f"  Copied: {img.name}")

    # 3. Assign images to ads
    assign_images(data, images)

    # 4. Write data.json
    json_dest = campaign_dir / "data.json"
    json_dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Written: {client}/data.json")

    # 5. Copy template index.html, bake in the campaign ID
    template = HERE / "template.html"
    if not template.exists():
        print(f"  ERROR: template.html not found at {template}")
        sys.exit(1)

    html = template.read_text(encoding="utf-8")
    html = html.replace("__CAMPAIGN_ID__", client)
    (campaign_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"  Written: {client}/index.html")

    # Summary
    ad_count = len(data["ads"])
    img_count = len(images)
    print(f"\nDone: {ad_count} ads, {img_count} images")
    print(f"URL: bbishilany.github.io/ad-preview/{client}/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build.py <client-slug>")
        print("Example: python build.py confluence-fp")
        sys.exit(1)

    build(sys.argv[1])
