# =============================================
# 📦 __init__.py — Módulo Relaciones
# =============================================
"""
Módulo para generar relaciones de facturas
Permite agrupar facturas por destino (Contabilidad, Pagos, etc.)
y exportarlas en formato Excel o PDF
"""

from .routes import relaciones_bp

__all__ = ['relaciones_bp']
