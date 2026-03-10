"""
Blueprint para las páginas del módulo Archivo Digital
Rutas que renderizan templates HTML (separadas de la API REST)
"""
from flask import Blueprint, render_template, session, redirect, url_for, request
from extensions import db
from decoradores_permisos import requiere_permiso_html
from modules.notas_contables.models import DocumentoContable
from modules.configuracion.models import TipoDocumento, CentroOperacion
from datetime import datetime
import math

# Crear blueprint para páginas
archivo_digital_pages_bp = Blueprint('archivo_digital_pages', __name__, url_prefix='/archivo_digital')

def validar_sesion():
    """Verifica que el usuario tenga sesión activa"""
    if 'usuario_id' not in session or 'usuario' not in session:
        return False
    return True

# =====================================================
# RUTAS PARA RENDERIZAR TEMPLATES
# =====================================================

@archivo_digital_pages_bp.route('/cargar')
@requiere_permiso_html('archivo_digital', 'acceder_modulo')
def cargar_documento():
    """Renderiza el formulario de carga de documentos"""
    if not validar_sesion():
        return redirect('/login')
    
    return render_template('cargar_documentos_contables.html')

@archivo_digital_pages_bp.route('/visor')
@requiere_permiso_html('archivo_digital', 'acceder_modulo')
def visor_documentos():
    """Renderiza el visor de documentos con filtros"""
    if not validar_sesion():
        return redirect('/login')
    
    # Parámetros de filtrado
    filtro = request.args.get('filtro', '').strip()
    fecha_desde = request.args.get('desde', '')
    fecha_hasta = request.args.get('hasta', '')
    pagina = int(request.args.get('pagina', 1))
    por_pagina = int(request.args.get('por_pagina', 50))
    
    # Base query
    query = DocumentoContable.query
    
    # Filtro de texto (busca en nombre_archivo)
    if filtro:
        query = query.filter(DocumentoContable.nombre_archivo.ilike(f'%{filtro}%'))
    
    # Filtro de fechas
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(DocumentoContable.fecha_documento >= fecha_desde_obj)
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            # Incluir el día completo (hasta las 23:59:59)
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(DocumentoContable.fecha_documento <= fecha_hasta_obj)
        except ValueError:
            pass
    
    # Ordenar por fecha de creación (más recientes primero)
    query = query.order_by(DocumentoContable.created_at.desc())
    
    # Total de documentos
    total_documentos = query.count()
    
    # Paginación
    total_paginas = math.ceil(total_documentos / por_pagina)
    offset = (pagina - 1) * por_pagina
    documentos = query.offset(offset).limit(por_pagina).all()
    
    return render_template('visor_documentos_contables.html',
                         documentos=documentos,
                         total_documentos=total_documentos,
                         pagina=pagina,
                         total_paginas=total_paginas,
                         por_pagina=por_pagina,
                         filtro=filtro,
                         fecha_desde=fecha_desde,
                         fecha_hasta=fecha_hasta)

@archivo_digital_pages_bp.route('/editar/<int:documento_id>')
@requiere_permiso_html('archivo_digital', 'acceder_modulo')
def editar_documento(documento_id):
    """Renderiza el editor de documentos (VERSIÓN 3 CON TODAS LAS MEJORAS)"""
    if not validar_sesion():
        return redirect('/login')
    
    return render_template('editar_nota_v3.html', documento_id=documento_id)

@archivo_digital_pages_bp.route('/')
@requiere_permiso_html('archivo_digital', 'acceder_modulo')
def index():
    """Redirige al visor por defecto"""
    return redirect(url_for('archivo_digital_pages.visor_documentos'))
