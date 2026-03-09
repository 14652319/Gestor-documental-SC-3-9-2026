"""Busca errores o warnings en la carga reciente de archivos"""
import re
from datetime import datetime

# Buscar en los últimos logs del servidor
print("="*80)
print("🔍 BUSCANDO ERRORES EN LOGS DEL SERVIDOR")
print("="*80)

# Patrones a buscar
patrones_error = [
    r"ERROR",
    r"FAILED",
    r"Exception",
    r"Traceback",
    r"StringDataRightTruncation",
    r"COPY.*failed",
    r"prefijo.*too long",
    r"registro.*omitido",
    r"registro.*rechazado"
]

# Buscar en la salida del terminal reciente
# (simular - en realidad buscaríamos en logs/app.log)

print("\n📋 Revisar manualmente la terminal del servidor desde las 10:08")
print("   Buscar líneas que contengan:")
for patron in patrones_error:
    print(f"   - {patron}")

print("\n" + "="*80)
print("💡 TAMBIÉN REVISA:")
print("="*80)
print("""
1. Terminal del servidor alrededor de las 10:08-10:09
2. Busca mensajes como:
   - "Registros procesados: X de Y"
   - "Registros omitidos: X"
   - "ERROR al insertar"
   - Cualquier Traceback o Exception
   
3. Si encuentras errores de "too long" o "StringDataRightTruncation"
   → Algunos registros se omitieron por exceder límite de caracteres
""")
print("="*80)
