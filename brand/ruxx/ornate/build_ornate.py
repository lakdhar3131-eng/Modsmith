#!/usr/bin/env python3
"""
RUXX — ORNATE peacock/mandala logo variants.

Takes the AI-generated ornate R emblem (master-emblem.png) and derives a full
set of assets: transparent / inverted / on-black emblem layers, then the primary
stacked, horizontal and wordmark logos, in PNG + SVG + ICO.

The emblem is raster art (AI-generated), so it is embedded into SVGs as a
high-res PNG data URI. Text/wordmark is authored as real vector text.
"""
import os, io, base64, math, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.abspath(os.path.join(HERE, ".."))
ORND  = HERE
PNGD  = os.path.join(ORND, "png")
SVGD  = os.path.join(ORND, "svg")
ICOD  = os.path.join(ORND, "ico")
for d in (PNGD, SVGD, ICOD):
    os.makedirs(d, exist_ok=True)

DEJAVU = "/usr/share/fonts/truetype/dejavu"
FONT_BOLD = os.path.join(DEJAVU, "DejaVuSans-Bold.ttf")
FONT_REG  = os.path.join(DEJAVU, "DejaVuSans.ttf")
FONT_FILES = [FONT_BOLD, FONT_REG,
              os.path.join(DEJAVU, "DejaVuSansMono-Bold.ttf")]

TAGLINE = "ENTERPRISES | DIGITAL • AUTOMATION • EXPORTS"
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

MASTER = os.path.join(ORND, "master-emblem.png")

# ---------------------------------------------------------------- emblem layers
def load_master():
    im = Image.open(MASTER).convert("RGB")
    return im

def emblem_mask(im, dark_thresh=48):
    """Return float HxW mask of the R region (1 = letter, 0 = background).
    The outer background is flood-filled from the borders; because the letter
    has a white outline, the inner (black) linework is sealed inside and stays
    part of the letter."""
    a = np.asarray(im.convert("L")).astype(np.float32)
    h, w = a.shape
    # bright/letter, dark/bg
    dark = a < dark_thresh
    # seed flood-fill region: outer background connected to the border
    region = np.zeros((h, w), bool)
    from collections import deque
    dq = deque()
    # set border seeds that are dark
    for x in range(w):
        for y in (0, h - 1):
            if dark[y, x] and not region[y, x]:
                region[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if dark[y, x] and not region[y, x]:
                region[y, x] = True; dq.append((y, x))
    # BFS over dark pixels (background region). The white outline blocks entry.
    while dq:
        y, x = dq.popleft()
        for ny, nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0 <= ny < h and 0 <= nx < w and dark[ny, nx] and not region[ny, nx]:
                region[ny, nx] = True; dq.append((ny, nx))
    letter = (~region).astype(np.float32)
    return letter

def to_transparent(master, letter):
    """White R + black linework on transparent (keeps ink)."""
    a = np.asarray(master).astype(np.float32)
    lum = np.asarray(master.convert("L")).astype(np.float32) / 255.0
    alpha = letter  # where letter, opaque
    out = np.zeros((*lum.shape, 4), np.float32)
    # RGB: keep original grayscale; white letter body stays white, linework stays dark
    out[..., 0] = lum
    out[..., 1] = lum
    out[..., 2] = lum
    out[..., 3] = alpha
    return Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8), "RGBA")

def to_inverted(letter):
    """Black R + white linework on transparent."""

def invert_layer(master, letter):
    """Black R with WHITE linework on transparent (for light backgrounds)."""
    a = np.asarray(master).astype(np.float32)
    lum = np.asarray(master.convert("L")).astype(np.float32) / 255.0
    alpha = letter
    inv = 1.0 - lum
    out = np.zeros((*inv.shape, 4), np.float32)
    out[..., 0] = inv
    out[..., 1] = inv
    out[..., 2] = inv
    out[..., 3] = alpha
    return Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8), "RGBA")

def trim_transparent(im, pad=6):
    bbox = im.getbbox()
    if bbox:
        bbox = (max(0, bbox[0]-pad), max(0, bbox[1]-pad),
                min(im.width, bbox[2]+pad), min(im.height, bbox[3]+pad))
        im = im.crop(bbox)
    return im

def fit_font(text, max_w, max_size=600):
    """Largest bold font whose string fits within max_w px."""
    size = max_size
    while size > 4:
        if ImageFont.truetype(FONT_BOLD, size).getlength(text) <= max_w:
            return ImageFont.truetype(FONT_BOLD, size)
        size -= 4
    return ImageFont.truetype(FONT_BOLD, 4)

# ---------------------------------------------------------------- render via resvg
import resvg_py
def render_svg(svg, out_png, width=None, height=None):
    png = resvg_py.svg_to_bytes(svg, font_files=FONT_FILES, width=width,
                                height=height, background=None,
                                skip_system_fonts=True)
    with open(out_png, "wb") as f:
        f.write(png)
    return out_png

def emb_png_to_svg(path, width_px=None):
    """Wrap a PNG as an SVG data URI image on a 512 square canvas."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    w, h = Image.open(path).size
    return (f'<image width="{w}" height="{h}" '
            f'xlink:href="data:image/png;base64,{data}"/>', w, h)

def svg_with_bg(inner, width, height, bg=None):
    bg_rect = "" if bg is None else f'<rect width="{width}" height="{height}" fill="{bg}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {width} {height}" width="{width}" height="{height}">{bg_rect}{inner}</svg>')

def text_stack(transparent, canvas=(1400, 1700), bg="#000000", text_fill="#ffffff"):
    """RUXX + tagline block only (no emblem) as SVG text."""
    W, H = canvas
    bg_rect = "" if transparent else f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    wf = fit_font("RUXX", int(W*0.46))
    tf = fit_font(TAGLINE, int(W*0.92))
    tag_y = int(H*0.6) + wf.size * 0.5
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'{bg_rect}'
            f'<text x="{W//2}" y="{int(H*0.6)}" font-family="\'DejaVu Sans\', sans-serif" '
            f'font-weight="bold" font-size="{wf.size}" fill="{text_fill}" letter-spacing="12" '
            f'text-anchor="middle">RUXX</text>'
            f'<text x="{W//2}" y="{tag_y}" font-family="\'DejaVu Sans\', sans-serif" '
            f'font-weight="bold" font-size="{tf.size}" fill="{text_fill}" letter-spacing="2.4" '
            f'text-anchor="middle">{TAGLINE}</text></svg>')

def build():
    master = load_master()
    letter = emblem_mask(master)

    # --- layers (on transparent) ---
    transparent = trim_transparent(to_transparent(master, letter))
    inverted    = trim_transparent(invert_layer(master, letter))
    transparent.save(os.path.join(PNGD, "ornate-emblem-transparent-1024.png"))
    inverted.save(os.path.join(PNGD, "ornate-emblem-inverted-transparent-1024.png"))

    # --- on-black / on-white squarish emblem (for avatars / app icons) ---
    on_black = Image.new("RGBA", (1024, 1024), BLACK)
    te = transparent.copy()
    on_black.alpha_composite(te, ((1024 - te.width)//2, (1024 - te.height)//2))
    on_black.save(os.path.join(PNGD, "ornate-emblem-black-1024.png"))
    on_white = Image.new("RGBA", (1024, 1024), WHITE)
    inv = inverted.copy()
    on_white.alpha_composite(inv, ((1024 - inv.width)//2, (1024 - inv.height)//2))
    on_white.save(os.path.join(PNGD, "ornate-emblem-white-1024.png"))

    # small sizes for app/favicon guidance
    for s in (128, 256, 512):
        on_black.resize((s, s), Image.LANCZOS).save(
            os.path.join(PNGD, f"ornate-monogram-{s}.png"))

    # --- primary stacked logo (emblem + RUXX + tagline) on black ---
    # Compose: emblem on top, text below, matching reference.
    W, H = 1200, 1500
    canvas = Image.new("RGBA", (W, H), BLACK)
    emb_s = int(W * 0.62)                       # emblem a bit smaller
    te_resized = transparent.copy().resize((emb_s, emb_s), Image.LANCZOS)
    canvas.alpha_composite(te_resized, ((W - emb_s)//2, int(H*0.04)))
    # text — wordmark and tagline sized to fit width
    d = ImageDraw.Draw(canvas)
    word_x = W // 2
    word_y = int(H * 0.72)
    # RUXX sized to ~46% of canvas width
    word_font = fit_font("RUXX", int(W*0.46))
    tag_font  = fit_font(TAGLINE, int(W*0.92))
    tag_y  = word_y + word_font.size * 0.5
    d.text((word_x, word_y), "RUXX", font=word_font, fill=WHITE, anchor="mm")
    d.text((word_x, tag_y), TAGLINE, font=tag_font, fill=WHITE, anchor="mm")
    canvas.convert("RGB").save(os.path.join(PNGD, "ornate-logo-primary-dark.png"))
    # transparent full logo
    canvast = transparent.copy().resize((emb_s, emb_s), Image.LANCZOS)
    full_t = Image.new("RGBA", (W, H), (0,0,0,0))
    full_t.alpha_composite(canvast, ((W - emb_s)//2, int(H*0.04)))
    t = ImageDraw.Draw(full_t)
    word_x = W // 2; word_y = int(H * 0.72)
    tf_word = fit_font("RUXX", int(W*0.46))
    tf_tag  = fit_font(TAGLINE, int(W*0.92))
    tag_y = word_y + tf_word.size * 0.5
    t.text((word_x, word_y), "RUXX", font=tf_word, fill=WHITE, anchor="mm")
    t.text((word_x, tag_y), TAGLINE, font=tf_tag, fill=WHITE, anchor="mm")
    full_t.save(os.path.join(PNGD, "ornate-logo-primary-transparent.png"))
    # light full logo (inverted emblem + black text)
    full_l = Image.new("RGBA", (W, H), WHITE)
    iv = inverted.copy().resize((emb_s, emb_s), Image.LANCZOS)
    full_l.alpha_composite(iv, ((W - emb_s)//2, int(H*0.04)))
    lt = ImageDraw.Draw(full_l)
    lt.text((word_x, word_y), "RUXX", font=ImageFont.truetype(FONT_BOLD, tf_word.size), fill=BLACK, anchor="mm")
    lt.text((word_x, tag_y), TAGLINE, font=ImageFont.truetype(FONT_BOLD, tf_tag.size), fill=BLACK, anchor="mm")
    full_l.convert("RGB").save(os.path.join(PNGD, "ornate-logo-primary-light.png"))

    # --- horizontal logo (emblem left, text right) ---
    def horizontal(emblem_img, bg, text_fill, fname):
        W2, H2 = 2200, 1000
        hz = Image.new("RGBA", (W2, H2), bg)
        emb_s2 = int(H2 * 0.84)
        ex = int(H2 * 0.05)
        hz.alpha_composite(emblem_img.resize((emb_s2, emb_s2), Image.LANCZOS),
                           (ex, (H2 - emb_s2)//2))
        hd = ImageDraw.Draw(hz)
        tx = ex + emb_s2 + int(H2 * 0.10)
        right = W2 - int(H2 * 0.05)
        avail = right - tx
        # wordmark & tagline both fit within the available width
        wf = fit_font("RUXX", avail)
        tf = fit_font(TAGLINE, avail)
        hd.text((tx, int(H2*0.45)), "RUXX", font=wf, fill=text_fill, anchor="lm")
        # space the tagline a bit below the wordmark
        hd.text((tx, int(H2*0.45) + wf.size + 30), TAGLINE, font=tf, fill=text_fill, anchor="lm")
        hz.convert("RGB").save(os.path.join(PNGD, fname))
    horizontal(transparent, BLACK, WHITE, "ornate-logo-horizontal-dark.png")
    horizontal(inverted, WHITE, BLACK, "ornate-logo-horizontal-light.png")
    # transparent horizontal (black text won't show on transparency; use white)
    hzt = Image.new("RGBA", (2200, 1000), (0,0,0,0))
    emb_s2 = int(1000 * 0.84); ex = int(1000 * 0.05)
    hzt.alpha_composite(transparent.resize((emb_s2, emb_s2), Image.LANCZOS),
                        (ex, (1000 - emb_s2)//2))
    hd = ImageDraw.Draw(hzt)
    tx = ex + emb_s2 + int(1000 * 0.10)
    right = 2200 - int(1000 * 0.05)
    hwf = fit_font("RUXX", right - tx)
    htf = fit_font(TAGLINE, right - tx)
    hd.text((tx, 450), "RUXX", font=hwf, fill=WHITE, anchor="lm")
    hd.text((tx, int(450 + hwf.size*0.9)), TAGLINE, font=htf, fill=WHITE, anchor="lm")
    hzt.save(os.path.join(PNGD, "ornate-logo-horizontal-transparent.png"))

    # --- wordmark (text only) ---
    def wordmark(bg, text_fill, fname):
        W3, H3 = 1600, 640
        wm = Image.new("RGBA", (W3, H3), bg)
        wd = ImageDraw.Draw(wm)
        wf = fit_font("RUXX", int(W3*0.5))
        tf = fit_font(TAGLINE, int(W3*0.9))
        wd.text((W3//2, int(H3*0.5)), "RUXX", font=wf, fill=text_fill, anchor="mm")
        wd.text((W3//2, int(H3*0.82)), TAGLINE, font=tf, fill=text_fill, anchor="mm")
        wm.convert("RGB").save(os.path.join(PNGD, fname))
    wordmark(BLACK, WHITE, "ornate-wordmark-dark.png")
    wordmark(WHITE, BLACK, "ornate-wordmark-light.png")

    # --- favicon (simplified: emblem on rounded black tile) ---
    fc = on_black.copy().resize((512, 512), Image.LANCZOS)
    fc.save(os.path.join(PNGD, "ornate-emblem-black-512.png"))
    fc.save(os.path.join(ICOD, "ornate-source-512.png"))

    # --- SVGs (emblem embedded as image) ---
    # transparent emblem svg
    embsvg, ew, eh = emb_png_to_svg(os.path.join(PNGD, "ornate-emblem-transparent-1024.png"))
    with open(os.path.join(SVGD, "ornate-emblem-transparent.svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'viewBox="0 0 {ew} {eh}" width="{ew}" height="{eh}">{embsvg}</svg>')
    # inverted svg
    insw, iw, ih = emb_png_to_svg(os.path.join(PNGD, "ornate-emblem-inverted-transparent-1024.png"))
    with open(os.path.join(SVGD, "ornate-emblem-inverted.svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'viewBox="0 0 {iw} {ih}" width="{iw}" height="{ih}">{insw}</svg>')

    # primary stacked SVGs (emblem image + vector text)
    def stacked_svg(emb_png, bg, text_fill):
        E, w, h = emb_png_to_svg(emb_png)
        W, H = 1200, 1500
        scale = (W*0.62)/h
        ew2 = int(w*scale); eh2 = int(h*scale)
        ex = (W - ew2)//2; ey = int(H*0.04)
        word_y = int(H*0.72)
        ws = fit_font("RUXX", int(W*0.46)).size
        ts = fit_font(TAGLINE, int(W*0.92)).size
        tag_y = word_y + int(ws * 0.5)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
                f'<rect width="{W}" height="{H}" fill="{bg}"/>'
                f'<g transform="translate({ex},{ey}) scale({scale})">{E}</g>'
                f'<text x="{W//2}" y="{word_y}" font-family="\'DejaVu Sans\', sans-serif" '
                f'font-weight="bold" font-size="{ws}" fill="{text_fill}" '
                f'textLength="{int(W*0.46)}" lengthAdjust="spacingAndGlyphs" text-anchor="middle">RUXX</text>'
                f'<text x="{W//2}" y="{tag_y}" font-family="\'DejaVu Sans\', sans-serif" '
                f'font-weight="bold" font-size="{ts}" fill="{text_fill}" '
                f'textLength="{int(W*0.92)}" lengthAdjust="spacingAndGlyphs" text-anchor="middle">{TAGLINE}</text>'
                f'</svg>')
    with open(os.path.join(SVGD, "ornate-logo-primary-dark.svg"), "w") as f:
        f.write(stacked_svg(os.path.join(PNGD, "ornate-emblem-transparent-1024.png"), "#000000", "#ffffff"))
    with open(os.path.join(SVGD, "ornate-logo-primary-light.svg"), "w") as f:
        f.write(stacked_svg(os.path.join(PNGD, "ornate-emblem-inverted-transparent-1024.png"), "#ffffff", "#000000"))

    # wordmark svg (pure vector text)
    with open(os.path.join(SVGD, "ornate-wordmark-dark.svg"), "w") as f:
        f.write(text_stack(False))

    # --- ICO (multi-res) from on-black 512 ---
    def save_ico(src_png, out_ico, sizes=(16,32,48,64,128,256)):
        im = Image.open(src_png).convert("RGBA")
        im.save(out_ico, format="ICO", sizes=[(s,s) for s in sizes])
    save_ico(os.path.join(ICOD, "ornate-source-512.png"), os.path.join(ICOD, "favicon.ico"))
    # light ico
    on_white.alpha_composite(inverted.copy(), ((1024 - inverted.width)//2, (1024 - inverted.height)//2))
    on_white.resize((512,512), Image.LANCZOS).save(os.path.join(ICOD, "ornate-light-source-512.png"))
    save_ico(os.path.join(ICOD, "ornate-light-source-512.png"), os.path.join(ICOD, "favicon-light.ico"))

    print("ORNAte BUILD COMPLETE")

if __name__ == "__main__":
    build()
