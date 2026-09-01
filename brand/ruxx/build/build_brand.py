#!/usr/bin/env python3
"""
RUXX Enterprises — brand package generator.

Pipeline:
  1. Author SVG masters (clipart-free, generated vector paths).
  2. Rasterize with resvg-py (real SVG renderer, no cairo needed).
  3. Color-key/post-process with Pillow for transparent & cut-out variants.
  4. Assemble multi-resolution favicon.ico.

Outputs land in ../svg, ../png, ../ico.
"""
import os, math, shutil
import resvg_py
from PIL import Image, ImageFont

HERE   = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.abspath(os.path.join(HERE, ".."))
SVGDIR = os.path.join(ROOT, "svg")
PNGDIR = os.path.join(ROOT, "png")
ICODIR = os.path.join(ROOT, "ico")
ISO     = os.path.join(ROOT, "iso")
for d in (SVGDIR, PNGDIR, ICODIR, ISO):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- fonts
DEJAVU = "/usr/share/fonts/truetype/dejavu"
FONT_FILES = [
    os.path.join(DEJAVU, "DejaVuSans-Bold.ttf"),
    os.path.join(DEJAVU, "DejaVuSans.ttf"),
    os.path.join(DEJAVU, "DejaVuSansMono-Bold.ttf"),
]

INK   = "#FFFFFF"
BLACK = "#000000"
GRAY  = "#B9BEC4"   # subtle secondary, rarely used

FONT_MAIN   = "'DejaVu Sans',  'Arial', 'Helvetica Neue', Helvetica, sans-serif"
FONT_MONO   = "'DejaVu Sans Mono', 'Courier New', monospace"

TAGLINE = "ENTERPRISES | DIGITAL • AUTOMATION • EXPORTS"

# ---------------------------------------------------------------- text metrics
def text_width_px(s, fontsize, ttf_path=os.path.join(DEJAVU, "DejaVuSans-Bold.ttf")):
    """Approximate rendered width (px) of `s` at `fontsize` using PIL metrics,
    adding letter-spacing by scaling with the average advance for uppercase."""
    f = ImageFont.truetype(ttf_path, int(fontsize))
    w = f.getlength(s)
    return w

def fit_size(s, available, ttf_path=os.path.join(DEJAVU, "DejaVuSans-Bold.ttf"),
             max_size=1000, spacing=0):
    """Largest font size at which `s` fits within `available` px (incl. spacing)."""
    lo, hi = 4, max_size
    best = 4
    for _ in range(60):
        mid = (lo + hi) / 2
        f = ImageFont.truetype(ttf_path, int(mid))
        w = f.getlength(s) + spacing * (len(s) - 1)
        if w <= available:
            best = mid
            lo = mid
        else:
            hi = mid
    return best

# ---------------------------------------------------------------- geometry
# R silhouette drawn in a 512x512 box, using a bold geometric letterform.
R_OUTER = ("M178 102 L320 102 Q384 102 384 162 L384 246 Q384 310 322 310 "
           "L302 310 L368 412 L306 412 L246 310 L246 412 L178 412 Z")

def _rrect(x, y, w, h, r):
    return (f"M{x+r} {y} L{x+w-r} {y} Q{x+w} {y} {x+w} {y+r} "
            f"L{x+w} {y+h-r} Q{x+w} {y+h} {x+w-r} {y+h} "
            f"L{x+r} {y+h} Q{x} {y+h} {x} {y+h-r} L{x} {y+r} Q{x} {y} {x+r} {y} Z")

# Counter (the hole in the bowl). Added as evenodd subpath so it stays a true hole.
R_COUNTER = _rrect(248, 168, 74, 82, 30)
R_PATH    = f"{R_OUTER} {R_COUNTER}"

# ---------------------------------------------------------------- motifs
def motifs(ink):
    """The mandala / henna / peacock linework. Drawn in `ink` colour as thin
    filled & stroked shapes, later clipped inside the R."""
    g = []
    cx, cy = 281, 206   # bowl visual centre

    # --- henna lattice (diamonds + dots) filling the whole bowl area ---
    def lattice(x0, y0, x1, y1, step):
        row = 0
        y = y0
        while y <= y1:
            x = x0
            off = (step // 2) if (row % 2) else 0
            while x + off <= x1:
                px = x + off
                if (row % 2) == 0:
                    g.append(f'<path d="M{px} {y} L{px+5} {y} L{px} {y+5} '
                             f'L{px-5} {y} Z" fill="{ink}"/>')
                else:
                    g.append(f'<circle cx="{px}" cy="{y}" r="2.4" fill="{ink}"/>')
                x += step
            y += step
            row += 1
    lattice(186, 108, 380, 306, 26)

    # --- central mandala medallion ---
    g.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{ink}"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="20" fill="none" stroke="{ink}" stroke-width="2.6"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="27" fill="none" stroke="{ink}" '
             f'stroke-width="1.2" stroke-dasharray="2.6 3.4"/>')
    for i in range(16):
        a = 2 * math.pi * i / 16
        r1, r2 = 34, 78
        x1, y1 = cx + r1 * math.cos(a), cy + r1 * math.sin(a)
        x2, y2 = cx + r2 * math.cos(a), cy + r2 * math.sin(a)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        g.append(f'<path d="M{x1:.1f} {y1:.1f} L{mx:.1f} {my-3.6:.1f} L{x2:.1f} {y2:.1f} '
                 f'L{mx:.1f} {my+3.6:.1f} Z" fill="{ink}"/>')
    for i in range(16):
        a = 2 * math.pi * i / 16 + math.pi / 16
        x, y = cx + 88 * math.cos(a), cy + 88 * math.sin(a)
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="{ink}"/>')
    # outer petal outline ring
    g.append(f'<circle cx="{cx}" cy="{cy}" r="99" fill="none" stroke="{ink}" '
             f'stroke-width="1.6" stroke-dasharray="5 4"/>')

    # --- peacock eye feathers (4 around the bowl) ---
    def eye(x, y, ang, r=1.0, flip=False):
        sc = -1 if flip else 1
        g.append(f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang}) scale({r},{r*sc})">'
                 f'<path d="M0 20 Q 17 2 0 -22 Q -17 2 0 20 Z" fill="none" stroke="{ink}" stroke-width="2.4"/>'
                 f'<path d="M0 14 Q 13 1 0 -15 Q -13 1 0 14 Z" fill="{ink}"/>'
                 f'<circle cx="0" cy="-6" r="3" fill="#fff"/></g>')
    eye(333, 150, 130)
    eye(333, 298, 228)
    eye(214, 298, -132)
    eye(214, 150, -48)

    # --- petal + chevron detail on stem and leg ---
    for i, yy in enumerate([172, 236, 300, 362]):
        eye(216, yy, 92, 0.82)
    for t in range(0, 5):
        bx = 262 + t * 19
        by = 322 + t * 20
        g.append(f'<path d="M{bx} {by} L{bx+12} {by-9} L{bx+6} {by+2}" '
                 f'fill="none" stroke="{ink}" stroke-width="2.4"/>')
    # scalloped shelf border
    g.append(f'<path d="M258 238 Q 275 250 303 238" fill="none" stroke="{ink}" stroke-width="2.6"/>')
    g.append(f'<path d="M262 306 L298 306 Q 316 306 332 338 L342 372" fill="none" '
             f'stroke="{ink}" stroke-width="2.4" stroke-dasharray="6 4"/>')
    return "".join(g)

def emblem_svg(r_fill, ink, transparent=True, outline=True, radius=None):
    """Inner 512x512 SVG markup for the mandala-filled R emblem."""
    bg = "" if transparent else f'<rect x="0" y="0" width="512" height="512" fill="{BLACK}"/>'
    if radius is not None and not transparent:
        bg = (f'<rect x="0" y="0" width="512" height="512" fill="{BLACK}" '
              f'rx="{radius}" ry="{radius}"/>')
    edge = ""
    if outline:
        edge = (f'<path d="{R_OUTER}" fill="none" stroke="{r_fill}" stroke-width="7"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
<defs><clipPath id="R"><path d="{R_PATH}" fill-rule="evenodd"/></clipPath></defs>
{bg}
<g clip-path="url(#R)">
  <rect x="0" y="0" width="512" height="512" fill="{r_fill}"/>
  {motifs(ink)}
</g>
{edge}
</svg>'''

# ---------------------------------------------------------------- render
def render(svg, out_png, width=None, height=None):
    png = resvg_py.svg_to_bytes(
        svg,
        font_files=FONT_FILES,
        width=width,
        height=height,
        background=None,
        skip_system_fonts=True,
    )
    with open(out_png, "wb") as f:
        f.write(png)
    return out_png

def color_key_transparent(path, threshold=48):
    """Replace near-black ink pixels with transparency (within opaque regions).
    Used to turn a black-on-white motif into cut-out holes for dark overlays."""
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0 and r < threshold and g < threshold and b < threshold:
                px[x, y] = (0, 0, 0, 0)
    im.save(path)
    return path

def save_ico(source_png, out_ico, sizes=(16, 32, 48, 64, 128, 256)):
    im = Image.open(source_png).convert("RGBA")
    im.save(out_ico, format="ICO", sizes=[(s, s) for s in sizes])
    return out_ico

def fit_center_square(path, side=512, pad=0.06):
    """Fit the artwork in `path` onto a square `side` canvas, centered, with a
    tasteful margin. Non-square sources (e.g. the portrait stacked logo) get a
    solid black pad so they can live inside an ICO without distortion."""
    im = Image.open(path).convert("RGBA")
    # Composite onto black first so we can measure the artwork's bounding box.
    canvas = Image.new("RGBA", im.size, (0, 0, 0, 255))
    canvas.alpha_composite(im)
    bbox = canvas.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    scale = (side * (1 - 2 * pad)) / max(im.size)
    new = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))),
                    Image.LANCZOS)
    out = Image.new("RGBA", (side, side), (0, 0, 0, 255))
    out.alpha_composite(new, ((side - new.width) // 2, (side - new.height) // 2))
    return out

def write_svg(name, svg):
    p = os.path.join(SVGDIR, name)
    with open(p, "w") as f:
        f.write(svg)
    return p

# ---------------------------------------------------------------- layouts
def stacked_svg(r_fill, ink, text, transparent, bg=None, canvas=(1400, 1700)):
    """Primary stacked logo: emblem on top, RUXX, tagline below."""
    W, H = canvas
    bg_rect = "" if transparent else f'<rect x="0" y="0" width="{W}" height="{H}" fill="{bg or BLACK}"/>'
    emb_w = int(W * 0.56)
    emb_x = (W - emb_w) // 2
    emb_y = int(H * 0.05)

    # Wordmark "RUXX" — fit to ~80% of width with generous tracking.
    word_size = fit_size("RUXX", W * 0.8, max_size=W, spacing=14)
    # Tagline — fit to ~92% of width.
    avail = W * 0.92
    tag_size = fit_size(TAGLINE, avail, max_size=W, spacing=2.2)

    # vertical positions
    ruxx_y = emb_y + emb_w + int(H * 0.13)
    tag_y = ruxx_y + int(word_size * 0.62)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
{bg_rect}
<svg x="{emb_x}" y="{emb_y}" width="{emb_w}" height="{emb_w}" viewBox="0 0 512 512">
  {emblem_svg(r_fill, ink, transparent=True)}
</svg>
<text x="{W//2}" y="{ruxx_y}" font-family="{FONT_MAIN}" font-weight="bold"
      font-size="{word_size:.0f}" fill="{text}" letter-spacing="14" text-anchor="middle">RUXX</text>
<text x="{W//2}" y="{tag_y}" font-family="{FONT_MAIN}" font-weight="bold"
      font-size="{tag_size:.0f}" fill="{text}" letter-spacing="2.2" text-anchor="middle">{TAGLINE}</text>
</svg>'''

def horizontal_svg(r_fill, ink, text, transparent, bg=None, canvas=(2200, 900)):
    """Secondary horizontal logo: emblem left, wordmark+tagline right."""
    W, H = canvas
    bg_rect = "" if transparent else f'<rect x="0" y="0" width="{W}" height="{H}" fill="{bg or BLACK}"/>'
    emb = int(H * 0.92)
    ex = int(H * 0.05)
    ey = (H - emb) // 2
    tx = ex + emb + int(H * 0.18)
    text_right = W - int(H * 0.06)
    avail = text_right - tx

    word_size = fit_size("RUXX", avail * 0.7, max_size=avail, spacing=8)
    tag_size = fit_size(TAGLINE, avail, max_size=avail, spacing=1.6)

    # vertical centers for the two lines within the emblem's vertical span
    line1_y = int(H * 0.46)
    line2_y = line1_y + int(word_size * 0.66)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
{bg_rect}
<svg x="{ex}" y="{ey}" width="{emb}" height="{emb}" viewBox="0 0 512 512">
  {emblem_svg(r_fill, ink, transparent=True)}
</svg>
<text x="{tx}" y="{line1_y}" font-family="{FONT_MAIN}" font-weight="bold"
      font-size="{word_size:.0f}" fill="{text}" letter-spacing="8" text-anchor="start">RUXX</text>
<text x="{tx}" y="{line2_y}" font-family="{FONT_MAIN}" font-weight="bold"
      font-size="{tag_size:.0f}" fill="{text}" letter-spacing="1.6" text-anchor="start">{TAGLINE}</text>
</svg>'''

def wordmark_svg(text, transparent, bg=None, canvas=(1600, 640)):
    W, H = canvas
    bg_rect = "" if transparent else f'<rect x="0" y="0" width="{W}" height="{H}" fill="{bg or BLACK}"/>'
    word_size = fit_size("RUXX", W * 0.84, max_size=H, spacing=12)
    tag_size = fit_size(TAGLINE, W * 0.9, max_size=W, spacing=2.2)
    ruxx_y = int(H * 0.55)
    tag_y = ruxx_y + int(word_size * 0.58)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
{bg_rect}
<text x="{W//2}" y="{ruxx_y}" font-family="{FONT_MAIN}" font-weight="bold"
      font-size="{word_size:.0f}" fill="{text}" letter-spacing="12" text-anchor="middle">RUXX</text>
<text x="{W//2}" y="{tag_y}" font-family="{FONT_MAIN}" font-weight="bold"
      font-size="{tag_size:.0f}" fill="{text}" letter-spacing="2.2" text-anchor="middle">{TAGLINE}</text>
</svg>'''

def favicon_svg(fg, transparent, bg=None, radius=100, canvas=512):
    """Simplified, ultra-clean emblem suitable for small sizes.
    A bold solid R with a single crisp ring of dots that reads as a mandala
    even at 16px (thin lines collapse; dots/negative space survive)."""
    bg_rect = "" if transparent else (
        f'<rect x="0" y="0" width="{canvas}" height="{canvas}" '
        f'fill="{bg or BLACK}" rx="{radius}" ry="{radius}"/>')
    motif = fg
    counter = "#000000"
    # a few bold radiating dots + one ring, sized to survive 16px
    dots = []
    cx, cy = 281, 206
    for i in range(12):
        a = math.radians(i * 30)
        r = 62
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{counter}"/>')
    ring = (f'<circle cx="{cx}" cy="{cy}" r="40" fill="none" '
            f'stroke="{counter}" stroke-width="9"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
{bg_rect}
<path d="{R_PATH}" fill="{fg}" fill-rule="evenodd"/>
<g>{ring}{"".join(dots)}</g>
</svg>'''

# ---------------------------------------------------------------- build
def build_all():
    # DARK THEME (white on black) + INVERTED (black on white)
    # (a) Standalone emblem
    w = 1024
    out = render(emblem_svg(INK, BLACK, transparent=False), os.path.join(PNGDIR, "ruxx-emblem-rect-dark-1024.png"), w, w)
    out_t = render(emblem_svg(INK, BLACK, transparent=True), os.path.join(PNGDIR, "ruxx-emblem-transparent-1024.png"), w, w)
    # overlay-friendly: white R, ink cut out
    render(emblem_svg(INK, INK, transparent=True), "/tmp/em_cut.png", w, w)
    color_key_transparent("/tmp/em_cut.png")
    shutil.copy("/tmp/em_cut.png", os.path.join(PNGDIR, "ruxx-emblem-cutout-transparent-1024.png"))

    # inverted (black on white)
    out_i = render(emblem_svg(BLACK, INK, transparent=False), os.path.join(PNGDIR, "ruxx-emblem-rect-light-1024.png"), w, w)
    # black emblem transparent
    render(emblem_svg(BLACK, INK, transparent=True), os.path.join(PNGDIR, "ruxx-emblem-black-transparent-1024.png"), w, w)

    # (b) Primary stacked (dark + light)
    render(stacked_svg(INK, BLACK, INK, transparent=False), os.path.join(PNGDIR, "ruxx-logo-primary-dark.png"), 1400, 1700)
    render(stacked_svg(INK, BLACK, INK, transparent=True), os.path.join(PNGDIR, "ruxx-logo-primary-transparent.png"), 1400, 1700)
    render(stacked_svg(BLACK, INK, BLACK, transparent=False, bg="#FFFFFF"), os.path.join(PNGDIR, "ruxx-logo-primary-light.png"), 1400, 1700)

    write_svg("ruxx-logo-primary-dark.svg",
              stacked_svg(INK, BLACK, INK, transparent=False))
    write_svg("ruxx-logo-primary-transparent.svg",
              stacked_svg(INK, BLACK, INK, transparent=True))
    write_svg("ruxx-logo-primary-light.svg",
              stacked_svg(BLACK, INK, BLACK, transparent=False, bg="#FFFFFF"))

    # (c) Secondary horizontal (dark + light)
    render(horizontal_svg(INK, BLACK, INK, transparent=False), os.path.join(PNGDIR, "ruxx-logo-horizontal-dark.png"), 2200, 900)
    render(horizontal_svg(INK, BLACK, INK, transparent=True), os.path.join(PNGDIR, "ruxx-logo-horizontal-transparent.png"), 2200, 900)
    render(horizontal_svg(BLACK, INK, BLACK, transparent=False, bg="#FFFFFF"), os.path.join(PNGDIR, "ruxx-logo-horizontal-light.png"), 2200, 900)

    write_svg("ruxx-logo-horizontal-dark.svg",
              horizontal_svg(INK, BLACK, INK, transparent=False))
    write_svg("ruxx-logo-horizontal-transparent.svg",
              horizontal_svg(INK, BLACK, INK, transparent=True))
    write_svg("ruxx-logo-horizontal-light.svg",
              horizontal_svg(BLACK, INK, BLACK, transparent=False, bg="#FFFFFF"))

    # (d) Wordmark / logotype only
    render(wordmark_svg(INK, transparent=False), os.path.join(PNGDIR, "ruxx-wordmark-dark.png"), 1600, 640)
    render(wordmark_svg(INK, transparent=True), os.path.join(PNGDIR, "ruxx-wordmark-transparent.png"), 1600, 640)
    render(wordmark_svg(BLACK, transparent=False, bg="#FFFFFF"), os.path.join(PNGDIR, "ruxx-wordmark-light.png"), 1600, 640)
    write_svg("ruxx-wordmark-dark.svg", wordmark_svg(INK, transparent=False))
    write_svg("ruxx-wordmark-transparent.svg", wordmark_svg(INK, transparent=True))
    write_svg("ruxx-wordmark-light.svg", wordmark_svg(BLACK, transparent=False, bg="#FFFFFF"))

    # (e) Standalone emblem SVGs
    write_svg("ruxx-emblem.svg", emblem_svg(INK, BLACK, transparent=True))
    write_svg("ruxx-emblem-rect-dark.svg", emblem_svg(INK, BLACK, transparent=False))
    write_svg("ruxx-emblem-rect-light.svg", emblem_svg(BLACK, INK, transparent=False))

    # (f) Favicon (simplified solid R) + ICO
    render(favicon_svg(INK, transparent=False), os.path.join(ICODIR, "favicon-source-512.png"), 512, 512)
    write_svg("ruxx-favicon.svg", favicon_svg(INK, transparent=False))
    save_ico(os.path.join(ICODIR, "favicon-source-512.png"),
             os.path.join(ICODIR, "favicon.ico"))
    # also a transparent favicon source + light favicon
    render(favicon_svg(BLACK, transparent=False, bg="#FFFFFF"), os.path.join(ICODIR, "favicon-light-source-512.png"), 512, 512)
    save_ico(os.path.join(ICODIR, "favicon-light-source-512.png"),
             os.path.join(ICODIR, "favicon-light.ico"))
    write_svg("ruxx-favicon-light.svg", favicon_svg(BLACK, transparent=False, bg="#FFFFFF"))

    # --- small-size PNGs -------------------------------------------------
    # Detailed monogram for app icons / avatars (large enough to hold detail).
    for s in (128, 256, 512):
        render(emblem_svg(INK, BLACK, transparent=False),
               os.path.join(PNGDIR, f"ruxx-monogram-{s}.png"), s, s)
    # Simplified favicon PNGs (browser-tab safe: 16/32/48 readable).
    for s in (16, 32, 48, 64, 128, 256):
        render(favicon_svg(INK, transparent=False),
               os.path.join(PNGDIR, f"ruxx-favicon-{s}.png"), s, s)

    # --- ICO versions of the two requested pieces -----------------------
    # (1) Primary stacked logo as a square favicon-style ICO
    fit_center_square(os.path.join(PNGDIR, "ruxx-logo-primary-dark.png"), 512).save(
        os.path.join(ICODIR, "ruxx-logo-primary-source-512.png"))
    save_ico(os.path.join(ICODIR, "ruxx-logo-primary-source-512.png"),
             os.path.join(ICODIR, "ruxx-logo-primary.ico"))
    # (2) R emblem (mandala monogram) as ICO
    fit_center_square(os.path.join(PNGDIR, "ruxx-monogram-512.png"), 512).save(
        os.path.join(ICODIR, "ruxx-emblem-source-512.png"))
    save_ico(os.path.join(ICODIR, "ruxx-emblem-source-512.png"),
             os.path.join(ICODIR, "ruxx-emblem.ico"))

    print("BUILD COMPLETE")

if __name__ == "__main__":
    build_all()
