# Data guide

Everything here is regenerable from the committed manifests and the public sources. Nothing
under the data root is committed except the manifests in `data/manifests/`.

## Manifests

| File | Rows | Content |
|---|---|---|
| `sources.csv` | 1808 | Every downloaded source file with its url, size, sha256 and license |
| `arxiv_candidates.csv` | 200 | arXiv ids of March 2024 cs papers under CC BY 4.0, first 200 by id |
| `pool.csv` | 11533 | Every candidate image with its source, member, size and source sha256 |
| `pool_stats.json` | | Per source counts of scanned, kept, duplicate, too small and skipped items |
| `test.csv` | 1000 | The benchmark set, 500 photos and 500 screens, seed 42 |
| `smoke.csv` | 50 | 25 photos and 25 screens drawn from the test set with seed 0 |
| `null.csv` | 5000 | Unwatermarked images for threshold calibration, disjoint from the test set, seed 43 |

Each split row carries `out_sha256`, the checksum of the decoded RGB pixels of the preprocessed
1024 px image together with its size. Pixels are hashed instead of file bytes because PNG
compression differs between zlib builds while the pixels do not. Any machine can check its own copy
with `python data/preprocess.py --manifest data/manifests/smoke.csv` followed by
`git diff data/manifests/smoke.csv`.

## Test set composition

| Domain | Category | Count | Source | License |
|---|---|---|---|---|
| photo | pro | 350 | CLIC 2020 professional | Unsplash License |
| photo | mobile | 150 | CLIC 2020 mobile | CC0 1.0 |
| screen | ui_mobile | 100 | ScreenSpot-v2 mobile, PNG only | Apache-2.0 |
| screen | ui_desktop_pro | 50 | ScreenSpot-Pro | MIT |
| screen | ui_desktop_v2 | 25 | ScreenSpot-v2 desktop | Apache-2.0 |
| screen | ui_web | 75 | VisualWebBench | Apache-2.0 |
| screen | doc_doclaynet | 150 | DocLayNet v1.2 validation, 25 per document category | CDLA-Permissive-1.0 |
| screen | doc_arxiv | 100 | arXiv first pages | CC BY 4.0 |

The null set holds every remaining CLIC photo, all 900 DIV2K images, and 2,920 screens split
evenly between UI screenshots and DocLayNet pages. DIV2K is licensed for academic use only, so it
never appears in the test set and none of its images are published.

## Preprocessing

Every image is decoded, its EXIF orientation applied, alpha composited on white, converted to RGB,
resized so the long side is exactly 1024 px with Lanczos, and saved as a PNG with no gAMA, iCCP,
cHRM, sRGB, pHYs or eXIf chunk. Candidates with a long side below 1024 px are excluded from the
pool so that no image is upscaled. Document pages are rendered from their PDF at 150 dpi before the
resize. Pillow and PyMuPDF versions are pinned in `environment/requirements.txt`.

## Where the data lives

| Location | Content | Size | Regenerable |
|---|---|---|---|
| VM `/home/student/data/sources` | Source archives, parquet files and PDFs | 18 GB | yes, `data/download.py` |
| VM `/home/student/data/test` | 1000 preprocessed test images | 712 MB | yes, `data/preprocess.py` |
| VM `/home/student/data/smoke` | 50 preprocessed smoke images | 35 MB | yes |
| VM `/home/student/data/null` | 5000 preprocessed null images | 3.2 GB | yes |
| VM `/home/student/data/logs` | One log per tmux job | small | no, kept |
| VM `/home/student/data/work` | Job outputs as JSONL and derived images | grows | yes |
| VM `/home/student/data/models` | Model checkpoints from `configs/models.yaml` | later | yes |
| PC `data/images/smoke` | The 50 smoke images, copied from the VM or rebuilt | 35 MB | yes |
| PC `data/images/sources` | Only the source files the smoke subset needs | see below | yes |

The PC keeps `data/images/` outside git. The smoke images arrive either by copying them from the VM
or by running the two commands in the top level README, which download only the archives the
smoke rows reference. A smoke rebuild on a fresh clone downloads about 9.7 GB, most of it two
CLIC archives, and the archives can be deleted once the 50 images exist.

## Cleanup

Everything marked regenerable can be deleted and rebuilt. Source archives are the slowest part to
restore, about 18 GB of downloads, so they stay until the project wraps.
