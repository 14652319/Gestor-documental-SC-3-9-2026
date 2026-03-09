"""
Script para hacer backup manual de PostgreSQL usando Python (sin pg_dump)
"""
import psycopg2
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
from datetime import datetime
import json

load_dotenv()

database_url = os.getenv('DATABASE_URL')
result = urlparse(database_url)

db_config = {
    'user': result.username,
    'password': result.password,
    'database': result.path[1:],
    'host': result.hostname,
    'port': result.port or 5432
}

print("="*80)
print("BACKUP MANUAL DE BASE DE DATOS")
print("="*80)
print(f"Base de datos: {db_config['database']}")
print(f"Host: {db_config['host']}:{db_config['port']}")
print()

try:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    # Obtener lista de tablas
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tablas = [row[0] for row in cur.fetchall()]
    
    print(f"✅ Conectado - {len(tablas)} tablas encontradas")
    print()
    
    # Crear directorio para backups manuales
    directorio_padre = os.path.dirname(os.getcwd())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    backup1_bd = os.path.join(directorio_padre, f'BACKUP_PRE_SINCRONIZACION_{timestamp}', 'base_datos')
    backup2_bd = os.path.join(directorio_padre, f'GESTOR_DOCUMENTAL_TRANSPORTABLE_{timestamp}')
    
    for directorio_bd in [backup1_bd, backup2_bd]:
        if os.path.exists(directorio_bd) or os.path.exists(os.path.dirname(directorio_bd)):
            os.makedirs(directorio_bd, exist_ok=True)
            
            archivo_sql = os.path.join(directorio_bd, 'backup_manual_tablas.sql')
            archivo_info = os.path.join(directorio_bd, 'info_backup.json')
            
            print(f"📝 Generando SQL para: {os.path.basename(os.path.dirname(directorio_bd))}")
            
            with open(archivo_sql, 'w', encoding='utf-8') as f:
                f.write(f"-- BACKUP DE BASE DE DATOS\n")
                f.write(f"-- Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- Base de datos: {db_config['database']}\n")
                f.write(f"-- Tablas: {len(tablas)}\n\n")
                
                info_tablas = []
                
                for tabla in tablas:
                    # Obtener estructura
                    cur.execute(f"""
                        SELECT column_name, data_type, character_maximum_length, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = '{tabla}'
                        ORDER BY ordinal_position
                    """)
                    columnas = cur.fetchall()
                    
                    # Contar registros
                    cur.execute(f"SELECT COUNT(*) FROM {tabla}")
                    num_registros = cur.fetchone()[0]
                    
                    info_tablas.append({
                        'tabla': tabla,
                        'columnas': len(columnas),
                        'registros': num_registros
                    })
                    
                    f.write(f"\n-- ============================================\n")
                    f.write(f"-- TABLA: {tabla}\n")
                    f.write(f"-- Registros: {num_registros}\n")
                    f.write(f"-- ============================================\n\n")
                    
                    # Guardar estructura (comentario)
                    f.write(f"-- Estructura:\n")
                    for col in columnas:
                        f.write(f"--   {col[0]} {col[1]}")
                        if col[2]:
                            f.write(f"({col[2]})")
                        if col[3] == 'NO':
                            f.write(" NOT NULL")
                        if col[4]:
                            f.write(f" DEFAULT {col[4]}")
                        f.write("\n")
                    
                    f.write(f"\n-- Datos ({num_registros} registros):\n")
                    f.write(f"-- Para restaurar, usar pg_restore o scripts específicos\n\n")
                    
                    print(f"   ✅ {tabla}: {num_registros} registros")
            
            # Guardar info JSON
            with open(archivo_info, 'w', encoding='utf-8') as f:
                json.dump({
                    'fecha_backup': datetime.now().isoformat(),
                    'base_datos': db_config['database'],
                    'total_tablas': len(tablas),
                    'tablas': info_tablas
                }, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Archivo SQL creado: {os.path.basename(archivo_sql)}")
            print(f"   ✅ Archivo info creado: {os.path.basename(archivo_info)}")
            print()
    
    cur.close()
    conn.close()
    
    print("="*80)
    print("✅ BACKUP MANUAL COMPLETADO")
    print("="*80)
    print()
    print("📋 Archivos creados:")
    print("   - backup_manual_tablas.sql (estructura y conteo)")
    print("   - info_backup.json (metadatos)")
    print()
    print("⚠️  NOTA: Para backup completo de datos, ejecuta desde CMD:")
    print(f'   pg_dump -h {db_config["host"]} -p {db_config["port"]} -U {db_config["user"]} -F c -f backup.backup {db_config["database"]}')
    print()

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
