# Results

Every number and figure the report uses lives here. Each folder has its own README that explains,
for a reader with no background, what was measured, what the columns and axes mean, what to look
for, and what can and cannot be concluded.

| Folder | Content |
|---|---|
| `summary/` | Quality of the five methods at their native setting and at the common 40 dB point, timing, residual strips, the detection thresholds with their realised false positive rates, the per family thresholds, the null score histograms, the heat maps over every condition and the cell tables with every cell |
| `jpeg/`, `downscale/`, `upscale/`, `crop/`, `shift/`, `letterbox/`, `caption/`, `sticker/`, `brightness/`, `contrast/`, `gamma/`, `rotate/` | One folder per family of sharing actions, with sample strips, the cell tables, the robustness curves and the failure breakdown |
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

The threshold is set on the pooled null set. Where the null shift check found more than 2 percent of
unwatermarked images above it after a sharing action, the cells of that family, method and rung also
carry a threshold set on the 500 null images of that family alone, listed in
`summary/thresholds_family.csv` and stored in the `tau_family` and `tpr_family` columns of the cell
tables, marked with a star in the heat maps and with dotted lines in the curves. The pooled number
stays the primary one everywhere.

Numbers and figures carry a tag. `smoke` is the 50 image smoke subset that every machine can
reproduce from a clean state. `full` is the 1,000 image run on the VM, verified by the checksums in
`summary/checksums.txt`. The Figures section of every guide describes the full run, and the smoke
figures sit next to the full ones with their own tag and are read the same way.
