#!/usr/bin/env python3
"""
Script para crear las tablas del módulo DIAN vs ERP
Ejecuta el schema SQL y verifica la creación exitosa

Uso: python crear_tablas_dian_vs_erp.py
"""

import os
import sys
import psycopg2
from datetime import datetime

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gestor_documental', 
    'user': 'gestor_user',
    'password': 'gestor_password'
}

def log_message(message, level="INFO"):
    """Registra un mensaje con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {level}: {message}")

def ejecutar_sql_desde_archivo(cursor, archivo_sql):
    """Ejecuta comandos SQL desde un archivo"""
    try:
        with open(archivo_sql, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Ejecutar el contenido SQL
        cursor.execute(sql_content)
        log_message(f"✅ Archivo SQL ejecutado exitosamente: {archivo_sql}")
        return True
        
    except FileNotFoundError:
        log_message(f"❌ Archivo no encontrado: {archivo_sql}", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ Error ejecutando SQL: {str(e)}", "ERROR")
        return False

def verificar_tablas_creadas(cursor):
    """Verifica que las tablas fueron creadas correctamente"""
    tablas_esperadas = [
        'reportes_dian',
        'facturas_erp', 
        'validaciones_facturas',
        'procesamientos_periodo',
        'configuracion_validacion'
    ]
    
    tablas_creadas = []
    tablas_faltantes = []
    
    for tabla in tablas_esperadas:
        try:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{tabla}'
                );
            """)
            
            existe = cursor.fetchone()[0]
            if existe:
                tablas_creadas.append(tabla)
            else:
                tablas_faltantes.append(tabla)
                
        except Exception as e:
            log_message(f"Error verificando tabla {tabla}: {str(e)}", "ERROR")
            tablas_faltantes.append(tabla)
    
    return tablas_creadas, tablas_faltantes

def obtener_estadisticas_tablas(cursor):
    """Obtiene estadísticas básicas de las tablas creadas"""
    estadisticas = {}
    
    tablas = [
        'reportes_dian',
        'facturas_erp',
        'validaciones_facturas', 
        'procesamientos_periodo',
        'configuracion_validacion'
    ]
    
    for tabla in tablas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla};")
            count = cursor.fetchone()[0]
            estadisticas[tabla] = count
        except Exception as e:
            log_message(f"Error obteniendo estadísticas de {tabla}: {str(e)}", "WARNING")
            estadisticas[tabla] = "Error"
    
    return estadisticas

def verificar_vista_creada(cursor):
    """Verifica que la vista de estadísticas fue creada"""
    try:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.views 
                WHERE table_schema = 'public' 
                AND table_name = 'v_estadisticas_validacion'
            );
        """)
        
        existe = cursor.fetchone()[0]
        if existe:
            # Probar ejecutar la vista
            cursor.execute("SELECT * FROM v_estadisticas_validacion;")
            resultado = cursor.fetchone()
            log_message("✅ Vista v_estadisticas_validacion creada y funcional")
            return True
        else:
            log_message("❌ Vista v_estadisticas_validacion no encontrada", "ERROR")
            return False
            
    except Exception as e:
        log_message(f"❌ Error verificando vista: {str(e)}", "ERROR")
        return False

def main():
    """Función principal"""
    log_message("🚀 Iniciando creación de tablas para módulo DIAN vs ERP")
    
    # Verificar que el archivo SQL existe
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(script_dir, 'sql', 'dian_vs_erp_schema.sql')
    
    if not os.path.exists(sql_file):
        log_message(f"❌ Archivo SQL no encontrado: {sql_file}", "ERROR")
        sys.exit(1)
    
    try:
        # Conectar a la base de datos
        log_message("📡 Conectando a la base de datos...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        log_message("✅ Conexión exitosa a PostgreSQL")
        
        # Ejecutar el script SQL
        log_message("📝 Ejecutando script de creación de tablas...")
        if not ejecutar_sql_desde_archivo(cursor, sql_file):
            sys.exit(1)
        
        # Confirmar cambios
        conn.commit()
        log_message("💾 Cambios confirmados en la base de datos")
        
        # Verificar tablas creadas
        log_message("🔍 Verificando tablas creadas...")
        tablas_creadas, tablas_faltantes = verificar_tablas_creadas(cursor)
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE CREACIÓN DE TABLAS")
        print("="*60)
        
        if tablas_creadas:
            print(f"✅ Tablas creadas exitosamente ({len(tablas_creadas)}):")
            for tabla in tablas_creadas:
                print(f"   • {tabla}")
        
        if tablas_faltantes:
            print(f"\n❌ Tablas faltantes ({len(tablas_faltantes)}):")
            for tabla in tablas_faltantes:
                print(f"   • {tabla}")
        
        # Verificar vista
        print(f"\n🔍 Verificando vista...")
        vista_ok = verificar_vista_creada(cursor)
        
        # Obtener estadísticas
        print(f"\n📈 Estadísticas de tablas:")
        stats = obtener_estadisticas_tablas(cursor)
        for tabla, count in stats.items():
            print(f"   • {tabla}: {count} registros")
        
        print("\n" + "="*60)
        
        if len(tablas_faltantes) == 0 and vista_ok:
            print("🎉 ¡Módulo DIAN vs ERP instalado exitosamente!")
            print("\n📍 Accede al módulo en: http://localhost:8099/dian_vs_erp/")
            print("🚀 Para activar el módulo, reinicia la aplicación Flask")
        else:
            print("⚠️  Instalación completada con advertencias")
            sys.exit(1)
            
    except psycopg2.Error as e:
        log_message(f"❌ Error de PostgreSQL: {str(e)}", "ERROR")
        sys.exit(1)
        
    except Exception as e:
        log_message(f"❌ Error inesperado: {str(e)}", "ERROR")
        sys.exit(1)
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        log_message("🔌 Conexión a base de datos cerrada")

if __name__ == "__main__":
    main()