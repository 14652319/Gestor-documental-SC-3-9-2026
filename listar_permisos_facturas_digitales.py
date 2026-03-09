"""
Script para listar todos los permisos únicos del módulo facturas_digitales
"""
from extensions import db
from sqlalchemy import text
from app import app

with app.app_context():
    # Obtener todos los permisos únicos del módulo facturas_digitales
    result = db.session.execute(text("""
        SELECT DISTINCT accion, 
               COUNT(DISTINCT usuario_id) as usuarios_con_permiso,
               SUM(CASE WHEN permitido = true THEN 1 ELSE 0 END) as usuarios_activos
        FROM permisos_usuarios
        WHERE modulo = 'facturas_digitales'
        GROUP BY accion
        ORDER BY accion
    """))
    
    permisos = result.fetchall()
    
    print("\n" + "=" * 80)
    print(" 📋 PERMISOS REGISTRADOS EN MÓDULO 'facturas_digitales'")
    print("=" * 80)
    
    if not permisos:
        print("\n⚠️  NO hay permisos registrados para este módulo")
    else:
        print(f"\n{'Acción':<40} {'Usuarios':<15} {'Activos':<10}")
        print("-" * 80)
        for accion, total, activos in permisos:
            print(f"{accion:<40} {total:<15} {activos:<10}")
        print("\n" + "=" * 80)
        print(f"Total de acciones únicas: {len(permisos)}\n")
