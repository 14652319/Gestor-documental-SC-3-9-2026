import psycopg2
conn = psycopg2.connect('postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental')
cur = conn.cursor()

print("=== Verificando y corrigiendo tablas SAGRILAFT ===\n")

# 1. observaciones_radicado: agregar columna 'estado' si no existe
cur.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name='observaciones_radicado'
""")
cols_obs = [r[0] for r in cur.fetchall()]
print(f"observaciones_radicado columnas: {cols_obs}")

if 'estado' not in cols_obs:
    cur.execute("ALTER TABLE observaciones_radicado ADD COLUMN estado VARCHAR(50)")
    print("  -> Columna 'estado' agregada OK")
else:
    print("  -> Columna 'estado' ya existe OK")

# 2. estados_documentos: agregar UNIQUE en documento_id si no existe
cur.execute("""
    SELECT constraint_name FROM information_schema.table_constraints 
    WHERE table_name='estados_documentos' AND constraint_type='UNIQUE'
""")
constraints = [r[0] for r in cur.fetchall()]
print(f"\nestados_documentos constraints: {constraints}")

if not constraints:
    cur.execute("ALTER TABLE estados_documentos ADD CONSTRAINT uq_estados_doc UNIQUE (documento_id)")
    print("  -> UNIQUE constraint en documento_id agregado OK")
else:
    print("  -> UNIQUE constraint ya existe OK")

# 3. Verificar tabla alertas_vencimiento_sagrilaft (de models.py)
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name='alertas_vencimiento_sagrilaft'
    )
""")
existe = cur.fetchone()[0]
print(f"\nalertas_vencimiento_sagrilaft existe: {existe}")
if not existe:
    cur.execute("""
        CREATE TABLE alertas_vencimiento_sagrilaft (
            id SERIAL PRIMARY KEY,
            tercero_id INTEGER NOT NULL,
            radicado VARCHAR(50) NOT NULL,
            fecha_primera_alerta TIMESTAMP,
            fecha_recordatorio TIMESTAMP,
            recordatorio_enviado BOOLEAN DEFAULT FALSE,
            fecha_creacion TIMESTAMP DEFAULT NOW(),
            fecha_actualizacion TIMESTAMP DEFAULT NOW()
        )
    """)
    print("  -> Tabla alertas_vencimiento_sagrilaft creada OK")

# 4. Verificar tabla terceros_preregistro (de models.py)
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name='terceros_preregistro'
    )
""")
existe = cur.fetchone()[0]
print(f"\nterceros_preregistro existe: {existe}")
if not existe:
    cur.execute("""
        CREATE TABLE terceros_preregistro (
            id SERIAL PRIMARY KEY,
            nit VARCHAR(20) UNIQUE NOT NULL,
            razon_social VARCHAR(255),
            tipo_persona VARCHAR(20),
            primer_nombre VARCHAR(100),
            segundo_nombre VARCHAR(100),
            primer_apellido VARCHAR(100),
            segundo_apellido VARCHAR(100),
            correo VARCHAR(255),
            celular VARCHAR(20),
            acepta_terminos BOOLEAN DEFAULT FALSE,
            acepta_contacto BOOLEAN DEFAULT FALSE,
            estado_preregistro VARCHAR(50) DEFAULT 'en_revision',
            fecha_registro TIMESTAMP DEFAULT NOW(),
            fecha_actualizacion TIMESTAMP DEFAULT NOW()
        )
    """)
    print("  -> Tabla terceros_preregistro creada OK")

conn.commit()
print("\n=== Todas las tablas SAGRILAFT verificadas y corregidas ===")
conn.close()
