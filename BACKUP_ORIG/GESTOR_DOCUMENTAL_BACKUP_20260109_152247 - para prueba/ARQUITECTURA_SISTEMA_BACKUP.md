# 🏗️ ARQUITECTURA DEL SISTEMA DE BACKUP

## 📊 Diagrama del Sistema Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GESTOR DOCUMENTAL                                 │
│                  Supertiendas Cañaveral                              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   INTERFAZ   │   │     API      │   │   SCRIPTS    │
│     WEB      │   │     REST     │   │   MANUALES   │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       │ Dashboard        │ Endpoints        │ Comandos
       │ Monitoreo        │ JSON             │ Terminal
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
              ┌───────────────────────┐
              │   BACKUP_MANAGER.PY   │
              │   (Motor Principal)   │
              └───────┬───────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐
│   BACKUP BD  │ │ BACKUP   │ │ BACKUP   │
│   pg_dump    │ │ ARCHIVOS │ │ CODIGO   │
└──────┬───────┘ └────┬─────┘ └────┬─────┘
       │              │            │
       │              │            │
       ▼              ▼            ▼
┌──────────────────────────────────────────┐
│         DESTINOS DE BACKUP               │
│  C:\Backups_GestorDocumental\            │
│    ├── base_datos\                       │
│    ├── documentos\                       │
│    └── codigo\                           │
└──────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│      REGISTRO EN BASE DE DATOS           │
│   ┌──────────────────────────┐           │
│   │ configuracion_backup     │           │
│   │ - tipo                   │           │
│   │ - destino                │           │
│   │ - horario_cron           │           │
│   │ - dias_retencion         │           │
│   └──────────────────────────┘           │
│   ┌──────────────────────────┐           │
│   │ historial_backup         │           │
│   │ - fecha_inicio/fin       │           │
│   │ - estado                 │           │
│   │ - tamano_bytes           │           │
│   │ - ruta_archivo           │           │
│   └──────────────────────────┘           │
└──────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────┐
│            LOGS DEL SISTEMA              │
│   logs/backup.log                        │
│   logs/security.log                      │
│   logs/errors.log                        │
└──────────────────────────────────────────┘
```

## 🔄 Flujo de Ejecución de Backup

### 1. EJECUCIÓN MANUAL (Terminal)

```
Usuario ejecuta:
python ejecutar_backup.py base_datos
         │
         ▼
┌────────────────────────────┐
│ ejecutar_backup.py         │
│ - Valida argumentos        │
│ - Muestra configuración    │
│ - Solicita confirmación    │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ backup_manager.py          │
│ ejecutar_backup_completo() │
└────────────┬───────────────┘
             │
             ├─── Crea registro en historial_backup (estado='en_progreso')
             │
             ▼
┌────────────────────────────┐
│ backup_base_datos()        │
│ - Obtiene credenciales     │
│ - Ejecuta pg_dump          │
│ - Verifica archivo creado  │
│ - Calcula tamaño           │
└────────────┬───────────────┘
             │
             ├─── Actualiza historial_backup (estado='exitoso'/'fallido')
             ├─── Actualiza configuracion_backup (ultima_ejecucion)
             ├─── Ejecuta limpieza de backups antiguos
             ├─── Escribe en logs/backup.log
             │
             ▼
┌────────────────────────────┐
│ Muestra resultado          │
│ ✅ ÉXITO                   │
│ Archivo: C:\...\backup.bkp │
│ Tamaño: 28.45 MB           │
│ Duración: 12 segundos      │
└────────────────────────────┘
```

### 2. EJECUCIÓN VÍA API REST

```
Cliente web hace:
POST /admin/monitoreo/api/backup/ejecutar/base_datos
         │
         ▼
┌────────────────────────────┐
│ routes.py                  │
│ @monitoreo_bp.route()      │
│ - Valida sesión admin      │
│ - Valida tipo de backup    │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ backup_manager.py          │
│ ejecutar_backup_completo() │
│ (mismo flujo que manual)   │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Respuesta JSON             │
│ {                          │
│   "success": true,         │
│   "message": "...",        │
│   "data": {                │
│     "ruta": "...",         │
│     "tamano_mb": 28.45     │
│   }                        │
│ }                          │
└────────────────────────────┘
```

### 3. EJECUCIÓN AUTOMÁTICA (Programada)

```
Windows Task Scheduler
  Tarea: "Backup BD Gestor"
  Horario: 2:00 AM diario
         │
         ▼
Ejecuta:
"C:\...\python.exe" "C:\...\ejecutar_backup.py" base_datos
         │
         │ (mismo flujo que manual)
         │
         ▼
Sistema registra en:
  - historial_backup (usuario='sistema')
  - logs/backup.log
```

## 🗄️ Modelo de Base de Datos Detallado

### Tabla: `configuracion_backup`

```
┌─────────────────────────────────────────────────────────┐
│ configuracion_backup                                     │
├──────────────────┬──────────────┬────────────────────────┤
│ Campo            │ Tipo         │ Descripción            │
├──────────────────┼──────────────┼────────────────────────┤
│ id               │ INTEGER PK   │ ID único               │
│ tipo             │ VARCHAR(50)  │ base_datos/archivos/   │
│                  │              │ codigo (UNIQUE)        │
│ habilitado       │ BOOLEAN      │ Si está activo         │
│ destino          │ VARCHAR(500) │ Ruta completa destino  │
│ horario_cron     │ VARCHAR(50)  │ Expresión cron         │
│ dias_retencion   │ INTEGER      │ Días antes de eliminar │
│ ultima_ejecucion │ TIMESTAMP    │ Último backup exitoso  │
│ proximo_backup   │ TIMESTAMP    │ Próximo programado     │
│ created_at       │ TIMESTAMP    │ Fecha creación         │
│ updated_at       │ TIMESTAMP    │ Última actualización   │
└──────────────────┴──────────────┴────────────────────────┘

Valores por defecto:
┌──────────────┬─────────────────────────────────────┬────────┬────────┐
│ tipo         │ destino                             │ cron   │ reten  │
├──────────────┼─────────────────────────────────────┼────────┼────────┤
│ base_datos   │ C:\Backups_..\base_datos            │ 0 2 ** │ 7 días │
│ archivos     │ C:\Backups_..\documentos            │ 0 3 ** │ 14 día │
│ codigo       │ C:\Backups_..\codigo                │ 0 4 *0 │ 30 día │
└──────────────┴─────────────────────────────────────┴────────┴────────┘
```

### Tabla: `historial_backup`

```
┌─────────────────────────────────────────────────────────┐
│ historial_backup                                         │
├──────────────────┬──────────────┬────────────────────────┤
│ Campo            │ Tipo         │ Descripción            │
├──────────────────┼──────────────┼────────────────────────┤
│ id               │ INTEGER PK   │ ID único               │
│ tipo             │ VARCHAR(50)  │ Tipo de backup         │
│ fecha_inicio     │ TIMESTAMP    │ Inicio ejecución       │
│ fecha_fin        │ TIMESTAMP    │ Fin ejecución          │
│ estado           │ VARCHAR(20)  │ exitoso/fallido/       │
│                  │              │ en_progreso            │
│ ruta_archivo     │ VARCHAR(500) │ Ruta archivo generado  │
│ tamano_bytes     │ BIGINT       │ Tamaño en bytes        │
│ duracion_segundos│ INTEGER      │ Tiempo de ejecución    │
│ mensaje          │ VARCHAR(1000)│ Mensaje informativo    │
│ error            │ VARCHAR(2000)│ Mensaje de error       │
│ usuario          │ VARCHAR(50)  │ Quien ejecutó          │
└──────────────────┴──────────────┴────────────────────────┘

Índices:
- idx_historial_tipo (tipo)
- idx_historial_fecha (fecha_inicio DESC)
- idx_historial_estado (estado)

Estados posibles:
  ✅ exitoso      - Backup completado correctamente
  ❌ fallido      - Backup falló con error
  ⏳ en_progreso  - Backup ejecutándose ahora
```

## 📁 Estructura de Archivos Generados

### Nomenclatura de Archivos

```
Formato: backup_{tipo}_{fecha}_{hora}.{extension}

Ejemplos:
- backup_bd_20251201_020015.backup        (Base de datos)
- backup_archivos_20251201_030045.zip     (Archivos)
- backup_codigo_20251208_040030.zip       (Código)

Estructura de carpetas:
C:\Backups_GestorDocumental\
│
├── base_datos\
│   ├── backup_bd_20251201_020015.backup  ← Formato pg_dump custom
│   ├── backup_bd_20251202_020012.backup  ← Comprimido automáticamente
│   ├── backup_bd_20251203_020018.backup
│   └── ... (7 días de retención)
│
├── documentos\
│   ├── backup_archivos_20251201_030045.zip  ← Contiene:
│   │                                           - documentos_terceros/
│   │                                           - documentos_contables/
│   │                                           - facturas_digitales/
│   ├── backup_archivos_20251202_030052.zip
│   └── ... (14 días de retención)
│
└── codigo\
    ├── backup_codigo_20251201_040030.zip  ← Contiene:
    │                                         - app.py
    │                                         - modules/
    │                                         - templates/
    │                                         - (excluye .venv, __pycache__, logs)
    ├── backup_codigo_20251208_040025.zip
    └── ... (30 días de retención)
```

## 🔌 API REST Completa

### Endpoints Disponibles

```
┌─────────────────────────────────────────────────────────────────────┐
│                   API REST - SISTEMA DE BACKUP                      │
└─────────────────────────────────────────────────────────────────────┘

1. GET /admin/monitoreo/api/backup/estado
   ┌──────────────────────────────────────────────────────┐
   │ Descripción: Estado actual de todos los backups      │
   │ Autenticación: Sesión admin requerida                │
   │ Permisos: monitoreo.consultar_estadisticas           │
   └──────────────────────────────────────────────────────┘
   Respuesta:
   {
     "success": true,
     "data": {
       "backups": [
         {
           "tipo": "Base de Datos",
           "tipo_key": "base_datos",
           "habilitado": true,
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
       "estado_general": "SALUDABLE",
       "total_backups_realizados": 45
     }
   }

2. POST /admin/monitoreo/api/backup/ejecutar/<tipo>
   ┌──────────────────────────────────────────────────────┐
   │ Descripción: Ejecuta un backup manual                │
   │ Parámetros: tipo = base_datos, archivos, codigo      │
   │ Autenticación: Sesión admin requerida                │
   │ Permisos: monitoreo.ejecutar_backups                 │
   └──────────────────────────────────────────────────────┘
   Request:
   POST /admin/monitoreo/api/backup/ejecutar/base_datos
   
   Respuesta:
   {
     "success": true,
     "message": "Backup base_datos completado exitosamente",
     "data": {
       "ruta": "C:\\...\\backup_bd_20251201_103045.backup",
       "tamano_mb": 28.45,
       "duracion_segundos": 12
     }
   }

3. GET /admin/monitoreo/api/backup/historial
   ┌──────────────────────────────────────────────────────┐
   │ Descripción: Historial de backups ejecutados         │
   │ Query Params:                                         │
   │   - page: Número de página (default: 1)              │
   │   - per_page: Registros por página (default: 20)     │
   │   - tipo: Filtrar por tipo (opcional)                │
   │ Autenticación: Sesión admin requerida                │
   │ Permisos: monitoreo.consultar_estadisticas           │
   └──────────────────────────────────────────────────────┘
   Request:
   GET /admin/monitoreo/api/backup/historial?page=1&per_page=20&tipo=base_datos
   
   Respuesta:
   {
     "success": true,
     "data": {
       "historial": [ ... ],
       "total": 45,
       "page": 1,
       "per_page": 20,
       "total_pages": 3
     }
   }

4. GET /admin/monitoreo/api/backup/configuracion
   ┌──────────────────────────────────────────────────────┐
   │ Descripción: Obtiene configuración actual            │
   │ Autenticación: Sesión admin requerida                │
   │ Permisos: monitoreo.consultar_estadisticas           │
   └──────────────────────────────────────────────────────┘

5. PUT /admin/monitoreo/api/backup/configuracion/<tipo>
   ┌──────────────────────────────────────────────────────┐
   │ Descripción: Actualiza configuración de un tipo      │
   │ Autenticación: Sesión admin requerida                │
   │ Permisos: monitoreo.configurar_sistema               │
   └──────────────────────────────────────────────────────┘
   Request:
   PUT /admin/monitoreo/api/backup/configuracion/base_datos
   Body: {
     "habilitado": true,
     "destino": "D:\\Backups\\BD",
     "horario_cron": "0 3 * * *",
     "dias_retencion": 14
   }
```

## 📝 Sistema de Logs Múltiples

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LOGS DEL SISTEMA                            │
└─────────────────────────────────────────────────────────────────────┘

logs/
├── security.log              ← Autenticación y seguridad
│   │ - Intentos de login
│   │ - Cambios de contraseña
│   │ - Bloqueos de IP
│   └── Activación/desactivación usuarios
│
├── backup.log               ← ⭐ Operaciones de backup
│   │ - Inicio/fin de backups
│   │ - Tamaños y duraciones
│   │ - Errores en backups
│   └── Limpieza de backups antiguos
│
├── app.log                  ← Eventos generales
│   │ - Inicio del servidor
│   │ - Carga de módulos
│   └── Inicializaciones
│
├── errors.log               ← Solo errores
│   │ - Excepciones no capturadas
│   │ - Errores de BD
│   └── Stack traces completos
│
├── facturas_digitales.log   ← Módulo facturas
│   │ - Carga de facturas
│   │ - Validaciones
│   └── Configuración catálogos
│
└── relaciones.log           ← Módulo relaciones
    │ - Generación de relaciones
    │ - Recepciones digitales
    └── Validaciones

Formato común:
[YYYY-MM-DD HH:MM:SS] | NIVEL | MENSAJE

Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔄 Proceso de Limpieza Automática

```
Después de cada backup exitoso:

┌─────────────────────────────────────┐
│ limpiar_backups_antiguos()          │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 1. Leer directorio de backups       │
│    C:\Backups_..\base_datos\        │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 2. Para cada archivo .backup o .zip │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 3. Verificar fecha de modificación  │
│    fecha_archivo = os.path.getmtime()│
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 4. Comparar con fecha límite        │
│    fecha_limite = now - dias_retencion│
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 5. Si archivo > fecha_limite:       │
│    - os.remove(archivo)              │
│    - Log: "Backup antiguo eliminado" │
└─────────────────────────────────────┘

Ejemplo:
  dias_retencion = 7
  Hoy = 2025-12-08
  fecha_limite = 2025-12-01
  
  Backups en C:\...\base_datos\:
  ✅ backup_bd_20251208_020000.backup  ← Mantener (hoy)
  ✅ backup_bd_20251207_020000.backup  ← Mantener (1 día)
  ✅ backup_bd_20251206_020000.backup  ← Mantener (2 días)
  ...
  ✅ backup_bd_20251202_020000.backup  ← Mantener (6 días)
  ❌ backup_bd_20251201_020000.backup  ← ELIMINAR (7 días)
  ❌ backup_bd_20251130_020000.backup  ← ELIMINAR (8 días)
```

## 🎯 Flujo Completo de Usuario

```
┌─────────────────────────────────────────────────────────────────────┐
│ CASO DE USO: Configurar y Ejecutar Backup Automático               │
└─────────────────────────────────────────────────────────────────────┘

DÍA 1: INSTALACIÓN
  │
  ├─ python instalar_sistema_backup.py
  │  ├─ Crea tablas en PostgreSQL
  │  ├─ Inserta configuración por defecto
  │  ├─ Crea directorios C:\Backups_GestorDocumental\
  │  └─ Ejecuta backup de prueba (código)
  │
  └─ Resultado: ✅ Sistema instalado

DÍA 1: PRIMERA EJECUCIÓN MANUAL
  │
  ├─ python ejecutar_backup.py todos
  │  ├─ Backup Base de Datos → 28 MB
  │  ├─ Backup Archivos → 1.2 GB
  │  └─ Backup Código → 15 MB
  │
  └─ Resultado: 3 archivos creados en C:\Backups_GestorDocumental\

DÍA 1: CONFIGURAR BACKUPS AUTOMÁTICOS
  │
  ├─ Abrir Task Scheduler
  │  ├─ Tarea 1: Backup BD - 2 AM diario
  │  ├─ Tarea 2: Backup Archivos - 3 AM diario
  │  └─ Tarea 3: Backup Código - 4 AM domingos
  │
  └─ Resultado: ✅ 3 tareas programadas

DÍA 2: EJECUCIÓN AUTOMÁTICA (2 AM)
  │
  ├─ Task Scheduler ejecuta:
  │  python ejecutar_backup.py base_datos
  │
  ├─ Sistema:
  │  ├─ Crea backup_bd_20251202_020000.backup
  │  ├─ Registra en historial_backup
  │  ├─ Actualiza configuracion_backup.ultima_ejecucion
  │  ├─ Escribe en logs/backup.log
  │  └─ Limpia backups > 7 días
  │
  └─ Resultado: ✅ Backup automático exitoso

DÍA 8: LIMPIEZA AUTOMÁTICA
  │
  ├─ Backups en C:\...\base_datos\:
  │  ├─ backup_bd_20251208_020000.backup ✅ (0 días)
  │  ├─ backup_bd_20251207_020000.backup ✅ (1 día)
  │  ├─ backup_bd_20251206_020000.backup ✅ (2 días)
  │  ├─ backup_bd_20251205_020000.backup ✅ (3 días)
  │  ├─ backup_bd_20251204_020000.backup ✅ (4 días)
  │  ├─ backup_bd_20251203_020000.backup ✅ (5 días)
  │  ├─ backup_bd_20251202_020000.backup ✅ (6 días)
  │  └─ backup_bd_20251201_020000.backup ❌ ELIMINADO (7 días)
  │
  └─ Resultado: Espacio liberado automáticamente

DÍA 30: MONITOREO
  │
  ├─ Acceder a: http://localhost:8099/admin/monitoreo/dashboard
  │
  ├─ Ver estadísticas:
  │  ├─ 30 backups de BD realizados (exitosos)
  │  ├─ 30 backups de archivos realizados
  │  ├─ 4 backups de código realizados (domingos)
  │  └─ 0 fallos registrados
  │
  └─ Resultado: ✅ Sistema funcionando perfectamente
```

---

**Creado:** Diciembre 1, 2025  
**Versión:** 1.0  
**Proyecto:** Gestor Documental - Supertiendas Cañaveral
