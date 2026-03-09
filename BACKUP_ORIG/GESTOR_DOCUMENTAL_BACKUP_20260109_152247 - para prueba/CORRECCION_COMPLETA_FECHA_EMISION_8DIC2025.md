# 🔥 CORRECCIÓN COMPLETA: Uso de Fecha de Emisión (No Fecha Actual)

**Fecha:** 8 de Diciembre de 2025  
**Módulo:** facturas_digitales  
**Archivo:** `modules/facturas_digitales/routes.py`

---

## 📋 PROBLEMA IDENTIFICADO

### Síntoma
Los archivos de facturas se estaban guardando en ubicaciones incorrectas:
- ❌ **Ubicación Real:** `D:\2025\12. DICIEMBRE\...`
- ✅ **Ubicación Esperada:** `D:\facturas_digitales\{EMPRESA}\{AÑO}\{MES}\{DEPARTAMENTO}\{FORMA_PAGO}\...`

### Ejemplo del Problema
**Factura XE-25:**
- **Base de Datos:**
  - `empresa = "LG"`
  - `departamento = "TIC"`
  - `fecha_emision = "2025-12-08"`
  - `forma_pago = "CREDITO"`
- **Ruta Esperada:** `D:\facturas_digitales\LG\2025\12\TIC\CREDITO\805...-XE-25\`
- **Ruta Real:** ❌ `D:\2025\12. DICIEMBRE\...` (carpeta incorrecta, sin empresa/departamento)

### Causa Raíz
```python
# ❌ CÓDIGO INCORRECTO (ANTES)
fecha_actual = datetime.now()  # ⚠️ Usando fecha ACTUAL, no fecha del documento
año = fecha_actual.year         # ⚠️ Año actual (2025)
mes = f"{fecha_actual.month:02d}"  # ⚠️ Mes actual (12)

# También usaba valores por defecto en lugar de requerir campos
empresa_final = empresa if empresa else 'SIN_EMPRESA'  # ❌ Default
```

**Problema:** El código usaba `datetime.now()` (fecha actual del sistema) en lugar de `fecha_emision` (fecha del documento del formulario) para construir la estructura de carpetas.

---

## ✅ SOLUCIÓN IMPLEMENTADA

### Principio Fundamental
> **TODAS las facturas deben guardarse usando su FECHA DE EMISIÓN (`fecha_emision`), NO la fecha actual del sistema.**

---

## 🔧 CORRECCIONES APLICADAS

### 1️⃣ ESCENARIO 1: Usuario Interno Carga Factura Directa
**Endpoint:** `POST /api/cargar-factura` (Usuario interno)  
**Líneas:** 865-920

#### Cambio Realizado
```python
# ❌ ANTES (INCORRECTO)
fecha_actual = datetime.now()
año = fecha_actual.year
mes = f"{fecha_actual.month:02d}"
empresa_final = empresa if empresa else 'SIN_EMPRESA'
departamento_final = departamento if departamento else 'SIN_DEPARTAMENTO'

# ✅ DESPUÉS (CORRECTO)
# Validar campos obligatorios
if not empresa or not empresa.strip():
    return jsonify({'error': 'EMPRESA es obligatorio'}), 400

if not departamento or not departamento.strip():
    return jsonify({'error': 'DEPARTAMENTO es obligatorio'}), 400

if not forma_pago or not forma_pago.strip():
    return jsonify({'error': 'FORMA DE PAGO es obligatorio'}), 400

# Usar fecha de emisión del formulario
año = fecha_emision.year  # ✅ Del documento, no del sistema
mes = f"{fecha_emision.month:02d}"  # ✅ Del documento

# Construir ruta con datos reales
ruta_final = os.path.join(
    ruta_base,
    empresa,        # ✅ Del formulario, sin default
    str(año),       # ✅ De fecha_emision
    mes,            # ✅ De fecha_emision
    departamento,   # ✅ Del formulario, sin default
    forma_pago      # ✅ Del formulario, sin default
)
```

#### Impacto
- ✅ Facturas se guardan en carpeta del **mes del documento**, no mes actual
- ✅ Requiere TODOS los campos (empresa, departamento, forma_pago)
- ✅ Retorna error 400 si falta algún campo obligatorio
- ✅ No usa valores por defecto (SIN_EMPRESA, etc.)

---

### 2️⃣ ESCENARIO 2: Usuario Externo Carga Factura (TEMPORALES)
**Endpoint:** `POST /api/cargar-factura` (Usuario externo)  
**Líneas:** 865-920

#### Lógica Correcta
```python
# Usuario externo: Guardar en TEMPORALES
if tipo_usuario == 'externo':
    ruta_carpeta = os.path.join(
        ruta_base,
        'TEMPORALES',
        tercero_nit,  # NIT del proveedor
        nombre_carpeta  # {NIT}-{PREFIJO}-{FOLIO}
    )
    # ✅ NO requiere empresa/departamento/forma_pago aún
    # ✅ Se guardan en carpeta temporal por NIT
```

#### Impacto
- ✅ Usuarios externos NO necesitan empresa/departamento/forma_pago al cargar
- ✅ Archivos van a `D:\facturas_digitales\TEMPORALES\{NIT}\{NIT-PREFIJO-FOLIO}\`
- ✅ Pendientes de que usuario interno complete los campos

---

### 3️⃣ ESCENARIO 3: Usuario Interno Completa Factura Externa
**Endpoint:** `PUT /api/factura/<id>/actualizar`  
**Líneas:** 1593-1660

#### Cambio Realizado
```python
# ❌ ANTES (INCORRECTO)
año = factura.fecha_emision.year if factura.fecha_emision else datetime.now().year
mes = f"{factura.fecha_emision.month:02d}" if factura.fecha_emision else f"{datetime.now().month:02d}"
forma_pago if forma_pago else 'SIN_FORMA_PAGO'  # Default

# ✅ DESPUÉS (CORRECTO)
# Validar campos obligatorios ANTES de mover archivos
if not empresa or not empresa.strip():
    return jsonify({'error': 'EMPRESA es obligatorio'}), 400

if not departamento or not departamento.strip():
    return jsonify({'error': 'DEPARTAMENTO es obligatorio'}), 400

if not forma_pago or not forma_pago.strip():
    return jsonify({'error': 'FORMA DE PAGO es obligatorio'}), 400

# Validar que la factura tenga fecha de emisión
if not factura.fecha_emision:
    return jsonify({
        'error': 'La factura no tiene fecha de emisión. No se puede determinar la ubicación final.'
    }), 400

# Usar SIEMPRE la fecha de emisión del documento
año = factura.fecha_emision.year  # ✅ Sin fallback a datetime.now()
mes = f"{factura.fecha_emision.month:02d}"  # ✅ Sin fallback

# Construir ruta final
nueva_ruta = os.path.join(
    ruta_base,
    empresa,        # ✅ Obligatorio
    str(año),       # ✅ De fecha_emision
    mes,            # ✅ De fecha_emision
    departamento,   # ✅ Obligatorio
    forma_pago      # ✅ Obligatorio, sin default
)

# Mover archivos de TEMPORALES a ubicación final
# (código de shutil.move...)
```

#### Impacto
- ✅ Al completar campos, archivos se mueven de TEMPORALES a ubicación correcta
- ✅ Usa **fecha_emision del documento**, no fecha actual
- ✅ Requiere TODOS los campos antes de mover archivos
- ✅ Retorna error si falta fecha_emision en la base de datos

---

## 📊 COMPARACIÓN: ANTES vs DESPUÉS

### Factura con fecha_emision = "2025-08-15", cargada el 8 de diciembre

| Aspecto | ❌ ANTES (Incorrecto) | ✅ DESPUÉS (Correcto) |
|---------|----------------------|----------------------|
| **Año usado** | 2025 (fecha actual) | 2025 (fecha emisión) ✅ |
| **Mes usado** | 12 (diciembre, actual) | 08 (agosto, emisión) ✅ |
| **Ruta generada** | `D:\2025\12\...` | `D:\facturas_digitales\{EMPRESA}\2025\08\{DEPTO}\{FORMA_PAGO}\` ✅ |
| **Empresa** | SIN_EMPRESA (default) | LG (del formulario) ✅ |
| **Departamento** | SIN_DEPARTAMENTO (default) | TIC (del formulario) ✅ |
| **Forma Pago** | SIN_FORMA_PAGO (default) | CREDITO (del formulario) ✅ |

### Ejemplo Real: Factura XE-25

**Datos del Formulario:**
- `empresa = "LG"`
- `departamento = "TIC"`
- `forma_pago = "CREDITO"`
- `fecha_emision = "2025-12-08"`

**Resultado:**

| ❌ ANTES | ✅ DESPUÉS |
|---------|-----------|
| `D:\2025\12. DICIEMBRE\805...-XE-25\` | `D:\facturas_digitales\LG\2025\12\TIC\CREDITO\805...-XE-25\` |
| ⚠️ Sin empresa en ruta | ✅ Empresa "LG" en ruta |
| ⚠️ Sin departamento en ruta | ✅ Departamento "TIC" en ruta |
| ⚠️ Sin forma de pago en ruta | ✅ Forma de pago "CREDITO" en ruta |
| ⚠️ Carpeta "12. DICIEMBRE" | ✅ Carpeta "12" (numérica) |

---

## 🎯 CASOS DE USO CORREGIDOS

### Caso 1: Factura de Agosto Cargada en Diciembre
```
Formulario:
  - fecha_emision: 2025-08-15
  - empresa: SC
  - departamento: CYS
  - forma_pago: CONTADO

❌ ANTES: D:\2025\12\SIN_EMPRESA\SIN_DEPARTAMENTO\SIN_FORMA_PAGO\805...-FE-123\
✅ AHORA:  D:\facturas_digitales\SC\2025\08\CYS\CONTADO\805...-FE-123\
```

### Caso 2: Usuario Externo (TEMPORALES)
```
Usuario: Externo (tipo_usuario = 'externo')
Factura: XE-456

❌ ANTES: D:\2025\12\... (ignoraba tipo de usuario)
✅ AHORA:  D:\facturas_digitales\TEMPORALES\805028041\805...-XE-456\
```

### Caso 3: Completar Factura Externa
```
Factura XE-456 en TEMPORALES (cargada por externo en agosto)
Usuario interno completa campos en diciembre:
  - empresa: LG
  - departamento: DOM
  - forma_pago: CREDITO
  - fecha_emision: 2025-08-20 (ya estaba en BD)

❌ ANTES: 
   - Movida a D:\2025\12\SIN_EMPRESA\... (fecha actual, defaults)
   
✅ AHORA:
   - Validación de campos obligatorios
   - Movida a D:\facturas_digitales\LG\2025\08\DOM\CREDITO\805...-XE-456\
   - Usa fecha_emision (agosto), no fecha actual (diciembre)
```

---

## 🔍 VALIDACIONES AGREGADAS

### Validación 1: Campos Obligatorios (Usuarios Internos)
```python
if not empresa or not empresa.strip():
    return jsonify({'error': 'EMPRESA es obligatorio'}), 400

if not departamento or not departamento.strip():
    return jsonify({'error': 'DEPARTAMENTO es obligatorio'}), 400

if not forma_pago or not forma_pago.strip():
    return jsonify({'error': 'FORMA DE PAGO es obligatorio'}), 400
```

**Impacto:**
- ✅ Frontend debe enviar TODOS los campos
- ✅ No se aceptan campos vacíos o solo espacios
- ✅ Error 400 con mensaje claro si falta algún campo

### Validación 2: Fecha de Emisión (Al Completar Campos)
```python
if not factura.fecha_emision:
    return jsonify({
        'error': 'La factura no tiene fecha de emisión. No se puede determinar la ubicación final.'
    }), 400
```

**Impacto:**
- ✅ Previene movimiento de archivos si fecha_emision es NULL
- ✅ Asegura que estructura de carpetas siempre tenga año/mes válido

---

## 📝 LOGS AGREGADOS

### ESCENARIO 1: Carga Directa (Usuario Interno)
```python
log_security(
    f"ESCENARIO 1 - USUARIO INTERNO | tipo_usuario={tipo_usuario} | "
    f"empresa={empresa} | departamento={departamento} | forma_pago={forma_pago} | "
    f"fecha_emision={fecha_emision.strftime('%Y-%m-%d')} | "
    f"ruta={ruta_final}"
)
```

### ESCENARIO 2: TEMPORALES (Usuario Externo)
```python
log_security(
    f"ESCENARIO 2 - USUARIO EXTERNO (TEMPORALES) | tipo_usuario={tipo_usuario} | "
    f"nit={tercero_nit} | prefijo={prefijo} | folio={folio} | "
    f"ruta={ruta_carpeta}"
)
```

### ESCENARIO 3: Completar Campos
```python
log_security(
    f"ESCENARIO 3 - COMPLETAR CAMPOS | factura_id={id} | "
    f"empresa={empresa} | departamento={departamento} | forma_pago={forma_pago} | "
    f"fecha_emision={factura.fecha_emision.strftime('%Y-%m-%d')}"
)

log_security(
    f"MOVIMIENTO TEMPORALES->FINAL | factura_id={id} | "
    f"archivos_movidos={archivos_movidos} | "
    f"hacia={empresa}/{año}/{mes}/{departamento}/{forma_pago}"
)
```

---

## 🧪 PRUEBAS RECOMENDADAS

### Prueba 1: Usuario Interno - Factura de Agosto
```
1. Login como usuario interno
2. Ir a "Cargar Nueva Factura"
3. Llenar formulario:
   - Fecha Emisión: 15/08/2025
   - Empresa: SC
   - Departamento: CYS
   - Forma Pago: CONTADO
   - Subir PDF
4. Verificar archivo en: D:\facturas_digitales\SC\2025\08\CYS\CONTADO\
5. ✅ NO debe estar en D:\2025\12\
```

### Prueba 2: Usuario Externo - TEMPORALES
```
1. Login como usuario externo
2. Ir a "Cargar Nueva Factura"
3. Llenar formulario:
   - Fecha Emisión: 08/12/2025
   - Subir PDF
   - NO llenar empresa/departamento/forma_pago
4. Verificar archivo en: D:\facturas_digitales\TEMPORALES\{NIT}\{NIT-PREFIJO-FOLIO}\
5. ✅ NO debe estar en D:\2025\12\
```

### Prueba 3: Completar Factura Externa
```
1. Login como usuario interno
2. Ir a "Facturas Temporales"
3. Seleccionar factura XE-456
4. Completar campos:
   - Empresa: LG
   - Departamento: DOM
   - Forma Pago: CREDITO
5. Guardar
6. Verificar:
   - Archivo movido de TEMPORALES a ubicación final
   - Ruta final: D:\facturas_digitales\LG\2025\{MES_EMISION}\DOM\CREDITO\
   - Carpeta TEMPORALES\{NIT}\{NIT-PREFIJO-FOLIO}\ eliminada
7. ✅ Año/Mes deben ser de fecha_emision, NO fecha actual
```

---

## 📁 ARCHIVOS MODIFICADOS

### `modules/facturas_digitales/routes.py`

#### Bloque 1: ESCENARIO 1 y 2 (Carga Inicial)
**Líneas:** 865-920  
**Función:** `cargar_factura_api()`

**Cambios:**
- ❌ Eliminado: `fecha_actual = datetime.now()`
- ✅ Agregado: Validación de campos obligatorios para usuarios internos
- ✅ Cambiado: `año = fecha_emision.year` (antes usaba `fecha_actual.year`)
- ✅ Cambiado: `mes = f"{fecha_emision.month:02d}"` (antes usaba `fecha_actual.month`)
- ✅ Eliminado: Valores por defecto (SIN_EMPRESA, SIN_DEPARTAMENTO, SIN_FORMA_PAGO)
- ✅ Agregado: Logs detallados con identificador de escenario

#### Bloque 2: ESCENARIO 3 (Completar Campos)
**Líneas:** 1593-1660  
**Función:** `actualizar_factura()`

**Cambios:**
- ✅ Agregado: Validación de empresa, departamento, forma_pago obligatorios
- ✅ Agregado: Validación de `factura.fecha_emision` no NULL
- ❌ Eliminado: Fallback a `datetime.now()` en construcción de año/mes
- ✅ Cambiado: `año = factura.fecha_emision.year` (sin fallback)
- ✅ Cambiado: `mes = f"{factura.fecha_emision.month:02d}"` (sin fallback)
- ✅ Eliminado: Default `'SIN_FORMA_PAGO'`
- ✅ Agregado: Log al inicio con valores del formulario

---

## ✅ CHECKLIST DE CORRECCIÓN

- [x] ESCENARIO 1: Usuario interno usa `fecha_emision` para año/mes
- [x] ESCENARIO 1: Validación de campos obligatorios (empresa, depto, forma_pago)
- [x] ESCENARIO 1: Sin valores por defecto (SIN_EMPRESA, etc.)
- [x] ESCENARIO 2: Usuario externo guarda en TEMPORALES
- [x] ESCENARIO 2: No requiere empresa/depto/forma_pago al cargar
- [x] ESCENARIO 3: Usuario interno completa campos con validación
- [x] ESCENARIO 3: Usa `factura.fecha_emision` (no datetime.now())
- [x] ESCENARIO 3: Valida fecha_emision no NULL antes de mover archivos
- [x] ESCENARIO 3: Sin defaults al construir ruta final
- [x] Logs agregados en los 3 escenarios
- [x] Documentación actualizada

---

## 🚨 FACTURAS EXISTENTES CON UBICACIÓN INCORRECTA

### Facturas Identificadas en Ruta Incorrecta
```
1. FE-13   → D:\2025\12. DICIEMBRE\
2. FE-44   → D:\2025\12. DICIEMBRE\
3. FE-48   → D:\2025\12. DICIEMBRE\
4. XE-25   → (Ruta incorrecta, sin empresa/depto en path)
```

### Acción Requerida
**Opción A: Mover Manualmente**
1. Consultar datos de cada factura en BD:
   ```sql
   SELECT id, empresa, departamento, forma_pago, fecha_emision, ruta_carpeta
   FROM facturas_digitales
   WHERE numero_factura IN ('FE-13', 'FE-44', 'FE-48', 'XE-25');
   ```
2. Construir ruta correcta: `D:\facturas_digitales\{EMPRESA}\{AÑO}\{MES}\{DEPTO}\{FORMA_PAGO}\`
3. Mover archivos con Windows Explorer
4. Actualizar campo `ruta_carpeta` en BD

**Opción B: Usar Endpoint de Actualización** (Recomendado)
1. Acceder al módulo de facturas digitales
2. Buscar cada factura (FE-13, FE-44, FE-48, XE-25)
3. Usar formulario "Completar Campos" (ESCENARIO 3)
4. El sistema:
   - Validará campos
   - Moverá archivos a ubicación correcta usando `fecha_emision`
   - Actualizará BD automáticamente

**Opción C: Script Automático**
```python
# Script: mover_facturas_incorrectas.py
# Lee facturas con ruta incorrecta
# Construye ruta correcta usando fecha_emision de BD
# Mueve archivos
# Actualiza campo ruta_carpeta
```

---

## 🎓 LECCIONES APRENDIDAS

### 1. Siempre Usar Fecha del Documento
> ❌ NO usar `datetime.now()` para estructura de carpetas  
> ✅ USAR `fecha_emision` del documento (del formulario o BD)

### 2. Validar, No Asumir
> ❌ NO usar valores por defecto (SIN_EMPRESA, etc.)  
> ✅ VALIDAR que campos requeridos estén presentes

### 3. Logs Detallados
> ✅ Agregar logs con identificador de escenario  
> ✅ Incluir valores clave: fecha_emision, empresa, ruta generada

### 4. Pruebas con Fechas Pasadas
> ✅ Probar con fecha_emision antigua (ej: agosto) cargada hoy (diciembre)  
> ✅ Verificar que año/mes usen fecha del documento, no fecha actual

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `LOGICA_GUARDADO_FACTURAS_DIGITALES.md` - Especificación completa de 3 escenarios
- `DONDE_ESTAN_MIS_ARCHIVOS.md` - Estado de archivos existentes
- `buscar_rutas_facturas.py` - Script diagnóstico
- `verificar_logica_facturas.py` - Script de verificación

---

## ✅ ESTADO FINAL

### Código Corregido
- ✅ `/api/cargar-factura` - Usa `fecha_emision` (no `datetime.now()`)
- ✅ `/api/factura/<id>/actualizar` - Usa `fecha_emision` (no `datetime.now()`)
- ✅ Validaciones agregadas en ambos endpoints
- ✅ Sin valores por defecto (SIN_EMPRESA, etc.)
- ✅ Logs detallados implementados

### Próximos Pasos
1. **Probar** los 3 escenarios con facturas nuevas
2. **Corregir** ubicación de facturas existentes (FE-13, FE-44, FE-48, XE-25)
3. **Monitorear** logs en `logs/security.log` para confirmar rutas correctas
4. **Documentar** cualquier caso especial descubierto durante pruebas

---

**Corrección Completada:** 8 de Diciembre de 2025  
**Autor:** GitHub Copilot  
**Revisado por:** Usuario  
**Estado:** ✅ LISTO PARA PROBAR
