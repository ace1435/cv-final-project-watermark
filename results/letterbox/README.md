# Letterbox bars

## What this transform is

Black bars are added at the top and bottom, as when an image is placed on a screen of a different shape.

## What the levels mean

Bar height is 5 and 15 percent of the image height.

## What to look for

The image content is untouched and only moves down by the bar height, so this tests alignment along one axis and the effect of the extra black area on decoders that resize their input.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. The 5 percent bar costs TrustMark 0.02 and the 15 percent bar drops it to 0.12, restored to 1.00 by both realignments, because its decoder squeezes the taller image into its fixed square. Watermark Anything, PixelSeal and HiDDeN read 0.96 to 1.00. DWT-DCT-SVD reads 0.37 and 0.34, the bar height lands on a multiple of its grid for some images, and 0.85 after the oracle.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 0.99, HiDDeN 0.97, TrustMark 0.55, DWT-DCT-SVD 0.36. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.98, DWT-DCT-SVD 0.85. The gain from realignment is DWT-DCT-SVD +0.50, TrustMark +0.45, Watermark Anything +0.00, PixelSeal +0.01, HiDDeN +0.01. No cell loses more than 0.1 after the oracle.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at letterbox_0.15 with 0.34, TrustMark at letterbox_0.15 with 0.12.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 0.97, PixelSeal 0.96, HiDDeN 0.89, DWT-DCT-SVD 0.73, TrustMark 0.70.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.45, TrustMark mostly survived at 0.55, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 0.99, HiDDeN mostly survived at 0.97.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.97, DWT-DCT-SVD 0.81, which is the practical ceiling for this family without a synchronisation watermark.
