# Shift

## What this transform is

A black margin of k pixels is added on the left and on the top, so the whole image moves k pixels right and down without any other change.

## What the levels mean

k is 1, 4, 8 and 16 pixels.

## What to look for

This is the purest alignment test. Nothing is lost, only the grid position changes. A method that fails at 1 pixel depends on the exact grid, a method that survives 16 pixels does not care about position.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. TrustMark, Watermark Anything, PixelSeal and HiDDeN do not notice a shift of 1 to 16 pixels, 0.98 to 1.00 throughout. DWT-DCT-SVD reads 0.59 at 1 px, 0.14 at 4 px and 0.00 at 8 and 16 px, because its block grid is 8 px wide, and an integer shift back restores 0.85 at every level, which is its clean ceiling on this set. The estimated realignment reaches 0.79 to 0.82.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is TrustMark 1.00, PixelSeal 1.00, Watermark Anything 1.00, HiDDeN 0.98, DWT-DCT-SVD 0.18. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.98, DWT-DCT-SVD 0.85. The gain from realignment is DWT-DCT-SVD +0.67, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.00. No cell loses more than 0.1 after the oracle.

**What we conclude.** The strongest method at rung 1 in this family is TrustMark 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at shift_8 with 0.00.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is TrustMark 1.00, PixelSeal 1.00, Watermark Anything 0.99, HiDDeN 0.90, DWT-DCT-SVD 0.65.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.62, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.98.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.97, DWT-DCT-SVD 0.80, which is the practical ceiling for this family without a synchronisation watermark.
