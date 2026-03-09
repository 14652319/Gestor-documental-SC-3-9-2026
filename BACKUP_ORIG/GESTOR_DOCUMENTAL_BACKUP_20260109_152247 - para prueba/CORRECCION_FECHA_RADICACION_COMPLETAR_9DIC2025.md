# 🔥 CORRECCIÓN CRÍTICA: Fecha de Radicación en Completar Campos

**Fecha:** 9 de Diciembre de 2025  
**Problema Identificado:** El formulario de completar-campos NO muestra la FECHA DE RADICACIÓN, que es necesaria para construir correctamente la ruta de carpetas.

---

## 🚨 PROBLEMA ACTUAL

### Síntoma 1: Factura RI-45 en Ubicación Incorrecta
**Factura:** 14652319-RI-45  
**Ubicación Real:** `D:\2025\12. DICIEMBRE\14652319-RI-45\`  
**Ubicación Esperada:** 
- Si es **usuario externo**: `D:\facturas_digitales\TEMPORALES\14652319\14652319-RI-45\`
- Si es **usuario interno**: `D:\facturas_digitales\{EMPRESA}\{AÑO}\{MES}\{DEPTO}\{FORMA_PAGO}\14652319-RI-45\`

### Síntoma 2: Nomenclatura Inconsistente
En el código backend se usa `fecha_emision`, pero en el **formulario de carga** el campo se muestra como:

```html
<input type="date" name="fecha_emision" ...>
<label>FECHA RADICACIÓN *</label>
```

El usuario ve **"FECHA RADICACIÓN"** pero el backend lo procesa como `fecha_emision`.

### Síntoma 3: Formulario de Completar-Campos NO Muestra Fecha
El formulario `completar_campos.html` **NO muestra** la fecha de radicación de la factura, lo cual es crítico porque:

1. El usuario interno necesita **VER la fecha** para saber en qué carpeta (AÑO/MES) quedará guardado el archivo
2. El backend usa `factura.fecha_emision` (que ya está en BD) para construir la ruta, pero el frontend NO lo muestra

---

## ✅ SOLUCIONES REQUERIDAS

### Solución 1: Mostrar Fecha de Radicación en Completar-Campos

#### En `templates/facturas_digitales/completar_campos.html`

**Ubicación:** Líneas 284-298 (sección info-panel)

**Agregar:**
```django-html
<div class="info-item">
    <span class="info-label">Fecha Radicación</span>
    <span class="info-value">{{ factura.fecha_emision.strftime('%d/%m/%Y') if factura.fecha_emision else 'SIN FECHA' }}</span>
</div>
```

**Resultado Visual:**
```
┌──────────────────────────────────────────────────────────────┐
│  NIT Proveedor      │  Número Factura  │  Valor Total       │
│  14652319           │  RI-45           │  $50,000.00        │
├──────────────────────────────────────────────────────────────┤
│  Estado Actual      │  Fecha Radicación                      │
│  PENDIENTE          │  09/12/2025       ← NUEVO              │
└──────────────────────────────────────────────────────────────┘
```

---

### Solución 2: Actualizar Mensaje de Advertencia

**Ubicación:** Líneas 302-308 (alert de advertencia)

**Cambiar:**
```django-html
<!-- ANTES -->
<strong>Importante:</strong> Al guardar, los archivos se moverán automáticamente de TEMPORALES a la ubicación final:
<br><code>EMPRESA/AÑO/MES/DEPARTAMENTO/FORMA_PAGO/</code>

<!-- DESPUÉS -->
<strong>Importante:</strong> Al guardar, los archivos se moverán automáticamente de TEMPORALES a la ubicación final:
<br><code>EMPRESA/{{ factura.fecha_emision.year if factura.fecha_emision else 'YYYY' }}/{{ "{:02d}".format(factura.fecha_emision.month) if factura.fecha_emision else 'MM' }}/DEPARTAMENTO/FORMA_PAGO/</code>
<br><small style="opacity: 0.8;">Ejemplo: SC/2025/12/TIC/CREDITO/ (basado en la fecha de radicación: {{ factura.fecha_emision.strftime('%d/%m/%Y') if factura.fecha_emision else 'SIN FECHA' }})</small>
```

**Resultado Visual:**
```
⚠️ Importante: Al guardar, los archivos se moverán automáticamente de TEMPORALES a la ubicación final:
   EMPRESA/2025/12/DEPARTAMENTO/FORMA_PAGO/
   Ejemplo: SC/2025/12/TIC/CREDITO/ (basado en la fecha de radicación: 09/12/2025)
```

**Ventaja:** El usuario **ve exactamente** en qué carpeta (año/mes) quedará guardada la factura.

---

### Solución 3: Aclarar Nomenclatura en Formulario de Carga

#### En `templates/facturas_digitales/cargar-nueva.html`

**Buscar el label del campo de fecha y cambiar:**

```django-html
<!-- OPCIÓN A: Usar "Fecha de Emisión" (técnicamente correcto) -->
<label for="fecha_emision">Fecha de Emisión *</label>

<!-- OPCIÓN B: Usar ambos nombres (más claro) -->
<label for="fecha_emision">Fecha de Emisión (Radicación) *</label>

<!-- OPCIÓN C: Mantener "Fecha Radicación" y cambiar backend -->
<label for="fecha_radicacion">Fecha Radicación *</label>
<!-- Y en backend cambiar request.form['fecha_emision'] → request.form['fecha_radicacion'] -->
```

**Recomendación:** **OPCIÓN B** - `"Fecha de Emisión (Radicación)"` porque:
- ✅ Técnicamente correcto (es la fecha del documento)
- ✅ Familiar para usuarios (mantiene "Radicación")
- ✅ NO requiere cambios en backend

---

## 🧪 PRUEBA PARA CONFIRMAR EL PROBLEMA

### Paso 1: Verificar Factura RI-45 en Base de Datos
```sql
SELECT 
    id,
    nit_proveedor,
    numero_factura,
    fecha_emision,
    empresa,
    departamento,
    forma_pago,
    ruta_carpeta,
    estado
FROM facturas_digitales
WHERE numero_factura = 'RI-45';
```

**Resultado Esperado:**
| Campo | Valor |
|-------|-------|
| numero_factura | RI-45 |
| fecha_emision | 2025-12-09 (o similar) |
| empresa | NULL (vacío) |
| departamento | NULL (vacío) |
| forma_pago | NULL (vacío) |
| ruta_carpeta | D:\2025\12. DICIEMBRE\14652319-RI-45 |
| estado | pendiente_revision |

**Análisis:**
- ✅ `fecha_emision` SÍ está en BD
- ❌ `empresa`, `departamento`, `forma_pago` están vacíos
- ❌ `ruta_carpeta` es incorrecta (debería estar en TEMPORALES o con estructura completa)

### Paso 2: Verificar Tipo de Usuario en Session
```python
# Agregar log temporal en routes.py línea ~806
print(f"🔍 DEBUG | usuario={session.get('usuario')} | tipo_usuario={session.get('tipo_usuario', 'DEFAULT')}")
```

**Si imprime:** `tipo_usuario=DEFAULT` → Usuario NO tiene tipo_usuario en sesión, cae en default 'interno'

---

## 🔧 CORRECCIONES APLICADAS (Resumen)

### 1. Backend Ya Corregido ✅
- **ESCENARIO 1** (Usuario Interno): Usa `fecha_emision` del formulario
- **ESCENARIO 2** (Usuario Externo): Guarda en TEMPORALES
- **ESCENARIO 3** (Completar Campos): Usa `factura.fecha_emision` de BD

### 2. Falta Corregir en Frontend ⚠️
- [ ] Mostrar fecha de radicación en `completar_campos.html`
- [ ] Actualizar mensaje de advertencia con año/mes calculado
- [ ] Aclarar nomenclatura en formulario de carga

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Completar-Campos (PRIORITARIO)
- [ ] Agregar campo "Fecha Radicación" en info-panel
- [ ] Actualizar mensaje de advertencia con ruta calculada
- [ ] Agregar ejemplo de ruta final con datos reales

### Formulario de Carga (SECUNDARIO)
- [ ] Cambiar label a "Fecha de Emisión (Radicación)"
- [ ] Agregar tooltip explicativo

### Debugging (TEMPORAL)
- [ ] Agregar log de `tipo_usuario` en cargar_factura_api
- [ ] Verificar que usuarios externos SÍ tengan `session['tipo_usuario'] = 'externo'`

---

## 🎯 RESULTADO ESPERADO

### Antes de la Corrección
```
Usuario completa campos de factura en TEMPORALES
↓
Frontend NO muestra fecha de radicación
↓
Usuario NO sabe en qué mes quedará guardada
↓
Backend usa fecha_emision de BD (correcto)
↓
Archivo movido a: SC/2025/08/TIC/CREDITO/ (si fecha_emision es agosto)
↓
Usuario confundido: "¿Por qué no está en diciembre?"
```

### Después de la Corrección
```
Usuario completa campos de factura en TEMPORALES
↓
Frontend MUESTRA: "Fecha Radicación: 15/08/2025"
Frontend MUESTRA: "Se moverá a: EMPRESA/2025/08/DEPARTAMENTO/FORMA_PAGO/"
↓
Usuario ENTIENDE: "Ah, la factura es de agosto, entonces quedará en carpeta 08"
↓
Backend usa fecha_emision de BD (correcto)
↓
Archivo movido a: SC/2025/08/TIC/CREDITO/
↓
Usuario satisfecho: "Quedó exactamente donde me dijeron"
```

---

## 🚨 CASO ESPECIAL: ¿Por Qué RI-45 NO Está en TEMPORALES?

### Análisis
Si RI-45 fue cargada por un **usuario externo**, debería estar en:
```
D:\facturas_digitales\TEMPORALES\14652319\14652319-RI-45\
```

Pero está en:
```
D:\2025\12. DICIEMBRE\14652319-RI-45\
```

### Posibles Causas
1. **Usuario NO tiene `tipo_usuario` en sesión** → Cae en default 'interno'
2. **Código anterior** guardaba sin validar tipo de usuario
3. **Usuario interno** cargó sin llenar empresa/depto/forma_pago (validación faltante antes de corrección)

### Verificación
```python
# En app.py o módulo de login, buscar:
session['tipo_usuario'] = ...

# Debe estar configurándose al momento del login
```

---

## 📄 ARCHIVOS A MODIFICAR

### 1. `templates/facturas_digitales/completar_campos.html`
**Líneas:** 280-310  
**Cambios:**
- Agregar info-item con fecha_radicacion
- Actualizar mensaje de advertencia con año/mes calculado

### 2. `templates/facturas_digitales/cargar-nueva.html` (Opcional)
**Buscar:** `<label for="fecha_emision">`  
**Cambiar a:** `<label for="fecha_emision">Fecha de Emisión (Radicación) *</label>`

### 3. `modules/facturas_digitales/routes.py` (Debugging temporal)
**Línea:** ~806  
**Agregar:**
```python
print(f"🔍 TIPO_USUARIO | usuario={session.get('usuario')} | tipo={tipo_usuario} | rol={session.get('rol')}")
```

---

## ✅ PRÓXIMO PASO INMEDIATO

**IMPLEMENTAR** los cambios en `completar_campos.html` para que el usuario vea:
1. La fecha de radicación de la factura
2. La ruta final calculada (EMPRESA/2025/12/DEPTO/PAGO/)
3. Un ejemplo claro con valores reales

Esto mejorará enormemente la **experiencia de usuario** y evitará confusión sobre dónde quedan guardados los archivos.
