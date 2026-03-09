# PROCESO DE CARGA LIMPIA - Febrero 23, 2026

## ✅ PASOS COMPLETADOS:
1. ✅ Tablas borradas (maestro_dian_vs_erp vacía)
2. ✅ Servidor cerrado (código viejo eliminado de memoria)

## 📋 PASOS SIGUIENTES:

### PASO 1: Reiniciar servidor con código actualizado
```powershell
# En terminal PowerShell desde la carpeta raíz:
.\1_iniciar_gestor.bat
```

**ESPERAR** a ver el mensaje:
```
 * Running on http://127.0.0.1:8099
 * Running on http://192.168.X.X:8099
```

### PASO 2: Cargar archivos por navegador
1. Abrir navegador: http://localhost:8099/dian_vs_erp/
2. Click en **"Subir Archivos"**
3. Seleccionar archivos:
   - **DIAN**: `uploads\dian\Dian.xlsx` (23/02/2026 13:25)
   - **ERP Comercial**: `uploads\erp_cm\ERP_comercial_23022026.xlsx`
   - **ERP Financiero**: `uploads\erp_fn\erp_financiero_23022026.xlsx`
   - **Acuses** (si aplica)
4. Click **"Subir y Procesar"**
5. **ESPERAR** hasta ver mensaje de éxito (puede tardar 1-2 minutos)

### PASO 3: Verificación inmediata (ejecutar script)
```powershell
python verificar_carga_exitosa.py
```

Este script verificará:
- ✅ Cantidad de registros cargados
- ✅ Prefijos correctos (6841, FEVA, 1FEA, etc.)
- ✅ Folios correctos (NO "0", NO NULL)
- ✅ Totales correctos (NO 0.00)
- ✅ Fechas correctas (NO todas 2026-02-23)

## 🎯 RESULTADO ESPERADO:

```
VERIFICACIÓN POST-CARGA
================================================================================
✅ Total registros DIAN: 66,276 (esperado: ~66,000)
✅ Registros con prefijo válido: 66,276 (100%)
✅ Registros con folio válido: 66,276 (100%)
✅ Registros con valor > 0: 66,276 (100%)
✅ Registros con fecha correcta: 66,276 (100%)

MUESTRA DE DATOS (primeros 5 registros):
ID 1: NIT=860025900, Prefijo='6841', Folio='896952', Total=1548683.00 ✅
ID 2: NIT=860000157, Prefijo='FEVA', Folio='49', Total=152877.00 ✅
ID 3: NIT=860000157, Prefijo='FEVA', Folio='42', Total=152877.00 ✅
```

## ⚠️ SI HAY ERRORES:

**Si prefijos siguen NULL o vacíos:**
→ El servidor NO se reinició correctamente
→ Solución: Cerrar TODO Python y reiniciar

**Si folios siguen "0":**
→ Mismo problema, reiniciar servidor

**Si todo sigue mal:**
→ Ejecutar: `python diagnostico_completo.py`
→ Me compartes resultado
