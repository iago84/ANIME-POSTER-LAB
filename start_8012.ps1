# ANIME POSTER LAB — arranque local de la API FastAPI
# Uso:  .\start_8012.ps1
# Puerto: $env:APP_PORT > APP_PORT de .env > 8012
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$port = $env:APP_PORT
if (-not $port -and (Test-Path ".env")) {
    $m = Select-String -Path ".env" -Pattern '^\s*APP_PORT\s*=\s*(\d+)' | Select-Object -First 1
    if ($m) { $port = $m.Matches[0].Groups[1].Value }
}
if (-not $port) { $port = "8012" }

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "ANIME POSTER LAB -> http://127.0.0.1:$port  (docs interactivas en /docs)"
& $py -m uvicorn web.backend.main:app --host 127.0.0.1 --port $port --reload
