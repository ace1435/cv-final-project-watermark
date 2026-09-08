#!/bin/bash
set -u
clone=${1:-/home/student/repro_check}
root=${2:-/home/student/repro_data}
shared=${3:-/home/student/data}
venv=${4:-/home/student/venv}
work=$root/work
logs=$root/logs
failed=0
start=$(date +%s)

say() {
  echo "$(date '+%F %T') $*"
}

step() {
  local name=$1
  shift
  local t0
  t0=$(date +%s)
  say "start $name"
  if "$@" > "$logs/$name.log" 2>&1; then
    say "done $name in $(( $(date +%s) - t0 )) s"
  else
    failed=$((failed + 1))
    say "FAILED $name in $(( $(date +%s) - t0 )) s, see $logs/$name.log"
  fi
}

launch() {
  local name=$1
  shift
  say "start $name in the background"
  "$@" > "$logs/$name.log" 2>&1 &
  pids+=($!)
  names+=("$name")
}

wait_all() {
  for i in "${!pids[@]}"; do
    if wait "${pids[$i]}"; then
      say "done ${names[$i]}"
    else
      failed=$((failed + 1))
      say "FAILED ${names[$i]}, see $logs/${names[$i]}.log"
    fi
  done
  pids=()
  names=()
}

mkdir -p "$root" "$logs" "$work"
ln -sfn "$shared/sources" "$root/sources"
ln -sfn "$shared/models" "$root/models"
cd "$clone"
. "$venv/bin/activate"
export PYTHONPATH=$clone/src
cpu="env WMBENCH_DEVICE=cpu OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 OPENCV_FOR_THREADS_NUM=3"
pids=()
names=()

say "fresh clone check, clone $clone at $(git rev-parse --short HEAD), data root $root, shared sources and models from $shared"
cp -r results "$root/results_committed"

if [ ! -d third_party/watermark_anything ]; then
  step fetch_wam git clone -q https://github.com/facebookresearch/watermark-anything third_party/watermark_anything
  step pin_wam git -C third_party/watermark_anything checkout -q "$(cat environment/wam_commit.txt)"
fi
step models python environment/download_models.py --root "$root/models"
step download_smoke python data/download.py --data-root "$root" --manifest data/manifests/smoke.csv
step download_null python data/download.py --data-root "$root" --manifest data/manifests/null.csv
step preprocess_smoke python data/preprocess.py --manifest data/manifests/smoke.csv --data-root "$root" --workers 8
step preprocess_null python data/preprocess.py --manifest data/manifests/null.csv --data-root "$root" --workers 32
git diff --stat data/manifests > "$logs/manifest_diff.txt"
say "manifest diff after preprocessing, $(wc -l < "$logs/manifest_diff.txt") lines, empty means every pixel checksum matched"
step tests python -m pytest -q

step quality python -m wmbench.quality.quality_run --manifest data/manifests/smoke.csv --data-root "$root" --out "$work/quality_smoke.jsonl"
step quality_table python -m wmbench.quality.quality_table --records "$work/quality_smoke.jsonl" --out-dir results/summary --tag smoke --machine vm
step samples python -m wmbench.figures.samples --manifest data/manifests/smoke.csv --data-root "$root"
step transform_samples python -m wmbench.figures.transform_samples --manifest data/manifests/smoke.csv --data-root "$root"

launch null_run python -m wmbench.detect.null_run --manifest data/manifests/null.csv --data-root "$root" --out "$work/null_scores.jsonl"
launch platform_sweep python -m wmbench.runner.robustness --manifest data/manifests/smoke.csv --data-root "$root" --quality "$work/quality_smoke.jsonl" --out "$work/robust_platform_smoke.jsonl" --groups platform --smoke
launch calibration python -m wmbench.transforms.calibration --manifest data/manifests/smoke.csv --data-root "$root" --quality "$work/quality_smoke.jsonl" --out "$work/calibration_smoke.jsonl"
wait_all
step thresholds python -m wmbench.detect.thresholds --records "$work/null_scores.jsonl"
step null_plots python -m wmbench.figures.null_plots --records "$work/null_scores.jsonl"
step sweep_table python -m wmbench.transforms.sweep_table --records "$work/robust_platform_smoke.jsonl"

launch robust_gpu python -m wmbench.runner.robustness --manifest data/manifests/smoke.csv --data-root "$root" --quality "$work/quality_smoke.jsonl" --out "$work/robust_smoke_gpu.jsonl" --smoke --zero-fill --methods trustmark_q wam pixelseal hidden
launch shift_gpu python -m wmbench.detect.null_shift --manifest data/manifests/null.csv --data-root "$root" --out "$work/null_shift_gpu.jsonl" --methods trustmark_q wam pixelseal hidden
wait_all

for i in 0 1 2 3; do
  launch robust_cpu$i $cpu python -m wmbench.runner.robustness --manifest data/manifests/smoke.csv --data-root "$root" --quality "$work/quality_smoke.jsonl" --out "$work/robust_smoke_cpu$i.jsonl" --smoke --zero-fill --methods dwtdct --shard "$i/4" --registration "$work/robust_smoke_gpu.registration.jsonl"
  launch shift_cpu$i $cpu python -m wmbench.detect.null_shift --manifest data/manifests/null.csv --data-root "$root" --out "$work/null_shift_cpu$i.jsonl" --methods dwtdct --shard "$i/4" --registration "$work/null_shift_gpu.registration.jsonl"
done
wait_all

step null_shift_table python -m wmbench.detect.null_shift_table --records "$work"/null_shift_gpu.jsonl "$work"/null_shift_cpu0.jsonl "$work"/null_shift_cpu1.jsonl "$work"/null_shift_cpu2.jsonl "$work"/null_shift_cpu3.jsonl
step cells python -m wmbench.figures.cells --records "$work"/robust_smoke_gpu.jsonl "$work"/robust_smoke_cpu0.jsonl "$work"/robust_smoke_cpu1.jsonl "$work"/robust_smoke_cpu2.jsonl "$work"/robust_smoke_cpu3.jsonl --thresholds results/summary/thresholds.csv --thresholds3 results/summary/thresholds_rung3.csv --smoke
step plots python -m wmbench.figures.plots --cells results/summary/cells_smoke.csv --tag smoke
step captions python -m wmbench.figures.captions --cells results/summary/cells_smoke.csv --tag smoke

python -m wmbench.runner.compare_tables "$root/results_committed" results --tolerance 0.02 > "$logs/compare_tables.txt" 2>&1
git status --short results > "$logs/changed_files.txt"
say "compared the rebuilt tables with the committed ones, $(tail -1 "$logs/compare_tables.txt")"
say "committed files that changed after the rebuild, $(wc -l < "$logs/changed_files.txt")"

elapsed=$(( $(date +%s) - start ))
if [ "$failed" -eq 0 ]; then
  say "fresh clone check done in $elapsed s with no failed step" | tee "$root/repro.done"
else
  say "fresh clone check finished in $elapsed s with $failed failed steps" | tee "$root/repro.failed"
fi
