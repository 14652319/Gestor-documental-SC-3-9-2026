"""
Script para listar usuarios y sus NITs
"""
from extensions import db
from sqlalchemy import text
from app import app

with app.app_context():
    result = db.session.execute(text("""
        SELECT u.id, u.usuario, t.nit, t.razon_social, u.activo
        FROM usuarios u
        JOIN terceros t ON u.tercero_id = t.id
        ORDER BY u.usuario
    """))
    
    usuarios = result.fetchall()
    
    print("\n📋 LISTADO DE USUARIOS:")
    print("=" * 80)
    print(f"{'ID':<5} {'Usuario':<20} {'NIT':<15} {'Razón Social':<30} {'Activo':<10}")
    print("-" * 80)
    
    for uid, usuario, nit, razon, activo in usuarios:
        estado = "✅" if activo else "❌"
        print(f"{uid:<5} {usuario:<20} {nit:<15} {razon[:28]:<30} {estado:<10}")
    
    print("=" * 80)
    print(f"\nTotal usuarios: {len(usuarios)}\n")
