#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla terceros
"""

from app import app, db, Tercero

def verificar_estructura_terceros():
    """Verifica la estructura de la tabla terceros"""
    with app.app_context():
        try:
            print("=== ESTRUCTURA DE LA TABLA TERCEROS ===")
            print(f"Tabla: {Tercero.__tablename__}")
            print("\nColumnas disponibles:")
            
            for i, col in enumerate(Tercero.__table__.columns, 1):
                print(f"{i:2}. {col.name:<20} -> {col.type}")
            
            print(f"\nTotal de columnas: {len(Tercero.__table__.columns)}")
            
            # Verificar si tiene campo activo
            columnas = [col.name for col in Tercero.__table__.columns]
            if 'activo' in columnas:
                print("\n✅ La tabla tiene campo 'activo'")
            else:
                print("\n❌ La tabla NO tiene campo 'activo'")
                print("💡 Campos que podrían usarse para estado:")
                campos_estado = ['estado', 'status', 'habilitado', 'enabled', 'vigente']
                for campo in campos_estado:
                    if campo in columnas:
                        print(f"   - {campo}")
            
            # Verificar algunos registros
            print("\n=== MUESTRA DE DATOS ===")
            terceros_muestra = Tercero.query.limit(3).all()
            
            for tercero in terceros_muestra:
                print(f"\nID: {tercero.id} | NIT: {tercero.nit} | {tercero.razon_social}")
                for col in Tercero.__table__.columns:
                    valor = getattr(tercero, col.name, 'N/A')
                    if valor is not None:
                        if hasattr(valor, 'strftime'):  # Es datetime
                            valor = valor.strftime('%Y-%m-%d %H:%M')
                        print(f"  {col.name}: {valor}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verificar_estructura_terceros()