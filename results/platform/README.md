# Platform profiles

## What this transform is

Each profile imitates what a sharing platform does to a posted image, resize to a maximum long side and recompress as JPEG at a fixed quality with 4:2:0 chroma subsampling. Our images are at most 1024 pixels wide, below every platform limit, so only the JPEG step applies.

## What the levels mean

telegram_std is 1280 pixels and q 80, twitter 2048 and q 85, both verified from source or measurement. whatsapp_android is 1600 and q 75, instagram 1080 and q 72, facebook 2048 and q 80, all three estimates from published forensics. For the three estimates the smoke subset also runs q 70, 75, 80 and 85 as a sensitivity band, in `sweep_smoke.csv`.

## What to look for

Nothing moves, so these are pure compression tests at realistic settings. Read the sweep to see how sensitive each method is to the exact quality a platform uses.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells.csv`, `curves_tpr` and `breakdown` figures arrive with the detection milestone.

## What can be concluded

Nothing yet. The strips show what the transform does to the pixels. Detection rates come with the calibrated thresholds in a later milestone.
