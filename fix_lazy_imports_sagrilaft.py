"""
Script para agregar lazy imports en routes.py de SAGRILAFT
Evita circular import de app.py
"""

import re

routes_file = r'modules\sagrilaft\routes.py'

# Leer archivo
with open(routes_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Patrones de funciones que necesitan SolicitudRegistro
patterns_solicitud = [
    (r'(def listar_radicados_pendientes\(\):)\n(    """[^"]*""")\n(    )(try:)', 
     r'\1\n\2\n\3from app import SolicitudRegistro  # Lazy import\n\3\4'),
    (r'(def actualizar_estado_radicado\([^)]*\):)\n(    """[^"]*""")\n(    )(try:)',
     r'\1\n\2\n\3from app import SolicitudRegistro  # Lazy import\n\3\4'),
    (r'(def exportar_radicados_excel\(\):)\n(    """[^"]*""")\n(    )(try:)',
     r'\1\n\2\n\3from app import SolicitudRegistro  # Lazy import\n\3\4'),
]

# Patrones de funciones que necesitan DocumentoTercero
patterns_documento = [
    (r'(def visualizar_documento\([^)]*\):)\n(    """[^"]*""")\n(    )(try:)',
     r'\1\n\2\n\3from app import DocumentoTercero  # Lazy import\n\3\4'),
    (r'(def descargar_documento_solo\([^)]*\):)\n(    """[^"]*""")\n(    )(try:)',
     r'\1\n\2\n\3from app import DocumentoTercero  # Lazy import\n\3\4'),
]

# Funciones que necesitan ambos
patterns_ambos = [
    (r'(def descargar_documentos_radicado\([^)]*\):)\n(    """[^"]*""")\n(    )(try:)',
     r'\1\n\2\n\3from app import SolicitudRegistro, DocumentoTercero  # Lazy import\n\3\4'),
]

# Aplicar reemplazos
for pattern, replacement in patterns_solicitud + patterns_documento + patterns_ambos:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Guardar archivo
with open(routes_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Lazy imports agregados correctamente")
print(f"   Archivo actualizado: {routes_file}")
