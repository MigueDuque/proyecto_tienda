<#
Instala lo necesario (Docker Desktop, Node.js) y levanta el proyecto Granero
con un solo doble clic. Pensado para Windows 10/11.

Uso: doble clic en "Instalar y Ejecutar.bat" (en la raiz del repo), que
invoca este script.
#>

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "    OK: $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    AVISO: $msg" -ForegroundColor Yellow }

function Test-CommandExists($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Test-IsAdmin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($id)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

Write-Host "==================================================="
Write-Host "  Granero - instalador y arranque del proyecto"
Write-Host "==================================================="

# Instalar Docker Desktop / Node.js requiere permisos de administrador.
# Si faltan y no estamos elevados, relanzamos este mismo script como admin.
$needsDocker = -not (Test-CommandExists "docker")
$needsNode = -not (Test-CommandExists "node")

if (($needsDocker -or $needsNode) -and -not (Test-IsAdmin)) {
    Write-Step "Se necesitan permisos de administrador para instalar dependencias faltantes."
    Write-Host "    Se abrira una ventana pidiendo confirmacion (UAC). Aceptala para continuar."
    Start-Process powershell -Verb RunAs -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`""
    )
    exit
}

Write-Step "Verificando winget (gestor de paquetes de Windows)"
if (-not (Test-CommandExists "winget")) {
    Write-Warn "winget no esta disponible en este equipo."
    Write-Host "    Instala 'App Installer' desde la Microsoft Store y vuelve a ejecutar este archivo:"
    Write-Host "    https://apps.microsoft.com/detail/9nblggh4nns1"
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Ok "winget disponible"

Write-Step "Verificando Docker"
if (Test-CommandExists "docker") {
    Write-Ok "Docker ya esta instalado"
} else {
    Write-Step "Instalando Docker Desktop (puede tardar varios minutos)..."
    winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
    Write-Warn "Docker Desktop fue instalado."
    Write-Warn "Si Windows te pide REINICIAR el equipo (para habilitar WSL2), hazlo y luego"
    Write-Warn "vuelve a ejecutar 'Instalar y Ejecutar.bat' para continuar."
    Read-Host "Presiona Enter para continuar (si Docker Desktop se abrio, acepta sus terminos de uso)"
}

Write-Step "Verificando Node.js (opcional, mejora el autocompletado del editor)"
if (Test-CommandExists "node") {
    Write-Ok "Node.js ya esta instalado ($(node --version))"
} else {
    Write-Step "Instalando Node.js LTS..."
    winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
    Write-Ok "Node.js instalado"
    Write-Warn "Puede que debas cerrar y volver a abrir esta ventana para que 'node' quede disponible."
}

Write-Step "Verificando que Docker Desktop este corriendo"
$dockerReady = $false
try { docker info 2>&1 | Out-Null; $dockerReady = $true } catch {}

if (-not $dockerReady) {
    $dockerExe = "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerExe) {
        Write-Step "Iniciando Docker Desktop..."
        Start-Process $dockerExe
    }
    Write-Host "    Esperando a que Docker Desktop inicie (hasta 3 minutos)..."
    $elapsed = 0
    while (-not $dockerReady -and $elapsed -lt 180) {
        Start-Sleep -Seconds 5
        $elapsed += 5
        try { docker info 2>&1 | Out-Null; $dockerReady = $true } catch {}
    }
}

if (-not $dockerReady) {
    Write-Warn "Docker Desktop no respondio a tiempo."
    Write-Warn "Abrelo manualmente desde el menu de inicio y vuelve a ejecutar este archivo."
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Ok "Docker esta corriendo"

Write-Step "Preparando archivo .env"
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Ok ".env creado a partir de .env.example"
} else {
    Write-Ok ".env ya existe, no se sobreescribe"
}

if (Test-CommandExists "npm") {
    Write-Step "Instalando dependencias del frontend localmente (para el editor)"
    Push-Location "frontend"
    try {
        npm install --no-audit --no-fund
        Write-Ok "Dependencias del frontend instaladas"
    } catch {
        Write-Warn "No se pudieron instalar las dependencias locales del frontend (no es critico, Docker las instala igual)"
    } finally {
        Pop-Location
    }
}

Write-Step "Construyendo y levantando los contenedores (la primera vez puede tardar varios minutos)"
docker compose up -d --build

Write-Step "Esperando a que el backend responda"
$backendReady = $false
$elapsed = 0
while (-not $backendReady -and $elapsed -lt 120) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3
        if ($resp.StatusCode -eq 200) { $backendReady = $true }
    } catch {}
    if (-not $backendReady) { Start-Sleep -Seconds 3; $elapsed += 3 }
}

if ($backendReady) {
    Write-Ok "Backend listo"
} else {
    Write-Warn "El backend tardo en responder. Revisa los logs con: docker compose logs backend"
}

Write-Host ""
Write-Host "==================================================="
Write-Host "  Listo!" -ForegroundColor Green
Write-Host "==================================================="
Write-Host ""
Write-Host "  Frontend:  http://localhost:5173"
Write-Host "  API/Docs:  http://localhost:8000/docs"
Write-Host "  Adminer:   http://localhost:8080"
Write-Host ""
Write-Host "  Usuario demo:     admin@granero.com"
Write-Host "  Contrasena demo:  admin123"
Write-Host ""

Start-Process "http://localhost:5173"

Read-Host "Presiona Enter para cerrar esta ventana"
