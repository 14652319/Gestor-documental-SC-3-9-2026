# -*- coding: utf-8 -*-
"""Resetear contraseña del usuario admin"""
import sys
sys.path.insert(0, '.')

import bcrypt
import psycopg2

# Nueva contraseña
NUEVA_PASSWORD = "admin123"

# Generar hash con bcrypt
password_hash = bcrypt.hashpw(NUEVA_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print(f"Nueva contraseña: {NUEVA_PASSWORD}")
print(f"Hash generado (bcrypt): {password_hash[:50]}...")

# Conectar a DB
try:
    conn = psycopg2.connect(
        host="localhost",
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025.",
        port=5432
    )
    
    cursor = conn.cursor()
    
    # Actualizar contraseña del usuario 14652319
    cursor.execute("""
        UPDATE usuarios 
        SET password_hash = %s
        WHERE usuario = '14652319'
        RETURNING id, usuario, correo, rol
    """, (password_hash,))
    
    result = cursor.fetchone()
    
    if result:
        print(f"\n✅ Contraseña actualizada:")
        print(f"   ID: {result[0]}")
        print(f"   Usuario: {result[1]}")
        print(f"   Correo: {result[2]}")
        print(f"   Rol: {result[3]}")
        print(f"\n🔑 Credenciales:")
        print(f"   Usuario: {result[1]}")
        print(f"   Contraseña: {NUEVA_PASSWORD}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ Actualización completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
