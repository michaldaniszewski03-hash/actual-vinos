#!/usr/bin/env python3
"""Render every raster asset vinOS ships from the palette and the mark geometry.

    python3 tools/render_branding.py

Requires Pillow. Outputs are committed so the ISO build never needs this.
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "branding"))
import palette as P  # noqa: E402

FONTS = ROOT / "branding" / "fonts"
SERIF = FONTS / "InstrumentSerif-Regular.ttf"
SERIF_ITALIC = FONTS / "InstrumentSerif-Italic.ttf"
MONO = FONTS / "JetBrainsMono-Regular.ttf"

GRUB = ROOT / "grub" / "themes" / "vinos"
CALAMARES = ROOT / "calamares" / "branding" / "vinos"
SYSLINUX = ROOT / "archiso" / "syslinux"
LOGO = ROOT / "branding" / "logo"

SS = 4  # supersampling factor for anti-aliased polygons

# The mark: a V drawn like a broad-nib letter. Heavy left stroke, hairline
# right stroke, both meeting on a flat foot. Unit box is 100 x 100.
THICK = [(4, 0), (34, 0), (60, 100), (42, 100)]
THIN = [(84, 0), (96, 0), (60, 100), (53, 100)]


def rgba(hex_, a=255):
    h = hex_.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def mark(size, thick=P.PAPER, thin=P.ACCENT_HI):
    """Square RGBA image of the mark, `size` px on each side."""
    big = size * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = big / 100
    d.polygon([(x * s, y * s) for x, y in THICK], fill=rgba(thick))
    d.polygon([(x * s, y * s) for x, y in THIN], fill=rgba(thin))
    return img.resize((size, size), Image.LANCZOS)


def mark_svg(thick, thin):
    pts = lambda poly: " ".join(f"{x},{y}" for x, y in poly)  # noqa: E731
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">\n'
        f'  <polygon points="{pts(THICK)}" fill="{thick}"/>\n'
        f'  <polygon points="{pts(THIN)}" fill="{thin}"/>\n'
        "</svg>\n"
    )


def lockup(height, fg=P.PAPER, thin=P.ACCENT_HI, os_color=P.MUTED):
    """Wordmark: the mark stands in for the 'v', then 'in' in Instrument Serif,
    then 'OS' in small mono caps. `height` is the serif point size in px."""
    serif = ImageFont.truetype(str(SERIF), height)
    mono = ImageFont.truetype(str(MONO), int(height * 0.2))
    x_height = -serif.getbbox("x", anchor="ls")[1]
    mark_h = int(x_height * 1.04)  # optical overshoot, like a real lowercase v

    in_w = serif.getlength("in")
    os_w = mono.getlength("OS")
    pad = int(height * 0.1)
    w = pad + mark_h + int(height * 0.02) + int(in_w) + int(height * 0.07) + int(os_w) + pad
    h = int(height * 1.3)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    baseline = int(h * 0.8)
    x = pad
    img.alpha_composite(mark(mark_h, fg, thin), (x, baseline - mark_h))
    x += mark_h + int(height * 0.02)
    d.text((x, baseline), "in", font=serif, fill=rgba(fg), anchor="ls")
    x += int(in_w) + int(height * 0.07)
    d.text((x, baseline), "OS", font=mono, fill=rgba(os_color), anchor="ls")
    return img.crop(img.getbbox())


def grain(img, amount=6, seed=7):
    """Low-amplitude monochrome noise so flat colour doesn't band on cheap panels."""
    rnd = random.Random(seed)
    w, h = img.size
    noise = Image.new("L", (w, h))
    noise.putdata([128 + rnd.randint(-amount, amount) for _ in range(w * h)])
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    # ImageChops.add(a, b, scale, offset) computes a + b - 128 per channel
    n3 = Image.merge("RGB", [noise] * 3)
    return ImageChops.add(img.convert("RGB"), n3, 1.0, -128)


def vignette(size, color, edge, strength=0.55):
    w, h = size
    base = Image.new("RGB", size, rgba(color)[:3])
    mask = Image.new("L", (w // 8, h // 8), 0)
    d = ImageDraw.Draw(mask)
    mw, mh = mask.size
    d.ellipse((-mw * 0.25, -mh * 0.35, mw * 1.25, mh * 1.35), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(mw / 6)).resize(size, Image.BILINEAR)
    dark = Image.new("RGB", size, rgba(edge)[:3])
    inv = Image.eval(mask, lambda v: int((255 - v) * strength))
    return Image.composite(dark, base, inv)


# ---------------------------------------------------------------- GRUB

def render_grub():
    GRUB.mkdir(parents=True, exist_ok=True)
    w, h = 1920, 1080
    bg = vignette((w, h), P.INK, "#0C0A09", 0.7)
    bg = grain(bg, amount=5)
    bg.save(GRUB / "background.png", optimize=True)

    lockup(150).save(GRUB / "logo.png", optimize=True)

    # Huge, barely-there mark bleeding off the right edge. Drawn as its own
    # image component so it never gets stretched with the background.
    ghost = mark(900, thick="#1E1916", thin="#2A1A1D")
    ghost.save(GRUB / "ghost.png", optimize=True)

    # Selected item: 9-slice "select_*.png". West edge is a 4px oxblood bar,
    # centre is the raised surface. Missing slices are allowed by GRUB.
    Image.new("RGBA", (4, 4), rgba(P.ACCENT)).save(GRUB / "select_w.png")
    Image.new("RGBA", (4, 4), rgba(P.INK_2)).save(GRUB / "select_c.png")

    # Thin scrollbar for long menus (e.g. many kernels)
    Image.new("RGBA", (2, 2), rgba(P.LINE_DARK)).save(GRUB / "scrollbar_frame_c.png")
    Image.new("RGBA", (2, 2), rgba(P.MUTED)).save(GRUB / "scrollbar_thumb_c.png")

    # Console (press c) and editor (press e) sit on plain ink
    Image.new("RGBA", (4, 4), rgba(P.INK)).save(GRUB / "terminal_box_c.png")

    # Hairline used under the logo
    Image.new("RGBA", (4, 1), rgba(P.LINE_DARK)).save(GRUB / "rule_c.png")


# ---------------------------------------------------------------- syslinux (BIOS live boot)

def render_syslinux():
    SYSLINUX.mkdir(parents=True, exist_ok=True)
    w, h = 640, 480
    img = vignette((w, h), P.INK, "#0C0A09", 0.6).convert("RGBA")
    lk = lockup(40)
    img.alpha_composite(lk, (48, 44))
    d = ImageDraw.Draw(img)
    d.line((48, 112, w - 48, 112), fill=rgba(P.LINE_DARK), width=1)
    img.convert("RGB").save(SYSLINUX / "splash.png", optimize=True)


# ---------------------------------------------------------------- Calamares

def render_calamares():
    CALAMARES.mkdir(parents=True, exist_ok=True)
    mark(256).save(CALAMARES / "logo.png", optimize=True)
    # Window/taskbar icon wants the mark on a solid tile so it reads on any panel
    icon = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    tile = Image.new("RGBA", (256 * SS, 256 * SS), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle((0, 0, 256 * SS - 1, 256 * SS - 1), 40 * SS, fill=rgba(P.INK))
    icon.alpha_composite(tile.resize((256, 256), Image.LANCZOS))
    icon.alpha_composite(mark(150), (53, 53))
    icon.save(CALAMARES / "icon.png", optimize=True)
    # Sidebar wordmark (sidebar is dark)
    lockup(112).save(CALAMARES / "sidebar-logo.png", optimize=True)
    # Combo box / spin box chevrons; QSS needs real images for these subcontrols
    for name, flip in (("chevron-down.png", False), ("chevron-up.png", True)):
        c = Image.new("RGBA", (12 * SS, 8 * SS), (0, 0, 0, 0))
        pts = [(1, 1.5), (6, 6.5), (11, 1.5)]
        if flip:
            pts = [(x, 8 - y) for x, y in pts]
        ImageDraw.Draw(c).line([(x * SS, y * SS) for x, y in pts], fill=rgba(P.SEPIA), width=int(1.6 * SS), joint="curve")
        c.resize((12, 8), Image.LANCZOS).save(CALAMARES / name)
    tick = Image.new("RGBA", (12 * SS, 12 * SS), (0, 0, 0, 0))
    ImageDraw.Draw(tick).line([(2 * SS, 6.5 * SS), (5 * SS, 9.5 * SS), (10 * SS, 3 * SS)],
                              fill=rgba("#F8F4ED"), width=int(1.8 * SS), joint="curve")
    tick.resize((12, 12), Image.LANCZOS).save(CALAMARES / "check.png")
    # Welcome page artwork: the lockup in ink on the light content area
    lockup(120, fg=P.INK, thin=P.ACCENT, os_color=P.MUTED).save(CALAMARES / "welcome.png", optimize=True)


def render_desktop_cards():
    """Preview cards for the Desktop page (packagechooser needs an image per item)."""
    out = CALAMARES / "desktop"
    out.mkdir(parents=True, exist_ok=True)
    serif = ImageFont.truetype(str(SERIF), 64)
    mono = ImageFont.truetype(str(MONO), 15)
    cards = {
        "base": ("Base system", "console login · add a desktop later"),
        "hyprland": ("Hyprland", "serpantinum · dynamic tiling"),
        "niri": ("niri", "serpantinum · scrollable tiling"),
        "sway": ("Sway", "serpantinum · i3-style tiling"),
        "mango": ("MangoWC", "serpantinum · dwl-style tiling"),
    }
    w, h = 560, 340
    for key, (title, sub) in cards.items():
        img = vignette((w, h), P.INK, "#0C0A09", 0.6).convert("RGBA")
        g = mark(300, thick="#1E1916", thin="#2A1A1D")
        img.alpha_composite(g, (w - 230, 20))
        d = ImageDraw.Draw(img)
        d.text((36, h - 92), title, font=serif, fill=rgba(P.PAPER), anchor="ls")
        d.text((38, h - 50), sub, font=mono, fill=rgba(P.MUTED), anchor="ls")
        if key != "base":
            d.rectangle((36, 36, 36 + 28, 36 + 3), fill=rgba(P.ACCENT_HI))
        img.convert("RGB").save(out / f"{key}.png", optimize=True)


# ---------------------------------------------------------------- loose logo files

def render_logo():
    LOGO.mkdir(parents=True, exist_ok=True)
    (LOGO / "vinos-mark.svg").write_text(mark_svg(P.INK, P.ACCENT))
    (LOGO / "vinos-mark-dark.svg").write_text(mark_svg(P.PAPER, P.ACCENT_HI))
    for s in (64, 128, 256, 512):
        mark(s, P.INK, P.ACCENT).save(LOGO / f"vinos-mark-{s}.png", optimize=True)
    lockup(160).save(LOGO / "vinos-lockup-dark.png", optimize=True)
    lockup(160, fg=P.INK, thin=P.ACCENT).save(LOGO / "vinos-lockup-light.png", optimize=True)


if __name__ == "__main__":
    render_logo()
    render_grub()
    render_syslinux()
    render_calamares()
    render_desktop_cards()
    print("rendered into", ROOT)
