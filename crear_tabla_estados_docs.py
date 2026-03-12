import psycopg2
conn = psycopg2.connect('postgresql://postgres:G3st0radm$2025.@localhost:5432/gestor_documental')
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS estados_documentos (
        id SERIAL PRIMARY KEY,
        documento_id INTEGER NOT NULL,
        estado VARCHAR(50) DEFAULT 'pendiente',
        observacion TEXT,
        usuario_revisor VARCHAR(100),
        fecha_revision TIMESTAMP DEFAULT NOW()
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_estados_doc_id ON estados_documentos(documento_id)")
conn.commit()
print("Tabla estados_documentos creada OK")
conn.close()
