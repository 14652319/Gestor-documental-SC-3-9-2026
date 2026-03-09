# =====================================
# INICIADOR AUTOMÁTICO DE AMBOS SISTEMAS
# Supertiendas Cañaveral
# =====================================

Write-Host "`n" -NoNewline
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "║     🚀 INICIADOR AUTOMÁTICO DE SISTEMAS                       ║" -ForegroundColor Cyan
Write-Host "║     Supertiendas Cañaveral - Gestor Documental               ║" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Sistemas a iniciar:" -ForegroundColor Yellow
Write-Host "   1. Gestor Documental    (Puerto 8099)" -ForegroundColor White
Write-Host "   2. DIAN vs ERP          (Puerto 8097)" -ForegroundColor White
Write-Host ""

# Obtener directorio actual
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DIAN_DIR = Join-Path $PROJECT_DIR "Proyecto Dian Vs ERP v5.20251130"

# Verificar que Python esté instalado
Write-Host "🔍 Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Solución: Instala Python desde https://www.python.org" -ForegroundColor Yellow
    pause
    exit 1
}

# Verificar carpeta DIAN vs ERP
Write-Host ""
Write-Host "🔍 Verificando carpetas..." -ForegroundColor Cyan
if (-not (Test-Path $DIAN_DIR)) {
    Write-Host "❌ ERROR: No se encuentra la carpeta 'Proyecto Dian Vs ERP v5.20251130'" -ForegroundColor Red
    Write-Host ""
    Write-Host "📁 Ruta esperada: $DIAN_DIR" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "✅ Carpeta DIAN vs ERP encontrada" -ForegroundColor Green

# Verificar si los puertos ya están en uso
Write-Host ""
Write-Host "🔍 Verificando puertos..." -ForegroundColor Cyan
$puerto8099 = netstat -ano | Select-String ":8099" | Select-String "LISTENING"
$puerto8097 = netstat -ano | Select-String ":8097" | Select-String "LISTENING"

if ($puerto8099) {
    Write-Host "⚠️  Puerto 8099 ya está en uso" -ForegroundColor Yellow
    Write-Host "   ¿Deseas detener el proceso existente? (S/N): " -ForegroundColor Yellow -NoNewline
    $respuesta = Read-Host
    if ($respuesta -eq "S" -or $respuesta -eq "s") {
        Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force
        Start-Sleep 2
        Write-Host "✅ Procesos Python detenidos" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Puerto 8099 libre" -ForegroundColor Green
}

if ($puerto8097) {
    Write-Host "⚠️  Puerto 8097 ya está en uso" -ForegroundColor Yellow
} else {
    Write-Host "✅ Puerto 8097 libre" -ForegroundColor Green
}

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

# Iniciar Gestor Documental (Puerto 8099)
Write-Host "🟢 [1/2] Iniciando Gestor Documental (Puerto 8099)..." -ForegroundColor Green
Write-Host "📁 Directorio: $PROJECT_DIR" -ForegroundColor DarkGray
Write-Host ""

# Crear script temporal para Gestor
$scriptGestor = @"
`$Host.UI.RawUI.WindowTitle = '🟢 GESTOR DOCUMENTAL - Puerto 8099'
Write-Host '═══════════════════════════════════════════════════════════' -ForegroundColor Green
Write-Host '   GESTOR DOCUMENTAL - Puerto 8099' -ForegroundColor White
Write-Host '═══════════════════════════════════════════════════════════' -ForegroundColor Green
Write-Host ''
Write-Host '🐍 Activando virtualenv...' -ForegroundColor Yellow
cd '$PROJECT_DIR'
& .\.venv\Scripts\Activate.ps1
Write-Host '✅ Virtualenv activado' -ForegroundColor Green
Write-Host ''
Write-Host '🚀 Iniciando servidor Flask...' -ForegroundColor Yellow
Write-Host ''
python app.py
"@

$tempScriptGestor = Join-Path $env:TEMP "iniciar_gestor_$(Get-Random).ps1"
$scriptGestor | Out-File -FilePath $tempScriptGestor -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$tempScriptGestor"

Write-Host "✅ Terminal de Gestor Documental iniciada" -ForegroundColor Green
Write-Host "⏳ Esperando 5 segundos para que el servidor inicie..." -ForegroundColor Yellow
Start-Sleep 5

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

# Iniciar DIAN vs ERP (Puerto 8097)
Write-Host "🔵 [2/2] Iniciando DIAN vs ERP (Puerto 8097)..." -ForegroundColor Cyan
Write-Host "📁 Directorio: $DIAN_DIR" -ForegroundColor DarkGray
Write-Host ""

# Crear script temporal para DIAN
$scriptDian = @"
`$Host.UI.RawUI.WindowTitle = '🔵 DIAN VS ERP - Puerto 8097'
Write-Host '═══════════════════════════════════════════════════════════' -ForegroundColor Cyan
Write-Host '   DIAN VS ERP - Puerto 8097' -ForegroundColor White
Write-Host '═══════════════════════════════════════════════════════════' -ForegroundColor Cyan
Write-Host ''
Write-Host '🚀 Iniciando servidor Flask...' -ForegroundColor Yellow
Write-Host ''
cd '$DIAN_DIR'
python app.py
"@

$tempScriptDian = Join-Path $env:TEMP "iniciar_dian_$(Get-Random).ps1"
$scriptDian | Out-File -FilePath $tempScriptDian -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$tempScriptDian"

Write-Host "✅ Terminal de DIAN vs ERP iniciada" -ForegroundColor Green
Write-Host "⏳ Esperando 5 segundos para que el servidor inicie..." -ForegroundColor Yellow
Start-Sleep 5

Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""
Write-Host "✅ SISTEMAS INICIADOS CORRECTAMENTE" -ForegroundColor Green -BackgroundColor Black
Write-Host ""
Write-Host "📊 Estado de servidores:" -ForegroundColor Yellow
Write-Host "   🟢 Gestor Documental:  http://localhost:8099" -ForegroundColor Green
Write-Host "   🔵 DIAN vs ERP:        http://localhost:8097" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏰ Los servidores están iniciándose en ventanas separadas..." -ForegroundColor Yellow
Write-Host "   (Pueden tardar 5-10 segundos en estar completamente listos)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "💡 TIP: Deja las ventanas abiertas mientras trabajas" -ForegroundColor Magenta
Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

# Verificar que los servidores iniciaron
Write-Host "🔍 Verificando que los servidores estén en línea..." -ForegroundColor Cyan
Start-Sleep 2

$puerto8099OK = netstat -ano | Select-String ":8099" | Select-String "LISTENING"
$puerto8097OK = netstat -ano | Select-String ":8097" | Select-String "LISTENING"

if ($puerto8099OK) {
    Write-Host "   OK Puerto 8099: ACTIVO" -ForegroundColor Green
} else {
    Write-Host "   WAIT Puerto 8099: Iniciando..." -ForegroundColor Yellow
}

if ($puerto8097OK) {
    Write-Host "   OK Puerto 8097: ACTIVO" -ForegroundColor Green
} else {
    Write-Host "   WAIT Puerto 8097: Iniciando..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌐 Abriendo navegador en 3 segundos..." -ForegroundColor Yellow
Start-Sleep 3

# Abrir navegador
Start-Process "http://localhost:8099"

Write-Host ""
Write-Host "✨ ¡Listo! Ya puedes usar los sistemas." -ForegroundColor Green -BackgroundColor Black
Write-Host ""
Write-Host "📌 Para cerrar los servidores: Cierra las ventanas de PowerShell" -ForegroundColor Cyan
Write-Host ""

Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
