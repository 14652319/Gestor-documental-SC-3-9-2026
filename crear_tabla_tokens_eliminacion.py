"""
Crear tabla tokens_eliminacion_dian_erp
Fecha: 16 de Febrero de 2026
"""
from app import app, db
from modules.dian_vs_erp.models import TokenEliminacionDatos

with app.app_context():
    print("=" * 80)
    print("CREANDO TABLA tokens_eliminacion_dian_erp")
    print("=" * 80)
    
    try:
        db.create_all()
        print("✅ Tabla creada exitosamente")
        print()
        print("Estructura:")
        print("  - id (INTEGER, PRIMARY KEY)")
        print("  - token (VARCHAR(6), index)")
        print("  - usuario_solicitante (VARCHAR(100), index)")
        print("  - email_destino (VARCHAR(255))")
        print("  - tipo_rango (VARCHAR(20)): 'dias', 'meses', 'año'")
        print("  - fecha_inicio (DATE)")
        print("  - fecha_fin (DATE)")
        print("  - archivos_eliminar (TEXT): JSON array")
        print("  - usado (BOOLEAN, index)")
        print("  - fecha_creacion (TIMESTAMP)")
        print("  - fecha_expiracion (TIMESTAMP)")
        print("  - fecha_uso (TIMESTAMP)")
        print("  - registros_eliminados (INTEGER)")
        print("  - resultado_json (TEXT)")
        print("  - ip_solicitud (VARCHAR(50))")
        print("  - ip_confirmacion (VARCHAR(50))")
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
