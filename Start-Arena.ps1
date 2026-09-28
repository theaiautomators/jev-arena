param([switch]$Prepare, [string[]]$Models = @('laya','plumb','decider'))
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'Install uv from https://docs.astral.sh/uv/ then run this launcher again.' }
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Install Node.js 22 or newer from https://nodejs.org/ then run this launcher again.' }
uv sync --frozen --extra dev
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
npm.cmd ci
if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
npm.cmd run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
if ($Prepare) {
    & '.venv\Scripts\python.exe' -m arena.setup --models @Models
    if ($LASTEXITCODE -ne 0) { throw 'Preparation failed. Check .arena/setup.log.' }
}
Write-Host 'Jev Arena: http://127.0.0.1:8787 — keep this terminal open.'
& '.venv\Scripts\python.exe' -m uvicorn arena.api:app --host 127.0.0.1 --port 8787
