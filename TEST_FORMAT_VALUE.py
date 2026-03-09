"""
TEST DE FUNCIÓN format_value_for_copy()
Prueba que la función maneja correctamente valores None
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la función desde routes
from modules.dian_vs_erp.routes import format_value_for_copy

print("=" * 80)
print("🧪 TEST DE format_value_for_copy()")
print("=" * 80)

# Test 1: None → debe retornar ''
print("\n📋 Test 1: Valor None")
result = format_value_for_copy(None)
print(f"   Input:  None")
print(f"   Output: '{result}'")
print(f"   ✅ PASS" if result == '' else f"   ❌ FAIL - Esperaba '', obtuvo '{result}'")

# Test 2: String normal
print("\n📋 Test 2: String normal")
result = format_value_for_copy("Texto normal")
print(f"   Input:  'Texto normal'")
print(f"   Output: '{result}'")
print(f"   ✅ PASS" if result == 'Texto normal' else f"   ❌ FAIL")

# Test 3: Número
print("\n📋 Test 3: Número")
result = format_value_for_copy(12345)
print(f"   Input:  12345")
print(f"   Output: '{result}'")
print(f"   ✅ PASS" if result == '12345' else f"   ❌ FAIL")

# Test 4: Boolean True
print("\n📋 Test 4: Boolean True")
result = format_value_for_copy(True)
print(f"   Input:  True")
print(f"   Output: '{result}'")
print(f"   ✅ PASS" if result == 't' else f"   ❌ FAIL - Esperaba 't', obtuvo '{result}'")

# Test 5: Boolean False
print("\n📋 Test 5: Boolean False")
result = format_value_for_copy(False)
print(f"   Input:  False")
print(f"   Output: '{result}'")
print(f"   ✅ PASS" if result == 'f' else f"   ❌ FAIL - Esperaba 'f', obtuvo '{result}'")

# Test 6: Float
print("\n📋 Test 6: Float")
result = format_value_for_copy(123.45)
print(f"   Input:  123.45")
print(f"   Output: '{result}'")
print(f"   ✅ PASS" if result == '123.45' else f"   ❌ FAIL")

# Test 7: String vacío
print("\n📋 Test 7: String vacío")
result = format_value_for_copy("")
print(f"   Input:  ''")
print(f"   Output: '{result}'")
print(f"   ✅ PASS" if result == '' else f"   ❌ FAIL")

# Test 8: Fecha (como string)
print("\n📋 Test 8: Fecha como string")
result = format_value_for_copy("2026-02-20")
print(f"   Input:  '2026-02-20'")
print(f"   Output: '{result}'")
print(f"   ✅ PASS" if result == '2026-02-20' else f"   ❌ FAIL")

print("\n" + "=" * 80)
print("✅ TODOS LOS TESTS COMPLETADOS")
print("=" * 80)
