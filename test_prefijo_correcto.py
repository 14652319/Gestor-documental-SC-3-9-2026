"""
TEST RÁPIDO - Función extraer_prefijo CORRECTA de routes.py línea 1062
"""
import re

def extraer_prefijo(docto: str) -> str:
    """Extrae prefijo alfanumérico (letras Y números), limpiando solo guiones y puntos"""
    if not docto:
        return ""
    # Solo eliminar guiones, puntos y espacios - MANTENER números
    prefijo = re.sub(r'[\-\.\s]', '', str(docto)).strip().upper()
    
    # Validar longitud máxima (20 caracteres por esquema BD)
    if len(prefijo) > 20:
        # Si es todo hexadecimal largo, es un CUFE - devolver vacío
        if re.match(r'^[A-F0-9]+$', prefijo) and len(prefijo) > 20:
            return ""  # CUFE mal posicionado
        return prefijo[:20]
    
    return prefijo

# Test con valores reales
test_cases = [
    ('6841', 'Prefijo NUMÉRICO'),
    ('FEVA', 'Prefijo ALFABÉTICO'),
    ('1FEA', 'Prefijo ALFANUMÉRICO'),
    ('2FEA', 'Prefijo ALFANUMÉRICO'),
    ('F3VB', 'Prefijo ALFANUMÉRICO'),
]

print("=" * 60)
print("TEST DE extraer_prefijo() - VERSIÓN CORRECTA")
print("=" * 60)

for valor, descripcion in test_cases:
    resultado = extraer_prefijo(valor)
    print(f"{descripcion:30} '{valor}' → '{resultado}'")

print("=" * 60)
