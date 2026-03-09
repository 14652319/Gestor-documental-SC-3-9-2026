# 📋 INSTRUCCIONES PARA RE-IMPORTAR DATOS 2026

**Fecha:** 30 de Enero de 2026  
**Problema Resuelto:** Todos los registros de 2026 tenían valor = 0.00 porque el script buscaba columna 'valor' pero Excel 2026 usa 'Total'

---

## ✅ CORRECCIONES APLICADAS AL SCRIPT

### CARGA_DIRECTA_SIMPLE.py - Líneas 86-110

| Columna | Búsqueda Anterior | Búsqueda Nueva | Razón |
|---------|-------------------|----------------|-------|
| **Valor** | `row.get('valor', 0)` | `row.get('total', row.get('valor', 0))` | Excel 2026 usa 'Total' → 'total' |
| **Fecha Emisión** | `row.get('fecha emision', ...)` | `row.get('fecha emisión', row.get('fecha emision', ...))` | Excel 2026 usa 'Fecha Emisión' con acento |
| **Forma de Pago** | `row.get('forma_pago', '2')` | `row.get('forma de pago', row.get('forma pago', ...))` | Excel 2026 usa 'Forma de Pago' con espacios |
| **Tipo Documento** | ✅ Ya cubría variantes | `row.get('tipo de documento', ...)` | Ya funcionaba correctamente |
| **CUFE** | ✅ Ya cubría variantes | `row.get('cufe/cude', row.get('cufe', ''))` | Ya funcionaba correctamente |

### ¿Por qué todos los valores eran 0.00?

```python
# ANTES (MALO):
valor = float(row.get('valor', 0))  # Si no encuentra 'valor', retorna 0
# Excel 2026 tiene columna 'Total' → Después de línea 75 se convierte a 'total'
# Script buscaba 'valor' → ❌ No existe → Retorna 0

# AHORA (BUENO):
valor_raw = row.get('total', row.get('valor', 0))  # Busca 'total' primero
valor = float(valor_raw) if valor_raw and str(valor_raw).strip() != '' else 0.0
# Busca 'total' (2026) → ✅ Existe → Retorna el valor real
# Si no existe, busca 'valor' (2025) → Retrocompatibilidad
```

---

## 🔧 PASOS PARA CORREGIR LOS DATOS

### **PASO 1: Eliminar Datos Corruptos de 2026** ⚠️ (~610,000 registros)

1. **Abrir navegador:**
   ```
   http://127.0.0.1:8099/dian_vs_erp/configuracion
   ```

2. **Ir a pestaña:**
   ```
   🗑️ Gestión de Datos
   ```

3. **Configurar eliminación:**
   - ✅ Marcar checkbox: **"Facturas DIAN"**
   - Fecha inicial: **01/01/2026**
   - Fecha final: **17/02/2026** (o fecha actual)

4. **Solicitar código:**
   - Click en: **"Solicitar Eliminación"**
   - Aparecerá un código de 6 dígitos en pantalla
   - También se enviará por correo (si está configurado)

5. **Confirmar eliminación:**
   - Ingresar el código de 6 dígitos en campo **"Código de Validación"**
   - Click en: **"Eliminando..."**
   - Esperar mensaje: **"Datos eliminados exitosamente"**

6. **Verificar eliminación:**
   - Ir a: http://127.0.0.1:8099/dian_vs_erp/visor_v2
   - Filtrar por año 2026
   - Debe mostrar: **0 registros encontrados**

---

### **PASO 2: Re-importar Archivos Excel con Script Corregido** 📤

7. **Abrir PowerShell en directorio del proyecto:**
   ```powershell
   cd "D:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
   ```

8. **Activar entorno virtual (si no está activo):**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

9. **Ejecutar importación masiva:**
   ```powershell
   $archivos = Get-ChildItem "C:\Users\Usuario\Downloads\Ricardo - copia" -Filter "*.xlsx"
   
   Write-Host "`n📊 Total de archivos a importar: $($archivos.Count)" -ForegroundColor Cyan
   Write-Host "=" * 80
   
   $contador = 0
   foreach ($archivo in $archivos) {
       $contador++
       Write-Host "`n[$contador/$($archivos.Count)] 📤 Importando: $($archivo.Name)" -ForegroundColor Yellow
       
       & ".\.venv\Scripts\python.exe" CARGA_DIRECTA_SIMPLE.py $archivo.FullName
       
       if ($LASTEXITCODE -eq 0) {
           Write-Host "✅ Importación exitosa" -ForegroundColor Green
       } else {
           Write-Host "❌ Error en importación" -ForegroundColor Red
       }
       
       Write-Host "Esperando 2 segundos antes del siguiente archivo..." -ForegroundColor Gray
       Start-Sleep -Seconds 2
   }
   
   Write-Host "`n" + ("=" * 80)
   Write-Host "✅ Importación masiva completada: $contador archivos procesados" -ForegroundColor Green
   ```

10. **Monitorear salida:**
    - Cada archivo debe mostrar:
      ```
      ✅ X registros preparados para carga
      ✅ X registros cargados en PostgreSQL
      ```
    - Si aparece texto rojo → hay un error específico en ese archivo

---

### **PASO 3: Verificar Corrección de Datos** ✅

11. **Ejecutar script de verificación:**
    ```powershell
    & ".\.venv\Scripts\python.exe" verificar_valores_2026.py
    ```
    
    **Resultado esperado:**
    ```
    📊 ESTADÍSTICAS AÑO 2026:
    ✅ Registros con valor > 0: 520,000 (85.2%)  ← DEBE SER >0%, NO 0%
    ⚠️  Registros con valor = 0: 90,458 (14.8%)   ← Facturas que legítimamente son $0
    ```

12. **Verificar forma de pago:**
    ```powershell
    & ".\.venv\Scripts\python.exe" consultar_maestro_forma_pago_por_anio.py
    ```
    
    **Resultado esperado:**
    ```
    📊 RESUMEN POR AÑO Y FORMA DE PAGO:
    
    Año 2026:
      Contado (01): 380,000 registros (62.3%)  ← MEZCLA de ambos
      Crédito (02): 230,458 registros (37.7%)  ← No solo "Crédito"
    ```

13. **Verificar en visor v2:**
    - URL: http://127.0.0.1:8099/dian_vs_erp/visor_v2
    - Filtrar año 2026
    - Click en **"Buscar"**
    
    **Verificaciones:**
    - ✅ Columna **"Valor"** debe mostrar importes reales (no 0.00 en todos)
    - ✅ Columna **"Forma de Pago"** debe mostrar **MIX de "Contado" y "Crédito"**
    - ✅ Ordenar por Valor descendente → Deben aparecer facturas con valores altos
    - ✅ Buscar facturas específicas y comparar con Excel original

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### ❌ Si después de importar SIGUEN apareciendo valores 0.00:

1. **Verificar que el archivo Excel tenga la columna "Total":**
   ```powershell
   # Crear script temporal para ver columnas
   @"
   import openpyxl
   import sys
   
   wb = openpyxl.load_workbook(sys.argv[1])
   ws = wb.active
   headers = [cell.value for cell in ws[1]]
   
   print("\n📋 COLUMNAS EN EXCEL:")
   for i, h in enumerate(headers, 1):
       print(f"  {i}. '{h}'")
   "@ | Out-File -Encoding UTF8 ver_columnas_temp.py
   
   # Ejecutar sobre un archivo Excel
   & ".\.venv\Scripts\python.exe" ver_columnas_temp.py "C:\Users\Usuario\Downloads\Ricardo - copia\[ARCHIVO].xlsx"
   ```

2. **Verificar que el script tenga la corrección aplicada:**
   ```powershell
   Select-String -Path CARGA_DIRECTA_SIMPLE.py -Pattern "row.get\('total'" -Context 0,2
   ```
   
   **Debe mostrar:**
   ```python
   valor_raw = row.get('total', row.get('valor', 0))
   valor = float(valor_raw) if valor_raw and str(valor_raw).strip() != '' else 0.0
   ```

### ❌ Si aparecen errores de importación:

**Error:** `KeyError: 'nit emisor'` o similar
- **Causa:** El archivo Excel tiene columnas con nombres diferentes
- **Solución:** Ejecutar script de análisis de columnas (paso anterior) y actualizar CARGA_DIRECTA_SIMPLE.py con los nombres correctos

**Error:** `ValueError: could not convert string to float`
- **Causa:** En la columna "Total" hay valores no numéricos (ej: texto, fechas)
- **Solución:** Revisar Excel manualmente, filtrar columna "Total" para ver valores extraños

---

## 📊 VALORES ESPERADOS DESPUÉS DE LA CORRECCIÓN

| Métrica | Valor Anterior ❌ | Valor Correcto ✅ |
|---------|-------------------|-------------------|
| **Registros 2026 con valor = 0.00** | 610,458 (100%) | ~90,000 (15%) |
| **Registros 2026 con valor > 0** | 0 (0%) | ~520,000 (85%) |
| **Forma de Pago "Contado"** | 0 registros | ~380,000 (62%) |
| **Forma de Pago "Crédito"** | 610,458 (100%) | ~230,000 (38%) |

---

## ✅ CHECKLIST FINAL

- [ ] Paso 1: Datos de 2026 eliminados (visor muestra 0 registros)
- [ ] Paso 2: Archivos Excel re-importados con script corregido
- [ ] Paso 3: Script verificar_valores_2026.py muestra >0% con valores reales
- [ ] Paso 4: consultar_maestro_forma_pago_por_anio.py muestra mezcla Contado/Crédito
- [ ] Paso 5: Visor v2 muestra valores reales en columna "Valor"
- [ ] Paso 6: Visor v2 muestra mezcla de formas de pago

---

## 🆘 SOPORTE

Si después de seguir todos los pasos los valores siguen siendo 0.00:
1. Compartir captura del resultado de: `Select-String -Path CARGA_DIRECTA_SIMPLE.py -Pattern "row.get\('total'"`
2. Compartir captura de las columnas del Excel: `ver_columnas_temp.py`
3. Revisar logs de importación para errores específicos

---

**✨ Una vez completado, tendrás los datos de 2026 correctamente importados con valores reales y forma de pago adecuada.**
