<#
.SYNOPSIS
    Levanta SESCO y lo publica en Internet con ngrok para probarlo desde el celular.

.DESCRIPTION
    Arranca tres procesos:
      1. El backend de Flask en el puerto 5000.
      2. El servidor de desarrollo de Vite en el puerto 5173.
      3. El túnel de ngrok hacia el puerto 5173.

    Se publica el servidor de Vite (y no el backend) porque el proxy de Vite
    ya reenvía las llamadas de /api al backend: así la aplicación completa
    queda bajo un único dominio HTTPS y el lector de QR puede usar la cámara
    en el celular (los navegadores solo dan acceso a la cámara en un origen
    seguro).

    Al abrir la URL en el celular, ngrok muestra su aviso una sola vez: hay
    que tocar "Visit Site". A partir de ahí queda en una cookie y funciona
    sin interrupciones.

.PARAMETER Puerto
    Puerto local del servidor de Vite. Por defecto 5173.

.PARAMETER Ssl
    Sirve el frontend con HTTPS y un certificado autofirmado. Se usa al entrar
    por la IP de la red local, porque los navegadores solo dan acceso a la
    cámara en un origen seguro. Con ngrok no hace falta: el túnel ya aporta el
    HTTPS.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\iniciar_celular.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\iniciar_celular.ps1 -Ssl
#>
param(
    [int]$Puerto = 5173,
    [switch]$Ssl
)

$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $PSScriptRoot
$log = Join-Path $env:TEMP 'sesco'

Write-Host ''
Write-Host '  SESCO — arranque para pruebas desde el celular' -ForegroundColor Cyan
Write-Host '  ---------------------------------------------' -ForegroundColor DarkCyan
Write-Host ''

# --- ¿Están el backend y la base de datos? -------------------------------
try {
    $salud = Invoke-WebRequest 'http://localhost:5000/api/health' -UseBasicParsing -TimeoutSec 3
    Write-Host "  [ok]   El backend ya responde en el puerto 5000." -ForegroundColor Green
} catch {
    Write-Host "  [falta] El backend no responde. Arranca primero:" -ForegroundColor Yellow
    Write-Host "         cd backend; ..\venv\Scripts\python wsgi.py" -ForegroundColor Yellow
    Write-Host ''
    Read-Host '  Pulsa Enter para continuar de todos modos'
}

# --- Servidor de Vite ------------------------------------------------------
Write-Host '  Arrancando el frontend...' -ForegroundColor Gray
if ($Ssl) {
    # El certificado autofirmado da el contexto seguro que exige la cámara.
    $env:VITE_USE_SSL = 'true'
    Write-Host '  Con HTTPS (certificado autofirmado) para entrar por la IP local.' -ForegroundColor Gray
} else {
    $env:VITE_USE_SSL = 'false'
}
$envFront = Join-Path $log 'frontend.log'
Start-Process -FilePath 'npm.cmd' `
    -ArgumentList 'run', 'dev', '--', '--port', "$Puerto" `
    -WorkingDirectory (Join-Path $raiz 'frontend') `
    -RedirectStandardOutput $envFront `
    -RedirectStandardError (Join-Path $log 'frontend.err') `
    -WindowStyle Hidden | Out-Null

Start-Sleep -Seconds 6

# --- Túnel de ngrok -------------------------------------------------------
Write-Host '  Arrancando el túnel de ngrok...' -ForegroundColor Gray
$envNgrok = Join-Path $log 'ngrok.log'
$proceso = Start-Process -FilePath 'ngrok' `
    -ArgumentList 'http', "$Puerto", '--log', 'stdout', '--log-format', 'json' `
    -RedirectStandardOutput $envNgrok `
    -RedirectStandardError (Join-Path $log 'ngrok.err') `
    -WindowStyle Hidden -PassThru

Start-Sleep -Seconds 8

$url = $null
if (Test-Path $envNgrok) {
    $linea = Get-Content $envNgrok | Select-String -Pattern '"url":"https' | Select-Object -Last 1
    if ($linea -and $linea.Line -match '"url":"(https://[^"]+)"') {
        $url = $matches[1]
    }
}

Write-Host ''
Write-Host '  ---------------------------------------------------------' -ForegroundColor DarkCyan
if ($url) {
    Write-Host "  Abre esta dirección en el celular:" -ForegroundColor Green
    Write-Host ''
    Write-Host "      $url" -ForegroundColor White
    Write-Host ''
    Write-Host '  La primera vez ngrok pide que toques "Visit Site". Después' -ForegroundColor Gray
    Write-Host '  queda en cookie y el lector de QR puede usar la cámara.' -ForegroundColor Gray
} else {
    Write-Host '  No se pudo leer la URL de ngrok. Revisa el registro:' -ForegroundColor Yellow
    Write-Host "      $envNgrok" -ForegroundColor Yellow
}
Write-Host ''
Write-Host '  Para detener todo: Ctrl+C y cerrar las ventanas de los procesos.' -ForegroundColor Gray
Write-Host '  ---------------------------------------------------------' -ForegroundColor DarkCyan
Write-Host ''

Read-Host '  Pulsa Enter para dejar los procesos corriendo en segundo plano'
