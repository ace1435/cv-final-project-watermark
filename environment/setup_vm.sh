#!/bin/sh
set -e

host=${1:-vm28}
admin=${2:-vm28admin}
remote=${3:-vm}
venv=/home/student/venv
work=/home/student/work
data=/home/student/data
bare=/home/student/repo.git

branch=$(git rev-parse --abbrev-ref HEAD)

ssh -o BatchMode=yes "$admin" "sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-venv python3-pip unzip tmux git"
ssh -o BatchMode=yes "$host" "mkdir -p $data/sources $data/images $data/logs $data/work $data/models"
ssh -o BatchMode=yes "$host" "test -d $bare || git init -q --bare $bare"
ssh -o BatchMode=yes "$host" "test -d $work || git clone -q $bare $work"
git remote get-url "$remote" >/dev/null 2>&1 || git remote add "$remote" "$host:$bare"
git push -q "$remote" "$branch:$branch"
ssh -o BatchMode=yes "$host" "git -C $work fetch -q origin && git -C $work checkout -q $branch && git -C $work reset -q --hard origin/$branch"
ssh -o BatchMode=yes "$host" "test -d $venv || python3 -m venv $venv"
ssh -o BatchMode=yes "$host" "$venv/bin/python -m pip install -q --upgrade pip"
ssh -o BatchMode=yes "$host" "$venv/bin/python -m pip install -q torch==2.14.0+cu126 torchvision==0.29.0+cu126 --index-url https://download.pytorch.org/whl/cu126"
ssh -o BatchMode=yes "$host" "$venv/bin/python -m pip install -q -r $work/environment/requirements.txt"
ssh -o BatchMode=yes "$host" "$venv/bin/python -m pip install -q -e $work"
ssh -o BatchMode=yes "$host" "$venv/bin/playwright install chromium"
ssh -o BatchMode=yes "$admin" "sudo $venv/bin/playwright install-deps chromium"
ssh -o BatchMode=yes "$host" "cd $work && $venv/bin/python environment/download_models.py --root $data/models"
ssh -o BatchMode=yes "$host" "cd $work && $venv/bin/python environment/gpu_check.py"
ssh -o BatchMode=yes "$host" "nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv"
