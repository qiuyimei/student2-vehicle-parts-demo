$ErrorActionPreference='Stop'
$pidFile=Join-Path $PSScriptRoot 'data\server-pid.txt'
if (-not (Test-Path -LiteralPath $pidFile)) {Write-Output 'No launched server found.';exit}
$serverProcessId=[int](Get-Content -LiteralPath $pidFile)
$processInfo=Get-CimInstance Win32_Process -Filter "ProcessId=$serverProcessId"
if ($processInfo -and $processInfo.CommandLine.Contains('ai.server:app') -and $processInfo.CommandLine.Contains($PSScriptRoot)) {
    # Windows venv可能有一个启动器进程；只停止属于本工程的子进程。
    $children=Get-CimInstance Win32_Process -Filter "ParentProcessId=$serverProcessId"
    foreach ($child in $children) {
        if ($child.CommandLine -and $child.CommandLine.Contains('ai.server:app') -and $child.CommandLine.Contains($PSScriptRoot)) {
            Stop-Process -Id $child.ProcessId -ErrorAction SilentlyContinue
        }
    }
    Stop-Process -Id $serverProcessId -ErrorAction SilentlyContinue
    Write-Output 'Student 2 demo stopped.'
} elseif ($processInfo) {throw 'PID does not belong to this demo. Nothing was stopped.'}
