"""
Manual script to update empresa_id NULL to 'SC' using psycopg2 directly
"""
import psycopg2

try:
    # Connect to database (using credentials from .env)
    conn = psycopg2.connect(
        host="localhost",
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    
    cursor = conn.cursor()
    
    print("\n" + "=" * 100)
    print("ACTUALIZANDO FACTURAS CON EMPRESA_ID NULL A 'SC'")
    print("=" * 100)
    
    # Count and update facturas_temporales
    cursor.execute("SELECT COUNT(*) FROM facturas_temporales WHERE empresa_id IS NULL")
    count_temp = cursor.fetchone()[0]
    print(f"\n[INFO] Facturas temporales con empresa_id NULL: {count_temp}")
    
    if count_temp > 0:
        cursor.execute("UPDATE facturas_temporales SET empresa_id = 'SC' WHERE empresa_id IS NULL")
        print(f"[OK] {count_temp} facturas temporales actualizadas a empresa_id = 'SC'")
    
    # Count and update facturas_recibidas
    cursor.execute("SELECT COUNT(*) FROM facturas_recibidas WHERE empresa_id IS NULL")
    count_recib = cursor.fetchone()[0]
    print(f"\n[INFO] Facturas recibidas con empresa_id NULL: {count_recib}")
    
    if count_recib > 0:
        cursor.execute("UPDATE facturas_recibidas SET empresa_id = 'SC' WHERE empresa_id IS NULL")
        print(f"[OK] {count_recib} facturas recibidas actualizadas a empresa_id = 'SC'")
    
    # Commit changes
    conn.commit()
    
    print("\n" + "=" * 100)
    print(f"[OK] ACTUALIZACIÓN COMPLETADA - Total: {count_temp + count_recib} facturas")
    print("=" * 100 + "\n")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n[ERROR] No se pudo conectar a la base de datos: {e}")
    print("[INFO] Asegúrate de que PostgreSQL esté ejecutándose y las credenciales sean correctas\n")
