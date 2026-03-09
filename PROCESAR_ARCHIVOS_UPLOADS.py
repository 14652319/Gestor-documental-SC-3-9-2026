"""
PROCESAR_ARCHIVOS_UPLOADS.py
=============================
Procesa los archivos que YA ESTÁN en uploads/ sin tener que subirlos de nuevo.

Los archivos fueron copiados por SOLUCION_COMPLETA_FINAL.py a:
- uploads/dian/Dian.xlsx
- uploads/erp_fn/ERP Financiero 18 02 2026.xlsx
- uploads/erp_cm/ERP comercial 18 02 2026.xlsx
- uploads/acuses/acuses 2.xlsx

Este script llama al endpoint /api/forzar_procesar que ejecuta actualizar_maestro()
"""

import requests
import time
from datetime import datetime

print("="*80)
print("🚀 PROCESAR ARCHIVOS DESDE uploads/")
print("="*80)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Esperar a que el servidor esté listo
print("⏳ Esperando a que el servidor esté listo...")
for i in range(10):
    try:
        response = requests.get("http://localhost:8099", timeout=2)
        if response.status_code in [200, 302, 400, 404]:
            print("   ✅ Servidor activo")
            break
    except:
        if i < 9:
            print(f"   Intento {i+1}/10...")
            time.sleep(2)
        else:
            print("   ❌ Servidor no responde")
            print("\n❌ ERROR: Ejecuta primero: python app.py")
            input("\nPresiona ENTER para salir...")
            exit(1)

print()
print("="*80)
print("⚙️  PROCESANDO ARCHIVOS DESDE uploads/")
print("="*80)
print()
print("📂 Archivos que se procesarán:")
print("   • uploads/dian/Dian.xlsx")
print("   • uploads/erp_fn/ERP Financiero 18 02 2026.xlsx")
print("   • uploads/erp_cm/ERP comercial 18 02 2026.xlsx")  
print("   • uploads/acuses/acuses 2.xlsx")
print()
print("⏳ Procesando (esto toma 1-2 minutos)...")
print()

try:
    # Llamar al endpoint que procesa desde uploads/
    response = requests.get(
        "http://localhost:8099/dian_vs_erp/api/forzar_procesar",
        timeout=300  # 5 minutos máximo
    )
    
    if response.status_code == 200:
        data = response.json()
        mensaje = data.get('mensaje', 'Procesado correctamente')
        
        print("="*80)
        print("✅ ÉXITO: ARCHIVOS PROCESADOS")
        print("="*80)
        print()
        print(mensaje)
        print()
        print("📊 VERIFICANDO RESULTADOS...")
        print()
        
        # Verificar registros creados
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
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE ver_pdf IS NOT NULL")
            con_pdf = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE estado_aprobacion IS NOT NULL")
            con_estado = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_FINANCIERO') as erp_fn,
                    COUNT(*) FILTER (WHERE tipo_fuente = 'ERP_COMERCIAL') as erp_cm
                FROM maestro_dian_vs_erp
            """)
            fuentes = cursor.fetchone()
            
            print("   📊 TABLA MAESTRO:")
            print(f"      Total registros:    {total:>10,}")
            print(f"      Con ver_pdf:        {con_pdf:>10,}")
            print(f"      Con estado:         {con_estado:>10,}")
            print(f"      ERP_FINANCIERO:     {fuentes[0]:>10,}")
            print(f"      ERP_COMERCIAL:      {fuentes[1]:>10,}")
            print()
            
            if total > 100000:
                print("   ✅ CONSOLIDACIÓN EXITOSA")
                print()
                print("🌐 ABRIR EN NAVEGADOR:")
                print("   http://localhost:8099/dian_vs_erp/visor_v2")
                print()
            else:
                print("   ⚠️  ADVERTENCIA: Pocos registros en maestro")
                print(f"   Se esperaban ~170,000 pero hay {total:,}")
                print()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"   ⚠️  No se pudo verificar BD: {e}")
            print("   Pero el procesamiento se completó")
            print()
        
    elif response.status_code == 401:
        print("="*80)
        print("❌ ERROR: SESIÓN NO VÁLIDA")
        print("="*80)
        print()
        print("Necesitas iniciar sesión primero:")
        print("1. Abre el navegador en: http://localhost:8099")
        print("2. Inicia sesión con tu usuario")
        print("3. Ejecuta este script de nuevo")
        print()
    else:
        print("="*80)
        print(f"❌ ERROR HTTP {response.status_code}")
        print("="*80)
        print()
        print(response.text)
        print()
        
except requests.Timeout:
    print("="*80)
    print("⏰ TIMEOUT: El proceso tomó más de 5 minutos")
    print("="*80)
    print()
    print("El procesamiento puede estar colgado.")
    print("Verifica los logs en: logs/security.log")
    print()
    
except Exception as e:
    print("="*80)
    print("❌ ERROR")
    print("="*80)
    print()
    print(f"Error: {str(e)}")
    print()
    import traceback
    print(traceback.format_exc())
    print()

print("="*80)
input("\nPresiona ENTER para salir...")
