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