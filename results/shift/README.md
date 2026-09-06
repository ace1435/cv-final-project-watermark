# Shift

## What this transform is

A black margin of k pixels is added on the left and on the top, so the whole image moves k pixels right and down without any other change.

## What the levels mean

k is 1, 4, 8 and 16 pixels.

## What to look for

This is the purest alignment test. Nothing is lost, only the grid position changes. A method that fails at 1 pixel depends on the exact grid, a method that survives 16 pixels does not care about position.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.