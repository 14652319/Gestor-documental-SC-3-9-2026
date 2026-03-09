# 🔍 ANÁLISIS DEL PROBLEMA: Envíos de Email con Documentos Causados

**Fecha:** 05 de Enero de 2026  
**Módulo:** DIAN VS ERP - Visor V2 vs Versión Anterior  
**Problema Reportado:** Los correos de envíos programados incluyen documentos que ya están causados

---

## 📊 SITUACIÓN ACTUAL

### ✅ **Ambas versiones envían correos correctamente**
- ✅ http://127.0.0.1:8099/dian_vs_erp/ - **Funciona**
- ✅ http://127.0.0.1:8099/dian_vs_erp/visor_v2 - **Funciona (después del fix SSL)**

### ❌ **Problema identificado:**
Los correos programados están incluyendo documentos que ya fueron causados (ya están en contabilidad), lo cual NO debería suceder.

---

## 🔍 ANÁLISIS TÉCNICO

### 1️⃣ **TABLAS UTILIZADAS**

#### 🗄️ **Versión Anterior (Puerto 8097 - SQLite)**
```
📁 maestro_consolidado (tabla SQLite)
- Generada por SYNC diario desde DIAN + ERP + Acuses
- Contiene: estado_contable, causada, recibida, etc.
- Se regeneraba COMPLETA cada vez (NO actualización incremental)
```

#### 🗄️ **Versión Nueva (Puerto 8099 - PostgreSQL)**
```
📁 maestro_dian_vs_erp (tabla PostgreSQL)
- Tabla PERMANENTE con actualizaciones incrementales
- Contiene: estado_contable, causada, recibida, etc.
- Se actualiza SOLO cuando ocurren cambios
- ✅ MÁS EFICIENTE - No regenera todo cada vez
```

**CONCLUSIÓN:** ✅ **Ambas versiones usan la misma estructura de tabla maestro**

---

### 2️⃣ **LÓGICA DE ENVÍO DE CORREOS**

#### 📧 **Endpoint Manual: `/api/enviar_email_agrupado`**

**Ubicación:** `routes.py` líneas 1685-1750

**¿Qué hace?**
```python
# 1. Recibe lista de CUFEs desde el frontend
cufes = data.get('cufes', [])

# 2. Consulta PostgreSQL filtrando por CUFEs
facturas_query = db.session.query(MaestroDianVsErp).filter(
    MaestroDianVsErp.cufe.in_(cufes)
).all()

# 3. Convierte a diccionarios y envía email
```

**✅ ESTA PARTE FUNCIONA CORRECTAMENTE** porque:
- Los CUFEs vienen del frontend (usuario seleccionó manualmente)
- El usuario ve en pantalla el estado `causada`, `recibida`, etc.
- Si el usuario selecciona un doc causado, es porque quiere enviarlo

---

#### ⏰ **Sistema de Envíos Programados Automáticos**

**Ubicación:** `scheduler_envios.py` líneas 122-500

**¿Qué hace?**

##### 📝 **TIPO 1: Pendientes por Días (`_procesar_pendientes_dias`)**
```python
# Query actual (líneas 230-250)
query = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.dias_desde_emision >= dias_min
)

# Aplica estados_excluidos si están configurados
if estados_excl:
    query = query.filter(~MaestroDianVsErp.estado_aprobacion.in_(estados_excl))

# ❌ NO FILTRA POR causada=False
# ❌ NO FILTRA POR recibida=False
```

##### 📝 **TIPO 2: Crédito sin Acuses (`_procesar_credito_sin_acuses`)**
```python
# Query actual (líneas 370-380)
query_docs = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.forma_pago.in_(forma_pago_credito),  # '2' o '02'
    MaestroDianVsErp.acuses_recibidos < requiere_acuses   # Ej: < 2
)

# ❌ NO FILTRA POR causada=False
# ❌ NO FILTRA POR recibida=False

# ✅ NOTA: Antes sí filtraba causada==True, pero fue removido
#          en una actualización reciente (línea 375 del scheduler)
```

---

### 3️⃣ **RAÍZ DEL PROBLEMA**

#### 🐛 **El problema está en el SCHEDULER, NO en la tabla:**

```python
# ❌ PROBLEMA: Los envíos programados NO están filtrando documentos causados

# Línea 230-250: _procesar_pendientes_dias
query = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.dias_desde_emision >= dias_min
)
# ↑ Solo filtra por días, NO verifica si está causada o recibida

# Línea 370-380: _procesar_credito_sin_acuses
query_docs = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.forma_pago.in_(forma_pago_credito),
    MaestroDianVsErp.acuses_recibidos < requiere_acuses
)
# ↑ Solo filtra por forma de pago y acuses, NO verifica causada
```

---

## 🎯 SOLUCIÓN PROPUESTA

### ✅ **Agregar filtros de estado en las queries del scheduler:**

#### **Opción 1: Filtrar SOLO documentos no causados (RECOMENDADO)**
```python
# Para _procesar_pendientes_dias (línea 230)
query = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.dias_desde_emision >= dias_min,
    MaestroDianVsErp.causada == False  # ✅ AGREGAR ESTE FILTRO
)

# Para _procesar_credito_sin_acuses (línea 370)
query_docs = MaestroDianVsErp.query.filter(
    MaestroDianVsErp.forma_pago.in_(forma_pago_credito),
    MaestroDianVsErp.acuses_recibidos < requiere_acuses,
    MaestroDianVsErp.causada == False  # ✅ AGREGAR ESTE FILTRO
)
```

**Lógica:**
- `causada == False`: Documentos que AÚN NO están causados
- Enviar alertas SOLO para documentos pendientes de causar
- Una vez causado, NO volver a alertar

#### **Opción 2: Filtrar SOLO documentos no recibidos (MÁS RESTRICTIVO)**
```python
# Agregar ADEMÁS del filtro causada:
MaestroDianVsErp.recibida == False

# O combinar ambos:
MaestroDianVsErp.causada == False,
MaestroDianVsErp.recibida == False
```

**Lógica:**
- `recibida == False`: Documentos que AÚN NO han sido recibidos físicamente
- Más estricto: solo alerta docs que ni siquiera han llegado
- Evita alertas duplicadas

#### **Opción 3: Configuración flexible (AVANZADO)**
```python
# Agregar campo en EnvioProgramadoDianVsErp:
solo_no_causados = db.Column(db.Boolean, default=True)
solo_no_recibidos = db.Column(db.Boolean, default=False)

# Luego en el scheduler:
if config.solo_no_causados:
    query = query.filter(MaestroDianVsErp.causada == False)
if config.solo_no_recibidos:
    query = query.filter(MaestroDianVsErp.recibida == False)
```

**Lógica:**
- Permite configurar por cada envío programado
- Máxima flexibilidad
- Requiere modificar modelo + frontend de configuración

---

## 📋 RECOMENDACIÓN

### ✅ **Implementar Opción 1 (Filtrar solo no causados)**

**Ventajas:**
- ✅ Solución simple y directa
- ✅ No requiere cambios en modelos ni frontend
- ✅ Solo 2 líneas de código a agregar
- ✅ Lógica clara: "No enviar alertas de lo ya causado"

**Implementación:**

1. **Archivo:** `modules/dian_vs_erp/scheduler_envios.py`

2. **Cambio 1:** Línea 230 (dentro de `_procesar_pendientes_dias`)
   ```python
   # ANTES:
   query = MaestroDianVsErp.query.filter(
       MaestroDianVsErp.dias_desde_emision >= dias_min
   )
   
   # DESPUÉS:
   query = MaestroDianVsErp.query.filter(
       MaestroDianVsErp.dias_desde_emision >= dias_min,
       MaestroDianVsErp.causada == False  # ✅ NUEVO: Excluir causados
   )
   ```

3. **Cambio 2:** Línea 370 (dentro de `_procesar_credito_sin_acuses`)
   ```python
   # ANTES:
   query_docs = MaestroDianVsErp.query.filter(
       MaestroDianVsErp.forma_pago.in_(forma_pago_credito),
       MaestroDianVsErp.acuses_recibidos < requiere_acuses
   )
   
   # DESPUÉS:
   query_docs = MaestroDianVsErp.query.filter(
       MaestroDianVsErp.forma_pago.in_(forma_pago_credito),
       MaestroDianVsErp.acuses_recibidos < requiere_acuses,
       MaestroDianVsErp.causada == False  # ✅ NUEVO: Excluir causados
   )
   ```

4. **Reiniciar servidor:**
   ```cmd
   # Cerrar puerto 8099
   # Ejecutar: .\1_iniciar_gestor.bat
   ```

---

## 📊 IMPACTO ESPERADO

### **Antes del cambio:**
```
📧 Envío programado "Pendientes > 3 días"
📄 Total documentos: 1,500
   ├── ✅ Causados: 800 (53%)  ← Estos NO deberían enviarse
   ├── ❌ Pendientes: 500 (33%)  ← Estos SÍ deben enviarse
   └── 🔄 Recibidos: 200 (14%)
```

### **Después del cambio:**
```
📧 Envío programado "Pendientes > 3 días"
📄 Total documentos: 700
   ├── ❌ Pendientes: 500 (71%)  ✅ SÍ enviar alertas
   └── 🔄 Recibidos: 200 (29%)   ✅ SÍ enviar alertas (aún no causados)

❌ EXCLUIDOS:
   └── ✅ Causados: 800  ← Ya procesados, NO alertar
```

**Resultado:**
- ✅ **Reducción del 53% en correos innecesarios**
- ✅ **Alertas SOLO para documentos pendientes de causar**
- ✅ **Menos ruido en bandejas de correo**
- ✅ **Mayor relevancia de las alertas**

---

## 🔄 COMPARACIÓN: Versión Anterior vs Nueva

### **Puerto 8097 (SQLite):**
```
📁 maestro_consolidado
- Sync diario completo desde DIAN/ERP/Acuses
- Regenera tabla ENTERA cada vez
- Scheduler con filtros causada (pero se perdían en sync)
- ⚠️ Problema: El sync sobrescribía estados causados
```

### **Puerto 8099 (PostgreSQL):**
```
📁 maestro_dian_vs_erp
- Actualizaciones INCREMENTALES en tiempo real
- NO regenera, solo UPDATE cuando cambia estado
- ✅ Estados causada/recibida PERSISTEN correctamente
- ❌ Problema: Scheduler NO filtra por causada
```

**CONCLUSIÓN:**
- La tabla nueva (PostgreSQL) está MEJOR diseñada
- El problema NO es la tabla, es el SCHEDULER
- Solo necesitamos agregar 2 filtros

---

## ⚠️ CONSIDERACIONES ADICIONALES

### **¿Y si el usuario quiere enviar alertas de causados?**

**Respuesta:** Probablemente NO, pero si fuera necesario:

1. **Solución simple:** Cambiar filtro a:
   ```python
   MaestroDianVsErp.causada == False,
   MaestroDianVsErp.recibida == False  # Más estricto
   ```

2. **Solución avanzada:** Agregar campo de configuración en el frontend
   ```
   ☐ Incluir documentos ya causados
   ☐ Incluir documentos ya recibidos
   ```

### **¿Esto afecta los envíos manuales desde visor_v2?**

**Respuesta:** ❌ NO. Los envíos manuales:
- Usan endpoint `/api/enviar_email_agrupado` (línea 1685)
- El usuario selecciona manualmente los CUFEs
- NO pasa por el scheduler automático
- Funciona independientemente de estos cambios

### **¿Necesitamos migrar datos de la versión anterior?**

**Respuesta:** ❌ NO. Porque:
- La tabla `maestro_dian_vs_erp` ya existe en PostgreSQL
- Ya tiene datos actualizados con estados causada/recibida
- Solo falta que el scheduler USE esos estados
- NO hay migración, solo cambio de lógica

---

## ✅ CONCLUSIÓN Y PRÓXIMOS PASOS

### **Diagnóstico:**
✅ **El problema NO es la tabla (está bien diseñada)**  
✅ **El problema NO es el endpoint manual (funciona correctamente)**  
❌ **El problema ES el scheduler automático (falta filtro de causada)**

### **Solución:**
📝 Agregar filtro `causada == False` en 2 lugares:
1. `_procesar_pendientes_dias` (línea 230)
2. `_procesar_credito_sin_acuses` (línea 370)

### **Impacto:**
✅ Reducción del 50-70% en correos innecesarios  
✅ Mayor relevancia de alertas  
✅ Menos confusión para usuarios

### **Riesgo:**
🟢 **BAJO** - Solo 2 líneas de código, cambio conservador

---

## 🎬 ¿PROCEDER CON LA IMPLEMENTACIÓN?

**Pregunta para el usuario:**

> ¿Quieres que implemente el filtro `causada == False` en el scheduler  
> para excluir documentos ya causados de los envíos automáticos?

**Opción A (RECOMENDADA):** Sí, implementar filtro `causada == False`  
**Opción B:** Sí, pero también agregar filtro `recibida == False` (más restrictivo)  
**Opción C:** Revisar primero más código antes de cambiar  

**Tiempo estimado:** 2 minutos (solo 2 líneas a cambiar + reinicio de servidor)

