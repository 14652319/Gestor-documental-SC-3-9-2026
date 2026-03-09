# 📚 ESTRUCTURA DE VALIDACIÓN DE DUPLICIDAD - MÓDULO DIAN VS ERP

**Fecha:** 19 de Febrero de 2026  
**Documentación técnica completa del sistema de validación de duplicados**

---

## 1️⃣ CARPETAS DE ALMACENAMIENTO DE ARCHIVOS EXCEL

Los archivos se guardan en las siguientes carpetas:

```
📁 GESTOR_DOCUMENTAL/
│
├── 📂 uploads/
│   │
│   ├── 📂 dian/           ⭐ ARCHIVO MAESTRO (OBLIGATORIO)
│   │   └── Dian.xlsx
│   │
│   ├── 📂 erp_fn/         (ERP Financiero - Opcional)
│   │   └── ERP_Financiero.xlsx
│   │
│   ├── 📂 erp_cm/         (ERP Comercial - Opcional)
│   │   └── ERP_Comercial.xlsx
│   │
│   ├── 📂 acuses/         (Acuses DIAN - Opcional)
│   │   └── acuses.xlsx
│   │
│   └── 📂 rg_erp_er/      (Errores Registro ERP - Opcional)
│       └── errores.xlsx
```

### 📍 Ubicación Exacta
```python
# Definido en routes.py líneas 52-61
BASE_DIR = Path(__file__).parent.parent.parent
UPLOADS = {
    "dian": BASE_DIR / "uploads" / "dian",
    "erp_fn": BASE_DIR / "uploads" / "erp_fn", 
    "erp_cm": BASE_DIR / "uploads" / "erp_cm",
    "acuses": BASE_DIR / "uploads" / "acuses",
    "errores": BASE_DIR / "uploads" / "rg_erp_er",
}
```

---

## 2️⃣ ¿POR QUÉ NECESITA EL ARCHIVO DIAN OBLIGATORIAMENTE?

### 🎯 RAZÓN TÉCNICA

El sistema está diseñado con **DIAN como archivo MAESTRO**. La lógica es:

```
📊 DIAN (Fuente oficial gobierno)
   ↓
   ├── ¿Está en ERP? → SÍ = "Registrada en sistema"
   │                  → NO = "Falta registrar"
   │
   └── ¿Tiene acuses? → SÍ = Estado real de DIAN
                       → NO = "Pendiente"
```

### 📍 Validación en el código

**Archivo:** `routes.py` líneas 1125-1130

```python
def actualizar_maestro() -> str:
    # 1️⃣ CARGAR ARCHIVO DIAN (OBLIGATORIO)
    print("\n📂 Buscando archivo DIAN...")
    f_dian = latest_csv(UPLOADS["dian"])
    if not f_dian:
        print("❌ No hay archivos DIAN")
        return "⚠️ No hay archivos DIAN. Sube un Excel/CSV de DIAN para procesar."
    
    print(f"✅ Archivo encontrado: {os.path.basename(f_dian)}")
```

### ⚠️ MENSAJE QUE VISTE

El modal que apareció:

```
127.0.0.1:8099 dice
⚠️ No hay archivos DIAN. Sube un Excel/CSV de DIAN para procesar.
[Aceptar]
```

Este mensaje se genera cuando:
1. Intentas procesar SOLO acuses
2. La carpeta `uploads/dian/` está vacía
3. El sistema detecta que falta el archivo maestro

### ✅ SOLUCIÓN

**DEBES subir siempre:** DIAN + Acuses (u otros)

**No puedes subir:** Solo Acuses, solo ERP FN, solo ERP CM

---

## 3️⃣ SISTEMA DE VALIDACIÓN DE DUPLICIDAD

### 🔑 CONCEPTO DE "CLAVE ÚNICA"

Cada tabla tiene una **clave única** que identifica una factura sin ambigüedad:

```
CLAVE = NIT_EMISOR + PREFIJO + FOLIO_8
```

Donde:
- **NIT_EMISOR**: Solo dígitos (sin puntos, guiones)
- **PREFIJO**: Solo letras (sin números)
- **FOLIO_8**: Últimos 8 dígitos SIN ceros a la izquierda

### 📝 EJEMPLO PRÁCTICO

```
Factura original: 805028041-FE-00000123
                  └─ NIT ──┘ └PREFIJO┘ └─ Folio ──┘

Clave generada: 805028041FE123
                └─ NIT ──┘└P┘└F8┘
```

### 🔧 FUNCIÓN DE CREACIÓN DE CLAVE

**Archivo:** `routes.py` líneas 1094-1099

```python
def crear_clave_factura(nit: str, prefijo: str, folio: str) -> str:
    """Crea clave única: NIT + PREFIJO + FOLIO_8"""
    nit_limpio = extraer_folio(str(nit))           # Solo dígitos
    prefijo_limpio = extraer_prefijo(str(prefijo))  # Solo letras
    folio_8 = ultimos_8_sin_ceros(extraer_folio(str(folio)))  # Últimos 8 sin ceros
    return f"{nit_limpio}{prefijo_limpio}{folio_8}"
```

---

## 4️⃣ VALIDACIÓN DE DUPLICIDAD POR TABLA

### 📊 **TABLA: DIAN**

**Modelo:** `modules/dian_vs_erp/models.py` línea 409

```python
class Dian(db.Model):
    __tablename__ = 'dian'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... otros campos ...
    clave = db.Column(db.String(100), unique=True)  # ⭐ UNIQUE CONSTRAINT
```

**Validación:**
- ✅ Constraint UNIQUE en columna `clave`
- ✅ PostgreSQL rechaza automáticamente duplicados
- ✅ Clave = NIT + PREFIJO + FOLIO_8

**Ejemplo de clave:** `805028041FE123`

---

### 📊 **TABLA: ERP FINANCIERO**

**Modelo:** `modules/dian_vs_erp/models.py` línea 459

```python
class ErpFinanciero(db.Model):
    __tablename__ = 'erp_financiero'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... otros campos ...
    clave_erp_financiero = db.Column(db.String(100), unique=True)  # ⭐ UNIQUE
```

**Validación:**
- ✅ Constraint UNIQUE en columna `clave_erp_financiero`
- ✅ Previene duplicados de facturas financieras
- ✅ Clave = NIT_PROVEEDOR + PREFIJO + FOLIO_8

---

### 📊 **TABLA: ERP COMERCIAL**

**Modelo:** `modules/dian_vs_erp/models.py` línea 435

```python
class ErpComercial(db.Model):
    __tablename__ = 'erp_comercial'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... otros campos ...
    clave_erp_comercial = db.Column(db.String(100), unique=True)  # ⭐ UNIQUE
```

**Validación:**
- ✅ Constraint UNIQUE en columna `clave_erp_comercial`
- ✅ Previene duplicados de facturas comerciales
- ✅ Clave = NIT_PROVEEDOR + PREFIJO + FOLIO_8

---

### 📊 **TABLA: ACUSES**

**Modelo:** `modules/dian_vs_erp/models.py` línea 483

```python
class Acuses(db.Model):
    __tablename__ = 'acuses'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... otros campos ...
    clave_acuse = db.Column(db.String(255), index=True)  # ⚠️ NO UNIQUE
```

**Validación:**
- ⚠️ **NO tiene constraint UNIQUE**
- ❓ **¿Por qué?** Un documento puede tener múltiples acuses:
  - Acuse Recibido
  - Acuse Bien/Servicio
  - Aceptación Expresa
  - Aceptación Tácita
  - Rechazada
- ✅ Se usa índice para búsquedas rápidas
- ✅ Se mantiene el acuse con mayor jerarquía

**Sistema de jerarquía de acuses:**

```python
# routes.py líneas 1018-1032
def obtener_jerarquia_aceptacion(estado: str) -> int:
    jerarquias = {
        'Pendiente': 1,
        'Acuse Recibido': 2,
        'Acuse Bien/Servicio': 3,
        'Rechazada': 4,
        'Aceptación Expresa': 5,      # ⭐ MAYOR
        'Aceptación Tácita': 6          # ⭐ MÁXIMO
    }
    return jerarquias.get(estado, 1)
```

Si hay 3 acuses para la misma factura:
- Acuse Recibido (2)
- Rechazada (4)
- Aceptación Expresa (5) ← **Se queda este**

---

### 📊 **TABLA: MAESTRO_DIAN_VS_ERP**

**Modelo:** `modules/dian_vs_erp/models.py` línea 11

```python
class MaestroDianVsErp(db.Model):
    __tablename__ = 'maestro_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    nit_emisor = db.Column(db.String(20), nullable=False, index=True)
    prefijo = db.Column(db.String(10), index=True)
    folio = db.Column(db.String(20), nullable=False, index=True)
    # ⚠️ NO tiene UNIQUE constraint en (nit, prefijo, folio)
```

**Validación:**
- ⚠️ **Permite duplicados temporalmente durante INSERT**
- ✅ **Limpia duplicados con DELETE después de INSERT**

**Lógica en routes.py líneas 1784-1791:**

```python
# INSERT SIMPLE (permite duplicados temporalmente)
INSERT INTO maestro_dian_vs_erp (nit_emisor, prefijo, folio, ...)
SELECT nit_emisor, prefijo, folio, ...
FROM temp_maestro_nuevos;

# DELETE de duplicados (mantiene solo el más reciente)
DELETE FROM maestro_dian_vs_erp a 
USING maestro_dian_vs_erp b
WHERE a.id < b.id                    -- ⭐ El ID más bajo (viejo) se elimina
  AND a.nit_emisor = b.nit_emisor    -- Mismo NIT
  AND a.prefijo = b.prefijo          -- Mismo prefijo
  AND a.folio = b.folio              -- Mismo folio
```

**Ejemplo:**

```
ANTES DEL DELETE:
ID | NIT        | PREFIJO | FOLIO
---+------------+---------+-------
10 | 805028041  | FE      | 123     ← Viejo
15 | 805028041  | FE      | 123     ← Nuevo (mayor ID)
20 | 900123456  | NC      | 456

DESPUÉS DEL DELETE:
ID | NIT        | PREFIJO | FOLIO
---+------------+---------+-------
15 | 805028041  | FE      | 123     ✅ Quedó el nuevo
20 | 900123456  | NC      | 456
```

---

## 5️⃣ FLUJO COMPLETO DE PROCESAMIENTO CON VALIDACIÓN DE DUPLICADOS

### 📋 PASO A PASO

```
1️⃣ SUBIDA DE ARCHIVOS
   Usuario sube: [DIAN.xlsx] + [Acuses.xlsx] + [ERP_FN.xlsx] + [ERP_CM.xlsx]
   ↓
   Archivos guardados en: uploads/dian/, uploads/acuses/, etc.

2️⃣ VALIDACIÓN DE ARCHIVO MAESTRO
   ✅ ¿Existe uploads/dian/Dian.xlsx?
      → SÍ: Continuar
      → NO: ❌ Mostrar modal "No hay archivos DIAN"

3️⃣ LECTURA Y CONVERSIÓN
   Excel → Polars DataFrame → CSV temporal
   ↓
   Normalización de columnas (quitar acentos, espacios)

4️⃣ CREACIÓN DE CLAVES ÚNICAS
   Para cada factura en DIAN:
      clave = crear_clave_factura(nit, prefijo, folio)
      Ejemplo: "805028041FE123"
   
   Para cada factura en ERP FN:
      clave_erp_financiero = crear_clave_factura(nit, prefijo, folio)
   
   Para cada factura en ERP CM:
      clave_erp_comercial = crear_clave_factura(nit, prefijo, folio)

5️⃣ INSERCIÓN EN TABLAS INDIVIDUALES
   
   DIAN:
   INSERT INTO dian (clave, ...)
   VALUES ('805028041FE123', ...)
   → Si ya existe: ERROR → Se ignora (constraint UNIQUE)
   
   ERP FINANCIERO:
   INSERT INTO erp_financiero (clave_erp_financiero, ...)
   VALUES ('805028041FE123', ...)
   → Si ya existe: ERROR → Se ignora
   
   ERP COMERCIAL:
   INSERT INTO erp_comercial (clave_erp_comercial, ...)
   VALUES ('900123456NC456', ...)
   → Si ya existe: ERROR → Se ignora
   
   ACUSES:
   INSERT INTO acuses (clave_acuse, estado_docto, ...)
   VALUES ('CUFE12345...', 'Aceptación Expresa', ...)
   → Permite múltiples: ✅ (NO unique)

6️⃣ CONSTRUCCIÓN DEL MAESTRO CONSOLIDADO
   
   A. Crear tabla temporal temp_maestro_nuevos
   
   B. Cruzar datos:
      DIAN (maestro)
      LEFT JOIN ERP_FN (por NIT+PREFIJO+FOLIO)
      LEFT JOIN ERP_CM (por NIT+PREFIJO+FOLIO)
      LEFT JOIN ACUSES (por CUFE)
   
   C. Insertar TODO en maestro_dian_vs_erp (permite duplicados temporalmente)
   
   D. DELETE de duplicados:
      Mantener solo el registro con ID mayor (más reciente)

7️⃣ RESULTADO FINAL
   
   ✅ Maestro consolidado sin duplicados
   ✅ Estado de aprobación actualizado desde acuses
   ✅ Estado contable actualizado desde ERP
   ✅ Tipo de tercero clasificado (Proveedor/Acreedor/Ambos/No Registrado)
```

---

## 6️⃣ EJEMPLOS PRÁCTICOS DE VALIDACIÓN

### 📌 EJEMPLO 1: Factura duplicada en DIAN

**Carga inicial:**
```
DIAN.xlsx:
NIT       | Prefijo | Folio    | Valor
805028041 | FE      | 00000123 | 1000000
```

**Segunda carga (mismo archivo):**
```
DIAN.xlsx:
NIT       | Prefijo | Folio    | Valor
805028041 | FE      | 00000123 | 1000000  ← Duplicado
```

**Resultado:**
```sql
-- Primera carga
INSERT INTO dian (clave, ...) VALUES ('805028041FE123', ...)  -- ✅ OK

-- Segunda carga
INSERT INTO dian (clave, ...) VALUES ('805028041FE123', ...)  -- ❌ ERROR
-- ERROR: duplicate key value violates unique constraint "dian_clave_key"
```

**Comportamiento:** El duplicado se ignora, mantiene el original

---

### 📌 EJEMPLO 2: Factura con múltiples acuses

**Acuses.xlsx:**
```
Factura   | Estado Docto.        | Fecha
FE123     | Acuse Recibido       | 2026-02-01
FE123     | Rechazada            | 2026-02-05
FE123     | Aceptación Expresa    | 2026-02-10  ← Mayor jerarquía
```

**Resultado en maestro:**
```sql
SELECT prefijo, folio, estado_aprobacion
FROM maestro_dian_vs_erp
WHERE prefijo = 'FE' AND folio = '123';

-- Resultado:
-- estado_aprobacion = 'Aceptación Expresa'  ✅ (Jerarquía 5)
```

---

### 📌 EJEMPLO 3: Factura en DIAN y ERP

**DIAN.xlsx:**
```
NIT       | Prefijo | Folio | Valor
805028041 | FE      | 123   | 1000000
```

**ERP_Financiero.xlsx:**
```
Proveedor | Docto. proveedor | Clase
805028041 | FE-123           | Factura de servicio compra
```

**Resultado en maestro:**
```sql
SELECT nit_emisor, prefijo, folio, modulo, estado_contable
FROM maestro_dian_vs_erp
WHERE nit_emisor = '805028041' AND prefijo = 'FE' AND folio = '123';

-- Resultado:
-- modulo = 'FINANCIERO'  ✅ (Encontrado en ERP FN)
-- estado_contable = 'Causada'  ✅ (Validado contra tabla facturas_recibidas)
```

---

## 7️⃣ RESUMEN DE CONSTRAINTS Y VALIDACIONES

| Tabla               | Columna Clave         | Constraint | Permite Duplicados | Validación                          |
|---------------------|-----------------------|------------|--------------------|-------------------------------------|
| **dian**            | `clave`               | UNIQUE ✅  | ❌ NO             | PostgreSQL rechaza automáticamente  |
| **erp_financiero**  | `clave_erp_financiero`| UNIQUE ✅  | ❌ NO             | PostgreSQL rechaza automáticamente  |
| **erp_comercial**   | `clave_erp_comercial` | UNIQUE ✅  | ❌ NO             | PostgreSQL rechaza automáticamente  |
| **acuses**          | `clave_acuse`         | INDEX ⚠️   | ✅ SÍ             | Se mantiene el de mayor jerarquía   |
| **maestro_dian_vs_erp** | `nit+prefijo+folio` | NINGUNO ⚠️ | ✅ SI (temporal)  | DELETE manual del ID menor          |

---

## 8️⃣ VERIFICACIÓN DE DUPLICADOS EN LA BASE DE DATOS

### 🔍 SQL para verificar duplicados en DIAN

```sql
-- Buscar duplicados en tabla DIAN
SELECT clave, COUNT(*) as cantidad
FROM dian
GROUP BY clave
HAVING COUNT(*) > 1;

-- Resultado esperado: 0 filas (UNIQUE constraint previene duplicados)
```

### 🔍 SQL para verificar duplicados en ERP FINANCIERO

```sql
-- Buscar duplicados en ERP Financiero
SELECT clave_erp_financiero, COUNT(*) as cantidad
FROM erp_financiero
GROUP BY clave_erp_financiero
HAVING COUNT(*) > 1;

-- Resultado esperado: 0 filas
```

### 🔍 SQL para verificar duplicados en ERP COMERCIAL

```sql
-- Buscar duplicados en ERP Comercial
SELECT clave_erp_comercial, COUNT(*) as cantidad
FROM erp_comercial
GROUP BY clave_erp_comercial
HAVING COUNT(*) > 1;

-- Resultado esperado: 0 filas
```

### 🔍 SQL para verificar duplicados en MAESTRO

```sql
-- Buscar duplicados en MAESTRO (no debería haber después del DELETE)
SELECT nit_emisor, prefijo, folio, COUNT(*) as cantidad
FROM maestro_dian_vs_erp
GROUP BY nit_emisor, prefijo, folio
HAVING COUNT(*) > 1;

-- Resultado esperado: 0 filas (DELETE limpia duplicados)
```

### 🔍 SQL para ver múltiples acuses de una factura

```sql
-- Ver todos los acuses de una factura específica
SELECT factura, estado_docto, fecha, cufe
FROM acuses
WHERE factura = 'FE123'
ORDER BY fecha DESC;

-- Puede retornar múltiples filas (esto es correcto)
```

---

## 9️⃣ PREGUNTAS FRECUENTES

### ❓ ¿Por qué no puedo procesar solo ACUSES?

**Respuesta:** El sistema requiere DIAN como archivo maestro porque:
1. **DIAN** es la fuente oficial de facturas electrónicas
2. **ACUSES** son complementarios (estados de aceptación)
3. La lógica es: "Para cada factura en DIAN, buscar su acuse"
4. No tiene sentido buscar acuses sin tener las facturas DIAN

### ❓ ¿Qué pasa si subo DIAN sin ACUSES?

**Respuesta:** ✅ Funciona perfectamente
- El campo `estado_aprobacion` quedará como "No Registra"
- El resto del procesamiento continúa normalmente
- Puedes subir ACUSES después y reprocesar

### ❓ ¿El sistema elimina datos anteriores al subir nuevos archivos?

**Respuesta:** ⚠️ Depende de la tabla:
- **DIAN, ERP_FN, ERP_CM**: ❌ NO elimina (constraint UNIQUE previene duplicados)
- **ACUSES**: ❌ NO elimina (permite múltiples)
- **MAESTRO**: ✅ Elimina duplicados después de INSERT (DELETE por ID)

### ❓ ¿Cómo evito duplicados al cargar el mismo archivo varias veces?

**Respuesta:** El sistema ya lo previene automáticamente:
1. **Tablas individuales**: Constraint UNIQUE rechaza duplicados
2. **Maestro**: DELETE elimina duplicados manteniendo el más reciente

### ❓ ¿Qué pasa si cambio el valor de una factura y la vuelvo a cargar?

**Respuesta:**
- Si cambias el **valor** pero mantienes **NIT+PREFIJO+FOLIO**: 
  - Tablas DIAN/ERP: ❌ Se rechaza (constraint UNIQUE)
  - Maestro: ✅ Se actualiza el más reciente
- Recomendación: Usar la opción "Eliminar datos por rango" si necesitas actualizar valores

---

## 🔟 DOCUMENTOS RELACIONADOS

- **PROBLEMA_ESTADO_APROBACION_FEB18.md** - Diagnóstico del problema original
- **ANALISIS_FLUJO_ACUSES_FEB18.md** - Análisis del flujo completo de acuses
- **VALIDACION_CUFE_FEB18.md** - Validación de CUFEs entre DIAN y Acuses
- **verificar_match_cufe.py** - Script para validar coincidencias

---

## ✅ CONCLUSIÓN

El sistema tiene una estructura sólida de validación de duplicidad:

1. **Tablas individuales**: Constraints UNIQUE en PostgreSQL
2. **Clave única**: NIT + PREFIJO + FOLIO_8 normalizado
3. **Maestro**: Limpieza automática de duplicados
4. **DIAN obligatorio**: Es el archivo maestro del sistema
5. **Acuses múltiples**: Permitidos, se mantiene el de mayor jerarquía

**Para tu caso:**
- ✅ Subir DIAN + Acuses juntos
- ✅ El sistema validará y eliminará duplicados automáticamente
- ✅ El campo `estado_aprobacion` se llenará correctamente

---

**Documentado por:** GitHub Copilot  
**Fecha:** 19 de Febrero de 2026  
**Versión:** 1.0
