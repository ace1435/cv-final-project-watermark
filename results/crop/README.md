# Cropping

## What this transform is

A rectangle keeping a fraction of the image area, at a random position that is recorded, is cut out and everything else is discarded.

## What the levels mean

The kept area runs from 0.95, a trim of the edges, through 0.85 and 0.7 to 0.5 and 0.3, where most of the image is gone.

## What to look for

The remaining pixels are untouched, so a failure here is either missing area or lost alignment. The realigned panel pastes the crop back at its recorded position on top of the cover, and the valid mask shows where watermark pixels exist.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform, the strongest level put back into the original grid by the oracle inverse, and the valid mask. The watermarked image is the TrustMark version at 40 dB.
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. Watermark Anything and PixelSeal read 1.00 down to half the area and 0.96 at 0.3. TrustMark stays at 1.00 down to 0.7, then reads 0.68 at 0.5 and 0.09 at 0.3, and the oracle restores both to 1.00 and the estimate to 1.00 and 0.99, so the mark is intact and the decoder only sees it stretched. HiDDeN reads 0.95 to 0.98 as received and lower after the oracle, 0.71 at 0.3, because the received crop alone carries the mark and pasting it onto the cover dilutes it for a decoder that reads the whole canvas. DWT-DCT-SVD reads 0.01 at every crop as received, 0.85 to 0.61 after the oracle down to half the area and 0.14 at 0.3 where too little area is left. HiDDeN carries a family threshold at rung 1 here, 43.8 against 36.3, and reads 0.94 to 0.97 at it.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is PixelSeal 0.99, Watermark Anything 0.99, HiDDeN 0.97, TrustMark 0.76, DWT-DCT-SVD 0.01. After the oracle it is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.90, DWT-DCT-SVD 0.65. The gain from realignment is DWT-DCT-SVD +0.64, TrustMark +0.24, Watermark Anything +0.01, PixelSeal +0.01, HiDDeN -0.07. Cells that lose more than 0.1 after the oracle are HiDDeN at crop_0.3 from 0.95 to 0.71. These are crops decoded by a method that reads the full canvas, where the received crop alone carries the mark and the oracle pastes it onto a canvas of unwatermarked cover pixels that the decoder averages in. In the null shift check the pooled threshold let more than 2 percent of unwatermarked images through for some cells of this family, so those cells carry a second number at a threshold set on the 500 null images of this family alone, drawn as dotted lines with crosses and stored in the `tau_family` and `tpr_family` columns of the cell table. The pooled number stays the primary one. HiDDeN at rung 1 reads 0.96 at the family threshold 43.84 against 0.97 at the pooled threshold.

**What we conclude.** The strongest method at rung 1 in this family is PixelSeal 0.99. Cells below one half at rung 1 are DWT-DCT-SVD at crop_0.95 with 0.01, TrustMark at crop_0.3 with 0.09.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 0.98, PixelSeal 0.96, HiDDeN 0.89, TrustMark 0.81, DWT-DCT-SVD 0.52.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.62, TrustMark mostly survived at 0.76, Watermark Anything mostly survived at 0.99, PixelSeal mostly survived at 0.99, HiDDeN mostly survived at 0.97.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.90, DWT-DCT-SVD 0.63, which is the practical ceiling for this family without a synchronisation watermark.
