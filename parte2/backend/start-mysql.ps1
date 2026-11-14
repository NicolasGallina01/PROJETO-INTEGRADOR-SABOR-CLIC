$mysqlExe = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
$configPath = Join-Path $PSScriptRoot "mysql-local.ini"

if (-not (Test-Path -LiteralPath $mysqlExe)) {
    throw "MySQL Server 8.0 nao foi encontrado em $mysqlExe"
}

$listener = Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    exit 0
}

Start-Process -FilePath $mysqlExe `
    -ArgumentList "--defaults-file=$configPath" `
    -WindowStyle Hidden

Start-Sleep -Seconds 4
if (-not (Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue)) {
    throw "O MySQL nao iniciou. Consulte o arquivo .err no diretorio de dados."
}
