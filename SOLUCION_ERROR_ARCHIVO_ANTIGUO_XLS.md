# 🐛 PROBLEMA: Error de archivo antiguo .xls al cargar archivos nuevos

**Fecha**: 18 Febrero 2026  
**Usuario**: Usuario del sistema  
**Módulo**: DIAN vs ERP - Módulo de carga de archivos

---

## 📋 **Descripción del Problema**

Cuando el usuario intenta cargar archivos nuevos (ej: `acuses 2.xlsx`), el sistema muestra un error mencionando un archivo **antiguo** que no fue el que se subió:

```
❌ ❌ Error: ⚠️ ARCHIVOS CON FORMATO NO ACEPTADO en 'acuses':
• SiesaE-Invoicing-Documento-Recepcion-20260218154422.xls (formato .xls)
```

**Pero el usuario subió**: `acuses 2.xlsx` (formato válido .xlsx) ✅

---

## 🔍 **Causa Raíz Identificada**

**Problema**: El sistema NO limpia las carpetas `uploads/` antes de procesar archivos nuevos.

**Flujo del Error**:
1. El usuario sube `acuses 2.xlsx` → Se guarda en `uploads/acuses/`
2. Pero el archivo viejo `SiesaE-Invoicing-Documento-Recepcion-20260218154422.xls` **TODAVÍA ESTÁ AHÍ**
3. Al procesar, el sistema busca **TODOS** los archivos en la carpeta:
   ```python
   archivos_invalidos = list(path.glob("*.xls"))  # Encuentra el .xls viejo
   ```
4. Encuentra el archivo `.xls` antiguo → Lanza error de formato

**Ubicación del código**: `modules/dian_vs_erp/routes.py` líneas 240-290 (función `latest_file`)

---

## ✅ **Solución Definitiva**

### **OPCIÓN 1: Limpiar manualmente las carpetas uploads** (INMEDIATO)

**1. Ejecutar script de limpieza:**
```powershell
cd "D:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
python limpiar_uploads_dian.py
```

Cuando pregunte: **Escribe `si` y presiona Enter**

**2. Verificar que se eliminaron los archivos:**
```powershell
ls uploads\dian\*.xls
ls uploads\acuses\*.xls
ls uploads\erp_fn\*.xls
ls uploads\erp_cm\*.xls
```

Si no hay resultados → ✅ Carpetas limpias

**3. Ahora puedes cargar tus archivos nuevos:**
- Accede a: http://127.0.0.1:8099/dian_vs_erp/cargar_archivos
- Carga tus archivos .xlsx
- Procesar normalmente

---

### **OPCIÓN 2: Modificar el código para auto-limpiar** (PERMANENTE)

**Mejorar la función `subir_archivos()` para limpiar carpetas antes de procesar:**

1. Abrir archivo: `modules/dian_vs_erp/routes.py`
2. Buscar la función `subir_archivos()` (línea 921)
3. Agregar esta función ANTES de guardar los archivos nuevos:

```python
# NUEVA FUNCIÓN (agregar en línea 920, antes de @dian_vs_erp_bp.route)
def limpiar_carpetas_uploads():
    """Limpia las carpetas uploads antes de procesar archivos nuevos"""
    import shutil
    
    for folder in UPLOADS.values():
        if folder.exists():
            # Eliminar todos los archivos de la carpeta
            for archivo in folder.glob("*.*"):
                try:
                    archivo.unlink()
                    print(f"   🧹 Eliminado archivo antiguo: {archivo.name}")
                except Exception as e:
                    print(f"   ⚠️  No se pudo eliminar {archivo.name}: {e}")

# Luego MODIFICAR la función subir_archivos (línea 923):
@dian_vs_erp_bp.route('/subir_archivos', methods=['POST'])
@dian_vs_erp_bp.route('/api/subir_archivos', methods=['POST'])
def subir_archivos():
    """..."""
    try:
        # Validar sesión
        if 'usuario_id' not in session or 'usuario' not in session:
            return jsonify({"error": "Sesión no válida", "redirect": "/login"}), 401
        
        archivos_guardados = []
        
        print("=" * 80)
        print("🧹 PASO 0: LIMPIANDO CARPETAS ANTIGUAS")  # ⬅️ NUEVO
        print("=" * 80)
        limpiar_carpetas_uploads()  # ⬅️ NUEVO
        
        print("\n" + "=" * 80)
        print("📤 PASO 1: GUARDANDO ARCHIVOS EN DISCO")
        print("=" * 80)
        
        # ... resto del código igual
```

**Ventajas de esta solución:**
- ✅ Limpieza automática al subir archivos nuevos
- ✅ No requiere intervención manual del usuario
- ✅ Evita conflictos con archivos antiguos
- ✅ Mantiene las carpetas organizadas

---

## 🔧 **Solución de Emergencia (Manual)**

Si no puedes ejecutar el script o modificar el código, elimina manualmente los archivos antiguos:

**1. Abrir carpetas:**
- `D:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\uploads\dian\`
- `D:\...\uploads\acuses\`
- `D:\...\uploads\erp_fn\`
- `D:\...\uploads\erp_cm\`
- `D:\...\uploads\rg_erp_er\`

**2. Eliminar todos los archivos `.xls` (Excel 97-2003):**
- Buscar archivos con extensión `.xls`
- Eliminarlos TODOS

**3. Verificar que solo queden archivos nuevos o nada:**
- La carpeta puede estar vacía (OK)
- O tener archivos `.xlsx` / `.xlsm` / `.csv` (OK)
- **NO debe tener archivos `.xls`** ❌

**4. Ahora puedes cargar archivos nuevos**

---

## 📝 **Para el Desarrollador**

**Archivos relevantes:**
- `modules/dian_vs_erp/routes.py` (líneas 240-290): Función `latest_file()` que valida formatos
- `modules/dian_vs_erp/routes.py` (líneas 921-985): Función `subir_archivos()` que guarda archivos
- `limpiar_uploads_dian.py`: Script de limpieza manual creado hoy

**Mejora implementada HOY (18 Feb 2026):**
- ✅ Creado script `limpiar_uploads_dian.py` para limpieza manual
- ✅ Documentado el problema y la causa raíz
- ⏳ Pendiente: Implementar auto-limpieza en el código (OPCIÓN 2)

**Próximos pasos recomendados:**
1. Implementar limpieza automática en `subir_archivos()` (ver OPCIÓN 2)
2. Agregar logging para saber qué archivos se eliminan
3. Considerar agregar fecha/hora a los archivos para historial
4. O mover archivos antiguos a carpeta `uploads/backup/` en lugar de eliminar

---

## ✅ **Comprobación**

Después de aplicar la solución, verifica:

1. **Limpiar carpetas** (manual o script)
2. **Cargar archivos nuevos** (.xlsx, .xlsm, .csv)
3. **Verificar que procese correctamente** sin errores de formato
4. **Revisar logs del servidor** para confirmar archivos procesados

**Log esperado:**
```
📤 PASO 1: GUARDANDO ARCHIVOS EN DISCO
💾 Guardando acuses: acuses 2.xlsx
   ✅ Guardado: D:\...\uploads\acuses\acuses 2.xlsx
⚙️ PASO 2: PROCESANDO DESDE DISCO
📂 Buscando archivo ACUSES...
✅ Archivo encontrado: acuses 2.xlsx
✅ Excel leído: 12,345 filas
```

**NO debe aparecer error de archivo .xls**

---

## 🔗 **Referencias**

- **Documentación previa**: `DOCUMENTACION_PROBLEMA_ESTADO_APROBACION.md`
- **Código fuente**: `modules/dian_vs_erp/routes.py`
- **Script de limpieza**: `limpiar_uploads_dian.py`
- **Logs del sistema**: Terminal del servidor Flask (puerto 8099)

---

**Estado**: ✅ **SOLUCIONADO** (Pendiente aplicar solución)  
**Autor**: GitHub Copilot  
**Fecha**: 18 Febrero 2026
