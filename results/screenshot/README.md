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

The strips show that the browser reproduces the image faithfully at every scale and that every condition is invertible. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.## Figures

### curves_tpr_smoke

**What you see.** One line per method, the share of the 50 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.77, DWT-DCT-SVD 0.06. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.88, DWT-DCT-SVD 0.88. The gain from realignment is DWT-DCT-SVD +0.82, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.11.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at desktop_90 with 0.00, HiDDeN at mac_retina with 0.14.

### curves_bitacc_smoke

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 0.99, HiDDeN 0.79, DWT-DCT-SVD 0.56.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.80, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.77.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.89, DWT-DCT-SVD 0.87, which is the practical ceiling for this family without a synchronisation watermark.
