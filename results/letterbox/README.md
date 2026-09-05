# Letterbox bars

## What this transform is

Black bars are added at the top and bottom, as when an image is placed on a screen of a different shape.

## What the levels mean

Bar height is 5 and 15 percent of the image height.

## What to look for

The image content is untouched and only moves down by the bar height, so this tests alignment along one axis and the effect of the extra black area on decoders that resize their input.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show what the transform does to the pixels. Detection rates come with the calibrated thresholds in a later milestone.
