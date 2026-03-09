"""
Módulo SAGRILAFT - Sistema de Gestión de Radicados y Aprobación de Terceros
Maneja el preregistro y aprobación de terceros antes de crearlos en el sistema principal
"""

from flask import Blueprint

sagrilaft_bp = Blueprint(
    'sagrilaft',
    __name__,
    url_prefix='/sagrilaft',
    template_folder='templates'
)

# Importar routes al final para registrar los endpoints en el blueprint
from modules.sagrilaft import routes
