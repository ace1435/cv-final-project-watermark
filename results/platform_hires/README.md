# Platform profiles on a high resolution original

## What this transform is

The same five platform profiles as in `../platform/`, applied to a 2048 px original. Because our
benchmark images are 1024 px wide, the original is simulated by enlarging the watermarked image
by two with bilinear resampling. The platform then shrinks it to its long side limit with area
resampling and saves it as JPEG at its quality, exactly as the plain profile does.

## What the levels mean

There is one condition per platform. The net scale from the 1024 px image to the output is
1.25 for telegram_std, 1.5625 for whatsapp_android, 1.055 for instagram, and 2.0 for twitter and
facebook, whose limits are 2048 px. The JPEG qualities are the same as in `../platform/`.

## What to look for

These conditions combine two resamplings with the JPEG, so they test alignment and compression
together. Compare with `../platform/` to see how much the resize adds on top of the JPEG, and
with `../upscale/` to see how much the JPEG adds on top of the enlargement.

## Files

- `samples/` holds one strip per smoke image for three images.
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. See `../platform/README.md` for why both families exist. With a 2048 px original the platform resize adds an alignment loss to the JPEG. HiDDeN falls to 0.09 on twitter and 0.08 on facebook, whose net scale is 2, and to 0.17 on whatsapp_android at 1.56, and the oracle restores 0.95, 0.94 and 0.86, so the enlargement and not the JPEG is the loss. Instagram at a net scale of 1.055 stays at 0.47 to 0.48 at both rungs, the JPEG at q 72 dominates there. DWT-DCT-SVD reads 0.00 to 0.01 as received and 0.50 to 0.77 after the oracle. The three modern methods read 1.00 on all five.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.26, DWT-DCT-SVD 0.01. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.80, DWT-DCT-SVD 0.67. The gain from realignment is DWT-DCT-SVD +0.66, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.54. No cell loses more than 0.1 after the oracle.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at platform_hires_twitter with 0.00, HiDDeN at platform_hires_facebook with 0.08.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.62, DWT-DCT-SVD 0.52.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.64, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly recoverable at 0.53.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.79, DWT-DCT-SVD 0.64, which is the practical ceiling for this family without a synchronisation watermark.
