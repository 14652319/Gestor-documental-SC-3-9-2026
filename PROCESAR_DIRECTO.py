"""
PROCESAR_DIRECTO.py
===================
Ejecuta actualizar_maestro() DIRECTAMENTE sin necesidad de sesión HTTP.

Este script:
1. Lee los archivos que YA ESTÁN en uploads/
2. Los procesa con actualizar_maestro()
3. Llena la tabla maestro_dian_vs_erp

NO necesitas iniciar sesión en el navegador.
"""

import os
import sys
from datetime import datetime

# Configurar rutas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('FLASK_ENV', 'development')

# Cargar .env
from dotenv import load_dotenv
load_dotenv()

print("="*80)
print("🚀 PROCESAMIENTO DIRECTO - SIN NECESIDAD DE SESIÓN")
print("="*80)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Verificar archivos en uploads/
from pathlib import Path
BASE_DIR = Path(__file__).parent

archivos = {
    "DIAN": BASE_DIR / "uploads" / "dian",
    "ERP Financiero": BASE_DIR / "uploads" / "erp_fn",
    "ERP Comercial": BASE_DIR / "uploads" / "erp_cm",
    "Acuses": BASE_DIR / "uploads" / "acuses"
}

print("📂 VERIFICANDO ARCHIVOS EN uploads/:")
print()
archivos_encontrados = 0
for nombre, carpeta in archivos.items():
    if carpeta.exists():
        archivos_en_carpeta = list(carpeta.glob("*.xlsx")) + list(carpeta.glob("*.xls"))
        if archivos_en_carpeta:
            for archivo in archivos_en_carpeta:
                size_mb = archivo.stat().st_size / (1024*1024)
                print(f"   ✅ {nombre}: {archivo.name} ({size_mb:.2f} MB)")
                archivos_encontrados += 1
        else:
            print(f"   ⚠️  {nombre}: Carpeta vacía")
    else:
        print(f"   ❌ {nombre}: Carpeta no existe")

print()

if archivos_encontrados == 0:
    print("❌ ERROR: No hay archivos en uploads/")
    print()
    print("Ejecuta primero: python SOLUCION_COMPLETA_FINAL.py")
    print()
    input("Presiona ENTER para salir...")
    sys.exit(1)

print(f"✅ {archivos_encontrados} archivo(s) encontrado(s)")
print()

# Verificar conexión a base de datos
print("🔌 VERIFICANDO CONEXIÓN A BASE DE DATOS...")
import psycopg2
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
    count_antes = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    print(f"   ✅ Conectado (maestro tiene {count_antes:,} registros antes de procesar)")
except Exception as e:
    print(f"   ❌ Error de conexión: {e}")
    input("Presiona ENTER para salir...")
    sys.exit(1)

print()
print("="*80)
print("⚙️  PROCESANDO ARCHIVOS")
print("="*80)
print()
print("⏳ Esto puede tomar 1-3 minutos dependiendo del tamaño de los archivos...")
print()

try:
    # Importar la app Flask y el módulo DIAN
    from app import app
    from modules.dian_vs_erp.routes import actualizar_maestro
    
    # Ejecutar dentro del contexto de la app
    with app.app_context():
        inicio = datetime.now()
        
        print("📊 INICIANDO actualizar_maestro()...")
        print()
        
        # Ejecutar procesamiento
        resultado = actualizar_maestro()
        
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        print()
        print("="*80)
        print("✅ PROCESAMIENTO COMPLETADO")
        print("="*80)
        print()
        print(f"⏱️  Tiempo: {duracion:.2f} segundos")
        print()
        print("📝 RESULTADO:")
        print()
        print(resultado)
        print()
        
        # Verificar resultados
        print("📊 VERIFICANDO RESULTADOS EN BASE DE DATOS...")
        print()
        
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="gestor_documental",
            user="postgres",
            password="G3st0radm$2025."
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE ver_pdf IS NOT NULL")
        con_pdf = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE estado_aprobacion IS NOT NULL")
        con_estado = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_FINANCIERO') as erp_fn,
                COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_COMERCIAL') as erp_cm,
                COUNT(*) FILTER (WHERE tipo_fuente = 'DIAN') as dian
            FROM maestro_dian_vs_erp
        """)
        fuentes = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM dian")
        count_dian = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM erp_comercial")
        count_erp_cm = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM erp_financiero")
        count_erp_fn = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM acuses")
        count_acuses = cursor.fetchone()[0]
        
        print("   📊 TABLA MAESTRO (maestro_dian_vs_erp):")
        print(f"      Total registros:       {total:>10,}")
        print(f"      Con ver_pdf:           {con_pdf:>10,} ({con_pdf*100//total if total>0 else 0}%)")
        print(f"      Con estado_aprobacion: {con_estado:>10,} ({con_estado*100//total if total>0 else 0}%)")
        print()
        print("   📂 POR TIPO DE FUENTE:")
        print(f"      DIAN:                  {fuentes[2]:>10,}")
        print(f"      ERP_FINANCIERO:        {fuentes[0]:>10,}")
        print(f"      ERP_COMERCIAL:         {fuentes[1]:>10,}")
        print()
        print("   📊 TABLAS INDIVIDUALES:")
        print(f"      dian:                  {count_dian:>10,}")
        print(f"      erp_financiero:        {count_erp_fn:>10,}")
        print(f"      erp_comercial:         {count_erp_cm:>10,}")
        print(f"      acuses:                {count_acuses:>10,}")
        print()
        
        cursor.close()
        conn.close()
        
        if total > 100000:
            print("="*80)
            print("🎉 ¡ÉXITO! CONSOLIDACIÓN COMPLETADA")
            print("="*80)
            print()
            print("✅ La tabla maestro tiene datos correctamente")
            print()
            print("🌐 ABRIR EN NAVEGADOR:")
            print("   http://localhost:8099/dian_vs_erp/visor_v2")
            print()
            print("Verifica que aparezcan:")
            print("   • Columna 'Ver PDF' con enlaces")
            print("   • Columna 'Estado Aprobación' con valores")
            print("   • Datos de ERP_FINANCIERO y ERP_COMERCIAL")
            print()
        elif total > 0:
            print("⚠️  ADVERTENCIA: Hay datos pero menos de lo esperado")
            print(f"   Se esperaban ~170,000 pero hay {total:,}")
            print()
            print("Verifica los archivos en uploads/:")
            print("   • ¿Son los archivos correctos?")
            print("   • ¿Tienen datos completos?")
            print()
        else:
            print("❌ ERROR: La tabla maestro sigue vacía")
            print()
            print("Posibles causas:")
            print("   • Los archivos en uploads/ están vacíos")
            print("   • Error en el procesamiento (ver arriba)")
            print("   • Formato de archivos incorrecto")
            print()
        
except Exception as e:
    print()
    print("="*80)
    print("❌ ERROR DURANTE EL PROCESAMIENTO")
    print("="*80)
    print()
    print(f"Error: {str(e)}")
    print()
    
    import traceback
    print("📋 DETALLES DEL ERROR:")
    print()
    print(traceback.format_exc())
    print()

print("="*80)
input("\nPresiona ENTER para salir...")
