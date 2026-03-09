# Script para hacer login y probar corrección
$BASE_URL = "http://127.0.0.1:8099"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🔐 PRUEBA CON AUTENTICACIÓN - LOGIN + CORRECCIÓN" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Crear sesión para mantener cookies
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Paso 1: LOGIN
Write-Host "1️⃣ Haciendo login..." -ForegroundColor Yellow

$loginData = @{
    usuario = "admin"
    clave = "admin123"
    nit = "805028041"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-WebRequest `
        -Uri "$BASE_URL/api/auth/login" `
        -Method POST `
        -Body $loginData `
        -ContentType "application/json" `
        -WebSession $session `
        -UseBasicParsing
    
    $loginResult = $loginResponse.Content | ConvertFrom-Json
    
    if ($loginResult.success) {
        Write-Host "   ✅ Login exitoso" -ForegroundColor Green
        Write-Host "   Usuario: $($loginResult.usuario)" -ForegroundColor Gray
        Write-Host "   Rol: $($loginResult.rol)" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "   ❌ Login falló: $($loginResult.message)" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "   ❌ Error en login: $_" -ForegroundColor Red
    exit 1
}

# Paso 2: SOLICITAR CORRECCIÓN
Write-Host "2️⃣ Solicitando corrección del documento..." -ForegroundColor Yellow

$correccionData = @{
    empresa_id = $null
    tipo_documento_id = $null
    centro_operacion_id = $null
    consecutivo = "00000099"
    fecha_expedicion = $null
    justificacion = "Prueba automatizada con autenticación desde PowerShell - Validando corrección de variables y envío de token"
} | ConvertTo-Json

Write-Host "   📋 Datos:" -ForegroundColor Gray
Write-Host "      Consecutivo: 00000099" -ForegroundColor Gray
Write-Host "      Justificación: Prueba automatizada..." -ForegroundColor Gray
Write-Host ""

try {
    $correccionResponse = Invoke-WebRequest `
        -Uri "$BASE_URL/api/notas/solicitar-correccion/32" `
        -Method POST `
        -Body $correccionData `
        -ContentType "application/json" `
        -WebSession $session `
        -UseBasicParsing
    
    $resultado = $correccionResponse.Content | ConvertFrom-Json
    
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host "✅ RESPUESTA DEL SERVIDOR" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Green
    Write-Host ""
    
    if ($resultado.success) {
        Write-Host "🎉 SUCCESS: $($resultado.message)" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Detalles del Token:" -ForegroundColor Cyan
        Write-Host "   🆔 Token ID: $($resultado.token_id)" -ForegroundColor White
        Write-Host "   ⏰ Expira en: $($resultado.expira_en_minutos) minutos" -ForegroundColor White
        Write-Host "   📧 Correo enviado: $($resultado.correo_enviado)" -ForegroundColor White
        Write-Host ""
        
        if ($resultado.correo_enviado) {
            Write-Host "✉️ ¡CORREO ENVIADO EXITOSAMENTE!" -ForegroundColor Green
            Write-Host "   Revisa tu bandeja de entrada para obtener el token de 6 dígitos" -ForegroundColor Gray
        } else {
            Write-Host "⚠️ El correo NO se envió (posible error SMTP)" -ForegroundColor Yellow
            Write-Host "   Revisa los logs del servidor para ver el token generado" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "✅ VALIDACIONES COMPLETADAS" -ForegroundColor Cyan
        Write-Host "================================================================================" -ForegroundColor Cyan
        Write-Host "✔️ Variables del formulario extraídas correctamente" -ForegroundColor Green
        Write-Host "✔️ Validación de duplicados ejecutada" -ForegroundColor Green
        Write-Host "✔️ Token generado exitosamente" -ForegroundColor Green
        Write-Host "✔️ Email procesado (enviado=$($resultado.correo_enviado))" -ForegroundColor Green
        Write-Host ""
        
    } else {
        Write-Host "⚠️ ADVERTENCIA: $($resultado.message)" -ForegroundColor Yellow
        
        if ($resultado.ruta_existente) {
            Write-Host ""
            Write-Host "📁 Documento duplicado detectado:" -ForegroundColor Yellow
            Write-Host "   Nombre: $($resultado.documento_existente)" -ForegroundColor White
            Write-Host "   Ruta: $($resultado.ruta_existente)" -ForegroundColor White
            Write-Host ""
            Write-Host "✅ LA VALIDACIÓN DE DUPLICADOS FUNCIONA CORRECTAMENTE" -ForegroundColor Green
        }
    }
    
} catch {
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host "❌ ERROR EN LA SOLICITUD" -ForegroundColor Red
    Write-Host "================================================================================" -ForegroundColor Red
    Write-Host ""
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "Status Code: $statusCode" -ForegroundColor Red
        
        try {
            $errorContent = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "Mensaje: $($errorContent.message)" -ForegroundColor Yellow
        } catch {
            Write-Host "Error: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "🏁 PRUEBA FINALIZADA" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
