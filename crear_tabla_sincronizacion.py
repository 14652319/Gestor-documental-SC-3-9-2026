"""
Script para crear la tabla de log de sincronizaciones del visor
"""
from app import app, db
from sqlalchemy import text

print("\n" + "="*80)
print("🔧 CREANDO TABLA LOG_SINCRONIZACION_VISOR")
print("="*80)

with app.app_context():
    try:
        # Leer el script SQL
        with open('crear_tabla_log_sincronizacion.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Ejecutar cada comando SQL
        for comando in sql_script.split(';'):
            comando = comando.strip()
            if comando:
                print(f"\n📝 Ejecutando: {comando[:80]}...")
                db.session.execute(text(comando))
        
        db.session.commit()
        
        print("\n✅ TABLA CREADA EXITOSAMENTE")
        
        # Verificar que existe
        result = db.session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'log_sincronizacion_visor'
            ORDER BY ordinal_position
        """))
        
        print("\n📊 ESTRUCTURA DE LA TABLA:")
        print("-"*80)
        for row in result:
            print(f"   {row[0]:30} {row[1]}")
        
        print("\n" + "="*80)
        print("✅ TODO LISTO - Tabla creada y verificada")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.session.rollback()
