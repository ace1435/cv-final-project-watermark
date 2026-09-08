# Downscaling

## What this transform is

The image is shrunk to a fraction s of its size with bilinear resampling, the most common resize in browsers and apps.

## What the levels mean

s runs from 0.9, barely smaller, to 0.25, a quarter of the width and height, which is what a large photo becomes as a phone thumbnail.

## What to look for

The pixel grid changes, so the watermark both loses fine detail and lands on a different grid. The oracle realigned panel scales the image back to the original size before decoding, which separates the two effects.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. The three modern methods read 1.00 at every scale down to a quarter as received. HiDDeN holds 0.98 down to 0.75, reads 0.83 at half size and collapses to 0.10 at a third and 0.03 at a quarter, and the oracle lifts those two only to 0.38 and 0.12, so the loss is destruction of the fine detail that carries its mark. DWT-DCT-SVD reads 0.01 to 0.02 at every scale as received, because any resampling moves its block grid, and the oracle restores it to 0.80 at 0.9 and 0.66 at a quarter, the estimated realignment to 0.80 and 0.49, which is the one place where a sub pixel registration error costs the classical method.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.58, DWT-DCT-SVD 0.01. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, DWT-DCT-SVD 0.74, HiDDeN 0.64. The gain from realignment is DWT-DCT-SVD +0.73, TrustMark +0.00, Watermark Anything +0.00, PixelSeal -0.00, HiDDeN +0.06. No cell loses more than 0.1 after the oracle.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at downscale_0.9 with 0.01, HiDDeN at downscale_0.25 with 0.03.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 0.98, HiDDeN 0.72, DWT-DCT-SVD 0.51.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.67, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.58.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, DWT-DCT-SVD 0.68, HiDDeN 0.64, which is the practical ceiling for this family without a synchronisation watermark.
