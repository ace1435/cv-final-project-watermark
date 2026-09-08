# Report skeleton

`main.tex` is the two column skeleton of the two to three page report with the section
structure the course asks for, abstract, introduction with related work, method, results and
discussion. The figures and tables are included from `../results/` so that a regenerated result
lands in the report without editing. `references.bib` holds every method, dataset, tool and
prior benchmark the text cites.

Every place that needs prose is marked with `\todo{...}`, which prints in bold, and says what
the sentence should carry. The team writes the text, the numbers to quote are in the figure
captions, the tables and the guides under `results/`.

## Build

From this folder, with any TeX distribution that has natbib, booktabs and hyperref.

```sh
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

or with tectonic, which fetches the packages it needs on first use.

```sh
tectonic main.tex
```

## Before submission

- Replace every `\todo{...}` and remove the `\todo` definition.
- Three bibliography entries carry a note to verify the author list, PixelSeal, ScreenMark and
  the entries written with `and others`. Check them against the papers.
- The heat map is a full width figure. If space is short, swap it for the rung 2 minus rung 1
  map or crop the page to two of the four blocks in the results folder.
- The quality table is the full one from `results/tables/quality_full.tex`. The tables
  `families_full.tex`, `domains_full.tex`, `conditions_full.tex` and `thresholds_family.tex` are
  ready to include in the same way if space allows.
