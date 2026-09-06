# Contrast

## What this transform is

Pixel values are stretched or squeezed around the image mean by a factor f.

## What the levels mean

f is 0.9 and 1.1, a small change, and 0.75 and 1.25, a strong one.

## What to look for

Like brightness the image does not move. A factor below 1 shrinks the watermark residual along with everything else, which is the harder direction.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.