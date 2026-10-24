param([int]$Port=8765,[switch]$NoBrowser,[string]$PartsModel='')
$ErrorActionPreference='Stop'
$projectDir=$PSScriptRoot
if ($PartsModel) {
    if (-not (Test-Path -LiteralPath $PartsModel -PathType Leaf)) {throw 'Specified parts model was not found.'}
    $env:STUDENT2_PARTS_MODEL=(Resolve-Path -LiteralPath $PartsModel).Path
}
$workspaceDir=Split-Path (Split-Path $projectDir -Parent) -Parent
$pythonCandidates=@((Join-Path $projectDir '.venv\Scripts\python.exe'),(Join-Path $workspaceDir 'work\runtime\python-env\Scripts\python.exe'))
$pythonPath=$pythonCandidates | Where-Object {Test-Path -LiteralPath $_} | Select-Object -First 1
if (-not $pythonPath) {throw 'Python environment missing. Run setup.ps1 first.'}
$url="http://127.0.0.1:$Port"
$isReady=$false
try {$health=Invoke-RestMethod "$url/api/health" -TimeoutSec 2; $isReady=($health.moduleId -eq 'student2-vehicle-parts-demo' -or $health.partsSource -eq 'https://huggingface.co/Majorburn/yolov11-carparts-seg')} catch {}
if (-not $isReady) {
    New-Item -ItemType Directory -Path (Join-Path $projectDir 'data\config\Ultralytics') -Force | Out-Null
    $env:YOLO_CONFIG_DIR=Join-Path $projectDir 'data\config'
    $env:PYTHONIOENCODING='utf-8'
    $arguments="-m uvicorn ai.server:app --app-dir `"$projectDir`" --host 127.0.0.1 --port $Port"
    $process=Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $projectDir -WindowStyle Hidden -RedirectStandardOutput (Join-Path $projectDir 'data\server.log') -RedirectStandardError (Join-Path $projectDir 'data\server-error.log') -PassThru
    $process.Id | Set-Content -LiteralPath (Join-Path $projectDir 'data\server-pid.txt')
    for ($attempt=0;$attempt -lt 60;$attempt++) {
        if ($process.HasExited) {throw "Server exited. Read data/server-error.log."}
        try {$health=Invoke-RestMethod "$url/api/health" -TimeoutSec 1; if ($health.status -eq 'ok') {$isReady=$true;break}} catch {}
        Start-Sleep -Milliseconds 500
    }
}
if (-not $isReady) {throw 'Server startup timed out. Read data/server-error.log.'}
if ($health.serverPid) {$health.serverPid | Set-Content -LiteralPath (Join-Path $projectDir 'data\server-pid.txt')}
Write-Output "Student 2 demo is running: $url"
if (-not $NoBrowser) {Start-Process $url}
