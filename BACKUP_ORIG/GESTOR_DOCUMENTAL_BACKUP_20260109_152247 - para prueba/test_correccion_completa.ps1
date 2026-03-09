# Script para probar el flujo completo de corrección de documentos
# Simula el navegador haciendo las peticiones

$BASE_URL = "http://127.0.0.1:8099"
$documento_id = 32

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🧪 PRUEBA COMPLETA - FLUJO DE CORRECCIÓN DE DOCUMENTOS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Crear sesión (simular cookies del navegador)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Write-Host "1️⃣ Iniciando sesión de prueba..." -ForegroundColor Yellow
Write-Host "   Nota: Esta prueba NO requiere login porque simula una sesión activa" -ForegroundColor Gray
Write-Host ""

# Paso 2: Solicitar corrección
Write-Host "2️⃣ Solicitando corrección de documento ID $documento_id..." -ForegroundColor Yellow

$datos = @{
    empresa_id = $null
    tipo_documento_id = $null
    centro_operacion_id = $null
    consecutivo = "00000099"
    fecha_expedicion = $null
    justificacion = "Prueba automatizada del sistema de corrección de documentos desde PowerShell"
} | ConvertTo-Json

Write-Host "   📋 Datos enviados:" -ForegroundColor Gray
Write-Host "      - Consecutivo nuevo: 00000099" -ForegroundColor Gray
Write-Host "      - Justificación: Prueba automatizada..." -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-WebRequest `
        -Uri "$BASE_URL/api/notas/solicitar-correccion/$documento_id" `
        -Method POST `
        -Body $datos `
        -ContentType "application/json" `
        -WebSession $session `
        -UseBasicParsing `
        -ErrorAction Stop
    
    Write-Host "   ✅ Petición enviada - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host ""
    
    $resultado = $response.Content | ConvertFrom-Json
    
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "✅ RESPUESTA DEL SERVIDOR" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Green
    
    if ($resultado.success) {
        Write-Host "🎉 SUCCESS: $($resultado.message)" -ForegroundColor Green
        Write-Host ""
        Write-Host "📧 Correo enviado: $($resultado.correo_enviado)" -ForegroundColor Cyan
        Write-Host "🆔 Token ID: $($resultado.token_id)" -ForegroundColor Cyan
        Write-Host "⏰ Expira en: $($resultado.expira_en_minutos) minutos" -ForegroundColor Cyan
        Write-Host ""
        
        if ($resultado.correo_enviado) {
            Write-Host "✉️ CORREO ENVIADO EXITOSAMENTE" -ForegroundColor Green
            Write-Host "   Revisa tu bandeja de entrada" -ForegroundColor Gray
        } else {
            Write-Host "⚠️ El correo NO se envió" -ForegroundColor Yellow
            Write-Host "   Revisa los logs del servidor para ver el token generado" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "📝 SIGUIENTE PASO: VALIDAR TOKEN" -ForegroundColor Cyan
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "Para validar el token, necesitas:" -ForegroundColor Gray
        Write-Host "1. Obtener el token de 6 dígitos (del correo o de los logs)" -ForegroundColor Gray
        Write-Host "2. Ejecutar:" -ForegroundColor Gray
        Write-Host ""
        Write-Host '   $token = "123456"  # Reemplaza con el token real' -ForegroundColor White
        Write-Host '   $body = @{ token = $token } | ConvertTo-Json' -ForegroundColor White
        Write-Host "   Invoke-WebRequest ``" -ForegroundColor White
        Write-Host "       -Uri `"$BASE_URL/api/notas/validar-correccion/$($resultado.token_id)`" ``" -ForegroundColor White
        Write-Host "       -Method POST ``" -ForegroundColor White
        Write-Host "       -Body `$body ``" -ForegroundColor White
        Write-Host "       -ContentType `"application/json`"" -ForegroundColor White
        Write-Host ""
        
    } else {
        Write-Host "❌ ERROR: $($resultado.message)" -ForegroundColor Red
        
        # Si hay información de duplicado
        if ($resultado.ruta_existente) {
            Write-Host ""
            Write-Host "📁 Documento duplicado encontrado:" -ForegroundColor Yellow
            Write-Host "   Nombre: $($resultado.documento_existente)" -ForegroundColor Gray
            Write-Host "   Ruta: $($resultado.ruta_existente)" -ForegroundColor Gray
            Write-Host ""
            Write-Host "✅ LA VALIDACIÓN DE DUPLICADOS FUNCIONA CORRECTAMENTE" -ForegroundColor Green
        }
    }
    
} catch {
    $errorDetails = $_.ErrorDetails.Message
    
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host "❌ ERROR EN LA PETICIÓN" -ForegroundColor Red
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host ""
    
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "🔒 Error 401: No autorizado" -ForegroundColor Yellow
        Write-Host "   El servidor requiere autenticación" -ForegroundColor Gray
        Write-Host ""
        Write-Host "💡 Solución:" -ForegroundColor Cyan
        Write-Host "   Esta prueba debe ejecutarse con una sesión activa" -ForegroundColor Gray
        Write-Host "   Haz login en el navegador primero en: $BASE_URL" -ForegroundColor Gray
        
    } elseif ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "🔍 Error 404: Ruta no encontrada" -ForegroundColor Yellow
        Write-Host "   La ruta /api/notas/solicitar-correccion/$documento_id no existe" -ForegroundColor Gray
        Write-Host ""
        Write-Host "💡 Posibles causas:" -ForegroundColor Cyan
        Write-Host "   - El servidor no cargó el módulo de notas contables" -ForegroundColor Gray
        Write-Host "   - El blueprint no está registrado correctamente" -ForegroundColor Gray
        
    } elseif ($_.Exception.Response.StatusCode -eq 500) {
        Write-Host "💥 Error 500: Error interno del servidor" -ForegroundColor Red
        Write-Host ""
        if ($errorDetails) {
            try {
                $errorJson = $errorDetails | ConvertFrom-Json
                Write-Host "Mensaje: $($errorJson.message)" -ForegroundColor Gray
            } catch {
                Write-Host "Detalles: $errorDetails" -ForegroundColor Gray
            }
        }
        
    } else {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        Write-Host "Mensaje: $($_.Exception.Message)" -ForegroundColor Gray
        
        if ($errorDetails) {
            Write-Host ""
            Write-Host "Detalles del error:" -ForegroundColor Yellow
            Write-Host $errorDetails -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🏁 PRUEBA FINALIZADA" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
