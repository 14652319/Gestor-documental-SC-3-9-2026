"""
Backend del módulo de Causaciones
Incluye extracción de datos de PDF, visualización en tiempo real, y gestión de documentos
"""
from flask import Blueprint, render_template, request, jsonify, send_file, session, redirect, url_for
# from flask_socketio import emit, join_room, leave_room  # Comentado temporalmente - usar polling en su lugar
from extensions import db
from decoradores_permisos import requiere_permiso, requiere_permiso_html
from modules.causaciones.models import DocumentoCausacion, ObservacionCausacion
from modules.configuracion.models import CentroOperacion  # ✅ CORREGIDO: estaba en notas_contables
import os
import re
import PyPDF2
from datetime import datetime
from werkzeug.utils import secure_filename
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Crear Blueprint
causaciones_bp = Blueprint('causaciones', __name__, url_prefix='/causaciones')

# Configuración de carpetas
CARPETA_CAUSACION = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'documentos_causacion')
if not os.path.exists(CARPETA_CAUSACION):
    os.makedirs(CARPETA_CAUSACION)

# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@causaciones_bp.route('/')
@requiere_permiso_html('causaciones', 'acceder_modulo')
def index():
    """
    Vista principal de causaciones - Compatible con el sistema original
    Escanea carpetas de red y muestra archivos con filtros por sede
    """
    if 'usuario_id' not in session:
        return redirect('/login')
    
    from config_carpetas import obtener_carpetas_base
    import os
    
    # Parámetros de filtros
    sedes_seleccionadas = request.args.getlist("sede") or ["Todo"]
    ruta_relativa = request.args.get("carpeta", "__all__")
    filtro = request.args.get("filtro", "").lower()
    pagina = int(request.args.get("pagina", 1))
    por_pagina = int(request.args.get("por_pagina", 50))
    archivo_actual = request.args.get("archivo", "")
    
    carpetas_base = obtener_carpetas_base()
    
    # Determinar sedes a revisar
    if "Todo" in sedes_seleccionadas or not sedes_seleccionadas:
        sedes_a_revisar = list(carpetas_base.keys())
    else:
        sedes_a_revisar = sedes_seleccionadas
    
    # Recolectar carpetas y archivos
    carpetas = set()
    archivos = []
    
    for sede in sedes_a_revisar:
        carpeta_principal = carpetas_base.get(sede, "")
        if not os.path.exists(carpeta_principal):
            logger.warning(f"Carpeta no existe: {carpeta_principal}")
            continue
        
        # Explorar subcarpetas
        for root, dirs, files in os.walk(carpeta_principal):
            rel_path = os.path.relpath(root, carpeta_principal).replace("\\", "/")
            
            # Agregar carpetas
            if rel_path != ".":
                carpetas.add(rel_path)
            
            # Filtrar archivos PDF
            for file in files:
                if not file.lower().endswith('.pdf'):
                    continue
                
                archivo_rel = rel_path if rel_path != "." else ""
                
                # Aplicar filtro de carpeta
                if ruta_relativa != "__all__" and archivo_rel != ruta_relativa:
                    continue
                
                # Aplicar filtro de texto
                if filtro and filtro not in file.lower():
                    continue
                
                # Obtener fecha de modificación
                try:
                    ruta_completa = os.path.join(root, file)
                    fecha_mod = os.path.getmtime(ruta_completa)
                    
                    # Construir ruta relativa completa
                    if archivo_rel:
                        archivo_completo = f"{archivo_rel}/{file}"
                    else:
                        archivo_completo = file
                    
                    archivos.append((sede, archivo_completo, fecha_mod))
                except Exception as e:
                    logger.error(f"Error procesando {file}: {e}")
                    continue
    
    # Ordenar por fecha (más recientes primero)
    archivos.sort(key=lambda x: x[2], reverse=True)
    
    # Paginación
    total_archivos = len(archivos)
    total_paginas = max(1, (total_archivos + por_pagina - 1) // por_pagina)
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    archivos_pagina = archivos[inicio:fin]
    
    # Obtener estados (si tienes sistema de estados)
    estados = {}
    historiales = {}
    archivos_ocupados = {}
    
    # Lista de sedes disponibles
    sedes_disponibles = ['CYS', 'DOM', 'TIC', 'MER', 'MYP', 'FIN']
    sedes = sedes_disponibles + ['Todo']
    
    return render_template('causacion.html',
        sedes=sedes,
        sede=sedes_seleccionadas,
        carpetas=sorted(list(carpetas)),
        archivos=archivos_pagina,
        estados=estados,
        historiales=historiales,
        ruta_relativa=ruta_relativa,
        filtro=filtro,
        archivo_actual=archivo_actual,
        cantidad_archivos=total_archivos,
        pagina=pagina,
        total_paginas=total_paginas,
        por_pagina=por_pagina,
        archivos_ocupados=archivos_ocupados
    )


@causaciones_bp.route('/renombrar')
@requiere_permiso_html('causaciones', 'renombrar_archivo')
def renombrar():
    """Vista de renombrado de documentos"""
    if 'usuario_id' not in session:
        return redirect('/login')
    
    return render_template('renombrar.html')


# ============================================================================
# API - LISTAR DOCUMENTOS
# ============================================================================
@causaciones_bp.route('/api/documentos', methods=['GET'])
@requiere_permiso('causaciones', 'consultar_documentos')
def listar_documentos():
    """
    Lista todos los documentos disponibles para causar
    Incluye estado de visualización en tiempo real
    """
    try:
        # Filtros opcionales
        estado = request.args.get('estado')  # pendiente, causado, rechazado
        centro_id = request.args.get('centro')
        con_observaciones = request.args.get('con_observaciones')  # 'true' o 'false'
        
        query = DocumentoCausacion.query
        
        if estado:
            query = query.filter_by(estado=estado)
        
        if centro_id:
            query = query.filter_by(centro_operacion_id=centro_id)
        
        if con_observaciones == 'true':
            # Solo documentos con observaciones
            query = query.join(ObservacionCausacion).distinct()
        
        documentos = query.order_by(DocumentoCausacion.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'documentos': [doc.to_dict() for doc in documentos],
            'total': len(documentos)
        })
        
    except Exception as e:
        logger.error(f"Error al listar documentos: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# API - VER PDF Y EXTRAER DATOS
# ============================================================================
@causaciones_bp.route('/api/ver_pdf/<int:documento_id>', methods=['GET'])
@requiere_permiso('causaciones', 'visualizar_pdf')
def ver_pdf(documento_id):
    """
    Devuelve el PDF y marca el documento como siendo visualizado
    """
    try:
        usuario = session.get('usuario')
        documento = DocumentoCausacion.query.get_or_404(documento_id)
        
        # Marcar como siendo visualizado
        documento.siendo_visualizado_por = usuario
        documento.fecha_inicio_visualizacion = datetime.utcnow()
        db.session.commit()
        
        # Emitir evento WebSocket para notificar a otros usuarios
        # (esto se maneja con Flask-SocketIO en el archivo principal)
        
        # Devolver el archivo PDF
        ruta_completa = documento.ruta_archivo
        if not os.path.exists(ruta_completa):
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
        
        return send_file(ruta_completa, mimetype='application/pdf')
        
    except Exception as e:
        logger.error(f"Error al ver PDF: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@causaciones_bp.route('/api/cerrar_pdf/<int:documento_id>', methods=['POST'])
@requiere_permiso('causaciones', 'visualizar_pdf')
def cerrar_pdf(documento_id):
    """
    Marca el documento como NO siendo visualizado
    """
    try:
        documento = DocumentoCausacion.query.get_or_404(documento_id)
        documento.siendo_visualizado_por = None
        documento.fecha_inicio_visualizacion = None
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error al cerrar PDF: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@causaciones_bp.route('/api/extraer_datos/<int:documento_id>', methods=['GET'])
@requiere_permiso('causaciones', 'extraer_datos')
def extraer_datos_pdf(documento_id):
    """
    Extrae datos del PDF: NIT, razón social, valores, CUFE, resolución, etc.
    """
    try:
        documento = DocumentoCausacion.query.get_or_404(documento_id)
        ruta_pdf = documento.ruta_archivo
        
        if not os.path.exists(ruta_pdf):
            return jsonify({'success': False, 'message': 'PDF no encontrado'}), 404
        
        datos_extraidos = _extraer_datos_factura(ruta_pdf)
        
        # Actualizar documento con datos extraídos
        documento.es_factura_electronica = datos_extraidos.get('es_electronica', False)
        documento.prefijo = datos_extraidos.get('prefijo')
        documento.folio = datos_extraidos.get('folio')
        documento.nit = datos_extraidos.get('nit')
        documento.razon_social = datos_extraidos.get('razon_social')
        documento.cufe = datos_extraidos.get('cufe')
        documento.valor_antes_iva = datos_extraidos.get('valor_antes_iva')
        documento.valor_iva = datos_extraidos.get('valor_iva')
        documento.valor_total = datos_extraidos.get('valor_total')
        documento.resolucion = datos_extraidos.get('resolucion')
        documento.rango_desde = datos_extraidos.get('rango_desde')
        documento.rango_hasta = datos_extraidos.get('rango_hasta')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'datos': datos_extraidos
        })
        
    except Exception as e:
        logger.error(f"Error al extraer datos del PDF: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# FUNCIÓN AUXILIAR - EXTRACCIÓN DE DATOS DEL PDF
# ============================================================================

def _extraer_datos_factura(ruta_pdf):
    """
    Extrae datos de una factura PDF usando PyPDF2 y expresiones regulares
    """
    datos = {
        'es_electronica': False,
        'prefijo': None,
        'folio': None,
        'nit': None,
        'razon_social': None,
        'cufe': None,
        'valor_antes_iva': None,
        'valor_iva': None,
        'valor_total': None,
        'resolucion': None,
        'rango_desde': None,
        'rango_hasta': None
    }
    
    try:
        with open(ruta_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            texto_completo = ''
            
            # Extraer texto de todas las páginas
            for page in reader.pages:
                texto_completo += page.extract_text()
            
            # Convertir a mayúsculas para búsquedas más robustas
            texto_upper = texto_completo.upper()
            
            # 1. Detectar si es factura electrónica
            if 'FACTURA ELECTRÓNICA' in texto_upper or 'FACTURA ELECTRONICA' in texto_upper:
                datos['es_electronica'] = True
            
            # 2. Extraer CUFE (cadena larga alfanumérica)
            patron_cufe = r'CUFE[:\s]*([A-Z0-9]{50,})'
            match_cufe = re.search(patron_cufe, texto_upper)
            if match_cufe:
                datos['cufe'] = match_cufe.group(1)
            
            # 3. Extraer NIT (formato: XXX.XXX.XXX-X o XXXXXXXXX-X)
            patron_nit = r'NIT[:\s]*(\d{1,3}\.?\d{3}\.?\d{3}-?\d{1})'
            match_nit = re.search(patron_nit, texto_completo)
            if match_nit:
                datos['nit'] = match_nit.group(1).replace('.', '').replace('-', '')
            
            # 4. Extraer Razón Social (línea después de NIT o cerca)
            patron_razon = r'RAZ[OÓ]N SOCIAL[:\s]*([A-ZÁÉÍÓÚÑ\s\.]+)'
            match_razon = re.search(patron_razon, texto_upper)
            if match_razon:
                datos['razon_social'] = match_razon.group(1).strip()
            
            # 5. Extraer Prefijo y Folio
            # Buscar patrones como: FACTURA No. ABC-12345 o Factura: ABC 12345
            patron_factura = r'FACTURA\s*N[OÚ]?\.?\s*:?\s*([A-Z]{1,10})[\s-]*(\d+)'
            match_factura = re.search(patron_factura, texto_upper)
            if match_factura:
                datos['prefijo'] = match_factura.group(1)
                datos['folio'] = match_factura.group(2)
            
            # 6. Extraer Resolución y Rango
            # Patrón: Resolución DIAN No. XXXX del DD/MM/YYYY. Rango: XXXX-YYYY
            patron_resolucion = r'RESOLUCI[OÓ]N.*?N[OÚ]\.?\s*(\d+)'
            match_resolucion = re.search(patron_resolucion, texto_upper)
            if match_resolucion:
                datos['resolucion'] = match_resolucion.group(1)
            
            patron_rango = r'RANGO[:\s]*(\d+)\s*[-A]\s*(\d+)'
            match_rango = re.search(patron_rango, texto_upper)
            if match_rango:
                datos['rango_desde'] = int(match_rango.group(1))
                datos['rango_hasta'] = int(match_rango.group(2))
            
            # 7. Extraer Valores (Subtotal, IVA, Total)
            # Patrones comunes: SUBTOTAL: $XXX,XXX.XX
            patron_subtotal = r'SUBTOTAL[:\s]*\$?\s*([\d,]+\.?\d{0,2})'
            match_subtotal = re.search(patron_subtotal, texto_completo)
            if match_subtotal:
                valor_str = match_subtotal.group(1).replace(',', '')
                datos['valor_antes_iva'] = float(valor_str)
            
            patron_iva = r'IVA[:\s]*\$?\s*([\d,]+\.?\d{0,2})'
            match_iva = re.search(patron_iva, texto_completo)
            if match_iva:
                valor_str = match_iva.group(1).replace(',', '')
                datos['valor_iva'] = float(valor_str)
            
            patron_total = r'TOTAL[:\s]*\$?\s*([\d,]+\.?\d{0,2})'
            match_total = re.search(patron_total, texto_completo)
            if match_total:
                valor_str = match_total.group(1).replace(',', '')
                datos['valor_total'] = float(valor_str)
            
    except Exception as e:
        logger.error(f"Error al extraer datos: {str(e)}")
    
    return datos


# ============================================================================
# API - RENOMBRAR DOCUMENTO
# ============================================================================
@causaciones_bp.route('/api/renombrar/<int:documento_id>', methods=['POST'])
@requiere_permiso('causaciones', 'renombrar_archivo')
def renombrar_documento(documento_id):
    """
    Renombra un documento en el sistema de archivos y en la BD
    """
    try:
        data = request.get_json()
        nuevo_nombre = data.get('nuevo_nombre')
        
        if not nuevo_nombre:
            return jsonify({'success': False, 'message': 'Nombre requerido'}), 400
        
        documento = DocumentoCausacion.query.get_or_404(documento_id)
        ruta_actual = documento.ruta_archivo
        
        # Validar que el archivo existe
        if not os.path.exists(ruta_actual):
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
        
        # Construir nueva ruta
        directorio = os.path.dirname(ruta_actual)
        extension = os.path.splitext(ruta_actual)[1]
        nuevo_nombre_seguro = secure_filename(nuevo_nombre)
        nueva_ruta = os.path.join(directorio, nuevo_nombre_seguro + extension)
        
        # Renombrar archivo físico
        os.rename(ruta_actual, nueva_ruta)
        
        # Actualizar BD
        documento.nombre_archivo = nuevo_nombre_seguro + extension
        documento.ruta_archivo = nueva_ruta
        db.session.commit()
        
        return jsonify({'success': True, 'nuevo_nombre': nuevo_nombre_seguro + extension})
        
    except Exception as e:
        logger.error(f"Error al renombrar documento: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# API - BORRAR DOCUMENTO
# ============================================================================
@causaciones_bp.route('/api/borrar/<int:documento_id>', methods=['DELETE'])
@requiere_permiso('causaciones', 'eliminar_archivo')
def borrar_documento(documento_id):
    """
    Elimina un documento del sistema de archivos y de la BD
    """
    try:
        documento = DocumentoCausacion.query.get_or_404(documento_id)
        ruta_archivo = documento.ruta_archivo
        
        # Eliminar archivo físico
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
        
        # Eliminar observaciones asociadas
        ObservacionCausacion.query.filter_by(documento_id=documento_id).delete()
        
        # Eliminar de BD
        db.session.delete(documento)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error al borrar documento: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# API - OBSERVACIONES
# ============================================================================
@causaciones_bp.route('/api/observaciones/<int:documento_id>', methods=['GET'])
@requiere_permiso('causaciones', 'ver_observaciones')
def obtener_observaciones(documento_id):
    """
    Obtiene todas las observaciones de un documento (de todos los módulos)
    """
    try:
        observaciones = ObservacionCausacion.query.filter_by(
            documento_id=documento_id
        ).order_by(ObservacionCausacion.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'observaciones': [obs.to_dict() for obs in observaciones]
        })
        
    except Exception as e:
        logger.error(f"Error al obtener observaciones: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@causaciones_bp.route('/api/observaciones/<int:documento_id>', methods=['POST'])
@requiere_permiso('causaciones', 'agregar_observacion')
def agregar_observacion(documento_id):
    """
    Agrega una nueva observación a un documento
    """
    try:
        data = request.get_json()
        observacion_texto = data.get('observacion')
        origen = data.get('origen', 'causacion')
        
        if not observacion_texto:
            return jsonify({'success': False, 'message': 'Observación requerida'}), 400
        
        observacion = ObservacionCausacion(
            documento_id=documento_id,
            observacion=observacion_texto,
            origen=origen,
            created_by=session.get('usuario'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(observacion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'observacion': observacion.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error al agregar observación: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# API - CENTROS DE OPERACIÓN
# ============================================================================

@causaciones_bp.route('/api/centros_operacion', methods=['GET'])
def listar_centros():
    """
    Lista todos los centros de operación disponibles
    """
    try:
        centros = CentroOperacion.query.order_by(CentroOperacion.codigo).all()
        
        return jsonify({
            'success': True,
            'centros': [{'id': c.id, 'codigo': c.codigo, 'nombre': c.nombre} for c in centros]
        })
        
    except Exception as e:
        logger.error(f"Error al listar centros: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# API - EXPLORADOR DE CARPETAS DE RED
# ============================================================================

@causaciones_bp.route('/api/carpetas/estado', methods=['GET'])
@requiere_permiso('causaciones', 'acceder_modulo')
def estado_carpetas():
    """
    Verifica el estado de acceso a las carpetas de red configuradas
    """
    try:
        from config_carpetas import verificar_acceso_carpetas
        estado = verificar_acceso_carpetas()
        
        return jsonify({
            'success': True,
            'carpetas': estado
        })
        
    except Exception as e:
        logger.error(f"Error al verificar carpetas: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@causaciones_bp.route('/api/carpetas/archivos', methods=['GET'])
@requiere_permiso('causaciones', 'consultar_documentos')
def listar_archivos_red():
    """
    Lista archivos PDF de las carpetas de red usando escaneo automático.
    Implementa la lógica del sistema original según documentación.
    
    Parámetros GET:
    - sede: Códigos de sede (CYS, DOM, TIC, MER, MYP, FIN) o 'Todo' (puede ser múltiple)
    - carpeta: Filtrar por carpeta específica (opcional, '__all__' para todas)
    - filtro: Texto para filtrar nombres de archivo (opcional)
    - pagina: Número de página (default 1)
    - por_pagina: Archivos por página (default 50)
    """
    try:
        from config_carpetas import escanear_sedes_y_carpetas, obtener_sedes_disponibles
        import os
        
        # Parámetros
        sedes_param = request.args.getlist('sede') or ['Todo']
        carpeta_filtro = request.args.get('carpeta', '__all__')  # __all__ = Todas las carpetas
        filtro_texto = request.args.get('filtro', '')
        pagina = int(request.args.get('pagina', 1))
        por_pagina = int(request.args.get('por_pagina', 50))
        
        logger.info(f"Parámetros recibidos - Sedes: {sedes_param}, Carpeta: {carpeta_filtro}, Filtro: {filtro_texto}")
        
        # Determinar sedes a escanear
        if 'Todo' in sedes_param:
            sedes_a_escanear = obtener_sedes_disponibles()
        else:
            sedes_a_escanear = sedes_param
        
        logger.info(f"Escaneando sedes: {sedes_a_escanear}")
        
        # Usar la función de escaneo del sistema original
        archivos, carpetas = escanear_sedes_y_carpetas(sedes_a_escanear, filtro_texto)
        
        logger.info(f"Archivos encontrados: {len(archivos)}, Carpetas: {len(carpetas)}")
        
        # Filtrar por carpeta específica si se solicita
        if carpeta_filtro != '__all__':
            archivos_filtrados = [a for a in archivos if a['rel_pdf'].startswith(carpeta_filtro)]
            logger.info(f"Filtrado por carpeta '{carpeta_filtro}': {len(archivos_filtrados)} archivos")
            archivos = archivos_filtrados
        
        # Ordenar por fecha (más recientes primero)
        archivos.sort(key=lambda x: x['fecha'], reverse=True)
        
        # Calcular paginación
        total_archivos = len(archivos)
        total_paginas = (total_archivos + por_pagina - 1) // por_pagina
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        archivos_pagina = archivos[inicio:fin]
        
        # Formatear respuesta
        archivos_formateados = []
        for archivo in archivos_pagina:
            nombre = os.path.basename(archivo['rel_pdf'])
            carpeta = os.path.dirname(archivo['rel_pdf'])
            tamaño = os.path.getsize(archivo['ruta']) if os.path.exists(archivo['ruta']) else 0
            
            archivos_formateados.append({
                'nombre': nombre,
                'sede': archivo['sede'],
                'carpeta': carpeta,
                'ruta_relativa': archivo['rel_pdf'],
                'ruta_completa': archivo['ruta'],
                'tamano': tamaño,
                'tamaño_mb': round(tamaño / (1024 * 1024), 2),
                'fecha_modificacion': datetime.fromtimestamp(archivo['fecha']).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'archivos': archivos_formateados,
            'carpetas_disponibles': carpetas,
            'total': total_archivos,
            'pagina': pagina,
            'por_pagina': por_pagina,
            'total_paginas': total_paginas
        })
        
    except Exception as e:
        logger.error(f"Error al listar archivos de red: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@causaciones_bp.route('/api/carpetas/ver_pdf', methods=['GET'])
@requiere_permiso('causaciones', 'visualizar_pdf')
def ver_pdf_red():
    """
    Visualiza un PDF desde las carpetas de red
    Parámetro: ruta (ruta completa del archivo)
    """
    try:
        ruta_archivo = request.args.get('ruta')
        if not ruta_archivo:
            return jsonify({'success': False, 'message': 'Ruta de archivo requerida'}), 400
        
        # Validar que el archivo existe y es PDF
        if not os.path.exists(ruta_archivo):
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
        
        if not ruta_archivo.lower().endswith('.pdf'):
            return jsonify({'success': False, 'message': 'Solo se permiten archivos PDF'}), 400
        
        # Validar que la ruta pertenece a una carpeta configurada
        from config_carpetas import obtener_carpetas_base
        carpetas = obtener_carpetas_base()
        ruta_normalizada = os.path.normpath(ruta_archivo)
        
        ruta_valida = False
        for carpeta_base in carpetas.values():
            if ruta_normalizada.startswith(os.path.normpath(carpeta_base)):
                ruta_valida = True
                break
        
        if not ruta_valida:
            return jsonify({'success': False, 'message': 'Acceso no autorizado a esta ruta'}), 403
        
        return send_file(ruta_archivo, mimetype='application/pdf')
        
    except Exception as e:
        logger.error(f"Error al ver PDF de red: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

