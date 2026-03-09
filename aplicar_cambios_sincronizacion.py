"""
Script para aplicar cambios de sincronización en tiempo real
Ejecuta el SQL de actualización de base de datos
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Leer DATABASE_URL del .env
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("❌ ERROR: DATABASE_URL no encontrado en .env")
    exit(1)

# Parsear la URL (formato: postgresql://user:pass@host:port/dbname)
from urllib.parse import urlparse
result = urlparse(database_url)
username = result.username
password = result.password
database = result.path[1:]  # Quitar el / inicial
hostname = result.hostname
port = result.port

print("=" * 80)
print("APLICACIÓN DE CAMBIOS PARA SINCRONIZACIÓN EN TIEMPO REAL")
print("=" * 80)
print(f"Base de datos: {database}")
print(f"Host: {hostname}:{port}")
print()

try:
    # Conectar a PostgreSQL
    conn = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )
    
    cur = conn.cursor()
    
    print("✅ Conexión exitosa a PostgreSQL")
    print()
    
    # Leer el archivo SQL
    sql_file = 'sql/actualizar_maestro_dian_para_sincronizacion.sql'
    
    if not os.path.exists(sql_file):
        print(f"❌ ERROR: No se encontró el archivo {sql_file}")
        exit(1)
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_completo = f.read()
    
    # Ejecutar todo el SQL de una vez (PostgreSQL maneja transacciones automáticamente)
    print(f"📄 Ejecutando script SQL completo...")
    print()
    
    try:
        # Ejecutar todo el script
        cur.execute(sql_completo)
        conn.commit()
        
        print("  ✅ Script SQL ejecutado correctamente")
        print()
        
        sentencias_exitosas = 1
        sentencias_fallidas = 0
        
    except psycopg2.Error as e:
        print(f"  ❌ ERROR: {e}")
        sentencias_fallidas = 1
        sentencias_exitosas = 0
        conn.rollback()
    
    cur.close()
    conn.close()
    
    print()
    print("=" * 80)
    print("RESUMEN DE EJECUCIÓN")
    print("=" * 80)
    print(f"✅ Sentencias exitosas: {sentencias_exitosas}")
    print(f"❌ Sentencias fallidas: {sentencias_fallidas}")
    print()
    
    if sentencias_fallidas == 0:
        print("🎉 ¡Base de datos actualizada correctamente!")
        print()
        print("📋 CAMBIOS APLICADOS:")
        print("   1. ✅ Campos agregados a maestro_dian_vs_erp:")
        print("      - usuario_recibio")
        print("      - origen_sincronizacion")
        print("      - rechazada")
        print("      - motivo_rechazo")
        print("      - fecha_rechazo")
        print()
        print("   2. ✅ Campos agregados a relaciones_facturas:")
        print("      - rechazada")
        print("      - motivo_rechazo")
        print("      - fecha_rechazo")
        print("      - usuario_rechazo")
        print()
        print("   3. ✅ Campos agregados a documentos_causacion:")
        print("      - tiene_novedad")
        print("      - descripcion_novedad")
        print("      - fecha_novedad")
        print("      - usuario_novedad")
        print("      - novedad_resuelta")
        print()
        print("   4. ✅ Índices creados:")
        print("      - idx_maestro_clave (nit_emisor, prefijo, folio)")
        print("      - idx_maestro_origen (origen_sincronizacion)")
        print()
        print("   5. ✅ Tabla creada:")
        print("      - logs_sincronizacion")
        print()
        print("🚀 El sistema está listo para sincronización en TIEMPO REAL")
    else:
        print("⚠️  Algunas sentencias fallaron. Revisa los errores arriba.")
    
    print("=" * 80)

except psycopg2.Error as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")
    exit(1)

except Exception as e:
    print(f"❌ ERROR INESPERADO: {e}")
    exit(1)
