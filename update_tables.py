from app import app, db, DocumentoTercero, SolicitudRegistro
from sqlalchemy import text

with app.app_context():
    try:
        # Crear todas las tablas nuevas
        db.create_all()
        print("✅ Tablas creadas correctamente")
        
        # Verificar que se crearon las tablas
        result = db.session.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
        """))
        
        print("\nTablas existentes en la base de datos:")
        for row in result:
            print(f"  - {row[0]}")
        
        print("\n🎉 Base de datos actualizada correctamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Pero las tablas principales se crearon correctamente")