#!/bin/bash
set -u
manifest=$1
tag=$2
gpu_shards=$3
cpu_shards=$4
data=/home/student/data
work=$data/work
logs=$data/logs
out=$work/robust_$tag
quality=$work/quality_$tag.jsonl
learned="trustmark_q wam pixelseal hidden"
failed=0

say() {
  echo "$(date '+%F %T') $*"
}

wait_all() {
  for pid in "$@"; do
    if ! wait "$pid"; then
      failed=$((failed + 1))
    fi
  done
}

cd /home/student/work
. /home/student/venv/bin/activate
mkdir -p "$logs"

say "wave 0 quality start, manifest $manifest"
pids=()
for m in $learned dwtdct; do
  python -m wmbench.quality.quality_run --manifest "$manifest" --data-root "$data" --out "${quality%.jsonl}_$m.jsonl" --methods "$m" > "$logs/${tag}_quality_$m.log" 2>&1 &
  pids+=($!)
done
wait_all "${pids[@]}"
cat "${quality%.jsonl}"_{trustmark_q,wam,pixelseal,hidden,dwtdct}.jsonl > "$quality"
say "wave 0 quality done, $(wc -l < "$quality") records, failures so far $failed"

say "wave 1 gpu start, $gpu_shards shards"
pids=()
for i in $(seq 0 $((gpu_shards - 1))); do
  python -m wmbench.runner.robustness --manifest "$manifest" --data-root "$data" --quality "$quality" --out "${out}_gpu$i.jsonl" --methods $learned --shard "$i/$gpu_shards" > "$logs/${tag}_gpu$i.log" 2>&1 &
  pids+=($!)
done
wait_all "${pids[@]}"
cat "${out}"_gpu*.registration.jsonl > "${out}.registration.jsonl"
say "wave 1 gpu done, $(cat "${out}"_gpu?.jsonl | wc -l) records, $(wc -l < "${out}.registration.jsonl") registrations, failures so far $failed"

say "wave 2 dwtdct start, $cpu_shards shards"
pids=()
for i in $(seq 0 $((cpu_shards - 1))); do
  WMBENCH_DEVICE=cpu OMP_NUM_THREADS=3 MKL_NUM_THREADS=3 OPENCV_FOR_THREADS_NUM=3 python -m wmbench.runner.robustness --manifest "$manifest" --data-root "$data" --quality "$quality" --out "${out}_cpu$i.jsonl" --methods dwtdct --shard "$i/$cpu_shards" --registration "${out}.registration.jsonl" > "$logs/${tag}_cpu$i.log" 2>&1 &
  pids+=($!)
done
wait_all "${pids[@]}"
say "wave 2 dwtdct done, $(cat "${out}"_cpu*.jsonl | wc -l) records, failures so far $failed"

if [ "$failed" -eq 0 ]; then
  say "all waves done" > "${out}.done"
  say "all done, marker ${out}.done"
else
  say "$failed processes failed" > "${out}.failed"
  say "finished with $failed failed processes, marker ${out}.failed"
fi
