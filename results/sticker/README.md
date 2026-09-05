# Sticker

## What this transform is

An opaque round sticker with a face is pasted at a random recorded position, as in a photo sharing app.

## What the levels mean

The sticker covers 5, 10 and 20 percent of the image area.

## What to look for

Like the caption this destroys the pixels under it and leaves the rest untouched, but the hole sits in the middle of the content rather than on an edge.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show what the transform does to the pixels. Detection rates come with the calibrated thresholds in a later milestone.
