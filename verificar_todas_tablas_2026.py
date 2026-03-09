"""
Script para verificar qué datos de 2026 hay en TODAS las tablas del módulo DIAN vs ERP
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Tablas del módulo DIAN vs ERP
TABLAS_DIAN_ERP = [
    'dian',                    # Facturas DIAN (XML/Excel)
    'erp_financiero',          # Datos ERP Financiero
    'erp_comercial',           # Datos ERP Comercial
    'errores_erp',             # Errores del ERP
    'acuses',                  # Acuses de recibo
    'maestro_dian_vs_erp'      # Tabla consolidada (ya la revisamos)
]

print("=" * 100)
print("🔍 VERIFICACIÓN COMPLETA - DATOS 2026 EN TODAS LAS TABLAS DIAN VS ERP")
print("=" * 100)

with engine.connect() as conn:
    resultados = []
    
    for tabla in TABLAS_DIAN_ERP:
        try:
            # Verificar si la tabla existe
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{tabla}'
                )
            """))
            
            existe = result.fetchone()[0]
            
            if not existe:
                print(f"\n❌ Tabla '{tabla}': NO EXISTE en la base de datos")
                continue
            
            # Contar registros totales
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            total = result.fetchone()[0]
            
            # Contar registros de 2026
            # Intentar con diferentes nombres de columna de fecha
            registros_2026 = 0
            columna_fecha = None
            
            for col in ['fecha_emision', 'fecha_documento', 'fecha', 'fecha_acuse']:
                try:
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM {tabla}
                        WHERE {col} >= '2026-01-01' AND {col} < '2027-01-01'
                    """))
                    registros_2026 = result.fetchone()[0]
                    columna_fecha = col
                    break
                except:
                    continue
            
            if columna_fecha:
                if registros_2026 > 0:
                    print(f"\n⚠️  Tabla '{tabla}':")
                    print(f"    Total registros: {total:,}")
                    print(f"    Registros 2026: {registros_2026:,} ⚠️ (HAY DATOS)")
                    resultados.append({
                        'tabla': tabla,
                        'total': total,
                        'año_2026': registros_2026,
                        'columna_fecha': columna_fecha
                    })
                else:
                    print(f"\n✅ Tabla '{tabla}':")
                    print(f"    Total registros: {total:,}")
                    print(f"    Registros 2026: 0 (LIMPIA)")
                    resultados.append({
                        'tabla': tabla,
                        'total': total,
                        'año_2026': 0,
                        'columna_fecha': columna_fecha
                    })
            else:
                print(f"\n⚠️  Tabla '{tabla}':")
                print(f"    Total registros: {total:,}")
                print(f"    No se pudo detectar columna de fecha")
                resultados.append({
                    'tabla': tabla,
                    'total': total,
                    'año_2026': '???',
                    'columna_fecha': None
                })
                
        except Exception as e:
            print(f"\n❌ Error verificando tabla '{tabla}': {str(e)}")

# Resumen
print("\n" + "=" * 100)
print("📊 RESUMEN DE VERIFICACIÓN:")
print("=" * 100)

tablas_con_2026 = [r for r in resultados if isinstance(r['año_2026'], int) and r['año_2026'] > 0]

if tablas_con_2026:
    print(f"\n⚠️  SE ENCONTRARON DATOS DE 2026 EN {len(tablas_con_2026)} TABLA(S):\n")
    for r in tablas_con_2026:
        print(f"   • {r['tabla']}: {r['año_2026']:,} registros de 2026")
    
    print(f"\n❌ PROBLEMA IDENTIFICADO:")
    print(f"   Solo se eliminó la tabla 'maestro_dian_vs_erp'")
    print(f"   Las tablas fuente ({', '.join([r['tabla'] for r in tablas_con_2026])}) aún tienen datos de 2026")
    print(f"\n⚠️  CONSECUENCIA:")
    print(f"   Si re-importas archivos Excel de 2026, se mezclarán con datos viejos corruptos")
    print(f"\n💡 SOLUCIÓN:")
    print(f"   Debes ELIMINAR datos de 2026 de TODAS las tablas, no solo maestro_dian_vs_erp")
else:
    print(f"\n✅ TODAS LAS TABLAS ESTÁN LIMPIAS DE DATOS 2026")
    print(f"✅ Es seguro re-importar archivos Excel de 2026")

print("\n" + "=" * 100)
