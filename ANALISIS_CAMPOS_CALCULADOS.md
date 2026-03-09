# ANÁLISIS: Campos Calculados por Tabla
## Fecha: 19 Febrero 2026

## 📋 TABLA: dian
**Campos calculados:**
1. `clave` = NIT + PREFIJO + FOLIO (formato: "8050280413951") - UNIQUE
2. `clave_acuse` = CUFE (completo 96 chars) - para match con acuses
3. `modulo` = 'DIAN' (fijo)
4. `tipo_tercero` = 'PROVEEDOR' | 'ACREEDOR' | 'PROVEEDOR Y ACREEDOR' | 'NO REGISTRADO'
5. `n_dias` = días entre fecha_emision y fecha actual

**Fuente de datos:** Archivo DIAN.xlsx
**Match con ERP:** Por clave (NIT+PREFIJO+FOLIO)

---

## 📋 TABLA: erp_comercial
**Campos calculados:**
1. `prefijo` = extraer_prefijo(docto_proveedor) - ej: "FE" de "FE-3951"
2. `folio` = ultimos_8_sin_ceros(extraer_folio(docto_proveedor)) - ej: "3951"
3. `clave_erp_comercial` = NIT + PREFIJO + FOLIO - UNIQUE
4. `modulo` = 'Comercial' (fijo)
5. `doc_causado_por` = f"{CO} - {Usuario_creacion} - {Nro_documento}"

**Fuente de datos:** Archivo ERP Comercial.xlsx
**Campo origen:** `Docto. proveedor` (ej: "FE-00003951")

---

## 📋 TABLA: erp_financiero
**Campos calculados:**
1. `prefijo` = extraer_prefijo(docto_proveedor)
2. `folio` = ultimos_8_sin_ceros(extraer_folio(docto_proveedor))  
3. `clave_erp_financiero` = NIT + PREFIJO + FOLIO - UNIQUE
4. `modulo` = 'Financiero' (fijo)
5. `doc_causado_por` = f"{CO} - {Usuario_creacion} - {Nro_documento}"

**Fuente de datos:** Archivo ERP Financiero.xlsx
**Campo origen:** `Docto. proveedor`

---

## 📋 TABLA: acuses
**Campos calculados:**
1. `clave_acuse` = CUFE (completo 96 chars) - para match con DIAN
2. Campos de tipo acuse (ya vienen en archivo, no se calculan)

**Fuente de datos:** Archivo Acuses.xlsx
**Campo crítico:** CUFE

---

## 📋 TABLA: maestro_dian_vs_erp (consolidada)
**Fuentes de datos:**
1. DIAN (todos los campos base)
2. ERP Comercial/Financiero (módulo, doc_causado_por)
3. ACUSES (estado_aprobacion por CUFE)

**Campos calculados adicionales:**
- `estado_contable` = 'Causada' si tiene módulo, 'No Registrada' si no
- `acuses_recibidos` = calculado según jerarquía de estados
- `tipo_tercero` = heredado de clasificación por NIT

---

## 🔧 FUNCIONES DE EXTRACCIÓN (ya existentes)

```python
def extraer_prefijo(docto: str) -> str:
    """Extrae prefijo de 'FE-00003951' → 'FE'"""
    
def extraer_folio(docto: str) -> str:
    """Extrae folio de 'FE-00003951' → '00003951'"""
    
def ultimos_8_sin_ceros(folio: str) -> str:
    """'00003951' → '3951' (remove leading zeros)"""
    
def crear_clave_factura(nit: str, prefijo: str, folio: str) -> str:
    """Crea 'NIT + PREFIJO + FOLIO' = '8050280413951'"""
```

---

## 🎯 FLUJO REQUERIDO (COMPLETO)

### PASO 1: Cargar archivo DIAN → tabla `dian`
```python
for each row in DIAN.xlsx:
    nit = row['NIT Emisor']
    prefijo = row['Prefijo']
    folio = row['Folio']
    cufe = row['CUFE/CUDE']
    
    clave = crear_clave_factura(nit, prefijo, folio)
    clave_acuse = cufe  # mismo valor
    tipo_tercero = clasificar_tercero(nit, erp_data)  # PROVEEDOR/ACREEDOR/etc
    n_dias = (hoy - fecha_emision).days
    
    INSERT INTO dian (... clave, clave_acuse, tipo_tercero, n_dias ...)
```

### PASO 2: Cargar ERP Comercial → tabla `erp_comercial`
```python
for each row in ERP_Comercial.xlsx:
    nit = row['Proveedor']
    docto = row['Docto. proveedor']  # "FE-00003951"
    
    prefijo = extraer_prefijo(docto)
    folio = ultimos_8_sin_ceros(extraer_folio(docto))
    clave = crear_clave_factura(nit, prefijo, folio)
    doc_causado_por = f"{CO} - {Usuario} - {Nro_doc}"
    
    INSERT INTO erp_comercial (... prefijo, folio, clave, doc_causado_por ...)
```

### PASO 3: Cargar ERP Financiero → tabla `erp_financiero`
Similar a Comercial

### PASO 4: Cargar Acuses → tabla `acuses`
```python
for each row in Acuses.xlsx:
    cufe = row['CUFE']
    clave_acuse = cufe
    
    INSERT INTO acuses (... clave_acuse ...)
```

### PASO 5: Consolidar → tabla `maestro_dian_vs_erp`
```python
# Leer de tablas ya cargadas
dian_data = SELECT * FROM dian
erp_cm_data = SELECT * FROM erp_comercial  
erp_fn_data = SELECT * FROM erp_financiero
acuses_data = SELECT * FROM acuses

# Hacer cruces por clave y CUFE
for each factura in dian_data:
    modulo = buscar_en_erp(factura.clave)
    estado_aprobacion = buscar_en_acuses(factura.cufe)
    
    INSERT INTO maestro_dian_vs_erp (...)
```

---

## ⚠️ PROBLEMA ACTUAL

El código actual hace SOLO el PASO 5:
- ❌ No inserta en tablas dian, erp, acuses
- ✅ Solo lee de archivos y consolida directo a maestro

**Consecuencia:**
- Visor V2 consulta tablas individuales → están vacías → no muestra datos
- Campo "Ver PDF" busca cufe en tabla `dian` → vacía
- Campo "Estado Aprobación" busca en acuses → vacía

---

## ✅ SOLUCIÓN

Modificar `actualizar_maestro()` para:

1. **Insertar en tabla `dian`** con todos sus campos calculados
2. **Insertar en tablas `erp`** con campos calculados  
3. **Insertar en tabla `acuses`** con clave_acuse
4. **Consolidar en `maestro`** (mantener lógica actual)

**Ventaja:** 
- Tablas individuales con datos completos
- Visor V2 funciona consultando tablas individuales
- Maestro con datos consolidados para análisis

**Velocidad:**
- Mantener COPY FROM para todas las tablas (rápido)
- Procesar todo en memoria, luego insertar en bloques
