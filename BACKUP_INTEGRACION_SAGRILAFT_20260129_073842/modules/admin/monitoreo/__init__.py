"""
Módulo de Monitoreo y Administración
Sistema de alertas, bloqueo de IPs, gestión de usuarios y monitoreo de recursos.
"""

from flask import Blueprint

# Crear blueprint
monitoreo_bp = Blueprint(
    'monitoreo',
    __name__,
    url_prefix='/admin/monitoreo'
)

# Importar rutas después de crear el blueprint para evitar circular imports
from . import routes
