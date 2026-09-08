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
- `cells_full.csv` holds every number behind the full run figures, one row per condition, method and domain over the 1,000 test images, with the TPR at each rung and its Wilson bounds, the bit accuracy, the failure label shares, the median registration error and, where the null shift check flagged the family, the per family threshold and the TPR at it in the `tau_family` and `tpr_family` columns. `cells_smoke.csv` is the same table for the 50 image smoke subset and adds the zero fill ablation. The figures `curves_tpr_full`, `curves_bitacc_full` and `breakdown_full` are explained under Figures below, and the same figures with the tag `smoke` are the smoke subset versions.

## What can be concluded

The strips show what the transform does to the pixels. The numbers below are the full run, 1,000 images at the 40 dB point, TPR at 1 percent FPR read against the thresholds in `../summary/thresholds.csv` and rung 3 against `../summary/thresholds_rung3.csv`, every cell with its Wilson bounds in `cells_full.csv`. Watermark Anything and PixelSeal read 0.99 to 1.00 on every chain. TrustMark reads 1.00 on four and 0.93 on the phone to instagram chain, whose centre crop is the loss, restored to 1.00 by the oracle. HiDDeN reads 0.96 on the double screenshot and 0.44 to 0.69 on the rest, with the two chains that end in a platform JPEG at 0.44 and 0.48, and the oracle helps only where a screenshot enlarged the image. DWT-DCT-SVD reads 0.01 on every chain with a screenshot and 0.50 on the telegram caption twitter chain, which never resamples, and the oracle restores 0.38 to 0.78.

## Figures

### curves_tpr_full

**What you see.** One line per method, the share of the 1,000 images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.

**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.

**What it means.** Mean TPR over the levels at rung 1 is PixelSeal 1.00, Watermark Anything 1.00, TrustMark 0.99, HiDDeN 0.64, DWT-DCT-SVD 0.11. After the oracle it is Watermark Anything 1.00, TrustMark 1.00, PixelSeal 1.00, HiDDeN 0.63, DWT-DCT-SVD 0.55. The gain from realignment is DWT-DCT-SVD +0.44, TrustMark +0.01, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN -0.01. Cells that lose more than 0.1 after the oracle are HiDDeN at chain_phone_instagram from 0.48 to 0.31, HiDDeN at chain_crop_jpeg_screenshot from 0.69 to 0.53. These are crops decoded by a method that reads the full canvas, where the received crop alone carries the mark and the oracle pastes it onto a canvas of unwatermarked cover pixels that the decoder averages in.

**What we conclude.** The strongest method at rung 1 in this family is PixelSeal 1.00. Cells below one half at rung 1 are DWT-DCT-SVD at chain_phone_instagram with 0.01, HiDDeN at chain_desktop_whatsapp with 0.44.

### curves_bitacc_full

**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.

**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.

**What it means.** Mean bit accuracy over the levels at rung 1 is PixelSeal 0.99, Watermark Anything 0.99, TrustMark 0.96, HiDDeN 0.73, DWT-DCT-SVD 0.57.

**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.

### breakdown_full

**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.

**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.

**What it means.** DWT-DCT-SVD mostly destroyed at 0.45, TrustMark mostly survived at 0.99, Watermark Anything mostly survived at 1.00, PixelSeal mostly survived at 1.00, HiDDeN mostly survived at 0.64.

**What we conclude.** After the estimated realignment the mean TPR is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.60, DWT-DCT-SVD 0.54, which is the practical ceiling for this family without a synchronisation watermark.
