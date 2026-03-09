# Sistema de Backup Automático - Gestor Documental

## 📋 Descripción General

Sistema completo de copias de seguridad para el Gestor Documental de Supertiendas Cañaveral. Realiza backups automáticos de:

- ✅ **Base de Datos PostgreSQL** (pg_dump formato comprimido)
- ✅ **Archivos del Sistema** (documentos_terceros, documentos_contables, facturas_digitales)
- ✅ **Código Fuente** (todo el proyecto excluyendo virtualenv y datos)

## 🚀 Instalación Rápida

### 1. Instalar el Sistema

```powershell
# Desde el directorio raíz del proyecto
python instalar_sistema_backup.py
```

Este script:
- ✅ Crea tablas `configuracion_backup` y `historial_backup`
- ✅ Inicializa configuración por defecto
- ✅ Crea directorios de destino en `C:\Backups_GestorDocumental\`
- ✅ Verifica que pg_dump esté instalado
- ✅ Ejecuta backup de prueba (opcional)

### 2. Verificar PostgreSQL

El sistema requiere `pg_dump.exe` para backups de base de datos:

```powershell
# Verificar si está instalado
pg_dump --version

# Si NO está instalado:
# 1. Descargar PostgreSQL desde https://www.postgresql.org/download/
# 2. Durante instalación, marcar "Agregar al PATH"
# 3. O agregar manualmente: C:\Program Files\PostgreSQL\16\bin
```

### 3. Primera Ejecución

```powershell
# Ejecutar todos los backups
python ejecutar_backup.py todos

# O ejecutar uno específico
python ejecutar_backup.py base_datos
python ejecutar_backup.py archivos
python ejecutar_backup.py codigo
```

## 📂 Estructura de Archivos

```
Gestor_Documental/
├── backup_manager.py              # ⭐ Motor del sistema de backup
├── ejecutar_backup.py             # ⭐ Script de ejecución manual
├── instalar_sistema_backup.py    # Instalador del sistema
│
├── sql/
│   └── schema_backup.sql          # Schema de tablas de backup
│
├── logs/
│   ├── backup.log                 # ⭐ Log de operaciones de backup
│   ├── security.log               # Log de seguridad
│   ├── app.log                    # Log general de aplicación
│   ├── errors.log                 # Log de errores
│   ├── facturas_digitales.log     # Log módulo facturas
│   └── relaciones.log             # Log módulo relaciones
│
├── modules/admin/monitoreo/
│   └── routes.py                  # Endpoints de backup (modificado)
│
└── C:\Backups_GestorDocumental\  # ⭐ Destino de backups
    ├── base_datos\                # .backup (formato pg_dump custom)
    ├── documentos\                # .zip (archivos del sistema)
    └── codigo\                    # .zip (código fuente)
```

## 🔧 Configuración

### Configuración por Defecto

| Tipo | Destino | Horario | Retención |
|------|---------|---------|-----------|
| **base_datos** | `C:\Backups_GestorDocumental\base_datos` | 2 AM diario | 7 días |
| **archivos** | `C:\Backups_GestorDocumental\documentos` | 3 AM diario | 14 días |
| **codigo** | `C:\Backups_GestorDocumental\codigo` | 4 AM domingos | 30 días |

### Cambiar Configuración

#### Desde la Interfaz Web:

1. Acceder a: http://localhost:8099/admin/monitoreo/dashboard
2. Sección "Backups Automáticos"
3. Click en "Configurar" para cada tipo

#### Desde PowerShell/Python:

```python
from app import app
from backup_manager import ConfiguracionBackup
from extensions import db

with app.app_context():
    config = ConfiguracionBackup.query.filter_by(tipo='base_datos').first()
    config.destino = 'D:\\Backups_Alternativo\\BD'
    config.dias_retencion = 14
    db.session.commit()
```

#### Desde SQL:

```sql
-- Ver configuración actual
SELECT * FROM configuracion_backup;

-- Cambiar destino de backups de BD
UPDATE configuracion_backup 
SET destino = 'D:\Backups_BD' 
WHERE tipo = 'base_datos';

-- Cambiar retención de archivos a 30 días
UPDATE configuracion_backup 
SET dias_retencion = 30 
WHERE tipo = 'archivos';
```

## 🖥️ Uso - Línea de Comandos

### Comandos Disponibles

```powershell
# ====== EJECUCIÓN DE BACKUPS ======

# Backup de base de datos
python ejecutar_backup.py base_datos

# Backup de archivos
python ejecutar_backup.py archivos

# Backup de código fuente
python ejecutar_backup.py codigo

# Ejecutar TODOS los backups
python ejecutar_backup.py todos


# ====== CONSULTAS ======

# Ver configuración actual
python ejecutar_backup.py config

# Ver historial de backups
python ejecutar_backup.py historial

# Ayuda
python ejecutar_backup.py help
```

### Ejemplo de Salida

```
==================================================================
  BACKUP: BASE_DATOS
==================================================================
[10:15:23] [BASE_DATOS] Iniciando backup...

✅ ÉXITO
   Archivo: C:\Backups_GestorDocumental\base_datos\backup_bd_20251201_101523.backup
   Tamaño: 28.45 MB
   Duración: 12 segundos

==================================================================
  ÚLTIMOS BACKUPS REALIZADOS
==================================================================

✅ BASE_DATOS
   Fecha: 2025-12-01 10:15:23
   Estado: exitoso
   Tamaño: 28.45 MB
   Duración: 12s
```

## 🌐 Uso - Interfaz Web

### Endpoints Disponibles

#### 1. Ver Estado de Backups

```
GET /admin/monitoreo/api/backup/estado
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "backups": [
      {
        "tipo": "Base de Datos",
        "tipo_key": "base_datos",
        "ultimo_backup": "2025-12-01 02:00:15",
        "tamaño_mb": 28.45,
        "estado": "exitoso",
        "dias_retencion": 7,
        "destino": "C:\\Backups_GestorDocumental\\base_datos",
        "duracion_segundos": 12
      }
    ],
    "espacio": {
      "total_gb": 500.0,
      "usado_gb": 150.5,
      "disponible_gb": 349.5,
      "porcentaje_uso": 30.1
    },
    "estado_general": "SALUDABLE"
  }
}
```

#### 2. Ejecutar Backup Manual

```
POST /admin/monitoreo/api/backup/ejecutar/{tipo}
```

**Tipos válidos:** `base_datos`, `archivos`, `codigo`

**Ejemplo:**
```javascript
fetch('/admin/monitoreo/api/backup/ejecutar/base_datos', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'}
})
.then(res => res.json())
.then(data => console.log(data));
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Backup base_datos completado exitosamente",
  "data": {
    "ruta": "C:\\...\\backup_bd_20251201_103045.backup",
    "tamano_mb": 28.45,
    "duracion_segundos": 12
  }
}
```

#### 3. Ver Historial de Backups

```
GET /admin/monitoreo/api/backup/historial?page=1&per_page=20&tipo=base_datos
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "historial": [
      {
        "id": 15,
        "tipo": "base_datos",
        "fecha_inicio": "2025-12-01T02:00:00",
        "fecha_fin": "2025-12-01T02:00:12",
        "estado": "exitoso",
        "ruta_archivo": "C:\\...\\backup_bd_20251201_020000.backup",
        "tamano_mb": 28.45,
        "duracion_segundos": 12,
        "usuario": "sistema"
      }
    ],
    "total": 45,
    "page": 1,
    "per_page": 20,
    "total_pages": 3
  }
}
```

#### 4. Ver Configuración

```
GET /admin/monitoreo/api/backup/configuracion
```

#### 5. Actualizar Configuración

```
PUT /admin/monitoreo/api/backup/configuracion/{tipo}

Body:
{
  "habilitado": true,
  "destino": "D:\\Backups_Alternativos\\BD",
  "horario_cron": "0 3 * * *",
  "dias_retencion": 14
}
```

## ⏰ Backups Automáticos (Programación)

### Opción 1: Windows Task Scheduler (Recomendado)

1. **Abrir Task Scheduler:**
   ```
   Win + R → taskschd.msc → Enter
   ```

2. **Crear Tarea Básica:**
   - Nombre: `Backup Gestor Documental - Base de Datos`
   - Trigger: Diario a las 2:00 AM
   - Action: Ejecutar programa
     - Programa: `python.exe` (ruta completa)
     - Argumentos: `C:\...\ejecutar_backup.py base_datos`
     - Directorio: `C:\...\Gestor_Documental\`

3. **Crear 3 tareas:**
   - Base de Datos: 2 AM diario
   - Archivos: 3 AM diario
   - Código: 4 AM domingos

### Opción 2: Script PowerShell (Alternativo)

Crear `programar_backups.ps1`:

```powershell
# Backup Base de Datos - 2 AM diario
$accion1 = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument "ejecutar_backup.py base_datos" `
    -WorkingDirectory "C:\...\Gestor_Documental"
    
$trigger1 = New-ScheduledTaskTrigger -Daily -At "02:00AM"

Register-ScheduledTask -TaskName "Backup BD Gestor" `
    -Action $accion1 -Trigger $trigger1 `
    -Description "Backup diario base de datos"

# Backup Archivos - 3 AM diario
$accion2 = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument "ejecutar_backup.py archivos" `
    -WorkingDirectory "C:\...\Gestor_Documental"
    
$trigger2 = New-ScheduledTaskTrigger -Daily -At "03:00AM"

Register-ScheduledTask -TaskName "Backup Archivos Gestor" `
    -Action $accion2 -Trigger $trigger2 `
    -Description "Backup diario archivos"

# Backup Código - 4 AM domingos
$accion3 = New-ScheduledTaskAction -Execute "python.exe" `
    -Argument "ejecutar_backup.py codigo" `
    -WorkingDirectory "C:\...\Gestor_Documental"
    
$trigger3 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "04:00AM"

Register-ScheduledTask -TaskName "Backup Codigo Gestor" `
    -Action $accion3 -Trigger $trigger3 `
    -Description "Backup semanal código fuente"
```

Ejecutar como administrador:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\programar_backups.ps1
```

## 📊 Tablas de Base de Datos

### `configuracion_backup`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | PK autoincremental |
| tipo | VARCHAR(50) | 'base_datos', 'archivos', 'codigo' |
| habilitado | BOOLEAN | Si el backup está activo |
| destino | VARCHAR(500) | Ruta donde guardar backups |
| horario_cron | VARCHAR(50) | Expresión cron para horario |
| dias_retencion | INTEGER | Días que se conservan los backups |
| ultima_ejecucion | TIMESTAMP | Fecha del último backup exitoso |
| proximo_backup | TIMESTAMP | Fecha programada siguiente |
| created_at | TIMESTAMP | Fecha de creación del registro |
| updated_at | TIMESTAMP | Última actualización |

### `historial_backup`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | PK autoincremental |
| tipo | VARCHAR(50) | Tipo de backup ejecutado |
| fecha_inicio | TIMESTAMP | Inicio de la ejecución |
| fecha_fin | TIMESTAMP | Fin de la ejecución |
| estado | VARCHAR(20) | 'exitoso', 'fallido', 'en_progreso' |
| ruta_archivo | VARCHAR(500) | Ruta del archivo generado |
| tamano_bytes | BIGINT | Tamaño del archivo en bytes |
| duracion_segundos | INTEGER | Tiempo que tardó el backup |
| mensaje | VARCHAR(1000) | Mensaje informativo |
| error | VARCHAR(2000) | Mensaje de error si falló |
| usuario | VARCHAR(50) | Usuario que ejecutó (manual/sistema) |

## 🔍 Consultas SQL Útiles

```sql
-- Ver estado general de backups
SELECT 
    tipo,
    habilitado,
    ultima_ejecucion,
    dias_retencion
FROM configuracion_backup
ORDER BY tipo;

-- Últimos 10 backups con tamaño
SELECT 
    tipo,
    fecha_inicio,
    estado,
    ROUND(tamano_bytes / (1024.0 * 1024.0), 2) AS tamano_mb,
    duracion_segundos
FROM historial_backup
ORDER BY fecha_inicio DESC
LIMIT 10;

-- Total de espacio usado por tipo de backup
SELECT 
    tipo,
    COUNT(*) AS total_backups,
    ROUND(SUM(tamano_bytes) / (1024.0 * 1024.0), 2) AS total_mb
FROM historial_backup
WHERE estado = 'exitoso'
GROUP BY tipo;

-- Backups fallidos últimos 7 días
SELECT 
    tipo,
    fecha_inicio,
    error,
    usuario
FROM historial_backup
WHERE estado = 'fallido'
  AND fecha_inicio >= NOW() - INTERVAL '7 days'
ORDER BY fecha_inicio DESC;

-- Promedio de duración por tipo
SELECT 
    tipo,
    AVG(duracion_segundos) AS duracion_promedio,
    MIN(duracion_segundos) AS duracion_minima,
    MAX(duracion_segundos) AS duracion_maxima
FROM historial_backup
WHERE estado = 'exitoso'
GROUP BY tipo;
```

## 🛠️ Mantenimiento

### Limpieza Automática

El sistema **elimina automáticamente** backups antiguos según `dias_retencion`:
- Base de Datos: 7 días (mantiene 7 backups diarios)
- Archivos: 14 días (mantiene 14 backups diarios)
- Código: 30 días (mantiene ~4 backups semanales)

### Limpieza Manual

```powershell
# Ver tamaño de backups
Get-ChildItem C:\Backups_GestorDocumental\* -Recurse | 
    Measure-Object -Property Length -Sum

# Eliminar backups más antiguos de 30 días manualmente
$limite = (Get-Date).AddDays(-30)
Get-ChildItem C:\Backups_GestorDocumental\* -Recurse | 
    Where-Object {$_.LastWriteTime -lt $limite} | 
    Remove-Item -Force
```

### Verificar Integridad

```powershell
# Probar restauración de backup de BD
pg_restore --version
pg_restore -l C:\Backups_GestorDocumental\base_datos\backup_bd_YYYYMMDD_HHMMSS.backup

# Probar descompresión de archivos
Expand-Archive -Path C:\Backups_GestorDocumental\documentos\backup_archivos_YYYYMMDD_HHMMSS.zip `
    -DestinationPath C:\Temp\test_restore\
```

## 🚨 Troubleshooting

### Error: "pg_dump not found"

**Problema:** pg_dump no está en PATH

**Solución:**
```powershell
# Agregar PostgreSQL al PATH permanentemente
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)

# O ejecutar con ruta completa
"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe" --version
```

### Error: "Permission denied" al guardar backup

**Problema:** Sin permisos en directorio de destino

**Solución:**
```powershell
# Dar permisos al directorio
icacls "C:\Backups_GestorDocumental" /grant "Users:(OI)(CI)F" /T
```

### Error: "Timeout en backup de base de datos"

**Problema:** Base de datos muy grande (>1 hora)

**Solución:** Editar `backup_manager.py` línea ~233:
```python
timeout=7200  # Cambiar de 3600 a 7200 (2 horas)
```

### Backup Falla Silenciosamente

**Ver logs:**
```powershell
# Ver últimas líneas del log de backup
Get-Content logs\backup.log -Tail 50

# Ver últimas líneas del log de errores
Get-Content logs\errors.log -Tail 50
```

### Disco Lleno

**Solución:**
```sql
-- Reducir días de retención
UPDATE configuracion_backup 
SET dias_retencion = 3 
WHERE tipo = 'archivos';

-- O cambiar destino a otra unidad
UPDATE configuracion_backup 
SET destino = 'E:\Backups_GestorDocumental\archivos' 
WHERE tipo = 'archivos';
```

## 📧 Notificaciones (Futuro)

*Pendiente de implementar:*

```python
# En backup_manager.py - agregar después de backup exitoso
from app import enviar_correo_notificacion, enviar_telegram_notificacion

if exito:
    enviar_correo_notificacion(
        destinatarios=['admin@supertiendascanaveral.com'],
        asunto=f'Backup {tipo} completado',
        mensaje=f'Backup exitoso: {ruta_completa}'
    )
```

## 📄 Licencia y Contacto

- **Proyecto:** Gestor Documental
- **Cliente:** Supertiendas Cañaveral
- **Fecha:** Diciembre 2025
- **Autor:** Sistema de Backup Automático v1.0

---

**¿Necesitas ayuda?** Consulta `logs/backup.log` o ejecuta `python ejecutar_backup.py help`
