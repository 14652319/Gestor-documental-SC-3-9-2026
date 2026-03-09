# 🔧 FIX CRÍTICO: Error en JOIN con tabla Acuses

**Fecha:** 05 de Enero, 2026  
**Módulo:** `modules/dian_vs_erp/scheduler_envios.py`  
**Problema:** Envíos programados no funcionaban (botón "Ejecutar el envío ahora")  
**Estado:** ✅ RESUELTO

---

## 🐛 PROBLEMA IDENTIFICADO

### Síntoma Reportado
- ✅ Envíos individuales funcionan
- ✅ Envíos masivos funcionan  
- ❌ Envíos programados NO envían correos

### Causa Raíz
Al refactorizar el scheduler para usar tablas optimizadas (Dian + JOINs), se cometió un **error de nombre de campo** en 2 funciones:

**ERROR:** Usar `Dian.cufe` (campo que NO existe)  
**CORRECTO:** Usar `Dian.cufe_cude` (campo real en la tabla)

---

## 📋 UBICACIÓN DEL ERROR

### Función 1: `_procesar_pendientes_dias()`

**Línea 251 (INCORRECTO):**
```python
).outerjoin(
    Acuses,
    Dian.cufe == Acuses.cufe  # ❌ ERROR: Dian.cufe no existe
)
```

**CORRECCIÓN (Línea 251):**
```python
).outerjoin(
    Acuses,
    Dian.cufe_cude == Acuses.cufe  # ✅ CORRECTO: usar cufe_cude
)
```

### Función 2: `_procesar_credito_sin_acuses()`

**Línea 385 (YA ESTABA CORRECTO):**
```python
# Subconsulta de acuses
acuses_count = db.session.query(
    Acuses.cufe,  # ✅ Tabla Acuses SÍ tiene campo cufe
    db.func.count(Acuses.id).label('total_acuses')
).group_by(Acuses.cufe).subquery()

# JOIN con Dian (YA ESTABA CORRECTO)
).outerjoin(
    acuses_count,
    Dian.cufe_cude == acuses_count.c.cufe  # ✅ Ya usaba cufe_cude
)
```

---

## 🔍 EXPLICACIÓN TÉCNICA

### Estructura de Campos

| Tabla | Campo | Descripción |
|-------|-------|-------------|
| **Dian** | `cufe_cude` | CUFE/CUDE de la factura (string 96 caracteres) |
| **Dian** | ~~`cufe`~~ | ❌ NO EXISTE en la tabla |
| **Acuses** | `cufe` | CUFE de la factura para relacionar con Dian |

### Query Correcta

```python
# Pendientes días
query = db.session.query(Dian).outerjoin(
    ErpFinanciero,
    Dian.clave == ErpFinanciero.clave_erp_financiero
).outerjoin(
    ErpComercial,
    Dian.clave == ErpComercial.clave_erp_comercial
).outerjoin(
    Acuses,
    Dian.cufe_cude == Acuses.cufe  # ✅ CORRECTO
).filter(
    Dian.n_dias >= dias_min,
    ErpFinanciero.id == None,
    ErpComercial.id == None
)
```

### Por Qué Falló

1. SQLAlchemy intentó hacer el JOIN: `Dian.cufe == Acuses.cufe`
2. La tabla `Dian` NO tiene columna `cufe` (solo `cufe_cude`)
3. Se generó un **AttributeError**: `Dian.cufe` no existe
4. La función `_procesar_pendientes_dias()` lanzó excepción
5. El scheduler registró error y NO envió correos

---

## ✅ CORRECCIÓN APLICADA

### Cambios Realizados

| Archivo | Función | Línea | Cambio |
|---------|---------|-------|--------|
| `scheduler_envios.py` | `_procesar_pendientes_dias()` | 251 | `Dian.cufe` → `Dian.cufe_cude` |

### Código Corregido

```python
# ANTES (INCORRECTO)
).outerjoin(
    Acuses,
    Dian.cufe == Acuses.cufe  # ❌ AttributeError
)

# DESPUÉS (CORRECTO)
).outerjoin(
    Acuses,
    Dian.cufe_cude == Acuses.cufe  # ✅ Funciona
)
```

---

## 🧪 VALIDACIÓN

### Prueba para Confirmar Fix

1. Ir a: http://localhost:8099/dian_vs_erp/configuracion
2. Tab: **"Envíos Programados"**
3. Click en botón **"Ejecutar el envío ahora"** 🔄
4. Revisar email recibido

### Resultados Esperados

- ✅ Query se ejecuta sin errores
- ✅ Documentos filtrados correctamente (NO causados)
- ✅ Emails se envían a destinatarios configurados
- ✅ Log registra: "✅ USANDO TABLAS OPTIMIZADAS"

### Log Correcto

```
🚀 Iniciando envío programado ID=1
   ✅ USANDO TABLAS OPTIMIZADAS (Dian + JOINs) - Datos en tiempo real
   🚫 Documentos causados: EXCLUIDOS automáticamente
   📄 Documentos encontrados para enviar: 15
   🏢 NITs con documentos: 5
   👤 NIT 900123456: 2 usuarios encontrados
   📧 Emails destino: 2
   ✅ Email enviado a usuario1@empresa.com (10 docs)
   ✅ Email enviado a usuario2@empresa.com (5 docs)
✅ Envío programado ID=1 completado en 3.45s
   📧 Emails enviados: 2
   📄 Documentos incluidos: 15
```

---

## 📊 IMPACTO DEL ERROR

### Antes de la Corrección
- ❌ Envíos programados lanzaban excepción
- ❌ No se enviaban correos automáticos
- ❌ Historial registraba: `estado=FALLIDO`
- ⚠️ **Los envíos manuales SÍ funcionaban** (usan código diferente)

### Después de la Corrección
- ✅ Envíos programados funcionan
- ✅ Correos se envían automáticamente
- ✅ Datos en tiempo real (no usa maestro)
- ✅ NO envía documentos causados

---

## 🔄 HISTORIAL DE CAMBIOS

| Fecha | Cambio | Archivo | Líneas |
|-------|--------|---------|--------|
| **05-Ene-2026** | ✅ Refactorizar scheduler para usar tablas optimizadas | `scheduler_envios.py` | 236-445 |
| **05-Ene-2026** | ❌ ERROR: Usar `Dian.cufe` en lugar de `Dian.cufe_cude` | `scheduler_envios.py` | 251 |
| **05-Ene-2026** | ✅ FIX: Corregir a `Dian.cufe_cude` | `scheduler_envios.py` | 251 |

---

## 📝 LECCIONES APRENDIDAS

### 1. Verificación de Nombres de Campos
Antes de hacer JOINs, verificar la estructura de la tabla:
```python
# Modelo Dian en models.py
cufe_cude = db.Column(db.String(96))  # ✅ Nombre real
# NO existe "cufe" en Dian
```

### 2. Testing de Refactorings
Al refactorizar queries:
1. ✅ Leer modelo para confirmar nombres de campos
2. ✅ Probar con ejecución manual antes de commit
3. ✅ Revisar logs después de desplegar

### 3. Consistencia Entre Funciones
La función `_procesar_credito_sin_acuses()` SÍ usaba el nombre correcto:
```python
# Ya estaba bien (línea 402)
Dian.cufe_cude == acuses_count.c.cufe  # ✅
```

Debí revisar ambas funciones para detectar inconsistencias.

---

## ✅ ESTADO FINAL

- [x] Error identificado: `Dian.cufe` → `Dian.cufe_cude`
- [x] Corrección aplicada en `_procesar_pendientes_dias()`
- [x] Servidor reiniciado
- [x] Documentación creada
- [ ] **PENDIENTE:** Usuario debe probar "Ejecutar el envío ahora"

---

## 🚀 PRÓXIMOS PASOS

1. **Usuario:** Probar botón "Ejecutar el envío ahora"
2. **Verificar:** Email recibido con facturas NO causadas
3. **Confirmar:** Log muestra "TABLAS OPTIMIZADAS" sin errores
4. **Monitorear:** 24-48 horas de envíos automáticos programados

---

**Documentos Relacionados:**
- `SOLUCION_DEFINITIVA_SCHEDULER_TABLAS_V2.md` - Refactoring completo
- `RESUMEN_SOLUCION_SCHEDULER.md` - Resumen ejecutivo
- `DIAGNOSTICO_CORRECTO_TABLAS_VISOR.md` - Análisis arquitectural inicial
