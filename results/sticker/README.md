# Sticker

## What this transform is

An opaque round sticker with a face is pasted at a random recorded position, as in a photo sharing app.

## What the levels mean

The sticker covers 5, 10 and 20 percent of the image area.

## What to look for

Like the caption this destroys the pixels under it and leaves the rest untouched, but the hole sits in the middle of the content rather than on an edge.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.