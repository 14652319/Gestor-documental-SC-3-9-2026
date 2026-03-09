# SISTEMA DE CARGA INCREMENTAL - IMPLEMENTADO
========================================

## ✅ CAMBIOS REALIZADOS (19 febrero 2026)

Se modificó el sistema de carga de datos para ser **INCREMENTAL** en lugar de borrar todo cada vez.

### 🔄 NUEVO COMPORTAMIENTO:

#### 1️⃣ **DIAN, ERP_COMERCIAL, ERP_FINANCIERO**:
- ✅ **Conserva datos viejos**
- ✅ **Agrega datos nuevos**
- ✅ **Si la clave ya existe → NO inserta** (mantiene el registro viejo)
- 🛠️ Método: `INSERT ... ON CONFLICT (clave) DO NOTHING`

**Ejemplo:**
```
BD tiene:  
  - Factura FC-001 del 01-enero
  
Subes archivo con:
  - Factura FC-001 del 01-enero (duplicada)
  - Factura FC-002 del 15-enero (nueva)
  
Resultado:
  - FC-001: Mantiene la vieja (no sobrescribe)
  - FC-002: Se agrega como nueva ✅
```

#### 2️⃣ **ACUSES**:
- ✅ **Conserva datos viejos**
- ✅ **Agrega nuevos**
- ✅ **Si la clave ya existe → Actualiza SOLO si jerarquía mayor**
- 🛠️ Método: `INSERT ... ON CONFLICT (clave_acuse) DO UPDATE ... WHERE jerarquia_nueva > jerarquia_vieja`

**Jerarquía de estados** (menor a mayor):
```
1. Pendiente
2. Acuse Recibido
3. Acuse Bien/Servicio
4. Rechazada
5. Aceptación Expresa
6. Aceptación Tácita
```

**Ejemplo:**
```
BD tiene:  
  - CUFE ABC123: Estado = "Acuse Recibido" (jerarquía 2)
  
Subes archivo con:
  - CUFE ABC123: Estado = "Aceptación Expresa" (jerarquía 5) → ✅ ACTUALIZA (5 > 2)
  - CUFE ABC123: Estado = "Pendiente" (jerarquía 1) → ❌ NO actualiza (1 < 2)
```

#### 3️⃣ **MAESTRO_DIAN_VS_ERP**:
- 🔄 **Se regenera completo** desde las tablas acumuladas
- ✅ Refleja todos los datos históricos + nuevos

---

## 🔑 ESPECIFICACIÓN DETALLADA DE CLAVES

### 📋 ¿Cómo identifica el sistema las facturas duplicadas?

Cada tabla tiene una **clave única** que se construye automáticamente al procesar los archivos Excel. Esta clave determina si una factura es nueva o duplicada.

### 📊 TABLA 1: DIAN

**Archivo Excel:** `Dian.xlsx` o `ERP Dian.xlsx`  
**Ubicación:** `uploads/dian/`

**Clave de comparación:** `clave`  
**Construcción:** `NIT_EMISOR + PREFIJO + FOLIO`

**Proceso de extracción:**
1. **NIT_EMISOR** se limpia (sin puntos, sin guiones)
2. **PREFIJO** se extrae de la columna "Prefijo" (se limpia)
3. **FOLIO** se toman los últimos 8 dígitos SIN ceros a la izquierda

**Ejemplos reales:**

| Excel: NIT Emisor | Excel: Prefijo | Excel: Folio | Clave generada | ¿Duplicado? |
|-------------------|----------------|--------------|----------------|-------------|
| 900.123.456-7 | FC | 00012345 | `900123456FC12345` | - |
| 900123456 | FC | 12345 | `900123456FC12345` | ✅ SÍ (misma clave) |
| 900.123.456-7 | FC | 00012346 | `900123456FC12346` | ❌ NO (folio diferente) |
| 800.999.888-1 | FP | 00056789 | `800999888FP56789` | ❌ NO (NIT diferente) |

**Campo adicional:** `clave_acuse` = `CUFE` (para relación con tabla `acuses`)

**Comparación en BD:**
```sql
INSERT INTO dian (...)
ON CONFLICT (clave) DO NOTHING
-- Si la clave existe → IGNORA el registro nuevo
-- Si la clave NO existe → INSERTA el registro
```

---

### 📊 TABLA 2: ERP_COMERCIAL

**Archivo Excel:** `ERP comercial.xlsx` o `ERP Comercial 18 02 2026.xlsx`  
**Ubicación:** `uploads/erp_cm/`

**Clave de comparación:** `clave_erp_comercial`  
**Construcción:** `PROVEEDOR + PREFIJO + FOLIO`

**Proceso de extracción:**
1. **PROVEEDOR** (columna "Proveedor") se limpia
2. **PREFIJO** se extrae del campo "Docto. proveedor" (parte izquierda del guion)
3. **FOLIO** se extrae del campo "Docto. proveedor" (parte derecha del guion, últimos 8 dígitos sin ceros)

**Ejemplos reales:**

| Excel: Proveedor | Excel: Docto. proveedor | Prefijo extraído | Folio extraído | Clave generada |
|------------------|-------------------------|------------------|----------------|----------------|
| 900789456 | FP-00056789 | FP | 56789 | `900789456FP56789` |
| 900.789.456-1 | FP-56789 | FP | 56789 | `900789456FP56789` ✅ DUPLICADO |
| 800555111 | FC-00012345 | FC | 12345 | `800555111FC12345` |
| 900789456 | NC-00000123 | NC | 123 | `900789456NC123` |

**Relación con DIAN:**
Esta clave se compara con `dian.clave` para determinar si la factura existe en DIAN:
```sql
SELECT * FROM dian
LEFT JOIN erp_comercial ON dian.clave = erp_comercial.clave_erp_comercial
-- Si coinciden: Factura está en DIAN y en ERP Comercial ✅
-- Si NO coinciden: Facturas faltantes o desajustes ⚠️
```

**Comparación en BD:**
```sql
INSERT INTO erp_comercial (...)
ON CONFLICT (clave_erp_comercial) DO NOTHING
-- Si la clave existe → IGNORA el registro nuevo
```

---

### 📊 TABLA 3: ERP_FINANCIERO

**Archivo Excel:** `ERP Financiero.xlsx` o `ERP financiero 18 02 2026.xlsx`  
**Ubicación:** `uploads/erp_fn/`

**Clave de comparación:** `clave_erp_financiero`  
**Construcción:** `PROVEEDOR + PREFIJO + FOLIO`

**Proceso de extracción:**
1. **PROVEEDOR** (columna "Proveedor") se limpia
2. **PREFIJO** se extrae del campo "Docto. proveedor" (parte izquierda del guion)
3. **FOLIO** se extrae del campo "Docto. proveedor" (parte derecha del guion, últimos 8 dígitos sin ceros)

**Ejemplos reales:**

| Excel: Proveedor | Excel: Docto. proveedor | Prefijo | Folio | Clave generada |
|------------------|-------------------------|---------|-------|----------------|
| 800111222 | FV-00078901 | FV | 78901 | `800111222FV78901` |
| 800.111.222-3 | FV-78901 | FV | 78901 | `800111222FV78901` ✅ DUPLICADO |
| 900333444 | ND-00001234 | ND | 1234 | `900333444ND1234` |

**Relación con DIAN:**
Esta clave se compara con `dian.clave` para determinar si la factura existe en DIAN:
```sql
SELECT * FROM dian
LEFT JOIN erp_financiero ON dian.clave = erp_financiero.clave_erp_financiero
-- Si coinciden: Factura está en DIAN y en ERP Financiero ✅
```

**Comparación en BD:**
```sql
INSERT INTO erp_financiero (...)
ON CONFLICT (clave_erp_financiero) DO NOTHING
-- Si la clave existe → IGNORA el registro nuevo
```

---

### 📊 TABLA 4: ACUSES

**Archivo Excel:** `acuses.xlsx` o `acuses 2.xlsx`  
**Ubicación:** `uploads/acuses/`

**Clave de comparación:** `clave_acuse`  
**Construcción:** `CUFE` (Código Único de Factura Electrónica)

**Proceso de extracción:**
1. **CUFE** se extrae directamente de la columna "CUFE" del archivo Excel
2. Es un código largo (hash) generado por la DIAN
3. NO se construye, se usa tal cual viene del Excel

**Ejemplos reales:**

| Excel: CUFE (extracto) | Clave generada | Excel: Estado Docto. | Jerarquía |
|------------------------|----------------|----------------------|-----------|
| a1b2c3d4e5f6g7h8... | `a1b2c3d4e5f6g7h8...` | Acuse Recibido | 2 |
| a1b2c3d4e5f6g7h8... | `a1b2c3d4e5f6g7h8...` | Aceptación Expresa | 5 ✅ ACTUALIZA (5 > 2) |
| x9y8z7w6v5u4t3s2... | `x9y8z7w6v5u4t3s2...` | Pendiente | 1 |

**Relación con DIAN:**
Esta clave se compara con `dian.clave_acuse` (que también es el CUFE):
```sql
SELECT * FROM dian
LEFT JOIN acuses ON dian.clave_acuse = acuses.clave_acuse
-- Si coinciden: Factura DIAN tiene acuse registrado ✅
```

**Comparación en BD (ESPECIAL - Con jerarquía):**
```sql
INSERT INTO acuses (...)
ON CONFLICT (clave_acuse) DO UPDATE SET
    estado_docto = EXCLUDED.estado_docto,
    [todos los campos...],
    fecha_actualizacion = CURRENT_TIMESTAMP
WHERE calcular_jerarquia_acuse(EXCLUDED.estado_docto) > calcular_jerarquia_acuse(acuses.estado_docto)
-- Si la clave existe Y el nuevo estado tiene jerarquía mayor → ACTUALIZA
-- Si la clave existe Y el nuevo estado tiene jerarquía menor → IGNORA
-- Si la clave NO existe → INSERTA
```

---

## 🔍 RESUMEN DE COMPARACIONES

| Tabla | Archivo Excel | Campo Clave | Construcción | Compara con |
|-------|---------------|-------------|--------------|-------------|
| **dian** | `Dian.xlsx` | `clave` | `NIT + PREFIJO + FOLIO` | Sí misma (duplicados) |
| **erp_comercial** | `ERP comercial.xlsx` | `clave_erp_comercial` | `PROVEEDOR + PREFIJO + FOLIO` | `dian.clave` (matching) |
| **erp_financiero** | `ERP Financiero.xlsx` | `clave_erp_financiero` | `PROVEEDOR + PREFIJO + FOLIO` | `dian.clave` (matching) |
| **acuses** | `acuses.xlsx` | `clave_acuse` | `CUFE` (directo) | `dian.clave_acuse` (matching) |

### 🔗 Flujo de Matching (Reconciliación):

```
1️⃣ DIAN.clave (900123456FC12345)
    ↓ compara con
2️⃣ ERP_COMERCIAL.clave_erp_comercial (900123456FC12345) ✅ MATCH
    ↓ compara con
3️⃣ ERP_FINANCIERO.clave_erp_financiero (900123456FC12345) ✅ MATCH

Por separado:
4️⃣ DIAN.clave_acuse (CUFE: a1b2c3d4...)
    ↓ compara con
5️⃣ ACUSES.clave_acuse (CUFE: a1b2c3d4...) ✅ MATCH

Resultado:
📋 Tabla MAESTRO muestra: DIAN ↔ ERP CM ↔ ERP FN ↔ ACUSES
```

---

### 🏗️ ARQUITECTURA MODIFICADA:

**Antes:**
```sql
DELETE FROM dian
DELETE FROM erp_comercial  
DELETE FROM erp_financiero
DELETE FROM acuses
DELETE FROM maestro_dian_vs_erp

INSERT INTO dian VALUES (archivo nuevo)
-- Resultado: Solo datos del archivo nuevo
```

**Ahora:**
```sql
-- Tabla temporal
CREATE TEMP TABLE temp_dian_nuevos (...)
COPY datos nuevos → temp_dian_nuevos

-- Insertar solo nuevos
INSERT INTO dian SELECT * FROM temp_dian_nuevos
ON CONFLICT (clave) DO NOTHING

-- Resultado: Datos viejos + nuevos acumulados
```

### 📊 RESTRICCIONES UNIQUE AGREGADAS:

- `acuses.uk_acuses_clave UNIQUE (clave_acuse)` ✅ **NUEVA**
- `dian.uk_dian_clave UNIQUE (clave)` ✅ Ya existía
- `erp_comercial.uk_erp_comercial_clave UNIQUE (clave_erp_comercial)` ✅ Ya existía
- `erp_financiero.uk_erp_financiero_clave UNIQUE (clave_erp_financiero)` ✅ Ya existía

### 🔧 FUNCIÓN DE JERARQUÍA (NUEVA):

```sql
CREATE FUNCTION calcular_jerarquia_acuse(estado TEXT) RETURNS INT AS $$
BEGIN
    RETURN CASE 
        WHEN estado IS NULL OR estado = '' OR estado = 'Pendiente' THEN 1
        WHEN estado = 'Acuse Recibido' THEN 2
        WHEN estado = 'Acuse Bien/Servicio' THEN 3
        WHEN estado = 'Rechazada' THEN 4
        WHEN estado = 'Aceptación Expresa' THEN 5
        WHEN estado = 'Aceptación Tácita' THEN 6
        ELSE 1
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

### 📝 ARCHIVOS MODIFICADOS:

1. **`modules/dian_vs_erp/routes.py`**:
   - Línea ~1219: `insertar_dian_bulk()` - Carga incremental
   - Línea ~1364: `insertar_erp_comercial_bulk()` - Carga incremental
   - Línea ~1509: `insertar_erp_financiero_bulk()` - Carga incremental
   - Línea ~1672: `insertar_acuses_bulk()` - Carga incremental con jerarquía

2. **`AGREGAR_UNIQUE_ACUSES.py`** (nuevo):
   - Agrega restricción UNIQUE a tabla acuses
   - Elimina duplicados existentes manteniendo el de mayor jerarquía

### ✅ VENTAJAS DEL SISTEMA INCREMENTAL:

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Datos históricos** | ❌ Se pierden al procesar nuevo archivo | ✅ Se conservan |
| **Archivos parciales** | ❌ Solo se ve el último archivo | ✅ Se acumulan todos |
| **Duplicados** | ⚠️ Error o sobrescribe | ✅ Ignora duplicados |
| **Acuses** | ⚠️ Sobrescribe con cualquier estado | ✅ Solo actualiza si jerarquía mayor |
| **Rendimiento** | 🐢 Borra + Inserta todo | ⚡ Solo inserta nuevos |

### 🚀 FLUJO DE CARGA RECOMENDADO:

**Opción A: Archivos mensuales completos** (Recomendado para auditoría)
```
Mes 1: DIAN_ENERO_2026.xlsx (todo enero)
Mes 2: DIAN_FEBRERO_2026.xlsx (todo febrero)
Mes 3: DIAN_MARZO_2026.xlsx (todo marzo)

Resultado: BD tiene enero + febrero + marzo completos
```

**Opción B: Archivos incrementales** (Ahora soportado ✅)
```
Semana 1: dian_semana1.xlsx (01-07 enero)
Semana 2: dian_semana2.xlsx (08-14 enero)  
Semana 3: dian_semana3.xlsx (15-21 enero)

Resultado: BD tiene semana1 + semana2 + semana3 acumuladas
```

**Opción C: Archivo acumulativo anual** (Más eficiente)
```
Cada vez:
1. Abre DIAN_2026.xlsx existente
2. Agrega filas nuevas al final
3. Guarda
4. Sube → Solo inserta las nuevas

Resultado: BD siempre tiene el año completo actualizado
```

### ⚠️ CASOS ESPECIALES:

#### ¿Qué pasa si quiero REEMPLAZAR datos existentes?

**Para DIAN, ERP_COMERCIAL, ERP_FINANCIERO:**
Debes borrar manualmente los registros que quieres reemplazar:
```sql
-- Ejemplo: Reemplazar facturas de un NIT específico
DELETE FROM dian WHERE nit_emisor = '900123456';
-- Luego procesas el archivo nuevo
```

**Para ACUSES:**
Si quieres forzar una actualización incluso con menor jerarquía:
```sql
-- Ejemplo: Forzar estado de un CUFE específico
DELETE FROM acuses WHERE clave_acuse = 'CUFE12345...';
-- Luego procesas el archivo nuevo
```

### 🎯 TESTING RECOMENDADO:

1. **Carga inicial:**
   - Subir archivos completos de DIAN, ERP, Acuses
   - Verificar que se carguen todos los registros

2. **Carga incremental:**
   - Subir archivo con algunos registros nuevos y algunos duplicados
   - Verificar que solo se agreguen los nuevos

3. **Actualización de acuses:**
   - Cargar acuse con estado "Acuse Recibido"
   - Cargar mismo CUFE con "Aceptación Expresa"
   - Verificar que se actualizó
   - Cargar mismo CUFE con "Pendiente"
   - Verificar que NO se actualizó

### 📞 SOPORTE:

Si encuentras problemas:
1. Verifica los logs durante el procesamiento
2. Checa la consola para mensajes como:
   - "🔄 Carga INCREMENTAL (conserva datos viejos, agrega nuevos)"
   - "✅ X registros NUEVOS insertados (duplicados ignorados)"
   - "✅ X registros procesados (nuevos + actualizaciones por jerarquía)"

---

**Fecha de implementación:** 19 de febrero de 2026
**Versión:** 1.0 - Sistema Incremental
**Estado:** ✅ IMPLEMENTADO Y TESTEADO
