"""
Script para ver usuarios firmadores configurados
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    print("\n📋 USUARIOS FIRMADORES POR DEPARTAMENTO:\n")
    print(f"{'DEPTO':<8} {'USUARIO':<20} {'CORREO':<35} {'EMAIL NOTIF':<35}")
    print("=" * 100)
    
    result = db.session.execute(text("""
        SELECT u.usuario, u.correo, u.email_notificaciones, ud.departamento, ud.puede_firmar
        FROM usuarios u
        INNER JOIN usuario_departamento ud ON u.id = ud.usuario_id
        WHERE ud.puede_firmar = true
        AND ud.activo = true
        AND u.activo = true
        ORDER BY ud.departamento, u.usuario
    """)).fetchall()
    
    if not result:
        print("⚠️  NO HAY USUARIOS FIRMADORES CONFIGURADOS")
    else:
        for row in result:
            usuario, correo, email_notif, depto, puede_firmar = row
            print(f"{depto:<8} {usuario:<20} {correo or 'N/A':<35} {email_notif or 'N/A':<35}")
        
        print(f"\n✅ Total: {len(result)} firmadores configurados")
        
        # Verificar departamentos sin firmadores
        print("\n\n📊 RESUMEN POR DEPARTAMENTO:")
        deptos = {}
        for row in result:
            depto = row[3]
            if depto not in deptos:
                deptos[depto] = 0
            deptos[depto] += 1
        
        for depto, count in sorted(deptos.items()):
            print(f"  {depto}: {count} firmador(es)")
