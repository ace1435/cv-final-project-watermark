# Small rotation

## What this transform is

The image is rotated about its centre and the corners that fall outside the frame are filled with the original cover pixels.

## What the levels mean

The angle is 1, 3 and 10 degrees.

## What to look for

Even one degree moves the outer pixels by many positions, so this is a hard alignment test. The realigned panel rotates the image back, and the valid mask shows the corners that were lost.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.