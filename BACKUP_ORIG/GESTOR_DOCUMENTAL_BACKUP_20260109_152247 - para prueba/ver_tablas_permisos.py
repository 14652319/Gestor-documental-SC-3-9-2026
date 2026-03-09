from app import app, db
from sqlalchemy import text

with app.app_context():
    # Listar todas las tablas que contienen 'permiso'
    result = db.session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name LIKE '%permiso%'
        ORDER BY table_name
    """))
    
    tablas = [row[0] for row in result]
    
    print('=' * 80)
    print('📋 TABLAS RELACIONADAS CON PERMISOS')
    print('=' * 80)
    print()
    
    for tabla in tablas:
        print(f'✅ {tabla}')
    
    print()
    print('=' * 80)
    print('📦 ESTRUCTURA DETALLADA DE CADA TABLA')
    print('=' * 80)
    
    for tabla in tablas:
        print(f'\n🔹 TABLA: {tabla}')
        print('-' * 80)
        
        result = db.session.execute(text(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = '{tabla}'
            ORDER BY ordinal_position
        """))
        
        print(f"{'COLUMNA':<30} {'TIPO':<20} {'NULL':<10} {'DEFAULT'}")
        print('-' * 80)
        
        for col in result:
            col_name, data_type, nullable, default = col
            default_str = str(default)[:30] if default else '-'
            print(f"{col_name:<30} {data_type:<20} {nullable:<10} {default_str}")
        
        # Contar registros
        count_result = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
        count = count_result.scalar()
        print(f"\n📊 Total de registros: {count}")
        
        # Ver sample de datos
        if count > 0 and count < 100:
            sample = db.session.execute(text(f"SELECT * FROM {tabla} LIMIT 3"))
            print(f"\n📋 Muestra de datos (primeros 3 registros):")
            for row in sample:
                print(f"   {dict(row._mapping)}")
    
    print()
    print('=' * 80)
