# Test bcrypt hash
import bcrypt
import psycopg2

# Contraseña que quiero verificar
password_to_test = "admin123"

# Conectar y obtener el hash guardado
conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="G3st0radm$2025.",
    port=5432
)

cursor = conn.cursor()
cursor.execute("SELECT password_hash FROM usuarios WHERE usuario = '14652319'")
stored_hash = cursor.fetchone()[0]

print(f"Hash guardado: {stored_hash}")
print(f"Probando contraseña: {password_to_test}")

# Verificar
if bcrypt.checkpw(password_to_test.encode('utf-8'), stored_hash.encode('utf-8')):
    print("✅ Contraseña CORRECTA")
else:
    print("❌ Contraseña INCORRECTA")

cursor.close()
conn.close()
