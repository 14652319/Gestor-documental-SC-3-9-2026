"""
Script para agregar campo empresa_id a la tabla relaciones_facturas
"""
import psycopg2

try:
    # Connect to database
    conn = psycopg2.connect(
        host="localhost",
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    
    cursor = conn.cursor()
    
    print("\n" + "=" * 100)
    print("AGREGANDO CAMPO EMPRESA_ID A TABLA relaciones_facturas")
    print("=" * 100)
    
    # Verificar si la columna ya existe
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'relaciones_facturas' 
        AND column_name = 'empresa_id'
    """)
    
    if cursor.fetchone():
        print("\n[INFO] La columna empresa_id ya existe en relaciones_facturas")
    else:
        # Agregar columna empresa_id
        cursor.execute("""
            ALTER TABLE relaciones_facturas 
            ADD COLUMN empresa_id VARCHAR(10)
        """)
        print("\n[OK] Columna empresa_id agregada a relaciones_facturas")
        
        # Agregar FK a empresas.sigla
        cursor.execute("""
            ALTER TABLE relaciones_facturas 
            ADD CONSTRAINT fk_relaciones_empresa 
            FOREIGN KEY (empresa_id) REFERENCES empresas(sigla)
        """)
        print("[OK] Foreign key agregada: empresa_id -> empresas.sigla")
        
        # Actualizar registros existentes con 'SC'
        cursor.execute("""
            UPDATE relaciones_facturas 
            SET empresa_id = 'SC' 
            WHERE empresa_id IS NULL
        """)
        rows_updated = cursor.rowcount
        print(f"[OK] {rows_updated} registros actualizados con empresa_id = 'SC'")
    
    # Commit changes
    conn.commit()
    
    print("\n" + "=" * 100)
    print("[OK] ACTUALIZACIÓN COMPLETADA")
    print("=" * 100 + "\n")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n[ERROR] No se pudo actualizar la tabla: {e}\n")
