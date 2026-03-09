"""
Script para consultar la estructura de las tablas de permisos
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    print("\n" + "="*80)
    print("📋 ESTRUCTURA DE LAS TABLAS DE PERMISOS")
    print("="*80)
    
    # Estructura de permisos_usuarios
    print("\n1️⃣ TABLA: permisos_usuarios (ACTIVA)")
    print("-" * 80)
    result = db.session.execute(text("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'permisos_usuarios' 
        ORDER BY ordinal_position
    """))
    for row in result:
        col_name, data_type, max_len, nullable = row
        len_str = f"({max_len})" if max_len else ""
        null_str = "NULL" if nullable == "YES" else "NOT NULL"
        print(f"  - {col_name}: {data_type}{len_str} {null_str}")
    
    # Muestra de datos
    print("\n  📊 Muestra de 5 registros:")
    result = db.session.execute(text("""
        SELECT id, usuario_id, modulo, accion, permitido 
        FROM permisos_usuarios 
        LIMIT 5
    """))
    for row in result:
        print(f"    ID={row[0]} | user={row[1]} | módulo={row[2]} | acción={row[3]} | permitido={row[4]}")
    
    # Contar registros
    result = db.session.execute(text("SELECT COUNT(*) FROM permisos_usuarios"))
    count = result.fetchone()[0]
    print(f"\n  ✅ Total registros: {count}")
    
    # Estructura de catalogo_permisos
    print("\n\n2️⃣ TABLA: catalogo_permisos (CATÁLOGO)")
    print("-" * 80)
    result = db.session.execute(text("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'catalogo_permisos' 
        ORDER BY ordinal_position
    """))
    for row in result:
        col_name, data_type, max_len, nullable = row
        len_str = f"({max_len})" if max_len else ""
        null_str = "NULL" if nullable == "YES" else "NOT NULL"
        print(f"  - {col_name}: {data_type}{len_str} {null_str}")
    
    # Muestra de datos
    print("\n  📊 Muestra de 10 permisos del catálogo:")
    result = db.session.execute(text("""
        SELECT id, modulo, accion, accion_descripcion, activo 
        FROM catalogo_permisos 
        WHERE activo = true
        LIMIT 10
    """))
    for row in result:
        print(f"    ID={row[0]} | módulo={row[1]} | acción={row[2]} | {row[3][:50]}... | activo={row[4]}")
    
    # Contar registros
    result = db.session.execute(text("SELECT COUNT(*) FROM catalogo_permisos WHERE activo = true"))
    count = result.fetchone()[0]
    print(f"\n  ✅ Total permisos activos en catálogo: {count}")
    
    # Módulos disponibles
    print("\n\n3️⃣ MÓDULOS EN catalogo_permisos:")
    print("-" * 80)
    result = db.session.execute(text("""
        SELECT DISTINCT modulo, COUNT(*) as total
        FROM catalogo_permisos 
        WHERE activo = true
        GROUP BY modulo
        ORDER BY modulo
    """))
    for row in result:
        print(f"  - {row[0]}: {row[1]} permisos")
    
    print("\n" + "="*80)
