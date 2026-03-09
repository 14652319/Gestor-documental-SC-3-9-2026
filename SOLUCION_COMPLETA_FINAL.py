"""
SOLUCION_COMPLETA_FINAL.py
===========================
Solución DEFINITIVA al problema de duplicados y consolidación

PROBLEMA IDENTIFICADO:
- Las tablas YA TIENEN datos de cargas anteriores
- actualizar_maestro() encuentra claves duplicadas al intentar cargar
- Error: "llave duplicada viola restricción de unicidad «uk_dian_clave»"

SOLUCIÓN:
1. LIMPIAR todas las tablas (dian, erp_comercial, erp_financiero, acuses, maestro)
2. Cerrar Excel y limpiar archivos temporales
3. Copiar archivos limpios a uploads/
4. Ejecutar actualizar_maestro() desde cero
"""

import os
import sys
import shutil
import subprocess
import psycopg2
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ['DATABASE_URL'] = 'postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental'

print("="*80)
print("🔥 SOLUCIÓN COMPLETA Y DEFINITIVA - LIMPIEZA TOTAL")
print("="*80)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# ============================================================================
# PASO 1: Cerrar Excel
# ============================================================================
print("📊 PASO 1: Cerrar Excel")
print("-"*80)

try:
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq EXCEL.EXE"],
        capture_output=True,
        text=True
    )
    
    if "EXCEL.EXE" in result.stdout:
        print("   ⚠️  Excel abierto - cerrando...")
        subprocess.run(["taskkill", "/F", "/IM", "EXCEL.EXE"], capture_output=True)
        print("   ✅ Excel cerrado")
    else:
        print("   ✅ Excel no está abierto")
except Exception as e:
    print(f"   ⚠️  {str(e)}")

print()

# ============================================================================
# PASO 2: LIMPIAR tablas de base de datos
# ============================================================================
print("🗑️  PASO 2: LIMPIAR tablas de base de datos")
print("-"*80)
print("   ⚠️  ADVERTENCIA: Se eliminarán TODOS los datos existentes")
print()

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    
    # Verificar conteos ANTES
    print("   📊 Registros ANTES de limpiar:")
    cursor.execute("SELECT COUNT(*) FROM dian")
    count_dian = cursor.fetchone()[0]
    print(f"      dian:             {count_dian:>10,}")
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    count_erp_cm = cursor.fetchone()[0]
    print(f"      erp_comercial:    {count_erp_cm:>10,}")
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    count_erp_fn = cursor.fetchone()[0]
    print(f"      erp_financiero:   {count_erp_fn:>10,}")
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    count_acuses = cursor.fetchone()[0]
    print(f"      acuses:           {count_acuses:>10,}")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    count_maestro = cursor.fetchone()[0]
    print(f"      maestro_dian_vs_erp: {count_maestro:>10,}")
    
    print()
    print("   🗑️  Limpiando tablas...")
    
    # LIMPIAR tablas en orden correcto (empezar por maestro que depende de otras)
    cursor.execute("TRUNCATE TABLE maestro_dian_vs_erp RESTART IDENTITY CASCADE")
    print("      ✅ maestro_dian_vs_erp limpiada")
    
    cursor.execute("TRUNCATE TABLE dian RESTART IDENTITY CASCADE")
    print("      ✅ dian limpiada")
    
    cursor.execute("TRUNCATE TABLE erp_comercial RESTART IDENTITY CASCADE")
    print("      ✅ erp_comercial limpiada")
    
    cursor.execute("TRUNCATE TABLE erp_financiero RESTART IDENTITY CASCADE")
    print("      ✅ erp_financiero limpiada")
    
    cursor.execute("TRUNCATE TABLE acuses RESTART IDENTITY CASCADE")
    print("      ✅ acuses limpiada")
    
    conn.commit()
    
    # Verificar conteos DESPUÉS
    print()
    print("   📊 Registros DESPUÉS de limpiar:")
    
    cursor.execute("SELECT COUNT(*) FROM dian")
    print(f"      dian:             {cursor.fetchone()[0]:>10,}")
    
    cursor.execute("SELECT COUNT(*) FROM erp_comercial")
    print(f"      erp_comercial:    {cursor.fetchone()[0]:>10,}")
    
    cursor.execute("SELECT COUNT(*) FROM erp_financiero")
    print(f"      erp_financiero:   {cursor.fetchone()[0]:>10,}")
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    print(f"      acuses:           {cursor.fetchone()[0]:>10,}")
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    print(f"      maestro_dian_vs_erp: {cursor.fetchone()[0]:>10,}")
    
    cursor.close()
    conn.close()
    
    print()
    print("   ✅ Todas las tablas están VACÍAS y listas para carga fresca")
    
except Exception as e:
    print(f"   ❌ ERROR limpiando tablas: {str(e)}")
    sys.exit(1)

print()

# ============================================================================
# PASO 3: Limpiar archivos temporales
# ============================================================================
print("🗑️  PASO 3: Limpiar archivos temporales")
print("-"*80)

uploads_dir = project_root / "uploads"
carpetas = ["dian", "erp_fn", "erp_cm", "acuses"]

for carpeta in carpetas:
    carpeta_path = uploads_dir / carpeta
    if carpeta_path.exists():
        for f in carpeta_path.glob("*"):
            try:
                if f.is_file():
                    f.unlink()
            except:
                pass
    carpeta_path.mkdir(parents=True, exist_ok=True)

print("   ✅ Carpetas uploads/ limpiadas")
print()

# ============================================================================
# PASO 4: Copiar archivos limpios
# ============================================================================
print("📁 PASO 4: Copiar archivos a uploads/")
print("-"*80)

archivos_fuente = {
    "dian": Path("C:/Users/Usuario/Downloads/Ricardo/Dian.xlsx"),
    "erp_fn": Path("C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx"),
    "erp_cm": Path("C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx"),
    "acuses": Path("C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx")
}

carpetas_destino = {
    "dian": uploads_dir / "dian",
    "erp_fn": uploads_dir / "erp_fn",
    "erp_cm": uploads_dir / "erp_cm",
    "acuses": uploads_dir / "acuses"
}

for nombre in archivos_fuente.keys():
    fuente = archivos_fuente[nombre]
    if not fuente.exists():
        print(f"   ❌ NO ENCONTRADO: {fuente}")
        sys.exit(1)
    
    # Verificar que NO sea archivo temporal
    if fuente.name.startswith("~$") or fuente.name.startswith("-$"):
        print(f"   ❌ ARCHIVO TEMPORAL: {fuente.name}")
        sys.exit(1)
    
    destino = carpetas_destino[nombre] / fuente.name
    shutil.copy2(fuente, destino)
    size_mb = destino.stat().st_size / (1024 * 1024)
    print(f"   ✅ {nombre:10} → {fuente.name} ({size_mb:.2f} MB)")

print()

# ============================================================================
# PASO 5: Ejecutar consolidación
# ============================================================================
print("🚀 PASO 5: Ejecutar consolidación DESDE CERO")
print("-"*80)
print("   ⏳ Procesando 4 archivos (esto toma 1-2 minutos)...")
print()

try:
    from app import app
    from modules.dian_vs_erp.routes import actualizar_maestro
    
    with app.app_context():
        inicio = datetime.now()
        resultado = actualizar_maestro()
        fin = datetime.now()
        
        duracion = (fin - inicio).total_seconds()
        print(f"✅ Consolidación completada en {duracion:.2f} segundos")
        print()
        
        if isinstance(resultado, dict):
            print(f"📋 {resultado.get('message', 'Proceso completado')}")
            metricas = resultado.get('metricas', {})
            if metricas:
                print()
                print("📊 MÉTRICAS FINALES:")
                print(f"   DIAN:     {metricas.get('registros_dian', 0):>10,} registros")
                print(f"   ERP FN:   {metricas.get('registros_erp_fn', 0):>10,} registros")
                print(f"   ERP CM:   {metricas.get('registros_erp_cm', 0):>10,} registros")
                print(f"   Acuses:   {metricas.get('registros_acuses', 0):>10,} registros")
        
except Exception as e:
    print(f"❌ ERROR durante consolidación:")
    print(f"   {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# ============================================================================
# PASO 6: Verificar resultado final
# ============================================================================
print("📊 PASO 6: Verificar resultado final")
print("-"*80)

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
    count_maestro = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE ver_pdf IS NOT NULL")
    count_pdf = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE estado_aprobacion IS NOT NULL")
    count_estado = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_FINANCIERO') as erp_fn,
            COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_COMERCIAL') as erp_cm
        FROM maestro_dian_vs_erp
    """)
    fuentes = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    print(f"   Total maestro:          {count_maestro:>10,}")
    print(f"   Con ver_pdf:            {count_pdf:>10,}")
    print(f"   Con estado_aprobacion:  {count_estado:>10,}")
    print(f"   ERP_FINANCIERO:         {fuentes[0]:>10,}")
    print(f"   ERP_COMERCIAL:          {fuentes[1]:>10,}")
    print()
    
    if count_maestro > 100000 and count_pdf > 0 and fuentes[0] > 0:
        print("   ✅ CONSOLIDACIÓN EXITOSA")
    else:
        print("   ⚠️  Verificar resultados (algunos conteos bajos)")
    
except Exception as e:
    print(f"   ⚠️  Error verificando: {str(e)}")

print()
print("="*80)
print("✅ PROCESO COMPLETADO")
print("="*80)
print()
print("📋 VERIFICAR EN NAVEGADOR:")
print("   http://localhost:8099/dian_vs_erp/visor_v2")
print()
print("   Debe mostrar:")
print("   ✓ ~170,000 registros totales")
print("   ✓ Columna 'Ver PDF' con enlaces")
print("   ✓ Columna 'Estado Aprobación' poblada")
print("   ✓ Datos de ERP_FINANCIERO visibles")
print("   ✓ Datos de ERP_COMERCIAL visibles")
print()
print("="*80)
