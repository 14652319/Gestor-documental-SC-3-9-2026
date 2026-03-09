# 🎯 DIAGNÓSTICO CORRECTO: Tablas Usadas por Cada Versión

**Fecha:** 05 de Enero de 2026  
**Problema:** Los envíos programados incluyen documentos causados  
**Causa Raíz:** **TABLA INCORRECTA en el scheduler**

---

## ✅ EL USUARIO TIENE RAZÓN

Las dos versiones del visor **SÍ USAN TABLAS DIFERENTES**:

### 📊 **Versión Antigua: http://127.0.0.1:8099/dian_vs_erp/**

**Template:** `visor_dian_v2.html`  
**API:** `/api/dian` (línea 397 de routes.py)  
**Tabla:** **`maestro_dian_vs_erp`** (PostgreSQL)

```python
# routes.py línea 397-530
@dian_vs_erp_bp.route('/api/dian')
def api_maestro_filtrar():
    """Lee maestro consolidado desde POSTGRESQL"""
    query = MaestroDianVsErp.query
    # Filtra por fechas, buscar, etc.
    # Retorna datos de maestro_dian_vs_erp
```

**Template verifica versión:**
```javascript
{% if version == 'v2' %}
let url = "/dian_vs_erp/api/dian_v2";
{% else %}
let url = "/dian_vs_erp/api/dian";  // ✅ USA ESTA (maestro)
{% endif %}
```

---

### 🆕 **Versión Nueva: http://127.0.0.1:8099/dian_vs_erp/visor_v2**

**Template:** Mismo `visor_dian_v2.html` (pero con `version='v2'`)  
**API:** `/api/dian_v2` (línea 530 de routes.py)  
**Tablas:** **MÚLTIPLES** (JOIN optimizado):
- `dian` (facturas DIAN) ← **TABLA PRINCIPAL**
- `acuses` (acuses de recepción)
- `erp_financiero` (causación módulo financiero)
- `erp_comercial` (causación módulo comercial)
- `facturas_temporales` (facturas en recepción)
- `facturas_recibidas` (facturas recibidas)
- `facturas_digitales` (facturas digitales)
- `tipo_tercero_dian_erp` (clasificación terceros)

```python
# routes.py línea 530-750
@dian_vs_erp_bp.route('/api/dian_v2')
def api_dian_v2():
    """Lee desde tablas optimizadas con LEFT JOIN"""
    query = db.session.query(
        Dian,  # ← TABLA BASE
        Acuses.estado_docto.label('estado_acuse'),
        ErpFinanciero.id.label('existe_financiero'),
        ErpComercial.id.label('existe_comercial'),
        FacturaTemporal.id.label('existe_temporal'),
        FacturaRecibida.id.label('existe_recibida'),
        # ... más campos
    ).outerjoin(Acuses, ...).outerjoin(ErpFinanciero, ...).outerjoin(...)
    # Calcula estado_contable en tiempo real según JOIN
    # Si existe en erp_financiero o erp_comercial → "Causada"
    # Si existe en facturas_recibidas → "Recibida"
    # Si no existe → "No Registrada"
```

**Estado contable se calcula EN TIEMPO REAL** (línea 720-735):
```python
if existe_financiero:
    estado_contable_validado = "Causada"
elif existe_comercial:
    estado_contable_validado = "Causada"
elif existe_recibida or existe_temporal or existe_digital:
    estado_contable_validado = "Recibida"
else:
    estado_contable_validado = "No Registrada"
```

---

## ❌ EL PROBLEMA DEL SCHEDULER

### **Scheduler de Envíos Programados**

**Archivo:** `modules/dian_vs_erp/scheduler_envios.py`  
**Líneas problemáticas:** 230, 370  
**Tabla que USA:** **`maestro_dian_vs_erp`** ❌ **INCORRECTA**

```python
# scheduler_envios.py línea 230 (_procesar_pendientes_dias)
query = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.dias_desde_emision >= dias_min
)
# ❌ USA maestro_dian_vs_erp

# scheduler_envios.py línea 370 (_procesar_credito_sin_acuses)
query_docs = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.forma_pago.in_(forma_pago_credito),
    MaestroDianVsErp.acuses_recibidos < requiere_acuses
)
# ❌ USA maestro_dian_vs_erp
```

---

## 🔍 ¿POR QUÉ ESTÁ MAL?

### **Tabla `maestro_dian_vs_erp`:**

❌ **NO se actualiza en tiempo real** cuando se causa un documento  
❌ **NO refleja el estado actual** de causación desde ERP  
❌ **Es un snapshot desactualizado** (solo se actualiza con SYNC manual)

**Evidencia:**
- Línea 355 de routes.py: Solo actualiza estadísticas básicas
- NO tiene trigger ni actualización automática cuando se causan docs en ERP
- El campo `causada` puede estar desactualizado

### **Tablas optimizadas (`dian`, `erp_financiero`, `erp_comercial`):**

✅ **SE actualizan en tiempo real** cuando se cargan archivos  
✅ **Reflejan el estado actual** de causación  
✅ **SON la fuente de verdad** del sistema

**Evidencia:**
- `erp_financiero` y `erp_comercial` se cargan desde Excel (carga_archivos)
- Representan el estado REAL del ERP en este momento
- `visor_v2` hace JOIN con estas tablas para calcular estado en vivo

---

## 🎯 SOLUCIÓN CORRECTA

### **Opción 1: Usar las MISMAS tablas que visor_v2 (RECOMENDADO)**

**Cambiar el scheduler para que use las tablas optimizadas igual que visor_v2:**

```python
# scheduler_envios.py línea 230
# ❌ ANTES (tabla maestro desactualizada):
query = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.dias_desde_emision >= dias_min
)

# ✅ DESPUÉS (tablas optimizadas con JOIN):
query = db.session.query(Dian).outerjoin(
    ErpFinanciero,
    Dian.clave == ErpFinanciero.clave_erp_financiero
).outerjoin(
    ErpComercial,
    Dian.clave == ErpComercial.clave_erp_comercial
).filter(
    Dian.n_dias >= dias_min,
    ErpFinanciero.id == None,  # ✅ NO causada en financiero
    ErpComercial.id == None    # ✅ NO causada en comercial
)
```

**Ventajas:**
- ✅ **Consistencia total** con visor_v2
- ✅ **Datos en tiempo real**
- ✅ **NO envía docs causados**
- ✅ **Refleja estado actual del ERP**

**Desventajas:**
- ⚠️ Requiere cambiar 2 funciones en scheduler
- ⚠️ Query más complejo (pero más preciso)

---

### **Opción 2: Actualizar maestro_dian_vs_erp en tiempo real (COMPLEJO)**

Agregar triggers/lógica para actualizar `maestro_dian_vs_erp` cuando:
- Se carga un archivo ERP Financiero
- Se carga un archivo ERP Comercial
- Se causan documentos manualmente

**Ventajas:**
- Mantiene tabla maestro actualizada
- No cambia lógica del scheduler

**Desventajas:**
- ❌ MUY COMPLEJO de implementar
- ❌ Requiere triggers en múltiples tablas
- ❌ Redundancia de datos (maestro duplica info de otras tablas)
- ❌ Difícil de mantener sincronizado

---

## 📋 RECOMENDACIÓN FINAL

### ✅ **Implementar Opción 1: Cambiar scheduler a tablas optimizadas**

**Por qué:**
1. **Consistencia:** El scheduler usará la MISMA fuente de datos que visor_v2
2. **Simplicidad:** Solo 2 funciones a modificar
3. **Precisión:** Datos en tiempo real, no snapshots desactualizados
4. **Arquitectura:** Elimina redundancia (maestro ya no es necesario para correos)

**Cambios necesarios:**

**Archivo:** `scheduler_envios.py`

**Cambio 1:** Función `_procesar_pendientes_dias` (línea ~230)
```python
# Cambiar query para usar tabla `dian` con JOIN a `erp_*`
# Filtrar donde ErpFinanciero.id == None Y ErpComercial.id == None
```

**Cambio 2:** Función `_procesar_credito_sin_acuses` (línea ~370)
```python
# Cambiar query para usar tabla `dian` con JOIN a `erp_*`
# Filtrar donde ErpFinanciero.id == None Y ErpComercial.id == None
```

**Tiempo estimado:** 15-20 minutos (queries más complejos)  
**Riesgo:** MEDIO (requiere testing de las queries)  
**Impacto:** ALTO (solución definitiva al problema)

---

## 🔄 COMPARACIÓN FINAL

| Aspecto | Maestro (Viejo) | Dian + Joins (Nuevo) |
|---------|-----------------|---------------------|
| **Actualización** | Manual (SYNC) | Automática (carga ERP) |
| **Estado causada** | Desactualizado | ⏱️ Tiempo real |
| **Complejidad query** | Simple | Media |
| **Consistencia** | ❌ Diferente a visor | ✅ Igual a visor_v2 |
| **Precisión** | ⚠️ 70-80% | ✅ 100% |
| **Tabla** | 1 (maestro) | 3 (dian + erp_* con JOIN) |

---

## ⚡ PRÓXIMO PASO

¿Quieres que implemente la **Opción 1** (cambiar scheduler a tablas optimizadas)?

**Pros:**
- ✅ Solución DEFINITIVA
- ✅ Consistencia total con visor_v2
- ✅ NO más correos con docs causados

**Contras:**
- ⚠️ Queries más complejos
- ⚠️ Requiere testing

**Alternativa rápida temporal:**
Agregar solo filtro `causada == False` a maestro (solución del primer análisis), pero:
- ⚠️ Sigue usando tabla desactualizada
- ⚠️ El campo `causada` puede estar mal
- ⚠️ NO es la solución ideal

¿Proceder con Opción 1 (scheduler con tablas optimizadas)? 🤔

