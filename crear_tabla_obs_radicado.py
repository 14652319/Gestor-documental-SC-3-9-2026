import psycopg2
conn = psycopg2.connect('postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental')
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS observaciones_radicado (
        id SERIAL PRIMARY KEY,
        radicado VARCHAR(50) NOT NULL,
        observacion TEXT NOT NULL,
        usuario VARCHAR(100),
        fecha_registro TIMESTAMP DEFAULT NOW()
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_obs_radicado ON observaciones_radicado(radicado)")
conn.commit()
print("Tabla observaciones_radicado creada OK")
conn.close()
