# Calibration of simulated against real screenshots

## What was measured

For every smoke image, every method at 40 dB and every screenshot condition, the watermarked
image was rendered by the real browser and also resampled by our simulation of what Chromium
does, bilinear resampling for scales above one half, a box reduction by powers of two followed
by bilinear resampling below that, with the exact scale and the sub pixel phase of the image
corner, and Chromium's own JPEG for the JPEG condition. The two outputs were compared pixel by
pixel and both were decoded.

## Files

- `screenshots_smoke.csv` has one row per condition and method with the mean and minimum PSNR
  between the real and the simulated output, the bit accuracy of each, the mean absolute
  difference between them, the analytic detection rate of each, the fraction of images where
  both agree on detection, and the fraction where the decoded bits are identical.

## How to read it

A PSNR above 45 dB between real and simulated means the simulation is close to pixel exact. A
detection agreement of 1.00 means the simulation would give the same benchmark answer as the
real browser for that condition and method. The columns to watch are `psnr_real_sim_mean` and
`detection_agreement`.

## What can be concluded

The number in the table for each condition says whether a paper that simulates a screenshot as
a resize would reach the same conclusion as one that takes real screenshots. The M4 report
lists the conditions where the two disagree.
