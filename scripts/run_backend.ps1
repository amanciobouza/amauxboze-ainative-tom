$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
& "$taskRoot/.venv/Scripts/python.exe" -m uvicorn amauxboze.control_plane.app:application --factory --host 127.0.0.1 --port 8000
