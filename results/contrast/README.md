# Contrast

## What this transform is

Pixel values are stretched or squeezed around the image mean by a factor f.

## What the levels mean

f is 0.9 and 1.1, a small change, and 0.75 and 1.25, a strong one.

## What to look for

Like brightness the image does not move. A factor below 1 shrinks the watermark residual along with everything else, which is the harder direction.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. Watermark Anything, PixelSeal and TrustMark read 1.00 at every level. HiDDeN reads 0.94 to 0.98. DWT-DCT-SVD reads 0.30 to 0.53, with 0.09 on photos at 0.75 against 0.51 on screens. The family threshold for the classical method is 11.15 against 10.00 and moves its mean from 0.41 to 0.39.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.97, DWT-DCT-SVD 0.41. After the oracle it is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.97, DWT-DCT-SVD 0.41. The gain from realignment is DWT-DCT-SVD +0.00, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.00. No cell loses more than 0.1 after the oracle. In the null shift check the pooled threshold let more than 2 percent of unwatermarked images through for some cells of this family, so those cells carry a second number at a threshold set on the 500 null images of this family alone, drawn as dotted lines with crosses and stored in the `tau_family` and `tpr_family` columns of the cell table. The pooled number stays the primary one. DWT-DCT-SVD at rung 1 reads 0.39 at the family threshold 11.15 against 0.41 at the pooled threshold. DWT-DCT-SVD at rung 2 reads 0.39 at the family threshold 11.15 against 0.41 at the pooled threshold. DWT-DCT-SVD at rung 3 reads 0.39 at the family threshold 11.28 against 0.41 at the pooled threshold.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at contrast_0.75 with 0.30.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, TrustMark 0.99, PixelSeal 0.98, HiDDeN 0.87, DWT-DCT-SVD 0.70.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly destroyed at 0.59, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.97.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.96, DWT-DCT-SVD 0.41, which is the practical ceiling for this family without a synchronisation watermark.
