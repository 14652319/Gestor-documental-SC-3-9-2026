# -*- coding: utf-8 -*-
"""
Sistema de Usuarios y Permisos - Blueprint
"""

from flask import Blueprint

# Crear blueprint
usuarios_permisos_bp = Blueprint(
    'usuarios_permisos', 
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/admin/usuarios-permisos'
)

# Importar rutas
from .routes import *

# Exportar
__all__ = ['usuarios_permisos_bp']