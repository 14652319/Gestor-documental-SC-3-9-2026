"""
✅ VERIFICACIÓN RÁPIDA POST-CARGA
====================================
Ejecuta esto DESPUÉS de que termine el procesamiento
para verificar si el FIX funcionó correctamente
"""
import psycopg2
from sqlalchemy import create_engine, text
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("🔍 VERIFICACIÓN POST-CARGA CON FIX")
print("=" * 80)

DATABASE_URL = "postgresql://gestor_user:G3st0r2024!@localhost:5432/gestor_documental"
engine = create_engine(DATABASE_URL)

try:
    with engine.begin() as conn:
        # 1. Contar registros en todas las tablas
        print("\n📊 REGISTROS EN TABLAS:")
        
        result = conn.execute(text("SELECT COUNT(*) FROM dian"))
        dian_count = result.scalar()
        print(f"   DIAN: {dian_count:,}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
        fn_count = result.scalar()
        print(f"   ERP Financiero: {fn_count:,}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
        cm_count = result.scalar()
        print(f"   ERP Comercial: {cm_count:,}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM acuses"))
        acuses_count = result.scalar()
        print(f"   Acuses: {acuses_count:,}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM maestro_dian_vs_erp"))
        maestro_count = result.scalar()
        print(f"   ✅ Maestro: {maestro_count:,}")
        
        # 2. VERIFICAR CUFE EN MAESTRO (CRÍTICO)
        print("\n" + "=" * 80)
        print("🔥 VERIFICACIÓN CRÍTICA: ¿SE CARGÓ EL CUFE?")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN cufe IS NOT NULL AND cufe != '' THEN 1 END) as con_cufe,
                COUNT(CASE WHEN cufe IS NULL OR cufe = '' THEN 1 END) as sin_cufe
            FROM maestro_dian_vs_erp
        """))
        row = result.fetchone()
        total = row[0]
        con_cufe = row[1]
        sin_cufe = row[2]
        
        porcentaje = (con_cufe / total * 100) if total > 0 else 0
        
        print(f"\n   Total registros: {total:,}")
        print(f"   Con CUFE: {con_cufe:,} ({porcentaje:.1f}%)")
        print(f"   Sin CUFE: {sin_cufe:,}")
        
        if con_cufe > 0:
            print(f"\n   ✅✅✅ ¡FIX FUNCIONÓ! CUFE se está cargando ✅✅✅")
        else:
            print(f"\n   ❌❌❌ PROBLEMA: CUFE sigue en NULL ❌❌❌")
        
        # 3. VERIFICAR ESTADO APROBACIÓN
        print("\n" + "=" * 80)
        print("📋 DISTRIBUCIÓN DE ESTADO APROBACIÓN")
        print("=" * 80)
        
        result = conn.execute(text("""
            SELECT 
                estado_aprobacion,
                COUNT(*) as cantidad,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as porcentaje
            FROM maestro_dian_vs_erp
            GROUP BY estado_aprobacion
            ORDER BY cantidad DESC
            LIMIT 10
        """))
        
        estados = result.fetchall()
        no_registra = 0
        estados_validos = 0
        
        for estado, cantidad, pct in estados:
            icono = "❌" if estado == "No Registra" else "✅"
            print(f"   {icono} {estado:30s} {cantidad:8,} ({pct:5.1f}%)")
            
            if estado == "No Registra":
                no_registra = cantidad
            else:
                estados_validos += cantidad
        
        # 4. MOSTRAR EJEMPLOS DE REGISTROS CON CUFE
        if con_cufe > 0:
            print("\n" + "=" * 80)
            print("📖 EJEMPLOS DE REGISTROS CON CUFE")
            print("=" * 80)
            
            result = conn.execute(text("""
                SELECT 
                    nit_emisor,
                    prefijo,
                    folio,
                    LEFT(cufe, 20) as cufe_inicio,
                    estado_aprobacion
                FROM maestro_dian_vs_erp
                WHERE cufe IS NOT NULL AND cufe != ''
                LIMIT 5
            """))
            
            ejemplos = result.fetchall()
            for nit, prefijo, folio, cufe_inicio, estado in ejemplos:
                print(f"\n   NIT: {nit} | {prefijo}-{folio}")
                print(f"   CUFE: {cufe_inicio}... (primeros 20 chars)")
                print(f"   Estado: {estado}")
        
        # 5. RESUMEN FINAL
        print("\n" + "=" * 80)
        print("📊 RESUMEN FINAL")
        print("=" * 80)
        
        if con_cufe == 0:
            print("\n   ❌ PROBLEMA: CUFE NO se está cargando")
            print("   ⚠️  Revisa la consola Flask para ver errores")
            print("   ⚠️  Verifica que el archivo DIAN tenga la columna CUFE/CUDE")
        elif porcentaje < 50:
            print(f"\n   ⚠️  CUFE se carga pero solo en {porcentaje:.1f}% de registros")
            print("   ⚠️  Puede haber un problema parcial")
        else:
            print(f"\n   ✅ CUFE se carga correctamente ({porcentaje:.1f}%)")
        
        if estados_validos > 0:
            tasa_exito = (estados_validos / total * 100) if total > 0 else 0
            print(f"\n   ✅ Estados válidos: {estados_validos:,} ({tasa_exito:.1f}%)")
            print(f"   ✅ Match con acuses funcionando correctamente")
        else:
            print(f"\n   ❌ NO hay estados válidos (todos 'No Registra')")
            print(f"   ⚠️  El match con acuses NO funcionó")
        
        print("\n" + "=" * 80)
        
        if con_cufe > 0 and estados_validos > 0:
            print("🎉 ¡ÉXITO! EL FIX FUNCIONÓ CORRECTAMENTE")
        elif con_cufe > 0:
            print("⚠️  PARCIAL: CUFE carga pero no hace match con acuses")
        else:
            print("❌ FALLO: CUFE no se está cargando")
        
        print("=" * 80)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print(traceback.format_exc())
