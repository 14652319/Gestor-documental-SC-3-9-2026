"""
🧹 LIMPIEZA COMPLETA - EMPEZAR DE CERO
========================================
Este script:
1. Elimina archivos de uploads/
2. Limpia todas las tablas de BD (DIAN, ERP, ACUSES, MAESTRO)
3. Deja el sistema listo para cargar archivos frescos
"""
import os
import shutil
import sys
from pathlib import Path

# Para colores en Windows
if sys.platform == 'win32':
    os.system('color')

print("=" * 80)
print("🧹 LIMPIEZA COMPLETA DEL SISTEMA")
print("=" * 80)

# 1️⃣ LIMPIAR CARPETAS DE UPLOADS
carpetas_uploads = [
    'uploads/dian',
    'uploads/erp_fn',
    'uploads/erp_cm',
    'uploads/errores',
    'uploads/acuses'
]

print("\n📂 LIMPIANDO CARPETAS DE UPLOADS...")
archivos_eliminados = 0

for carpeta in carpetas_uploads:
    if os.path.exists(carpeta):
        archivos = [f for f in os.listdir(carpeta) if os.path.isfile(os.path.join(carpeta, f))]
        for archivo in archivos:
            try:
                os.remove(os.path.join(carpeta, archivo))
                archivos_eliminados += 1
                print(f"   🗑️  {carpeta}/{archivo}")
            except Exception as e:
                print(f"   ❌ Error eliminando {archivo}: {e}")
    else:
        print(f"   ⚠️  Carpeta no existe: {carpeta}")

print(f"\n✅ {archivos_eliminados} archivos eliminados de uploads/")

# 2️⃣ MOSTRAR SQL PARA LIMPIAR BD
print("\n" + "=" * 80)
print("📋 PASO 2: EJECUTA ESTE SQL EN pgAdmin/DBeaver")
print("=" * 80)

sql_cleanup = """
-- Limpiar todas las tablas del módulo DIAN vs ERP

-- Ver conteo ANTES
SELECT 'ANTES - Maestro' as tabla, COUNT(*) as registros FROM maestro_dian_vs_erp
UNION ALL SELECT 'ANTES - DIAN', COUNT(*) FROM dian
UNION ALL SELECT 'ANTES - ERP FN', COUNT(*) FROM erp_financiero
UNION ALL SELECT 'ANTES - ERP CM', COUNT(*) FROM erp_comercial
UNION ALL SELECT 'ANTES - Acuses', COUNT(*) FROM acuses;

-- ELIMINAR todos los datos
DELETE FROM maestro_dian_vs_erp;
DELETE FROM dian;
DELETE FROM erp_financiero;
DELETE FROM erp_comercial;
DELETE FROM errores_erp;
DELETE FROM acuses;

-- Ver conteo DESPUÉS (todos deben estar en 0)
SELECT 'DESPUÉS - Maestro' as tabla, COUNT(*) as registros FROM maestro_dian_vs_erp
UNION ALL SELECT 'DESPUÉS - DIAN', COUNT(*) FROM dian
UNION ALL SELECT 'DESPUÉS - ERP FN', COUNT(*) FROM erp_financiero
UNION ALL SELECT 'DESPUÉS - ERP CM', COUNT(*) FROM erp_comercial
UNION ALL SELECT 'DESPUÉS - Acuses', COUNT(*) FROM acuses;
"""

print(sql_cleanup)

# Guardar SQL en archivo
with open('LIMPIAR_BD.sql', 'w', encoding='utf-8') as f:
    f.write(sql_cleanup)

print("\n✅ SQL guardado en: LIMPIAR_BD.sql")

# 3️⃣ INSTRUCCIONES FINALES
print("\n" + "=" * 80)
print("📝 PROCESO COMPLETO DE VALIDACIÓN")
print("=" * 80)

instrucciones = """
✅ PASO 1: LIMPIEZA (COMPLETADO)
   - Archivos uploads/ eliminados ✅
   
⏳ PASO 2: LIMPIAR BASE DE DATOS
   Opción A - Desde pgAdmin:
      1. Abre pgAdmin
      2. Conecta a gestor_documental
      3. Copia y pega el SQL de arriba
      4. Ejecuta
   
   Opción B - Desde línea de comandos:
      psql -U gestor_user -d gestor_documental -f LIMPIAR_BD.sql

⏳ PASO 3: CARGAR ARCHIVOS FRESCOS
   1. Ve a: http://127.0.0.1:8099/dian_vs_erp/cargar_archivos
   2. Sube los archivos Excel:
      📄 DIAN (Obligatorio)
      📄 ERP Financiero (Opcional)
      📄 ERP Comercial (Opcional)
      📄 Acuses (Opcional - para estados de aprobación)
   3. Click "Procesar & Consolidar"

⏳ PASO 4: OBSERVAR LA CONSOLA FLASK
   Deberías ver:
   ✅ COLUMNA CUFE DETECTADA: 'cufe/cude'
   📝 Fila 0: CUFE desde columna 'cufe/cude': '929f7761...' (len=96)
   📝 Fila 1: CUFE desde columna 'cufe/cude': '3b651964...' (len=96)
   🔍 Búsqueda acuse: ✅ ENCONTRADO → Estado: 'Acuse Bien/Servicio'

⏳ PASO 5: VERIFICAR RESULTADOS
   1. Ve a Visor V2
   2. Verifica columna "Ver PDF" - debe tener contenido ✅
   3. Verifica columna "Estado Aprobación":
      ✅ Acuse Bien/Servicio
      ✅ Aceptación Expresa
      ✅ Aceptación Tácita
      ✅ Pendiente
      ✅ No Registra (solo algunos, no todos)

🎯 RESULTADO ESPERADO:
   - Ver PDF: Con CUFE en ~70,000 registros
   - Estados variados (no solo "No Registra")
   - Tasa de éxito >80% si tienes archivo acuses
"""

print(instrucciones)

print("\n" + "=" * 80)
print("🚀 SISTEMA LISTO PARA CARGA FRESCA")
print("=" * 80)
print("\n⚡ SIGUIENTE: Ejecuta el SQL de arriba y luego sube archivos desde la web")
