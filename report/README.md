# Report

`main.tex` is the source of the submitted two column report, with abstract, introduction with related work, method, results and discussion. `references.bib` holds every work it cites. Every number in the report comes from the committed results, and unless the text names another file it is a row of `results/summary/cells_full.csv`.

## Figures

The report expects its two figures in a `figures/` folder next to `main.tex`, which is not committed because both come from the results folder.

- `figures/curves_tpr_full_screenshot.png` is a copy of `results/screenshot/curves_tpr_full.png`.
- `figures/heatmap_rung1_two_blocks.png` is the first and the last of the four condition blocks of `results/summary/heatmap_rung1_full.png`, cropped without resampling, with the colour bar.

## Build

From this folder, with the two figures in place and any TeX distribution that has natbib, booktabs and hyperref.

```sh
pdflatex main && bibtex main && pdflatex main && pdflatex main
```
