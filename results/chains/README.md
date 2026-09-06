# Chains of sharing actions

## What this transform is

Five named sequences of actions that imitate how an image actually travels between people. Each
step records its parameters and the chain composes them, so the oracle inverse of the whole chain
still exists.

| Chain | Steps |
|---|---|
| chain_desktop_whatsapp | Windows 125 percent screenshot, then the WhatsApp Android profile |
| chain_phone_instagram | Pixel 7 screenshot, then a centre crop to 4 by 5, then the Instagram profile |
| chain_crop_jpeg_screenshot | crop keeping 70 percent, JPEG q85, then a 110 percent desktop screenshot |
| chain_double_screenshot | a 110 percent screenshot, then a 90 percent screenshot of that |
| chain_telegram_caption_twitter | the Telegram profile, then a 10 percent caption band, then the Twitter profile |

## What to look for

Chains stack two or three losses. Compare each chain with its single actions in the other
folders to see whether the losses add up or whether one step dominates. The strip ends with the
phone to Instagram chain put back into the original grid, where the valid mask shows the area
lost to the centre crop.

## Files

- `samples/` holds one strip per smoke image for three images.
- `cells_smoke.csv` holds every number behind the figures, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, the bit accuracy, the zero fill ablation, the failure label shares and the median registration error. The figures `curves_tpr_smoke`, `curves_bitacc_smoke` and `breakdown` are explained under Figures below.

## What can be concluded

The strips show the pixels after each chain and that the composed inverse works. The detection rates on the 50 smoke images at the three rungs are in the Figures section below and in `cells_smoke.csv`, read against the thresholds in `../summary/thresholds.csv`. The full 1,000 image run comes with the next milestone.

## Figures

### curves_tpr_smoke

**What you see.** One line per method, the share of the 50 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 0.98, HiDDeN 0.61, DWT-DCT-SVD 0.11. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, DWT-DCT-SVD 0.60, HiDDeN 0.59. The gain from realignment is DWT-DCT-SVD +0.50, TrustMark +0.02, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN -0.02.

**What we conclude.** The strongest method at rung 1 in this family is Watermark Anything 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at chain_desktop_whatsapp with 0.00, HiDDeN at chain_desktop_whatsapp with 0.40.

### curves_bitacc_smoke

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is PixelSeal 0.99, Watermark Anything 0.98, TrustMark 0.96, HiDDeN 0.74, DWT-DCT-SVD 0.59.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly recoverable at 0.48, TrustMark mostly survived at 0.98, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.61.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, DWT-DCT-SVD 0.59, HiDDeN 0.55, which is the practical ceiling for this family without a synchronisation watermark.
