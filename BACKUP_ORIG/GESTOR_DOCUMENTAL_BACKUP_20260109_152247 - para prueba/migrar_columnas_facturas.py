# -*- coding: utf-8 -*-
"""
Script de migración SEGURO - Agregar columnas para usuarios externos
GARANTÍA: Solo agrega columnas si NO existen, no toca las existentes
"""

from app import app, db
from sqlalchemy import text
import sys

def verificar_y_agregar_columnas():
    """
    Verifica y agrega columnas faltantes de forma SEGURA
    """
    with app.app_context():
        try:
            # Obtener conexión
            connection = db.engine.connect()
            
            print("=" * 80)
            print("🔍 VERIFICANDO COLUMNAS EN 'facturas_digitales'...")
            print("=" * 80)
            
            # Consultar columnas existentes
            result = connection.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'facturas_digitales'
                ORDER BY ordinal_position;
            """))
            
            columnas_existentes = {row[0]: row for row in result}
            
            print(f"\n✅ Total de columnas encontradas: {len(columnas_existentes)}")
            print("\n📋 Columnas existentes:")
            for nombre, info in columnas_existentes.items():
                print(f"   - {nombre}: {info[1]} (nullable: {info[2]})")
            
            # Definir columnas que necesitamos
            columnas_necesarias = {
                'tipo_documento': "ALTER TABLE facturas_digitales ADD COLUMN tipo_documento VARCHAR(30);",
                'tipo_servicio': "ALTER TABLE facturas_digitales ADD COLUMN tipo_servicio VARCHAR(50);",
                'departamento': "ALTER TABLE facturas_digitales ADD COLUMN departamento VARCHAR(50);",
                'forma_pago': "ALTER TABLE facturas_digitales ADD COLUMN forma_pago VARCHAR(30);",
                'ruta_carpeta': "ALTER TABLE facturas_digitales ADD COLUMN ruta_carpeta TEXT;",
            }
            
            print("\n" + "=" * 80)
            print("🔧 VERIFICANDO COLUMNAS REQUERIDAS...")
            print("=" * 80)
            
            columnas_a_agregar = []
            
            for columna, sql in columnas_necesarias.items():
                if columna in columnas_existentes:
                    print(f"\n✅ '{columna}' YA EXISTE - No se modificará")
                else:
                    print(f"\n⚠️  '{columna}' NO EXISTE - Se agregará")
                    columnas_a_agregar.append((columna, sql))
            
            # Si no hay columnas que agregar
            if not columnas_a_agregar:
                print("\n" + "=" * 80)
                print("✅ TODAS LAS COLUMNAS YA EXISTEN")
                print("=" * 80)
                print("\n✨ La base de datos está actualizada. No se requieren cambios.")
                return True
            
            # Confirmar antes de agregar
            print("\n" + "=" * 80)
            print(f"📝 SE AGREGARÁN {len(columnas_a_agregar)} COLUMNAS:")
            print("=" * 80)
            for columna, _ in columnas_a_agregar:
                print(f"   - {columna}")
            
            print("\n⚠️  IMPORTANTE:")
            print("   • Esto NO modificará las columnas existentes")
            print("   • Los registros actuales NO se verán afectados")
            print("   • Las nuevas columnas permitirán valores NULL")
            print("   • Es una operación SEGURA y REVERSIBLE")
            
            respuesta = input("\n¿Deseas continuar? (s/n): ").strip().lower()
            
            if respuesta != 's':
                print("\n❌ Operación cancelada por el usuario")
                return False
            
            # Ejecutar migraciones
            print("\n" + "=" * 80)
            print("🚀 EJECUTANDO MIGRACIONES...")
            print("=" * 80)
            
            for columna, sql in columnas_a_agregar:
                try:
                    print(f"\n📌 Agregando columna '{columna}'...")
                    connection.execute(text(sql))
                    connection.commit()
                    print(f"   ✅ Columna '{columna}' agregada exitosamente")
                except Exception as e:
                    print(f"   ❌ Error al agregar '{columna}': {str(e)}")
                    connection.rollback()
                    return False
            
            # Verificar resultado final
            print("\n" + "=" * 80)
            print("🔍 VERIFICACIÓN FINAL...")
            print("=" * 80)
            
            result = connection.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'facturas_digitales'
                ORDER BY ordinal_position;
            """))
            
            columnas_finales = [row[0] for row in result]
            
            print(f"\n✅ Total de columnas después de migración: {len(columnas_finales)}")
            
            # Verificar que todas las requeridas existen
            faltantes = []
            for columna in columnas_necesarias.keys():
                if columna in columnas_finales:
                    print(f"   ✅ '{columna}' - Confirmada")
                else:
                    print(f"   ❌ '{columna}' - FALTA")
                    faltantes.append(columna)
            
            if faltantes:
                print(f"\n❌ ERROR: Faltan columnas: {', '.join(faltantes)}")
                return False
            
            print("\n" + "=" * 80)
            print("✨ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print("\n✅ La base de datos está lista para el sistema de usuarios externos")
            print("✅ Puedes reiniciar el servidor y probar la funcionalidad")
            
            connection.close()
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("\n🔧 SCRIPT DE MIGRACIÓN SEGURA - FACTURAS DIGITALES")
    print("=" * 80)
    
    exito = verificar_y_agregar_columnas()
    
    if exito:
        print("\n✅ Script ejecutado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Script terminó con errores")
        sys.exit(1)
