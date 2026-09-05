# What survives a screenshot

A quality matched robustness benchmark of invisible image watermarks against everyday sharing
actions, above all real screenshots, with a per condition diagnosis of why each failure happens.

Five post hoc watermarking methods are matched to the same visual quality of 40 dB PSNR, applied
to 1,000 real images, pushed through about 64 sharing conditions, and decoded three ways. Detection
is reported as TPR at an empirical 1 percent FPR from a large set of unwatermarked images.

## Layout

| Path | Content |
|---|---|
| `environment/` | Pinned requirements, setup scripts for the PC and the GPU VM, the warning policy |
| `configs/` | Seeds, dataset sources, remote machine settings, model downloads |
| `data/` | Manifests, download, sampling and preprocessing scripts, and the data guide |
| `src/wmbench/` | The benchmark package |
| `tests/` | Fast tests that run on a laptop in under two minutes |
| `results/` | Every number, figure and table the report uses |

## Environment

The PC side uses Python 3.10 in a virtual environment at `.venv`. On Windows run

```powershell
powershell -ExecutionPolicy Bypass -File environment\setup_pc.ps1
```

The GPU VM is reached through the ssh aliases `vm28` for the student user and `vm28admin` for the
admin user. One command bootstraps it from the PC, including a bare git remote named `vm`, a working
clone, the Python environment, Playwright with Chromium, and a GPU check.

```sh
sh environment/setup_vm.sh vm28 vm28admin vm
```

Warnings raised by our own code are errors. Warnings from third party libraries are silenced one at
a time in `environment/warning_filters.py`, each with the library, the message pattern and the reason.

## Data

Sources, licenses and checksums live in `configs/datasets.yaml` and `data/manifests/sources.csv`.
The image lists are `data/manifests/test.csv` with 1,000 images, `data/manifests/smoke.csv` with 50
images drawn from the test set, and `data/manifests/null.csv` with at least 5,000 unwatermarked
images for threshold calibration. See `data/README.md` for what is stored where.

Download every source, build the image pool, draw the splits, and preprocess, on a machine with the
data root `ROOT`.

```sh
python data/download.py --data-root ROOT
python data/sample.py --data-root ROOT
python data/preprocess.py --manifest data/manifests/smoke.csv --data-root ROOT --workers 8
python data/preprocess.py --manifest data/manifests/test.csv --data-root ROOT --workers 32
python data/preprocess.py --manifest data/manifests/null.csv --data-root ROOT --workers 32
```

To fetch only the sources that one manifest needs, for example the smoke subset on a PC, pass the
manifest to the downloader.

```sh
python data/download.py --data-root data/images --manifest data/manifests/smoke.csv
python data/preprocess.py --manifest data/manifests/smoke.csv --data-root data/images
```

Preprocessing applies the EXIF orientation, composites alpha on white, converts to RGB, resizes the
long side to 1024 px with Lanczos, and saves a PNG with no color metadata chunks. Document pages are
rendered from PDF at 150 dpi first. The sha256 of every output image is recorded in the manifest,
so a rerun on any machine can be checked with `git diff data/manifests`.

## Watermarkers and quality matching

Five methods share one adapter interface, see `src/wmbench/watermarkers/README.md`. Model files
are fetched by `environment/download_models.py` from `configs/models.yaml` with checksums, and
the setup scripts do this for you. The quality run embeds every smoke image with every method at
the native strength and at the strength that gives 40 dB PSNR, decodes the cover, the native and
the matched image, and records quality metrics and timings, one JSON line per image and method.

```sh
python -m wmbench.quality.quality_run --manifest data/manifests/smoke.csv --data-root data/images --out data/images/work/quality_smoke.jsonl
python -m wmbench.quality.quality_table --records data/images/work/quality_smoke.jsonl --out-dir results/summary --tag smoke --machine pc
python -m wmbench.figures.samples --manifest data/manifests/smoke.csv --data-root data/images
```

The first command takes about 40 minutes on a CPU and about 5 minutes on the VM, and resumes
where it stopped. The second writes `results/summary/quality_smoke.csv`, the per image file, the
timing file and `results/tables/quality_smoke.tex`. The third writes the residual strips under
`results/summary/samples/`.

## Transforms

The sharing actions live in `src/wmbench/transforms/`. `tier1.py` implements the single actions
listed in `configs/transforms.yaml`, `platforms.py` the platform profiles in
`configs/platforms.yaml`, and `registry.py` turns both into named conditions. Every transform
returns the output image and its exact parameters, and `inverse` turns those parameters into a
matrix that maps the original 1024 px grid to the output grid plus a mask of the original pixels
that survived. `src/wmbench/realign/oracle.py` uses that matrix to put a transformed image back
into the original grid, filling lost regions with the cover. The tests check that this round
trip is close to identity on the valid region for every geometric condition.

```sh
python -m pytest -q tests/test_transforms.py
python -m wmbench.figures.transform_samples --manifest data/manifests/smoke.csv --data-root data/images
python -m wmbench.runner.robustness --manifest data/manifests/smoke.csv --data-root data/images --quality data/images/work/quality_smoke.jsonl --out data/images/work/robust_platform_smoke.jsonl --groups platform --smoke
python -m wmbench.transforms.sweep_table --records data/images/work/robust_platform_smoke.jsonl
```

The second command writes one strip per smoke image under `results/<family>/samples/`. The third
decodes every smoke image after every platform profile and the quality sweep, and the fourth
writes `results/platform/sweep_smoke.csv`.

## Running jobs on the VM

```sh
python -m wmbench.runner.remote push BRANCH
python -m wmbench.runner.remote launch NAME "python -m wmbench.runner.jobs dummy --n 20 --out /home/student/data/work/dummy.jsonl"
python -m wmbench.runner.remote jobs
python -m wmbench.runner.remote pull /home/student/data/work/dummy.jsonl data/images/work/dummy.jsonl
```

Every job writes one JSON line per finished item and skips finished items when relaunched, so a
stopped job is resumed by launching the same command again.

## Tests

```sh
python -m pytest -q
```
