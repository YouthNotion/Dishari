"""Generate the link-preview image shown when the site is shared (WhatsApp, Messenger,
Facebook, LinkedIn, X, ...): static/img/social-preview.png, 1200x630 (1.91:1).

The image is committed, so this only needs re-running when the logo or wording changes:

    pip install pillow
    python tools/make_social_image.py

Fonts default to Open Sans (SIL Open Font License) at the usual Linux path. Pass
--bold/--semibold/--regular to use other font files.
"""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "static/img/logo.png"
OUT = ROOT / "static/img/social-preview.png"
FONTS = Path("/usr/share/fonts/open-sans")

W, H = 1200, 630
BRAND = (7, 138, 53)  # --brand
BRAND_DARK = (6, 108, 45)  # --brand-hover
INK = (23, 35, 27)
MUTED = (76, 90, 80)
TINT = (242, 250, 244)

TITLE = "Dishari"
TAGLINE = "Dream of New Earth"
BODY = (
    "Shelter, care, education and skills training for children and women in Noakhali, Bangladesh."
)
FOOTER = "Since 2001  ·  dishari.orgs.bd"


def wrap(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int
) -> list[str]:
    """Greedy word wrap so each line fits within ``width`` pixels."""
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bold", default=FONTS / "OpenSans-Bold.ttf", type=Path)
    parser.add_argument("--semibold", default=FONTS / "OpenSans-Semibold.ttf", type=Path)
    parser.add_argument("--regular", default=FONTS / "OpenSans-Regular.ttf", type=Path)
    args = parser.parse_args()

    # Opaque background: many messengers render transparency as black.
    img = Image.new("RGB", (W, H), "white")
    px = img.load()
    for y in range(H):  # vertical tint -> white, like the hero
        t = y / (H - 1)
        row = tuple(round(TINT[i] + (255 - TINT[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = row
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((W - 520, -360, W + 360, 300), fill=40)
    img.paste(Image.new("RGB", (W, H), BRAND), (0, 0), glow.filter(ImageFilter.GaussianBlur(90)))

    draw = ImageDraw.Draw(img)

    # Logo on the left, vertically centred above the bottom bar.
    logo = Image.open(LOGO).convert("RGBA")
    logo_h = 450
    logo = logo.resize((round(logo.width * logo_h / logo.height), logo_h), Image.LANCZOS)
    img.paste(logo, (90, (H - 14 - logo_h) // 2), logo)

    # Text column on the right.
    x = 90 + logo.width + 70
    col_w = W - x - 80
    title_f = ImageFont.truetype(str(args.bold), 118)
    tag_f = ImageFont.truetype(str(args.semibold), 40)
    body_f = ImageFont.truetype(str(args.regular), 33)
    foot_f = ImageFont.truetype(str(args.semibold), 29)

    y = 118
    draw.text((x, y), TITLE, font=title_f, fill=BRAND)
    y += 150
    draw.text((x, y), TAGLINE, font=tag_f, fill=MUTED)
    y += 66
    draw.rectangle((x, y, x + 72, y + 5), fill=BRAND)
    y += 30
    for line in wrap(draw, BODY, body_f, col_w):
        draw.text((x, y), line, font=body_f, fill=INK)
        y += 47
    draw.text((x, H - 14 - 78), FOOTER, font=foot_f, fill=BRAND_DARK)

    draw.rectangle((0, H - 14, W, H), fill=BRAND)  # brand bar along the bottom

    img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    img.save(OUT, optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)} ({W}x{H}, {OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
