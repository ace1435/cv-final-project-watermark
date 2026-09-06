# Results

Every number and figure the report uses lives here. Each folder has its own README that explains,
for a reader with no background, what was measured, what the columns and axes mean, what to look
for, and what can and cannot be concluded.

| Folder | Content |
|---|---|
| `summary/` | Quality of the five methods at their native setting and at the common 40 dB point, timing, residual strips, the detection thresholds with their realised false positive rates, the null score histograms, the heat maps over every condition and `cells_smoke.csv` with every cell |
| `jpeg/`, `downscale/`, `upscale/`, `crop/`, `shift/`, `letterbox/`, `caption/`, `sticker/`, `brightness/`, `contrast/`, `gamma/`, `rotate/` | One folder per family of sharing actions, with sample strips, the cell table, the robustness curves and the failure breakdown |
| `platform/`, `platform_hires/` | The five platform profiles applied to the 1024 px image and to a simulated 2048 px original |
| `screenshot/` | The 15 real browser screenshot conditions |
| `chains/` | The five chains of sharing actions |
| `calibration/` | How closely a simulated screenshot matches a real browser render |
| `tables/` | LaTeX tables ready to include in the report |

## How detection is reported

Every method decodes a score per image. The threshold per method is the value that 1 percent of
5,000 unwatermarked images exceed, so every rate in this folder is a true positive rate at 1 percent
false positive rate, written TPR at 1 percent FPR. Each image is decoded three ways, called rungs.
Rung 1 decodes the image as received. Rung 2 undoes the recorded geometry with the exact recorded
parameters and fills the lost regions with the original unwatermarked pixels, which no real detector
can do, so it is an oracle that shows whether the watermark is still in the pixels. Rung 3 estimates
the geometry from the received image and the original with a keypoint matcher and decodes after
that, which is what a practical detector with the original at hand could do. From the three answers
each image gets one label. Survived means rung 1 detects it. Alignment means only the oracle rescues
it. Recoverable means the estimated realignment rescues it too. Sync failed means the oracle rescues
it but the estimate does not. Destroyed means not even the oracle rescues it.

Numbers marked `smoke` come from the 50 image smoke subset that every machine can reproduce.
Numbers from the full 1,000 image run will carry the tag `full` and a checksum file.
