#!/usr/bin/env python3
"""Generate 'Image Forthcoming' placeholders for Confluence FP ads.
Branded, creative placeholders that look intentional, not broken."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os
import random

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'confluence-fp', 'images')

# Confluence brand palette
NAVY = (11, 26, 46)
NAVY_MID = (16, 36, 62)
NAVY_LIGHT = (21, 45, 75)
GOLD = (201, 168, 76)
GOLD_DIM = (161, 134, 61)
GOLD_BRIGHT = (221, 192, 106)
WHITE = (232, 234, 246)
WHITE_DIM = (139, 146, 184)
SLATE = (34, 38, 58)
SLATE_LIGHT = (44, 50, 72)


def load_font(size):
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def draw_radial_gradient(img, cx, cy, radius, center_color, edge_color):
    """Soft radial glow behind the main content area."""
    pixels = img.load()
    w, h = img.size
    for y in range(max(0, cy - radius), min(h, cy + radius)):
        for x in range(max(0, cx - radius), min(w, cx + radius)):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            if dist > radius:
                continue
            t = dist / radius
            t = t * t  # ease-out for softer falloff
            r = int(center_color[0] * (1 - t) + edge_color[0] * t)
            g = int(center_color[1] * (1 - t) + edge_color[1] * t)
            b = int(center_color[2] * (1 - t) + edge_color[2] * t)
            pixels[x, y] = (r, g, b)


def draw_constellation(draw, width, height, scale, seed=42):
    """Scattered dots connected by faint lines — like a constellation map.
    Feels like data points being connected. On brand for a financial firm."""
    rng = random.Random(seed)
    points = []
    margin = int(60 * scale)
    for _ in range(18):
        px = rng.randint(margin, width - margin)
        py = rng.randint(margin, height - margin)
        points.append((px, py))

    # Draw connecting lines between nearby points
    for i, p1 in enumerate(points):
        for j, p2 in enumerate(points):
            if i >= j:
                continue
            dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
            max_dist = min(width, height) * 0.3
            if dist < max_dist:
                alpha = int(30 * (1 - dist / max_dist))
                line_color = (GOLD[0], GOLD[1], GOLD[2], alpha)
                # Can't do alpha lines easily in RGB, so use dim gold
                dim = tuple(int(c * 0.15) + int(NAVY[i] * 0.85) for i, c in enumerate(GOLD))
                draw.line([p1, p2], fill=dim, width=1)

    # Draw dots at each point
    for px, py in points:
        r = int(rng.uniform(2, 5) * scale)
        dot_color = GOLD_DIM if rng.random() > 0.4 else SLATE_LIGHT
        draw.ellipse([px - r, py - r, px + r, py + r], fill=dot_color)

    # A few brighter "star" nodes
    for px, py in rng.sample(points, min(4, len(points))):
        r = int(3 * scale)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=GOLD_BRIGHT)


def draw_golden_rings(draw, cx, cy, scale):
    """Concentric rings radiating outward — elegant, financial, confident."""
    for i, radius in enumerate([60, 100, 150]):
        r = int(radius * scale)
        alpha_factor = 1 - (i * 0.3)
        w = max(1, int(2 * scale * alpha_factor))
        color = tuple(int(c * alpha_factor + NAVY[j] * (1 - alpha_factor)) for j, c in enumerate(GOLD))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)


def draw_diagonal_accent(draw, width, height, scale):
    """A single bold diagonal gold line cutting across the composition."""
    line_w = max(2, int(3 * scale))
    # Top-right to mid-left diagonal
    x1 = int(width * 0.75)
    y1 = 0
    x2 = int(width * 0.25)
    y2 = height
    dim_gold = tuple(int(c * 0.2) + int(NAVY[i] * 0.8) for i, c in enumerate(GOLD))
    draw.line([(x1, y1), (x2, y2)], fill=dim_gold, width=line_w)


def generate_placeholder(width, height, ad_num, title, filename):
    """Generate a creative, branded placeholder image."""
    img = Image.new('RGB', (width, height), NAVY)
    draw = ImageDraw.Draw(img)

    scale = min(width, height) / 1080
    cx, cy = width // 2, height // 2

    # Layer 1: Subtle radial glow behind center content
    glow_radius = int(min(width, height) * 0.45)
    draw_radial_gradient(img, cx, int(cy * 0.85), glow_radius, NAVY_MID, NAVY)
    draw = ImageDraw.Draw(img)  # refresh draw after pixel manipulation

    # Layer 2: Constellation pattern (full background)
    draw_constellation(draw, width, height, scale, seed=ad_num * 7)

    # Layer 3: Diagonal accent line
    draw_diagonal_accent(draw, width, height, scale)

    # Layer 4: Golden rings behind the text
    ring_cy = int(height * 0.42)
    draw_golden_rings(draw, cx, ring_cy, scale * 1.2)

    # Layer 5: Text block
    font_main = load_font(int(48 * scale))
    font_sub = load_font(int(24 * scale))
    font_badge = load_font(int(20 * scale))
    font_tiny = load_font(int(14 * scale))

    # Main text: "IMAGE FORTHCOMING"
    text_main = "IMAGE FORTHCOMING"
    bbox = draw.textbbox((0, 0), text_main, font=font_main)
    tw = bbox[2] - bbox[0]
    text_y = int(height * 0.52)
    draw.text(((width - tw) // 2, text_y), text_main, fill=WHITE, font=font_main)

    # Gold rule below
    rule_y = text_y + int(62 * scale)
    rule_w = int(180 * scale)
    draw.line(
        [(cx - rule_w // 2, rule_y), (cx + rule_w // 2, rule_y)],
        fill=GOLD, width=max(2, int(3 * scale))
    )

    # Subtitle: ad title
    sub_y = rule_y + int(20 * scale)
    bbox2 = draw.textbbox((0, 0), title, font=font_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((width - tw2) // 2, sub_y), title, fill=WHITE_DIM, font=font_sub)

    # Ad number pill badge
    ad_label = f"Ad {ad_num}"
    bbox3 = draw.textbbox((0, 0), ad_label, font=font_badge)
    tw3 = bbox3[2] - bbox3[0]
    th3 = bbox3[3] - bbox3[1]
    badge_y = sub_y + int(44 * scale)
    pad_x, pad_y = int(16 * scale), int(8 * scale)
    draw.rounded_rectangle(
        [(cx - tw3 // 2 - pad_x, badge_y - pad_y),
         (cx + tw3 // 2 + pad_x, badge_y + th3 + pad_y)],
        radius=int(14 * scale), fill=SLATE, outline=GOLD, width=max(1, int(2 * scale))
    )
    draw.text(((width - tw3) // 2, badge_y), ad_label, fill=GOLD, font=font_badge)

    # Bottom watermark
    wm = "CONFLUENCE FINANCIAL PARTNERS"
    bbox4 = draw.textbbox((0, 0), wm, font=font_tiny)
    tw4 = bbox4[2] - bbox4[0]
    wm_y = height - int(40 * scale)
    wm_color = tuple(int(c * 0.35) + int(NAVY[i] * 0.65) for i, c in enumerate(WHITE))
    draw.text(((width - tw4) // 2, wm_y), wm, fill=wm_color, font=font_tiny)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path, 'PNG')
    print(f"  Generated: {filename} ({width}x{height})")
    return path


if __name__ == '__main__':
    print("Generating image placeholders...")

    # Ad 3 — Personal invite (feed, 1080x1080)
    generate_placeholder(1080, 1080, 3, "Personal Invite", "ad3-personal-invite.png")

    # Ad 5 — Local connection (stories/reels, 1080x1920)
    generate_placeholder(1080, 1920, 5, "Local Connection", "ad5-local-connection-story.png")

    # Ad 7 — Expert insight (feed 1080x1080 + story 1080x1920)
    generate_placeholder(1080, 1080, 7, "Expert Insight", "ad7-expert-insight.png")
    generate_placeholder(1080, 1920, 7, "Expert Insight", "ad7-expert-insight-story.png")

    # Ad 9 — Final reminder (stories/reels, 1080x1920)
    generate_placeholder(1080, 1920, 9, "Final Reminder", "ad9-final-reminder-story.png")

    print("Done!")
