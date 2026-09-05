# Caption band

## What this transform is

A dark band with white text is painted over the bottom of the image, as in a meme or a story post.

## What the levels mean

The band covers 5, 10 and 20 percent of the image area.

## What to look for

The pixels under the band are gone and the rest is untouched. The valid mask excludes the band, so the realigned panel keeps the cover there.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show what the transform does to the pixels. Detection rates come with the calibrated thresholds in a later milestone.
