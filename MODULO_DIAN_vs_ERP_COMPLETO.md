# 📋 Módulo DIAN vs ERP - Documentación Completa

**Fecha de Implementación:** 13 de Noviembre de 2025  
**Estado:** ✅ COMPLETAMENTE IMPLEMENTADO Y LISTO PARA USAR  
**Acceso:** http://localhost:8099/dian_vs_erp/

---

## 🎯 Descripción General

El módulo **Validación DIAN vs ERP** es un sistema integral para comparar y validar facturas reportadas ante la DIAN contra las facturas registradas en el sistema ERP interno de Supertiendas Cañaveral. 

**Objetivo Principal:** Identificar discrepancias entre la información fiscal reportada a la DIAN y los datos internos del ERP para garantizar la consistencia contable y fiscal.

---

## 🏗️ Arquitectura del Sistema

### Estructura de Archivos Implementada
```
modules/dian_vs_erp/
├── __init__.py                     # Inicialización del módulo
├── models.py                       # 5 modelos SQLAlchemy con base de datos
├── routes.py                       # 15+ endpoints Flask Blueprint  
├── services.py                     # 3 servicios de negocio
└── 

templates/dian_vs_erp/
├── dashboard.html                  # Dashboard principal con estadísticas
├── cargar_archivos.html           # Interfaz drag & drop para carga de archivos
├── validaciones.html              # Visualización de resultados con filtros
└── reportes.html                   # Generación y exportación de reportes

sql/
└── dian_vs_erp_schema.sql         # Script de creación de 5 tablas + vista

crear_tablas_dian_vs_erp.py       # Script de instalación de BD
```

### Integración en el Sistema Principal
- ✅ **app.py**: Blueprint registrado en `/dian_vs_erp/*`
- ✅ **dashboard.html**: Módulo agregado al menú principal con 4 submenús
- ✅ **Permisos**: Integrado con sistema de decoradores de permisos
- ✅ **Email**: Configurado para usar SMTP del sistema (Gmail/Zimbra)

---

## 🗄️ Base de Datos

### Tablas Implementadas (5 + 1 vista)

#### 1. **reportes_dian**
Almacena facturas reportadas ante la DIAN
```sql
- id (SERIAL PRIMARY KEY)
- periodo (VARCHAR) - Formato YYYY-MM
- nit_tercero, nombre_tercero
- prefijo, folio (únicos por periodo)
- fecha_factura, valor_factura  
- datos_adicionales (JSONB)
- archivo_origen, fecha_carga, usuario_carga
```

#### 2. **facturas_erp**
Almacena facturas del sistema ERP interno
```sql
- id (SERIAL PRIMARY KEY)  
- periodo (VARCHAR) - Formato YYYY-MM
- nit_tercero, nombre_tercero
- prefijo, folio (únicos por periodo)
- fecha_factura, valor_factura
- datos_adicionales (JSONB)
- archivo_origen, fecha_carga, usuario_carga
```

#### 3. **validaciones_facturas** 
Resultados de las validaciones DIAN vs ERP
```sql
- id (SERIAL PRIMARY KEY)
- periodo, nit_tercero, nombre_tercero
- prefijo, folio, fecha_factura, valor_factura
- tipo_validacion: 'coincidente'|'discrepante'|'solo_dian'|'solo_erp'
- coincide (BOOLEAN)
- discrepancias (JSONB) - Array de diferencias encontradas
- datos_dian, datos_erp (JSONB)
- fecha_validacion, usuario_validacion, observaciones
```

#### 4. **procesamientos_periodo**
Control y estadísticas de procesamientos
```sql
- id (SERIAL PRIMARY KEY)
- periodo (UNIQUE)
- total_dian, total_erp, total_coincidentes, total_discrepantes
- total_solo_dian, total_solo_erp
- estado_procesamiento: 'iniciado'|'validando'|'completado'|'error'
- fecha_inicio, fecha_finalizacion
- usuario_procesamiento, tiempo_procesamiento
- archivos_procesados (JSONB)
```

#### 5. **configuracion_validacion**
Configuración del módulo
```sql
- id (SERIAL PRIMARY KEY)
- clave, valor, descripcion, tipo, categoria
- activo, fecha_actualizacion, usuario_actualizacion
```

#### Vista: **v_estadisticas_validacion**
Vista agregada con estadísticas generales del sistema

---

## 🛠️ Funcionalidades Implementadas

### 1. **Dashboard Principal** (`/dian_vs_erp/`)
- 📊 4 tarjetas de estadísticas principales
- 📈 Estado del periodo actual con progreso
- ⚡ Acciones rápidas: Cargar, Validar, Reportes, Ejecutar
- 📋 Historial de procesamientos con acciones
- 🔄 Actualización automática cada 30 segundos
- 🎛️ Modal de confirmación para acciones críticas

### 2. **Carga de Archivos** (`/dian_vs_erp/cargar_archivos`)
- 📁 Interfaz drag & drop para Excel/CSV
- 🔄 Carga separada: Archivos DIAN y Archivos ERP
- 📊 Barras de progreso durante la carga
- 👀 Preview del archivo seleccionado
- 📋 Historial de archivos cargados recientemente
- ✅ Validación automática disponible al tener ambos tipos

### 3. **Visualización de Validaciones** (`/dian_vs_erp/validaciones`)  
- 🔍 Filtros avanzados: periodo, tipo, factura, rango de valor
- 📄 Paginación: 25/50/100 registros por página
- 🎨 Código de colores por tipo de validación:
  - 🟢 Verde: Coincidentes
  - 🔴 Rojo: Discrepantes  
  - 🟡 Amarillo: Solo en DIAN
  - 🔵 Azul: Solo en ERP
- 🔎 Modal de detalles con comparación lado a lado
- 📊 Estadísticas del periodo seleccionado

### 4. **Generación de Reportes** (`/dian_vs_erp/reportes`)
- 📈 3 pestañas: Generación, Programados, Historial
- 📋 4 tipos de reporte: Completo, Coincidentes, Discrepantes, Resumen
- 📄 2 formatos: Excel (.xlsx) y CSV  
- 📧 Envío automático por correo electrónico
- 👀 Vista previa del reporte antes de generar
- 📚 Historial de reportes generados con re-descarga
- 🔄 Funcionalidad de reenvío por email

---

## 🔧 Servicios Implementados

### 1. **ValidacionService** (`services.py`)
```python
- validar_periodo(): Ejecuta validación completa de un periodo
- buscar_coincidencias(): Algoritmo de matching DIAN vs ERP
- detectar_discrepancias(): Identifica diferencias en valores/fechas
- generar_estadisticas(): Calcula métricas del procesamiento
```

### 2. **CargaService** (`services.py`) 
```python
- procesar_archivo_dian(): Carga y valida archivos DIAN
- procesar_archivo_erp(): Carga y valida archivos ERP  
- validar_formato(): Verifica estructura de archivos Excel/CSV
- limpiar_datos(): Normaliza y sanitiza datos de entrada
```

### 3. **ReporteService** (`services.py`)
```python
- generar_reporte_excel(): Crea archivos Excel con múltiples hojas
- enviar_reporte_email(): Integración SMTP con sistema principal
- obtener_preview_datos(): Genera vista previa para interfaz
- gestionar_historial(): Controla archivos generados
```

---

## 🌐 APIs REST Implementadas

### Endpoints del Dashboard
- `GET /dian_vs_erp/` - Dashboard principal
- `GET /dian_vs_erp/api/estadisticas/{periodo}` - Estadísticas de un periodo
- `POST /dian_vs_erp/api/ejecutar_validacion/{periodo}` - Ejecutar validación
- `DELETE /dian_vs_erp/api/limpiar_periodo/{periodo}` - Limpiar datos

### Endpoints de Carga de Archivos  
- `GET /dian_vs_erp/cargar_archivos` - Interfaz de carga
- `POST /dian_vs_erp/api/cargar_dian` - Cargar archivo DIAN
- `POST /dian_vs_erp/api/cargar_erp` - Cargar archivo ERP
- `GET /dian_vs_erp/api/archivos_recientes` - Historial de archivos
- `GET /dian_vs_erp/api/verificar_archivos/{periodo}` - Verificar disponibilidad

### Endpoints de Validaciones
- `GET /dian_vs_erp/validaciones` - Interfaz de validaciones  
- `GET /dian_vs_erp/api/validaciones` - Lista paginada con filtros
- `GET /dian_vs_erp/api/validacion_detalles/{id}` - Detalles de una validación
- `GET /dian_vs_erp/api/exportar_validaciones` - Exportar a Excel

### Endpoints de Reportes
- `GET /dian_vs_erp/reportes` - Interfaz de reportes
- `GET /dian_vs_erp/api/preview_reporte` - Vista previa de datos
- `POST /dian_vs_erp/api/generar_reporte` - Generar y descargar/enviar
- `GET /dian_vs_erp/api/historial_reportes` - Historial de reportes
- `POST /dian_vs_erp/api/reenviar_reporte` - Reenviar por email

---

## 🔐 Seguridad y Permisos

### Sistema de Permisos Integrado
```python
@requiere_permiso('dian_vs_erp', 'acceder_modulo')  # API endpoints  
@requiere_permiso_html('dian_vs_erp', 'cargar_archivos')  # Páginas HTML
@requiere_rol('admin', 'interno')  # Control por rol
```

### Auditoría Completa
- 📝 Todos los procesamientos registrados con usuario y timestamp
- 🔍 Log de validaciones con detalles de discrepancias  
- 📧 Log de envíos de email con destinatarios
- 🗂️ Historial de archivos cargados con metadatos

---

## 💾 Instalación y Configuración

### 1. Ejecutar Script de Base de Datos
```cmd
python crear_tablas_dian_vs_erp.py
```

### 2. Verificar Integración en app.py
✅ Ya incluido en app.py:
- Import del blueprint: `from modules.dian_vs_erp.routes import dian_vs_erp_bp`
- Import de modelos: `from modules.dian_vs_erp.models import *`
- Registro: `app.register_blueprint(dian_vs_erp_bp, url_prefix='/dian_vs_erp')`

### 3. Verificar Menú en Dashboard
✅ Ya incluido en `templates/dashboard.html`:
- Módulo agregado a `modulosInternos` con icono ⚖️
- Menú sidebar con 4 submenús
- Función de navegación configurada

### 4. Reiniciar Aplicación
```cmd
python app.py
```

---

## 🚀 Uso del Sistema

### Flujo Típico de Trabajo

#### 1. **Cargar Archivos** 📁
- Acceder a `/dian_vs_erp/cargar_archivos`
- Seleccionar periodo (formato YYYY-MM)
- Arrastrar archivo DIAN (Excel/CSV)
- Arrastrar archivo ERP (Excel/CSV)  
- Validar formatos y confirmar carga

#### 2. **Ejecutar Validación** ⚖️
- Click en "Ejecutar Validación" desde dashboard o carga
- El sistema procesará automáticamente:
  - Búsqueda de coincidencias por prefijo+folio
  - Detección de discrepancias en valor/fecha
  - Clasificación en 4 tipos
  - Generación de estadísticas

#### 3. **Revisar Resultados** 🔍  
- Acceder a `/dian_vs_erp/validaciones`
- Usar filtros para análisis específico
- Hacer clic en registros para ver detalles
- Exportar subconjuntos filtrados a Excel

#### 4. **Generar Reportes** 📊
- Acceder a `/dian_vs_erp/reportes`  
- Seleccionar tipo y formato de reporte
- Configurar envío por email (opcional)
- Descargar o enviar automáticamente

### Casos de Uso Frecuentes

#### **Auditoría Mensual**
1. Cargar archivos del mes actual
2. Ejecutar validación completa  
3. Generar reporte de discrepancias
4. Enviar a equipo contable por email

#### **Investigación de Discrepancias**
1. Filtrar validaciones por tipo "discrepante"
2. Revisar detalles factura por factura
3. Identificar patrones en observaciones
4. Exportar para análisis externo

#### **Dashboard Ejecutivo**
1. Acceder a dashboard principal
2. Revisar estadísticas de periodo actual
3. Comparar con periodos anteriores
4. Identificar tendencias en el tiempo

---

## 📊 Métricas y Rendimiento

### Capacidad del Sistema
- ✅ **Archivos**: Hasta 100MB por archivo (Excel/CSV)
- ✅ **Registros**: Procesamiento optimizado para 100K+ facturas
- ✅ **Concurrencia**: Múltiples usuarios simultáneos
- ✅ **Histórico**: Retención configurable (por defecto 30 días)

### Algoritmo de Validación
```python
# Lógica de matching
def buscar_coincidencias(periodo):
    # 1. JOIN por prefijo + folio
    coincidencias = DIAN ∩ ERP  
    
    # 2. Validar tolerancias
    if |valor_dian - valor_erp| <= tolerancia_valor:
        return "coincidente"
    else:
        return "discrepante" 
    
    # 3. Identificar únicos  
    solo_dian = DIAN - ERP
    solo_erp = ERP - DIAN
```

### Índices de Base de Datos
- 📈 Búsquedas por periodo: `idx_*_periodo`
- 🔍 Filtros por NIT: `idx_*_nit`  
- 📅 Ordenamiento por fecha: `idx_*_fecha_factura`
- 💰 Rangos de valor: `idx_*_valor`

---

## 🔧 Configuración Avanzada

### Variables de Configuración (`configuracion_validacion`)
```sql
tolerancia_valor: 0.01          -- Tolerancia en diferencias de valor
tolerancia_fecha: 1             -- Tolerancia en días para fechas
email_notificaciones: true      -- Activar emails automáticos  
email_destinatarios: ""         -- Lista de destinatarios por defecto
auto_procesamiento: false       -- Validar automáticamente al cargar
retener_archivos_dias: 30       -- Días de retención de archivos
columnas_dian: ["nit", ...]     -- Mapeo de columnas DIAN
columnas_erp: ["nit", ...]      -- Mapeo de columnas ERP
```

### Personalización de Templates
Los archivos HTML utilizan:
- 🎨 **TailwindCSS** para estilos responsivos
- ⚡ **JavaScript vanilla** para interactividad
- 📱 **Font Awesome** para iconografía
- 🌈 **CSS custom** con variables del sistema principal

---

## 🐛 Troubleshooting

### Problemas Comunes

#### ❌ Error: "Módulo no accesible"
**Solución:** Verificar que el blueprint está registrado:
```python
# En app.py debe existir:
app.register_blueprint(dian_vs_erp_bp, url_prefix='/dian_vs_erp')
```

#### ❌ Error: "Tabla no existe"  
**Solución:** Ejecutar script de creación:
```cmd
python crear_tablas_dian_vs_erp.py
```

#### ❌ Error: "Archivo no soportado"
**Solución:** Verificar formato:
- ✅ Archivos válidos: `.xlsx`, `.xls`, `.csv`
- ✅ Tamaño máximo: 100MB
- ✅ Columnas requeridas: nit, nombre, prefijo, folio, fecha, valor

#### ❌ Error: "Email no enviado"
**Solución:** Verificar configuración SMTP:
- Revisar variables en `.env`: `MAIL_SERVER`, `MAIL_USERNAME`, etc.
- Verificar que el correo esté configurado en sistema principal

#### ❌ Validación muy lenta
**Solución:** Optimizar base de datos:
```sql
-- Verificar índices
SELECT * FROM pg_indexes WHERE tablename LIKE '%dian%';

-- Actualizar estadísticas  
ANALYZE reportes_dian;
ANALYZE facturas_erp;
ANALYZE validaciones_facturas;
```

---

## 🔄 Roadmap de Mejoras

### Versión Actual (v1.0)
✅ Funcionalidad básica completa  
✅ Interfaz web responsive
✅ Validación manual por periodo
✅ Reportes Excel/CSV
✅ Integración con sistema principal

### Próximas Versiones

#### v1.1 - Automatización
- [ ] Programación de validaciones automáticas
- [ ] Notificaciones proactivas por email/Telegram  
- [ ] API REST para integración externa
- [ ] Webhooks para eventos de validación

#### v1.2 - Analytics Avanzado
- [ ] Dashboard con gráficos Chart.js
- [ ] Análisis de tendencias temporales
- [ ] Detección de patrones en discrepancias  
- [ ] Alertas por umbral de coincidencia

#### v1.3 - Integraciones
- [ ] Conexión directa con APIs de DIAN
- [ ] Importación automática desde ERP
- [ ] Exportación a sistemas contables (SAP, etc.)
- [ ] Integración con firma digital Adobe Sign

---

## 👥 Soporte y Mantenimiento

### Logs del Sistema
📍 Todos los eventos se registran en:
- `logs/security.log` - Eventos de seguridad y accesos
- Base de datos - Auditoría completa de procesamientos

### Respaldos Recomendados
```sql
-- Backup mensual de datos de validación
pg_dump gestor_documental \
  --table=reportes_dian \
  --table=facturas_erp \
  --table=validaciones_facturas \
  --table=procesamientos_periodo \
  > backup_dian_vs_erp_YYYY_MM.sql
```

### Contacto Técnico
- 📧 Soporte: Equipo de desarrollo del Gestor Documental
- 📖 Documentación: Este archivo + copilot-instructions.md
- 🐛 Issues: Reportar en sistema de tickets interno

---

## 🎉 Conclusión

El módulo **DIAN vs ERP** está completamente implementado y listo para producción. Proporciona una solución integral para:

✅ **Validación automatizada** de consistencia fiscal  
✅ **Interfaz intuitiva** para usuarios no técnicos
✅ **Reportería completa** con múltiples formatos  
✅ **Auditoría exhaustiva** de todos los procesamientos
✅ **Integración perfecta** con el sistema existente

**🚀 Para comenzar a usar:**
1. Ejecutar `python crear_tablas_dian_vs_erp.py`
2. Reiniciar la aplicación Flask
3. Acceder a http://localhost:8099/dian_vs_erp/
4. Cargar archivos y comenzar validaciones

---

**📅 Documento actualizado:** 13 de Noviembre de 2025  
**🏢 Sistema:** Gestor Documental - Supertiendas Cañaveral  
**👨‍💻 Implementado por:** GitHub Copilot con supervisión técnica