param([switch]$NoBrowser, [switch]$Production)
$ErrorActionPreference = "Stop"
$taskRoot = $PSScriptRoot
Set-Location -LiteralPath $taskRoot
if (-not (Test-Path -LiteralPath "$taskRoot/.venv/Scripts/python.exe")) {
    if (Get-Command uv -ErrorAction SilentlyContinue) { uv sync --extra dev }
    else { python -m venv .venv; & "$taskRoot/.venv/Scripts/python.exe" -m pip install -e ".[dev]" }
    if ($LASTEXITCODE -ne 0) { throw "Python setup failed" }
}
if (-not (Test-Path -LiteralPath "$taskRoot/web/node_modules")) {
    Push-Location -LiteralPath "$taskRoot/web"
    try { npm.cmd ci; if ($LASTEXITCODE -ne 0) { throw "Frontend setup failed" } } finally { Pop-Location }
}
$taskPython = Join-Path $taskRoot ".venv/Scripts/python.exe"
$taskFrontend = $null
try {
    if ($Production) {
        Push-Location -LiteralPath "$taskRoot/web"
        try { npm.cmd run build; if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" } } finally { Pop-Location }
        $taskUrl = "http://127.0.0.1:8000"
    } else {
        $taskFrontend = Start-Process -FilePath (Get-Command node.exe).Source -ArgumentList @("node_modules/vite/bin/vite.js", "--host", "127.0.0.1", "--port", "3000", "--strictPort") -WorkingDirectory "$taskRoot/web" -WindowStyle Hidden -PassThru
        $taskUrl = "http://127.0.0.1:3000"
    }
    Write-Host "Amaux Boze Company OS: $taskUrl"
    Write-Host "Ctrl+C stops the local services. LM Studio is optional for simulation."
    if (-not $NoBrowser) { Start-Process $taskUrl }
    & $taskPython -m uvicorn amauxboze.control_plane.app:application --factory --host 127.0.0.1 --port 8000
} finally {
    if ($null -ne $taskFrontend -and -not $taskFrontend.HasExited) { Stop-Process -Id $taskFrontend.Id }
}
