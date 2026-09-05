# Summary results

This folder holds the numbers that describe the five watermarking methods before any sharing
action is applied. Everything here was produced from the 50 image smoke subset with one command
per machine, see the top level README.

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
  bits. This is a provisional detector until the empirical thresholds arrive in a later
  milestone. `clean_fpr_analytic` applies the same threshold to the unwatermarked image and
  should be 0.
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
