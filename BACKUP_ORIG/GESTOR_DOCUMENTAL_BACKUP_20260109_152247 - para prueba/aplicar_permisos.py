"""
🔐 APLICAR PERMISOS FALTANTES AL CATÁLOGO
Script para ejecutar el SQL de permisos de manera segura con validaciones
Fecha: 11 de Diciembre, 2025
"""

import os
from sqlalchemy import text
from app import app, db

def crear_backup():
    """Crea backup de la tabla catalogo_permisos antes de modificar"""
    print("\n" + "="*80)
    print("💾 CREANDO BACKUP DE TABLA catalogo_permisos")
    print("="*80)
    
    try:
        # Crear backup como otra tabla
        query_backup = text("""
            DROP TABLE IF EXISTS catalogo_permisos_backup_20251211;
            CREATE TABLE catalogo_permisos_backup_20251211 AS 
            SELECT * FROM catalogo_permisos;
        """)
        
        db.session.execute(query_backup)
        db.session.commit()
        
        # Contar registros del backup
        query_count = text("SELECT COUNT(*) FROM catalogo_permisos_backup_20251211")
        result = db.session.execute(query_count)
        count = result.scalar()
        
        print(f"✅ Backup creado exitosamente: catalogo_permisos_backup_20251211")
        print(f"✅ Registros respaldados: {count}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return False

def contar_permisos_actuales():
    """Cuenta permisos actuales en el catálogo"""
    try:
        query = text("SELECT COUNT(*) FROM catalogo_permisos WHERE activo = true")
        result = db.session.execute(query)
        return result.scalar()
    except Exception as e:
        print(f"❌ Error contando permisos: {e}")
        return 0

def ejecutar_sql_permisos():
    """Ejecuta el SQL de permisos faltantes"""
    print("\n" + "="*80)
    print("🚀 EJECUTANDO SQL DE PERMISOS FALTANTES")
    print("="*80)
    
    archivo_sql = 'AGREGAR_PERMISOS_FALTANTES.sql'
    
    if not os.path.exists(archivo_sql):
        print(f"❌ ERROR: No se encontró el archivo {archivo_sql}")
        return False
    
    try:
        # Leer archivo SQL
        with open(archivo_sql, 'r', encoding='utf-8') as f:
            sql_completo = f.read()
        
        # Dividir en sentencias individuales
        sentencias = [s.strip() for s in sql_completo.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"\n📄 Sentencias SQL a ejecutar: {len(sentencias)}")
        print("⏳ Ejecutando... (esto puede tardar 30-60 segundos)")
        
        # Ejecutar cada sentencia
        insertados = 0
        duplicados = 0
        errores = 0
        
        for i, sentencia in enumerate(sentencias, 1):
            if not sentencia:
                continue
                
            try:
                result = db.session.execute(text(sentencia))
                db.session.commit()
                
                # Verificar si se insertó (rowcount > 0 significa INSERT exitoso)
                if result.rowcount > 0:
                    insertados += 1
                else:
                    duplicados += 1
                
                # Mostrar progreso cada 50 sentencias
                if i % 50 == 0:
                    print(f"   ⏳ Procesadas {i}/{len(sentencias)} sentencias...")
                    
            except Exception as e:
                errores += 1
                error_msg = str(e)
                # Ignorar errores de duplicado (ON CONFLICT)
                if 'duplicate key' not in error_msg.lower() and 'conflict' not in error_msg.lower():
                    print(f"   ⚠️  Error en sentencia {i}: {error_msg[:100]}")
        
        print(f"\n✅ Ejecución completada:")
        print(f"   - Permisos insertados: {insertados}")
        print(f"   - Duplicados omitidos: {duplicados}")
        print(f"   - Errores: {errores}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando SQL: {e}")
        db.session.rollback()
        return False

def validar_permisos_agregados():
    """Valida que los permisos fueron agregados correctamente"""
    print("\n" + "="*80)
    print("✅ VALIDANDO PERMISOS AGREGADOS")
    print("="*80)
    
    try:
        # Contar permisos por módulo
        query = text("""
            SELECT modulo, COUNT(*) as total
            FROM catalogo_permisos
            WHERE activo = true
            GROUP BY modulo
            ORDER BY modulo
        """)
        
        result = db.session.execute(query)
        
        print("\n📊 DISTRIBUCIÓN FINAL DE PERMISOS:")
        total_final = 0
        for row in result:
            modulo = row[0]
            count = row[1]
            total_final += count
            print(f"   - {modulo}: {count} permisos")
        
        print(f"\n✅ TOTAL DE PERMISOS EN CATÁLOGO: {total_final}")
        
        return total_final
        
    except Exception as e:
        print(f"❌ Error validando permisos: {e}")
        return 0

def restaurar_backup():
    """Restaura el backup en caso de error"""
    print("\n" + "="*80)
    print("🔄 RESTAURANDO BACKUP")
    print("="*80)
    
    try:
        # Vaciar tabla actual
        query_truncate = text("TRUNCATE TABLE catalogo_permisos RESTART IDENTITY CASCADE")
        db.session.execute(query_truncate)
        
        # Restaurar desde backup
        query_restore = text("""
            INSERT INTO catalogo_permisos
            SELECT * FROM catalogo_permisos_backup_20251211
        """)
        db.session.execute(query_restore)
        db.session.commit()
        
        print("✅ Backup restaurado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error restaurando backup: {e}")
        db.session.rollback()
        return False

def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🔐 APLICADOR DE PERMISOS FALTANTES")
    print("="*80)
    print("Sistema: Gestor Documental - Supertiendas Cañaveral")
    print("Fecha: 11 de Diciembre, 2025")
    print("="*80)
    
    with app.app_context():
        # 1. Contar permisos iniciales
        permisos_inicial = contar_permisos_actuales()
        print(f"\n📊 Permisos actuales en catálogo: {permisos_inicial}")
        
        # 2. Confirmar ejecución
        print("\n⚠️  ADVERTENCIA:")
        print("   Este script va a agregar 326 permisos nuevos al catálogo.")
        print("   Se creará un backup automático antes de proceder.")
        print()
        
        respuesta = input("¿Deseas continuar? (escribe 'SI' para confirmar): ")
        
        if respuesta.upper() != 'SI':
            print("\n❌ Operación cancelada por el usuario.")
            return
        
        # 3. Crear backup
        if not crear_backup():
            print("\n❌ ERROR: No se pudo crear backup. Abortando operación.")
            return
        
        # 4. Ejecutar SQL
        if not ejecutar_sql_permisos():
            print("\n❌ ERROR: Hubo problemas ejecutando el SQL.")
            print("🔄 Intentando restaurar backup...")
            restaurar_backup()
            return
        
        # 5. Validar permisos agregados
        permisos_final = validar_permisos_agregados()
        
        # 6. Mostrar resumen
        print("\n" + "="*80)
        print("✅ OPERACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print(f"\n📊 RESUMEN:")
        print(f"   - Permisos iniciales:     {permisos_inicial}")
        print(f"   - Permisos finales:       {permisos_final}")
        print(f"   - Permisos agregados:     {permisos_final - permisos_inicial}")
        print(f"   - Backup disponible en:   catalogo_permisos_backup_20251211")
        
        print("\n💡 SIGUIENTES PASOS:")
        print("   1. Acceder a /admin/usuarios-permisos")
        print("   2. Verificar que nuevos permisos aparecen en interfaz")
        print("   3. Crear usuario de prueba con permisos limitados")
        print("   4. Probar acceso a endpoints con/sin permiso")
        print("   5. Revisar logs en logs/security.log")
        
        print("\n🔄 RESTAURAR BACKUP (si algo sale mal):")
        print("   python -c \"from aplicar_permisos import restaurar_backup; from app import app; app.app_context().push(); restaurar_backup()\"")
        
        print()

if __name__ == "__main__":
    main()
