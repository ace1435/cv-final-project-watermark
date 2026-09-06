# JPEG compression

## What this transform is

The image is saved as a JPEG file at a quality setting q and read back. JPEG throws away fine detail that the eye does not miss, more so at lower q, and it is what every messaging app and website does to a photo.

## What the levels mean

q runs from 95, nearly lossless, through 85 and 75, the usual defaults, to 60 and 40, which look visibly blocky.

## What to look for

The image does not move, so a watermark that fails here has been erased by the compression itself, not lost by misalignment. Compare the columns from left to right to see the detail vanish.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.