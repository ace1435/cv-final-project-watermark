# Cropping

## What this transform is

A rectangle keeping a fraction of the image area, at a random position that is recorded, is cut out and everything else is discarded.

## What the levels mean

The kept area runs from 0.95, a trim of the edges, through 0.85 and 0.7 to 0.5 and 0.3, where most of the image is gone.

## What to look for

The remaining pixels are untouched, so a failure here is either missing area or lost alignment. The realigned panel pastes the crop back at its recorded position on top of the cover, and the valid mask shows where watermark pixels exist.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show what the transform does to the pixels. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.

## Figures

### curves_tpr_smoke

**What you see.** One line per method, the share of the 50 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 0.99, PixelSeal 0.99, HiDDeN 0.91, TrustMark 0.76, DWT-DCT-SVD 0.00. After the oracle it is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.84, DWT-DCT-SVD 0.73. The gain from realignment is DWT-DCT-SVD +0.73, TrustMark +0.24, Watermark Anything +0.01, PixelSeal +0.01, HiDDeN -0.07.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 0.99. Cells below one half at rung 1 are DWT-DCT-SVD at crop_0.95 with 0.00, TrustMark at crop_0.3 with 0.08.

### curves_bitacc_smoke

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 0.98, PixelSeal 0.97, HiDDeN 0.88, TrustMark 0.81, DWT-DCT-SVD 0.52.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.70, TrustMark mostly survived at 0.76, Watermark Anything mostly survived at 0.99, PixelSeal mostly survived at 0.99, HiDDeN mostly survived at 0.91.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.83, DWT-DCT-SVD 0.70, which is the practical ceiling for this family without a synchronisation watermark.
