# 📊 Módulo DIAN vs ERP - Sistema de Alto Rendimiento

## 🎯 Descripción

El módulo DIAN vs ERP es un sistema híbrido de alto rendimiento para el análisis y conciliación de facturas electrónicas entre los reportes de la DIAN y el sistema ERP de la empresa. Utiliza una arquitectura híbrida combinando SQLite para máximo rendimiento operativo y PostgreSQL para reportes y auditoría.

## 🏗️ Arquitectura Híbrida

### SQLite (Datos Operativos)
- **Alto rendimiento**: Operaciones de lectura/escritura optimizadas
- **Funciones Python UDF**: Funciones personalizadas para análisis de datos
- **WAL Mode**: Lectura concurrente sin bloqueos
- **Schema optimizado**: Índices estratégicos para consultas rápidas

### PostgreSQL (Reportes y Auditoría)
- **Integración**: Compatible con el resto del Gestor Documental
- **Auditoría**: Log completo de procesamientos
- **Reportes**: Almacenamiento de estadísticas históricas
- **Configuración**: Parámetros del módulo

## 📁 Estructura del Módulo

```
modules/dian_vs_erp/
├── __init__.py                      # Inicialización del módulo
├── routes.py                        # Flask Blueprint con todas las rutas
├── models.py                        # Modelos híbridos SQLite + PostgreSQL
├── schema.sql                       # Schema SQLite optimizado
├── data/                           # Directorio de datos
│   ├── dian_vs_erp.db              # Base de datos SQLite
│   └── csv/                        # Archivos CSV procesados
└── templates/
    ├── index.html                  # Dashboard principal
    └── cargar_moderno.html         # Interfaz de carga
```

## 🔧 Funcionalidades Principales

### 1. Carga de Archivos
- **Formatos soportados**: Excel (.xlsx, .xlsm, .xls) y CSV
- **Tipos de archivo**:
  - 📁 DIAN: Facturas electrónicas reportadas
  - 💰 ERP Financiero: Datos del módulo financiero
  - 🛒 ERP Comercial: Datos del módulo comercial
  - ❌ Errores ERP: Excepciones y errores
  - 📋 Acuses: Acuses de recibo

### 2. Procesamiento de Alto Rendimiento
- **Polars**: Procesamiento de datos ultra-rápido
- **Conversión automática**: Excel → CSV optimizado
- **Carga incremental**: Solo procesa cambios nuevos
- **Hash de archivos**: Evita procesamiento duplicado

### 3. Dashboard Inteligente
- **Tabulator Tables**: Interfaz moderna y responsiva
- **Estadísticas en tiempo real**: Métricas clave del negocio
- **Filtros avanzados**: Búsqueda multi-criterio
- **Exportación**: Excel de facturas seleccionadas

### 4. API REST Completa
- **`/api/dian`**: Obtener facturas consolidadas
- **`/subir_archivos`**: Carga masiva de archivos
- **`/api/forzar_procesar`**: Reprocesamiento manual

## 🚀 Instalación y Configuración

### 1. Dependencias
```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Inicialización
```bash
# Ejecutar script de inicialización
python inicializar_dian_vs_erp.py
```

Este script:
- ✅ Verifica dependencias
- ✅ Crea base de datos SQLite con schema optimizado
- ✅ Crea tablas PostgreSQL para auditoría
- ✅ Configura parámetros iniciales
- ✅ Registra funciones Python UDF

### 3. Verificación
```bash
# Probar módulo
python -c "from modules.dian_vs_erp.models import *; print('✅ Módulo listo')"
```

## 📋 URLs del Sistema

| URL | Descripción |
|-----|-------------|
| `/dian_vs_erp/` | Dashboard principal con estadísticas |
| `/dian_vs_erp/cargar` | Interfaz de carga de archivos |
| `/dian_vs_erp/api/dian` | API REST - facturas consolidadas |
| `/dian_vs_erp/subir_archivos` | Endpoint de carga masiva |

## 📊 Base de Datos

### Tablas SQLite (Alto Rendimiento)
```sql
-- Facturas DIAN
CREATE TABLE dian (
    id INTEGER PRIMARY KEY,
    nit_emisor TEXT,
    nombre_emisor TEXT,
    prefijo TEXT,
    folio TEXT,
    fecha_emision DATE,
    valor DECIMAL(15,2),
    cufe TEXT UNIQUE,
    estado_contable TEXT,
    modulo TEXT
);

-- Datos ERP
CREATE TABLE erp (
    id INTEGER PRIMARY KEY,
    nit_proveedor TEXT,
    prefijo TEXT,
    folio TEXT,
    fecha_factura DATE,
    valor DECIMAL(15,2),
    centro_costo TEXT,
    modulo TEXT
);

-- Vista consolidada optimizada
CREATE VIEW vista_consolidada AS
SELECT 
    d.*,
    e.centro_costo,
    e.modulo as modulo_erp,
    DIAS_DIFERENCIA(d.fecha_emision) as dias_desde_emision
FROM dian d
LEFT JOIN erp e ON 
    LIMPIAR_NIT(d.nit_emisor) = LIMPIAR_NIT(e.nit_proveedor) 
    AND NORMALIZAR_TEXTO(d.prefijo) = NORMALIZAR_TEXTO(e.prefijo)
    AND d.folio = e.folio;
```

### Tablas PostgreSQL (Auditoría)
```sql
-- Reportes consolidados
CREATE TABLE reportes_dian (
    id SERIAL PRIMARY KEY,
    empresa_id VARCHAR(50),
    periodo VARCHAR(20),
    total_dian INTEGER,
    total_erp INTEGER,
    matches INTEGER,
    diferencias INTEGER,
    fecha_generacion TIMESTAMP
);

-- Log de procesamientos
CREATE TABLE logs_procesamiento_dian (
    id SERIAL PRIMARY KEY,
    archivo_tipo VARCHAR(50),
    archivo_original VARCHAR(255),
    registros_procesados INTEGER,
    estado VARCHAR(50),
    fecha_procesamiento TIMESTAMP
);
```

## 🔍 Funciones Python UDF

El sistema registra funciones personalizadas en SQLite:

```sql
-- Limpieza de NITs
SELECT LIMPIAR_NIT('805.028.041-1') -- Retorna: 8050280411

-- Normalización de texto
SELECT NORMALIZAR_TEXTO(' ABC-123 ') -- Retorna: ABC-123

-- Cálculo de días
SELECT DIAS_DIFERENCIA('2025-01-01') -- Retorna: días desde hoy
```

## 📈 Métricas y Estadísticas

El dashboard muestra:

- 📄 **Total Facturas DIAN**: Facturas reportadas a la DIAN
- 📁 **Registros ERP**: Datos del sistema interno
- 🔗 **Matches DIAN ↔ ERP**: Facturas coincidentes
- 🏷️ **Con Módulo Asignado**: Facturas con centro de costo

## 🛠️ Desarrollo y Mantenimiento

### Agregar Nuevos Tipos de Archivo
1. Actualizar `schema.sql` con nueva tabla
2. Modificar `routes.py` para manejar el nuevo tipo
3. Actualizar frontend en `templates/`

### Optimización de Rendimiento
- **Índices**: Agregar índices para consultas frecuentes
- **Particionado**: Considerar particionado por fecha
- **Caching**: Implementar cache Redis para consultas pesadas

### Backup y Recuperación
```bash
# Backup SQLite
cp modules/dian_vs_erp/data/dian_vs_erp.db backup_$(date +%Y%m%d).db

# Restauración
cp backup_20250101.db modules/dian_vs_erp/data/dian_vs_erp.db
```

## 🔒 Seguridad

- **Validación de archivos**: Solo Excel/CSV permitidos
- **Tamaño máximo**: 100MB por archivo
- **Hash de archivos**: Previene modificaciones
- **Logs de auditoría**: Rastreo completo en PostgreSQL

## 📞 Soporte y Troubleshooting

### Problemas Comunes

**Error: "no such column"**
```bash
# Solución: Reinicializar schema
python inicializar_dian_vs_erp.py
```

**Error: "polars not found"**
```bash
# Solución: Reinstalar dependencias
pip install polars==0.20.2
```

**Error: "Working outside application context"**
```bash
# Solución: Ejecutar dentro del contexto Flask
python -c "from app import app; app.app_context().pushes(); # tu código aquí"
```

### Logs de Depuración

Los logs se encuentran en:
- **Aplicación**: `logs/security.log`
- **SQLite**: Error automático en consola
- **PostgreSQL**: Log de SQLAlchemy

## 🚀 Próximas Mejoras

- [ ] **Cache Redis**: Para consultas repetitivas
- [ ] **API GraphQL**: Consultas más flexibles  
- [ ] **Machine Learning**: Detección de anomalías
- [ ] **Dashboard en Tiempo Real**: WebSockets
- [ ] **Exportación Avanzada**: PDF con gráficos
- [ ] **Integración DIAN**: API oficial de consultas

## 📝 Changelog

### v1.0.0 (Noviembre 30, 2025)
- ✅ Sistema híbrido SQLite + PostgreSQL
- ✅ Dashboard con Tabulator Tables
- ✅ Carga masiva con Polars
- ✅ Funciones Python UDF
- ✅ API REST completa
- ✅ Integración con Gestor Documental

---

**Desarrollado para Supertiendas Cañaveral**  
*Gestión inteligente de facturas electrónicas*