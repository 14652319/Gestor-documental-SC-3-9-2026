"""
Módulo DIAN vs ERP - PostgreSQL Integrado
Validación de Facturas DIAN vs ERP  
Integrado al Gestor Documental
"""

from flask import Blueprint

# Crear blueprint
dian_vs_erp_bp = Blueprint(
    'dian_vs_erp',
    __name__,
    template_folder='../../templates/dian_vs_erp',
    static_folder='../../static',
    url_prefix='/dian_vs_erp'
)

# Importar rutas
from . import routes