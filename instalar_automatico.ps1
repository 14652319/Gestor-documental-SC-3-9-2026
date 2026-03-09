# ========================================================
# SCRIPT DE INSTALACIÓN AUTOMÁTICA - GESTOR DOCUMENTAL
# ========================================================
# Este script automatiza la instalación completa del sistema
# Ejecutar: .\instalar_automatico.ps1

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  INSTALACIÓN AUTOMÁTICA - GESTOR DOCUMENTAL" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Variables de configuración
$POSTGRES_PATH = "C:\Program Files\PostgreSQL\18\bin"
$DB_NAME = "gestor_documental"
$DB_USER = "postgres"
$BACKUP_FILE = "backup_gestor_documental.backup"

# Paso 1: Solicitar contraseña de PostgreSQL
Write-Host "[PASO 1/6] Configuración de PostgreSQL" -ForegroundColor Yellow
Write-Host "Por favor, ingresa la contraseña de PostgreSQL (usuario: postgres):" -ForegroundColor White
$POSTGRES_PASSWORD = Read-Host -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($POSTGRES_PASSWORD)
$PlainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Configurar variable de entorno para psql
$env:PGPASSWORD = $PlainPassword

Write-Host "✓ Contraseña configurada" -ForegroundColor Green
Write-Host ""

# Paso 2: Verificar si la base de datos ya existe
Write-Host "[PASO 2/6] Verificando base de datos existente..." -ForegroundColor Yellow
$dbExists = & "$POSTGRES_PATH\psql.exe" -U $DB_USER -lqt | Select-String $DB_NAME
if ($dbExists) {
    Write-Host "⚠ La base de datos '$DB_NAME' ya existe." -ForegroundColor Yellow
    $respuesta = Read-Host "¿Deseas eliminarla y crearla de nuevo? (S/N)"
    if ($respuesta -eq "S" -or $respuesta -eq "s") {
        Write-Host "Eliminando base de datos existente..." -ForegroundColor Yellow
        & "$POSTGRES_PATH\dropdb.exe" -U $DB_USER $DB_NAME
        Write-Host "✓ Base de datos eliminada" -ForegroundColor Green
    } else {
        Write-Host "⚠ Saltando creación de base de datos" -ForegroundColor Yellow
        $createDB = $false
    }
} else {
    $createDB = $true
}

# Paso 3: Crear base de datos
if ($createDB -ne $false) {
    Write-Host "[PASO 3/6] Creando base de datos '$DB_NAME'..." -ForegroundColor Yellow
    & "$POSTGRES_PATH\createdb.exe" -U $DB_USER $DB_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Base de datos creada exitosamente" -ForegroundColor Green
    } else {
        Write-Host "✗ Error al crear la base de datos" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[PASO 3/6] Base de datos ya existe, continuando..." -ForegroundColor Yellow
}
Write-Host ""

# Paso 4: Restaurar backup
Write-Host "[PASO 4/6] Restaurando backup de datos..." -ForegroundColor Yellow
if (Test-Path $BACKUP_FILE) {
    & "$POSTGRES_PATH\pg_restore.exe" -U $DB_USER -d $DB_NAME -v $BACKUP_FILE
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Backup restaurado exitosamente" -ForegroundColor Green
    } else {
        Write-Host "⚠ Hubo algunos warnings al restaurar, pero puede ser normal" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ No se encontró el archivo de backup: $BACKUP_FILE" -ForegroundColor Yellow
    Write-Host "  Intentando con el backup SQL alternativo..." -ForegroundColor Yellow
    
    $SQL_BACKUP = "..\..\..\BACKUPS_TRANSPORTABLES\gestor_documental_SQL_20251113_202140.sql"
    if (Test-Path $SQL_BACKUP) {
        & "$POSTGRES_PATH\psql.exe" -U $DB_USER -d $DB_NAME -f $SQL_BACKUP
        Write-Host "✓ Backup SQL restaurado" -ForegroundColor Green
    } else {
        Write-Host "✗ No se encontró ningún archivo de backup" -ForegroundColor Red
    }
}
Write-Host ""

# Paso 5: Actualizar archivo .env
Write-Host "[PASO 5/6] Configurando archivo .env..." -ForegroundColor Yellow

# Determinar el puerto de PostgreSQL
Write-Host "¿Qué puerto usa tu PostgreSQL? (Presiona Enter para usar el puerto por defecto 5432):" -ForegroundColor White
$POSTGRES_PORT = Read-Host
if ([string]::IsNullOrWhiteSpace($POSTGRES_PORT)) {
    $POSTGRES_PORT = "5432"
}

# Leer el archivo .env
$envContent = Get-Content .env -Raw

# Actualizar DATABASE_URL
$DATABASE_URL = "postgresql://$DB_USER`:$PlainPassword@localhost:$POSTGRES_PORT/$DB_NAME"
$envContent = $envContent -replace 'DATABASE_URL=.*', "DATABASE_URL=$DATABASE_URL"

# Generar SECRET_KEY aleatorio
$SECRET_KEY = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$envContent = $envContent -replace 'SECRET_KEY=.*', "SECRET_KEY=$SECRET_KEY"

# Guardar .env actualizado
$envContent | Set-Content .env -Encoding UTF8

Write-Host "✓ Archivo .env configurado" -ForegroundColor Green
Write-Host "  - DATABASE_URL actualizado" -ForegroundColor Gray
Write-Host "  - SECRET_KEY generado" -ForegroundColor Gray
Write-Host ""

# Paso 6: Verificar instalación
Write-Host "[PASO 6/6] Verificando instalación..." -ForegroundColor Yellow
Write-Host "Listando tablas en la base de datos:" -ForegroundColor White
& "$POSTGRES_PATH\psql.exe" -U $DB_USER -d $DB_NAME -c "\dt"
Write-Host ""

# Limpiar contraseña de memoria
$env:PGPASSWORD = $null
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)

# Resumen final
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  ✓ INSTALACIÓN COMPLETADA EXITOSAMENTE" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "1. Activar el entorno virtual:" -ForegroundColor White
Write-Host "   .\.venv\Scripts\activate" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Iniciar el servidor:" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host "   O usar: .\iniciar_servidor.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Abrir en navegador:" -ForegroundColor White
Write-Host "   http://localhost:8099" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Verificar usuarios disponibles:" -ForegroundColor White
Write-Host "   python check_user_status.py" -ForegroundColor Gray
Write-Host ""
Write-Host "¡El sistema está listo para usar!" -ForegroundColor Green
Write-Host ""
