# 🔥 CORRECCIÓN CRÍTICA: Movimiento de Archivos y Creación de Carpetas

**Fecha:** 9 de Diciembre de 2025  
**Problema:** Al completar campos de factura RII-14, NO se movieron los archivos y NO se crearon las carpetas necesarias.

---

## 🚨 PROBLEMA IDENTIFICADO

### Caso Real: Factura RII-14
**Situación:**
1. Usuario (¿externo o interno?) cargó factura RII-14
2. Archivo guardado en: `D:\2025\12. DICIEMBRE\14652319-RII-14\` ❌ **INCORRECTO**
3. Usuario interno completó campos:
   - Empresa: SC - SUPERTIENDAS CAÑAVERAL
   - Departamento: COMPRAS Y SUMINISTROS
   - Forma de Pago: TARJETA DE CRÉDITO
   - Tipo Documento: FACTURA
   - Tipo Servicio: COMPRA
4. Sistema respondió: "Archivos movidos a: `/2025/12. DICIEMBRE///14652319-RII-14`" ❌
5. **Resultado:** NO se crearon carpetas, NO se movieron archivos

### Ubicación Esperada
```
D:\facturas_digitales\
├── SC - SUPERTIENDAS CAÑAVERAL\    ← Carpeta por empresa
│   └── 2025\                        ← Carpeta por año
│       └── 12\                      ← Carpeta por mes
│           └── COMPRAS Y SUMINISTROS\  ← Carpeta por departamento
│               └── TARJETA DE CRÉDITO\  ← Carpeta por forma de pago
│                   └── 14652319-RII-14\  ← Carpeta de la factura
│                       ├── 14652319-RII-14-PRINCIPAL.pdf
│                       └── otros archivos...
```

---

## 🔍 CAUSAS RAÍZ IDENTIFICADAS

### 1. Movimiento Condicional Incorrecto
**Código anterior:**
```python
if factura.ruta_carpeta and 'TEMPORALES' in factura.ruta_carpeta.upper():
    # Solo movía si estaba en TEMPORALES
```

**Problema:** Si la factura NO estaba en TEMPORALES (ej: en `D:\2025\`), NO movía los archivos.

### 2. Carga Inicial Incorrecta
**Posible causa:** Usuario NO tenía `tipo_usuario = 'externo'` en sesión, por lo que cayó en default `'interno'` pero NO llenó campos obligatorios.

**Resultado:** Archivo guardado en ubicación incorrecta (`D:\2025\` en lugar de `TEMPORALES` o ruta completa).

### 3. Falta de Logs de Diagnóstico
Sin logs detallados era imposible saber:
- ¿Qué tipo de usuario cargó la factura?
- ¿Qué ruta se calculó?
- ¿Se crearon las carpetas?
- ¿Se movieron los archivos?

---

## ✅ CORRECCIONES APLICADAS

### 1️⃣ Movimiento SIEMPRE (No Solo desde TEMPORALES)

**Antes:**
```python
if factura.ruta_carpeta and 'TEMPORALES' in factura.ruta_carpeta.upper():
    # Solo si viene de TEMPORALES
    nueva_ruta = ...
    os.makedirs(nueva_ruta, exist_ok=True)
    # mover archivos
```

**Después:**
```python
# SIEMPRE construir ruta final y crear carpetas
nueva_ruta = os.path.join(
    ruta_base,
    empresa,
    str(año),
    mes,
    departamento,
    forma_pago
)

# 🔧 CREAR TODA LA ESTRUCTURA (empresa/año/mes/depto/pago)
os.makedirs(nueva_ruta, exist_ok=True)

# MOVER si la ruta actual es diferente a la nueva
if factura.ruta_carpeta and os.path.normpath(factura.ruta_carpeta) != os.path.normpath(nueva_ruta):
    # mover todos los archivos
    # eliminar carpeta origen vacía
```

**Ventajas:**
- ✅ Crea carpetas SIEMPRE (aunque NO esté en TEMPORALES)
- ✅ Mueve archivos desde CUALQUIER ubicación incorrecta
- ✅ Actualiza ruta en BD correctamente

---

### 2️⃣ Logs Detallados de Diagnóstico

#### En Carga de Factura (línea ~809)
```python
print(f"🔍 CARGA FACTURA | usuario={usuario} | tipo_usuario={tipo_usuario} | rol={session.get('rol')}")
```

#### ESCENARIO 1 - Usuario Interno (línea ~920)
```python
print(f"📦 ESCENARIO 1 - USUARIO INTERNO")
print(f"   Ruta base: {ruta_base}")
print(f"   Empresa: {empresa}")
print(f"   Año: {año} (de fecha_emision: {fecha_emision})")
print(f"   Mes: {mes}")
print(f"   Departamento: {departamento}")
print(f"   Forma Pago: {forma_pago}")
print(f"   Ruta final: {ruta_principal}")
```

#### ESCENARIO 2 - Usuario Externo (línea ~885)
```python
print(f"📦 ESCENARIO 2 - USUARIO EXTERNO")
print(f"   Ruta base: {ruta_base}")
print(f"   Ruta TEMPORALES: {ruta_principal}")
```

#### ESCENARIO 3 - Completar Campos (línea ~1635)
```python
print(f"📁 Creando estructura de carpetas: {nueva_ruta}")
print(f"📦 Moviendo archivos...")
print(f"   Desde: {factura.ruta_carpeta}")
print(f"   Hacia: {nueva_ruta}")
print(f"✅ {archivos_movidos} archivos movidos")
```

**Ventajas:**
- ✅ Permite diagnosticar problemas en tiempo real
- ✅ Muestra exactamente qué ruta se está usando
- ✅ Confirma que carpetas fueron creadas

---

### 3️⃣ Limpieza Mejorada de Carpetas Vacías

**Antes:**
```python
os.rmdir(factura.ruta_carpeta)  # Solo carpeta de factura
os.rmdir(carpeta_nit)           # Solo carpeta padre (NIT)
```

**Después:**
```python
# Eliminar carpeta origen vacía
if os.path.exists(factura.ruta_carpeta) and not os.listdir(factura.ruta_carpeta):
    os.rmdir(factura.ruta_carpeta)
    
    # Eliminar TODAS las carpetas padres vacías
    carpeta_padre = os.path.dirname(factura.ruta_carpeta)
    while carpeta_padre and carpeta_padre != ruta_base:
        if os.path.exists(carpeta_padre) and not os.listdir(carpeta_padre):
            os.rmdir(carpeta_padre)
            carpeta_padre = os.path.dirname(carpeta_padre)
        else:
            break
```

**Ventajas:**
- ✅ Limpia toda la jerarquía de carpetas vacías
- ✅ No deja carpetas huérfanas (`D:\2025\12. DICIEMBRE\` vacío)

---

### 4️⃣ Actualización de Ruta en BD Siempre

**Antes:**
```python
if factura.ruta_carpeta and 'TEMPORALES' in ...:
    # ... mover archivos
    factura.ruta_carpeta = nueva_ruta  # Solo si estaba en TEMPORALES
```

**Después:**
```python
# Construir nueva_ruta SIEMPRE
nueva_ruta = os.path.join(...)

# Mover archivos SI es necesario
if factura.ruta_carpeta and ruta_actual != nueva_ruta:
    # ... mover archivos

# ACTUALIZAR BD SIEMPRE (aunque no se hayan movido archivos)
factura.ruta_carpeta = nueva_ruta
```

**Ventajas:**
- ✅ BD siempre tiene la ruta correcta
- ✅ Siguiente acceso ya usa ruta correcta

---

## 🧪 PRUEBAS RECOMENDADAS

### Prueba 1: Factura RII-14 (Ya Existe en D:\2025\)
1. Acceder a formulario "Completar Campos" de RII-14
2. Llenar campos (empresa, depto, forma_pago)
3. Click "Actualizar y Mover Archivos"
4. **Verificar en terminal:**
   ```
   📁 Creando estructura de carpetas: D:\facturas_digitales\SC - SUPERTIENDAS CAÑAVERAL\2025\12\COMPRAS Y SUMINISTROS\TARJETA DE CRÉDITO
   ✅ Estructura creada exitosamente
   📦 Moviendo archivos...
      Desde: D:\2025\12. DICIEMBRE\14652319-RII-14
      Hacia: D:\facturas_digitales\SC - SUPERTIENDAS CAÑAVERAL\2025\12\COMPRAS Y SUMINISTROS\TARJETA DE CRÉDITO
   ✅ 3 archivos movidos
   ✅ Carpeta origen eliminada (vacía): D:\2025\12. DICIEMBRE\14652319-RII-14
   ```
5. **Verificar en Windows Explorer:**
   - ✅ Existe: `D:\facturas_digitales\SC - SUPERTIENDAS CAÑAVERAL\2025\12\COMPRAS Y SUMINISTROS\TARJETA DE CRÉDITO\`
   - ✅ NO existe: `D:\2025\12. DICIEMBRE\14652319-RII-14\` (eliminada)
   - ✅ Archivos movidos correctamente

### Prueba 2: Usuario Externo Carga Nueva Factura
1. Login como usuario externo (rol='externo')
2. Ir a "Cargar Nueva Factura"
3. Llenar solo campos básicos (SIN empresa/depto/forma_pago)
4. Subir PDF
5. **Verificar en terminal:**
   ```
   🔍 CARGA FACTURA | usuario=proveedor123 | tipo_usuario=externo | rol=externo
   📦 ESCENARIO 2 - USUARIO EXTERNO
      Ruta base: D:/facturas_digitales
      Ruta TEMPORALES: D:/facturas_digitales/TEMPORALES/14652319/14652319-XE-30
   ✅ Carpeta TEMPORALES creada
   ```
6. **Verificar en Windows Explorer:**
   - ✅ Existe: `D:\facturas_digitales\TEMPORALES\14652319\14652319-XE-30\`
   - ❌ NO existe en: `D:\2025\`

### Prueba 3: Usuario Interno Carga con Todos los Campos
1. Login como usuario interno (rol='interno' o 'admin')
2. Ir a "Cargar Nueva Factura"
3. Llenar TODOS los campos (empresa, depto, forma_pago, etc.)
4. Subir PDF
5. **Verificar en terminal:**
   ```
   🔍 CARGA FACTURA | usuario=admin | tipo_usuario=interno | rol=admin
   📦 ESCENARIO 1 - USUARIO INTERNO
      Empresa: LG
      Año: 2025 (de fecha_emision: 2025-12-09)
      Mes: 12
      Departamento: TIC
      Forma Pago: CREDITO
      Ruta final: D:/facturas_digitales/LG/2025/12/TIC/CREDITO
   ✅ Estructura de carpetas creada
   ```
6. **Verificar en Windows Explorer:**
   - ✅ Existe: `D:\facturas_digitales\LG\2025\12\TIC\CREDITO\`
   - ❌ NO existe en: `D:\2025\` ni en `TEMPORALES`

---

## 📋 COMPARACIÓN: ANTES vs DESPUÉS

### Caso: Completar Campos de Factura en D:\2025\

| Aspecto | ❌ ANTES | ✅ DESPUÉS |
|---------|---------|-----------|
| **Condición de movimiento** | Solo si está en TEMPORALES | SIEMPRE si ruta es diferente |
| **Creación de carpetas** | Solo si está en TEMPORALES | SIEMPRE (empresa/año/mes/depto/pago) |
| **Ruta en BD** | Solo actualiza si mueve | SIEMPRE actualiza |
| **Logs** | Sin logs | Logs detallados en cada paso |
| **Limpieza** | Solo 2 niveles | Recursiva hasta ruta_base |
| **Resultado RII-14** | Quedó en D:\2025\ | Se mueve a D:\facturas_digitales\SC\2025\12\... |

---

## 🎯 ESTRUCTURA DE DATOS Y TABLAS

### Tabla: `facturas_digitales`
Cada factura tiene un registro con:
```sql
CREATE TABLE facturas_digitales (
    id SERIAL PRIMARY KEY,
    nit_proveedor VARCHAR(20),
    numero_factura VARCHAR(50),         -- "RII-14"
    fecha_emision DATE,                  -- 2025-12-09 (usado para año/mes en ruta)
    empresa VARCHAR(100),                -- "SC - SUPERTIENDAS CAÑAVERAL"
    departamento VARCHAR(100),           -- "COMPRAS Y SUMINISTROS"
    forma_pago VARCHAR(50),              -- "TARJETA DE CRÉDITO"
    ruta_carpeta TEXT,                   -- Ruta COMPLETA en disco
    estado VARCHAR(50),                  -- "pendiente", "pendiente_firma", etc.
    -- ... otros campos
);
```

### Uso de Datos para Ruta
**SÍ**, el sistema **SÍ usa los datos de la tabla** para construir la ruta:

```python
# 1. Lee datos de la tabla
empresa = factura.empresa           # "SC - SUPERTIENDAS CAÑAVERAL"
departamento = factura.departamento # "COMPRAS Y SUMINISTROS"
forma_pago = factura.forma_pago     # "TARJETA DE CRÉDITO"
año = factura.fecha_emision.year    # 2025
mes = factura.fecha_emision.month   # 12

# 2. Construye ruta con esos datos
nueva_ruta = os.path.join(
    'D:/facturas_digitales',
    empresa,           # Del registro en BD
    str(año),          # De fecha_emision en BD
    f"{mes:02d}",      # De fecha_emision en BD
    departamento,      # Del registro en BD
    forma_pago         # Del registro en BD
)
# Resultado: D:\facturas_digitales\SC - SUPERTIENDAS CAÑAVERAL\2025\12\COMPRAS Y SUMINISTROS\TARJETA DE CRÉDITO

# 3. Crea carpetas y mueve archivos
os.makedirs(nueva_ruta, exist_ok=True)
shutil.move(archivo_origen, archivo_destino)
```

**Flujo completo:**
```
Usuario completa campos en formulario
↓
POST /api/factura/<id>/actualizar con datos del form
↓
Backend actualiza campos en tabla facturas_digitales
↓
Backend lee esos mismos campos de la tabla
↓
Backend construye ruta usando: empresa + año + mes + depto + forma_pago
↓
Backend crea carpetas con os.makedirs()
↓
Backend mueve archivos con shutil.move()
↓
Backend actualiza campo ruta_carpeta en tabla
```

---

## 📊 VALIDACIONES IMPLEMENTADAS

### Validación 1: Campos Obligatorios
```python
if not empresa or not empresa.strip():
    return error("EMPRESA es obligatorio")

if not departamento or not departamento.strip():
    return error("DEPARTAMENTO es obligatorio")

if not forma_pago or not forma_pago.strip():
    return error("FORMA DE PAGO es obligatorio")
```

### Validación 2: Fecha de Emisión
```python
if not factura.fecha_emision:
    return error("Factura sin fecha de emisión. No se puede determinar ubicación.")
```

### Validación 3: Carpeta Origen Existe
```python
if not os.path.exists(factura.ruta_carpeta):
    return error(f"La carpeta origen no existe: {factura.ruta_carpeta}")
```

### Validación 4: Creación de Carpetas
```python
try:
    os.makedirs(nueva_ruta, exist_ok=True)
except Exception as e:
    return error(f"Error al crear estructura de carpetas: {str(e)}")
```

---

## 🚀 PRÓXIMOS PASOS

1. **Reiniciar servidor Flask** para aplicar cambios
   ```cmd
   Ctrl+C
   python app.py
   ```

2. **Probar con factura RII-14** usando formulario de completar-campos

3. **Verificar logs en terminal** para confirmar:
   - Creación de carpetas
   - Movimiento de archivos
   - Actualización de BD

4. **Verificar en Windows Explorer**:
   - Estructura de carpetas correcta
   - Archivos movidos
   - Carpeta origen eliminada

5. **Probar caso de usuario externo** para confirmar guardado en TEMPORALES

---

## ✅ CHECKLIST DE VALIDACIÓN

- [ ] RII-14 movida de `D:\2025\` a `D:\facturas_digitales\SC\2025\12\...\`
- [ ] Todas las carpetas creadas (empresa/año/mes/depto/pago)
- [ ] Archivos movidos correctamente
- [ ] Carpeta origen `D:\2025\12. DICIEMBRE\14652319-RII-14\` eliminada
- [ ] Campo `ruta_carpeta` en BD actualizado
- [ ] Usuario externo nueva factura → guarda en TEMPORALES
- [ ] Logs visibles en terminal con detalles completos

---

**Estado:** ✅ CORRECCIONES APLICADAS - Listo para probar

**Archivos Modificados:**
- `modules/facturas_digitales/routes.py` (líneas 809, 885, 920, 1620-1710)

**Documentación:**
- Este archivo: `CORRECCION_MOVIMIENTO_ARCHIVOS_9DIC2025.md`
