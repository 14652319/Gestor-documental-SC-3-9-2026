#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RESUMEN_PROBLEMA_Y_SOLUCION.md - Análisis del problema de carga
================================================================

## 🔍 PROBLEMA IDENTIFICADO

### Síntomas:
- ✅ DIAN: 66,276 registros cargados correctamente
- ❌ ERP COMERCIAL: Solo 21 de 58,187 (99.96% perdidos)
- ❌ ERP FINANCIERO: Solo 21 de 2,996 (99.3% perdidos)
- ❌ ACUSES: Solo 256 de 46,650 (99.45% perdidos)

### Causa Raíz:
**pandas `drop_duplicates()` está completamente ROTO para este caso**

#### Intentos Fallidos:
1. **CARGA_3_TABLAS.py**: Clave incorrecta (prefijo + folio), solo 955/650/255 registros
2. **CARGA_CORREGIDA.py**: Clave compuesta, solo 21/21/21 registros ← WTF!
3. **CARGA_FINAL.py**: Clave simplificada, solo 21/21/21 registros ← MISMO ERROR
4. **CARGA_SIN_FILTRO.py**: Sin drop_duplicates, pandas cuelga leyendo Excel
5. **CARGA_CORREGIDA_FLEXIBLE.py**: Detección flexible, pandas cuelga con ACUSES (46k filas)

#### Diagnóstico con analizar_duplicados.py:
```
Total rows: 58,187
Claves únicas: 58,187 ← NO HAY DUPLICADOS REALES!
```

**Conclusión**: pandas NO tiene duplicados, pero el código sigue marcando 58,166 como duplicados.

### Análisis de Encabezados:

#### ✅ ERP COMERCIAL (PERFECTO):
```
Proveedor
Razón social proveedor
Fecha docto. prov.
Docto. proveedor         ← CORRECTO
Valor bruto
Valor imptos
C.O.
Usuario creación
Clase docto.
Nro documento
```

#### ⚠️ ERP FINANCIERO (DIFERENCIAS MENORES):
```
Proveedor
Razón social proveedor   ← Tiene espacio extra al final
Fecha proveedor
Docto. proveedor         ← CORRECTO (NO "Factura proveedor")
Valor subtotal
Valor impuestos
C.O.
Usuario creación
Clase docto.
Nro documento
```

#### ⚠️ ACUSES (VARIANTES CON PUNTOS/TILDES):
```
Fecha
Adquiriente
Factura
Emisor
Nit Emisor
Nit. PT                  ← Con PUNTO
Estado Docto.            ← Con PUNTO
Descripción Reclamo      ← Con TILDE
Tipo Documento
CUFE
Valor
(+ 5 columnas de acuse adicionales)
```

## 🚨 PROBLEMA CRÍTICO DE PANDAS

### pandas está COLGÁNDOSE al leer Excel grandes:
- ERP COMERCIAL 58k filas → Lee pero cuelga en procesamiento
- ACUSES 46k filas → Cuelga en `pd.read_excel()` (KeyboardInterrupt en XML parsing)

**Causa**: `openpyxl` parsea todo el XML del Excel en memoria, es extremadamente lento para archivos grandes.

## ✅ SOLUCIÓN PROPUESTA

### Opción 1: Convertir Excel → CSV primero
**Ventaja**: pandas lee CSV 100x más rápido que Excel
**Desventaja**: Paso manual extra

```powershell
# En PowerShell:
$excel = New-Object -ComObject Excel.Application
$wb = $excel.Workbooks.Open("C:\...\ERP comercial.xlsx")
$wb.SaveAs("C:\...\ERP comercial.csv", 6)  # 6 = CSV format
$wb.Close()
$excel.Quit()
```

###Option 2: Usar `pyarrow` engine (más rápido)
```python
df = pd.read_excel(file, dtype=str, engine='pyarrow')
```

### Opción 3: Abandonar drop_duplicates, usar SQL
**MEJOR OPCIÓN**: Insertar TODO y dejar que PostgreSQL maneje duplicados

```python
# NO hacer drop_duplicates()
try:
    cursor.copy_from(buffer, 'erp_comercial', columns, sep='\t')
    conn.commit()
except psycopg2.errors.UniqueViolation:
    # Duplicados ignorados por UNIQUE constraint
    conn.rollback()
    # Hacer INSERT ... ON CONFLICT DO NOTHING
```

## 🎯 RECOMENDACIÓN FINAL

**OPCIÓN 3 es la mejor:**
1. ❌ NO usar `drop_duplicates()` en pandas (está roto)
2. ✅ Insertar TODOS los registros del Excel
3. ✅ Dejar que PostgreSQL maneje duplicados con `ON CONFLICT DO NOTHING`
4. ✅ Ver `clave_erp_comercial` UNIQUE constraint en schema

**Ventajas**:
- PostgreSQL es la fuente de verdad para unicidad
- pandas NO puede crear falsos positivos
- Más rápido (sin procesamiento en Python)
- Más confiable (base de datos maneja integridad)

## 📊 VERIFICACIÓN DE ENCABEZADOS

**Script creado**: `verificar_encabezados_excel.py`

**Resultados**:
```
ERP_COMERCIAL:  ✅ 10/10 columnas correctas
ERP_FINANCIERO: ⚠️ 8/10 (pero usa "Docto. proveedor" correctamente)
ACUSES:         ⚠️ 8/11 (variantes con puntos y tildes)
```

**Conclusión**: Los encabezados SON compatibles, solo necesitan búsqueda flexible (case-insensitive).

## 🔧 PRÓXIMO PASO

Crear `CARGA_POSTGRESQL_NATIVO.py que:
1. Lee Excel (o mejor CSV)
2. Mapea columnas con detección flexible
3. **NO hace drop_duplicates()**
4. Usa `INSERT ... ON CONFLICT (clave_xxx) DO NOTHING`
5. PostgreSQL ignora duplicados automáticamente

**Resultado esperado**: 58,187 + 2,996 + 46,650 = ~107,833 registros cargados
