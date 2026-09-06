# Summary results

This folder holds the numbers that describe the five watermarking methods before any sharing
action is applied, the detection thresholds from the 5,000 image null set, and the summary of
every detection cell. The quality and cell numbers come from the 50 image smoke subset, the
thresholds from the null set decoded on the VM, each with one command, see the top level README.

## What quality matching means

Every method has a knob that trades visibility against robustness. Out of the box the methods
sit at very different visibility levels, from about 33 dB PSNR for HiDDeN to about 47 dB for
PixelSeal, so comparing their robustness directly would be unfair. PSNR is peak signal to noise
ratio in decibels between the cover image and the watermarked image, higher means less visible,
and 40 dB is a common target where the change is hard to see. For each image and each method
we search the knob so that the watermarked image lands at 40 dB, then measure everything at both
the native setting and the matched setting.

For the four learned methods the residual scales linearly with the knob, so one closed form step
`alpha = 10^((psnr_native - 40) / 20)` followed by one remeasure lands within 0.1 dB. For the
classical DWT-DCT-SVD method the knob is a quantisation step, which cannot be scaled linearly,
so the step is found by a binary search between 24 and 250. Steps below 24 are finer than the
uint8 rounding noise of the colour conversion and stop decoding, so the search never goes below
24 and a few photos stay below 40 dB.

## Files

| File | Content |
|---|---|
| `quality_smoke.csv` | One row per method, domain and operating point with the mean, sd and min of PSNR, SSIM, LPIPS and DISTS, the strength used, bit accuracy, and detection rates |
| `quality_smoke_per_image.csv` | The same quantities for every image, for distributions and for finding outliers |
| `timing_smoke_pc.csv` | Mean seconds per image for embedding, decoding and the strength search on the Windows PC with CPU only |
| `timing_smoke_vm.csv` | The same on the VM with an NVIDIA A10 |
| `samples/` | For three smoke images per method, a strip showing the cover, the native watermarked image, its residual amplified ten times, the matched watermarked image and its residual |
| `../tables/quality_smoke.tex` | The pooled rows as a LaTeX table |
| `thresholds.csv` | One row per method with the score threshold that 1 percent of the 5,000 null images exceed, the realised false positive rate pooled and for photos and screens, and the analytic threshold on hard bits with its realised rate |
| `null_scores.svg`, `null_scores.png` | The distribution of null scores per method, photos and screens in two colours, with the threshold |
| `thresholds_rung3.csv` | The threshold for rung 3, from 500 null images pushed through 17 representative conditions and the estimated realignment |
| `null_shift.csv` | The realised false positive rate per condition, method and rung on those transformed null images, with a flag above 2 percent |
| `cells_smoke.csv` | Every detection cell, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, bit accuracy, the zero fill ablation, the failure label shares and the median registration error |
| `heatmap_rung1_smoke`, `heatmap_rung2_smoke`, `heatmap_rung3_smoke`, `heatmap_diff_smoke` | The TPR of every method under every condition at each rung, and the rung 2 minus rung 1 difference, as SVG and PNG |

## How to read the columns

- `point` is `native` for the setting the authors ship or `matched` for our 40 dB setting.
- `strength_mean`, `strength_min` and `strength_max` describe the knob values the search chose.
- `psnr_mean` and `psnr_sd` should read close to 40.0 and close to 0 in the matched rows.
- `ssim_mean` is structural similarity, 1 means identical. `lpips_mean` and `dists_mean` are
  learned perceptual distances, 0 means identical, computed on the residual between cover and
  watermarked image.
- `bitacc_mean` is the fraction of message bits decoded correctly from the watermarked image
  with no sharing action applied. `bitacc_min` is the worst image.
- `tpr_analytic` is the fraction of watermarked images whose number of correct bits reaches the
  binomial threshold `tau_1pct`, the smallest count with a chance below 1 percent under random
  bits. This was the provisional detector before the empirical thresholds in `thresholds.csv`,
  which every cell table uses now. `clean_fpr_analytic` applies the same threshold to the
  unwatermarked image and should be 0.
- In `thresholds.csv`, `tau_1pct` is the empirical threshold on the continuous score, the
  matched filter between the decoder logits and the message, `fpr_pooled` should read 0.0100
  and `fpr_photo` and `fpr_screen` show how the two domains split it. `null_score_mean` and
  `null_score_sd` describe the null distribution and `null_bitacc_mean` should sit at 0.50.
- In `cells_smoke.csv`, `tpr_r1`, `tpr_r2` and `tpr_r3` are the detection rates at the three
  rungs with `_low` and `_high` Wilson bounds, `bitacc_r1` to `bitacc_r3` the mean bit accuracy,
  `tpr_r2_zero_fill` the oracle rung with black instead of cover pixels, `label_*` the share of
  images per failure label, `valid_fraction` the share of original pixels still present after
  the oracle realignment, `corner_error_median` the registration error of rung 3 in pixels and
  `reg_failed` the share of images where the matcher found no registration.
- `ecc_ok_rate` exists only for TrustMark and tells whether the 61 bit payload survives the
  error correcting code. `pixel_score_mean` exists only for Watermark Anything and is the
  fraction of pixels its detector flags, with `clean_pixel_score_mean` the same on the cover.

## What to look for and what can be concluded

- TrustMark, Watermark Anything and PixelSeal decode every smoke image at 40 dB with bit
  accuracy above 0.99 and analytic TPR of 1.00, so the matching does not hurt them.
- HiDDeN ships at 33 dB. Bringing it to 40 dB divides its residual by about two and its bit
  accuracy drops from 0.96 to 0.89, so for HiDDeN the matching hurts and its robustness rows
  later must be read with that in mind.
- DWT-DCT-SVD cannot reach 40 dB on photos while still decoding, its matched photos sit at
  38.0 dB on average. On screens it fails at its default step on many images because its
  modulation clips in saturated white regions, and a larger step recovers most but not all of
  them. This is the first sign that the screen domain behaves differently.
- PixelSeal is the least visible method at its native setting and needs its knob raised from
  0.2 to about 0.5 to reach 40 dB.
- Timing on the A10 is well under 0.1 s per image for the learned methods, so the full run is
  not limited by embedding or decoding. DWT-DCT-SVD runs on the CPU and its strength search
  costs about 2.4 s per image on the VM.

## What cannot be concluded yet

Nothing here says anything about robustness. These are clean image numbers that define the
operating points. The sharing actions, screenshots and calibrated thresholds come in the
following milestones.

## Figures

### heatmap_rung1_smoke, heatmap_rung2_smoke, heatmap_rung3_smoke

**What you see.** Methods as rows, every condition as a column, each cell the share of images detected at 1 percent FPR, dark is low and bright is high. Rung 1 is the image as received, rung 2 after the oracle puts it back into place, rung 3 after the estimated realignment.

**How to read it.** Scan a row to see where a method breaks. Scan a column to see which methods a condition breaks. Compare the same cell across the three maps to see whether the failure is alignment or destruction.

**What it means.** Mean TPR over all conditions at rung 1 is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 0.96, HiDDeN 0.71, DWT-DCT-SVD 0.30, at rung 2 Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.77, DWT-DCT-SVD 0.74, at rung 3 Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.76, DWT-DCT-SVD 0.71.

**What we conclude.** The gap between rung 1 and rung 2 is the share of failures that are pure alignment and that a synchronisation step could repair.

### heatmap_diff_smoke

**What you see.** Rung 2 minus rung 1 per cell, blue where realignment rescues detections, white where it changes nothing.

**How to read it.** Strong blue columns are the conditions where the watermark survives in the pixels but the decoder loses it. Red would mean realignment hurt, which should not happen.

**What it means.** The mean gain per method is DWT-DCT-SVD +0.44, TrustMark +0.03, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.05.

**What we conclude.** The methods and conditions with the largest gain are the ones where a practical synchroniser is worth building.

### null_scores

**What you see.** For every method, the distribution of detection scores on the 5,000 unwatermarked null images, photos and screens in different colours, with the 1 percent threshold as a dashed line.

**How to read it.** The threshold sits where 1 percent of all null images fall to its right. When the two colours are offset, the realised false positive rate differs between photos and screens at that threshold, which is reported in `thresholds.csv`.

**What it means.** The classical method has a discrete score, so its threshold lands on a tie and its realised rate is 1.66 percent, 2.8 percent on screens. TrustMark, Watermark Anything and HiDDeN score photos and screens differently, with photo rates of 2.2, 1.4 and 0.3 percent at the pooled threshold.

**What we conclude.** Every TPR in this benchmark is read against a threshold whose realised false positive rate per domain is known, and the per domain table travels with it.
