# JPEG compression

## What this transform is

The image is saved as a JPEG file at a quality setting q and read back. JPEG throws away fine detail that the eye does not miss, more so at lower q, and it is what every messaging app and website does to a photo.

## What the levels mean

q runs from 95, nearly lossless, through 85 and 75, the usual defaults, to 60 and 40, which look visibly blocky.

## What to look for

The image does not move, so a watermark that fails here has been erased by the compression itself, not lost by misalignment. Compare the columns from left to right to see the detail vanish.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.

## Figures

### curves_tpr_smoke

**What you see.** One line per method, the share of the 50 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, DWT-DCT-SVD 0.60, HiDDeN 0.59. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, DWT-DCT-SVD 0.60, HiDDeN 0.59. The gain from realignment is DWT-DCT-SVD +0.00, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.00.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at jpeg_40 with 0.28, HiDDeN at jpeg_40 with 0.24.

### curves_bitacc_smoke

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 0.99, TrustMark 0.99, DWT-DCT-SVD 0.83, HiDDeN 0.74.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly survived at 0.60, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.59.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, DWT-DCT-SVD 0.60, HiDDeN 0.58, which is the practical ceiling for this family without a synchronisation watermark.
