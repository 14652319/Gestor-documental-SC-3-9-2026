from app import app, db
from sqlalchemy import text

with app.app_context():
    # Ver tablas de tokens
    print("=" * 60)
    print("TABLAS DE TOKENS EN LA BASE DE DATOS")
    print("=" * 60)
    
    tablas = db.session.execute(text("SELECT tablename FROM pg_tables WHERE tablename LIKE '%token%'")).fetchall()
    print(f"\nTablas encontradas: {[t[0] for t in tablas]}")
    
    # Verificar estructura de tokens_password
    print("\n" + "=" * 60)
    print("ESTRUCTURA DE LA TABLA tokens_password")
    print("=" * 60)
    
    columnas = db.session.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'tokens_password'
    """)).fetchall()
    
    for col in columnas:
        print(f"  - {col[0]}: {col[1]}")
    
    # Ver últimos tokens creados
    print("\n" + "=" * 60)
    print("ÚLTIMOS 5 TOKENS CREADOS")
    print("=" * 60)
    
    tokens = db.session.execute(text("""
        SELECT tp.id, tp.token, tp.usuario_id, u.usuario, u.tercero_id, 
               tp.fecha_creacion, tp.expiracion, tp.usado
        FROM tokens_password tp
        JOIN usuarios u ON u.id = tp.usuario_id
        ORDER BY tp.fecha_creacion DESC
        LIMIT 5
    """)).fetchall()
    
    if tokens:
        for t in tokens:
            print(f"\n  Token ID: {t[0]}")
            print(f"  Token: {t[1]}")
            print(f"  Usuario ID: {t[2]} | Usuario: {t[3]} | Tercero ID: {t[4]}")
            print(f"  Creado: {t[5]}")
            print(f"  Expira: {t[6]}")
            print(f"  Usado: {t[7]}")
    else:
        print("\n  No hay tokens en la base de datos")
    
    # Verificar contraseña del usuario admin con NIT 805028041
    print("\n" + "=" * 60)
    print("USUARIO ADMIN - NIT 805028041")
    print("=" * 60)
    
    admin = db.session.execute(text("""
        SELECT u.id, u.usuario, u.password_hash, u.activo, u.rol, t.nit, t.razon_social
        FROM usuarios u
        LEFT JOIN terceros t ON t.id = u.tercero_id
        WHERE u.usuario = 'admin' AND t.nit = '805028041'
    """)).fetchone()
    
    if admin:
        print(f"\n  Usuario ID: {admin[0]}")
        print(f"  Usuario: {admin[1]}")
        print(f"  Password Hash: {admin[2][:50]}... (truncado)")
        print(f"  Activo: {admin[3]}")
        print(f"  Rol: {admin[4]}")
        print(f"  NIT: {admin[5]}")
        print(f"  Razón Social: {admin[6]}")
        
        # Verificar si la contraseña es Admin123456$
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        
        test_passwords = ['Admin12345$', 'Admin123456$']
        print(f"\n  VERIFICACIÓN DE CONTRASEÑAS:")
        for pwd in test_passwords:
            match = bcrypt.check_password_hash(admin[2], pwd)
            print(f"    - '{pwd}': {'✅ COINCIDE' if match else '❌ NO COINCIDE'}")
    else:
        print("\n  ❌ No se encontró usuario 'admin' con NIT 805028041")
