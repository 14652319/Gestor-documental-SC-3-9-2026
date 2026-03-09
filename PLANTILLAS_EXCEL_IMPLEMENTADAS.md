# ✅ PLANTILLAS EXCEL IMPLEMENTADAS - DIAN vs ERP

**Fecha:** 04 de Enero de 2026  
**Módulo:** DIAN vs ERP - Cargar y Procesar  
**Versión:** 1.0

---

## 📋 RESUMEN

Se implementó un sistema completo de plantillas Excel descargables con los encabezados **EXACTOS** que el sistema espera al cargar archivos.

### ✅ Cambios Implementados

1. **3 Plantillas Excel creadas** en `/plantillas/`
   - `plantilla_dian.xlsx` - 9 columnas
   - `plantilla_erp.xlsx` - 6 columnas
   - `plantilla_acuses.xlsx` - 6 columnas

2. **Endpoint Flask actualizado** en `modules/dian_vs_erp/routes.py`
   - `/dian_vs_erp/descargar_plantilla/<tipo>`
   - Genera plantillas automáticamente si no existen
   - Usa encabezados del código de procesamiento (líneas 1240-1265)

3. **Botones agregados/actualizados en 3 templates:**
   - ✅ `visor_dian_v2.html` - Ya tenía botones correctos
   - ✅ `cargar_archivos.html` - Botones agregados con sección dedicada
   - ✅ `cargar_moderno_NEGRO.html` - URLs corregidas con prefijo `/dian_vs_erp/`

---

## 📊 ENCABEZADOS IMPLEMENTADOS

### 1️⃣ PLANTILLA DIAN (9 columnas)

Encabezados **CON ESPACIOS** (formato original DIAN que busca el sistema primero):

```
Tipo Documento
CUFE/CUDE
Numero
Prefijo
Fecha Emision
NIT Emisor
Nombre Emisor
Valor
Forma Pago
```

**Mapeo en código** (routes.py líneas 1241-1267):
```python
nit = str(row.get('nit emisor', row.get('nit_emisor', ''))).strip()
fecha_emision = row.get('fecha emision', row.get('fecha_emision', date.today()))
tipo_documento = str(row.get('tipo documento', row.get('tipo_documento', 'Factura Electrónica')))
prefijo = str(row.get('prefijo', ''))
folio = str(row.get('numero', row.get('folio', '')))
cufe = str(row.get('cufe/cude', row.get('CUFE', row.get('cufe', ''))))
nombre_emisor = str(row.get('nombre emisor', row.get('razon_social', '')))
forma_pago = str(row.get('forma pago', row.get('forma_pago', 'Crédito')))
valor = float(row.get('valor', 0))
```

**Nota:** El sistema acepta ambos formatos:
- **Primario:** "nit emisor" (con espacio) ✅ RECOMENDADO
- **Secundario:** "nit_emisor" (con guion bajo) ✅ También funciona

---

### 2️⃣ PLANTILLA ERP (6 columnas)

Encabezados **EXACTOS** que busca el código mediante detección dinámica:

```
Proveedor
Docto. Proveedor
Clase de Documento
C.O.
Usuario Creacion
Nro. Documento
```

**Lógica de detección** (routes.py líneas 1082-1086):
```python
proveedor_col = next((c for c in cols if "proveedor" in c.lower() and "razon" not in c.lower()), None)
docto_col = next((c for c in cols if "docto" in c.lower() and "proveedor" in c.lower()), None)
clase_col = next((c for c in cols if "clase" in c.lower()), None)
co_col = next((c for c in cols if c.upper() == "C.O."), None)
usuario_col = next((c for c in cols if "usuario" in c.lower() and "creac" in c.lower()), None)
nro_doc_col = next((c for c in cols if "nro" in c.lower() and "documento" in c.lower()), None)
```

**Requisitos críticos:**
- ✅ Columna `Proveedor` NO debe contener "razon" en el nombre
- ✅ Columna `Docto. Proveedor` debe contener ambos: "docto" Y "proveedor"
- ✅ Columna `C.O.` debe ser EXACTAMENTE "C.O." (mayúsculas con puntos)

---

### 3️⃣ PLANTILLA ACUSES (6 columnas)

Encabezados con espacios (formato SIESA):

```
Fecha
Adquiriente
Factura
Emisor
CUFE
Estado Docto.
```

**Mapeo en código** (routes.py línea 1215):
```python
cufe = str(row.get('CUFE', row.get('cufe', '')))
estado = str(row.get('Estado Docto.', row.get('estado', 'Pendiente')))
```

**Nota:** Sistema acepta:
- **Primario:** "Estado Docto." (con punto) ✅ RECOMENDADO
- **Secundario:** "estado" (minúscula) ✅ También funciona

---

## 🖼️ INTERFAZ DE USUARIO

### Visor V2 (`/dian_vs_erp/visor_v2`)

Botones en la parte superior:
```
[📂 Cargar/Procesar] [Plantilla DIAN] [Plantilla ERP] [Plantilla Acuses]
```

### Cargar Archivos (`/dian_vs_erp/cargar_archivos`)

Sección dedicada antes de las zonas de carga:
```
📋 Plantillas Excel:  [📥 Plantilla DIAN] [📥 Plantilla ERP] [📥 Plantilla Acuses]
```

### Cargar Moderno Negro (`/dian_vs_erp/cargar_moderno_negro`)

Botones en la parte inferior del formulario:
```
Plantillas:  [📥 DIAN] [📥 ERP] [📥 Acuses]
```

---

## 🔧 IMPLEMENTACIÓN TÉCNICA

### Endpoint Flask

**Archivo:** `modules/dian_vs_erp/routes.py` (líneas 776-852)

```python
@dian_vs_erp_bp.route('/descargar_plantilla/<tipo>')
def descargar_plantilla(tipo):
    """
    Descargar plantillas Excel con encabezados EXACTOS que el sistema espera
    """
    plantillas_dir = BASE_DIR / "plantillas"
    
    if tipo == "dian":
        archivo = plantillas_dir / "plantilla_dian.xlsx"
        headers = [
            'Tipo Documento', 'CUFE/CUDE', 'Numero', 'Prefijo', 
            'Fecha Emision', 'NIT Emisor', 'Nombre Emisor', 
            'Valor', 'Forma Pago'
        ]
    elif tipo == "erp":
        archivo = plantillas_dir / "plantilla_erp.xlsx"
        headers = [
            'Proveedor', 'Docto. Proveedor', 'Clase de Documento',
            'C.O.', 'Usuario Creacion', 'Nro. Documento'
        ]
    elif tipo == "acuses":
        archivo = plantillas_dir / "plantilla_acuses.xlsx"
        headers = [
            'Fecha', 'Adquiriente', 'Factura', 
            'Emisor', 'CUFE', 'Estado Docto.'
        ]
    
    # Si no existe, crear con pandas
    if not archivo.exists():
        df = pd.DataFrame(columns=headers)
        df.to_excel(str(archivo), index=False, engine='openpyxl')
    
    return send_file(str(archivo), as_attachment=True)
```

### Script de Generación

**Archivo:** `crear_plantillas_excel.py`

Script standalone para generar las 3 plantillas. Útil para regenerar después de actualizar encabezados.

**Ejecutar:**
```powershell
python crear_plantillas_excel.py
```

---

## 📝 NOTAS IMPORTANTES

### 1. Normalización de Columnas

El sistema normaliza columnas al leer archivos:
```python
df.rename({c: c.strip().lower() for c in df.columns})
```

**Impacto:**
- "Tipo Documento" → "tipo documento"
- "CUFE/CUDE" → "cufe/cude"
- Espacios múltiples → espacio único
- Mayúsculas → minúsculas

**Por eso el sistema busca ambos formatos (con espacios y con guiones bajos).**

### 2. Validación de Formatos

**Formatos aceptados:** `.xlsx`, `.xlsm`, `.csv`  
**Formato NO aceptado:** `.xls` (Excel 97-2003 - genera errores)

Si un usuario intenta cargar `.xls`, el sistema muestra mensaje de error con solución:
```
❌ ARCHIVO RECHAZADO: 'archivo.xls'
   Formato: .xls

💡 SOLUCIÓN:
   1. Abre el archivo en Excel
   2. Guarda como: Libro de Excel (.xlsx)
   3. Vuelve a subir el archivo
```

### 3. Columnas Opcionales vs Requeridas

**DIAN - Columnas críticas (necesarias para JOIN):**
- `NIT Emisor` - Para identificar proveedor
- `Prefijo` + `Numero` - Para crear clave única
- `CUFE/CUDE` - Para cruces con Acuses

**ERP - Columnas críticas:**
- `Proveedor` - NIT del proveedor
- `Docto. Proveedor` - Prefijo + Folio combinado
- `Clase de Documento` - Para clasificar en COMERCIAL/FINANCIERO

**ACUSES - Columnas críticas:**
- `CUFE` - Para cruce con DIAN
- `Estado Docto.` - Para determinar estado de aprobación

---

## ✅ VALIDACIÓN Y PRUEBAS

### Prueba 1: Descargar Plantillas

1. Ir a `http://localhost:8099/dian_vs_erp/visor_v2`
2. Hacer clic en "Plantilla DIAN"
3. Verificar que descarga `plantilla_dian.xlsx`
4. Abrir en Excel y verificar 9 columnas con nombres correctos
5. Repetir con "Plantilla ERP" y "Plantilla Acuses"

### Prueba 2: Cargar con Plantilla

1. Descargar plantilla DIAN
2. Llenar 2-3 filas con datos de ejemplo:
   ```
   Factura Electrónica | 123abc... | 001 | FV | 2026-01-04 | 123456789 | Proveedor Test | 1000000 | Crédito
   ```
3. Guardar como `.xlsx`
4. Ir a `/dian_vs_erp/cargar_archivos`
5. Cargar archivo en zona DIAN
6. Hacer clic en "Procesar & Consolidar"
7. Verificar que procesa sin errores

### Prueba 3: Validación de Encabezados

1. Modificar encabezado "NIT Emisor" → "nit_emisor" (con guion bajo)
2. Volver a cargar
3. **Resultado esperado:** ✅ Debería funcionar (sistema acepta ambos)

4. Modificar encabezado "C.O." → "co" (minúscula)
5. Volver a cargar
6. **Resultado esperado:** ⚠️ No detectará columna C.O. (debe ser exacto)

---

## 🔮 MEJORAS FUTURAS

### Corto Plazo
- [ ] Agregar filas de ejemplo en las plantillas (no solo encabezados)
- [ ] Incluir comentarios Excel con descripción de cada columna
- [ ] Validación de datos en Excel (listas desplegables para campos categóricos)

### Mediano Plazo
- [ ] Plantillas con formato condicional (colores por tipo de dato)
- [ ] Instrucciones embebidas en primera hoja
- [ ] Plantillas separadas para ERP Financiero vs ERP Comercial
- [ ] Plantilla completa con TODAS las columnas opcionales (no solo las críticas)

### Largo Plazo
- [ ] Validación de archivo antes de procesar (pre-check de columnas)
- [ ] Preview de plantilla en navegador (sin descargar)
- [ ] Generación de plantilla personalizada desde el visor (seleccionar columnas)

---

## 📞 SOPORTE

**Archivos modificados:**
- `modules/dian_vs_erp/routes.py` (líneas 776-852)
- `templates/dian_vs_erp/visor_dian_v2.html` (líneas 277-279)
- `templates/dian_vs_erp/cargar_archivos.html` (líneas 420-440)
- `templates/dian_vs_erp/cargar_moderno_NEGRO.html` (líneas 168-173)
- `crear_plantillas_excel.py` (nuevo)
- `plantillas/*.xlsx` (nuevos - 3 archivos)

**Documentación relacionada:**
- `.github/copilot-instructions.md` - Contexto completo del sistema
- `modules/dian_vs_erp/routes.py` - Lógica de procesamiento de archivos

**Logs:** Los encabezados se imprimen en consola al generar plantillas automáticas:
```
✅ Plantilla dian creada con 9 columnas
   📋 Encabezados: Tipo Documento, CUFE/CUDE, Numero, ...
```

---

**Desarrollador:** GitHub Copilot (Claude Sonnet 4.5)  
**Sistema:** Gestor Documental - Supertiendas Cañaveral  
**Módulo:** DIAN vs ERP v5.0 (Híbrido SQLite + PostgreSQL)
