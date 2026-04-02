#!/usr/bin/env python3
"""
Bake script: parses ad-copy-draft.md -> campaign folder with index.html + images.

Output structure:
  ad-preview/<client>/
    index.html      <- copy of template with campaign ID baked in
    data.json       <- parsed ad data
    images/         <- ad creative PNGs

Usage:
    python build.py confluence-fp           # full build for one client
    python build.py --rebuild-all           # re-bake all clients from template
Shareable URL: bbishilany.github.io/ad-preview/confluence-fp/
"""

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Paths
MILEAGE_OS = Path.home() / "Projects" / "mileage-os"
WORKBENCH = Path.home() / "Projects" / "mileage" / "workbench"
HERE = Path(__file__).parent

# Add workbench/preview to sys.path so we can import the parser
sys.path.insert(0, str(WORKBENCH / "preview"))
from parser import parse_ad_copy_file  # noqa: E402


# ── Client Discovery ───────────────────────────────────────────────────────

def discover_clients() -> list[str]:
    """Scan subdirectories for client campaigns (those with data.json)."""
    clients = []
    for subdir in sorted(HERE.iterdir()):
        if subdir.is_dir() and (subdir / "data.json").exists():
            clients.append(subdir.name)
    return clients


# ── Helpers ────────────────────────────────────────────────────────────────

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
    """Assign image filenames to ads based on naming convention (ad1-*, ad2-*, etc.).

    Detects variation pattern: ad{N}-v{M}-{format}.png
    Groups into a 'variations' array when multiple variations exist.
    """
    import re

    img_map: dict[int, list[str]] = {}
    for img in images:
        name = img.name
        for ad in data["ads"]:
            prefix = f"ad{ad['num']}-"
            if name.startswith(prefix):
                img_map.setdefault(ad["num"], []).append(name)
                break

    var_pattern = re.compile(r"-v(\d+)-")

    for ad in data["ads"]:
        all_imgs = sorted(img_map.get(ad["num"], []))
        ad["images"] = all_imgs

        # Detect variations: group images by -v{M}- pattern
        var_groups: dict[int, list[str]] = {}
        for name in all_imgs:
            m = var_pattern.search(name)
            if m:
                var_groups.setdefault(int(m.group(1)), []).append(name)

        if len(var_groups) >= 2:
            # Build variations array; preserve any manually-set labels in existing data
            existing_vars = {v["num"]: v for v in ad.get("variations", [])}
            variations = []
            for vnum in sorted(var_groups.keys()):
                existing = existing_vars.get(vnum, {})
                variations.append({
                    "num": vnum,
                    "label": existing.get("label", f"Variation {vnum}"),
                    "images": sorted(var_groups[vnum]),
                })
            ad["variations"] = variations
            # Backward compat: flat images list = first variation
            ad["images"] = variations[0]["images"]
        else:
            # No multi-variation pattern — remove stale variations if present
            ad.pop("variations", None)


def parse_creative_direction(client: str) -> dict[int, str]:
    """Parse image creative direction markdown, extract per-ad blocks."""
    copy_dir = MILEAGE_OS / "clients" / client / "copy"
    candidates = sorted(copy_dir.glob("*image-creative-direction*.md"))
    if not candidates:
        return {}

    text = candidates[0].read_text(encoding="utf-8")
    result: dict[int, str] = {}

    # Split by ### Ad N: headers
    import re
    blocks = re.split(r"(?=^### Ad \d+:)", text, flags=re.MULTILINE)
    for block in blocks:
        header = re.match(r"^### Ad (\d+):\s*(.+)", block)
        if not header:
            continue
        ad_num = int(header.group(1))
        content = block[header.end():].strip()
        end_marker = content.find("\n---")
        if end_marker > 0:
            content = content[:end_marker].strip()
        result[ad_num] = content

    return result


# ── Build ──────────────────────────────────────────────────────────────────

def build(client: str) -> None:
    """Run the full build for a client campaign folder."""
    print(f"Building ad preview for: {client}")

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

    # 4. Attach creative direction per ad
    creative = parse_creative_direction(client)
    for ad in data["ads"]:
        ad["image_direction"] = creative.get(ad["num"], "")
    if creative:
        print(f"  Attached creative direction for {len(creative)} ads")

    # 5. Write data.json (with overwrite protection)
    json_dest = campaign_dir / "data.json"
    if json_dest.exists() and "--force" not in sys.argv:
        print(f"\n  ⚠️  WARNING: {client}/data.json already exists.")
        print(f"  A full build re-parses from markdown and OVERWRITES data.json.")
        print(f"  If compliance edits were made directly to data.json, they will be LOST.")
        print(f"  Use --force to overwrite, or --images-only to just update images.")
        confirm = input("  Type 'overwrite' to proceed: ")
        if confirm.strip().lower() != "overwrite":
            print("  Aborted. data.json was NOT overwritten.")
            print("  Tip: use --images-only to copy images without touching data.json.")
            return
    json_dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Written: {client}/data.json")

    # 6. Copy template index.html, bake in the campaign ID
    rebake(client)

    # 7. Rebuild root index.html
    rebuild_index()

    # Summary
    ad_count = len(data["ads"])
    img_count = len(images)
    print(f"\nDone: {ad_count} ads, {img_count} images")
    print(f"URL: bbishilany.github.io/ad-preview/{client}/")


# ── Images Only ───────────────────────────────────────────────────────────

def images_only(client: str) -> None:
    """Copy images and update data.json image assignments WITHOUT re-parsing markdown copy."""
    print(f"Updating images for: {client} (copy untouched)")

    campaign_dir = HERE / client
    json_dest = campaign_dir / "data.json"
    if not json_dest.exists():
        print(f"  ERROR: {client}/data.json does not exist. Run a full build first.")
        sys.exit(1)

    # Load existing data.json (preserves compliance edits)
    data = json.loads(json_dest.read_text(encoding="utf-8"))

    # Copy images
    images = find_images(client)
    img_dest = campaign_dir / "images"
    img_dest.mkdir(parents=True, exist_ok=True)
    for img in images:
        dest = img_dest / img.name
        shutil.copy2(img, dest)
        print(f"  Copied: {img.name}")

    # Re-assign images to ads (updates image arrays + variations)
    assign_images(data, images)

    # Write updated data.json (only image fields changed)
    json_dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Updated image assignments in: {client}/data.json")

    # Rebake template + root index
    rebake(client)
    rebuild_index()

    print(f"\nDone: {len(images)} images updated. Copy was NOT touched.")
    print(f"URL: bbishilany.github.io/ad-preview/{client}/")


# ── Rebake ─────────────────────────────────────────────────────────────────

def rebake(client: str) -> None:
    """Re-bake template.html -> client index.html without re-parsing markdown."""
    template = HERE / "template.html"
    if not template.exists():
        print(f"  ERROR: template.html not found at {template}")
        sys.exit(1)

    campaign_dir = HERE / client
    if not campaign_dir.exists():
        print(f"  ERROR: {client}/ directory does not exist")
        return

    html = template.read_text(encoding="utf-8")
    html = html.replace("__CAMPAIGN_ID__", client)
    (campaign_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"  Baked: {client}/index.html")


# ── Root Index ─────────────────────────────────────────────────────────────

def rebuild_index() -> None:
    """Generate root index.html listing all campaigns."""
    clients = discover_clients()
    if not clients:
        print("  No clients found for index.html")
        return

    # Gather metadata from each client's data.json
    entries = []
    for slug in clients:
        data_path = HERE / slug / "data.json"
        try:
            data = json.loads(data_path.read_text(encoding="utf-8"))
            campaign_name = data.get("campaign", slug)
            ad_count = len(data.get("ads", []))
            event_date = data.get("event_date", "")
            entries.append({
                "slug": slug,
                "name": campaign_name,
                "ads": ad_count,
                "event_date": event_date,
            })
        except Exception:
            entries.append({"slug": slug, "name": slug, "ads": 0, "event_date": ""})

    # Build HTML
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    links_html = ""
    for e in entries:
        sub_parts = []
        if e["ads"]:
            sub_parts.append(f"{e['ads']} ads")
        if e["event_date"]:
            sub_parts.append(e["event_date"])
        sub = " — ".join(sub_parts) if sub_parts else ""
        links_html += f'  <a href="{e["slug"]}/">\n'
        links_html += f'    {e["name"]}\n'
        if sub:
            links_html += f'    <span class="sub">{sub}</span>\n'
        links_html += f'  </a>\n'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ad Preview — Mileage Design</title>
<style>
  body {{
    font-family: Arial, Helvetica, sans-serif;
    background: #0f1117;
    color: #e8eaf6;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    margin: 0;
  }}
  h1 {{
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, #4f7aff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }}
  p {{ color: #8b92b8; font-size: 14px; margin-bottom: 32px; }}
  a {{
    display: block;
    padding: 14px 28px;
    background: #1a1d27;
    border: 1px solid #2e3350;
    border-radius: 10px;
    color: #e8eaf6;
    text-decoration: none;
    font-size: 15px;
    font-weight: 600;
    transition: all 0.15s;
    margin-bottom: 10px;
  }}
  a:hover {{ border-color: #4f7aff; background: rgba(79,122,255,0.1); }}
  .sub {{ font-size: 12px; color: #8b92b8; font-weight: 400; display: block; margin-top: 4px; }}
  .footer {{ color: #5c6280; font-size: 11px; margin-top: 32px; }}
</style>
</head>
<body>
  <h1>Mileage Design — Ad Preview</h1>
  <p>Select a campaign to review:</p>
{links_html}  <div class="footer">Last built: {now}</div>
</body>
</html>
"""

    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"  Built root index.html ({len(entries)} campaigns)")


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python build.py <client-slug>              # full build (overwrites data.json)")
        print("  python build.py --images-only <client>      # update images only (safe)")
        print("  python build.py --rebuild-all               # re-bake all from template")
        sys.exit(1)

    if sys.argv[1] == "--rebuild-all":
        clients = discover_clients()
        if not clients:
            print("No client directories found (looking for subdirs with data.json)")
            sys.exit(1)
        print(f"Rebuilding {len(clients)} client(s): {', '.join(clients)}")
        for client in clients:
            rebake(client)
        rebuild_index()
        print("\nDone.")
    elif sys.argv[1] == "--images-only":
        if len(sys.argv) < 3:
            print("Usage: python build.py --images-only <client-slug>")
            sys.exit(1)
        images_only(sys.argv[2])
    else:
        build(sys.argv[1])
