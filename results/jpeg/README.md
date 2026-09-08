# JPEG compression

## What this transform is

The image is saved as a JPEG file at a quality setting q and read back. JPEG throws away fine detail that the eye does not miss, more so at lower q, and it is what every messaging app and website does to a photo.

## What the levels mean

q runs from 95, nearly lossless, through 85 and 75, the usual defaults, to 60 and 40, which look visibly blocky.

## What to look for

The image does not move, so a watermark that fails here has been erased by the compression itself, not lost by misalignment. Compare the columns from left to right to see the detail vanish.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. Watermark Anything, PixelSeal and TrustMark read 1.00 at every quality down to q 40 on all 1,000 images. HiDDeN at 40 dB falls with the quality, 0.95 at q 95, 0.83 at q 85, 0.67 at q 75, 0.47 at q 60 and 0.25 at q 40, and DWT-DCT-SVD falls from 0.76 to 0.27 over the same range. Nothing moves, so rung 2 equals rung 1 and every failure here is destruction. Photos and screens split for the classical method, 0.90 against 0.62 at q 95, and the other way for HiDDeN at low quality, 0.55 against 0.39 at q 60.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.63, DWT-DCT-SVD 0.55. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.63, DWT-DCT-SVD 0.55. The gain from realignment is DWT-DCT-SVD +0.00, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.00. No cell loses more than 0.1 after the oracle.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at jpeg_40 with 0.27, HiDDeN at jpeg_40 with 0.25.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 0.99, TrustMark 0.99, DWT-DCT-SVD 0.79, HiDDeN 0.74.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly survived at 0.55, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.63.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.61, DWT-DCT-SVD 0.55, which is the practical ceiling for this family without a synchronisation watermark.
