# -*- coding: utf-8 -*-
"""
Módulo: Recepción de Facturas Digitales
Descripción: Blueprint para la gestión de facturas digitales de proveedores
Autor: Sistema
Fecha: Noviembre 2025
"""

from flask import Blueprint

facturas_digitales_bp = Blueprint(
    'facturas_digitales',
    __name__,
    url_prefix='/facturas-digitales',
    template_folder='../../templates/facturas_digitales',
    static_folder='../../static'
)

from . import routes
