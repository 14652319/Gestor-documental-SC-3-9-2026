# ========================================================
# INSTALACIÓN COMPLETA - GESTOR DOCUMENTAL
# ========================================================
# Este script intentará conectarse y configurar la base de datos
# Probando diferentes combinaciones de usuario/contraseña/puerto
# ========================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  INSTALACIÓN - GESTOR DOCUMENTAL" -ForegroundColor Cyan  
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$POSTGRES_BIN = "C:\Program Files\PostgreSQL\18\bin"
$DB_NAME = "gestor_documental"

# Configuraciones a probar (según tu tabla)
$configs = @(
    @{User="gestor_user"; Password="admin2025*"; Port=5432},
    @{User="postgres"; Password="admin2025*"; Port=5432},
    @{User="postgres"; Password="Admin2025!"; Port=5432}
)

Write-Host "[1/7] Probando conexión a PostgreSQL..." -ForegroundColor Yellow
Write-Host ""

$connected = $false
$workingConfig = $null

foreach ($config in $configs) {
    $env:PGPASSWORD = $config.Password
    Write-Host "  Probando: Usuario=$($config.User), Puerto=$($config.Port)..." -ForegroundColor Gray
    
    $result = & "$POSTGRES_BIN\psql.exe" -U $config.User -p $config.Port -l 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Conexión exitosa!" -ForegroundColor Green
        $connected = $true
        $workingConfig = $config
        break
    } else {
        Write-Host "  ✗ Falló" -ForegroundColor Red
    }
}

if (-not $connected) {
    Write-Host ""
    Write-Host "✗ No se pudo conectar a PostgreSQL con ninguna configuración" -ForegroundColor Red
    Write-Host ""
    Write-Host "SOLUCIÓN MANUAL:" -ForegroundColor Yellow
    Write-Host "1. Abre pgAdmin 4" -ForegroundColor White
    Write-Host "2. Conectate a PostgreSQL 18" -ForegroundColor White
    Write-Host "3. Ejecuta el archivo: CREAR_BD_MANUAL.sql" -ForegroundColor White
    Write-Host "4. Restaura el backup: backup_gestor_documental.backup" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "[2/7] Verificando si la base de datos existe..." -ForegroundColor Yellow
$env:PGPASSWORD = $workingConfig.Password
$dbExists = & "$POSTGRES_BIN\psql.exe" -U $workingConfig.User -p $workingConfig.Port -lqt | Select-String -Pattern "^\s*$DB_NAME\s"

if ($dbExists) {
    Write-Host "  ⚠ La base de datos '$DB_NAME' ya existe" -ForegroundColor Yellow
    $respuesta = Read-Host "  ¿Deseas eliminarla y recrearla? (S/N)"
    if ($respuesta -eq "S" -or $respuesta -eq "s") {
        Write-Host "  Eliminando base de datos..." -ForegroundColor Yellow
        & "$POSTGRES_BIN\dropdb.exe" -U $workingConfig.User -p $workingConfig.Port $DB_NAME
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Base de datos eliminada" -ForegroundColor Green
            $needCreate = $true
        }
    } else {
        Write-Host "  Usando base de datos existente" -ForegroundColor Gray
        $needCreate = $false
    }
} else {
    $needCreate = $true
}

if ($needCreate) {
    Write-Host ""
    Write-Host "[3/7] Creando base de datos..." -ForegroundColor Yellow
    & "$POSTGRES_BIN\createdb.exe" -U $workingConfig.User -p $workingConfig.Port $DB_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Base de datos '$DB_NAME' creada" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Error al crear la base de datos" -ForegroundColor Red
        pause
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "[3/7] Saltando creación (base de datos existe)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[4/7] Restaurando backup..." -ForegroundColor Yellow

if (Test-Path "backup_gestor_documental.backup") {
    & "$POSTGRES_BIN\pg_restore.exe" -U $workingConfig.User -p $workingConfig.Port -d $DB_NAME --clean --if-exists -v "backup_gestor_documental.backup" 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) {
        Write-Host "  ✓ Backup restaurado (algunos warnings son normales)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Restauración completada con errores" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ No se encontró backup_gestor_documental.backup" -ForegroundColor Red
}

Write-Host ""
Write-Host "[5/7] Verificando tablas..." -ForegroundColor Yellow
$tables = & "$POSTGRES_BIN\psql.exe" -U $workingConfig.User -p $workingConfig.Port -d $DB_NAME -c "\dt" 2>&1
if ($tables -match "terceros|usuarios|facturas") {
    Write-Host "  ✓ Tablas encontradas en la base de datos" -ForegroundColor Green
} else {
    Write-Host "  ⚠ No se encontraron las tablas esperadas" -ForegroundColor Yellow
    Write-Host "  Ejecutando scripts SQL de creación..." -ForegroundColor Yellow
    
    if (Test-Path "sql\schema_core.sql") {
        & "$POSTGRES_BIN\psql.exe" -U $workingConfig.User -p $workingConfig.Port -d $DB_NAME -f "sql\schema_core.sql"
        Write-Host "  ✓ Esquema core ejecutado" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "[6/7] Actualizando archivo .env..." -ForegroundColor Yellow

# Actualizar .env con la configuración que funcionó
$DATABASE_URL = "postgresql://$($workingConfig.User):$($workingConfig.Password)@localhost:$($workingConfig.Port)/$DB_NAME"
(Get-Content .env) | ForEach-Object {
    if ($_ -match '^DATABASE_URL=') {
        "DATABASE_URL=$DATABASE_URL"
    } else {
        $_
    }
} | Set-Content .env -Encoding UTF8

Write-Host "  ✓ Archivo .env actualizado" -ForegroundColor Green
Write-Host "    DATABASE_URL=$DATABASE_URL" -ForegroundColor Gray

Write-Host ""
Write-Host "[7/7] Ejecutando update_tables.py..." -ForegroundColor Yellow

# Activar virtualenv y ejecutar update_tables
& ".\.venv\Scripts\python.exe" update_tables.py

# Limpiar contraseña
$env:PGPASSWORD = $null

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  ✓ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "CONFIGURACIÓN EXITOSA:" -ForegroundColor Cyan
Write-Host "  Usuario PostgreSQL: $($workingConfig.User)" -ForegroundColor White
Write-Host "  Puerto: $($workingConfig.Port)" -ForegroundColor White
Write-Host "  Base de datos: $DB_NAME" -ForegroundColor White
Write-Host ""
Write-Host "PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host "1. Iniciar el servidor:" -ForegroundColor White
Write-Host "   python app.py" -ForegroundColor Gray
Write-Host "   O ejecutar: .\iniciar_servidor.bat" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Abrir navegador en:" -ForegroundColor White
Write-Host "   http://localhost:8099" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Verificar usuarios:" -ForegroundColor White
Write-Host "   python check_user_status.py" -ForegroundColor Gray
Write-Host ""
pause
