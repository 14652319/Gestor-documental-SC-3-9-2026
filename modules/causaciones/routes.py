"""
Backend del módulo de Causaciones - Versión compatible con sistema original
Funcionalidad: Visualizar y renombrar PDFs de carpetas de red
"""
from flask import Blueprint, render_template, request, send_file, session, redirect, url_for, flash, abort, jsonify
from decoradores_permisos import requiere_permiso_html, requiere_permiso
import os
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from io import BytesIO
import pandas as pd

# Usa el logger "security" compartido → escribe en logs/security.log (igual que app.py)
logger = logging.getLogger("security")

def log_security(mensaje):
    """Registra eventos de seguridad en logger compartido (logs/security.log)"""
    logger.info(mensaje)

# Crear Blueprint
causaciones_bp = Blueprint('causaciones', __name__, url_prefix='/causaciones')

# ============================================================================
# RUTA PRINCIPAL: Vista de causaciones
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
    
    from config_carpetas import obtener_carpetas_base, obtener_sedes_disponibles
    
    carpetas_base = obtener_carpetas_base()
    sedes_disponibles = list(carpetas_base.keys())  # TODAS las sedes (incluye _C y CYS_)
    
    # Sedes APROBADAS = las que NO terminan en _C (se derivan automáticamente de config_carpetas)
    # Si en el futuro se agrega una sede nueva en config_carpetas.py, se incluye aquí sola.
    sedes_solo_aprobadas = [k for k in carpetas_base.keys() if not k.endswith('_C')]
    
    # Parámetros de filtros
    sedes_seleccionadas = request.args.getlist("sede")
    if not sedes_seleccionadas or sedes_seleccionadas == ['']:
        # Carga inicial: solo APROBADAS (más rápido — la mitad de carpetas vs "Todo")
        sedes_seleccionadas = sedes_solo_aprobadas
    
    ruta_relativa = request.args.get("carpeta", "__all__")
    filtro = request.args.get("filtro", "").lower()
    filtro_anio = request.args.get("anio", "").strip()
    filtro_mes = request.args.get("mes", "").strip()
    filtro_tipo = request.args.get("tipo", "").strip()
    pagina = int(request.args.get("pagina", 1))
    por_pagina = int(request.args.get("por_pagina", 50))
    archivo_actual = request.args.get("archivo", "")
    
    # Determinar sedes a revisar  
    if "Todo" in sedes_seleccionadas:
        sedes_a_revisar = list(carpetas_base.keys())  # Todas las carpetas (12)
    else:
        # Usar las sedes seleccionadas directamente
        sedes_a_revisar = sedes_seleccionadas
    
    # Recolectar carpetas y archivos
    carpetas = set()
    archivos = []
    anios_disponibles = set()
    meses_disponibles = set()
    tipos_disponibles = set()
    
    for sede in sedes_a_revisar:
        carpeta_principal = carpetas_base.get(sede, "")
        if not os.path.exists(carpeta_principal):
            logger.warning(f"Carpeta no existe: {carpeta_principal}")
            continue
        
        # Explorar subcarpetas
        for root, dirs, files in os.walk(carpeta_principal):
            rel_path = os.path.relpath(root, carpeta_principal).replace("\\", "/")
            
            # Extraer años y meses disponibles de la estructura de carpetas
            partes = rel_path.split("/")
            for parte in partes:
                if parte.isdigit() and len(parte) == 4:
                    anios_disponibles.add(parte)
                elif any(mes in parte.upper() for mes in ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']):
                    meses_disponibles.add(parte)
            
            # Extraer tipo (primera subcarpeta: ESTANDAR, TARJETAS_DE_CREDITO, etc.)
            if rel_path != ".":
                tipos_disponibles.add(rel_path.split("/")[0])
            
            # Aplicar filtro de tipo: si el primer segmento no coincide, saltar
            if filtro_tipo and (rel_path == "." or rel_path.split("/")[0] != filtro_tipo):
                continue
            
            # Aplicar filtro de año: si rel_path no contiene el año, saltar
            if filtro_anio and filtro_anio not in rel_path:
                continue
            
            # Aplicar filtro de mes: si rel_path no contiene el mes, saltar
            if filtro_mes and filtro_mes not in rel_path:
                continue
            
            # Agregar carpetas al listado
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
                    
                    # Construir ruta relativa completa (siempre con /)
                    if archivo_rel:
                        archivo_completo = f"{archivo_rel}/{file}".replace("\\", "/")
                    else:
                        archivo_completo = file.replace("\\", "/")
                    
                    archivos.append({
                        'sede': sede,
                        'archivo': archivo_completo,
                        'timestamp': fecha_mod,
                        'fecha': datetime.fromtimestamp(fecha_mod).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except Exception as e:
                    logger.error(f"Error procesando {file}: {e}")
                    continue
    
    # Ordenar por timestamp (más ANTIGUOS primero - reverse=False)
    archivos.sort(key=lambda x: x['timestamp'], reverse=False)
    
    # DEBUG: Mostrar primeros 3 archivos para verificar orden
    if archivos:
        print("🔍 DEBUG ORDEN - Primeros 3 archivos:")
        for i, arch in enumerate(archivos[:3]):
            print(f"  {i+1}. {arch['fecha']} - {arch['archivo']}")
    
    # Paginación
    total_archivos = len(archivos)
    total_paginas = max(1, (total_archivos + por_pagina - 1) // por_pagina)
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    archivos_pagina = archivos[inicio:fin]
    
    # Estados y otros datos (placeholders)
    estados = {}
    historiales = {}
    archivos_ocupados = {}
    
    # Ordenar sedes alfabéticamente y agregar "Todo" al inicio
    sedes_ordenadas = sorted(sedes_disponibles)
    sedes = ['Todo'] + sedes_ordenadas
    
    logger.info(f"Causaciones: {total_archivos} archivos encontrados en {len(sedes_a_revisar)} carpetas")
    
    # Ordenar años (desc: más reciente primero) y meses (por número)
    orden_meses = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
    def orden_mes(m):
        for i, nombre in enumerate(orden_meses):
            if nombre in m.upper():
                return i
        return 99
    anios_lista = sorted(anios_disponibles, reverse=True)
    meses_lista = sorted(meses_disponibles, key=orden_mes)
    
    return render_template('causacion_mejorado.html',
        sedes=sedes,
        sede=sedes_seleccionadas,
        carpetas=sorted(list(carpetas)),
        archivos=archivos_pagina,
        estados=estados,
        historiales=historiales,
        ruta_relativa=ruta_relativa,
        filtro=filtro,
        filtro_anio=filtro_anio,
        filtro_mes=filtro_mes,
        filtro_tipo=filtro_tipo,
        anios_disponibles=anios_lista,
        meses_disponibles=meses_lista,
        tipos_disponibles=sorted(tipos_disponibles),
        archivo_actual=archivo_actual,
        cantidad_archivos=total_archivos,
        pagina=pagina,
        total_paginas=total_paginas,
        por_pagina=por_pagina,
        archivos_ocupados=archivos_ocupados
    )

# ============================================================================
# SERVIR PDF
# ============================================================================
@causaciones_bp.route('/ver/<sede>/<path:archivo>')
@requiere_permiso_html('causaciones', 'ver_pdf')
def servir_pdf(sede, archivo):
    """Sirve archivos PDF con validación de seguridad"""
    try:
        from config_carpetas import obtener_carpetas_base
        from urllib.parse import unquote
        
        # Decodificar la sede si viene encoded
        sede = unquote(sede)
        
        carpetas_base = obtener_carpetas_base()
        carpeta_sede = carpetas_base.get(sede, "")
        
        if not carpeta_sede:
            logger.error(f"Sede '{sede}' no encontrada en carpetas_base. Sedes disponibles: {list(carpetas_base.keys())}")
            return jsonify({'error': f'Sede {sede} no configurada'}), 404
        
        # Construir ruta segura
        ruta_archivo = os.path.join(carpeta_sede, archivo.replace("/", os.sep))
        ruta_archivo = os.path.normpath(ruta_archivo)
        
        logger.info(f"Sede: {sede}")
        logger.info(f"Carpeta base: {carpeta_sede}")
        logger.info(f"Archivo solicitado: {archivo}")
        logger.info(f"Ruta completa: {ruta_archivo}")
        
        # Validar que existe
        if not os.path.exists(ruta_archivo):
            logger.error(f"Archivo no existe: {ruta_archivo}")
            # Buscar archivos similares para debug
            directorio = os.path.dirname(ruta_archivo)
            if os.path.exists(directorio):
                archivos_dir = os.listdir(directorio)
                logger.error(f"Archivos en {directorio}: {archivos_dir[:5]}")
            return jsonify({'error': 'Archivo no encontrado', 'ruta': ruta_archivo}), 404
        
        # Validar que está dentro de la carpeta permitida
        if not ruta_archivo.startswith(os.path.normpath(carpeta_sede)):
            logger.error(f"Intento de acceso fuera de carpeta permitida: {ruta_archivo}")
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Validar que es un PDF
        if not ruta_archivo.lower().endswith('.pdf'):
            logger.error(f"Archivo no es PDF: {ruta_archivo}")
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400
        
        return send_file(ruta_archivo, mimetype='application/pdf')
        
    except Exception as e:
        logger.error(f"Error inesperado al servir PDF: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error al cargar PDF: {str(e)}'}), 500

# ============================================================================
# API: OBTENER METADATA COMPLETA DEL DOCUMENTO
# ============================================================================
@causaciones_bp.route('/api/metadata/<sede>/<path:archivo>')
@requiere_permiso('causaciones', 'consultar_documentos')
def obtener_metadata(sede, archivo):
    """
    Retorna metadata completa del documento desde la base de datos.
    Parsea el nombre del archivo para extraer NIT + prefijo + folio y busca
    en FacturaRecibida usando la misma clave que usan los demás módulos.

    Formatos soportados:
      805027317FECR-29998.pdf  → NIT=805027317, prefijo=FECR, folio=29998
      261463205 -20260301.pdf  → NIT=261463205, prefijo='',   folio=20260301
      NIT_PREFIJO_FOLIO.pdf    → separador guion bajo
    """
    import re
    try:
        from config_carpetas import obtener_carpetas_base
        from modules.recibir_facturas.models import FacturaRecibida, ObservacionFactura

        carpetas_base = obtener_carpetas_base()
        carpeta_sede = carpetas_base.get(sede, "")

        if not carpeta_sede:
            return jsonify({'success': False, 'error': 'Sede no encontrada'}), 404

        ruta_archivo = os.path.join(carpeta_sede, archivo.replace("/", os.sep))
        ruta_archivo = os.path.normpath(ruta_archivo)

        if not os.path.exists(ruta_archivo):
            return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404

        nombre_archivo = os.path.basename(ruta_archivo)
        nombre_sin_ext = os.path.splitext(nombre_archivo)[0]

        metadata = {
            'nombre_archivo': nombre_archivo,
            'ruta': archivo,
            'ruta_completa': archivo,
            'sede': sede,
            'existe_en_bd': False
        }

        factura = None
        nit_p = None
        prefijo_p = None
        folio_p = None

        # --- Intento 1: NIT + PREFIJO(letras) + separador + FOLIO ---
        # Ejemplos: 805027317FECR-29998 | 805027317-FECR-29997 - signed | 805027317FECR_29998
        m = re.match(r'^(\d+)[-_\s]*([A-Za-z]+)[-_\s]+(\d+)', nombre_sin_ext)
        if m:
            nit_p = m.group(1)
            prefijo_p = m.group(2).upper()
            folio_p = m.group(3).lstrip('0') or '0'
            candidatas = FacturaRecibida.query.filter_by(nit=nit_p, prefijo=prefijo_p).all()
            for f in candidatas:
                if (f.folio_normalizado or '') == folio_p:
                    factura = f
                    break

        # --- Intento 2: Solo NIT + separador + FOLIO (sin prefijo alfabético) ---
        # Ejemplo: 261463205 -20260301
        if not factura:
            m2 = re.match(r'^(\d+)\s*[-_\s]+\s*(\d+)', nombre_sin_ext)
            if m2:
                nit_p = m2.group(1)
                folio_p = m2.group(2).lstrip('0') or '0'
                candidatas = FacturaRecibida.query.filter_by(nit=nit_p, prefijo='').all()
                for f in candidatas:
                    if (f.folio_normalizado or '') == folio_p:
                        factura = f
                        break

        # --- Fallback: buscar en FacturaTemporal (facturas pendientes de aprobación) ---
        es_temporal = False
        if not factura:
            from modules.recibir_facturas.models import FacturaTemporal
            m3 = re.match(r'^(\d+)[-_\s]*([A-Za-z]*)[-_\s]+(\d+)', nombre_sin_ext)
            if m3:
                nit_p = m3.group(1)
                prefijo_p = m3.group(2).upper()
                folio_p = m3.group(3).lstrip('0') or '0'
                candidatas = FacturaTemporal.query.filter_by(nit=nit_p, prefijo=prefijo_p).all()
                for f in candidatas:
                    if (f.folio_normalizado or '') == folio_p:
                        factura = f
                        es_temporal = True
                        break

        # --- Buscar en FacturaDigital (facturas_digitales) ---
        factura_digital = None
        if nit_p and folio_p:
            try:
                from modules.facturas_digitales.models import FacturaDigital
                candidatas_fd = FacturaDigital.query.filter_by(nit_proveedor=nit_p).all()
                for fd in candidatas_fd:
                    num = fd.numero_factura or ''
                    # numero_factura puede ser "FECR-29998" o solo "29998" → extraer folio del final
                    m_fd = re.search(r'(\d+)$', num)
                    if m_fd and m_fd.group(1).lstrip('0') == folio_p:
                        factura_digital = fd
                        break
            except Exception as e_fd:
                logger.warning(f"FacturaDigital lookup error: {e_fd}")

        # --- Buscar CUFE en MaestroDianVsErp y Dian ---
        cufe = None
        dian_estado = None
        if nit_p and folio_p:
            try:
                from modules.dian_vs_erp.models import MaestroDianVsErp, Dian
                maestro_rows = MaestroDianVsErp.query.filter_by(nit_emisor=nit_p, prefijo=prefijo_p or '').all()
                for mm in maestro_rows:
                    if (mm.folio or '').lstrip('0') == folio_p:
                        cufe = mm.cufe
                        dian_estado = mm.estado_aprobacion
                        break
                if not cufe:
                    dian_rows = Dian.query.filter_by(nit_emisor=nit_p, prefijo=prefijo_p or '').all()
                    for dr in dian_rows:
                        if (dr.folio or '').lstrip('0') == folio_p:
                            cufe = dr.cufe_cude
                            break
            except Exception as e_dian:
                logger.warning(f"DIAN CUFE lookup error: {e_dian}")

        metadata['existe_en_bd'] = factura is not None or factura_digital is not None or cufe is not None
        metadata['es_temporal'] = es_temporal
        metadata['cufe'] = cufe
        metadata['dian_estado'] = dian_estado
        metadata['factura_digital'] = {
            'radicado': factura_digital.radicado_rfd,
            'estado': factura_digital.estado,
            'observaciones': factura_digital.observaciones,
            'empresa': factura_digital.empresa,
            'departamento': getattr(factura_digital, 'departamento', None),
            'usuario_carga': getattr(factura_digital, 'usuario_carga', None),
            'fecha_carga': factura_digital.fecha_carga.strftime('%Y-%m-%d') if getattr(factura_digital, 'fecha_carga', None) else None,
        } if factura_digital else None

        if factura:
            obs_list = []

            # Observaciones del modelo relacional (solo FacturaRecibida tiene ObservacionFactura)
            if not es_temporal:
                observaciones_rel = ObservacionFactura.query.filter_by(
                    factura_id=factura.id
                ).order_by(ObservacionFactura.fecha_creacion.desc()).all()
                obs_list = [
                    {
                        'observacion': obs.observacion,
                        'usuario': obs.usuario_nombre,
                        'fecha': obs.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if obs.fecha_creacion else None
                    }
                    for obs in observaciones_rel
                ]

            # Campo observaciones directo (ambas tablas lo tienen)
            if factura.observaciones and factura.observaciones.strip():
                obs_list.append({
                    'observacion': factura.observaciones.strip(),
                    'usuario': factura.usuario_nombre or 'Sistema',
                    'fecha': factura.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if factura.fecha_creacion else None
                })

            metadata.update({
                'id': factura.id,
                'consecutivo': factura.numero_factura,
                'estado': 'TEMPORAL (pendiente aprobación)' if es_temporal else 'RECIBIDA',
                'fecha_factura': factura.fecha_expedicion.strftime('%Y-%m-%d') if factura.fecha_expedicion else None,
                'fecha_recepcion': factura.fecha_radicacion.strftime('%Y-%m-%d') if factura.fecha_radicacion else None,
                'nit_tercero': factura.nit,
                'razon_social': factura.razon_social or 'N/A',
                'valor_total': float(factura.valor_neto) if factura.valor_neto else 0,
                'centro_operacion': factura.centro_operacion,
                'tipo_documento': factura.forma_pago,
                'usuario_registro': factura.usuario_nombre,
                'observaciones': obs_list
            })

        # Si no hay factura en recibir_facturas pero sí en factura digital, rellenar datos básicos
        if not factura and factura_digital:
            metadata.update({
                'id': factura_digital.id,
                'consecutivo': factura_digital.numero_factura,
                'estado': 'DIGITAL (' + (factura_digital.estado or 'N/A') + ')',
                'nit_tercero': factura_digital.nit_proveedor,
                'razon_social': getattr(factura_digital, 'razon_social_proveedor', None) or 'N/A',
                'valor_total': float(factura_digital.valor_total) if getattr(factura_digital, 'valor_total', None) else 0,
                'usuario_registro': getattr(factura_digital, 'usuario_carga', None),
                'fecha_factura': factura_digital.fecha_emision.strftime('%Y-%m-%d') if getattr(factura_digital, 'fecha_emision', None) else None,
                'observaciones': []
            })

        return jsonify({'success': True, 'metadata': metadata})

    except Exception as e:
        logger.error(f"Error obteniendo metadata: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# API: EXPORTAR LISTADO A EXCEL
# ============================================================================
@causaciones_bp.route('/exportar/excel')
@requiere_permiso_html('causaciones', 'exportar_excel')
def exportar_excel():
    """
    Exporta el listado de archivos filtrados a Excel
    Incluye: Sede, Carpeta, Nombre de Archivo, Fecha
    """
    try:
        from config_carpetas import obtener_carpetas_base, obtener_sedes_disponibles
        
        # Obtener parámetros de filtros (igual que en index)
        sedes_seleccionadas = request.args.getlist("sede")
        if not sedes_seleccionadas or sedes_seleccionadas == ['']:
            sedes_seleccionadas = ["Todo"]
        
        ruta_relativa = request.args.get("carpeta", "__all__")
        filtro = request.args.get("filtro", "").lower()
        filtro_anio = request.args.get("anio", "").strip()
        filtro_mes = request.args.get("mes", "").strip()
        filtro_tipo = request.args.get("tipo", "").strip()
        
        # Log de depuración para exportación
        logger.info(f"EXPORTAR EXCEL: sedes={sedes_seleccionadas}, carpeta={ruta_relativa}, filtro='{filtro}', anio='{filtro_anio}', mes='{filtro_mes}'")
        
        carpetas_base = obtener_carpetas_base()
        
        # Determinar sedes a revisar (MISMA LÓGICA QUE INDEX)
        if "Todo" in sedes_seleccionadas or not sedes_seleccionadas or sedes_seleccionadas == ['']:
            sedes_a_revisar = list(carpetas_base.keys())  # Todas las carpetas
            sedes_seleccionadas = ["Todo"]  # Asegurar que se muestre "Todo" en el selector
        else:
            # Usar las sedes seleccionadas directamente (SIN agregar sufijo _C)
            sedes_a_revisar = sedes_seleccionadas
        
        # Recolectar archivos (misma lógica que index)
        archivos = []
        
        for sede in sedes_a_revisar:
            carpeta_principal = carpetas_base.get(sede, "")
            if not os.path.exists(carpeta_principal):
                continue
            
            for root, dirs, files in os.walk(carpeta_principal):
                rel_path = os.path.relpath(root, carpeta_principal).replace("\\", "/")
                
                # Aplicar filtro de tipo, año y mes al escaneo
                if filtro_tipo and (rel_path == "." or rel_path.split("/")[0] != filtro_tipo):
                    continue
                if filtro_anio and filtro_anio not in rel_path:
                    continue
                if filtro_mes and filtro_mes not in rel_path:
                    continue
                
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
                    
                    try:
                        ruta_completa = os.path.join(root, file)
                        fecha_mod = os.path.getmtime(ruta_completa)
                        
                        if archivo_rel:
                            archivo_completo = f"{archivo_rel}/{file}"
                            carpeta_display = archivo_rel
                        else:
                            archivo_completo = file
                            carpeta_display = "Raíz"
                        
                        archivos.append({
                            'sede': sede,
                            'carpeta': carpeta_display,
                            'archivo': file,
                            'timestamp': fecha_mod,
                            'fecha': datetime.fromtimestamp(fecha_mod).strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except Exception as e:
                        logger.error(f"Error procesando {file}: {e}")
                        continue
        
        # Ordenar por fecha (más recientes primero)
        archivos.sort(key=lambda x: x['timestamp'], reverse=False)
        
        # Crear DataFrame con información de filtros aplicados
        df_data = []
        for item in archivos:
            try:
                # Construir ruta para obtener tamaño
                carpeta_sede = carpetas_base.get(item['sede'], '')
                if item['carpeta'] == 'Raíz':
                    ruta_archivo = os.path.join(carpeta_sede, item['archivo'])
                else:
                    ruta_archivo = os.path.join(carpeta_sede, item['carpeta'], item['archivo'])
                
                # Obtener tamaño en MB
                tamaño_mb = 0
                if os.path.exists(ruta_archivo):
                    tamaño_mb = round(os.path.getsize(ruta_archivo) / (1024*1024), 2)
                
                df_data.append({
                    'Sede': item['sede'],
                    'Carpeta': item['carpeta'],
                    'Nombre de Archivo': item['archivo'],
                    'Fecha de Modificación': item['fecha'],
                    'Tamaño MB': tamaño_mb
                })
            except Exception as e:
                # Si hay error, agregar sin tamaño
                df_data.append({
                    'Sede': item['sede'],
                    'Carpeta': item['carpeta'],
                    'Nombre de Archivo': item['archivo'],
                    'Fecha de Modificación': item['fecha'],
                    'Tamaño MB': 0
                })
        
        df = pd.DataFrame(df_data)
        
        # Crear información de filtros aplicados
        filtros_info = {
            'Filtro de Sedes': ', '.join(sedes_seleccionadas) if sedes_seleccionadas else 'Todas',
            'Filtro de Carpeta': ruta_relativa if ruta_relativa != '__all__' else 'Todas las carpetas',
            'Filtro de Texto': filtro if filtro else 'Sin filtro de texto',
            'Total de Archivos': len(archivos),
            'Fecha de Exportación': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Usuario': session.get('usuario', 'desconocido')
        }
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Hoja principal con archivos
            df.to_excel(writer, sheet_name='Archivos', index=False)
            
            # Hoja con información de filtros
            filtros_df = pd.DataFrame(list(filtros_info.items()), columns=['Filtro', 'Valor'])
            filtros_df.to_excel(writer, sheet_name='Filtros Aplicados', index=False)
            
            # Obtener workbooks para formatear
            workbook = writer.book
            worksheet_archivos = writer.sheets['Archivos']
            worksheet_filtros = writer.sheets['Filtros Aplicados']
            
            # Formato de encabezados
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#20c997',
                'font_color': '#ffffff',
                'border': 1
            })
            
            # Aplicar formato a encabezados de archivos
            for col_num, value in enumerate(df.columns.values):
                worksheet_archivos.write(0, col_num, value, header_format)
            
            # Aplicar formato a encabezados de filtros
            for col_num, value in enumerate(['Filtro', 'Valor']):
                worksheet_filtros.write(0, col_num, value, header_format)
            
            # Ajustar anchos de columna - Archivos
            worksheet_archivos.set_column('A:A', 15)  # Sede
            worksheet_archivos.set_column('B:B', 40)  # Carpeta
            worksheet_archivos.set_column('C:C', 50)  # Nombre de Archivo
            worksheet_archivos.set_column('D:D', 20)  # Fecha
            worksheet_archivos.set_column('E:E', 12)  # Tamaño
            
            # Ajustar anchos de columna - Filtros
            worksheet_filtros.set_column('A:A', 25)  # Filtro
            worksheet_filtros.set_column('B:B', 40)  # Valor
        
        output.seek(0)
        
        # Generar nombre de archivo con fecha actual
        nombre_archivo = f"causaciones_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Log de seguridad
        usuario = session.get('usuario', 'desconocido')
        filtros_aplicados = {
            'sedes': sedes_seleccionadas, 
            'carpeta': ruta_relativa,
            'filtro_texto': filtro
        }
        logger.info(f"EXCEL EXPORTADO | usuario={usuario} | archivos={len(archivos)} | filtros={filtros_aplicados}")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=nombre_archivo
        )
        
    except Exception as e:
        logger.error(f"Error exportando a Excel: {e}")
        flash(f"❌ Error al exportar: {str(e)}", "error")
        return redirect(url_for('causaciones.index'))

# ============================================================================
# API: ELIMINAR ARCHIVO (Solo para admins)
# ============================================================================
@causaciones_bp.route('/api/eliminar/<sede>/<path:archivo>', methods=['POST'])
@requiere_permiso('causaciones', 'eliminar_archivo')
def eliminar_archivo(sede, archivo):
    """
    Elimina un archivo (solo para usuarios con permiso)
    """
    try:
        # Verificar rol de admin
        rol_usuario = session.get('rol', 'externo')
        if rol_usuario not in ['admin', 'interno']:
            return jsonify({'success': False, 'error': 'No tienes permisos para eliminar archivos'}), 403
        
        from config_carpetas import obtener_carpetas_base
        
        carpetas_base = obtener_carpetas_base()
        carpeta_sede = carpetas_base.get(sede, "")
        
        if not carpeta_sede:
            return jsonify({'success': False, 'error': 'Sede no encontrada'}), 404
        
        # Construir ruta segura
        ruta_archivo = os.path.join(carpeta_sede, archivo.replace("/", os.sep))
        ruta_archivo = os.path.normpath(ruta_archivo)
        
        # Validar que existe y está dentro de la carpeta permitida
        if not os.path.exists(ruta_archivo) or not ruta_archivo.startswith(os.path.normpath(carpeta_sede)):
            return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404
        
        # Eliminar archivo
        os.remove(ruta_archivo)
        
        # Log de seguridad
        usuario = session.get('usuario', 'desconocido')
        logger.info(f"ARCHIVO ELIMINADO | usuario={usuario} | archivo={archivo} | sede={sede}")
        
        return jsonify({'success': True, 'message': 'Archivo eliminado correctamente'})
        
    except Exception as e:
        logger.error(f"Error eliminando archivo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# RENOMBRAR ARCHIVO
# ============================================================================
@causaciones_bp.route('/renombrar/<sede>/<path:archivo>', methods=['GET', 'POST'])
@requiere_permiso_html('causaciones', 'renombrar_archivo')
def renombrar(sede, archivo):
    """Interfaz para renombrar archivos"""
    try:
        from config_carpetas import obtener_carpetas_base
        
        logger.info(f"=== RENOMBRAR: Iniciando ===")
        logger.info(f"Sede recibida: {sede}")
        logger.info(f"Archivo recibido: {archivo}")
        logger.info(f"Method: {request.method}")
        
        carpetas_base = obtener_carpetas_base()
        carpeta_origen = carpetas_base.get(sede, "")
        
        logger.info(f"Carpeta origen: {carpeta_origen}")
        logger.info(f"Sedes disponibles: {list(carpetas_base.keys())}")
        
        if not carpeta_origen:
            logger.error(f"Sede '{sede}' no encontrada en carpetas_base")
            flash("❌ Sede no válida.")
            return redirect(url_for('causaciones.index'))
        
        archivo_original = os.path.join(carpeta_origen, archivo.replace("/", os.sep))
        nombre_actual = os.path.basename(archivo_original)  # Extraer nombre del archivo
        
        # Eliminar espacios del nombre original para sugerir nombre limpio
        nombre_sin_extension = os.path.splitext(nombre_actual)[0]
        nombre_limpio_sugerido = nombre_sin_extension.replace(' ', '')  # Eliminar todos los espacios
        
        logger.info(f"Ruta archivo completa: {archivo_original}")
        logger.info(f"Nombre actual: {nombre_actual}")
        logger.info(f"Nombre limpio sugerido: {nombre_limpio_sugerido}")
        logger.info(f"Archivo existe: {os.path.exists(archivo_original)}")
        
        if not os.path.exists(archivo_original):
            logger.error(f"Archivo no existe: {archivo_original}")
            flash("❌ Error: El archivo original no existe.")
            return redirect(url_for('causaciones.index'))
        
        if request.method == 'POST':
            nuevo_nombre_campo = request.form.get('nuevo_nombre', '').strip()
            carpeta_destino_tipo = request.form.get('carpeta_destino', 'original')  # 'original' o 'causadas'
            
            # CONSTRUIR NUEVO NOMBRE: REEMPLAZAR completamente (NO concatenar)
            # Eliminar TODOS los espacios del nombre ingresado
            if nuevo_nombre_campo:
                nuevo_nombre_limpio = nuevo_nombre_campo.replace(' ', '')  # Eliminar espacios
                nuevo_nombre = f"{nuevo_nombre_limpio}.pdf"
            else:
                nuevo_nombre = nombre_actual  # Sin cambios si no se digita nada
            
            # DETERMINAR CARPETA DESTINO
            directorio_original = os.path.dirname(archivo_original)
            logger.info(f"📂 Directorio original: {directorio_original}")
            logger.info(f"📋 Carpeta destino solicitada: {carpeta_destino_tipo}")
            
            if carpeta_destino_tipo == 'causadas':
                # Cambiar de APROBADAS a CAUSADAS
                if 'APROBADAS' in directorio_original:
                    carpeta_destino = directorio_original.replace('APROBADAS', 'CAUSADAS')
                    logger.info(f"✅ Cambiando a CAUSADAS: {carpeta_destino}")
                else:
                    carpeta_destino = directorio_original  # Si no está en APROBADAS, se queda igual
                    logger.warning(f"⚠️ La carpeta original no contiene 'APROBADAS', se mantiene en: {carpeta_destino}")
            else:
                # Mantener en carpeta original (APROBADAS)
                carpeta_destino = directorio_original
                logger.info(f"📍 Se mantiene en carpeta original: {carpeta_destino}")
            
            archivo_nuevo = os.path.join(carpeta_destino, nuevo_nombre)
            logger.info(f"🎯 Archivo destino final: {archivo_nuevo}")
            
            try:
                # Crear carpeta destino si no existe
                logger.info(f"🔧 Creando carpeta destino (si no existe): {carpeta_destino}")
                os.makedirs(carpeta_destino, exist_ok=True)
                logger.info(f"✅ Carpeta destino confirmada")
                
                # Verificar que el nuevo nombre no existe EN LA CARPETA DESTINO
                if os.path.exists(archivo_nuevo) and archivo_nuevo != archivo_original:
                    flash(f"❌ Ya existe un archivo con el nombre: {nuevo_nombre} en la carpeta destino")
                    logger.warning(f"⚠️ Archivo duplicado en destino: {archivo_nuevo}")
                else:
                    # MOVER/RENOMBRAR archivo
                    logger.info(f"🚀 Ejecutando shutil.move()")
                    logger.info(f"   Origen: {archivo_original}")
                    logger.info(f"   Destino: {archivo_nuevo}")
                    
                    shutil.move(archivo_original, archivo_nuevo)
                    
                    logger.info(f"✅✅✅ OPERACIÓN EXITOSA ✅✅✅")
                    logger.info(f"  📄 Nombre anterior: {nombre_actual}")
                    logger.info(f"  📄 Nombre nuevo: {nuevo_nombre}")
                    logger.info(f"  📂 Carpeta: {carpeta_destino}")
                    logger.info(f"  🎯 Tipo operación: {carpeta_destino_tipo}")
                    
                    # 🔥 SINCRONIZAR CON DIAN VS ERP (Dec 29, 2025)
                    if carpeta_destino_tipo == 'causadas':
                        try:
                            from modules.dian_vs_erp.sync_service import sincronizar_factura_causada
                            
                            # Extraer NIT, PREFIJO, FOLIO del nombre del archivo
                            # Formato esperado: NIT-PREFIJO-FOLIO.pdf o similar
                            nombre_sin_ext = os.path.splitext(nuevo_nombre)[0]
                            partes = nombre_sin_ext.split('-')
                            
                            if len(partes) >= 3:
                                nit_extraido = partes[0].strip()
                                prefijo_extraido = partes[1].strip()
                                folio_extraido = partes[2].strip()
                                usuario = session.get('usuario', 'sistema')
                                
                                logger.info(f"🔄 Sincronizando factura causada: NIT={nit_extraido}, PREFIJO={prefijo_extraido}, FOLIO={folio_extraido}")
                                
                                exito, mensaje, accion = sincronizar_factura_causada(
                                    nit=nit_extraido,
                                    prefijo=prefijo_extraido,
                                    folio=folio_extraido,
                                    usuario=usuario
                                )
                                
                                if exito:
                                    logger.info(f"✅ SYNC CAUSADA OK: {mensaje}")
                                else:
                                    logger.warning(f"⚠️ SYNC CAUSADA FALLIDO: {mensaje}")
                            else:
                                logger.warning(f"⚠️ No se pudo extraer NIT-PREFIJO-FOLIO del nombre: {nuevo_nombre}")
                        
                        except Exception as e:
                            logger.error(f"❌ Error al sincronizar factura causada: {e}", exc_info=True)
                        
                        flash(f"✅ Archivo '{nuevo_nombre}' movido exitosamente a carpeta CAUSADAS")
                    else:
                        flash(f"✅ Archivo renombrado exitosamente a '{nuevo_nombre}'")
                
            except Exception as e:
                flash(f"❌ Error al procesar el archivo: {str(e)}")
                logger.error(f"Error en renombrado/movimiento: {e}", exc_info=True)
            
            # Redirigir con filtros
            return redirect(url_for('causaciones.index',
                sede=sede,
                carpeta=request.args.get("carpeta", ""),
                filtro=request.args.get("filtro", ""),
                pagina=request.args.get("pagina", 1),
                por_pagina=request.args.get("por_pagina", 50)
            ))
        
        # Mostrar formulario (GET)
        logger.info(f"Renderizando template renombrar.html")
        logger.info(f"  Nombre actual: {nombre_actual}")
        logger.info(f"  Nombre limpio sugerido: {nombre_limpio_sugerido}")
        
        return render_template('renombrar.html',
            archivo=archivo,
            nombre_actual=nombre_actual,
            nombre_sugerido=nombre_limpio_sugerido,
            sede=sede,
            carpeta=request.args.get("carpeta", ""),
            filtro=request.args.get("filtro", ""),
            pagina=request.args.get("pagina", 1),
            por_pagina=request.args.get("por_pagina", 50)
        )
    
    except Exception as e:
        logger.error(f"ERROR EN RENOMBRAR: {str(e)}", exc_info=True)
        flash(f"❌ Error en el sistema de renombrado: {str(e)}")
        return redirect(url_for('causaciones.index'))
