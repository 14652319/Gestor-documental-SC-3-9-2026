# 📋 DOCUMENTACIÓN: Problema Estado de Aprobación "No Registra"

**Fecha**: 18 de Febrero de 2026  
**Módulo**: DIAN vs ERP - Cargar y Procesar  
**Ubicación**: `modules/dian_vs_erp/routes.py`

---

## 🔍 PROBLEMA IDENTIFICADO

El campo **"Estado de Aprobación"** aparece como **"No Registra"** en el visor de facturas, a pesar de que existen acuses cargados en el sistema.

### Síntomas
- ✅ Archivos DIAN cargan correctamente
- ✅ Archivos ERP (Financiero/Comercial) cargan correctamente
- ✅ Archivo ACUSES carga correctamente
- ❌ Estado de aprobación muestra "No Registra" para todas las facturas
- ⚠️  El JOIN entre DIAN y ACUSES no está encontrando coincidencias

---

## 📊 ANÁLISIS TÉCNICO

### 1. Flujo de Procesamiento de Acuses

**Archivo**: `modules/dian_vs_erp/routes.py` - Líneas 1343-1397

```python
# PASO 1: Cargar archivo acuses desde uploads/acuses/
acuses_csv = latest_csv(UPLOADS["acuses"])
acuses_por_cufe = {}

if acuses_csv:
    acuses_df = read_csv(acuses_csv)
    acuses_pd = acuses_df.to_pandas()
    
    # PASO 2: Buscar columna CUFE
    cufe_col = None
    for col in acuses_pd.columns:
        col_lower = col.lower().strip()
        if 'cufe' in col_lower or 'cude' in col_lower:
            cufe_col = col
            break
    
    # PASO 3: Buscar columna ESTADO
    estado_col = None
    for col in acuses_pd.columns:
        col_lower = col.lower().strip()
        if 'estado' in col_lower and ('docto' in col_lower or 'documento' in col_lower):
            estado_col = col
            break
    
    # PASO 4: Crear diccionario CUFE → Estado
    for _, row in acuses_pd.iterrows():
        cufe = str(row.get(cufe_col, ''))
        estado = str(row.get(estado_col, 'Pendiente'))
        
        if cufe and cufe.strip():
            acuses_por_cufe[cufe.strip()] = estado.strip()
```

### 2. Asignación de Estado de Aprobación

**Archivo**: `modules/dian_vs_erp/routes.py` - Líneas 1602-1607

```python
# Para cada registro de DIAN procesado:
estado_aprobacion = acuses_por_cufe.get(cufe, 'No Registra')

# DEBUG (líneas 1605-1607)
if idx < 3:
    encontrado = "✅ ENCONTRADO" if cufe in acuses_por_cufe else "❌ NO ENCONTRADO"
    print(f"   🔍 Búsqueda acuse: {encontrado} → Estado: '{estado_aprobacion}'")
```

**REGLA CRÍTICA**:
- ✅ Si `cufe` existe en `acuses_por_cufe` → Usa el estado del archivo acuses
- ❌ Si `cufe` NO existe → Muestra **"No Registra"**

### 3. JOIN en Consultas del Visor

**Archivo**: `modules/dian_vs_erp/routes.py` - Líneas 467-478

```python
# LEFT JOIN con tabla Acuses (PostgreSQL)
query = db.session.query(
    MaestroDianVsErp,
    Acuses.estado_docto.label('estado_acuse')
).outerjoin(
    Acuses,
    and_(
        MaestroDianVsErp.cufe == Acuses.cufe,  # 🔥 MATCH POR CUFE
        MaestroDianVsErp.cufe != None,
        MaestroDianVsErp.cufe != ''
    )
)

# Si no hay match:
if estado_acuse and str(estado_acuse).strip():
    estado_aprobacion_final = str(estado_acuse).strip()
else:
    estado_aprobacion_final = "No Registra"  # ⚠️  Sin acuse
```

---

## 🎯 CAUSAS POSIBLES

### Causa #1: CUFEs con Formato Diferente
❌ **DIAN**: `abc123XYZ...` (mayúsculas/minúsculas mixtas)  
❌ **ACUSES**: `ABC123XYZ...` (todo mayúsculas)  
➡️ **Resultado**: No coinciden en comparación exacta

### Causa #2: Espacios o Caracteres Invisibles
❌ **DIAN**: `abc123` (sin espacios)  
❌ **ACUSES**: `abc123 ` (espacio al final)  
➡️ **Resultado**: No coinciden por espacio extra

### Causa #3: Columna CUFE No Detectada
❌ El script busca columnas con texto `'cufe'` o `'cude'`  
❌ Si la columna se llama diferente (ej: `'codigo_unico'`), no la encuentra  
➡️ **Resultado**: Acuses no se procesan

### Causa #4: CUFEs Vacíos o NULL
❌ **DIAN**: CUFE completo de 96 caracteres  
❌ **ACUSES**: CUFE vacío o NULL  
➡️ **Resultado**: No hay nada que comparar

### Causa #5: Archivo .xls No Compatible
❌ El error muestra: `"SiesaE-Invoicing-Documento-Recepcion-20260218154422.xls"`  
❌ El sistema rechaza archivos `.xls` (Excel 97-2003)  
❌ **Mensajede error**: _"ARCHIVOS CON FORMATO NO ACEPTADO en 'acuses/'"_  
➡️ **Resultado**: Archivo NO se procesa, tabla acuses queda vacía

---

## 🔧 SOLUCIONES IMPLEMENTADAS

### Solución #1: Validación de Formato de Archivo (✅ IMPLEMENTADO)

**Archivo**: `modules/dian_vs_erp/routes.py` - Líneas 194-209

```python
def save_excel_to_csv_from_disk(archivo_path: str, folder: Path) -> str:
    fname = os.path.basename(archivo_path)
    ext = os.path.splitext(fname)[1].lower()
    
    # ✅ VALIDACIÓN DE FORMATO
    FORMATOS_ACEPTADOS = ['.xlsx', '.xlsm', '.csv']
    if ext not in FORMATOS_ACEPTADOS:
        raise ValueError(
            f"❌ ARCHIVO RECHAZADO: '{fname}'\n"
            f"   Formato: {ext}\n"
            f"   Formatos aceptados: {', '.join(FORMATOS_ACEPTADOS)}\n\n"
            f"💡 SOLUCIÓN:\n"
            f"   1. Abre el archivo en Excel\n"
            f"   2. Guarda como: Libro de Excel (.xlsx)\n"
            f"   3. Vuelve a subir el archivo\n"
        )
```

**MENSAJE AL USUARIO**:
```
❌ ERROR: ARCHIVOS CON FORMATO NO ACEPTADO en 'acuses/':
   • SiesaE-Invoicing-Documento-Recepcion-20260218154422.xls

💡 SOLUCIÓN:
   1. Abre estos archivos en Excel
   2. Guarda como: Libro de Excel (.xlsx)
   3. Elimina los archivos .xls viejos
   4. Vuelve a procesar
   
📋 Formatos aceptados: .xlsx, .xlsm, .csv
```

### Solución #2: Debug Mejorado (✅ IMPLEMENTADO)

**Archivo**: `modules/dian_vs_erp/routes.py` - Líneas 1354-1361, 1368-1389

```python
# 🐛 DEBUG: Mostrar columnas del archivo de acuses
print(f"\n🔍 DEBUG - Columnas disponibles en archivo ACUSES:")
print(f"   Total columnas: {len(acuses_pd.columns)}")
for col in acuses_pd.columns:
    print(f"   - '{col}' (tipo: {acuses_pd[col].dtype})")

# 🐛 DEBUG: Mostrar primeras 3 filas de acuses
print(f"\n🔍 DEBUG - Primeras 3 filas de ACUSES:")
for idx, (_, row) in enumerate(acuses_pd.head(3).iterrows()):
    print(f"   Fila {idx}:")
    for col in acuses_pd.columns:
        print(f"      {col}: {repr(row[col])}")

# 🐛 DEBUG: Mostrar CUFEs cargados
print(f"\n🔍 DEBUG - Primeros 5 acuses en diccionario:")
for idx, (cufe, estado) in enumerate(list(acuses_por_cufe.items())[:5]):
    print(f"   {idx+1}. CUFE: {cufe[:50]}... → Estado: {estado}")
```

### Solución #3: Debug en Búsqueda de CUFEs (✅ IMPLEMENTADO)

**Archivo**: `modules/dian_vs_erp/routes.py` - Líneas 1597-1607

```python
# 🐛 DEBUG: Mostrar CUFEs de primeras 3 facturas DIAN
if idx < 3:
    print(f"   📝 Consulta CUFE: '{cufe[:50] if cufe else 'VACÍO'}...'")

# Buscar estado en acuses
estado_aprobacion = acuses_por_cufe.get(cufe, 'No Registra')

# 🐛 DEBUG: Mostrar resultado de búsqueda
if idx < 3:
    encontrado = "✅ ENCONTRADO" if cufe in acuses_por_cufe else "❌ NO ENCONTRADO"
    print(f"   🔍 Búsqueda acuse: {encontrado} → Estado: '{estado_aprobacion}'")
```

---

## 🛠️ HERRAMIENTAS DE DIAGNÓSTICO

### Script: `verificar_cufes_match.py` (✅ MEJORADO)

Propósito: Verificar si existen coincidencias entre CUFEs de DIAN y ACUSES

**Funcionalidades**:
1. ✅ Lee archivos DIAN y ACUSES
2. ✅ Normaliza nombres de columnas (lowercase)
3. ✅ Detecta columnas CUFE automáticamente
4. ✅ Muestra primeros valores de cada archivo
5. ✅ Calcula intersección de CUFEs
6. ✅ Identifica CUFEs únicos en cada archivo
7. ✅ Calcula porcentaje de cobertura

**Uso**:
```powershell
python verificar_cufes_match.py
```

**Salida Esperada**:
```
🔍 VERIFICACIÓN DE MATCH ENTRE DIAN Y ACUSES
══════════════════════════════════════════════════════════════

📂 Leyendo archivo DIAN: uploads\dian\Dian.xlsx
✅ DIAN leído: 1,234 registros
✅ Columna CUFE encontrada en DIAN: 'cufe/cude'

📂 Leyendo archivo ACUSES: uploads\acuses\acuses.xlsx
✅ ACUSES leído: 567 registros
✅ Columna CUFE encontrada en ACUSES: 'cufe cude'
✅ Columna ESTADO encontrada en ACUSES: 'estado docto'

📊 RESULTADOS:
   ✅ CUFEs que coinciden: 234
   ⚠️  Solo en DIAN: 1,000
   ⚠️  Solo en ACUSES: 333

📈 Cobertura: 18.95% de facturas DIAN tienen acuse
```

---

## 📋 PASOS PARA RESOLVER EL PROBLEMA

### Paso 1: Convertir Archivos .xls a .xlsx ⭐ **CRÍTICO**

**Problema Actual**:
```
❌ Archivo: SiesaE-Invoicing-Documento-Recepcion-20260218154422.xls
❌ Formato: .xls (Excel 97-2003) - NO COMPATIBLE
```

**Solución**:
1. Abre el archivo `.xls` en Microsoft Excel
2. Haz clic en **Archivo** → **Guardar como**
3. Selecciona formato: **Libro de Excel (*.xlsx)**
4. Guarda con el mismo nombre o uno nuevo
5. Elimina el archivo `.xls` antiguo de `uploads/acuses/`
6. Vuelve a cargar el archivo `.xlsx` nuevo

**Verificación**:
```powershell
# Ver archivos en carpeta acuses
dir "uploads\acuses\"

# Debería mostrar solo archivos .xlsx o .csv
```

### Paso 2: Ejecutar Script de Verificación

```powershell
python verificar_cufes_match.py
```

**Analizar Salida**:
- ✅ **Si hay coincidencias**: El problema está resuelto parcialmente
- ❌ **Si NO hay coincidencias**: Continúa con Paso 3

### Paso 3: Verificar Nombres de Columnas

**Si el script muestra**:
```
❌ ERROR: No se encontró columna CUFE en ACUSES
```

**Solución**:
1. Abre el archivo `acuses.xlsx` en Excel
2. Verifica que haya una columna con nombre:
   - `CUFE/CUDE` o
   - `CUFE` o
   - `CUDE` o
   - Similar
3. Renombra la columna a: **`CUFE/CUDE`** (texto exacto)
4. Guarda el archivo
5. Vuelve a procesar

### Paso 4: Verificar si CUFEs están completos

```powershell
# Ejecutar script que muestra primeros CUFEs
python ver_columnas_directa.py
```

**Verificar**:
- ✅ CUFEs deben tener ~96 caracteres (CUFE) o ~90 (CUDE)
- ❌ Si muestra "nan", "NULL" o vacío → Archivo incompleto

### Paso 5: Re-procesar Archivos

1. Ve al módulo DIAN vs ERP: http://127.0.0.1:8099/dian_vs_erp/cargar_archivos
2. Haz clic en **"Cargar archivo"** para cada sección:
   - 📄 DIAN: `Dian.xlsx` (nuevo o existente)
   - 📋 ACUSES: `acuses.xlsx` (✅ CONVERTIDO A .xlsx)
   - 💼 ERP Financiero: `erp financiero.xlsx`
   - 🏪 ERP Comercial: `erp comercial.xlsx`
3. Haz clic en **"Procesar & Consolidar"**
4. Espera a que termine (puede tomar 1-2 minutos)
5. Ve al Visor V2

### Paso 6: Verificar en Visor

1. Accede a http://127.0.0.1:8099/dian_vs_erp/visor_v2
2. Busca una factura que sepas que tiene acuse
3. Verifica la columna **"Estado de Aprobación"**
4. ✅ Debería mostrar: `Aprobado`, `Rechazado`, `Pendiente`, etc.
5. ❌ Si aún muestra "No Registra" → Ver Paso 7

### Paso 7: Verificar en Base de Datos (Avanzado)

```sql
-- Consultar tabla acuses
SELECT COUNT(*) as total_acuses FROM acuses;

-- Ver primeros acuses
SELECT cufe, estado_docto FROM acuses LIMIT 5;

-- Ver facturas DIAN con y sin acuse
SELECT 
    COUNT(*) FILTER (WHERE estado_aprobacion = 'No Registra') as sin_acuse,
    COUNT(*) FILTER (WHERE estado_aprobacion != 'No Registra') as con_acuse
FROM maestro_dian_vs_erp;
```

---

## 📝 CAMBIOS REALIZADOS EN EL CÓDIGO

### Cambio #1: Validación de Formatos (Dic 29, 2025)
- **Archivo**: `modules/dian_vs_erp/routes.py`
- **Líneas**: 194-231
- **Descripción**: Rechaza archivos `.xls` con mensaje claro
- **Estado**: ✅ IMPLEMENTADO

### Cambio #2: Debug de Columnas de Acuses
- **Archivo**: `modules/dian_vs_erp/routes.py`
- **Líneas**: 1354-1397
- **Descripción**: Imprime todas las columnas y primeras filas de acuses
- **Estado**: ✅ IMPLEMENTADO

### Cambio #3: Debug de Búsqueda de CUFEs
- **Archivo**: `modules/dian_vs_erp/routes.py`
- **Líneas**: 1597-1607
- **Descripción**: Muestra si cada CUFE fue encontrado o no
- **Estado**: ✅ IMPLEMENTADO

### Cambio #4: Normalize Strip en CUFEs
- **Archivo**: `modules/dian_vs_erp/routes.py`
- **Líneas**: 1390-1392
- **Descripción**: Elimina espacios al inicio/final de CUFEs
- **Estado**: ✅ IMPLEMENTADO

```python
if cufe and cufe.strip():
    acuses_por_cufe[cufe.strip()] = estado.strip()
```

---

## 🚦 ESTADOS DE APROBACIÓN ESPERADOS

Valores válidos para `estado_aprobacion`:

| Estado | Descripción | Origen |
|--------|-------------|--------|
| `No Registra` | ❌ Sin acuse en tabla acuses | Sistema |
| `Pendiente` | ⏳ Acuse recibido, sin acción | Archivo acuses |
| `Acuse Recibido` | 📨 DIAN confirmó recibo | Archivo acuses |
| `Acuse Bien/Servicio` | ✅ Recibo de bien/servicio | Archivo acuses |
| `Aceptación Expresa` | ✅ Aceptación explícita | Archivo acuses |
| `Aceptación Tácita` | ✅ Aceptación por tiempo | Archivo acuses |
| `Rechazada` | ❌ Factura rechazada | Archivo acuses |
| `Reclamo` | ⚠️  Con observaciones | Archivo acuses |

---

## 📞 SOPORTE Y SIGUIENTES PASOS

### Si el problema persiste después de los pasos anteriores:

1. **Ejecutar diagnóstico completo**:
   ```powershell
   python verificar_cufes_match.py > diagnostico_acuses.txt
   ```

2. **Revisar logs del sistema**:
   - Terminal donde corre el gestor (puerto 8099)
   - Buscar líneas que digan `DEBUG - Columnas disponibles en archivo ACUSES`
   - Verifica que muestre las columnas correctas

3. **Verificar que el archivo .xlsx sea válido**:
   - Ábrelo en Excel
   - Verifica que tenga datos (no solo encabezados)
   - Verifica que la columna CUFE tenga valores completos

4. **Contactar soporte técnico** con:
   - Archivo `diagnostico_acuses.txt`
   - Screenshot del error
   - Archivo acuses (primeras 10 filas en Excel)

---

## 📌 RESUMEN EJECUTIVO

**PROBLEMA**: Campo "Estado de Aprobación" aparece como "No Registra"

**CAUSA RAÍZ IDENTIFICADA**: 
- ❌ Archivo acuses tiene formato `.xls` (Excel 97-2003)
- ❌ Sistema solo acepta `.xlsx`, `.xlsm`, `.csv`
- ❌ Archivo no se procesa → Tabla `acuses` queda vacía
- ❌ Sin registros en tabla → Todos muestran "No Registra"

**SOLUCIÓN INMEDIATA**:
1. ✅ Convertir archivo `.xls` a `.xlsx` en Excel
2. ✅ Re-cargar archivo en módulo DIAN vs ERP
3. ✅ Procesar y verificar en visor

**MEJORAS IMPLEMENTADAS**:
- ✅ Validación de formatos con mensaje claro
- ✅ Debug detallado de columnas y valores
- ✅ Script de diagnóstico `verificar_cufes_match.py`
- ✅ Normalización de CUFEs (trim de espacios)

**PRÓXIMOS PASOS**:
1. Usuario convierte archivo a .xlsx
2. Re-procesa con nuevo formato
3. Estado de aprobación debería aparecer correctamente

---

**Documentado por**: Copilot  
**Fecha**: 18 de Febrero de 2026  
**Módulo**: DIAN vs ERP v5.20251130
