"""
Script para crear la tabla AlertaVencimiento en PostgreSQL
Ejecutar: python crear_tabla_alertas_vencimiento.py
"""
from app import app, db
from modules.sagrilaft.models import AlertaVencimiento

def crear_tabla_alertas():
    """Crea la tabla alertas_vencimiento_sagrilaft si no existe"""
    with app.app_context():
        try:
            # Crear tabla
            db.create_all()
            
            print("✅ Tabla 'alertas_vencimiento_sagrilaft' creada exitosamente")
            print("\nEstructura de la tabla:")
            print("  - id (INTEGER, PRIMARY KEY)")
            print("  - tercero_id (INTEGER, FK a terceros.id, INDEX)")
            print("  - radicado (VARCHAR(20), INDEX)")
            print("  - fecha_primera_alerta (TIMESTAMP, NULL)")
            print("  - fecha_recordatorio (TIMESTAMP, NULL)")
            print("  - recordatorio_enviado (BOOLEAN, DEFAULT FALSE)")
            print("  - fecha_creacion (TIMESTAMP, DEFAULT NOW)")
            print("  - fecha_actualizacion (TIMESTAMP)")
            print("\nÍndices:")
            print("  - idx_tercero_radicado (tercero_id, radicado)")
            
            # Verificar que la tabla existe
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'alertas_vencimiento_sagrilaft' in tables:
                print("\n✅ Verificación: Tabla existe en la base de datos")
            else:
                print("\n⚠️ Advertencia: No se pudo verificar la tabla")
            
        except Exception as e:
            print(f"❌ Error creando tabla: {e}")
            db.session.rollback()

if __name__ == '__main__':
    crear_tabla_alertas()
