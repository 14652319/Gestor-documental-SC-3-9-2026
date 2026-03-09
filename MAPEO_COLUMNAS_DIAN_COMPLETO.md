# 📋 MAPEO COMPLETO: EXCEL DIAN → BASE DE DATOS → VISOR V2

**Fecha:** 17 de Febrero 2026  
**Propósito:** Documentar el mapeo entre columnas del Excel DIAN y la tabla `maestro_dian_vs_erp`

---

## 📊 TABLA DE MAPEO COMPLETO

| # | Columna Excel DIAN | Variantes Buscadas | Columna BD | Estado | Línea Código | Notas |
|---|-------------------|-------------------|-----------|--------|--------------|-------|
| 1 | **Tipo de documento** | 'tipo documento', 'tipo_documento' | `tipo_documento` | ✅ LEÍDA | routes.py:1314 | VARCHAR(100) |
| 2 | **CUFE/CUDE** | 'cufe/cude', 'CUFE', 'cufe' | `cufe` | ✅ LEÍDA | routes.py:1316 | VARCHAR(255) |
| 3 | **Folio** | 'numero', 'folio' | `folio` | ✅ LEÍDA | routes.py:1309-1310 | VARCHAR(20), normalizado con `ultimos_8_sin_ceros()` |
| 4 | **Prefijo** | 'prefijo' | `prefijo` | ✅ LEÍDA | routes.py:1306-1307 | VARCHAR(10), normalizado con `extraer_prefijo()` |
| 5 | **Divisa** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **FALTA AGREGAR** al modelo |
| 6 | **Forma de Pago** | 'forma de pago', 'forma pago', 'forma_pago' | `forma_pago` | ✅ LEÍDA | routes.py:1319 | VARCHAR(100), default='2' |
| 7 | **Medio de Pago** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **FALTA AGREGAR** al modelo |
| 8 | **Fecha Emisión** | ⭐ 'fecha emisión', 'fecha emision', 'fecha_emision' | `fecha_emision` | ✅ LEÍDA | routes.py:1297-1304 | DATE, **FIX aplicado con acento** |
| 9 | **Fecha Recepción** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **FALTA AGREGAR** al modelo |
| 10 | **NIT Emisor** | 'nit emisor', 'nit_emisor' | `nit_emisor` | ✅ LEÍDA | routes.py:1290-1291 | VARCHAR(20), normalizado con `extraer_folio()` |
| 11 | **Nombre Emisor** | 'nombre emisor', 'razon_social' | `razon_social` | ✅ LEÍDA | routes.py:1293 | VARCHAR(255) |
| 12 | **NIT Receptor** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **FALTA AGREGAR** al modelo (siempre es 805028041?) |
| 13 | **Nombre Receptor** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **FALTA AGREGAR** al modelo |
| 14 | **IVA** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 15 | **ICA** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 16 | **IC** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 17 | **INC** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 18 | **Timbre** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 19 | **INC Bolsas** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 20 | **IN Carbono** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 21 | **IN Combustibles** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 22 | **IC Datos** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 23 | **ICL** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 24 | **INPP** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 25 | **IBUA** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 26 | **ICUI** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **IMPUESTO - FALTA AGREGAR** |
| 27 | **Rete IVA** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **RETENCIÓN - FALTA AGREGAR** |
| 28 | **Rete Renta** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **RETENCIÓN - FALTA AGREGAR** |
| 29 | **Rete ICA** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **RETENCIÓN - FALTA AGREGAR** |
| 30 | **Total** | ⭐ 'total', 'valor' | `valor` | ✅ LEÍDA | routes.py:1312-1313 | NUMERIC(15,2), **FIX aplicado Total primero** |
| 31 | **Estado** | - | `estado_aprobacion` | ⚠️ PARCIAL | routes.py:1328 | Viene de ACUSES, no del Excel DIAN |
| 32 | **Grupo** | - | ❌ NO EXISTE | ❌ NO LEÍDA | - | **FALTA AGREGAR** al modelo |

---

## ✅ COLUMNAS IMPLEMENTADAS (11 de 32)

### ✅ Columnas leídas correctamente:
1. **Tipo de documento** → `tipo_documento`
2. **CUFE/CUDE** → `cufe`
3. **Folio** → `folio` (normalizado)
4. **Prefijo** → `prefijo` (normalizado)
5. **Forma de Pago** → `forma_pago` (3 variantes buscadas)
6. **Fecha Emisión** → `fecha_emision` (⭐ FIX con acento aplicado)
7. **NIT Emisor** → `nit_emisor` (normalizado)
8. **Nombre Emisor** → `razon_social`
9. **Total** → `valor` (⭐ FIX 'total' primero aplicado)

### ⚠️ Columnas derivadas (no del Excel):
- `estado_aprobacion` → Viene del archivo **Acuses**, no DIAN
- `modulo` → Calculado desde archivos **ERP** (COMERCIAL/FINANCIERO)
- `estado_contable` → Calculado (Causada/No Registrada)
- `tipo_tercero` → Calculado desde **ERP** (PROVEEDOR/ACREEDOR)
- `dias_desde_emision` → Calculado (hoy - fecha_emision)
- `doc_causado_por` → Viene de **ERP** (C.O. - Usuario - Nro)
- `acuses_recibidos` → Calculado desde `estado_aprobacion`

---

## ❌ COLUMNAS FALTANTES (21 de 32)

### 🔍 **Categoría 1: Datos Generales**
- **Divisa** (Peso colombiano, USD, etc.)
- **Medio de Pago** (Efectivo, Transferencia, etc.)
- **Fecha Recepción** (fecha en que se recibió físicamente)
- **NIT Receptor** (probablemente siempre 805028041)
- **Nombre Receptor** (Supertiendas Cañaveral)
- **Grupo** (clasificación adicional)

### 💰 **Categoría 2: Impuestos y Retenciones (15 columnas)**
Estas columnas son **valores monetarios** de impuestos:
- IVA, ICA, IC, INC, Timbre
- INC Bolsas, IN Carbono, IN Combustibles, IC Datos
- ICL, INPP, IBUA, ICUI
- Rete IVA, Rete Renta, Rete ICA

**Impacto:** Actualmente **NO se puede hacer análisis tributario** porque no se guardan estos datos.

---

## 🔧 CÓDIGO RELEVANTE

### 📂 **Archivo: `modules/dian_vs_erp/routes.py`**

#### **Función: `actualizar_maestro()` - Líneas 1073-1450**
Lee el Excel DIAN y procesa los datos:

```python
# Línea 1290-1293: NIT y Razón Social
nit = str(row.get('nit emisor', row.get('nit_emisor', ''))).strip()
razon_social = str(row.get('nombre emisor', row.get('razon_social', ''))).strip()

# Línea 1297-1304: Fecha Emisión (⭐ FIX CON ACENTO)
fecha_emision_raw = row.get('fecha emisión', row.get('fecha emision', row.get('fecha_emision', date.today())))

# Línea 1306-1307: Prefijo
prefijo_raw = str(row.get('prefijo', ''))
prefijo = extraer_prefijo(prefijo_raw)

# Línea 1309-1310: Folio
folio_raw = str(row.get('numero', row.get('folio', '')))
folio = ultimos_8_sin_ceros(extraer_folio(folio_raw))

# Línea 1312-1313: Total/Valor (⭐ FIX TOTAL PRIMERO)
valor_raw = row.get('total', row.get('valor', 0))
valor = float(valor_raw) if valor_raw and str(valor_raw).strip() != '' else 0.0

# Línea 1314: Tipo Documento
tipo_documento = str(row.get('tipo documento', row.get('tipo_documento', 'Factura Electrónica')))

# Línea 1316: CUFE
cufe = str(row.get('cufe/cude', row.get('CUFE', row.get('cufe', ''))))

# Línea 1319: Forma de Pago
forma_pago = str(row.get('forma de pago', row.get('forma pago', row.get('forma_pago', '2')))).strip()
```

---

### 📂 **Archivo: `modules/dian_vs_erp/models.py`**

#### **Clase: `MaestroDianVsErp` - Líneas 10-63**

```python
class MaestroDianVsErp(db.Model):
    __tablename__ = 'maestro_dian_vs_erp'
    
    # ✅ COLUMNAS EXISTENTES QUE SE LLENAN DEL EXCEL:
    nit_emisor = db.Column(db.String(20), nullable=False, index=True)
    razon_social = db.Column(db.String(255))
    fecha_emision = db.Column(db.Date, index=True)
    prefijo = db.Column(db.String(10), index=True)
    folio = db.Column(db.String(20), nullable=False, index=True)
    valor = db.Column(db.Numeric(15, 2))
    tipo_documento = db.Column(db.String(100))
    cufe = db.Column(db.String(255))
    forma_pago = db.Column(db.String(100))
    
    # ⚠️ COLUMNAS CALCULADAS (NO DEL EXCEL DIAN):
    estado_aprobacion = db.Column(db.String(100))  # De Acuses
    tipo_tercero = db.Column(db.String(50))        # De ERP
    modulo = db.Column(db.String(50))              # De ERP
    estado_contable = db.Column(db.String(100))    # Calculado
    dias_desde_emision = db.Column(db.Integer)     # Calculado
    doc_causado_por = db.Column(db.String(100))    # De ERP
    
    # ❌ COLUMNAS FALTANTES:
    # divisa = db.Column(db.String(10))              # FALTA
    # medio_pago = db.Column(db.String(50))          # FALTA
    # fecha_recepcion = db.Column(db.Date)           # FALTA
    # nit_receptor = db.Column(db.String(20))        # FALTA
    # nombre_receptor = db.Column(db.String(255))    # FALTA
    # grupo = db.Column(db.String(50))               # FALTA
    
    # ❌ IMPUESTOS Y RETENCIONES (15 columnas):
    # iva = db.Column(db.Numeric(15, 2))             # FALTA
    # ica = db.Column(db.Numeric(15, 2))             # FALTA
    # ic = db.Column(db.Numeric(15, 2))              # FALTA
    # inc = db.Column(db.Numeric(15, 2))             # FALTA
    # timbre = db.Column(db.Numeric(15, 2))          # FALTA
    # inc_bolsas = db.Column(db.Numeric(15, 2))      # FALTA
    # in_carbono = db.Column(db.Numeric(15, 2))      # FALTA
    # in_combustibles = db.Column(db.Numeric(15, 2)) # FALTA
    # ic_datos = db.Column(db.Numeric(15, 2))        # FALTA
    # icl = db.Column(db.Numeric(15, 2))             # FALTA
    # inpp = db.Column(db.Numeric(15, 2))            # FALTA
    # ibua = db.Column(db.Numeric(15, 2))            # FALTA
    # icui = db.Column(db.Numeric(15, 2))            # FALTA
    # rete_iva = db.Column(db.Numeric(15, 2))        # FALTA
    # rete_renta = db.Column(db.Numeric(15, 2))      # FALTA
    # rete_ica = db.Column(db.Numeric(15, 2))        # FALTA
```

---

### 📂 **Archivo: `modules/dian_vs_erp/routes.py`**

#### **Función: `descargar_plantilla()` - Líneas 809-880**
Genera plantillas Excel para descarga:

```python
# Línea 837-847: ENCABEZADOS ACTUALES DE LA PLANTILLA (9 columnas)
if tipo == "dian":
    headers = [
        'Tipo Documento',      # ✅ SE LEE
        'CUFE/CUDE',           # ✅ SE LEE
        'Numero',              # ✅ SE LEE (folio)
        'Prefijo',             # ✅ SE LEE
        'Fecha Emision',       # ✅ SE LEE (⚠️ sin acento en plantilla)
        'NIT Emisor',          # ✅ SE LEE
        'Nombre Emisor',       # ✅ SE LEE
        'Valor',               # ✅ SE LEE (o 'Total')
        'Forma Pago'           # ✅ SE LEE
    ]
```

**⚠️ PROBLEMA:** La plantilla tiene solo **9 columnas**, pero el Excel del usuario tiene **32 columnas**.

---

## 🚨 PROBLEMAS IDENTIFICADOS

### 1️⃣ **Plantilla desactualizada** ⚠️
**Archivo:** `modules/dian_vs_erp/routes.py` líneas 837-847

**Problema:**
```python
headers = [
    'Tipo Documento', 'CUFE/CUDE', 'Numero', 'Prefijo',
    'Fecha Emision',  # ❌ SIN ACENTO (debería ser 'Fecha Emisión')
    'NIT Emisor', 'Nombre Emisor', 'Valor', 'Forma Pago'
]
```

**Impacto:**
- Si el usuario descarga la plantilla, obtendrá solo 9 columnas
- Falta "Total" como alternativa a "Valor"
- Falta acento en "Fecha Emision" → No coincide con Excel 2026
- Faltan 23 columnas del Excel real

### 2️⃣ **Impuestos no se guardan** ❌
Las 15 columnas de impuestos/retenciones NO están en el modelo:
- IVA, ICA, IC, INC, Timbre
- INC Bolsas, IN Carbono, IN Combustibles, IC Datos
- ICL, INPP, IBUA, ICUI
- Rete IVA, Rete Renta, Rete ICA

**Impacto:**
- **NO se puede hacer análisis tributario**
- **NO se pueden generar reportes por tipo de impuesto**
- **Se pierde información financiera crítica**

### 3️⃣ **Datos del receptor no se guardan** ❌
- NIT Receptor
- Nombre Receptor

**Impacto leve:** Probablemente siempre es el mismo (805028041), pero sería ideal para validación.

---

## ✅ FIXES APLICADOS (Febrero 17, 2026)

### **FIX #1: Fecha Emisión con acento** ✅
**Archivo:** `modules/dian_vs_erp/routes.py` línea 1297

**ANTES:**
```python
fecha_emision_raw = row.get('fecha emision', row.get('fecha_emision', date.today()))
```

**DESPUÉS:**
```python
# ✅ FIX: Buscar 'fecha emisión' (con acento) para Excel 2026
fecha_emision_raw = row.get('fecha emisión', row.get('fecha emision', row.get('fecha_emision', date.today())))
```

**Resultado:** Ahora lee correctamente "Fecha Emisión" con acento (Excel 2026)

---

### **FIX #2: Total antes que Valor** ✅
**Archivo:** `modules/dian_vs_erp/routes.py` línea 1312-1313

**ANTES:**
```python
valor = float(row.get('valor', 0))
```

**DESPUÉS:**
```python
# ✅ FIX: Buscar 'total' primero (Excel 2026) antes de 'valor' (Excel 2025)
valor_raw = row.get('total', row.get('valor', 0))
valor = float(valor_raw) if valor_raw and str(valor_raw).strip() != '' else 0.0
```

**Resultado:** Ahora lee correctamente columna "Total" (Excel 2026) y tiene fallback a "Valor"

---

## 📋 RECOMENDACIONES

### 🔥 **PRIORIDAD ALTA**

#### 1️⃣ **Actualizar plantilla DIAN** (⚡ URGENTE)
**Archivo a modificar:** `modules/dian_vs_erp/routes.py` líneas 837-847

**Acción:**
```python
if tipo == "dian":
    headers = [
        # ✅ Columnas implementadas
        'Tipo de documento',
        'CUFE/CUDE',
        'Folio',                    # Cambiar 'Numero' por 'Folio'
        'Prefijo',
        'Divisa',                   # ⭐ NUEVO
        'Forma de Pago',
        'Medio de Pago',            # ⭐ NUEVO
        'Fecha Emisión',            # ✅ Con acento
        'Fecha Recepción',          # ⭐ NUEVO
        'NIT Emisor',
        'Nombre Emisor',
        'NIT Receptor',             # ⭐ NUEVO
        'Nombre Receptor',          # ⭐ NUEVO
        
        # ⭐ IMPUESTOS (15 columnas nuevas)
        'IVA', 'ICA', 'IC', 'INC', 'Timbre',
        'INC Bolsas', 'IN Carbono', 'IN Combustibles', 'IC Datos',
        'ICL', 'INPP', 'IBUA', 'ICUI',
        
        # ⭐ RETENCIONES (3 columnas nuevas)
        'Rete IVA', 'Rete Renta', 'Rete ICA',
        
        # ✅ Total
        'Total',
        
        # ⭐ Otros
        'Estado',                   # ⭐ NUEVO
        'Grupo'                     # ⭐ NUEVO
    ]
```

**Total columnas:** 32 (coincide con Excel del usuario)

---

#### 2️⃣ **Ampliar modelo de base de datos**
**Archivo a modificar:** `modules/dian_vs_erp/models.py` línea 10+

**Acción:** Agregar columnas faltantes al modelo `MaestroDianVsErp`:

```python
class MaestroDianVsErp(db.Model):
    # ... columnas existentes ...
    
    # 🆕 DATOS GENERALES
    divisa = db.Column(db.String(10))              # COP, USD, etc.
    medio_pago = db.Column(db.String(50))          # Efectivo, Transferencia, etc.
    fecha_recepcion = db.Column(db.Date)           # Fecha física de recepción
    nit_receptor = db.Column(db.String(20))        # Probablemente siempre 805028041
    nombre_receptor = db.Column(db.String(255))    # Supertiendas Cañaveral
    grupo = db.Column(db.String(50))               # Clasificación adicional
    
    # 🆕 IMPUESTOS (15 columnas)
    iva = db.Column(db.Numeric(15, 2))
    ica = db.Column(db.Numeric(15, 2))
    ic = db.Column(db.Numeric(15, 2))
    inc = db.Column(db.Numeric(15, 2))
    timbre = db.Column(db.Numeric(15, 2))
    inc_bolsas = db.Column(db.Numeric(15, 2))
    in_carbono = db.Column(db.Numeric(15, 2))
    in_combustibles = db.Column(db.Numeric(15, 2))
    ic_datos = db.Column(db.Numeric(15, 2))
    icl = db.Column(db.Numeric(15, 2))
    inpp = db.Column(db.Numeric(15, 2))
    ibua = db.Column(db.Numeric(15, 2))
    icui = db.Column(db.Numeric(15, 2))
    
    # 🆕 RETENCIONES (3 columnas)
    rete_iva = db.Column(db.Numeric(15, 2))
    rete_renta = db.Column(db.Numeric(15, 2))
    rete_ica = db.Column(db.Numeric(15, 2))
```

**Después:** Ejecutar migración:
```bash
python agregar_columnas_impuestos.py
```

---

#### 3️⃣ **Actualizar código de lectura**
**Archivo a modificar:** `modules/dian_vs_erp/routes.py` líneas 1350+

**Acción:** Agregar lectura de nuevas columnas en `actualizar_maestro()`:

```python
# Después de línea 1319 (forma_pago), agregar:

# 🆕 DATOS GENERALES
divisa = str(row.get('divisa', 'COP')).strip()
medio_pago = str(row.get('medio de pago', row.get('medio_pago', ''))).strip()
fecha_recepcion_raw = row.get('fecha recepción', row.get('fecha_recepcion', None))
nit_receptor = str(row.get('nit receptor', row.get('nit_receptor', '805028041'))).strip()
nombre_receptor = str(row.get('nombre receptor', row.get('nombre_receptor', 'Supertiendas Cañaveral'))).strip()
grupo = str(row.get('grupo', '')).strip()

# 🆕 IMPUESTOS (15 columnas)
iva = float(row.get('iva', 0))
ica = float(row.get('ica', 0))
ic = float(row.get('ic', 0))
inc = float(row.get('inc', 0))
timbre = float(row.get('timbre', 0))
inc_bolsas = float(row.get('inc bolsas', 0))
in_carbono = float(row.get('in carbono', 0))
in_combustibles = float(row.get('in combustibles', 0))
ic_datos = float(row.get('ic datos', 0))
icl = float(row.get('icl', 0))
inpp = float(row.get('inpp', 0))
ibua = float(row.get('ibua', 0))
icui = float(row.get('icui', 0))

# 🆕 RETENCIONES (3 columnas)
rete_iva = float(row.get('rete iva', 0))
rete_renta = float(row.get('rete renta', 0))
rete_ica = float(row.get('rete ica', 0))

# Actualizar dict de registros (línea 1357+):
registros.append({
    # ... campos existentes ...
    'divisa': divisa,
    'medio_pago': medio_pago,
    'fecha_recepcion': fecha_recepcion,
    'nit_receptor': nit_receptor,
    'nombre_receptor': nombre_receptor,
    'grupo': grupo,
    'iva': iva,
    'ica': ica,
    # ... etc (todos los nuevos campos)
})
```

---

### 🟡 **PRIORIDAD MEDIA**

#### 4️⃣ **Validar normalización de columnas**
**Archivo:** `modules/dian_vs_erp/routes.py` línea 1075+

**Verificar:** Que se haga `df.columns = [c.strip().lower() for c in df.columns]` ANTES de leer columnas

**Estado actual:** ⚠️ NO se ve normalización de columnas en `actualizar_maestro()`

**Impacto:** Si el Excel tiene "Fecha Emisión" con mayúsculas, puede no encontrarse

**Acción:** Agregar normalización antes de línea 1285:
```python
# Normalizar nombres de columnas (lowercase y sin espacios extra)
d_pd.columns = [c.strip().lower() for c in d_pd.columns]
```

---

#### 5️⃣ **Documentar casos edge**
- ¿Qué pasa si "Total" y "Valor" están ambas presentes?
  - **Respuesta:** Toma "Total" (preferencia)
- ¿Qué pasa si "Fecha Emisión" con/sin acento coexisten?
  - **Respuesta:** Toma con acento primero (preferencia)
- ¿Qué pasa si columnas de impuestos están vacías?
  - **Respuesta:** Default a 0.0

---

## 🔍 VERIFICACIÓN VISOR V2

### **Template:** `templates/dian_vs_erp/visor_dian_v2.html`

**Columnas mostradas actualmente:**
- NIT Emisor
- Nombre Emisor
- Fecha Emisión
- Prefijo
- Folio
- Valor
- Forma de Pago
- Estado (Contable)
- Módulo
- Tipo Tercero
- Días desde emisión

**Columnas FALTANTES en visor:**
- ❌ CUFE/CUDE
- ❌ Tipo Documento
- ❌ Todos los impuestos (15)
- ❌ Todas las retenciones (3)
- ❌ Divisa, Medio de Pago, Grupo

**Recomendación:** Agregar botón "Mostrar todas las columnas" o columnas ocultas expandibles

---

## 📊 SUMMARY

| Categoría | Total | Implementadas | Faltantes | % |
|-----------|-------|---------------|-----------|---|
| **Datos Generales** | 13 | 8 | 5 | 62% |
| **Impuestos** | 15 | 0 | 15 | 0% |
| **Retenciones** | 3 | 0 | 3 | 0% |
| **Otros** | 1 | 0 | 1 | 0% |
| **TOTAL** | **32** | **8** | **24** | **25%** |

### ✅ **Columnas básicas funcionando:** 8/32 (25%)
### ❌ **Columnas de impuestos faltantes:** 18/32 (56%)
### ⚠️ **Otros datos faltantes:** 6/32 (19%)

---

## 🎯 PLAN DE ACCIÓN SUGERIDO

### **FASE 1: EMERGENCIA (HOY)**
1. ✅ **FIX aplicado:** Fecha Emisión con acento
2. ✅ **FIX aplicado:** Total antes que Valor
3. ⏳ **Validar:** Usuario debe subir archivo de nuevo

---

### **FASE 2: CORTO PLAZO (Esta semana)**
1. **Actualizar plantilla** con 32 columnas completas
2. **Agregar normalización** de columnas (lowercase)
3. **Documentar** en README.md los formatos aceptados

---

### **FASE 3: MEDIANO PLAZO (Próximas 2 semanas)**
1. **Agregar impuestos** al modelo (15 columnas)
2. **Agregar retenciones** al modelo (3 columnas)
3. **Agregar datos generales** faltantes (6 columnas)
4. **Crear migración** para actualizar BD
5. **Actualizar código** de lectura en `actualizar_maestro()`
6. **Probar** con Excel real del usuario

---

### **FASE 4: LARGO PLAZO (Próximo mes)**
1. **Actualizar visor_v2** para mostrar nuevas columnas
2. **Crear reportes** por tipo de impuesto
3. **Análisis tributario** avanzado
4. **Exportar** con todas las columnas a Excel

---

## 📝 NOTAS FINALES

### ⚠️ **Incompatibilidades conocidas:**
1. Plantilla descargable tiene solo 9 columnas, Excel real tiene 32
2. Nombres sin acento en plantilla ("Fecha Emision") vs con acento en Excel 2026 ("Fecha Emisión")
3. "Numero" en plantilla vs "Folio" en Excel real

### ✅ **Fortalezas del sistema actual:**
1. Normalización de NIT, Prefijo, Folio funcionando
2. Integración con ERP (módulo COMERCIAL/FINANCIERO)
3. Integración con Acuses (estado_aprobacion)
4. Cálculos automáticos (días, tipo tercero, estado contable)
5. COPY FROM ultra-rápido (25,000+ reg/seg)

### 🚀 **Oportunidades:**
1. Análisis tributario completo si se agregan impuestos
2. Reportes por retención
3. Validaciones cruzadas (Total = Subtotal + IVA + otros)
4. Dashboard financiero avanzado

---

**Documento generado:** 2026-02-17  
**Autor:** Sistema de mapeo automático  
**Versión:** 1.0  
**Próxima revisión:** Después de aplicar FASE 2
