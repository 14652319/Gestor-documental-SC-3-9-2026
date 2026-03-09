"""
Módulo de Notas Contables / Archivo Digital
Gestiona la carga, visualización y edición de documentos contables
"""
from modules.notas_contables.routes import notas_bp
from modules.notas_contables.pages import archivo_digital_pages_bp

__all__ = ['notas_bp', 'archivo_digital_pages_bp']
