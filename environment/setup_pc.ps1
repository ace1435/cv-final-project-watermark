$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $root ".venv"
if (-not (Test-Path $venv)) {
    py -3.10 -m venv $venv
}
$python = Join-Path $venv "Scripts\python.exe"
& $python -m pip install --quiet --upgrade pip
& $python -m pip install --quiet -r (Join-Path $PSScriptRoot "requirements.txt")
& $python -m pip install --quiet -e $root
& $python -m playwright install chromium
& $python -c "import torch, cv2, PIL; print('torch', torch.__version__, 'cv2', cv2.__version__, 'pillow', PIL.__version__)"
