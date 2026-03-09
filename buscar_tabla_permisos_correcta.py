"""
Buscar la tabla correcta de permisos (la que tiene 600+)
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    print("\n" + "="*100)
    print("🔍 BUSCANDO TABLA CORRECTA DE PERMISOS")
    print("="*100 + "\n")
    
    # 1. Listar todas las tablas relacionadas
    print("📋 PASO 1: Tablas relacionadas con permisos/gestión/usuarios\n")
    result = db.session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        AND (table_name LIKE '%permiso%' 
             OR table_name LIKE '%gestion%' 
             OR table_name LIKE '%usuario%'
             OR table_name LIKE '%catalogo%')
        ORDER BY table_name
    """))
    
    tablas = [row[0] for row in result]
    for tabla in tablas:
        print(f"   📊 {tabla}")
    
    # 2. Contar registros en cada tabla de permisos
    print(f"\n📊 PASO 2: Contando registros en cada tabla de permisos\n")
    
    for tabla in tablas:
        if 'permiso' in tabla.lower() or 'catalogo' in tabla.lower():
            try:
                result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                count = result.scalar()
                
                # Ver estructura básica
                result = db.session.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='{tabla}' 
                    ORDER BY ordinal_position
                """))
                columnas = [row[0] for row in result]
                
                if count > 0:
                    print(f"   ✅ {tabla:40} → {count:4} registros")
                    print(f"      Columnas: {', '.join(columnas[:5])}{'...' if len(columnas) > 5 else ''}")
                    
                    # Si tiene más de 500, esta es la que buscamos
                    if count > 500:
                        print(f"      🎯 ¡ESTA ES LA TABLA PRINCIPAL! ({count} permisos)")
                        
                        # Ver muestra de datos
                        result = db.session.execute(text(f"SELECT * FROM {tabla} LIMIT 3"))
                        print(f"\n      📝 Muestra de datos:")
                        for row in result:
                            print(f"         {dict(row._mapping)}")
                else:
                    print(f"   ⚠️  {tabla:40} → VACÍA")
                    
                print()
            except Exception as e:
                print(f"   ❌ Error en {tabla}: {e}\n")
    
    # 3. Buscar específicamente tablas con "gestion_usuario" (singular y plural)
    print("🔍 PASO 3: Diferencia entre gestion_usuario vs gestion_usuarios\n")
    
    for nombre in ['gestion_usuario', 'gestion_usuarios']:
        result = db.session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = :nombre
            )
        """), {"nombre": nombre})
        
        existe = result.scalar()
        
        if existe:
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {nombre}"))
            count = result.scalar()
            
            result = db.session.execute(text(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='{nombre}' 
                ORDER BY ordinal_position
                LIMIT 10
            """))
            columnas = [row[0] for row in result]
            
            print(f"   {'✅' if count > 500 else '⚠️ '} {nombre:30} → {count:4} registros")
            print(f"      Columnas: {', '.join(columnas)}")
            
            if count > 0:
                result = db.session.execute(text(f"SELECT * FROM {nombre} LIMIT 2"))
                print(f"      Muestra:")
                for row in result:
                    print(f"         {dict(row._mapping)}")
            print()
        else:
            print(f"   ❌ {nombre:30} → NO EXISTE\n")
    
    print("="*100 + "\n")
