@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  🧹 LIMPIEZA DE CACHÉ DE EDGE - GESTOR DOCUMENTAL         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📌 Cerrando todas las ventanas de Edge...
taskkill /F /IM msedge.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 🗑️  Limpiando caché de navegación...
RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 8

echo.
echo 🗑️  Limpiando cookies y datos de sesión...
RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 2

echo.
echo 🗑️  Limpiando historial...
RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 1

echo.
echo 🗑️  Limpiando datos de formularios...
RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 16

echo.
echo ✅ CACHÉ LIMPIADA COMPLETAMENTE
echo.
echo 🚀 Abriendo Edge en modo incógnito con la URL correcta...
timeout /t 2 /nobreak >nul
start msedge --inprivate http://localhost:8099/dian_vs_erp/cargar_archivos

echo.
echo ✅ ¡Listo! Edge abierto en modo incógnito
echo 📍 URL: http://localhost:8099/dian_vs_erp/cargar_archivos
echo.
echo 🔍 VERIFICA QUE VEAS:
echo    ✓ Título: "🚀🚀🚀 SELECCIÓN MÚLTIPLE ACTIVA v3.0 🚀🚀🚀"
echo    ✓ Botón: "📊 Volver al Visor V2"
echo.
pause
