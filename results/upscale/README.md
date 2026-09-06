# Upscaling

## What this transform is

The image is enlarged by a factor s with bilinear resampling, which happens when a small image is shown on a high resolution screen.

## What the levels mean

s is 1.25, 1.5 and 2.0, the last being what a retina display does to an image at its natural size.

## What to look for

No detail is lost, but every decoder that resizes its input internally now sees the watermark at a different scale. The realigned panel shrinks the image back to the original grid.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.