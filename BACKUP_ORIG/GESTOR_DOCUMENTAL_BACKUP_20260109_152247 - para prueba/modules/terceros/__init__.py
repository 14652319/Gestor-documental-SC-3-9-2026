"""
Módulo de Gestión Integral de Terceros
Sistema enterprise para administración completa de terceros
Incluye: CRUD, validación documental, notificaciones automáticas, auditoría
Fecha: 28 Noviembre 2025
"""

from flask import Blueprint

# Crear blueprint del módulo terceros
terceros_bp = Blueprint(
    'terceros', 
    __name__,
    template_folder='../../templates',
    static_folder='../../static'
)

# Importar rutas después de crear el blueprint para evitar imports circulares
from . import routes