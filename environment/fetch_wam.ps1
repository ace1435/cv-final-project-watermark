$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$commit = Get-Content (Join-Path $PSScriptRoot "wam_commit.txt")
$dest = Join-Path $root "third_party\watermark_anything"
if (-not (Test-Path $dest)) {
    git clone --quiet https://github.com/facebookresearch/watermark-anything $dest
}
git -C $dest checkout --quiet $commit
git -C $dest log -1 --format="watermark_anything at %h %ad" --date=short
