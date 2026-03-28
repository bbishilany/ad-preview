#!/usr/bin/env python3
"""Generate 'Video in Production' clapperboard placeholders for Confluence FP ads."""

from PIL import Image, ImageDraw, ImageFont
import math
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'confluence-fp', 'images')

# Brand colors
NAVY = (11, 26, 46)         # #0b1a2e
NAVY_LIGHT = (21, 45, 75)   # #152d4b
GOLD = (201, 168, 76)       # #c9a84c
WHITE = (232, 234, 246)     # #e8eaf6
WHITE_DIM = (139, 146, 184) # #8b92b8
SLATE = (34, 38, 58)        # #22263a

def load_font(size):
    """Try system fonts, fall back to default."""
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


def draw_clapper(draw, cx, cy, scale, color_top, color_bottom):
    """Draw a simplified movie clapperboard centered at (cx, cy)."""
    w = int(260 * scale)
    h_top = int(60 * scale)
    h_bot = int(160 * scale)
    stripe_w = int(32 * scale)

    x0 = cx - w // 2
    y_top = cy - (h_top + h_bot) // 2

    # Top clapper bar (angled stripes)
    draw.rounded_rectangle(
        [x0, y_top, x0 + w, y_top + h_top],
        radius=int(8 * scale), fill=color_top
    )
    # Diagonal stripes on top bar
    for i in range(0, w + h_top, stripe_w * 2):
        pts = [
            (x0 + i, y_top),
            (x0 + i + stripe_w, y_top),
            (x0 + i + stripe_w - h_top, y_top + h_top),
            (x0 + i - h_top, y_top + h_top),
        ]
        # Clip to bar bounds
        draw.polygon(pts, fill=color_bottom)

    # Bottom board
    draw.rounded_rectangle(
        [x0, y_top + h_top - int(4 * scale), x0 + w, y_top + h_top + h_bot],
        radius=int(8 * scale), fill=color_bottom
    )

    # Lines on board (like a slate)
    line_y_start = y_top + h_top + int(24 * scale)
    for i in range(4):
        ly = line_y_start + i * int(32 * scale)
        draw.line(
            [(x0 + int(20 * scale), ly), (x0 + w - int(20 * scale), ly)],
            fill=(*GOLD, 80), width=max(1, int(2 * scale))
        )

    # Circle "lens" dot
    dot_r = int(12 * scale)
    dot_cx = x0 + w - int(36 * scale)
    dot_cy = y_top + h_top + int(30 * scale)
    draw.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=GOLD
    )


def generate_placeholder(width, height, ad_num, title, filename):
    """Generate a single placeholder image."""
    img = Image.new('RGB', (width, height), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle diagonal line texture
    for i in range(-height, width + height, 40):
        draw.line([(i, 0), (i + height, height)], fill=NAVY_LIGHT, width=1)

    # Clapperboard
    scale = min(width, height) / 1080
    clapper_y = int(height * 0.38)
    draw_clapper(draw, width // 2, clapper_y, scale * 1.4, GOLD, SLATE)

    # "VIDEO IN PRODUCTION" text
    font_big = load_font(int(52 * scale))
    font_mid = load_font(int(28 * scale))
    font_sm = load_font(int(22 * scale))

    text_main = "VIDEO IN PRODUCTION"
    bbox = draw.textbbox((0, 0), text_main, font=font_big)
    tw = bbox[2] - bbox[0]
    text_y = int(height * 0.58)
    draw.text(((width - tw) // 2, text_y), text_main, fill=WHITE, font=font_big)

    # Gold accent line
    line_y = text_y + int(70 * scale)
    line_w = int(200 * scale)
    draw.line(
        [(width // 2 - line_w // 2, line_y), (width // 2 + line_w // 2, line_y)],
        fill=GOLD, width=max(2, int(3 * scale))
    )

    # Ad title
    title_y = line_y + int(24 * scale)
    bbox2 = draw.textbbox((0, 0), title, font=font_mid)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((width - tw2) // 2, title_y), title, fill=WHITE_DIM, font=font_mid)

    # Ad number badge
    ad_label = f"Ad {ad_num}"
    bbox3 = draw.textbbox((0, 0), ad_label, font=font_sm)
    tw3 = bbox3[2] - bbox3[0]
    th3 = bbox3[3] - bbox3[1]
    badge_y = title_y + int(50 * scale)
    pad_x, pad_y = int(16 * scale), int(8 * scale)
    draw.rounded_rectangle(
        [(width // 2 - tw3 // 2 - pad_x, badge_y - pad_y),
         (width // 2 + tw3 // 2 + pad_x, badge_y + th3 + pad_y)],
        radius=int(12 * scale), fill=NAVY_LIGHT, outline=GOLD, width=max(1, int(2 * scale))
    )
    draw.text(((width - tw3) // 2, badge_y), ad_label, fill=GOLD, font=font_sm)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    img.save(path, 'PNG')
    print(f"  Generated: {filename} ({width}x{height})")
    return path


if __name__ == '__main__':
    print("Generating video placeholder images...")

    # Ad 3 — Personal invite video (feed, 1080x1080)
    generate_placeholder(1080, 1080, 3, "Personal Invite Video", "ad3-personal-invite.png")

    # Ad 5 — Local connection video (stories/reels, 1080x1920)
    generate_placeholder(1080, 1920, 5, "Local Connection Video", "ad5-local-connection-story.png")

    # Ad 7 — Expert insight video (feed 1080x1080 + story 1080x1920)
    generate_placeholder(1080, 1080, 7, "Expert Insight Video", "ad7-expert-insight.png")
    generate_placeholder(1080, 1920, 7, "Expert Insight Video", "ad7-expert-insight-story.png")

    # Ad 9 — Final reminder video (stories/reels, 1080x1920)
    generate_placeholder(1080, 1920, 9, "Final Reminder Video", "ad9-final-reminder-story.png")

    print("Done!")
