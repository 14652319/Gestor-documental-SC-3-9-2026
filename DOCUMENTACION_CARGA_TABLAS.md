# Documentación: Carga de Datos – Módulo DIAN vs ERP
*Generado automáticamente – Diciembre 2025*

---

## Índice
1. [Resumen del Sistema](#1-resumen-del-sistema)
2. [Tabla `dian`](#2-tabla-dian)
3. [Tabla `erp_comercial`](#3-tabla-erp_comercial)
4. [Tabla `erp_financiero`](#4-tabla-erp_financiero)
5. [Tabla `acuses`](#5-tabla-acuses)
6. [Tabla `maestro_dian_vs_erp`](#6-tabla-maestro_dian_vs_erp)
7. [Flujo de Carga Completo](#7-flujo-de-carga-completo)
8. [Módulo cargador_bd.py](#8-módulo-cargador_bdpy)
9. [Carga desde el Navegador](#9-carga-desde-el-navegador)
10. [Estado Final de Registros](#10-estado-final-de-registros)
11. [Bugs Resueltos en esta Sesión](#11-bugs-resueltos-en-esta-sesión)

---

## 1. Resumen del Sistema

El módulo DIAN vs ERP concilia facturas electrónicas del sistema DIAN con los
registros contabilizados en el ERP (módulo Comercial y módulo Financiero). 

La reconciliación se construye en **5 tablas PostgreSQL**:

| Tabla | Origen | Propósito |
|-------|--------|-----------|
| `dian` | Descarga DIAN (Excel) | Facturas electrónicas recibidas |
| `erp_comercial` | ERP módulo Comercial (Excel) | Facturas causadas en CM |
| `erp_financiero` | ERP módulo Financiero (Excel) | Facturas causadas en FN |
| `acuses` | DIAN Acuses (Excel) | Estado de aprobación DIAN |
| `maestro_dian_vs_erp` | Construido automáticamente | Vista consolidada DIAN ↔ ERP |

El módulo cargador: `modules/dian_vs_erp/cargador_bd.py`

---

## 2. Tabla `dian`

### Descripción
Contiene **todas las facturas electrónicas** reportadas por el sistema DIAN.
Cada fila = un documento electrónico (factura, nota crédito, nota débito, etc.)

### Origen del archivo
Archivo Excel descargado directamente del portal DIAN.  
Nombre típico: `DIAN_Documentos_*.xlsx`

### Función de carga: `cargar_dian(ruta_excel, db_url, truncar=True)`

#### Columnas detectadas automáticamente (por nombre normalizado)
| Columna Excel | Campo en BD | Notas |
|---------------|-------------|-------|
| `Tipo Documento` | `tipo_documento` | Filtrado según TIPOS_EXCLUIDOS |
| `CUFE` / `CUDE` | `cufe_cude` | Identificador único DIAN |
| `Folio` | `folio` | Número de la factura |
| `Prefijo` | `prefijo` | Prefijo (ej: FV, FAC) |
| `Divisa` | `divisa` | Moneda |
| `Forma Pago` | `forma_pago` | 1→Contado, 2→Crédito |
| `Medio Pago` | `medio_pago` | Efectivo, transferencia, etc. |
| `Fecha Emisión` | `fecha_emision` | Fecha de la factura |
| `Fecha Recepción` | `fecha_recepcion` | Fecha de recepción |
| `NIT Emisor` | `nit_emisor` | NIT del proveedor |
| `Nombre/Razón Emisor` | `nombre_emisor` | Nombre del proveedor |
| `NIT Receptor` | `nit_receptor` | NIT de Supertiendas |
| `Nombre Receptor` | `nombre_receptor` | Razón social receptora |
| `IVA`, `ICA`, `IC`, `INC`, etc. | campos de impuesto | Numéricos |
| `RETE_IVA`, `RETE_RENTA`, `RETE_ICA` | retenciones | Numéricos |
| `Total` | `total` | Valor total del documento |
| `Estado` | `estado` | Estado DIAN |
| `Grupo` | `grupo` | Grupo DIAN |

#### Campo calculado: `clave`
```
clave = "{nit_emisor}-{prefijo}-{folio}"
```
Es la llave única para detectar duplicados.

#### Tipos de documento EXCLUIDOS
Los siguientes tipos se filtran y **no se insertan**:
- `nota de debito`
- `nota débito`
- `nota de débito`
- `documento soporte`
- `documento soporte de pago al exterior`
- Y otros documentos no-factura

#### Mapeo de Forma de Pago
| Valor Excel | Valor en BD |
|-------------|-------------|
| `1` | `Contado` |
| `2` | `Crédito` |
| Otros / vacío | Se usa el valor tal cual |

#### Proceso de inserción
1. `READ` Excel → 61,940+ filas leídas
2. `FILTER` tipos excluidos
3. `CREATE TEMP TABLE _t_dian (LIKE dian ...)`
4. `COPY FROM` → tabla temporal
5. `TRUNCATE TABLE dian` (si `truncar=True`)
6. `INSERT INTO dian SELECT * FROM _t_dian`

**Registros actuales:** 61,940

---

## 3. Tabla `erp_comercial`

### Descripción
Contiene los documentos causados en el **módulo Comercial** del ERP.
Cada fila = una factura de proveedor registrada en el sistema contable comercial.

### Origen del archivo
Reporte Excel del ERP – módulo Comercial.  
Nombre típico: `ERP_Comercial_*.xlsx`

### Función de carga: `cargar_erp(ruta_excel, 'erp_comercial', db_url)`

#### Columnas detectadas automáticamente
| Columna Excel | Campo en BD | Notas |
|---------------|-------------|-------|
| `Proveedor` | `proveedor` | NIT del proveedor |
| `Razón Social` / `Razón Proveedor` | `razon_social` | Nombre del proveedor |
| `Fecha Docto Prov.` | `fecha_recibido` | Fecha del documento |
| `Docto. Proveedor` | `docto_proveedor` | Nro. doc ERP (ej: FV-001234) |
| `Valor Bruto` / `Importe` | `valor` | Valor base |
| `Valor Imptos` | `valor_imptos` | Impuestos causados |
| `C.O.` | `co` | Centro de Operación |
| `Usuario Creación` | `usuario_creacion` | Usuario que causó |
| `Clase Docto` | `clase_documento` | Clase del documento |
| `Nro. Documento` | `nro_documento` | Número interno ERP |

#### Detección robusta de `docto_proveedor`
La columna `Docto. proveedor` se detecta excluyendo la palabra `'fecha'` para
evitar confusión con `Fecha docto. prov.`:
```python
docto_col = find_col('docto', 'prov', exclude=['fecha'])
```

#### Campos calculados

**`prefijo` y `folio`** — se extraen del campo `Docto. proveedor`:
```
"FV-001234" → prefijo="FV", folio_raw="001234"
"001234"    → prefijo="",   folio_raw="001234"
folio = ultimos_8_digitos_sin_ceros(folio_raw)  # → "1234"
```

**`clave_erp_comercial`** — clave de reconciliación con DIAN:
```
nit_solo = solo_digitos(nit_proveedor)
clave_erp_comercial = "{nit_solo}{prefijo}{folio}"
```
Esta clave se usa para hacer JOIN con la tabla `dian`.

**`doc_causado_por`** — identifica quién causó el documento:
```
doc_causado_por = "{co} | {usuario_creacion} | {nro_documento}"
Ejemplo: "017 | inte.artificial | CCR-00054949"
```
Este campo aparece en la columna **"Causador"** del visor.

#### Proceso de inserción
1. `READ` Excel
2. `DEDUP` por `clave_erp_comercial` (último prevalece)
3. `CREATE TEMP TABLE _t_erp_comercial` (sin constraints)
4. `DROP` constraints heredados de la temp table
5. `COPY FROM` → tabla temporal
6. `TRUNCATE TABLE erp_comercial`
7. `INSERT ... ON CONFLICT (clave_erp_comercial) DO NOTHING`

**Registros actuales:** 62,446

---

## 4. Tabla `erp_financiero`

### Descripción
Contiene los documentos causados en el **módulo Financiero** del ERP.
Generalmente son acreedores/cuentas por pagar no-comerciales.

### Origen del archivo
Reporte Excel del ERP – módulo Financiero.  
Nombre típico: `ERP_Financiero_*.xlsx`

### Función de carga: `cargar_erp(ruta_excel, 'erp_financiero', db_url)`

Idéntica a `erp_comercial` excepto:
- Campo de impuestos: `valor_impuestos` (en lugar de `valor_imptos`)
- Clave única: `clave_erp_financiero`
- `modulo` = `'Financiero'`

#### `doc_causado_por` (igual que comercial)
```
doc_causado_por = "{co} | {usuario_creacion} | {nro_documento}"
Ejemplo: "301 | lmrestrepov | FAC-00001843"
```

**Registros actuales:** 3,179

---

## 5. Tabla `acuses`

### Descripción
Contiene el **estado de aprobación DIAN** de las facturas.
Los estados van desde "Pendiente" hasta "Aceptación Tácita" (máxima jerarquía).

### Origen del archivo
Descarga DIAN de acuses de recibo.  
Nombre típico: `Acuses_*.xlsx`

### Función de carga: `cargar_acuses(ruta_excel, db_url)`

#### Mapeo de columnas Excel → BD
| Columna Excel | Campo en BD |
|---------------|-------------|
| `Fecha` | `fecha` |
| `Adquiriente` | `adquiriente` |
| `Factura` | `factura` |
| `Emisor` | `emisor` |
| `NIT Emisor` | `nit_emisor` |
| `NIT. PT` | `nit_pt` |
| `Estado Docto.` | `estado_docto` |
| `Descripción Reclamo` | `descripcion_reclamo` |
| `Tipo Documento` | `tipo_documento` |
| `CUFE` | `cufe` |
| `Valor` | `valor` |
| `Acuse Recibido` | `acuse_recibido` |
| `Recibo Bien/Servicio` | `recibo_bien_servicio` |
| `Aceptación Expresa` | `aceptacion_expresa` |
| `Reclamo` | `reclamo` |
| `Aceptación Tácita` | `aceptacion_tacita` |

#### Deduplicación por CUFE (jerarquía)
Cuando el mismo CUFE aparece varias veces con distintos estados,
se mantiene el estado de mayor jerarquía:
```
Jerarquía de estados:
1 = Pendiente
2 = No Registra  
3 = Acuse Recibido
4 = Recibo Bien/Servicio (Acuse Bien/Servicio)
5 = Aceptación Expresa
6 = Aceptación Tácita  ← mayor jerarquía
```

**Registros actuales:** 51,283

---

## 6. Tabla `maestro_dian_vs_erp`

### Descripción
Vista consolidada que **une DIAN + ERP + Acuses** en una sola tabla.
Se reconstruye automáticamente después de cada carga.
NO se debe editar directamente (se sobreescribe en cada reconstrucción).

### Función de construcción: `reconstruir_maestro(db_url)`

#### Algoritmo paso a paso

**Paso 1: Lookup ERP**
```
Para cada fila de erp_comercial y erp_financiero:
    clave = _crear_clave(proveedor, prefijo, folio)
    guardar en diccionario: clave → {razon_social, modulo, doc_causado_por}
```

**Paso 2: Lookup Acuses**
```
Para cada fila de acuses:
    guardar en diccionario: cufe → estado_docto (máxima jerarquía)
```

**Paso 3: Tipo de Tercero**
```
Si NIT está en erp_comercial Y erp_financiero → "Proveedor y Acreedor"
Si NIT está solo en erp_comercial             → "Proveedor"
Si NIT está solo en erp_financiero            → "Acreedor"
Sino                                          → "No Registrado"
```

**Paso 4: Construir registro para cada fila DIAN**
```
Para cada factura en dian:
    nit    = solo_digitos(nit_emisor)
    prefijo = extraer_prefijo(prefijo_raw)
    folio   = ultimos_8_sin_ceros(solo_digitos(folio_raw))
    clave  = _crear_clave(nit, prefijo_raw, folio_raw)
    
    erp_info  = lookup_erp[clave] o {}
    modulo    = erp_info.modulo        → "" si no está en ERP
    causador  = erp_info.doc_causado_por  → columna "Causador" en visor
    
    estado_aprobacion = lookup_acuses[cufe] o "No Registra"
    estado_contable   = "Causada" si modulo else "No Registrada"
    acuses_recibidos  = 1 si "Acuse Bien/Servicio" else 2 si "Aceptación Expresa" else...
    dias              = (hoy - fecha_emision).days
```

**Función `_crear_clave`**  
Es el corazón de la reconciliación:
```python
def _crear_clave(nit, prefijo, folio):
    return (
        _extraer_folio(str(nit))            # solo dígitos del NIT
        + _extraer_prefijo(str(prefijo))    # prefijo alfanumérico
        + _ultimos_8_sin_ceros(             # últimos 8 dígitos, sin ceros a la izq.
              _extraer_folio(str(folio))
          )
    )

# Ejemplo:
# nit="900123456-1", prefijo="FV", folio="0001234"
# → "900123456" + "FV" + "1234"
# → clave = "900123456FV1234"
```

La misma función se usa en `cargar_erp()` para calcular `clave_erp`.
Así DIAN y ERP tienen claves comparables para hacer el match.

#### Backup y restauración de causación manual
Antes de sobrescribir el maestro, se **respaldan** los campos de causación manual:
```sql
-- Campos que se respaldan:
causada, fecha_causacion, usuario_causacion, doc_causado_por,
recibida, fecha_recibida, usuario_recibio,
rechazada, fecha_rechazo, motivo_rechazo,
estado_contable, origen_sincronizacion
```
Después de insertar los 61,940 registros nuevos, se **restauran** esos campos
haciendo UPDATE por `(nit_emisor, prefijo, folio)`.

#### Campos del maestro
| Campo | Origen | Descripción |
|-------|--------|-------------|
| `nit_emisor` | DIAN | NIT del proveedor |
| `razon_social` | ERP o DIAN | Nombre del proveedor (ERP tiene prioridad) |
| `fecha_emision` | DIAN | Fecha de la factura |
| `prefijo` | DIAN | Prefijo (FV, FAC, etc.) |
| `folio` | DIAN | Número de factura (normalizado) |
| `valor` | DIAN | Valor total |
| `tipo_documento` | DIAN | Sigla (FE = Factura Electrónica, etc.) |
| `cufe` | DIAN | Identificador único DIAN |
| `forma_pago` | DIAN | Contado / Crédito |
| `estado_aprobacion` | Acuses | Estado DIAN más alto por CUFE |
| `modulo` | ERP | "Comercial" / "Financiero" / "" |
| `estado_contable` | ERP/Manual | "Causada" / "No Registrada" / "Rechazada" |
| `doc_causado_por` | ERP | "CO \| usuario \| nro_doc" |
| `acuses_recibidos` | Acuses | Conteo numérico acuse recibido |
| `dias_desde_emision` | Calculado | Días desde fecha_emision hasta hoy |
| `tipo_tercero` | ERP | "Proveedor" / "Acreedor" / etc. |
| `causada`, etc. | Manual | Marcaciones manuales de causación |

**Registros actuales:** 61,940 (de los cuales 41,127 tienen módulo ERP)

---

## 7. Flujo de Carga Completo

```
ARCHIVOS EXCEL (descargados de DIAN/ERP)
        │
        ▼
┌─────────────────────────────────────────────┐
│          cargador_bd.py                     │
│                                             │
│  cargar_dian()       → tabla dian           │
│  cargar_erp(cm)      → tabla erp_comercial  │
│  cargar_erp(fn)      → tabla erp_financiero │
│  cargar_acuses()     → tabla acuses         │
│              │                              │
│              ▼                              │
│  reconstruir_maestro()                      │
│    1. lookup ERP por clave                  │
│    2. lookup acuses por CUFE                │
│    3. por cada fila DIAN → crear registro   │
│    4. COPY FROM → maestro_dian_vs_erp       │
│    5. restaurar causación manual            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        maestro_dian_vs_erp (61,940 filas)
                   │
                   ▼
          /dian_vs_erp/visor_v2
          (tabla en el navegador)
```

---

## 8. Módulo `cargador_bd.py`

**Ubicación:** `modules/dian_vs_erp/cargador_bd.py`  
**Líneas:** ~1010

### Funciones exportadas
| Función | Descripción |
|---------|-------------|
| `cargar_dian(ruta, db_url, truncar=True)` | Carga Excel DIAN → tabla `dian` |
| `cargar_erp(ruta, tabla, db_url, truncar=True)` | Carga Excel ERP → `erp_comercial` o `erp_financiero` |
| `cargar_acuses(ruta, db_url, truncar=True)` | Carga Excel acuses → tabla `acuses` |
| `reconstruir_maestro(db_url)` | Reconstruye `maestro_dian_vs_erp` desde las 3 tablas |
| `procesar_archivo_subido(tipo, ruta, db_url)` | Despachador para carga desde navegador |

### Retorno de cada función
Todas devuelven un dict:
```python
{
    "tabla":        "dian",           # nombre de la tabla
    "insertados":   61940,            # registros insertados
    "omitidos":     1234,             # filas omitidas (excluidas/sin NIT)
    "total_leidos": 63174,            # filas totales en el Excel
    "tiempo":       8.3,              # segundos
    "mensaje":      "✅ DIAN: 61940 ..."  # mensaje legible
}
```

### Patrón de inserción (COPY FROM con tabla temporal)
Todas las funciones usan el mismo patrón para velocidad y seguridad:
```python
1. CREATE TEMP TABLE _t_x (LIKE tabla INCLUDING DEFAULTS) ON COMMIT DROP
2. Eliminar constraints de la temp table (evita UniqueViolation)
3. COPY FROM buf (io.StringIO con TSV)
4. TRUNCATE TABLE real
5. INSERT INTO tabla SELECT * FROM _t_x ON CONFLICT ... DO NOTHING
6. COMMIT
```
Velocidad: ~25,000 registros/segundo.

---

## 9. Carga desde el Navegador

### Endpoint de carga
```
POST  /dian_vs_erp/subir_archivos
```

### Parámetros del formulario (multipart/form-data)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `archivo_dian` | file | Excel DIAN |
| `archivo_erp_cm` | file | Excel ERP Comercial |
| `archivo_erp_fn` | file | Excel ERP Financiero |
| `archivo_acuses` | file | Excel Acuses |

### Flujo en `routes.py` (`subir_archivos()`)
```python
1. Para cada archivo recibido:
   - Guardar en carpeta temporal
   - Llamar procesar_archivo_subido(tipo, ruta, DB_URL)

2. Después de todos los archivos:
   - Llamar reconstruir_maestro_bd(DB_URL)

3. Retornar JSON con resultados de cada tabla
```

### Tipos detectados
| Nombre del campo | `tipo` enviado a cargador |
|-----------------|--------------------------|
| `archivo_dian` | `'dian'` |
| `archivo_erp_cm` | `'erp_cm'` |
| `archivo_erp_fn` | `'erp_fn'` |
| `archivo_acuses` | `'acuses'` |

### Estado: ✅ FUNCIONAL
El módulo `cargador_bd.py` está integrado en `routes.py` y el endpoint de upload
llama automáticamente `procesar_archivo_subido()` + `reconstruir_maestro()`.

---

## 10. Estado Final de Registros

| Tabla | Registros | Velocidad | Estado |
|-------|-----------|-----------|--------|
| `dian` | **61,940** | ~6 seg | ✅ |
| `erp_comercial` | **62,446** | ~4 seg | ✅ |
| `erp_financiero` | **3,179** | <1 seg | ✅ |
| `acuses` | **51,283** | ~3 seg | ✅ |
| `maestro_dian_vs_erp` | **61,940** (41,127 con módulo ERP) | ~36 seg | ✅ |

---

## 11. Bugs Resueltos en esta Sesión

### Bug 1: `UnicodeEncodeError` en Windows
**Síntoma:** `UnicodeEncodeError: 'charmap' codec can't encode character`  
**Causa:** La consola de Windows (cp1252) no podía mostrar emojis (✅, 📥...) del módulo  
**Fix:** Línea 1 de `cargador_bd.py`:
```python
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
```

### Bug 2: `erp_comercial` cargaba 0 registros (detección errónea de columna)
**Síntoma:** `cargar_erp()` encontraba la columna `docto_col` = `'Fecha docto. prov.'`  
en lugar de `'Docto. proveedor'`, generando claves incorrectas.  
**Causa:** `find_col('docto', 'prov')` coincidía primero con la columna de fecha.  
**Fix:**
```python
docto_col = find_col('docto', 'prov', exclude=['fecha'])
```
Sin este fix, la deduplicación por clave_erp eliminaba 53,147 registros,
dejando solo 10,392, y luego fallaba con `UniqueViolation`.

### Bug 3: `UniqueViolation` al insertar `erp_comercial`
**Síntoma:** `psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "uk_erp_comercial_clave"`  
**Causa:** La tabla temporal heredaba los constraints de la tabla real, y al hacer
COPY FROM con datos duplicados fallaba.  
**Fix:** Crear tabla temporal SIN constraints:
```python
cur.execute(f"""
    DO $$ DECLARE r RECORD;
    BEGIN
        FOR r IN SELECT conname FROM pg_constraint WHERE conrelid = '_t_{tabla}'::regclass
        LOOP EXECUTE 'ALTER TABLE _t_{tabla} DROP CONSTRAINT ' || quote_ident(r.conname);
        END LOOP;
    END $$
""")
```

### Bug 4: Regex `~` sobre columna numérica en `reconstruir_maestro`
**Síntoma:** `operator does not exist: numeric ~ unknown`  
**Causa:** El código usaba `CASE WHEN valor ~ '^[0-9.]+$' THEN valor::numeric` pero
`valor` ya era de tipo NUMERIC en la tabla temporal.  
**Fix:** Reemplazar la rama con `COALESCE`:
```python
COALESCE(valor, 0),
COALESCE(acuses_recibidos, 0),
COALESCE(dias_desde_emision, 0),
```

### Bug 5: Columna "Causador" mostraba solo el número de documento
**Síntoma:** El visor mostraba `doc_causado_por = "CCR-00069657"` (solo el nro_documento)  
**Causa:** El cargador anterior (antes de `cargador_bd.py`) no construía el campo
`doc_causado_por` con el formato completo.  
**Nuevo formato:**
```
"{co} | {usuario_creacion} | {nro_documento}"
Ejemplo: "017 | inte.artificial | CCR-00054949"
```
**Fix:** El campo ya está correcto en `cargador_bd.py`. Con la reconstrucción
del maestro el visor ahora muestra el formato completo.

---

## Arquitectura del Módulo (Referencia Rápida)

```
modules/dian_vs_erp/
├── cargador_bd.py          ← Todos los loaders + reconstruir_maestro
├── routes.py               ← Flask routes (5900+ líneas)
├── models.py               ← Modelos SQLAlchemy
└── templates/
    └── visor_dian_v2.html  ← Visor DIAN vs ERP (Tabulator.js)
```

**Base de datos:** `gestor_documental` (PostgreSQL)  
**Puerto:** 8099  
**URL del visor:** `http://localhost:8099/dian_vs_erp/visor_v2`
