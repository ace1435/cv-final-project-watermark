# Summary results

This folder holds the numbers that describe the five watermarking methods before any sharing
action is applied, the detection thresholds from the 5,000 image null set, and the summary of
every detection cell. The quality and cell numbers exist twice, with the tag `smoke` for the 50
image smoke subset that every machine can reproduce and with the tag `full` for the 1,000 image
run on the VM, whose checksums are in `checksums.txt`. The thresholds come from the null set
decoded on the VM. Each file is written by one command, see the top level README.

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
| `quality_full.csv`, `quality_smoke.csv` | One row per method, domain and operating point with the mean, sd and min of PSNR, SSIM, LPIPS and DISTS, the strength used, bit accuracy, and detection rates, for the 1,000 image run and for the smoke subset |
| `quality_full_per_image.csv`, `quality_smoke_per_image.csv` | The same quantities for every image, for distributions and for finding outliers |
| `timing_full_vm.csv`, `timing_smoke_vm.csv` | Mean seconds per image for embedding, decoding and the strength search on the VM with an NVIDIA A10 |
| `timing_smoke_pc.csv` | The same on the Windows PC with CPU only |
| `samples/` | For three smoke images per method, a strip showing the cover, the native watermarked image, its residual amplified ten times, the matched watermarked image and its residual |
| `../tables/` | LaTeX tables, the quality rows per tag, the headline per method, the means per family, the photo and screen split, every condition, the thresholds and the per family thresholds |
| `thresholds.csv` | One row per method with the score threshold that 1 percent of the 5,000 null images exceed, the realised false positive rate pooled and for photos and screens, and the analytic threshold on hard bits with its realised rate |
| `null_scores.svg`, `null_scores.png` | The distribution of null scores per method, photos and screens in two colours, with the threshold |
| `thresholds_rung3.csv` | The threshold for rung 3, from 500 null images pushed through 17 representative conditions and the estimated realignment |
| `null_shift.csv` | The realised false positive rate per condition, method and rung on those transformed null images, with a flag above 2 percent |
| `thresholds_family.csv` | For the 11 flagged null shift cells, the threshold set on the 500 null images of that condition alone, with the pooled and the family realised rates, pooled and per domain |
| `cells_full.csv`, `cells_smoke.csv` | Every detection cell, one row per condition, method and domain, with the TPR at each rung and its Wilson bounds, bit accuracy, the failure label shares, the median registration error, and in the full table the per family threshold columns |
| `heatmap_rung1_full`, `heatmap_rung2_full`, `heatmap_rung3_full`, `heatmap_diff_full` | The TPR of every method under every condition at each rung, and the rung 2 minus rung 1 difference, as SVG and PNG, with the smoke versions next to them |
| `checksums.txt` | sha256 of every table written from the full run and of the record files behind them |

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
- In the cell tables, `tpr_r1`, `tpr_r2` and `tpr_r3` are the detection rates at the three
  rungs with `_low` and `_high` Wilson bounds, `bitacc_r1` to `bitacc_r3` the mean bit accuracy,
  `label_*` the share of images per failure label, `valid_fraction` the share of original pixels
  still present after the oracle realignment, `corner_error_median` the registration error of
  rung 3 in pixels and `reg_failed` the share of images where the matcher found no registration.
  `tpr_r2_zero_fill`, the oracle rung with black instead of cover pixels, exists in the smoke
  table only.
- In `cells_full.csv`, `tau_family_r1` to `tau_family_r3` and `tpr_family_r1` to
  `tpr_family_r3` exist only in the rows of a family, method and rung that the null shift check
  flagged, and `recalibrated_rungs` lists those rungs. They hold the threshold from
  `thresholds_family.csv` and the detection rate at it. The pooled `tpr_r1` to `tpr_r3` stay the
  primary numbers.
- `ecc_ok_rate` exists only for TrustMark and tells whether the 61 bit payload survives the
  error correcting code. `pixel_score_mean` exists only for Watermark Anything and is the
  fraction of pixels its detector flags, with `clean_pixel_score_mean` the same on the cover.

## What to look for and what can be concluded

- TrustMark, Watermark Anything and PixelSeal land at 40.0 dB on all 1,000 images with a spread
  under 0.1 dB and decode the untouched matched image with bit accuracy 0.998, 1.000 and 0.998,
  so the matching does not hurt them.
- HiDDeN ships at 32.6 dB. Bringing it to 40 dB divides its residual by about two and its clean
  bit accuracy drops from 0.977 to 0.900, 0.92 on photos and 0.88 on screens, so for HiDDeN the
  matching hurts and every robustness row must be read with that in mind.
- DWT-DCT-SVD cannot reach 40 dB on many photos while still decoding. Its matched images sit at
  39.0 dB on average with a spread of 1.9 dB and a worst photo at 26.8 dB, and its clean bit
  accuracy at the matched point is 0.909, 1.000 on photos and 0.818 on screens, because its
  modulation clips in saturated white regions. Its clean ceiling of about 0.85 detected images
  is visible in every cell where nothing moves.
- PixelSeal is the least visible method at its native setting, 46.7 dB, and needs its knob
  raised from 0.2 to 0.47 to reach 40 dB.
- Over the 75 conditions of the full run the mean TPR at 1 percent FPR as received is Watermark
  Anything 1.00, PixelSeal 1.00, TrustMark 0.96, HiDDeN 0.79 and DWT-DCT-SVD 0.26, and after the
  oracle 1.00, 1.00, 1.00, 0.86 and 0.68. The whole TrustMark gap sits in crops at half the area
  and below, the 15 percent letterbox, the 10 degree rotation and the phone to instagram chain.
  The HiDDeN gap is enlargement only. The classical gap is every geometric change, and the
  estimated realignment closes most of it, to 0.66.
- Timing on the A10 is 0.03 to 0.06 s per image to embed and 0.02 to 0.08 s to decode for the
  learned methods, and 0.19 s and 0.12 s for DWT-DCT-SVD on the CPU, whose strength search costs
  2.1 s per image.

## What cannot be concluded

The benchmark measures five post hoc methods at one visual quality point on 1024 px images,
against a real Chromium renderer and a simulated platform recompression. Screenshots from
operating system tools, phones and messaging apps were not collected, and the platform qualities
for WhatsApp, Instagram and Facebook are estimates covered by the sweep in
`../platform/sweep_smoke.csv`. Nothing here says how a method behaves at a different quality
point or on images larger than 1024 px.

## Figures

### heatmap_rung1_full, heatmap_rung2_full, heatmap_rung3_full

**What you see.** Methods as rows, every condition as a column, each cell the share of images detected at 1 percent FPR, dark is low and bright is high. Rung 1 is the image as received, rung 2 after the oracle puts it back into place, rung 3 after the estimated realignment.

**How to read it.** Scan a row to see where a method breaks. Scan a column to see which methods a condition breaks. Compare the same cell across the three maps to see whether the failure is alignment or destruction. A star after a number marks a cell that also carries a per family threshold in the cell table, because the pooled threshold let more than 2 percent of unwatermarked images through in the null shift check for that family, method and rung. The starred cells are DWT-DCT-SVD under brightness, DWT-DCT-SVD under contrast, DWT-DCT-SVD under gamma, HiDDeN under crop, PixelSeal under caption, and their second number is in `thresholds_family.csv` and in the `tpr_family` columns.

**What it means.** Mean TPR over all conditions at rung 1 is Watermark Anything 1.00, PixelSeal 1.00, TrustMark 0.96, HiDDeN 0.79, DWT-DCT-SVD 0.26, at rung 2 Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.86, DWT-DCT-SVD 0.68, at rung 3 Watermark Anything 1.00, PixelSeal 1.00, TrustMark 1.00, HiDDeN 0.85, DWT-DCT-SVD 0.66.

**What we conclude.** The gap between rung 1 and rung 2 is the share of failures that are pure alignment and that a synchronisation step could repair.

### heatmap_diff_full

**What you see.** Rung 2 minus rung 1 per cell, blue where realignment rescues detections, white where it changes nothing, red where the oracle lowers the rate.

**How to read it.** Strong blue columns are the conditions where the watermark survives in the pixels but the decoder loses it. Red cells are the ones where putting the image back hurts, which only happens when the decoder reads the whole canvas and the filled in cover pixels dilute the mark.

**What it means.** The mean gain per method is DWT-DCT-SVD +0.42, TrustMark +0.04, Watermark Anything +0.00, PixelSeal +0.00, HiDDeN +0.07. Cells that lose more than 0.1 after the oracle are HiDDeN at crop_0.3 from 0.95 to 0.71, HiDDeN at chain_phone_instagram from 0.48 to 0.31, HiDDeN at chain_crop_jpeg_screenshot from 0.69 to 0.53. These are crops decoded by a method that reads the full canvas, where the received crop alone carries the mark and the oracle pastes it onto a canvas of unwatermarked cover pixels that the decoder averages in.

**What we conclude.** The methods and conditions with the largest gain are the ones where a practical synchroniser is worth building.

### null_scores

**What you see.** For every method, the distribution of detection scores on the 5,000 unwatermarked null images, photos and screens in different colours, with the 1 percent threshold as a dashed line.

**How to read it.** The threshold sits where 1 percent of all null images fall to its right. When the two colours are offset, the realised false positive rate differs between photos and screens at that threshold, which is reported in `thresholds.csv`.

**What it means.** The classical method has a discrete score, so its threshold lands on a tie and its realised rate is 1.66 percent, 2.8 percent on screens. TrustMark, Watermark Anything and HiDDeN score photos and screens differently, with photo rates of 2.2, 1.4 and 0.3 percent at the pooled threshold.

**What we conclude.** Every TPR in this benchmark is read against a threshold whose realised false positive rate per domain is known, and the per domain table travels with it.
