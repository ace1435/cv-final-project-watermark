# Cropping

## What this transform is

A rectangle keeping a fraction of the image area, at a random position that is recorded, is cut out and everything else is discarded.

## What the levels mean

The kept area runs from 0.95, a trim of the edges, through 0.85 and 0.7 to 0.5 and 0.3, where most of the image is gone.

## What to look for

The remaining pixels are untouched, so a failure here is either missing area or lost alignment. The realigned panel pastes the crop back at its recorded position on top of the cover, and the valid mask shows where watermark pixels exist.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.