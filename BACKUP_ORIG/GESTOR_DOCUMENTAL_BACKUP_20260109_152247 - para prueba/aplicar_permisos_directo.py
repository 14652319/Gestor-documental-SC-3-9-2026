"""
Aplicar permisos directamente leyendo el archivo SQL línea por línea
"""
from sqlalchemy import text
from app import app, db

def aplicar_permisos():
    with app.app_context():
        print("🚀 Aplicando permisos...")
        
        # Leer archivo SQL
        with open('AGREGAR_PERMISOS_FALTANTES.sql', 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        # Procesar línea por línea
        sentencia_actual = []
        insertados = 0
        duplicados = 0
        errores = 0
        
        for linea in lineas:
            linea = linea.strip()
            
            # Ignorar comentarios y líneas vacías
            if not linea or linea.startswith('--'):
                continue
            
            # Acumular líneas de la sentencia
            sentencia_actual.append(linea)
            
            # Si termina con ;, ejecutar
            if linea.endswith(';'):
                sentencia = ' '.join(sentencia_actual)
                sentencia = sentencia.rstrip(';')
                
                if 'INSERT INTO' in sentencia:
                    try:
                        db.session.execute(text(sentencia))
                        db.session.commit()
                        insertados += 1
                        
                        if insertados % 50 == 0:
                            print(f"   ⏳ Insertados {insertados} permisos...")
                            
                    except Exception as e:
                        error_msg = str(e)
                        if 'duplicate' in error_msg.lower() or 'already exists' in error_msg.lower():
                            duplicados += 1
                        else:
                            errores += 1
                            print(f"   ⚠️ Error: {error_msg[:100]}")
                        db.session.rollback()
                
                sentencia_actual = []
        
        print(f"\n✅ COMPLETADO:")
        print(f"   - Insertados: {insertados}")
        print(f"   - Duplicados: {duplicados}")
        print(f"   - Errores: {errores}")
        
        # Contar total final
        result = db.session.execute(text("SELECT COUNT(*) FROM catalogo_permisos WHERE activo = true"))
        total = result.scalar()
        print(f"\n📊 TOTAL DE PERMISOS EN CATÁLOGO: {total}")

if __name__ == "__main__":
    aplicar_permisos()
