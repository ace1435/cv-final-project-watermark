# Contrast

## What this transform is

Pixel values are stretched or squeezed around the image mean by a factor f.

## What the levels mean

f is 0.9 and 1.1, a small change, and 0.75 and 1.25, a strong one.

## What to look for

Like brightness the image does not move. A factor below 1 shrinks the watermark residual along with everything else, which is the harder direction.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show what the transform does to the pixels. Detection rates come with the calibrated thresholds in a later milestone.
