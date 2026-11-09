# Windows PowerShell. Запуск: .\01_start_nodes.ps1        (все три)
#                             .\01_start_nodes.ps1 -Node 1 (только rs1)
param([int]$Node = 0)
$base = Join-Path (Get-Location) "data"
function Start-Rs($n) {
  $port = 27100 + $n; $dir = Join-Path $base "rs$n"
  New-Item -ItemType Directory -Force $dir | Out-Null
  Start-Process mongod -ArgumentList "--replSet rsLab10 --port $port --dbpath `"$dir`" --bind_ip 127.0.0.1 --logpath `"$dir\mongod.log`""
  Write-Host "rs$n started on $port"
}
if ($Node -gt 0) { Start-Rs $Node } else { 1..3 | ForEach-Object { Start-Rs $_ } }
