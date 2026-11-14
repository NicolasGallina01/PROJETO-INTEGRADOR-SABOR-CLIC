param([ValidateRange(1024,65535)][int]$Port = 5001)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Ambiente Python ausente. Crie .venv e instale requirements.txt antes de iniciar.'
}
& $python -m flask --app app:create_app check-db
if ($LASTEXITCODE -ne 0) { throw 'MySQL indisponivel. Inicie o MySQL e confira o arquivo .env.' }
Write-Host "Sistema local: http://127.0.0.1:$Port/"
& $python -m flask --app app:create_app run --host 127.0.0.1 --port $Port
exit $LASTEXITCODE
