#!/bin/sh
set -u

root=${DATA_ROOT:-data/images}
mode=list
scope=derived

for arg in "$@"; do
  case "$arg" in
    --yes) mode=delete ;;
    --all) scope=all ;;
    --data-root=*) root=${arg#--data-root=} ;;
    *) echo "usage: sh cleanup.sh [--data-root=PATH] [--all] [--yes]"; exit 2 ;;
  esac
done

targets="$root/work $root/images"
if [ "$scope" = all ]; then
  targets="$targets $root/smoke $root/test $root/null $root/models $root/sources"
fi
targets="$targets third_party .pytest_cache"

echo "data root $root, scope $scope, mode $mode"
total=0
for t in $targets; do
  if [ -e "$t" ]; then
    size=$(du -sh "$t" 2>/dev/null | cut -f1)
    echo "  $size  $t"
    total=$((total + 1))
  fi
done
find . -name __pycache__ -type d -not -path "./.venv/*" -not -path "./third_party/*" 2>/dev/null | while read -r d; do echo "  cache  $d"; done

if [ "$mode" = list ]; then
  echo "listed only, nothing deleted. Add --yes to delete these $total folders, --all to include the preprocessed splits, the models and the source archives."
  exit 0
fi

for t in $targets; do
  if [ -e "$t" ]; then
    rm -rf "$t"
    echo "deleted $t"
  fi
done
find . -name __pycache__ -type d -not -path "./.venv/*" -prune -exec rm -rf {} + 2>/dev/null
echo "done. Manifests, results, configs and code are untouched. Everything deleted is rebuilt by the commands in the README."
