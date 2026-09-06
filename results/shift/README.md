# Shift

## What this transform is

A black margin of k pixels is added on the left and on the top, so the whole image moves k pixels right and down without any other change.

## What the levels mean

k is 1, 4, 8 and 16 pixels.

## What to look for

This is the purest alignment test. Nothing is lost, only the grid position changes. A method that fails at 1 pixel depends on the exact grid, a method that survives 16 pixels does not care about position.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.## Figures

### curves_tpr_smoke

**What you see.** One line per method, the share of the 50 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is TrustMark 1.00, PixelSeal 1.00, Watermark Anything 0.99, HiDDeN 0.92, DWT-DCT-SVD 0.17. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, DWT-DCT-SVD 0.94, HiDDeN 0.92. The gain from realignment is DWT-DCT-SVD +0.77, TrustMark +0.00, Watermark Anything +0.01, PixelSeal +0.00, HiDDeN +0.00.

**What we conclude.** The strongest method at rung 1 in this family is TrustMark 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at shift_8 with 0.00.

### curves_bitacc_smoke

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is PixelSeal 1.00, TrustMark 0.99, Watermark Anything 0.98, HiDDeN 0.89, DWT-DCT-SVD 0.66.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.71, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 0.99, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.92.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.92, DWT-DCT-SVD 0.88, which is the practical ceiling for this family without a synchronisation watermark.
