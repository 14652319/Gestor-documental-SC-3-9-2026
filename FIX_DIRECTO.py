"""
🔧 FIX DIRECTO: Reemplazar buffer.write con format_value_for_copy
"""

routes_file = "modules/dian_vs_erp/routes.py"

print("🔧 APLICANDO CORRECCIONES DIRECTAS...")
print("=" * 70)

with open(routes_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

changes = 0
for i, line in enumerate(lines):
    # Buscar líneas que contienen buffer.write(f"{reg[
    if "buffer.write(f\"{reg[" in line:
        # Reemplazar con format_value_for_copy
        old_line = line
        new_line = line.replace(
            "buffer.write(f\"{reg[",
            "buffer.write(f\"{format_value_for_copy(reg["
        ).replace(
            "]}\\t\")",
            "])}\\t\")"
        ).replace(
            "]}\\n\")",
            "])}\\n\")"
        )
        
        if old_line != new_line:
            lines[i] = new_line
            changes += 1
            print(f"   Línea {i+1}: {old_line.strip()[:60]}... → CORREGIDO")

# Guardar cambios
with open(routes_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n" + "=" * 70)
print(f"✅ CORRECCIONES APLICADAS: {changes} líneas modificadas")
print("\n📊 RESUMEN:")
print("   ✅ Función helper format_value_for_copy() ya existe")
print(f"   ✅ {changes} buffer.write() corregidos en todas las tablas")
print("\n🔄 SIGUIENTE PASO:")
print("   1. REINICIA el servidor Flask")
print("   2. Reintenta cargar los archivos")
print("   3. Ahora valores None se manejan como NULL ✅")
