"""
Script para verificar datos de 2026 en tablas NO eliminadas
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("=" * 100)
print("🔍 VERIFICACIÓN DE TABLAS NO ELIMINADAS - DATOS 2026")
print("=" * 100)

tablas_info = {
    'acuses': {
        'nombre': 'Acuses',
        'columna_fecha': 'fecha_acuse',
        'descripcion': 'Acuses de recibo de facturas'
    },
    'erp_financiero': {
        'nombre': 'ERP Financiero',  
        'columna_fecha': 'fecha',
        'descripcion': 'Datos del módulo financiero'
    },
    'erp_comercial': {
        'nombre': 'ERP Comercial',
        'columna_fecha': 'fecha',
        'descripcion': 'Datos del módulo comercial'
    }
}

resultado_global = {
    'tiene_datos_2026': False,
    'tablas_con_2026': []
}

with engine.connect() as conn:
    for tabla, info in tablas_info.items():
        try:
            # Verificar si la tabla existe
            result = conn.execute(text(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{tabla}'
                )
            """))
            
            if not result.fetchone()[0]:
                print(f"\n⚪ Tabla '{info['nombre']}': NO EXISTE en base de datos")
                continue
            
            # Contar registros totales
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            total = result.fetchone()[0]
            
            # Intentar contar registros de 2026 con la columna de fecha
            try:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM {tabla}
                    WHERE {info['columna_fecha']} >= '2026-01-01' 
                      AND {info['columna_fecha']} < '2027-01-01'
                """))
                registros_2026 = result.fetchone()[0]
                
                if registros_2026 > 0:
                    print(f"\n⚠️  Tabla '{info['nombre']}': {registros_2026:,} REGISTROS DE 2026")
                    print(f"    Total en tabla: {total:,}")
                    print(f"    Descripción: {info['descripcion']}")
                    
                    resultado_global['tiene_datos_2026'] = True
                    resultado_global['tablas_con_2026'].append({
                        'tabla': tabla,
                        'nombre': info['nombre'],
                        'registros_2026': registros_2026,
                        'total': total
                    })
                    
                    # Mostrar algunos ejemplos
                    result = conn.execute(text(f"""
                        SELECT * FROM {tabla}
                        WHERE {info['columna_fecha']} >= '2026-01-01' 
                          AND {info['columna_fecha']} < '2027-01-01'
                        LIMIT 3
                    """))
                    
                    print(f"    \n    📋 Ejemplos:")
                    for i, row in enumerate(result, 1):
                        print(f"       {i}. {dict(row)}")
                    
                else:
                    print(f"\n✅ Tabla '{info['nombre']}': LIMPIA (0 registros de 2026)")
                    print(f"    Total en tabla: {total:,}")
                    
            except Exception as e:
                conn.rollback()  # Rollback en caso de error
                print(f"\n❌ Tabla '{info['nombre']}': Error verificando fecha - {str(e)}")
                print(f"    Total en tabla: {total:,}")
                
        except Exception as e:
            conn.rollback()  # Rollback en caso de error
            print(f"\n❌ Error procesando tabla '{info['nombre']}': {str(e)}")

# Resumen final
print("\n" + "=" * 100)
print("📊 RESUMEN:")
print("=" * 100)

if resultado_global['tiene_datos_2026']:
    print(f"\n⚠️  PROBLEMA DETECTADO:")
    print(f"   Solo eliminaste 'Facturas DIAN' pero hay {len(resultado_global['tablas_con_2026'])} tabla(s) más con datos de 2026:\n")
    
    for t in resultado_global['tablas_con_2026']:
        print(f"   ❌ {t['nombre']}: {t['registros_2026']:,} registros de 2026")
    
    print(f"\n💡 QUÉ SIGNIFICA ESTO:")
    print(f"   • Los archivos Excel que subas se procesarán correctamente con el script corregido")
    print(f"   • PERO las tablas {', '.join([t['tabla'] for t in resultado_global['tablas_con_2026']])} tienen datos VIEJOS")
    print(f"   • Estos datos viejos pueden causar conflictos o mezcla de información")
    
    print(f"\n🔧 OPCIONES:")
    print(f"   OPCIÓN A) Eliminar también estas tablas:")
    print(f"      - Volver a http://127.0.0.1:8099/dian_vs_erp/configuracion")
    print(f"      - Marcar checkboxes: {', '.join([t['nombre'] for t in resultado_global['tablas_con_2026']])}")
    print(f"      - Solicitar nueva eliminación")
    
    print(f"\n   OPCIÓN B) Dejar estas tablas como están:")
    print(f"      - Si estás seguro que no afectan tu análisis")
    print(f"      - Proceder con importación de Facturas DIAN solamente")
    
else:
    print(f"\n✅ TODAS LAS TABLAS ESTÁN LIMPIAS O NO TIENEN DATOS DE 2026")
    print(f"✅ Es seguro proceder con la re-importación de archivos Excel")

print("=" * 100)
