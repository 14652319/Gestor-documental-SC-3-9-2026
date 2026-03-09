"""
CONSOLIDAR_MAESTRO_DESDE_TABLAS.py
====================================
Solución al problema: "en la tabla maestro no procesa los datos"

PROBLEMA IDENTIFICADO:
- Las tablas individuales (dian, erp_comercial, erp_financiero, acuses) tienen datos ✅
- La tabla maestro_dian_vs_erp está vacía/desactualizada ❌
- La función actualizar_maestro() espera archivos en uploads/, no datos en tablas

SOLUCIÓN:
1. Copiar archivos Excel a carpetas uploads/ correctas
2. Ejecutar actualizar_maestro(forzar=True) para consolidar
3. Verificar maestro_dian_vs_erp poblado con ver_pdf y estado_aprobacion

Fecha: 18 Febrero 2026
Registros esperados: ~173,000 (DIAN=66,276 + ERP_CM=57,191 + ERP_FN=2,995 + Acuses=46,650)
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Configurar entorno
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ['DATABASE_URL'] = 'postgresql://postgres:Vimer2024*@localhost:5432/gestor_documental'

print("="*100)
print("🔄 CONSOLIDACIÓN DE TABLA MAESTRO - SOLUCIÓN DEFINITIVA")
print("="*100)
print(f"📅 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)
print()

# ============================================================================
# PASO 1: Configurar rutas de archivos fuente y destino
# ============================================================================
print("📁 PASO 1: Configurar rutas de archivos")
print("-"*100)

# Archivos fuente (donde están actualmente)
archivos_fuente = {
    "dian": Path("C:/Users/Usuario/Downloads/Ricardo/Dian.xlsx"),
    "erp_fn": Path("C:/Users/Usuario/Downloads/Ricardo/ERP Financiero 18 02 2026.xlsx"),
    "erp_cm": Path("C:/Users/Usuario/Downloads/Ricardo/ERP comercial 18 02 2026.xlsx"),
    "acuses": Path("C:/Users/Usuario/Downloads/Ricardo/acuses 2.xlsx")
}

# Carpetas destino (donde actualizar_maestro() espera encontrarlos)
uploads_dir = project_root / "uploads"
carpetas_destino = {
    "dian": uploads_dir / "dian",
    "erp_fn": uploads_dir / "erp_fn",
    "erp_cm": uploads_dir / "erp_cm",
    "acuses": uploads_dir / "acuses"
}

# Verificar que archivos fuente existen
print("✅ Verificando archivos fuente:")
for nombre, ruta in archivos_fuente.items():
    if ruta.exists():
        size_mb = ruta.stat().st_size / (1024 * 1024)
        print(f"   ✓ {nombre:10} → {ruta.name} ({size_mb:.2f} MB)")
    else:
        print(f"   ✗ {nombre:10} → ❌ NO ENCONTRADO: {ruta}")
        print(f"\n❌ ERROR: Falta archivo {nombre}")
        print(f"   Ruta esperada: {ruta}")
        sys.exit(1)

print()

# ============================================================================
# PASO 2: Crear carpetas uploads/ si no existen
# ============================================================================
print("📂 PASO 2: Crear carpetas de uploads")
print("-"*100)

for nombre, carpeta in carpetas_destino.items():
    carpeta.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ {nombre:10} → {carpeta}")

print()

# ============================================================================
# PASO 3: Copiar archivos a carpetas uploads/
# ============================================================================
print("📋 PASO 3: Copiar archivos a uploads/")
print("-"*100)
print("⚠️  NOTA: Si ya existen archivos, se sobrescribirán")
print()

for nombre in archivos_fuente.keys():
    fuente = archivos_fuente[nombre]
    destino = carpetas_destino[nombre] / fuente.name
    
    try:
        shutil.copy2(fuente, destino)
        size_mb = destino.stat().st_size / (1024 * 1024)
        print(f"   ✅ Copiado {nombre:10} → {destino.name} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"   ❌ ERROR copiando {nombre}: {str(e)}")
        sys.exit(1)

print()

# ============================================================================
# PASO 4: Importar Flask y función de consolidación
# ============================================================================
print("🔧 PASO 4: Importar módulos Flask")
print("-"*100)

try:
    from app import app
    from modules.dian_vs_erp.routes import actualizar_maestro
    from extensions import db
    print("   ✅ Módulos importados correctamente")
except Exception as e:
    print(f"   ❌ ERROR importando módulos: {str(e)}")
    sys.exit(1)

print()

# ============================================================================
# PASO 5: Verificar estado ANTES de consolidar
# ============================================================================
print("📊 PASO 5: Verificar estado ANTES de consolidar")
print("-"*100)

with app.app_context():
    try:
        # Usar psycopg2 directamente con encoding correcto
        import psycopg2
        conn = psycopg2.connect(
            "postgresql://postgres:Vimer2024*@localhost:5432/gestor_documental",
            client_encoding='utf8'
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM dian")
        count_dian = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM erp_comercial")
        count_erp_cm = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM erp_financiero")
        count_erp_fn = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM acuses")
        count_acuses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
        count_maestro_antes = cursor.fetchone()[0]
        
        print(f"   DIAN:             {count_dian:>10,} registros ✅")
        print(f"   ERP Comercial:    {count_erp_cm:>10,} registros ✅")
        print(f"   ERP Financiero:   {count_erp_fn:>10,} registros ✅")
        print(f"   Acuses:           {count_acuses:>10,} registros ✅")
        print(f"   ──────────────────────────────────")
        print(f"   TOTAL INDIVIDUAL: {count_dian + count_erp_cm + count_erp_fn + count_acuses:>10,} registros")
        print()
        print(f"   maestro_dian_vs_erp (ANTES): {count_maestro_antes:>10,} registros ⚠️")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ ERROR verificando conteos: {str(e)}")
        sys.exit(1)

print()

# ============================================================================
# PASO 6: Ejecutar consolidación (actualizar_maestro)
# ============================================================================
print("🚀 PASO 6: Ejecutar consolidación maestro")
print("-"*100)
print("⏳ Procesando datos (esto puede tomar 1-2 minutos)...")
print()

with app.app_context():
    try:
        inicio = datetime.now()
        
        # Llamar a la función real de consolidación
        resultado = actualizar_maestro(forzar=True)
        
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        print(f"✅ Consolidación completada en {duracion:.2f} segundos")
        print()
        
        # Mostrar resultado
        if isinstance(resultado, dict):
            mensaje = resultado.get('message', 'Sin mensaje')
            print(f"📋 Mensaje del sistema: {mensaje}")
            
            metricas = resultado.get('metricas', {})
            if metricas:
                print()
                print("📊 MÉTRICAS DEL PROCESO:")
                print(f"   Registros DIAN procesados:        {metricas.get('registros_dian', 0):>10,}")
                print(f"   Registros ERP FN procesados:      {metricas.get('registros_erp_fn', 0):>10,}")
                print(f"   Registros ERP CM procesados:      {metricas.get('registros_erp_cm', 0):>10,}")
                print(f"   Registros Acuses procesados:      {metricas.get('registros_acuses', 0):>10,}")
                print(f"   Tiempo de proceso:                {metricas.get('tiempo_proceso', 0):>10.2f}s")
        else:
            print(f"📋 Resultado: {resultado}")
        
    except Exception as e:
        print(f"❌ ERROR durante consolidación:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print()

# ============================================================================
# PASO 7: Verificar estado DESPUÉS de consolidar
# ============================================================================
print("📊 PASO 7: Verificar estado DESPUÉS de consolidar")
print("-"*100)

with app.app_context():
    try:
        # Usar psycopg2 directamente con encoding correcto
        import psycopg2
        conn = psycopg2.connect(
            "postgresql://postgres:Vimer2024*@localhost:5432/gestor_documental",
            client_encoding='utf8'
        )
        cursor = conn.cursor()
        
        # Conteo total maestro
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
        count_maestro_despues = cursor.fetchone()[0]
        
        # Verificar campos críticos
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE ver_pdf IS NOT NULL")
        count_con_pdf = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE estado_aprobacion IS NOT NULL")
        count_con_estado = cursor.fetchone()[0]
        
        # Verificar tipos de fuente
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_COMERCIAL') as comercial,
                COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_FINANCIERO') as financiero,
                COUNT(*) FILTER (WHERE tipo_fuente = 'DIAN') as dian_solo
            FROM maestro_dian_vs_erp
        """)
        tipos = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print(f"   maestro_dian_vs_erp (DESPUÉS): {count_maestro_despues:>10,} registros")
        print()
        print(f"   Registros con ver_pdf:         {count_con_pdf:>10,} ({'✅' if count_con_pdf > 0 else '❌'})")
        print(f"   Registros con estado_aprobacion: {count_con_estado:>10,} ({'✅' if count_con_estado > 0 else '❌'})")
        print()
        print("   📊 Distribución por fuente:")
        print(f"      ERP_COMERCIAL:  {tipos[0]:>10,}")
        print(f"      ERP_FINANCIERO: {tipos[1]:>10,}")
        print(f"      DIAN solo:      {tipos[2]:>10,}")
        
        # Validación final
        print()
        if count_maestro_despues > count_maestro_antes:
            incremento = count_maestro_despues - count_maestro_antes
            print(f"   ✅ ÉXITO: Maestro incrementó en {incremento:,} registros")
        else:
            print(f"   ⚠️  ADVERTENCIA: Maestro no incrementó (antes={count_maestro_antes:,}, después={count_maestro_despues:,})")
        
        if count_con_pdf > 0 and count_con_estado > 0:
            print(f"   ✅ ÉXITO: Campos ver_pdf y estado_aprobacion poblados")
        else:
            print(f"   ❌ ERROR: Faltan campos críticos")
        
        if tipos[1] > 0:  # ERP_FINANCIERO
            print(f"   ✅ ÉXITO: ERP_FINANCIERO consolidado correctamente")
        else:
            print(f"   ❌ ERROR: ERP_FINANCIERO no aparece en maestro")
        
    except Exception as e:
        print(f"   ❌ ERROR verificando resultados: {str(e)}")
        sys.exit(1)

print()

# ============================================================================
# PASO 8: Instrucciones finales
# ============================================================================
print("="*100)
print("✅ PROCESO COMPLETADO")
print("="*100)
print()
print("📋 PRÓXIMOS PASOS:")
print("   1. Abrir navegador en: http://localhost:8099/dian_vs_erp/visor_v2")
print("   2. Verificar que aparezcan los registros")
print("   3. Verificar columna 'Ver PDF' (debe mostrar enlaces)")
print("   4. Verificar columna 'Estado Aprobación' (debe mostrar estados)")
print("   5. Verificar que aparezcan datos de ERP_FINANCIERO")
print()
print("💡 Si los datos NO aparecen:")
print("   - Verificar logs en logs/security.log")
print("   - Ejecutar: python check.py")
print("   - Revisar si hay errores en la consola durante el proceso")
print()
print("="*100)
print(f"📅 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)
