# -*- coding: utf-8 -*-
"""
APLICAR SISTEMA DE CARGA AUTOMÁTICA
Fecha: 30 de Diciembre de 2025
Propósito: Crear tablas y configurar sistema de carga automática de archivos
"""

import psycopg2
from psycopg2 import sql
from pathlib import Path

# Configuración de conexión
DB_CONFIG = {
    'dbname': 'gestor_documental',
    'user': 'gestor_user',
    'password': 'Gestor2024$',
    'host': 'localhost',
    'port': '5432'
}

def aplicar_cambios():
    """Aplica los cambios necesarios para el sistema de carga automática"""
    
    print("=" * 70)
    print("🚀 APLICANDO SISTEMA DE CARGA AUTOMÁTICA DE ARCHIVOS")
    print("=" * 70)
    
    try:
        # Conectar a PostgreSQL
        print("\n1️⃣ Conectando a PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cursor = conn.cursor()
        print("   ✅ Conexión establecida")
        
        # Leer script SQL
        print("\n2️⃣ Leyendo script SQL...")
        sql_path = Path(__file__).parent / 'sql' / 'carga_automatica_archivos.sql'
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        print("   ✅ Script leído correctamente")
        
        # Ejecutar script SQL
        print("\n3️⃣ Ejecutando cambios en base de datos...")
        cursor.execute(sql_script)
        conn.commit()
        print("   ✅ Tablas creadas correctamente:")
        print("      - archivos_procesados")
        print("      - configuracion_rutas_carga")
        
        # Verificar tablas creadas
        print("\n4️⃣ Verificando tablas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('archivos_procesados', 'configuracion_rutas_carga')
            ORDER BY table_name
        """)
        tablas = cursor.fetchall()
        
        if len(tablas) == 2:
            print("   ✅ Verificación exitosa:")
            for tabla in tablas:
                print(f"      - {tabla[0]}")
        else:
            print("   ⚠️ ADVERTENCIA: Se esperaban 2 tablas, se encontraron", len(tablas))
        
        # Verificar configuraciones insertadas
        print("\n5️⃣ Verificando configuraciones por defecto...")
        cursor.execute("""
            SELECT nombre_carpeta, tipo_archivo, activa, orden_procesamiento
            FROM configuracion_rutas_carga
            ORDER BY orden_procesamiento
        """)
        configs = cursor.fetchall()
        
        print(f"   ✅ Se encontraron {len(configs)} configuraciones:")
        for config in configs:
            nombre, tipo, activa, orden = config
            estado = "ACTIVA" if activa else "INACTIVA"
            print(f"      {orden}. {nombre:20} → {tipo:20} [{estado}]")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ APLICACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("\n📋 PRÓXIMOS PASOS:")
        print("\n1. Accede al módulo DIAN VS ERP desde el dashboard")
        print("2. Busca el botón '🚀 Carga Automática' en la interfaz")
        print("3. Haz clic en 'Escanear Archivos' para ver archivos pendientes")
        print("4. Selecciona archivos y haz clic en 'Procesar Seleccionados'")
        print("\n💡 NOTA: Los archivos se procesarán en este orden:")
        print("   1° DIAN")
        print("   2° ERP Financiero")
        print("   3° ERP Comercial")
        print("   4° Acuses")
        print("   5° Errores ERP")
        print("\n📁 Los archivos procesados se moverán automáticamente a:")
        print("   carpeta_origen/Procesados/YYYY-MM-DD/")
        print()
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Error de PostgreSQL: {e}")
        print(f"   Código de error: {e.pgcode}")
        if conn:
            conn.rollback()
            conn.close()
        return False
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: No se encontró el archivo SQL")
        print(f"   Ruta esperada: {sql_path}")
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == '__main__':
    aplicar_cambios()
    input("\n✅ Presiona Enter para cerrar...")
