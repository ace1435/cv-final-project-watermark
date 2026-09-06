# Real browser screenshots

## What this transform is

The watermarked image is placed on a plain web page and rendered by a real headless Chromium
browser under a chosen zoom level and screen density, then the whole viewport is captured as a
PNG at device pixels and the image region is cut out at its recorded device box. This is what
happens to pixels when a person screenshots an image in a browser, and it is the family the
project was built around. Playwright cannot set the browser zoom directly, so zoom Z on a screen
with density d is emulated as a viewport divided by Z with a device scale factor of d times Z,
which is how Chromium implements zoom internally.

## What the conditions mean

| Condition | Zoom | Density | Effective scale | Everyday case |
|---|---|---|---|---|
| desktop_100 | 100 percent | 1 | 1.00 | control, bit exact on a PNG |
| desktop_90, 110, 125, 150 | 90 to 150 percent | 1 | 0.9 to 1.5 | browser zoom presets |
| win_125, win_150 | 100 percent | 1.25, 1.5 | 1.25, 1.5 | Windows display scaling |
| win_125_zoom_110 | 110 percent | 1.25 | 1.375 | scaling and zoom together, half pixel phase |
| mac_retina | 100 percent | 2 | 2.0 | Mac laptop screen |
| phone_pixel7 | fit to 412 px | 2.625 | 1.056 | Android phone, half pixel phase |
| phone_iphone15pro | fit to 393 px | 3 | 1.151 | iPhone |
| fit_75, fit_50 | 100 percent | 1 | 0.75, 0.5 | image shown at part of its size, 0.5 crosses the browser mip level |
| partial_80 | 100 percent | 1 | 1.0 plus a random 80 percent window | a partial screenshot |
| desktop_110_jpeg | 110 percent | 1 | 1.1 plus JPEG q80 | the browser saves the screenshot as JPEG |

Every condition records the exact scale, the device box, the sub pixel phase of the image
corner and the Chromium build, so the oracle inverse can map the result back to the original
grid. A reference pattern is rendered at the start of every run and its checksum compared with
`configs/screenshots.yaml`, so a different browser build on another machine is noticed.

## What to look for

The strips show the same watermarked image under every condition with its output size. Most
conditions only resample, so the image looks the same and only its pixel grid changes. The
partial screenshot and the JPEG variant are the two that lose content. The calibration table in
`../calibration/` says how close a plain resize comes to the real browser render.

## Files

- `samples/` holds two strips per smoke image for three images, the first with the watermarked
  image and eight conditions, the second with the remaining conditions and the partial
  screenshot put back into the original grid by the oracle inverse with its valid mask.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show that the browser reproduces the image faithfully at every scale and that every condition is invertible. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.