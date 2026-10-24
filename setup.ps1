param([string]$PythonPath='python')
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
& $PythonPath -m venv .venv
if ($LASTEXITCODE -ne 0) {throw 'Install Python 3.12 first, or pass -PythonPath with its executable.'}
$pythonExe=Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $pythonExe -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) {throw 'CPU PyTorch installation failed.'}
& $pythonExe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {throw 'Dependency installation failed.'}
& $pythonExe scripts\download_models.py
if ($LASTEXITCODE -ne 0) {throw 'Model download or checksum verification failed.'}
Write-Output 'Ready. Double-click start.cmd to launch.'
