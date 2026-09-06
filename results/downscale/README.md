# Downscaling

## What this transform is

The image is shrunk to a fraction s of its size with bilinear resampling, the most common resize in browsers and apps.

## What the levels mean

s runs from 0.9, barely smaller, to 0.25, a quarter of the width and height, which is what a large photo becomes as a phone thumbnail.

## What to look for

The pixel grid changes, so the watermark both loses fine detail and lands on a different grid. The oracle realigned panel scales the image back to the original size before decoding, which separates the two effects.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.