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
| `report/` | The LaTeX skeleton of the report and its bibliography, with the figures and tables included from `results/` |

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

### Manual setup on any Linux machine

The commands below are what the two setup scripts do, for a reader who downloaded the code and
runs neither of them. They work from a clone and from an unpacked ZIP alike. Even when the code came from a
ZIP, git must be installed, because two dependencies are fetched from GitHub by commit, the
VideoSeal package during the requirements install and the Watermark Anything code below. Run them
in order from the repository root.

```sh
sudo apt-get install -y python3-venv python3-pip unzip tmux git libgl1 libglib2.0-0
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch==2.14.0+cu126 torchvision==0.29.0+cu126 --index-url https://download.pytorch.org/whl/cu126
python -m pip install -r environment/requirements.txt
python -m pip install -e .
playwright install chromium
sudo .venv/bin/playwright install-deps chromium
git clone https://github.com/facebookresearch/watermark-anything third_party/watermark_anything
git -C third_party/watermark_anything checkout $(cat environment/wam_commit.txt)
python environment/download_models.py --root data/images/models
```

The torch line installs the CUDA 12.6 build from the PyTorch index before the requirements, because
the default PyPI wheel may need a newer driver than the machine has and every number in this
repository comes from the cu126 build. A driver too old for CUDA 12.6 needs the newest CUDA build the
PyTorch index offers for that driver, in both places of that line, and the results may then differ slightly. The requirements pin torch 2.14.0
without a CUDA suffix, so pip keeps whichever build is already installed. The model download fetches
about 1.8 GB and checks every file against the checksum in `configs/models.yaml`.

On a machine without a GPU, or to force the CPU on a machine with one, set `WMBENCH_DEVICE=cpu`
in the environment. Every smoke command in this README then runs on the CPU with no other change.
The quality run takes about 40 minutes, the platform sweep under an hour, the calibration about two
and a half hours, and the robustness run at three rungs most of a day, because the image
registration costs about 5 s per image and condition on the CPU. The thresholds are read from the
committed `results/summary/thresholds.csv` and `thresholds_rung3.csv`, so the 5,000 image null set
is not needed for any smoke command. Recomputing the thresholds themselves needs the null set and took
about three hours on the VM's GPU.

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

## Screenshots and chains

`screenshots.py` renders the image on a plain page in a headless Chromium through Playwright
under the zoom and density of each condition in `configs/screenshots.yaml`, cuts the image out
at its recorded device box, and records the exact scale, phase, format and browser build. It
also simulates the same resampling without a browser, and `calibration.py` compares the two on
the smoke subset for every method. `chains.py` composes screenshots, platform profiles and tier 1
actions into the five named chains and composes their inverses. A reference pattern is rendered
at the start of every calibration run and its checksum compared with the config, so a different
browser build is noticed.

```sh
python -m pytest -q tests/test_screenshots.py
python -m wmbench.transforms.calibration --quality data/images/work/quality_smoke.jsonl --out data/images/work/calibration_smoke.jsonl
```

The calibration writes `results/calibration/screenshots_smoke.csv` and takes about two hours on
a CPU, most of it decoding. The screenshot conditions need Chromium, which `setup_pc.ps1` and
`setup_vm.sh` install. Without `playwright install chromium` the screenshot conditions and the
calibration cannot run and the screenshot tests skip.

## Real device screenshots

`python -m wmbench.runner.real_sheet --out <folder>` writes a 100 file sheet of watermarked
images for screenshots taken on real devices, and `python -m wmbench.runner.real_ingest --folder
<drop> --quality <records> --out <jsonl> --summary <csv>` decodes a folder of such screenshots,
matching files by their `<method>__<image>` names and grouping by the person and device folders.
No real device screenshots were collected in this project, the tools exist for anyone who wants
to add them.

## Detection and realignment

The detection threshold per method is the score that 1 percent of the 5,000 unwatermarked null
images exceed, with the realised rate reported for photos and screens. The robustness runner
decodes every watermarked smoke image after every condition at three rungs, as received, after
the oracle realignment with cover fill plus a zero fill ablation, and after the estimated
realignment. The null shift check decodes 500 null images after 17 representative conditions at
the same three rungs and gives rung 3 its own threshold. The cell tables, curves, heat maps,
breakdowns and captions are built from the records.

```sh
python -m wmbench.detect.null_run --manifest data/manifests/null.csv --data-root data/images --out data/images/work/null_scores.jsonl
python -m wmbench.detect.thresholds --records data/images/work/null_scores.jsonl
python -m wmbench.figures.null_plots
python -m wmbench.runner.robustness --manifest data/manifests/smoke.csv --data-root data/images --quality data/images/work/quality_smoke.jsonl --out data/images/work/robust_smoke.jsonl --smoke --zero-fill
python -m wmbench.detect.null_shift --manifest data/manifests/null.csv --data-root data/images --out data/images/work/null_shift.jsonl
python -m wmbench.detect.null_shift_table --records data/images/work/null_shift.jsonl
python -m wmbench.figures.cells --records data/images/work/robust_smoke.jsonl --thresholds results/summary/thresholds.csv --thresholds3 results/summary/thresholds_rung3.csv --smoke
python -m wmbench.figures.plots
python -m wmbench.figures.captions
```

The null decode and the null shift need the 5,000 null images and ran on the VM. The runner
takes `--methods` and `--shard i/n` to split the work over processes, each process keeps its own
registration cache next to its output and `--registration` points several processes at one
cache. On the VM the smoke run took 2 h 20 for the four learned methods on the GPU and 2 h 45
for the classical method on four CPU shards.

## Running jobs on the VM

```sh
python -m wmbench.runner.remote push BRANCH
python -m wmbench.runner.remote launch NAME "python -m wmbench.runner.jobs dummy --n 20 --out /home/student/data/work/dummy.jsonl"
python -m wmbench.runner.remote jobs
python -m wmbench.runner.remote pull /home/student/data/work/dummy.jsonl data/images/work/dummy.jsonl
```

Every job writes one JSON line per finished item and skips finished items when relaunched, so a
stopped job is resumed by launching the same command again.

## Full run

`environment/full_run.sh` runs the 1,000 test images through the 75 conditions on the VM in one
tmux session and chains three waves with no gap, the quality run per method in parallel, three
GPU shards of the four learned methods, and then the classical method on CPU shards that reuse
the GPU registration caches. It ends by writing `robust_full.done`, or `robust_full.failed` with
a count, under `/home/student/data/work`. Launch it from the PC and let it run, it does not need
the PC afterwards, and relaunching the same command resumes every wave.

```sh
python -m wmbench.runner.remote launch full_run "bash environment/full_run.sh data/manifests/test.csv full 3 12"
python -m wmbench.runner.remote pull /home/student/data/work/robust_full_gpu0.jsonl data/images/work/robust_full_gpu0.jsonl
```

The arguments are the manifest, the tag for the output names, the number of GPU shards, at most
three on a 24 GB card, and the number of CPU shards of three threads each.

With the record files pulled to `data/images/work`, the full run tables, figures, captions and
LaTeX tables are built on the PC. The null shift table also writes
`results/summary/thresholds_family.csv`, a threshold per flagged condition, method and rung set
on the 500 null images of that condition alone, which the cell table carries as extra columns
next to the pooled numbers.

```sh
python -m wmbench.quality.quality_table --records data/images/work/quality_full.jsonl --out-dir results/summary --tag full --machine vm
python -m wmbench.detect.null_shift_table --records data/images/work/null_shift.jsonl
python -m wmbench.figures.cells --records data/images/work/robust_full_*.jsonl --thresholds results/summary/thresholds.csv --thresholds3 results/summary/thresholds_rung3.csv --thresholds-family results/summary/thresholds_family.csv --tag full
python -m wmbench.figures.plots --cells results/summary/cells_full.csv --tag full
python -m wmbench.figures.captions --cells results/summary/cells_full.csv --tag full
python -m wmbench.figures.tables --cells results/summary/cells_full.csv --tag full
```

The sha256 of every table written by these commands is in `results/summary/checksums.txt`.

## Reproducing from a fresh copy

`environment/reproduce_smoke.sh` runs every smoke command of this README in order from a fresh
copy of the code into a fresh data root and compares what comes out with the committed tables. It
links the `sources` and `models` folders of a shared data root into the new root, downloads into
them whatever is missing, and rebuilds everything else, the vendored Watermark Anything code, the
preprocessed images, the quality run, the residual and transform strips, the null decode and
thresholds, the platform sweep, the calibration, the robustness run at three rungs, the null shift
check, the cell tables, the figures and the captions. It needs the Python environment of the
section above, with Chromium, and a GPU for a run of about four hours.

Start from a clone of the GitHub repository or from an unpacked ZIP, then

```sh
bash environment/reproduce_smoke.sh CLONE ROOT SHARED VENV
```

The four arguments are positional and each has the VM default shown in the example below. `CLONE`
is the directory of the code copy the check runs from. `ROOT` is the new data root that receives
the preprocessed images, the job outputs and the logs. `SHARED` is an existing data root whose
`sources` and `models` folders are linked into `ROOT`, so that archives and weights downloaded once
are reused. `VENV` is the Python environment to activate. For a reader who followed the manual setup section, with the code in the current directory, the
environment at `.venv` and a new data root under the home folder, the shared root is the data root
of the manual setup section, so the model files are not downloaded twice. The call is

```sh
mkdir -p data/images/sources
bash environment/reproduce_smoke.sh "$PWD" ~/repro_data "$PWD/data/images" "$PWD/.venv"
```

On the VM the call is

```sh
git clone /home/student/repo.git /home/student/repro_check
cd /home/student/repro_check
bash environment/reproduce_smoke.sh /home/student/repro_check /home/student/repro_data /home/student/data /home/student/venv
```

A machine with nothing creates the two shared folders first, `mkdir -p SHARED/sources
SHARED/models`, and the script then downloads into them the source archives the smoke and null
manifests reference, about 18 GB, and the model files, about 1.8 GB. With the folders already
filled the check downloads nothing.

The script writes one log per step under `ROOT/logs`, `compare_tables.txt` with the largest
numeric difference per table against the committed ones, `changed_files.txt` with every committed
result file the rebuild changed, `manifest_diff.txt` which is empty when every pixel checksum
matched, and `repro.done` or `repro.failed` at the end. On a copy without a `.git` folder the
manifest diff and the changed files outputs are empty and the comparison in `compare_tables.txt` is
unaffected, because the committed tables are copied aside before anything is rebuilt. The tables
from a GPU rebuild agree with the committed ones within the float noise of the decoders, the
committed smoke quality numbers come from the CPU run on the PC. `python -m
wmbench.runner.compare_tables <dir a> <dir b> --tolerance 0.02` runs the same comparison between
any two result folders.

## Cleanup

`sh cleanup.sh` lists the regenerable folders under the data root and their sizes and deletes
nothing. `sh cleanup.sh --yes` deletes the job outputs, the derived images and the vendored code.
`sh cleanup.sh --all --yes` also deletes the preprocessed splits, the models and the source
archives, which the download and preprocessing commands rebuild. `--data-root=PATH` selects
another data root, the default is `data/images`. Manifests, configs, code and results are never
touched.

## Tests

```sh
python -m pytest -q
```
