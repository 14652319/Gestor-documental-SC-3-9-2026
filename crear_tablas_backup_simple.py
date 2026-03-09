import psycopg2

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='gestor_user',
    password='Temporal2024*',
    host='localhost',
    port=5432
)

cur = conn.cursor()

# Crear tabla configuracion_backup
cur.execute("""
CREATE TABLE IF NOT EXISTS configuracion_backup (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL UNIQUE,
    habilitado BOOLEAN DEFAULT TRUE,
    destino VARCHAR(500) NOT NULL,
    horario_cron VARCHAR(50) DEFAULT '0 2 * * *',
    dias_retencion INTEGER DEFAULT 7,
    ultima_ejecucion TIMESTAMP,
    proximo_backup TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Crear tabla historial_backup
cur.execute("""
CREATE TABLE IF NOT EXISTS historial_backup (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP,
    estado VARCHAR(20) NOT NULL,
    ruta_archivo VARCHAR(500),
    tamano_bytes BIGINT,
    duracion_segundos INTEGER,
    mensaje VARCHAR(1000),
    error VARCHAR(2000),
    usuario VARCHAR(50)
)
""")

# Insertar configuracion
cur.execute("""
INSERT INTO configuracion_backup (tipo, destino, horario_cron, dias_retencion, habilitado)
VALUES 
    ('base_datos', 'C:\\Backups_GestorDocumental\\base_datos', '0 2 * * *', 7, TRUE),
    ('archivos', 'C:\\Backups_GestorDocumental\\documentos', '0 3 * * *', 14, TRUE),
    ('codigo', 'C:\\Backups_GestorDocumental\\codigo', '0 4 * * 0', 30, TRUE)
ON CONFLICT (tipo) DO NOTHING
""")

conn.commit()
print('Tablas creadas exitosamente!')

# Verificar
cur.execute("SELECT tipo, habilitado FROM configuracion_backup ORDER BY tipo")
print('\nConfiguracion insertada:')
for row in cur.fetchall():
    print(f'  - {row[0]}: {"Habilitado" if row[1] else "Deshabilitado"}')

cur.close()
conn.close()
