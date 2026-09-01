# RUXX Enterprises — Brand Assets & Logo Package

A complete, production-ready logo kit for **RUXX** (RUXX Enterprises).
All artwork is original, clipart-free, and generated as precise vector paths so it
scales cleanly to any size — from a 16px browser tab to a billboard.

> Brand name: **RUXX**
> Sub-brand / legal line: **ENTERPRISES | DIGITAL • AUTOMATION • EXPORTS**
> Style: flat, modern, minimalist • mandala / henna / peacock motif inside a bold geometric **R**
> Palette: **pure black `#000000`** and **pure white `#FFFFFF`**

---

## 1. What's in the package

```
brand/ruxx/
├── svg/   ← vector masters (infinitely scalable, editable)   [primary source]
├── png/   ← high-resolution flat rasters (crisp, web & slides)
├── ico/   ← browser favicons (multi-resolution)
└── build/ ← generator script (regenerate / tweak everything)
```

### Vector source (`.svg`)
Use these as the **master files**. They are lossless at any scale and are the
right choice for print, merchandise, high-density screens, and future editing.

| File | What it is | Best for |
|------|-----------|----------|
| `ruxx-logo-primary-dark.svg` | Emblem on top, RUXX, tagline | Heroes, billboards, pitch decks |
| `ruxx-logo-primary-light.svg` | Same, black-on-white | Light layouts, white letterheads |
| `ruxx-logo-primary-transparent.svg` | Full logo, no background | Dark photos, video overlays |
| `ruxx-logo-horizontal-dark.svg` | Emblem left, text right | Headers, nav bars, invoices |
| `ruxx-logo-horizontal-light.svg` | Horizontal, black-on-white | Light UI, documents |
| `ruxx-logo-horizontal-transparent.svg` | Horizontal, no background | Email signatures, overlays |
| `ruxx-emblem.svg` | The mandala **R**, standalone | App icons, avatars, monogram |
| `ruxx-emblem-rect-dark.svg` | Emblem on black rounded canvas | Social profile pictures |
| `ruxx-emblem-rect-light.svg` | Emblem on white rounded canvas | Light social/avatars |
| `ruxx-favicon.svg` | Simplified bold **R** + dot-ring | Browser tab icon |
| `ruxx-favicon-light.svg` | Simplified **R**, black-on-white | Light favicon |
| `ruxx-wordmark-dark.svg` | **RUXX** + tagline, no emblem | Footers, contracts, minimal decks |
| `ruxx-wordmark-light.svg` | Wordmark, black-on-white | Light documents |
| `ruxx-wordmark-transparent.svg` | Wordmark, no background | Overlays |

### Raster (`.png`)

| File | Notes |
|------|-------|
| `ruxx-logo-primary-{dark,light,transparent}.png` | 1400×1700, flat |
| `ruxx-logo-horizontal-{dark,light,transparent}.png` | 2200×900, flat |
| `ruxx-wordmark-{dark,light,transparent}.png` | 1600×640, flat |
| `ruxx-monogram-{128,256,512}.png` | Detailed mandala **R**, square |
| `ruxx-emblem-transparent-1024.png` | White R + black ink, transparent bg |
| `ruxx-emblem-cutout-transparent-1024.png` | White R with **hollow ink** (holes) for dark overlays |
| `ruxx-emblem-black-transparent-1024.png` | Black R, transparent bg (for light overlays) |
| `ruxx-emblem-rect-dark-1024.png` / `rect-light-1024.png` | With rounded background, for avatars |
| `ruxx-favicon-{16,32,48,64,128,256}.png` | Simplified favicon in every size |

### Favicon (`.ico`)
| File | Contains |
|------|----------|
| `favicon.ico` | Dark icon at 16, 32, 48, 64, 128, 256 px |
| `favicon-light.ico` | Light icon at the same resolutions |

---

## 2. When to use which

| Context | Recommended file | Format |
|---------|-----------------|--------|
| Landing page / hero | `ruxx-logo-primary-dark` | SVG or PNG |
| Website header / navbar | `ruxx-logo-horizontal-*` | SVG |
| Email signature / invoice | `ruxx-logo-horizontal-transparent` | PNG |
| Social profile pic (LinkedIn/X/Insta) | `ruxx-emblem-rect-*` | PNG (square) |
| Mobile app icon | `ruxx-monogram-512` | PNG |
| Browser tab / favicon | `favicon.ico` | ICO |
| Document / letterhead (light) | `ruxx-logo-primary-light` | SVG/PNG |
| Footer / legal / contracts | `ruxx-wordmark-*` | SVG |
| Merch / print / large format | any `.svg` | SVG |
| Rubber stamp / official print | `ruxx-logo-horizontal-light` (black on white) | SVG |
| Overlay on dark photo / video | `ruxx-emblem-cutout-transparent-1024` | PNG |

---

## 3. Colors & style rules

- **Primary palette:** keep it strictly black-and-white. Do **not** add color fills.
- **Contrast rule:** white logo on a dark/black surface; black logo on a white/light surface.
- **Clear space:** keep a margin of at least the height of the "R" `X`-height around the logo on all sides.
- **Minimum size:** when printing the full stacked logo keep the emblem at least ~8mm wide;
  below that, switch to the wordmark or favicon.
- **Do not:** stretch, rotate, add shadows/gradients, outline the text, or drop the tagline
  (unless at very small sizes where the tagline becomes unreadable).
- **Small sizes:** at icon/favicon sizes always use the simplified `ruxx-favicon-*` or monogram —
  not the full detailed emblem — so the mark stays legible.

---

## 4. Technical file formats

| Format | Use |
|--------|-----|
| **`.svg`** | Vector master. Scale to any size, ideal for print/merch. |
| **`.png`** | High-res transparent raster for web, slides, social. |
| **`.ico`** | Multi-resolution favicon for browsers. |

> Need `.ai`, `.eps`, or `.pdf`? The `.svg` files are the canonical vector source;
> open them in Illustrator/Inkscape and export to `.ai`/`.eps`/`.pdf` with one click.
> The `build/` script regenerates every asset if you tweak a value.

---

## 5. Regenerating the package

All assets are produced by a single deterministic script:

```bash
cd brand/ruxx/build
python3 build_brand.py
```

It writes fresh `.svg`, `.png`, and `.ico` files. It depends on:

- `resvg-py` (Rust SVG renderer) — install with `pip install resvg-py`
- `Pillow` — `pip install pillow`

Source files start at `Emblem geometry` in `build_brand.py` — change the R
silhouette, the mandala motif radii, the tagline text, or the palette in one place
and re-run to regenerate the whole kit.

---

## 6. Fonts

Text uses a neutral bold geometric sans (bundled here as **DejaVu Sans Bold**).
The SVG masters declare a fallback stack
(`'DejaVu Sans', 'Arial', 'Helvetica Neue', Helvetica, sans-serif`) so they render
correctly on machines that don't ship DejaVu. If you'd prefer a different brand
font (e.g. Inter, Montserrat, Roboto), replace the font files referenced in
`build_brand.py` and re-run — the letter-spacing and fit logic adapts automatically.

---

*Generated for RUXX Enterprises. For questions on usage or customisation, refer
to this guide or re-run the build script.*
