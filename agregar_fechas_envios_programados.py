"""
Script para agregar columnas fecha_inicio y fecha_fin a envios_programados_dian_vs_erp
Fecha: 26 de Enero de 2026
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db

def agregar_columnas_fecha():
    """Agrega las columnas fecha_inicio y fecha_fin a la tabla"""
    with app.app_context():
        try:
            # Verificar si las columnas ya existen
            inspector = db.inspect(db.engine)
            columnas_existentes = [col['name'] for col in inspector.get_columns('envios_programados_dian_vs_erp')]
            
            cambios_realizados = []
            
            # Agregar fecha_inicio si no existe
            if 'fecha_inicio' not in columnas_existentes:
                print("➕ Agregando columna fecha_inicio...")
                db.session.execute(db.text("""
                    ALTER TABLE envios_programados_dian_vs_erp
                    ADD COLUMN fecha_inicio DATE DEFAULT NULL
                """))
                cambios_realizados.append("fecha_inicio")
                print("   ✅ Columna fecha_inicio agregada")
            else:
                print("   ℹ️  Columna fecha_inicio ya existe")
            
            # Agregar fecha_fin si no existe
            if 'fecha_fin' not in columnas_existentes:
                print("➕ Agregando columna fecha_fin...")
                db.session.execute(db.text("""
                    ALTER TABLE envios_programados_dian_vs_erp
                    ADD COLUMN fecha_fin DATE DEFAULT NULL
                """))
                cambios_realizados.append("fecha_fin")
                print("   ✅ Columna fecha_fin agregada")
            else:
                print("   ℹ️  Columna fecha_fin ya existe")
            
            # Commit de cambios
            if cambios_realizados:
                db.session.commit()
                print(f"\n✅ MIGRACIÓN COMPLETADA - {len(cambios_realizados)} columnas agregadas")
                print(f"   Columnas: {', '.join(cambios_realizados)}")
            else:
                print("\nℹ️  NO SE REQUIRIERON CAMBIOS - Todas las columnas ya existen")
            
            # Mostrar estructura actual de la tabla
            print("\n📋 ESTRUCTURA ACTUAL DE LA TABLA:")
            columnas = inspector.get_columns('envios_programados_dian_vs_erp')
            for col in columnas:
                tipo = str(col['type'])
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f"DEFAULT {col['default']}" if col['default'] else ""
                print(f"   • {col['name']:<30} {tipo:<20} {nullable:<10} {default}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    print("="*80)
    print("MIGRACIÓN: Agregar columnas de fecha a envios_programados_dian_vs_erp")
    print("="*80 + "\n")
    
    exito = agregar_columnas_fecha()
    
    if exito:
        print("\n✅ MIGRACIÓN EXITOSA")
        print("\nℹ️  Ahora puedes:")
        print("   1. Reiniciar el servidor Flask")
        print("   2. Crear/editar configuraciones con filtros de fecha")
        print("   3. Los envíos programados aplicarán los filtros automáticamente")
    else:
        print("\n❌ MIGRACIÓN FALLIDA")
        sys.exit(1)
