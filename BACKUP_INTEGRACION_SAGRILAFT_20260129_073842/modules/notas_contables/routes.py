"""
Blueprint para el módulo de Notas Contables
Gestiona carga, visualización y descarga de documentos contables
"""
from flask import Blueprint, request, jsonify, send_file, render_template, session, redirect
from datetime import datetime
from werkzeug.utils import secure_filename
import sys
import os

# Agregar el directorio raíz al path para importar extensions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from extensions import db
from decoradores_permisos import requiere_permiso, requiere_permiso_html
from modules.notas_contables.models import DocumentoContable, AdjuntoDocumento, HistorialDocumento, ObservacionDocumento
from modules.configuracion.models import TipoDocumento, CentroOperacion, Empresa
from utils_fecha import obtener_fecha_naive_colombia

# Crear blueprint
notas_bp = Blueprint('notas_contables', __name__, url_prefix='/api/notas')

# Configuración de archivos
ALLOWED_EXTENSIONS_PDF = {'pdf'}
ALLOWED_EXTENSIONS_ADJUNTOS = {'pdf', 'xlsx', 'xls', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

# Ruta base de documentos (configurar en .env)
BASE_DIR_DOCUMENTOS = os.environ.get('BASE_DIR_DOCUMENTOS', 'D:/DOCUMENTOS_CONTABLES')

# =====================================================
# LOGGING DE SEGURIDAD (local a este módulo)
# =====================================================
def log_security(mensaje):
    """Registra eventos de seguridad en logs/security.log (función local)"""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'security.log')
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {mensaje}\n")
    except Exception as e:
        print(f"ERROR AL ESCRIBIR LOG: {e}")

def allowed_file(filename, allowed_extensions):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def crear_carpeta_documento(empresa, ano, mes, tipo_siglas, co_codigo, consecutivo):
    """
    Crea la estructura de carpetas: BASE_DIR/EMPRESA/AÑO/MES/CO/TIPO/CO-TIPO-CONSECUTIVO/
    Ejemplo: D:/DOCUMENTOS_CONTABLES/SC/2025/08/002/NOC/002-NOC-00000001/
    Retorna la ruta completa de la carpeta creada
    """
    try:
        # Formatear consecutivo con padding de ceros (8 dígitos)
        consecutivo_formateado = consecutivo.zfill(8)
        
        # Construir nombre de carpeta final: CO-TIPO-CONSECUTIVO
        nombre_carpeta = f"{co_codigo}-{tipo_siglas}-{consecutivo_formateado}"
        
        # Construir ruta: SC/2025/08/002/NOC/002-NOC-00000001/
        ruta = os.path.join(
            BASE_DIR_DOCUMENTOS,
            empresa,                    # SC o LG
            str(ano),                   # 2025
            str(mes).zfill(2),         # 08
            co_codigo,                  # 002
            tipo_siglas,                # NOC
            nombre_carpeta              # 002-NOC-00000001
        )
        
        # Crear carpetas si no existen
        os.makedirs(ruta, exist_ok=True)
        
        log_security(f"CARPETA CREADA | ruta={ruta}")
        return ruta
        
    except Exception as e:
        log_security(f"ERROR CREAR CARPETA | ruta={ruta} | error={str(e)}")
        raise

# =====================================================
# ENDPOINTS PARA CARGAR DOCUMENTOS
# =====================================================

@notas_bp.route('/cargar/validar', methods=['POST'])
@requiere_permiso('notas_contables', 'cargar_documento')
def validar_consecutivo():
    """Valida que el consecutivo no exista para el tipo y C.O. especificados"""
    try:
        data = request.get_json()
        
        tipo_id = data.get('tipo_documento_id')
        centro_id = data.get('centro_operacion_id')
        consecutivo = data.get('consecutivo', '').zfill(8)  # Auto-padding
        
        # Buscar documento con mismo tipo, C.O. y consecutivo
        documento_existente = DocumentoContable.query.filter_by(
            tipo_documento_id=tipo_id,
            centro_operacion_id=centro_id,
            consecutivo=consecutivo
        ).first()
        
        if documento_existente:
            # Compatibilidad: siempre 200 y exponer 'disponible' para el frontend y tests
            return jsonify({
                'success': False,
                'message': f'Ya existe un documento con consecutivo {consecutivo} para este tipo y C.O.',
                'existe': True,
                'disponible': False,
                'consecutivo_formateado': consecutivo
            }), 200
        
        return jsonify({
            'success': True,
            'message': 'Consecutivo disponible',
            'existe': False,
            'disponible': True,
            'consecutivo_formateado': consecutivo
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al validar consecutivo: {str(e)}'
        }), 500

@notas_bp.route('/validar-consecutivo-correccion/<int:documento_id>', methods=['POST'])
@requiere_permiso('notas_contables', 'solicitar_correccion_documento')
def validar_consecutivo_correccion(documento_id):
    """Valida en tiempo real que el nuevo consecutivo no exista (para formulario de corrección)"""
    try:
        data = request.get_json()
        
        # Obtener documento actual
        documento = DocumentoContable.query.get(documento_id)
        if not documento:
            return jsonify({
                'success': False,
                'message': 'Documento no encontrado'
            }), 404
        
        # Obtener valores del formulario (pueden ser parciales)
        tipo_nuevo_id = data.get('tipo_documento_id')
        centro_nuevo_id = data.get('centro_operacion_id')
        consecutivo_nuevo = data.get('consecutivo', '').zfill(8)
        
        # Determinar valores finales (usar nuevos si existen, si no usar actuales)
        tipo_final_id = tipo_nuevo_id if tipo_nuevo_id else documento.tipo_documento_id
        centro_final_id = centro_nuevo_id if centro_nuevo_id else documento.centro_operacion_id
        consecutivo_final = consecutivo_nuevo if consecutivo_nuevo else documento.consecutivo
        
        # Si no hay consecutivo nuevo o es igual al actual, no validar
        if not consecutivo_nuevo or consecutivo_nuevo == documento.consecutivo:
            return jsonify({
                'success': True,
                'message': 'Consecutivo sin cambios',
                'disponible': True,
                'sin_cambios': True
            }), 200
        
        # Buscar si existe otro documento con esa combinación
        doc_duplicado = DocumentoContable.query.filter_by(
            tipo_documento_id=tipo_final_id,
            centro_operacion_id=centro_final_id,
            consecutivo=consecutivo_final
        ).filter(
            DocumentoContable.id != documento_id  # Excluir el documento actual
        ).first()
        
        if doc_duplicado:
            from modules.configuracion.models import TipoDocumento, CentroOperacion
            tipo_obj = TipoDocumento.query.get(tipo_final_id)
            centro_obj = CentroOperacion.query.get(centro_final_id)
            nombre_duplicado = f"{centro_obj.codigo}-{tipo_obj.siglas}-{consecutivo_final}" if tipo_obj and centro_obj else "N/A"
            
            return jsonify({
                'success': False,
                'message': f'⚠️ Ya existe un documento con consecutivo {consecutivo_final}',
                'existe': True,
                'disponible': False,
                'documento_existente': doc_duplicado.nombre_archivo,
                'nombre_duplicado': nombre_duplicado,
                'consecutivo_formateado': consecutivo_final
            }), 200
        
        return jsonify({
            'success': True,
            'message': f'✓ Consecutivo {consecutivo_final} disponible',
            'existe': False,
            'disponible': True,
            'consecutivo_formateado': consecutivo_final
        }), 200
        
    except Exception as e:
        log_security(f"ERROR VALIDAR CONSECUTIVO | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al validar consecutivo: {str(e)}'
        }), 500

@notas_bp.route('/cargar/subir', methods=['POST'])
@requiere_permiso('notas_contables', 'cargar_documento')
def subir_documento():
    """
    Carga un documento principal con adjuntos opcionales
    Crea estructura de carpetas y guarda archivos
    """
    try:
        print("🔵 Iniciando carga de documento...")
        print(f"🔵 Archivos recibidos: {list(request.files.keys())}")
        print(f"🔵 Datos form: {list(request.form.keys())}")
        
        # Validar que venga el archivo principal
        if 'archivo_principal' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No se ha enviado el archivo principal'
            }), 400
        
        archivo_principal = request.files['archivo_principal']
        
        if archivo_principal.filename == '':
            return jsonify({
                'success': False,
                'message': 'No se ha seleccionado ningún archivo'
            }), 400
        
        # Validar extensión PDF
        if not allowed_file(archivo_principal.filename, ALLOWED_EXTENSIONS_PDF):
            return jsonify({
                'success': False,
                'message': 'El archivo principal debe ser un PDF'
            }), 400
        
        # Obtener datos del formulario
        tipo_id = int(request.form.get('tipo_documento_id'))
        centro_id = int(request.form.get('centro_operacion_id'))
        consecutivo = request.form.get('consecutivo', '').zfill(8)
        fecha_documento = request.form.get('fecha_documento')  # YYYY-MM-DD
        empresa = request.form.get('empresa', 'SC')  # SC o LG
        nombre_archivo = request.form.get('nombre_archivo', '')  # Editable por usuario
        observaciones = request.form.get('observaciones', '')
        created_by = request.form.get('created_by', 'sistema')
        
        # Obtener objetos de tipo y C.O. para nombres
        tipo = TipoDocumento.query.get(tipo_id)
        centro = CentroOperacion.query.get(centro_id)
        
        if not tipo or not centro:
            return jsonify({
                'success': False,
                'message': 'Tipo de documento o centro de operación no encontrado'
            }), 404
        
        # Validar consecutivo único
        if DocumentoContable.query.filter_by(
            tipo_documento_id=tipo_id,
            centro_operacion_id=centro_id,
            consecutivo=consecutivo
        ).first():
            return jsonify({
                'success': False,
                'message': f'Ya existe un documento con consecutivo {consecutivo}'
            }), 400
        
        # Extraer año y mes de la fecha
        fecha_obj = datetime.strptime(fecha_documento, '%Y-%m-%d')
        ano = fecha_obj.year
        mes = fecha_obj.month
        
        # Crear carpeta de documento
        ruta_carpeta = crear_carpeta_documento(
            empresa, ano, mes, tipo.siglas, centro.codigo, consecutivo
        )
        
        # Nombre para mostrar (SIN extensión .pdf)
        nombre_para_mostrar = nombre_archivo.strip() if nombre_archivo else ""
        
        # Si no hay nombre personalizado, generar automáticamente
        if not nombre_para_mostrar:
            nombre_para_mostrar = f"{centro.codigo}-{tipo.siglas}-{consecutivo}"
        
        # Quitar extensión .pdf si viene en el input
        if nombre_para_mostrar.lower().endswith('.pdf'):
            nombre_para_mostrar = nombre_para_mostrar[:-4]
        
        # Nombre del archivo físico (SIEMPRE con .pdf)
        nombre_archivo_fisico = f"{nombre_para_mostrar}.pdf"
        nombre_seguro = secure_filename(nombre_archivo_fisico)
        ruta_archivo_principal = os.path.join(ruta_carpeta, nombre_seguro)
        
        # Guardar archivo principal
        archivo_principal.save(ruta_archivo_principal)
        
        # Crear registro en base de datos (nombre_archivo SIN extensión .pdf)
        nuevo_documento = DocumentoContable(
            tipo_documento_id=tipo_id,
            centro_operacion_id=centro_id,
            consecutivo=consecutivo,
            fecha_documento=fecha_obj,
            empresa=empresa,
            nombre_archivo=nombre_para_mostrar,  # ✅ SIN extensión .pdf
            ruta_archivo=ruta_carpeta,
            observaciones=observaciones,
            estado='activo',
            created_by=created_by
        )
        
        db.session.add(nuevo_documento)
        db.session.flush()  # Obtener ID antes del commit
        
        # Registrar en historial
        historial = HistorialDocumento(
            documento_id=nuevo_documento.id,
            accion='CREADO',
            motivo='Carga inicial de documento',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=created_by
        )
        db.session.add(historial)
        
        # Procesar adjuntos (Excel, imágenes, etc) con etiquetas personalizadas
        adjuntos_info = []
        adjuntos_files = request.files.getlist('adjuntos[]')
        etiquetas_adjuntos = request.form.getlist('etiquetas[]')  # Recibir etiquetas
        
        # Formatear consecutivo para nombres de archivo (8 dígitos)
        consecutivo_formateado = consecutivo.zfill(8)
        prefijo_documento = f"{centro.codigo}-{tipo.siglas}-{consecutivo_formateado}"
        
        for idx, adjunto in enumerate(adjuntos_files):
            if adjunto and adjunto.filename != '':
                if not allowed_file(adjunto.filename, ALLOWED_EXTENSIONS_ADJUNTOS):
                    continue  # Saltar archivos con extensión no permitida
                
                # Obtener etiqueta personalizada o usar nombre original
                if idx < len(etiquetas_adjuntos) and etiquetas_adjuntos[idx]:
                    etiqueta = etiquetas_adjuntos[idx]
                else:
                    # Si no hay etiqueta, usar: PREFIJO_ANEXO_nombreoriginal
                    nombre_sin_ext = adjunto.filename.rsplit('.', 1)[0]
                    etiqueta = f"ANEXO_{nombre_sin_ext}"
                
                # Construir nombre final: 002-NOC-00000001_ANEXO_nombre
                extension = adjunto.filename.rsplit('.', 1)[1].lower()
                nombre_adjunto = f"{prefijo_documento}_{etiqueta}.{extension}"
                nombre_seguro = secure_filename(nombre_adjunto)
                
                ruta_adjunto = os.path.join(ruta_carpeta, nombre_seguro)
                adjunto.save(ruta_adjunto)
                
                # Crear registro de adjunto
                nuevo_adjunto = AdjuntoDocumento(
                    documento_id=nuevo_documento.id,
                    nombre_archivo=nombre_seguro,
                    ruta_archivo=ruta_carpeta,
                    tipo_archivo=extension,
                    tamano_bytes=os.path.getsize(ruta_adjunto),
                    descripcion=f'Adjunto: {etiqueta}',
                    created_by=created_by
                )
                db.session.add(nuevo_adjunto)
                adjuntos_info.append(nuevo_adjunto.to_dict())
        
        # Commit de toda la transacción
        db.session.commit()
        
        log_security(f"DOCUMENTO CARGADO | id={nuevo_documento.id} | tipo={tipo.siglas} | co={centro.codigo} | consecutivo={consecutivo} | adjuntos={len(adjuntos_info)} | usuario={created_by}")
        
        return jsonify({
            'success': True,
            'message': 'Documento cargado exitosamente',
            'data': {
                'documento': nuevo_documento.to_dict(include_relations=True),
                'adjuntos': adjuntos_info,
                'ruta_carpeta': ruta_carpeta
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CARGAR DOCUMENTO | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al cargar documento: {str(e)}'
        }), 500

# =====================================================
# ENDPOINTS PARA VISOR DE DOCUMENTOS
# =====================================================
@notas_bp.route('/listar', methods=['GET'])
@requiere_permiso('notas_contables', 'consultar_notas')
def listar_documentos():
    """
    Lista documentos con filtros opcionales
    Query params: tipo_id, centro_id, empresa, fecha_desde, fecha_hasta, estado, page, per_page
    """
    try:
        # Filtros
        tipo_id = request.args.get('tipo_id', type=int)
        centro_id = request.args.get('centro_id', type=int)
        empresa = request.args.get('empresa')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        estado = request.args.get('estado', 'activo')
        
        # Paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Construir query
        query = DocumentoContable.query
        
        if tipo_id:
            query = query.filter_by(tipo_documento_id=tipo_id)
        if centro_id:
            query = query.filter_by(centro_operacion_id=centro_id)
        if empresa:
            query = query.filter_by(empresa=empresa)
        if estado:
            query = query.filter_by(estado=estado)
        if fecha_desde:
            query = query.filter(DocumentoContable.fecha_documento >= fecha_desde)
        if fecha_hasta:
            query = query.filter(DocumentoContable.fecha_documento <= fecha_hasta)
        
        # Ordenar por fecha descendente
        query = query.order_by(DocumentoContable.fecha_documento.desc())
        
        # Paginar
        paginacion = query.paginate(page=page, per_page=per_page, error_out=False)
        
        documentos = [doc.to_dict(include_relations=True) for doc in paginacion.items]
        
        log_security(f"LISTADO DOCUMENTOS | total={paginacion.total} | page={page} | filtros=tipo:{tipo_id},centro:{centro_id},empresa:{empresa}")
        
        return jsonify({
            'success': True,
            'data': documentos,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginacion.total,
                'pages': paginacion.pages,
                'has_next': paginacion.has_next,
                'has_prev': paginacion.has_prev
            }
        }), 200
        
    except Exception as e:
        log_security(f"ERROR LISTAR DOCUMENTOS | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al listar documentos: {str(e)}'
        }), 500

@notas_bp.route('/descargar/<int:documento_id>', methods=['GET'])
@requiere_permiso('notas_contables', 'descargar_nota')
def descargar_documento(documento_id):
    """Descarga el archivo PDF principal de un documento"""
    try:
        documento = DocumentoContable.query.get(documento_id)
        
        if not documento:
            return jsonify({
                'success': False,
                'message': 'Documento no encontrado'
            }), 404
        
        # Construir ruta completa: nombre_archivo en BD NO tiene .pdf, agregarlo
        nombre_archivo_con_extension = f"{documento.nombre_archivo}.pdf"
        ruta_completa = os.path.join(documento.ruta_archivo, nombre_archivo_con_extension)
        
        if not os.path.exists(ruta_completa):
            return jsonify({
                'success': False,
                'message': f'Archivo no encontrado: {ruta_completa}'
            }), 404
        
        log_security(f"DESCARGA DOCUMENTO | id={documento_id} | archivo={nombre_archivo_con_extension} | IP={request.remote_addr}")
        
        return send_file(ruta_completa, as_attachment=True, download_name=nombre_archivo_con_extension)
        
    except Exception as e:
        log_security(f"ERROR DESCARGAR DOCUMENTO | id={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al descargar documento: {str(e)}'
        }), 500

@notas_bp.route('/visualizar/<int:documento_id>', methods=['GET'])
@requiere_permiso('notas_contables', 'visualizar_nota')
def visualizar_documento(documento_id):
    """Visualiza el archivo PDF principal en el navegador (SIN descarga)"""
    try:
        documento = DocumentoContable.query.get(documento_id)
        
        if not documento:
            return jsonify({
                'success': False,
                'message': 'Documento no encontrado'
            }), 404
        
        # Construir ruta completa: nombre_archivo en BD NO tiene .pdf, agregarlo
        nombre_archivo_con_extension = f"{documento.nombre_archivo}.pdf"
        base_dir = "D:/DOCUMENTOS_CONTABLES"
        ruta_completa = os.path.join(base_dir, documento.ruta_archivo, nombre_archivo_con_extension)
        
        if not os.path.exists(ruta_completa):
            return jsonify({
                'success': False,
                'message': f'Archivo no encontrado: {ruta_completa}'
            }), 404
        
        log_security(f"VISUALIZAR DOCUMENTO | id={documento_id} | archivo={nombre_archivo_con_extension} | IP={request.remote_addr}")
        
        # ✅ as_attachment=False para VISUALIZAR en navegador
        return send_file(ruta_completa, as_attachment=False, mimetype='application/pdf')
        
    except Exception as e:
        log_security(f"ERROR VISUALIZAR DOCUMENTO | id={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al visualizar documento: {str(e)}'
        }), 500

@notas_bp.route('/estadisticas', methods=['GET'])
@requiere_permiso('notas_contables', 'consultar_notas')
def obtener_estadisticas():
    """Obtiene estadísticas para el dashboard"""
    try:
        # Total de documentos activos
        total_documentos = DocumentoContable.query.filter_by(estado='activo').count()
        
        # Documentos del mes actual
        hoy = datetime.now()
        inicio_mes = datetime(hoy.year, hoy.month, 1)
        documentos_mes = DocumentoContable.query.filter(
            DocumentoContable.fecha_documento >= inicio_mes,
            DocumentoContable.estado == 'activo'
        ).count()
        
        # Documentos de hoy
        inicio_hoy = datetime(hoy.year, hoy.month, hoy.day)
        documentos_hoy = DocumentoContable.query.filter(
            DocumentoContable.fecha_documento >= inicio_hoy,
            DocumentoContable.estado == 'activo'
        ).count()
        
        # Documentos por empresa
        documentos_sc = DocumentoContable.query.filter_by(
            empresa='SC', 
            estado='activo'
        ).count()
        
        # Total de tipos y centros activos
        total_tipos = TipoDocumento.query.filter_by(estado='activo').count()
        total_centros = CentroOperacion.query.filter_by(estado='activo').count()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total_documentos,
                'mes': documentos_mes,
                'hoy': documentos_hoy,
                'sc': documentos_sc,
                'tipos': total_tipos,
                'centros': total_centros
            }
        }), 200
        
    except Exception as e:
        log_security(f"ERROR ESTADÍSTICAS | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener estadísticas: {str(e)}'
        }), 500

# =====================================================
# NUEVO: ENDPOINT PARA OPCIONES DEL FORMULARIO
# =====================================================
@notas_bp.route('/dashboard/opciones', methods=['GET'])
def obtener_opciones_formulario():
    """
    Retorna listas de tipos de documento, centros de operación y empresas activos
    para llenar selectores dinámicamente desde BD
    """
    try:
        # Obtener todos los tipos de documento activos
        tipos = TipoDocumento.query.filter_by(estado='activo').order_by(TipoDocumento.siglas).all()
        tipos_list = [{'id': t.id, 'siglas': t.siglas, 'nombre': t.nombre, 'modulo': t.modulo} for t in tipos]
        
        # Obtener todos los centros de operación activos (puede ser 'activo' o 'ACTIVO')
        centros = CentroOperacion.query.filter(
            db.or_(
                CentroOperacion.estado == 'activo',
                CentroOperacion.estado == 'ACTIVO'
            )
        ).order_by(CentroOperacion.codigo).all()
        centros_list = [{'id': c.id, 'codigo': c.codigo, 'nombre': c.nombre} for c in centros]
        
        # Obtener todas las empresas activas
        empresas = Empresa.query.filter_by(activo=True).order_by(Empresa.sigla).all()
        empresas_list = [{'id': e.id, 'sigla': e.sigla, 'nombre': e.nombre} for e in empresas]
        
        log_security(f"OPCIONES FORMULARIO | tipos={len(tipos_list)} | centros={len(centros_list)} | empresas={len(empresas_list)}")
        
        return jsonify({
            'success': True,
            'tipos': tipos_list,
            'centros': centros_list,
            'empresas': empresas_list
        }), 200
        
    except Exception as e:
        log_security(f"ERROR OPCIONES FORMULARIO | error={str(e)}")
        import traceback
        traceback.print_exc()  # Para debugging
        return jsonify({
            'success': False,
            'message': f'Error al obtener opciones: {str(e)}'
        }), 500

# =====================================================
# NUEVOS: ENDPOINTS PARA EDITAR/ELIMINAR
# =====================================================
@notas_bp.route('/detalle/<int:documento_id>', methods=['GET'])
@requiere_permiso('notas_contables', 'consultar_notas')
def obtener_detalle_documento(documento_id):
    """Obtiene detalles completos de un documento incluyendo adjuntos, historial y observaciones"""
    try:
        documento = DocumentoContable.query.get(documento_id)
        
        if not documento:
            return jsonify({
                'success': False,
                'message': 'Documento no encontrado'
            }), 404
        
        # Registrar visualización en historial
        historial_viz = HistorialDocumento(
            documento_id=documento_id,
            accion='VISUALIZADO',
            motivo='Usuario accedió al documento',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=session.get('usuario', 'anonimo')
        )
        db.session.add(historial_viz)
        db.session.commit()
        
        # Obtener adjuntos
        adjuntos = AdjuntoDocumento.query.filter_by(
            documento_id=documento_id
        ).all()
        
        # Obtener historial (ordenado de más reciente a más antigua)
        historial = HistorialDocumento.query.filter_by(
            documento_id=documento_id
        ).order_by(HistorialDocumento.created_at.desc()).all()
        
        # Obtener observaciones auditadas (ordenadas de más reciente a más antigua)
        observaciones = ObservacionDocumento.query.filter_by(
            documento_id=documento_id
        ).order_by(ObservacionDocumento.created_at.desc()).all()
        
        adjuntos_list = [adj.to_dict() for adj in adjuntos]
        historial_list = [hist.to_dict() for hist in historial]
        observaciones_list = [obs.to_dict() for obs in observaciones]
        
        return jsonify({
            'success': True,
            'data': {
                **documento.to_dict(include_relations=True),
                'adjuntos': adjuntos_list,
                'historial': historial_list,
                'observaciones_auditadas': observaciones_list
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR DETALLE DOCUMENTO | id={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener detalle: {str(e)}'
        }), 500

@notas_bp.route('/editar/<int:documento_id>', methods=['PUT'])
@requiere_permiso('notas_contables', 'editar_nota')
def editar_documento(documento_id):
    """Edita información de un documento existente"""
    try:
        documento = DocumentoContable.query.get(documento_id)
        
        if not documento:
            return jsonify({
                'success': False,
                'message': 'Documento no encontrado'
            }), 404
        
        data = request.get_json()
        
        # Campos editables
        if 'estado' in data:
            documento.estado = data['estado']
        if 'fecha_documento' in data:
            documento.fecha_documento = datetime.strptime(data['fecha_documento'], '%Y-%m-%d')
        if 'empresa' in data:
            documento.empresa = data['empresa']
        if 'observaciones' in data:
            documento.observaciones = data['observaciones']
        
        # ✅ RENOMBRADO DE DOCUMENTO PRINCIPAL
        if 'nuevo_nombre_principal' in data and data['nuevo_nombre_principal']:
            nuevo_nombre = data['nuevo_nombre_principal'].strip()
            if nuevo_nombre:
                # Renombrar archivo físico
                ruta_vieja = os.path.join(documento.ruta_archivo, f"{documento.nombre_archivo}.pdf")
                ruta_nueva = os.path.join(documento.ruta_archivo, f"{nuevo_nombre}.pdf")
                
                if os.path.exists(ruta_vieja):
                    os.rename(ruta_vieja, ruta_nueva)
                
                # Actualizar base de datos
                nombre_anterior = documento.nombre_archivo
                documento.nombre_archivo = nuevo_nombre
                
                # Registrar en historial
                historial_renombrado = HistorialDocumento(
                    documento_id=documento_id,
                    accion='RENOMBRADO',
                    motivo=f"Documento principal: '{nombre_anterior}' → '{nuevo_nombre}'",
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    created_by=session.get('usuario', 'sistema')
                )
                db.session.add(historial_renombrado)
        
        # ✅ RENOMBRADO DE ADJUNTO
        if 'adjunto_id' in data and 'nuevo_nombre_adjunto' in data:
            adjunto_id = data['adjunto_id']
            nuevo_nombre = data['nuevo_nombre_adjunto'].strip()
            
            adjunto = AdjuntoDocumento.query.get(adjunto_id)
            if adjunto and nuevo_nombre:
                # Renombrar archivo físico
                extension = os.path.splitext(adjunto.nombre_archivo)[1]
                if not nuevo_nombre.endswith(extension):
                    nuevo_nombre += extension
                
                ruta_vieja = os.path.join(adjunto.ruta_archivo, adjunto.nombre_archivo)
                ruta_nueva = os.path.join(adjunto.ruta_archivo, nuevo_nombre)
                
                if os.path.exists(ruta_vieja):
                    os.rename(ruta_vieja, ruta_nueva)
                
                # Actualizar base de datos
                nombre_anterior = adjunto.nombre_archivo
                adjunto.nombre_archivo = nuevo_nombre
                
                # Registrar en historial
                historial_renombrado_adj = HistorialDocumento(
                    documento_id=documento_id,
                    accion='RENOMBRADO',
                    motivo=f"Adjunto: '{nombre_anterior}' → '{nuevo_nombre}'",
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    created_by=session.get('usuario', 'sistema')
                )
                db.session.add(historial_renombrado_adj)
        
        documento.updated_by = session.get('usuario', 'sistema')
        # updated_at se actualiza automáticamente con onupdate
        
        # Registrar en historial
        historial = HistorialDocumento(
            documento_id=documento_id,
            accion='EDITADO',
            motivo=f"Cambios generales aplicados",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=documento.updated_by
        )
        db.session.add(historial)
        
        db.session.commit()
        
        log_security(f"DOCUMENTO EDITADO | id={documento_id} | estado={documento.estado} | usuario={documento.updated_by}")
        
        return jsonify({
            'success': True,
            'message': 'Documento actualizado exitosamente',
            'data': documento.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR EDITAR DOCUMENTO | id={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al editar documento: {str(e)}'
        }), 500

@notas_bp.route('/eliminar/<int:documento_id>', methods=['DELETE'])
@requiere_permiso('notas_contables', 'eliminar_nota')
def eliminar_documento(documento_id):
    """Marca un documento como eliminado (soft delete)"""
    try:
        documento = DocumentoContable.query.get(documento_id)
        
        if not documento:
            return jsonify({
                'success': False,
                'message': 'Documento no encontrado'
            }), 404
        
        # Soft delete: cambiar estado a 'eliminado'
        documento.estado = 'eliminado'
        documento.updated_by = 'sistema'  # Cambiar por usuario en sesión
        # updated_at se actualiza automáticamente
        
        # Registrar en historial
        historial = HistorialDocumento(
            documento_id=documento_id,
            accion='ELIMINADO',
            motivo='Eliminación solicitada por usuario',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=documento.updated_by
        )
        db.session.add(historial)
        
        db.session.commit()
        
        log_security(f"DOCUMENTO ELIMINADO | id={documento_id} | usuario={documento.updated_by}")
        
        return jsonify({
            'success': True,
            'message': 'Documento eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR ELIMINAR DOCUMENTO | id={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al eliminar documento: {str(e)}'
        }), 500
@notas_bp.route('/historial/<int:documento_id>', methods=['GET'])
@requiere_permiso('notas_contables', 'consultar_notas')
def obtener_historial(documento_id):
    """Obtiene el historial de cambios de un documento"""
    try:
        historial = HistorialDocumento.query.filter_by(
            documento_id=documento_id
        ).order_by(HistorialDocumento.created_at.desc()).all()
        
        historial_list = [h.to_dict() for h in historial]
        
        return jsonify({
            'success': True,
            'data': historial_list
        }), 200
        
    except Exception as e:
        log_security(f"ERROR HISTORIAL | id={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener historial: {str(e)}'
        }), 500

@notas_bp.route('/descargar_adjunto/<int:adjunto_id>', methods=['GET'])
@requiere_permiso('notas_contables', 'descargar_nota')
def descargar_adjunto(adjunto_id):
    """Descarga un archivo adjunto específico"""
    try:
        adjunto = AdjuntoDocumento.query.get(adjunto_id)
        
        if not adjunto:
            return jsonify({
                'success': False,
                'message': 'Adjunto no encontrado'
            }), 404
        
        ruta_completa = os.path.join(adjunto.ruta_archivo, adjunto.nombre_archivo)
        
        if not os.path.exists(ruta_completa):
            return jsonify({
                'success': False,
                'message': 'Archivo no encontrado en el sistema'
            }), 404
        
        log_security(f"DESCARGA ADJUNTO | id={adjunto_id} | archivo={adjunto.nombre_archivo}")
        
        return send_file(ruta_completa, as_attachment=True, download_name=adjunto.nombre_archivo)
        
    except Exception as e:
        log_security(f"ERROR DESCARGAR ADJUNTO | id={adjunto_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al descargar adjunto: {str(e)}'
        }), 500

@notas_bp.route('/visualizar_adjunto/<int:adjunto_id>', methods=['GET'])
@requiere_permiso('notas_contables', 'visualizar_nota')
def visualizar_adjunto(adjunto_id):
    """Visualiza un archivo adjunto en el navegador (SIN descarga)"""
    try:
        adjunto = AdjuntoDocumento.query.get(adjunto_id)
        
        if not adjunto:
            return jsonify({
                'success': False,
                'message': 'Adjunto no encontrado'
            }), 404
        
        base_dir = "D:/DOCUMENTOS_CONTABLES"
        ruta_completa = os.path.join(base_dir, adjunto.ruta_archivo)
        
        if not os.path.exists(ruta_completa):
            return jsonify({
                'success': False,
                'message': 'Archivo no encontrado en el sistema'
            }), 404
        
        log_security(f"VISUALIZAR ADJUNTO | id={adjunto_id} | archivo={adjunto.nombre_archivo}")
        
        # ✅ as_attachment=False para VISUALIZAR en navegador
        # Detectar tipo MIME según extensión
        extension = adjunto.tipo_archivo.lower()
        mime_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        mimetype = mime_types.get(extension, 'application/octet-stream')
        
        return send_file(ruta_completa, as_attachment=False, mimetype=mimetype)
        
    except Exception as e:
        log_security(f"ERROR VISUALIZAR ADJUNTO | id={adjunto_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al visualizar adjunto: {str(e)}'
        }), 500


# =====================================================
# RUTAS PARA RENDERIZAR TEMPLATES HTML
# =====================================================
@notas_bp.route('/cargar_notas', methods=['GET'])
@requiere_permiso_html('notas_contables', 'acceder_modulo')
def cargar_notas():
    """Renderiza el formulario de carga de documentos contables"""
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return redirect('/login')
        
        return render_template('cargar_documentos_contables.html')
    
    except Exception as e:
        log_security(f"ERROR CARGAR NOTAS | error={str(e)}")
        return f"Error al cargar página: {str(e)}", 500

@notas_bp.route('/visor', methods=['GET'])
@requiere_permiso_html('notas_contables', 'consultar_notas')
def visor_documentos():
    """Renderiza el visor de documentos contables con filtros y paginación"""
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return redirect('/login')
        
        # Obtener parámetros de filtro
        filtro = request.args.get('filtro', '')
        fecha_desde = request.args.get('desde', '')
        fecha_hasta = request.args.get('hasta', '')
        pagina = int(request.args.get('pagina', 1))
        por_pagina = int(request.args.get('por_pagina', 50))
        
        # Construir query base
        query = DocumentoContable.query
        
        # Aplicar filtros
        if filtro:
            query = query.filter(
                db.or_(
                    DocumentoContable.nombre_documento.ilike(f'%{filtro}%'),
                    DocumentoContable.consecutivo.ilike(f'%{filtro}%'),
                    DocumentoContable.usuario_creador.ilike(f'%{filtro}%')
                )
            )
        
        if fecha_desde:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(DocumentoContable.fecha_documento >= fecha_desde_obj)
        
        if fecha_hasta:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            query = query.filter(DocumentoContable.fecha_documento <= fecha_hasta_obj)
        
        # Ordenar por fecha de creación descendente
        query = query.order_by(DocumentoContable.fecha_creacion.desc())
        
        # Paginación
        total_documentos = query.count()
        total_paginas = (total_documentos + por_pagina - 1) // por_pagina
        
        documentos = query.limit(por_pagina).offset((pagina - 1) * por_pagina).all()
        
        return render_template(
            'visor_documentos_contables.html',
            documentos=documentos,
            total_documentos=total_documentos,
            pagina=pagina,
            total_paginas=total_paginas,
            por_pagina=por_pagina,
            filtro=filtro,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )
    
    except Exception as e:
        log_security(f"ERROR VISOR DOCUMENTOS | error={str(e)}")
        return f"Error al cargar visor: {str(e)}", 500

@notas_bp.route('/editar/<int:documento_id>', methods=['GET'])
@requiere_permiso_html('notas_contables', 'editar_nota')
def editar_nota(documento_id):
    """Renderiza el formulario de edición de documento contable"""
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return redirect('/login')
        
        # Buscar documento
        documento = DocumentoContable.query.get_or_404(documento_id)
        
        return render_template('editar_nota.html', documento=documento)
    
    except Exception as e:
        log_security(f"ERROR EDITAR NOTA | id={documento_id} | error={str(e)}")
        return f"Error al cargar editor: {str(e)}", 500

@notas_bp.route('/descargar_notas', methods=['POST'])
@requiere_permiso('notas_contables', 'descargar_nota')
def descargar_notas():
    """Descarga documentos seleccionados como ZIP"""
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
        
        # Obtener IDs seleccionados
        ids_seleccionados = request.form.getlist('seleccionados')
        
        if not ids_seleccionados:
            return jsonify({'success': False, 'message': 'No hay documentos seleccionados'}), 400
        
        # TODO: Implementar lógica de descarga ZIP
        return jsonify({
            'success': True,
            'message': 'Función de descarga ZIP en desarrollo',
            'total': len(ids_seleccionados)
        })
    
    except Exception as e:
        log_security(f"ERROR DESCARGAR NOTAS | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@notas_bp.route('/exportar_excel_notas', methods=['POST'])
@requiere_permiso('notas_contables', 'exportar_excel')
def exportar_excel_notas():
    """Exporta documentos seleccionados a Excel"""
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
        
        # Obtener IDs seleccionados
        ids_seleccionados = request.form.getlist('seleccionados')
        
        if not ids_seleccionados:
            return jsonify({'success': False, 'message': 'No hay documentos seleccionados'}), 400
        
        # TODO: Implementar lógica de exportación Excel
        return jsonify({
            'success': True,
            'message': 'Función de exportación Excel en desarrollo',
            'total': len(ids_seleccionados)
        })
    
    except Exception as e:
        log_security(f"ERROR EXPORTAR EXCEL | error={str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================================
# OBSERVACIONES
# =====================================================
@notas_bp.route('/observacion/<int:documento_id>', methods=['POST'])
@requiere_permiso('notas_contables', 'agregar_observacion')
def agregar_observacion(documento_id):
    """Agrega una nueva observación auditada a un documento"""
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
        
        # Verificar que el documento existe
        documento = DocumentoContable.query.get(documento_id)
        if not documento:
            return jsonify({'success': False, 'message': 'Documento no encontrado'}), 404
        
        # Obtener datos del request
        data = request.get_json()
        observacion_texto = data.get('observacion', '').strip()
        momento = data.get('momento', 'EDICION')  # CARGA o EDICION
        
        if not observacion_texto:
            return jsonify({'success': False, 'message': 'La observación no puede estar vacía'}), 400
        
        # Crear nueva observación
        nueva_obs = ObservacionDocumento(
            documento_id=documento_id,
            observacion=observacion_texto,
            momento=momento,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=session.get('usuario', 'sistema')
        )
        db.session.add(nueva_obs)
        
        # Registrar en historial
        historial = HistorialDocumento(
            documento_id=documento_id,
            accion='OBSERVACION_AGREGADA',
            motivo=f'Se agregó observación: {observacion_texto[:50]}...',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=session.get('usuario', 'sistema')
        )
        db.session.add(historial)
        
        db.session.commit()
        
        log_security(f"OBSERVACION AGREGADA | documento={documento_id} | usuario={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'message': 'Observación agregada correctamente',
            'data': nueva_obs.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR AGREGAR OBSERVACION | documento={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al agregar observación: {str(e)}'
        }), 500

@notas_bp.route('/agregar_adjuntos/<int:documento_id>', methods=['POST'])
@requiere_permiso('notas_contables', 'cargar_documento')
def agregar_adjuntos_adicionales(documento_id):
    """Permite agregar anexos adicionales a un documento existente"""
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
        
        # Verificar que el documento existe
        documento = DocumentoContable.query.get(documento_id)
        if not documento:
            return jsonify({'success': False, 'message': 'Documento no encontrado'}), 404
        
        # Verificar que se enviaron archivos
        if 'adjuntos' not in request.files:
            return jsonify({'success': False, 'message': 'No se enviaron archivos'}), 400
        
        archivos = request.files.getlist('adjuntos')
        if len(archivos) == 0:
            return jsonify({'success': False, 'message': 'No se seleccionaron archivos'}), 400
        
        # ✅ OBTENER NOMBRES PERSONALIZADOS (si existen)
        nombres_personalizados = []
        if 'nombres_personalizados' in request.form:
            import json
            nombres_personalizados = json.loads(request.form['nombres_personalizados'])
        
        # Procesar cada archivo
        archivos_guardados = []
        ruta_carpeta = documento.ruta_archivo  # Misma carpeta del documento principal
        
        for idx, archivo in enumerate(archivos):
            if archivo.filename == '':
                continue
            
            # Validar extensión
            extension = archivo.filename.rsplit('.', 1)[1].lower() if '.' in archivo.filename else ''
            if extension not in ALLOWED_EXTENSIONS_ADJUNTOS:
                continue
            
            # Validar tamaño
            archivo.seek(0, os.SEEK_END)
            tamano = archivo.tell()
            archivo.seek(0)
            
            if tamano > MAX_FILE_SIZE:
                continue
            
            # ✅ USAR NOMBRE PERSONALIZADO SI EXISTE
            if idx < len(nombres_personalizados) and nombres_personalizados[idx]:
                nombre_personalizado = secure_filename(nombres_personalizados[idx])
                # Asegurar extensión correcta
                if not nombre_personalizado.endswith(f'.{extension}'):
                    nombre_personalizado = f"{nombre_personalizado}.{extension}"
                nombre_final = nombre_personalizado
            else:
                # Nombre por defecto con timestamp
                nombre_base = secure_filename(archivo.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_final = f"{documento.nombre_archivo}_ANEXO_{timestamp}_{nombre_base}"
            
            ruta_completa = os.path.join(ruta_carpeta, nombre_final)
            
            # Guardar archivo
            archivo.save(ruta_completa)
            
            # Crear registro en BD
            nuevo_adjunto = AdjuntoDocumento(
                documento_id=documento_id,
                nombre_archivo=nombre_final,
                ruta_archivo=ruta_carpeta,
                tipo_archivo=extension,
                tamano_bytes=tamano,
                descripcion=f'Anexo agregado posteriormente',
                created_by=session.get('usuario', 'sistema')
            )
            db.session.add(nuevo_adjunto)
            archivos_guardados.append(nombre_final)
        
        # Registrar en historial
        historial = HistorialDocumento(
            documento_id=documento_id,
            accion='ANEXO_AGREGADO',
            motivo=f'Se agregaron {len(archivos_guardados)} anexo(s) adicional(es)',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=session.get('usuario', 'sistema')
        )
        db.session.add(historial)
        
        db.session.commit()
        
        log_security(f"ANEXOS AGREGADOS | documento={documento_id} | cantidad={len(archivos_guardados)} | usuario={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'message': f'{len(archivos_guardados)} anexo(s) agregado(s) correctamente',
            'archivos': archivos_guardados
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR AGREGAR ANEXOS | documento={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al agregar anexos: {str(e)}'
        }), 500


# ========================================
# 🔄 ENDPOINTS DE CORRECCIÓN DE DOCUMENTOS
# ========================================

@notas_bp.route('/solicitar-correccion/<int:documento_id>', methods=['POST'])
@requiere_permiso('notas_contables', 'solicitar_correccion_documento')
def solicitar_correccion_documento(documento_id):
    """
    Solicita corrección de campos críticos de un documento.
    Genera token de validación y envía código por correo.
    """
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
        
        usuario_nombre = session.get('usuario')
        print(f"\n{'='*80}")
        print(f"[CORRECCION] SOLICITUD DE CORRECCION INICIADA")
        print(f"{'='*80}")
        print(f"Usuario: {usuario_nombre}")
        print(f"Documento ID: {documento_id}")
        print(f"Documento ID: {documento_id}")
        
        # Obtener documento
        documento = DocumentoContable.query.get(documento_id)
        if not documento:
            print("❌ Documento no encontrado")
            return jsonify({'success': False, 'message': 'Documento no encontrado'}), 404
        
        print(f"✅ Documento encontrado: {documento.nombre_archivo}")
        
        # Obtener datos del request
        data = request.get_json()
        if not data:
            print("❌ No se recibieron datos JSON")
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400
        
        print(f"Datos recibidos: {data.keys()}")
        
        # Extraer campos del formulario
        empresa_nueva_id = data.get('empresa_id')
        tipo_nuevo_id = data.get('tipo_documento_id')
        centro_nuevo_id = data.get('centro_operacion_id')
        consecutivo_nuevo = data.get('consecutivo', '').strip()
        fecha_nueva = data.get('fecha_expedicion')
        justificacion = data.get('justificacion', '').strip()
        
        if not justificacion or len(justificacion) < 10:
            print("❌ Justificación inválida")
            return jsonify({
                'success': False,
                'message': 'La justificación debe tener al menos 10 caracteres'
            }), 400
        
        print(f"✅ Justificación válida: {len(justificacion)} caracteres")
        print(f"📋 Campos recibidos: empresa={empresa_nueva_id}, tipo={tipo_nuevo_id}, centro={centro_nuevo_id}, consec={consecutivo_nuevo}, fecha={fecha_nueva}")
        
        # Obtener sigla de empresa si se proporciona ID
        empresa_nueva_sigla = None
        if empresa_nueva_id:
            from modules.configuracion.models import Empresa
            emp = Empresa.query.get(empresa_nueva_id)
            if emp:
                empresa_nueva_sigla = emp.sigla
        
        # 🔍 DEBUG: Mostrar valores actuales del documento
        print(f"\n🔍 VALORES ACTUALES DEL DOCUMENTO:")
        print(f"   empresa: {documento.empresa}")
        print(f"   tipo_documento_id: {documento.tipo_documento_id}")
        print(f"   centro_operacion_id: {documento.centro_operacion_id}")
        print(f"   consecutivo: {documento.consecutivo}")
        print(f"   fecha_documento: {documento.fecha_documento}")
        
        print(f"\n🔍 VALORES NUEVOS RECIBIDOS:")
        print(f"   empresa_nueva_sigla: {empresa_nueva_sigla}")
        print(f"   tipo_nuevo_id: {tipo_nuevo_id}")
        print(f"   centro_nuevo_id: {centro_nuevo_id}")
        print(f"   consecutivo_nuevo: {consecutivo_nuevo}")
        print(f"   fecha_nueva: {fecha_nueva}")
        
        # Validar que al menos un campo cambió
        cambios_detectados = False
        if empresa_nueva_sigla and empresa_nueva_sigla != documento.empresa:
            print(f"   ✅ Cambio en empresa: {documento.empresa} → {empresa_nueva_sigla}")
            cambios_detectados = True
        if tipo_nuevo_id and tipo_nuevo_id != documento.tipo_documento_id:
            print(f"   ✅ Cambio en tipo: {documento.tipo_documento_id} → {tipo_nuevo_id}")
            cambios_detectados = True
        if centro_nuevo_id and centro_nuevo_id != documento.centro_operacion_id:
            print(f"   ✅ Cambio en centro: {documento.centro_operacion_id} → {centro_nuevo_id}")
            cambios_detectados = True
        if consecutivo_nuevo and consecutivo_nuevo != documento.consecutivo:
            print(f"   ✅ Cambio en consecutivo: {documento.consecutivo} → {consecutivo_nuevo}")
            cambios_detectados = True
        if fecha_nueva and fecha_nueva != str(documento.fecha_documento):
            print(f"   ✅ Cambio en fecha: {documento.fecha_documento} → {fecha_nueva}")
            cambios_detectados = True
        
        print(f"\n🔍 CAMBIOS DETECTADOS: {cambios_detectados}")
        
        if not cambios_detectados:
            return jsonify({
                'success': False,
                'message': 'No se detectaron cambios en los campos críticos'
            }), 400
        
        # ✅ VALIDAR QUE EL NUEVO CONSECUTIVO NO EXISTA (IGUAL QUE EN CARGA INICIAL)
        if consecutivo_nuevo or tipo_nuevo_id or centro_nuevo_id:
            from modules.configuracion.models import TipoDocumento, CentroOperacion
            
            # Determinar valores finales
            empresa_final = empresa_nueva_sigla or documento.empresa
            tipo_final_id = tipo_nuevo_id or documento.tipo_documento_id
            centro_final_id = centro_nuevo_id or documento.centro_operacion_id
            consecutivo_final = consecutivo_nuevo or documento.consecutivo
            
            print(f"🔍 Validando consecutivo único: Tipo={tipo_final_id}, Centro={centro_final_id}, Consecutivo={consecutivo_final}")
            
            # VALIDACIÓN IDÉNTICA A LA CARGA INICIAL
            # Buscar si ya existe un documento con ese tipo+centro+consecutivo
            doc_duplicado = DocumentoContable.query.filter_by(
                tipo_documento_id=tipo_final_id,
                centro_operacion_id=centro_final_id,
                consecutivo=consecutivo_final
            ).filter(
                DocumentoContable.id != documento_id  # Excluir el documento actual
            ).first()
            
            if doc_duplicado:
                # Obtener datos para mensaje claro
                tipo_doc_obj = TipoDocumento.query.get(tipo_final_id)
                centro_obj = CentroOperacion.query.get(centro_final_id)
                nombre_esperado = f"{centro_obj.codigo}-{tipo_doc_obj.siglas}-{consecutivo_final.zfill(8)}" if tipo_doc_obj and centro_obj else "N/A"
                
                print(f"❌ CONSECUTIVO YA EXISTE: {nombre_esperado} (ID: {doc_duplicado.id})")
                
                return jsonify({
                    'success': False,
                    'message': f'⚠️ Ya existe un documento con consecutivo {consecutivo_final} para este tipo y centro de operación',
                    'documento_existente': doc_duplicado.nombre_archivo,
                    'ruta_existente': doc_duplicado.ruta_archivo
                }), 409
            
            print(f"✅ Consecutivo disponible")
        
        # Validar justificación (validación adicional)
        if not justificacion or len(justificacion.strip()) < 10:
            return jsonify({
                'success': False,
                'message': 'La justificación debe tener al menos 10 caracteres'
            }), 400
        
        # Generar token de 6 dígitos
        import random
        token = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Calcular fecha de expiración (10 minutos)
        from utils_fecha import obtener_fecha_naive_colombia
        from datetime import timedelta
        
        fecha_creacion = obtener_fecha_naive_colombia()
        fecha_expiracion = fecha_creacion + timedelta(minutes=10)
        
        # Crear registro de token
        from modules.notas_contables.models import TokenCorreccionDocumento
        from datetime import datetime as dt
        
        # Convertir fecha_nueva a objeto date si existe
        fecha_doc_nueva = None
        if fecha_nueva:
            try:
                fecha_doc_nueva = dt.strptime(fecha_nueva, '%Y-%m-%d').date()
            except:
                pass
        
        token_correccion = TokenCorreccionDocumento(
            token=token,
            documento_id=documento_id,
            empresa_anterior=documento.empresa,
            empresa_nueva=empresa_nueva_sigla or documento.empresa,
            tipo_documento_anterior_id=documento.tipo_documento_id,
            tipo_documento_nuevo_id=tipo_nuevo_id or documento.tipo_documento_id,
            centro_operacion_anterior_id=documento.centro_operacion_id,
            centro_operacion_nuevo_id=centro_nuevo_id or documento.centro_operacion_id,
            consecutivo_anterior=documento.consecutivo,
            consecutivo_nuevo=consecutivo_nuevo or documento.consecutivo,
            fecha_documento_anterior=documento.fecha_documento,
            fecha_documento_nueva=fecha_doc_nueva or documento.fecha_documento,
            justificacion=justificacion.strip(),
            fecha_creacion=fecha_creacion,
            fecha_expiracion=fecha_expiracion,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=usuario_nombre
        )
        
        db.session.add(token_correccion)
        db.session.commit()
        
        print(f"✅ Token creado: ID={token_correccion.id}, Token={token}")
        
        # Obtener información del usuario logueado (correo)
        usuario_id = session.get('usuario_id')
        
        print(f"🔍 DEBUG: Session data - usuario={usuario_nombre}, usuario_id={usuario_id}")
        
        # Buscar correo del usuario
        correo_destinatario = None
        
        # Intento 1: Buscar en tabla usuarios por ID
        if usuario_id:
            try:
                from sqlalchemy import text
                result = db.session.execute(
                    text("SELECT correo FROM usuarios WHERE id = :uid"),
                    {"uid": usuario_id}
                ).fetchone()
                if result and result[0]:
                    correo_destinatario = result[0]
                    print(f"[OK] DEBUG: Correo encontrado por ID: {correo_destinatario}")
            except Exception as e:
                print(f"[WARN] DEBUG: Error buscando por ID: {e}")
        
        # Intento 2: Buscar en tabla usuarios por nombre de usuario
        if not correo_destinatario and usuario_nombre:
            try:
                result = db.session.execute(
                    text("SELECT correo FROM usuarios WHERE usuario = :uname"),
                    {"uname": usuario_nombre}
                ).fetchone()
                if result and result[0]:
                    correo_destinatario = result[0]
                    print(f"[OK] DEBUG: Correo encontrado por nombre: {correo_destinatario}")
            except Exception as e:
                print(f"[WARN] DEBUG: Error buscando por nombre: {e}")
        
        # Intento 3: Buscar en usuarios_internos
        if not correo_destinatario and usuario_nombre:
            try:
                from modules.usuarios_internos.models import UsuarioInterno
                user_int = UsuarioInterno.query.filter_by(username=usuario_nombre).first()
                if user_int and user_int.email:
                    correo_destinatario = user_int.email
                    print(f"[OK] DEBUG: Correo encontrado en usuarios_internos: {correo_destinatario}")
            except Exception as e:
                print(f"[WARN] DEBUG: Error buscando en usuarios_internos: {e}")
        
        # Si no se encuentra correo, retornar error
        if not correo_destinatario:
            print(f"[ERROR] DEBUG: No se encontro correo para usuario={usuario_nombre}, id={usuario_id}")
            return jsonify({
                'success': False,
                'message': f'No se encontró correo registrado para el usuario {usuario_nombre}'
            }), 400
        
        # Preparar resumen de cambios para el email
        cambios_html = "<ul>"
        if empresa_nueva_sigla and empresa_nueva_sigla != documento.empresa:
            from modules.configuracion.models import Empresa
            emp_ant = Empresa.query.filter_by(sigla=documento.empresa).first()
            emp_nva = Empresa.query.filter_by(sigla=empresa_nueva_sigla).first()
            cambios_html += f"<li><strong>Empresa:</strong> {emp_ant.nombre if emp_ant else documento.empresa} → {emp_nva.nombre if emp_nva else empresa_nueva_sigla}</li>"
        
        if tipo_nuevo_id and tipo_nuevo_id != documento.tipo_documento_id:
            from modules.configuracion.models import TipoDocumento
            tipo_ant = TipoDocumento.query.get(documento.tipo_documento_id)
            tipo_nvo = TipoDocumento.query.get(tipo_nuevo_id)
            cambios_html += f"<li><strong>Tipo:</strong> {tipo_ant.siglas if tipo_ant else 'N/A'} → {tipo_nvo.siglas if tipo_nvo else 'N/A'}</li>"
        
        if centro_nuevo_id and centro_nuevo_id != documento.centro_operacion_id:
            from modules.configuracion.models import CentroOperacion
            co_ant = CentroOperacion.query.get(documento.centro_operacion_id)
            co_nvo = CentroOperacion.query.get(centro_nuevo_id)
            cambios_html += f"<li><strong>Centro:</strong> {co_ant.codigo if co_ant else 'N/A'} - {co_ant.nombre if co_ant else 'N/A'} → {co_nvo.codigo if co_nvo else 'N/A'} - {co_nvo.nombre if co_nvo else 'N/A'}</li>"
        
        if consecutivo_nuevo and consecutivo_nuevo != documento.consecutivo:
            cambios_html += f"<li><strong>Consecutivo:</strong> {documento.consecutivo} → {consecutivo_nuevo}</li>"
        
        if fecha_nueva and fecha_nueva != str(documento.fecha_documento):
            cambios_html += f"<li><strong>Fecha de Expedición:</strong> {documento.fecha_documento} → {fecha_nueva}</li>"
        
        cambios_html += "</ul>"
        
        # Enviar correo con token
        from flask_mail import Message
        
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background: #f5f7fa; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; background: linear-gradient(135deg, #ea580c, #c2410c); color: white; padding: 25px; border-radius: 8px; margin-bottom: 30px; }}
                .token-box {{ background: #fff7ed; border: 2px solid #ea580c; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0; }}
                .token {{ font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #ea580c; font-family: monospace; }}
                .info {{ background: #eff6ff; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e8ed; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>[CORRECCION] Código de Corrección de Documento</h1>
                    <p>Archivo Digital - Gestión Documental</p>
                </div>
                
                <p>Hola <strong>{usuario_nombre}</strong>,</p>
                
                <p>Has solicitado corregir los siguientes campos del documento <strong>{documento.nombre_archivo}</strong>:</p>
                
                {cambios_html}
                
                <p><strong>Justificación:</strong> {justificacion}</p>
                
                <div class="token-box">
                    <p style="margin: 0; font-size: 14px; color: #666;">Tu código de validación es:</p>
                    <div class="token">{token}</div>
                </div>
                
                <div class="info">
                    <p style="margin: 0;"><strong>⏱ Validez:</strong> 10 minutos</p>
                    <p style="margin: 0;"><strong>🔢 Intentos permitidos:</strong> 3</p>
                </div>
                
                <p><strong>Instrucciones:</strong></p>
                <ol>
                    <li>Copia el código de 6 dígitos mostrado arriba</li>
                    <li>Pégalo en el formulario de edición del documento</li>
                    <li>Haz clic en "Validar y Aplicar Corrección"</li>
                </ol>
                
                <p style="color: #dc2626;"><strong>⚠️ IMPORTANTE:</strong> La corrección moverá los archivos a la nueva estructura de carpetas y renombrará el documento y sus anexos.</p>
                
                <div class="footer">
                    <p>Supertiendas Cañaveral - Sistema de Gestión Documental</p>
                    <p>Este es un mensaje automático, por favor no responder</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Enviar correo (manejo de error para que no bloquee el flujo)
        correo_enviado = False
        mensaje_correo = ""
        
        try:
            msg = Message(
                subject=f"[CORRECCION] Código de Corrección - Documento {documento.nombre_archivo}",
                recipients=[correo_destinatario],
                html=html_body
            )
            
            # Usar la instancia global de mail desde app
            from app import mail
            mail.send(msg)
            correo_enviado = True
            mensaje_correo = f"Código enviado a {correo_destinatario}"
            log_security(f"EMAIL ENVIADO | Corrección doc={documento_id} | destinatario={correo_destinatario}")
            
        except Exception as e_mail:
            correo_enviado = False
            mensaje_correo = f"Código generado (correo no enviado: {str(e_mail)})"
            log_security(f"ERROR EMAIL | Corrección doc={documento_id} | error={str(e_mail)}")
            
            # Mostrar token en consola como fallback
            print("\n" + "="*80)
            print(f"[ALERTA] CODIGO DE CORRECCION GENERADO (Correo fallo)")
            print("="*80)
            print(f"[EMAIL] Destinatario: {correo_destinatario}")
            print(f"[USER] Usuario: {usuario_nombre}")
            print(f"[DOC] Documento: {documento.nombre_archivo}")
            print(f"[TOKEN] TOKEN: {token}")
            print(f"[ERROR] Error: {str(e_mail)}")
            print("="*80 + "\n")
        
        log_security(f"CORRECCIÓN SOLICITADA | doc={documento_id} | usuario={usuario_nombre} | token_id={token_correccion.id}")
        
        return jsonify({
            'success': True,
            'message': mensaje_correo,
            'token_id': token_correccion.id,
            'expira_en_minutos': 10,
            'correo_enviado': correo_enviado
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()  # 🔍 Imprimir traceback completo en consola
        db.session.rollback()
        log_security(f"ERROR SOLICITAR CORRECCIÓN | doc={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al solicitar corrección: {str(e)}'
        }), 500


@notas_bp.route('/validar-correccion/<int:token_id>', methods=['POST'])
@requiere_permiso('notas_contables', 'validar_correccion_documento')
def validar_correccion_documento(token_id):
    """
    Valida el token de corrección y aplica los cambios al documento.
    Mueve archivos físicos y actualiza base de datos.
    """
    try:
        # Verificar sesión
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
        
        usuario = session.get('usuario')
        
        # Obtener datos del request
        data = request.get_json()
        token_ingresado = data.get('token', '').strip()
        
        if not token_ingresado or len(token_ingresado) != 6:
            return jsonify({
                'success': False,
                'message': 'Código de validación inválido'
            }), 400
        
        # Obtener registro del token
        from modules.notas_contables.models import TokenCorreccionDocumento
        token_correccion = TokenCorreccionDocumento.query.get(token_id)
        
        if not token_correccion:
            return jsonify({
                'success': False,
                'message': 'Token no encontrado'
            }), 404
        
        # Verificar que el token esté vigente
        if not token_correccion.esta_vigente():
            return jsonify({
                'success': False,
                'message': 'El código ha expirado o fue usado. Solicita uno nuevo.'
            }), 400
        
        # Incrementar contador de intentos
        token_correccion.intentos_validacion += 1
        db.session.commit()
        
        # Verificar código
        if token_correccion.token != token_ingresado:
            intentos_restantes = 3 - token_correccion.intentos_validacion
            
            if intentos_restantes <= 0:
                return jsonify({
                    'success': False,
                    'message': 'Código incorrecto. Se agotaron los intentos.'
                }), 400
            
            return jsonify({
                'success': False,
                'message': f'Código incorrecto. Te quedan {intentos_restantes} intento(s).'
            }), 400
        
        # ✅ CÓDIGO VÁLIDO - Procesar corrección
        documento = DocumentoContable.query.get(token_correccion.documento_id)
        
        if not documento:
            return jsonify({
                'success': False,
                'message': 'Documento no encontrado'
            }), 404
        
        # Guardar valores anteriores para historial
        valores_anteriores = {
            'empresa': documento.empresa,
            'tipo_documento_id': documento.tipo_documento_id,
            'centro_operacion_id': documento.centro_operacion_id,
            'consecutivo': documento.consecutivo,
            'fecha_documento': documento.fecha_documento,
            'nombre_archivo': documento.nombre_archivo,
            'ruta': documento.ruta_archivo
        }
        
        # Aplicar cambios en el documento
        documento.empresa = token_correccion.empresa_nueva
        documento.tipo_documento_id = token_correccion.tipo_documento_nuevo_id
        documento.centro_operacion_id = token_correccion.centro_operacion_nuevo_id
        documento.consecutivo = token_correccion.consecutivo_nuevo
        documento.fecha_documento = token_correccion.fecha_documento_nueva
        
            # ========================================
            # SOLUCIÓN RADICAL: MOVER Y RENOMBRAR ARCHIVOS
            # ========================================
        try:
            from modules.configuracion.models import Empresa, TipoDocumento, CentroOperacion
            import shutil
            
            # ============================================================================
            # 🎯 LÓGICA DE CORRECCIÓN DE ARCHIVOS - PASO A PASO
            # ============================================================================
            
            # Obtener información necesaria
            empresa = Empresa.query.filter_by(sigla=documento.empresa).first()
            tipo_doc = TipoDocumento.query.get(documento.tipo_documento_id)
            centro = CentroOperacion.query.get(documento.centro_operacion_id)
            
            # Base de datos
            base_dir = "D:/DOCUMENTOS_CONTABLES"
            
            # Obtener año y mes
            import datetime
            fecha_creacion = documento.created_at or obtener_fecha_naive_colombia()
            año = str(fecha_creacion.year)
            mes = str(fecha_creacion.month).zfill(2)
            
            # NUEVO NOMBRE BASE (nombre de la carpeta nueva)
            nuevo_nombre_base = f"{centro.codigo}-{tipo_doc.siglas}-{documento.consecutivo.zfill(8)}"
            print(f"\n{'='*80}")
            print(f"🎯 CORRECCIÓN DE DOCUMENTO")
            print(f"   Nuevo nombre: {nuevo_nombre_base}")
            print(f"{'='*80}")
            
            # ============================================================================
            # PASO 1: CREAR LA CARPETA NUEVA CON EL NOMBRE PRINCIPAL
            # ============================================================================
            directorio_tipo = os.path.join(base_dir, empresa.sigla, año, mes, centro.codigo, tipo_doc.siglas)
            nuevo_directorio = os.path.join(directorio_tipo, nuevo_nombre_base)
            
            print(f"\n📁 PASO 1: CREAR CARPETA NUEVA")
            print(f"   Ruta: {nuevo_directorio}")
            os.makedirs(nuevo_directorio, exist_ok=True)
            print(f"   ✅ Carpeta creada")
            
            # ============================================================================
            # PASO 2: TRAER ARCHIVO PRINCIPAL Y RENOMBRARLO
            # ============================================================================
            print(f"\n📄 PASO 2: TRAER ARCHIVO PRINCIPAL")
            
            # Ubicación anterior del archivo principal
            carpeta_anterior = os.path.join(base_dir, documento.ruta_archivo)
            archivo_principal_viejo = f"{documento.nombre_archivo}.pdf"
            ruta_archivo_principal_viejo = os.path.join(carpeta_anterior, archivo_principal_viejo)
            
            # Nuevo nombre y ubicación
            archivo_principal_nuevo = f"{nuevo_nombre_base}.pdf"
            ruta_archivo_principal_nuevo = os.path.join(nuevo_directorio, archivo_principal_nuevo)
            
            print(f"   Origen: {ruta_archivo_principal_viejo}")
            print(f"   Destino: {ruta_archivo_principal_nuevo}")
            
            # Mover archivo principal
            if os.path.exists(ruta_archivo_principal_viejo):
                # Si ya existe en destino, eliminarlo
                if os.path.exists(ruta_archivo_principal_nuevo):
                    os.remove(ruta_archivo_principal_nuevo)
                    print(f"   🗑️ Archivo destino eliminado")
                
                # Copiar archivo a nueva ubicación con nuevo nombre
                shutil.copy2(ruta_archivo_principal_viejo, ruta_archivo_principal_nuevo)
                print(f"   ✅ Archivo principal copiado y renombrado")
                
                # ⭐ ELIMINAR EL ORIGINAL de la carpeta anterior
                os.remove(ruta_archivo_principal_viejo)
                print(f"   🗑️ Original eliminado de carpeta anterior")
            else:
                raise Exception(f"❌ Archivo principal no encontrado: {ruta_archivo_principal_viejo}")
            
            # ============================================================================
            # PASO 3: TRAER ANEXOS UNO POR UNO Y RENOMBRARLOS
            # ============================================================================
            print(f"\n📎 PASO 3: BUSCAR Y TRAER ANEXOS")
            
            # ⭐ BUSCAR FÍSICAMENTE todos los archivos en la carpeta anterior
            archivos_en_carpeta_anterior = []
            if os.path.exists(carpeta_anterior):
                archivos_en_carpeta_anterior = [f for f in os.listdir(carpeta_anterior) 
                                               if os.path.isfile(os.path.join(carpeta_anterior, f)) 
                                               and f.endswith('.pdf')]
            
            print(f"   Archivos encontrados en carpeta anterior: {len(archivos_en_carpeta_anterior)}")
            
            # Filtrar solo los anexos (que contienen _ANEXO_)
            anexos_fisicos = [f for f in archivos_en_carpeta_anterior if '_ANEXO_' in f]
            print(f"   Anexos a procesar: {len(anexos_fisicos)}")
            
            # Procesar cada anexo encontrado físicamente
            adjuntos_bd = AdjuntoDocumento.query.filter_by(documento_id=documento.id).all()
            
            for idx, nombre_anexo_viejo in enumerate(anexos_fisicos, 1):
                print(f"\n   --- Anexo {idx}/{len(anexos_fisicos)} ---")
                print(f"   Archivo encontrado: {nombre_anexo_viejo}")
                
                # RENOMBRAR: Cambiar solo el PREFIJO antes de _ANEXO_
                sufijo_despues_anexo = nombre_anexo_viejo.split('_ANEXO_', 1)[1]
                nombre_anexo_nuevo = f"{nuevo_nombre_base}_ANEXO_{sufijo_despues_anexo}"
                
                print(f"   Nuevo nombre: {nombre_anexo_nuevo}")
                
                # Rutas completas
                ruta_anexo_viejo = os.path.join(carpeta_anterior, nombre_anexo_viejo)
                ruta_anexo_nuevo = os.path.join(nuevo_directorio, nombre_anexo_nuevo)
                
                print(f"   Origen: {ruta_anexo_viejo}")
                print(f"   Destino: {ruta_anexo_nuevo}")
                
                try:
                    # Si el destino existe, eliminarlo
                    if os.path.exists(ruta_anexo_nuevo):
                        if os.path.isdir(ruta_anexo_nuevo):
                            shutil.rmtree(ruta_anexo_nuevo)
                            print(f"   🗑️ Carpeta destino eliminada")
                        else:
                            os.remove(ruta_anexo_nuevo)
                            print(f"   🗑️ Archivo destino eliminado")
                    
                    # Copiar anexo
                    shutil.copy2(ruta_anexo_viejo, ruta_anexo_nuevo)
                    print(f"   ✅ Anexo copiado")
                    
                    # Eliminar original
                    os.remove(ruta_anexo_viejo)
                    print(f"   🗑️ Original eliminado")
                    
                    # Buscar el registro en BD y actualizarlo
                    adjunto_bd = None
                    for adj in adjuntos_bd:
                        if adj.nombre_archivo == nombre_anexo_viejo or nombre_anexo_viejo in adj.nombre_archivo:
                            adjunto_bd = adj
                            break
                    
                    if adjunto_bd:
                        adjunto_bd.nombre_archivo = nombre_anexo_nuevo
                        adjunto_bd.ruta_archivo = os.path.join(
                            empresa.sigla, año, mes, centro.codigo, tipo_doc.siglas,
                            nuevo_nombre_base, nombre_anexo_nuevo
                        ).replace('\\', '/')
                        print(f"   💾 BD actualizada")
                    else:
                        print(f"   ⚠️ No se encontró registro en BD (archivo huérfano)")
                        
                except Exception as e:
                    print(f"   ❌ Error procesando anexo: {str(e)}")
                    # Continuar con el siguiente anexo
            
            # ============================================================================
            # PASO 4: ACTUALIZAR BASE DE DATOS DEL DOCUMENTO PRINCIPAL
            # ============================================================================
            print(f"\n💾 PASO 4: ACTUALIZAR BASE DE DATOS")
            documento.ruta_archivo = os.path.join(
                empresa.sigla, año, mes, centro.codigo, tipo_doc.siglas, nuevo_nombre_base
            ).replace('\\', '/')
            documento.nombre_archivo = nuevo_nombre_base
            print(f"   ✅ BD del documento actualizada")
            
            # ============================================================================
            # PASO 5: VERIFICAR QUE TODO ESTÉ EN LA CARPETA NUEVA
            # ============================================================================
            print(f"\n✅ PASO 5: VERIFICACIÓN FINAL")
            archivos_en_nueva_carpeta = os.listdir(nuevo_directorio)
            print(f"   Archivos en carpeta nueva: {len(archivos_en_nueva_carpeta)}")
            for archivo in archivos_en_nueva_carpeta:
                print(f"   - {archivo}")
            
            # ============================================================================
            # PASO 6: ELIMINAR CARPETA ANTERIOR (solo si está vacía)
            # ============================================================================
            print(f"\n🗑️ PASO 6: LIMPIAR CARPETA ANTERIOR")
            try:
                if os.path.exists(carpeta_anterior):
                    archivos_restantes = os.listdir(carpeta_anterior)
                    if len(archivos_restantes) == 0:
                        os.rmdir(carpeta_anterior)
                        print(f"   ✅ Carpeta anterior eliminada (estaba vacía)")
                    else:
                        print(f"   ⚠️ Carpeta anterior NO eliminada (tiene {len(archivos_restantes)} archivos)")
                        # Eliminar archivos que ya copiamos
                        for archivo in archivos_restantes:
                            ruta_archivo = os.path.join(carpeta_anterior, archivo)
                            if archivo == archivo_principal_viejo or archivo.startswith(documento.nombre_archivo):
                                os.remove(ruta_archivo)
                                print(f"   🗑️ Eliminado: {archivo}")
                        # Intentar eliminar carpeta de nuevo
                        if len(os.listdir(carpeta_anterior)) == 0:
                            os.rmdir(carpeta_anterior)
                            print(f"   ✅ Carpeta anterior eliminada")
            except Exception as e:
                print(f"   ⚠️ No se pudo eliminar carpeta anterior: {str(e)}")
            
            print(f"\n{'='*80}")
            print(f"✅ CORRECCIÓN COMPLETADA")
            print(f"{'='*80}\n")
            
            # Intentar eliminar directorio antiguo (si está vacío)
            try:
                if os.path.exists(directorio_anterior) and not os.listdir(directorio_anterior):
                    os.rmdir(directorio_anterior)
            except:
                pass  # No es crítico si no se puede eliminar
            
        except Exception as e_move:
            db.session.rollback()
            log_security(f"ERROR MOVER ARCHIVOS | doc={documento.id} | error={str(e_move)}")
            return jsonify({
                'success': False,
                'message': f'Error al mover archivos: {str(e_move)}'
            }), 500
        
        # Marcar token como usado
        token_correccion.usado = True
        token_correccion.validado_por = usuario
        
        # Registrar en historial
        from utils_fecha import obtener_fecha_naive_colombia
        
        resumen_cambios = f"CORRECCIÓN APLICADA: "
        if valores_anteriores['empresa'] != documento.empresa:
            resumen_cambios += f"Empresa({valores_anteriores['empresa']}→{documento.empresa}) "
        if valores_anteriores['tipo_documento_id'] != documento.tipo_documento_id:
            resumen_cambios += f"Tipo({valores_anteriores['tipo_documento_id']}→{documento.tipo_documento_id}) "
        if valores_anteriores['centro_operacion_id'] != documento.centro_operacion_id:
            resumen_cambios += f"Centro({valores_anteriores['centro_operacion_id']}→{documento.centro_operacion_id}) "
        if valores_anteriores['consecutivo'] != documento.consecutivo:
            resumen_cambios += f"Consec({valores_anteriores['consecutivo']}→{documento.consecutivo}) "
        
        resumen_cambios += f"| Justificación: {token_correccion.justificacion}"
        
        historial = HistorialDocumento(
            documento_id=documento.id,
            accion='correccion_critica',
            motivo=resumen_cambios,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=usuario
        )
        db.session.add(historial)
        
        db.session.commit()
        
        # Enviar email de confirmación
        # Obtener correo del usuario logueado por ID
        usuario_id = session.get('usuario_id')
        from app import Usuario
        usuario_obj = Usuario.query.get(usuario_id)
        
        if usuario_obj and usuario_obj.correo:
            correo_destinatario = usuario_obj.correo
            
            from flask_mail import Message
            from flask import current_app
            
            html_confirmacion = f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f5f7fa; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; background: linear-gradient(135deg, #16a34a, #15803d); color: white; padding: 25px; border-radius: 8px; margin-bottom: 30px; }}
                    .success-box {{ background: #f0fdf4; border: 2px solid #16a34a; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e8ed; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Corrección Aplicada Exitosamente</h1>
                        <p>Archivo Digital - Gestión Documental</p>
                    </div>
                    
                    <div class="success-box">
                        <h2 style="color: #16a34a; margin: 0;">Documento Actualizado</h2>
                        <p style="margin-top: 10px;">El documento ha sido corregido y los archivos se movieron a la nueva ubicación.</p>
                    </div>
                    
                    <p><strong>Documento:</strong> {valores_anteriores['nombre_archivo']} → {documento.nombre_archivo}</p>
                    <p><strong>Nueva ubicación:</strong> {documento.ruta_archivo}</p>
                    <p><strong>Fecha:</strong> {obtener_fecha_naive_colombia().strftime('%d/%m/%Y %H:%M:%S')}</p>
                    
                    <div class="footer">
                        <p>Supertiendas Cañaveral - Sistema de Gestión Documental</p>
                        <p>Este es un mensaje automático, por favor no responder</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=f"✅ Corrección Aplicada - {documento.nombre_archivo}",
                recipients=[correo_destinatario],
                html=html_confirmacion
            )
            
            # Enviar correo usando el mismo patrón del módulo de relaciones
            from flask import current_app
            with current_app.app_context():
                from flask_mail import Mail
                mail = Mail(current_app)
                mail.send(msg)
        
        # ============================================================================
        # 📋 LOG COMPLETO DE AUDITORÍA
        # ============================================================================
        from utils_fecha import obtener_fecha_naive_colombia
        fecha_hora_correccion = obtener_fecha_naive_colombia().strftime("%Y-%m-%d %H:%M:%S")
        
        log_auditoria = f"""
================================================================================
🔄 CORRECCIÓN DE DOCUMENTO APLICADA
================================================================================
📅 Fecha/Hora: {fecha_hora_correccion}
👤 Usuario: {usuario} (ID: {session.get('usuario_id')})
🌐 IP: {request.remote_addr}
💻 User Agent: {request.headers.get('User-Agent', 'N/A')}
🔐 Token usado: {token_correccion.token}
🔢 Token ID: {token_id}

📄 DOCUMENTO:
   ID: {documento.id}
   Nombre original: {valores_anteriores['nombre_base']}
   Nombre final: {documento.nombre_archivo}
   
📁 RUTAS:
   Ruta original: {valores_anteriores['ruta_original']}
   Ruta final: {documento.ruta_archivo}

🔄 CAMBIOS APLICADOS:
   Empresa: {valores_anteriores['empresa']} → {documento.empresa}
   Tipo: {valores_anteriores['tipo_documento_id']} → {documento.tipo_documento_id}
   Centro: {valores_anteriores['centro_operacion_id']} → {documento.centro_operacion_id}
   Consecutivo: {valores_anteriores['consecutivo']} → {documento.consecutivo}
   Fecha expedición: {valores_anteriores['fecha_expedicion']} → {documento.fecha_expedicion}

📎 ADJUNTOS MODIFICADOS: {len(adjuntos_bd)} archivo(s)
"""
        
        # Agregar detalles de cada adjunto
        for adj in adjuntos_bd:
            log_auditoria += f"   - {adj.nombre_archivo}\n"
        
        # Agregar observaciones del documento
        observaciones_texto = documento.observaciones if hasattr(documento, 'observaciones') and documento.observaciones else "Sin observaciones"
        
        log_auditoria += f"""
📝 JUSTIFICACIÓN: {token_correccion.justificacion}

💬 OBSERVACIONES DEL DOCUMENTO:
{observaciones_texto}

================================================================================
"""
        
        log_security(log_auditoria)
        
        return jsonify({
            'success': True,
            'message': 'Corrección aplicada exitosamente',
            'nuevo_nombre': documento.nombre_archivo,
            'nueva_ruta': documento.ruta_archivo,
            'documento_id': documento.id,
            'refresh': True  # ⭐ Indicar al frontend que debe refrescar
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR VALIDAR CORRECCIÓN | token_id={token_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al validar corrección: {str(e)}'
        }), 500


@notas_bp.route('/datos-documento/<int:documento_id>', methods=['GET'])
@requiere_permiso('notas_contables', 'editar_documento')
def obtener_datos_documento(documento_id):
    """
    Obtiene los datos actuales del documento para prellenar el formulario de corrección
    """
    try:
        documento = DocumentoContable.query.get(documento_id)
        
        if not documento:
            return jsonify({
                'success': False,
                'message': 'Documento no encontrado'
            }), 404
        
        # Obtener datos completos de la empresa
        empresa_obj = Empresa.query.filter_by(sigla=documento.empresa).first()
        
        # Obtener datos del tipo de documento
        tipo_doc_obj = TipoDocumento.query.get(documento.tipo_documento_id)
        
        # Obtener datos del centro de operación
        centro_obj = CentroOperacion.query.get(documento.centro_operacion_id)
        
        # Construir nombre actual del archivo principal (formato CO-TIPO-CONSEC)
        nombre_archivo_principal = f"{centro_obj.codigo}-{tipo_doc_obj.siglas}-{documento.consecutivo.zfill(8)}"
        
        return jsonify({
            'success': True,
            'data': {
                'id': documento.id,
                'empresa_id': empresa_obj.id if empresa_obj else None,
                'empresa_sigla': documento.empresa,
                'empresa_nombre': empresa_obj.nombre if empresa_obj else 'N/A',
                'tipo_documento_id': documento.tipo_documento_id,
                'tipo_documento_siglas': tipo_doc_obj.siglas if tipo_doc_obj else 'N/A',
                'centro_operacion_id': documento.centro_operacion_id,
                'centro_operacion_codigo': centro_obj.codigo if centro_obj else 'N/A',
                'centro_operacion_nombre': centro_obj.nombre if centro_obj else 'N/A',
                'consecutivo': documento.consecutivo,
                'fecha_documento': str(documento.fecha_documento),
                'nombre_archivo': documento.nombre_archivo,
                'nombre_archivo_principal': nombre_archivo_principal
            }
        }), 200
        
    except Exception as e:
        log_security(f"ERROR OBTENER DATOS DOCUMENTO | doc_id={documento_id} | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener datos del documento: {str(e)}'
        }), 500


@notas_bp.route('/opciones-correccion', methods=['GET'])
def obtener_opciones_correccion():
    """
    Endpoint para obtener las opciones de empresas, tipos y centros
    para el formulario de corrección de documentos
    SIN REQUERIR PERMISOS (para permitir carga en todos los usuarios)
    """
    try:
        # Obtener empresas
        empresas = Empresa.query.order_by(Empresa.sigla).all()
        empresas_data = [{
            'id': e.id,
            'sigla': e.sigla,
            'nombre': e.nombre,
            'razon_social': e.nombre  # Por compatibilidad
        } for e in empresas]
        
        # Obtener tipos de documento (TODOS los tipos, sin filtrar por módulo)
        tipos = TipoDocumento.query.order_by(TipoDocumento.siglas).all()
        tipos_data = [{
            'id': t.id,
            'siglas': t.siglas,
            'nombre': t.nombre
        } for t in tipos]
        
        # Obtener centros de operación
        centros = CentroOperacion.query.order_by(CentroOperacion.codigo).all()
        centros_data = [{
            'id': c.id,
            'codigo': c.codigo,
            'nombre': c.nombre
        } for c in centros]
        
        log_security(f"OPCIONES CORRECCIÓN | empresas={len(empresas_data)} | tipos={len(tipos_data)} | centros={len(centros_data)}")
        
        return jsonify({
            'success': True,
            'data': {
                'empresas': empresas_data,
                'tipos': tipos_data,
                'centros': centros_data
            }
        }), 200
        
    except Exception as e:
        log_security(f"ERROR OPCIONES CORRECCIÓN | error={str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener opciones: {str(e)}'
        }), 500


