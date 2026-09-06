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
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

See `../platform/README.md` for why both families exist. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.

## Figures

### curves_tpr_smoke

**What you see.** One line per method, the share of the 50 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.24, DWT-DCT-SVD 0.00. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.73, DWT-DCT-SVD 0.72. The gain from realignment is DWT-DCT-SVD +0.72, TrustMark +0.00, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.50.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at platform_hires_telegram_std with 0.00, HiDDeN at platform_hires_twitter with 0.06.

### curves_bitacc_smoke

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 0.99, HiDDeN 0.62, DWT-DCT-SVD 0.53.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.69, TrustMark mostly survived at 1.00, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly recoverable at 0.49.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.72, DWT-DCT-SVD 0.69, which is the practical ceiling for this family without a synchronisation watermark.
