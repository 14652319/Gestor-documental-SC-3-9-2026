"""
Script para actualizar el catálogo de permisos en la base de datos
Fecha: 27 de Noviembre 2025
Autor: Sistema Automatizado

Este script:
1. Lee el catálogo de permisos desde models.py
2. Inserta/actualiza los permisos en la tabla catalogo_permisos
3. Mantiene sincronizado el código con la base de datos
"""

from app import app, db
from modules.admin.usuarios_permisos.models import CatalogoPermisos
from sqlalchemy import text
from datetime import datetime

def actualizar_catalogo():
    """Actualiza el catálogo de permisos en la base de datos"""
    
    print("=" * 80)
    print("ACTUALIZACIÓN DEL CATÁLOGO DE PERMISOS")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    with app.app_context():
        try:
            # Obtener catálogo desde el código
            catalogo = CatalogoPermisos.MODULOS
            
            total_modulos = len(catalogo)
            total_acciones = sum(len(mod['acciones']) for mod in catalogo.values())
            
            print(f"📊 Catálogo cargado:")
            print(f"   • {total_modulos} módulos")
            print(f"   • {total_acciones} acciones")
            print()
            
            # Verificar si la tabla existe
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'catalogo_permisos'
                )
            """))
            
            tabla_existe = result.scalar()
            
            if not tabla_existe:
                print("⚠️  La tabla 'catalogo_permisos' no existe.")
                print("   Creando tabla...")
                
                # Crear tabla
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS catalogo_permisos (
                        id SERIAL PRIMARY KEY,
                        modulo VARCHAR(50) NOT NULL,
                        modulo_nombre VARCHAR(100) NOT NULL,
                        modulo_descripcion TEXT,
                        accion VARCHAR(100) NOT NULL,
                        accion_descripcion TEXT,
                        tipo_accion VARCHAR(50),
                        es_critico BOOLEAN DEFAULT FALSE,
                        activo BOOLEAN DEFAULT TRUE,
                        fecha_creacion TIMESTAMP DEFAULT NOW(),
                        UNIQUE(modulo, accion)
                    )
                """))
                db.session.commit()
                print("   ✅ Tabla creada exitosamente")
                print()
            
            # Contadores
            insertados = 0
            actualizados = 0
            errores = 0
            
            print("🔄 Procesando permisos...")
            print()
            
            # Procesar cada módulo y sus acciones
            for modulo_key, modulo_data in catalogo.items():
                modulo_nombre = modulo_data['nombre']
                modulo_descripcion = modulo_data['descripcion']
                
                print(f"📦 Módulo: {modulo_nombre} ({modulo_key})")
                
                for accion_key, accion_data in modulo_data['acciones'].items():
                    try:
                        # Verificar si el permiso ya existe
                        result = db.session.execute(text("""
                            SELECT id FROM catalogo_permisos 
                            WHERE modulo = :modulo AND accion = :accion
                        """), {'modulo': modulo_key, 'accion': accion_key})
                        
                        existe = result.fetchone()
                        
                        if existe:
                            # Actualizar existente
                            db.session.execute(text("""
                                UPDATE catalogo_permisos 
                                SET modulo_nombre = :modulo_nombre,
                                    modulo_descripcion = :modulo_descripcion,
                                    accion_descripcion = :accion_descripcion,
                                    tipo_accion = :tipo_accion,
                                    es_critico = :es_critico,
                                    activo = TRUE
                                WHERE modulo = :modulo AND accion = :accion
                            """), {
                                'modulo': modulo_key,
                                'modulo_nombre': modulo_nombre,
                                'modulo_descripcion': modulo_descripcion,
                                'accion': accion_key,
                                'accion_descripcion': accion_data['descripcion'],
                                'tipo_accion': accion_data['tipo'],
                                'es_critico': accion_data['critico']
                            })
                            actualizados += 1
                            print(f"   ↻ {accion_key} - actualizado")
                        else:
                            # Insertar nuevo
                            db.session.execute(text("""
                                INSERT INTO catalogo_permisos 
                                (modulo, modulo_nombre, modulo_descripcion, accion, 
                                 accion_descripcion, tipo_accion, es_critico, activo)
                                VALUES 
                                (:modulo, :modulo_nombre, :modulo_descripcion, :accion,
                                 :accion_descripcion, :tipo_accion, :es_critico, TRUE)
                            """), {
                                'modulo': modulo_key,
                                'modulo_nombre': modulo_nombre,
                                'modulo_descripcion': modulo_descripcion,
                                'accion': accion_key,
                                'accion_descripcion': accion_data['descripcion'],
                                'tipo_accion': accion_data['tipo'],
                                'es_critico': accion_data['critico']
                            })
                            insertados += 1
                            print(f"   ➕ {accion_key} - insertado")
                    
                    except Exception as e:
                        errores += 1
                        print(f"   ❌ {accion_key} - ERROR: {str(e)}")
                
                print()
            
            # Commit de todos los cambios
            db.session.commit()
            
            # Resumen final
            print("=" * 80)
            print("✅ ACTUALIZACIÓN COMPLETADA")
            print("=" * 80)
            print(f"📊 Resultados:")
            print(f"   • Permisos insertados: {insertados}")
            print(f"   • Permisos actualizados: {actualizados}")
            print(f"   • Errores: {errores}")
            print(f"   • Total procesado: {insertados + actualizados + errores}")
            print()
            
            # Verificar total en BD
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM catalogo_permisos WHERE activo = TRUE
            """))
            total_bd = result.scalar()
            
            print(f"📦 Total de permisos activos en BD: {total_bd}")
            print()
            
            # Mostrar módulos disponibles
            result = db.session.execute(text("""
                SELECT DISTINCT modulo, modulo_nombre, COUNT(*) as acciones
                FROM catalogo_permisos 
                WHERE activo = TRUE
                GROUP BY modulo, modulo_nombre
                ORDER BY modulo
            """))
            
            print("📋 Módulos disponibles:")
            for row in result:
                print(f"   • {row[1]} ({row[0]}): {row[2]} acciones")
            
            print()
            print("=" * 80)
            print("🎉 Catálogo de permisos actualizado exitosamente")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR CRÍTICO: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    try:
        exito = actualizar_catalogo()
        if exito:
            print("\n✅ Proceso completado exitosamente")
        else:
            print("\n❌ Proceso completado con errores")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
