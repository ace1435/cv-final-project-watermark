# Gamma

## What this transform is

Pixel values are raised to a power g after scaling to the range 0 to 1, which changes mid tones while leaving black and white in place.

## What the levels mean

g is 0.9 and 1.1, a small change, and 0.75 and 1.25, a strong one.

## What to look for

A non linear change of tone. It affects dark and bright regions differently, so a watermark that hides in one of them may be scaled more than the other.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show what the transform does to the pixels. Detection rates come with the calibrated thresholds in a later milestone.
