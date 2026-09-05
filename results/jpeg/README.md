# JPEG compression

## What this transform is

The image is saved as a JPEG file at a quality setting q and read back. JPEG throws away fine detail that the eye does not miss, more so at lower q, and it is what every messaging app and website does to a photo.

## What the levels mean

q runs from 95, nearly lossless, through 85 and 75, the usual defaults, to 60 and 40, which look visibly blocky.

## What to look for

The image does not move, so a watermark that fails here has been erased by the compression itself, not lost by misalignment. Compare the columns from left to right to see the detail vanish.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show what the transform does to the pixels. Detection rates come with the calibrated thresholds in a later milestone.
