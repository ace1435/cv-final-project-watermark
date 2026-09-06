# Platform profiles

## What this transform is

Each profile imitates what a sharing platform does to a posted image, resize to a maximum long side and recompress as JPEG at a fixed quality with 4:2:0 chroma subsampling. Our images are at most 1024 pixels wide, below every platform limit, so only the JPEG step applies.

## What the levels mean

telegram_std is 1280 pixels and q 80, twitter 2048 and q 85, both verified from source or measurement. whatsapp_android is 1600 and q 75, instagram 1080 and q 72, facebook 2048 and q 80, all three estimates from published forensics. For the three estimates the smoke subset also runs q 70, 75, 80 and 85 as a sensitivity band, in `sweep_smoke.csv`.

## Why two platform families exist

Our benchmark images are 1024 px wide, so the resize step of every profile is idle here and
these five conditions measure the JPEG step alone. Real users often post larger originals, and
then the platform shrinks them. The `platform_hires` family in `../platform_hires/` simulates
that case by first enlarging the image by two with bilinear resampling, as if a 2048 px original
had been watermarked, then applying the platform resize to its long side limit and its JPEG.
Its net scale is 1.25 for Telegram, 1.5625 for WhatsApp, 1.055 for Instagram and 2.0 for
Twitter and Facebook, and its inverse is composed from the two resizes like a chain. Both
families run on the smoke subset and on the full set.

## What to look for

Nothing moves, so these are pure compression tests at realistic settings. Read the sweep to see how sensitive each method is to the exact quality a platform uses.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.## Figures

### curves_tpr_smoke

**What you see.** One line per method, the share of the 50 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.68, DWT-DCT-SVD 0.66. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.68, DWT-DCT-SVD 0.66. The gain from realignment is DWT-DCT-SVD +0.00, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.00.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00.

### curves_bitacc_smoke

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 0.99, DWT-DCT-SVD 0.89, HiDDeN 0.76.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly survived at 0.66, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.68.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.69, DWT-DCT-SVD 0.66, which is the practical ceiling for this family without a synchronisation watermark.
