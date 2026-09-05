# Shift

## What this transform is

A black margin of k pixels is added on the left and on the top, so the whole image moves k pixels right and down without any other change.

## What the levels mean

k is 1, 4, 8 and 16 pixels.

## What to look for

This is the purest alignment test. Nothing is lost, only the grid position changes. A method that fails at 1 pixel depends on the exact grid, a method that survives 16 pixels does not care about position.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show what the transform does to the pixels. Detection rates come with the calibrated thresholds in a later milestone.
