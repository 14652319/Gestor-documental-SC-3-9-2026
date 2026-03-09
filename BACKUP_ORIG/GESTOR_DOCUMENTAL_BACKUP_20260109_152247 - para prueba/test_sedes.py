"""
Script de prueba para verificar que obtener_sedes_disponibles() funciona
"""
from config_carpetas import obtener_sedes_disponibles, obtener_nombre_sede

print("=" * 60)
print("TEST: obtener_sedes_disponibles()")
print("=" * 60)

sedes = obtener_sedes_disponibles()
print(f"\nTipo de dato retornado: {type(sedes)}")
print(f"Contenido: {sedes}")
print(f"Cantidad de sedes: {len(sedes)}")

print("\n" + "=" * 60)
print("DETALLES DE CADA SEDE:")
print("=" * 60)

for sede in sedes:
    nombre_completo = obtener_nombre_sede(sede)
    print(f"  {sede:5} -> {nombre_completo}")
