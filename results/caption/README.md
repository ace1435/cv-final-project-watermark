# Caption band

## What this transform is

A dark band with white text is painted over the bottom of the image, as in a meme or a story post.

## What the levels mean

The band covers 5, 10 and 20 percent of the image area.

## What to look for

The pixels under the band are gone and the rest is untouched. The valid mask excludes the band, so the realigned panel keeps the cover there.

## Files

- `samples/` holds one strip per smoke image for three images, showing the watermarked image, every level of the transform. The watermarked image is the TrustMark version at 40 dB.
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. The band destroys 5 to 20 percent of the pixels and the rest is untouched, and the four learned methods read 0.97 to 1.00 at every level. DWT-DCT-SVD reads 0.83 to 0.85, its clean ceiling, 1.00 on photos and 0.66 to 0.69 on screens. The oracle changes nothing because nothing moved, and the estimated realignment costs the classical method 0.06 to 0.12 where the registration is refined on an image with a band. PixelSeal carries a family threshold at rung 3, 34.2 against 24.4, and still reads 1.00.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.97, DWT-DCT-SVD 0.84. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.97, DWT-DCT-SVD 0.84. The gain from realignment is DWT-DCT-SVD +0.00, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.00. No cell loses more than 0.1 after the oracle. In the null shift check the pooled threshold let more than 2 percent of unwatermarked images through for some cells of this family, so those cells carry a second number at a threshold set on the 500 null images of this family alone, drawn as dotted lines with crosses and stored in the `tau_family` and `tpr_family` columns of the cell table. The pooled number stays the primary one. PixelSeal at rung 3 reads 1.00 at the family threshold 34.20 against 1.00 at the pooled threshold.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 0.99, DWT-DCT-SVD 0.90, HiDDeN 0.90.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly survived at 0.84, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.97.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.97, DWT-DCT-SVD 0.75, which is the practical ceiling for this family without a synchronisation watermark.
