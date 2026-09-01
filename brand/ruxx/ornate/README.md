# RUXX — Ornate Peacock / Mandala Logo Kit

This is the **detailed ornate version** — the hero R filled with intricate
black-and-white henna, paisley, mandala and a prominent peacock, matching the
reference design.

It lives in its own folder so the full original kit (`../`) stays intact. The
emblem artwork is AI-generated raster art, so it is embedded into the SVGs as a
high-res image; the **RUXX** wordmark and tagline are real vector text.

## What's here

```
ornate/
├── master-emblem.png            ← the source ornate R (AI-generated, 1024px)
├── build_ornate.py              ← generator (derives all variants)
├── BRAND-BOARD-PREVIEW.png      ← visual overview of all variants
├── png/                         ← 16 high-res raster variants
├── svg/                         ← 5 vector masters
├── ico/                         ← favicons + drop-folder ICOs
├── ruxx-primary-logo/           ← primary logo drop folder (svg/png/ico + README)
└── ruxx-r-emblem/               ← R emblem drop folder (svg/png/ico + README)
```

## Variants

| Variant | Files |
|---------|-------|
| Primary stacked (dark/light/transparent) | `png/ornate-logo-primary-*.png` |
| Horizontal (dark/light/transparent) | `png/ornate-logo-horizontal-*.png` |
| Standalone R emblem (on black / on white / transparent) | `png/ornate-emblem-*.png` |
| Emblem (black/white/monogram sizes 128–512) | `png/ornate-emblem-black-1024.png`, `ornate-monogram-*` |
| Wordmark (dark/light) | `png/ornate-wordmark-*.png` |
| Favicon (dark + light, 16→256px) | `ico/favicon.ico`, `ico/favicon-light.ico` |

## Regenerate

```bash
cd brand/ruxx/ornate
python3 build_ornate.py
```

Requires `pip install numpy resvg-py pillow`.

## Note vs. the crisp vector kit

The `../` (simple) kit is genuine vector paths that scale perfectly. This ornate
version trades that for much richer, denser artwork — the SVG embeds the emblem
as an image (up to 1024px), which is fine for web/social/print at typical sizes
but not a true infinite-zoom vector. If you need the ornate emblem as editable
vector paths, it would require retracing — happy to do that if you want.
