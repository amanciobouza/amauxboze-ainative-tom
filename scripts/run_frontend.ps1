$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath "$taskRoot/web"
npm.cmd run dev
