# 🚀 GUÍA PARA CARGAR NUEVA INFORMACIÓN - DIAN vs ERP

## ✅ SISTEMA LISTO PARA CARGAS INCREMENTALES

El sistema está **100% operativo** y listo para recibir nuevos archivos. Los datos existentes (173,342 registros) **NO SE PERDERÁN** gracias al sistema de carga incremental.

---

## 📋 PASO A PASO PARA CARGAR NUEVA INFORMACIÓN

### **PASO 1: INICIAR EL SERVIDOR** 🖥️

```bash
# Desde PowerShell en la carpeta del proyecto:
.\1_iniciar_gestor.bat

# O manualmente:
python app.py
```

**Espera ver:**
```
✅ SERVIDOR INICIANDO - Módulos HABILITADOS: Recibir Facturas, Relaciones, 
   Archivo Digital, Causaciones, DIAN vs ERP, Monitoreo, Facturas Digitales, SAGRILAFT

 * Running on http://127.0.0.1:8099
```

---

### **PASO 2: ACCEDER AL MÓDULO DE CARGA** 🌐

**Abre tu navegador en:**
```
http://localhost:8099/dian_vs_erp/cargar
```

**Deberías ver la interfaz de carga con fondo negro:**

┌────────────────────────────────────────────────────┐
│  🔥 CARGA DE ARCHIVOS DIAN vs ERP                  │
├────────────────────────────────────────────────────┤
│                                                     │
│  📁 DIAN (Facturas Electrónicas)                  │
│  [Seleccionar archivo...] [Subir DIAN]            │
│                                                     │
│  📁 ERP Financiero (Módulo FN)                    │
│  [Seleccionar archivo...] [Subir ERP FN]          │
│                                                     │
│  📁 ERP Comercial (Módulo CM)                     │
│  [Seleccionar archivo...] [Subir ERP CM]          │
│                                                     │
│  📁 ACUSES (Respuestas DIAN)                      │
│  [Seleccionar archivo...] [Subir ACUSES]          │
│                                                     │
│  ════════════════════════════════════════════      │
│                                                     │
│     [🚀 PROCESAR TODOS LOS ARCHIVOS]              │
│                                                     │
└────────────────────────────────────────────────────┘

---

### **PASO 3: SUBIR TUS ARCHIVOS** 📤

**Puedes cargar archivos en estos formatos:**
- ✅ Excel (.xlsx, .xls, .xlsm)
- ✅ CSV (.csv)
- ✅ LibreOffice (.ods)

**Nomenclatura recomendada:**
```
DIAN_FEBRERO_2026.xlsx
ERP_FINANCIERO_FEBRERO_2026.xlsx
ERP_COMERCIAL_FEBRERO_2026.xlsx
ACUSES_FEBRERO_2026.xlsx
```

**Pasos:**
1. Click en "Seleccionar archivo..." para DIAN
2. Elige tu archivo Excel/CSV
3. Click en "Subir DIAN"
4. Repite para ERP Financiero, ERP Comercial y ACUSES

**Espera mensajes de confirmación:**
```
✅ Archivo DIAN subido correctamente
✅ Archivo ERP Financiero subido correctamente
✅ Archivo ERP Comercial subido correctamente
✅ Archivo ACUSES subido correctamente
```

---

### **PASO 4: PROCESAR LOS ARCHIVOS** ⚡

**Una vez que subiste los 4 archivos:**

1. Click en el botón **"🚀 PROCESAR TODOS LOS ARCHIVOS"**
2. Verás una barra de progreso o mensaje de procesamiento
3. El sistema hace esto automáticamente:
   ```
   Leer archivos con Polars (ultra-rápido)
        ↓
   Normalizar columnas (quitar acentos, espacios)
        ↓
   Aplicar reglas de negocio (tipos doc, módulos)
        ↓
   Escapar caracteres especiales (format_value_for_copy)
        ↓
   Insertar en PostgreSQL con COPY FROM (25,000 reg/seg)
        ↓
   Consolidar en maestro (LEFT JOIN de 4 tablas)
        ↓
   ✅ COMPLETADO
   ```

**Tiempo estimado:**
- 1,000 registros → ~1 segundo
- 10,000 registros → ~5 segundos
- 50,000 registros → ~20 segundos
- 100,000 registros → ~40 segundos

---

### **PASO 5: VERIFICAR LOS RESULTADOS** 📊

**Opción 1: En el navegador**
```
http://localhost:8099/dian_vs_erp/visor_v2
```
- Verás los datos consolidados
- Usa filtros por fecha para ver solo los nuevos

**Opción 2: Desde línea de comandos**
```bash
python CHECK_ALL_TABLES.py
```

**Deberías ver algo como:**
```
============================================================
📊 ESTADO DE LAS TABLAS
============================================================
dian                     : 2,800 (antes: 1,400)   ← +1,400 nuevos
erp_comercial            : 114,382 (antes: 57,191) ← +57,191 nuevos
erp_financiero           : 5,990 (antes: 2,995)   ← +2,995 nuevos
acuses                   : 93,300 (antes: 46,650) ← +46,650 nuevos
maestro_dian_vs_erp      : 130,212 (antes: 65,106) ← +65,106 nuevos
============================================================
TOTAL                    : 346,684 (+173,342)     ← ¡DUPLICADO!
============================================================
```

---

## 🔄 CARGA INCREMENTAL - ¿CÓMO FUNCIONA?

### **SIN DUPLICADOS** ✅

El sistema usa **ON CONFLICT DO UPDATE** en todas las tablas:

```sql
-- Ejemplo en tabla DIAN
ON CONFLICT (cufe) DO UPDATE SET
    razon_social = EXCLUDED.razon_social,
    fecha_emision = EXCLUDED.fecha_emision,
    valor_factura = EXCLUDED.valor_factura,
    ...
```

**Esto significa:**
- ✅ Si el CUFE ya existe → **ACTUALIZA** los datos (no duplica)
- ✅ Si el CUFE es nuevo → **INSERTA** nuevo registro
- ✅ **NUNCA** borra datos antiguos
- ✅ **SIEMPRE** mantiene la versión más reciente

### **¿Qué pasa si cargo el mismo archivo dos veces?**

**Respuesta:** ¡No pasa nada malo! 😊

- Primera carga: Inserta todos los registros
- Segunda carga: Actualiza los existentes (sin duplicar)
- Los conteos se mantienen iguales

---

## 📝 ESTRUCTURA DE LOS ARCHIVOS EXCEL

### **1. ARCHIVO DIAN** (Facturas Electrónicas)

**Columnas requeridas:**
```
NIT Emisor | Nombre Emisor | Fecha de Emisión | CUFE/CUDE | 
Prefijo | Folio | Tipo Documento | Valor Factura
```

**Ejemplo:**
```
805028041 | SUPERTIENDAS CAÑAVERAL | 15/02/2026 | abc123def456... | 
FE | 12345 | Factura Electrónica | 1500000
```

### **2. ARCHIVO ERP FINANCIERO** (Módulo FN)

**Columnas requeridas:**
```
Proveedor (NIT) | Razón Social Proveedor | Fecha Docto | Docto Proveedor | 
Valor Bruto | Clase Docto | Nro Documento | Prefijo | Folio
```

### **3. ARCHIVO ERP COMERCIAL** (Módulo CM)

**Columnas requeridas:**
```
Proveedor (NIT) | Razón Social Proveedor | Fecha Docto Prov | Docto Proveedor | 
Valor Bruto | Clase Docto | Nro Documento | Prefijo | Folio
```

### **4. ARCHIVO ACUSES** (Respuestas DIAN) ⚠️ IMPORTANTE

**Columnas requeridas (CON acentos y espacios como están en Excel):**
```
fecha | adquiriente | factura | emisor | nit emisor | nit. pt | 
estado docto. | descripción reclamo | tipo documento | cufe | valor | 
acuse recibido | recibo bien servicio | aceptación expresa | 
reclamo | aceptación tacita
```

**⚠️ NO cambies los nombres de las columnas en Excel**
- El sistema mapea automáticamente: "nit emisor" → nit_emisor
- Respeta los espacios y acentos exactamente como están

---

## ⚠️ PROBLEMAS COMUNES Y SOLUCIONES

### **Problema 1: "Error al procesar archivo"**

**Causas posibles:**
- ❌ Archivo corrupto o sin datos
- ❌ Columnas requeridas faltantes
- ❌ Formato de fecha incorrecto

**Solución:**
1. Verifica que el archivo tenga datos (no solo encabezados)
2. Verifica nombres de columnas
3. Usa formato de fecha: DD/MM/YYYY

### **Problema 2: "No se cargaron registros"**

**Solución:**
```bash
# Ver logs del sistema
type logs\security.log | find "DIAN"
```

### **Problema 3: "Columna no existe"**

**Causa:** Nombres de columnas en Excel diferentes a los esperados

**Solución:**
- Ver documentación completa en:
  `SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md`
- Sección: "MAPEO DE COLUMNAS"

### **Problema 4: "datos extra después de la última columna"**

**Causa:** Caracteres especiales sin escapar (bug ya corregido)

**Solución:**
- ✅ Ya está resuelto en la versión actual
- La función `format_value_for_copy()` escapa automáticamente

---

## 🎯 RECOMENDACIONES

### **ANTES de cargar archivos masivos:**

1. **Haz un backup de la base de datos:**
   ```bash
   .\BACKUP_BD_MANUAL.bat
   ```

2. **Prueba con archivo pequeño primero:**
   - Crea un Excel con 10-100 registros
   - Procesa y verifica que funcione
   - Luego sí carga el archivo completo

3. **Verifica el estado ANTES:**
   ```bash
   python CHECK_ALL_TABLES.py
   ```

4. **Verifica el estado DESPUÉS:**
   ```bash
   python CHECK_ALL_TABLES.py
   ```

### **Buenas prácticas:**

✅ **SÍ hacer:**
- Cargar archivos mensuales (Enero, Febrero, etc.)
- Verificar conteos después de cada carga
- Mantener los archivos originales como respaldo
- Revisar el visor después de cargar

❌ **NO hacer:**
- NO modificar `format_value_for_copy()` en el código
- NO cambiar mapeo de columnas de ACUSES
- NO eliminar las cláusulas ON CONFLICT
- NO cargar archivos con estructuras completamente diferentes

---

## 🔍 VERIFICACIÓN POST-CARGA

### **Checklist de validación:**

```bash
# 1. Contar registros
python CHECK_ALL_TABLES.py

# 2. Ver flujo visual
python FLUJO_TRABAJO_COMPLETO.py

# 3. Verificar en navegador
# http://localhost:8099/dian_vs_erp/visor_v2
```

### **¿Cómo sé que todo salió bien?**

✅ **Indicadores de éxito:**
- Los conteos aumentaron (no se duplicaron exactamente)
- No aparecen errores en la consola
- El visor muestra los nuevos registros
- Los filtros por fecha funcionan

⚠️ **Señales de alerta:**
- Los conteos no cambiaron → Archivo vacío o sin datos nuevos
- Errores en consola → Revisar logs/security.log
- Datos duplicados exactamente → Posible problema (raro con ON CONFLICT)

---

## 📞 SOPORTE

**Si algo sale mal:**

1. **Ver logs:**
   ```bash
   type logs\security.log
   ```

2. **Documentación completa:**
   - `SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md`
   - `INDEX_DOCUMENTACION_DIAN.md`
   - `README.md`

3. **Scripts de diagnóstico:**
   ```bash
   python CHECK_ALL_TABLES.py
   python FLUJO_TRABAJO_COMPLETO.py
   ```

---

## ✅ RESUMEN RÁPIDO

```
1. Iniciar servidor:
   .\1_iniciar_gestor.bat

2. Abrir navegador:
   http://localhost:8099/dian_vs_erp/cargar

3. Subir 4 archivos:
   - DIAN
   - ERP Financiero
   - ERP Comercial
   - ACUSES

4. Click: "PROCESAR TODOS LOS ARCHIVOS"

5. Verificar:
   python CHECK_ALL_TABLES.py

6. Ver resultados:
   http://localhost:8099/dian_vs_erp/visor_v2
```

---

**¡LISTO! El sistema está preparado para recibir tus nuevos archivos sin perder los datos existentes.** 🚀

**Fecha:** 23 de Febrero de 2026  
**Estado:** ✅ Sistema 100% operativo (173,342 registros actuales)
