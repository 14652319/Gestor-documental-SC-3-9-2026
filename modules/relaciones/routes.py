# =============================================
# 🚀 routes.py — Flask Blueprint para Relaciones
# =============================================
from flask import Blueprint, render_template, request, jsonify, session, send_file, flash, redirect, url_for
from werkzeug.exceptions import HTTPException
from flask_mail import Message  # 🆕 Para envío de correos con tokens
from datetime import datetime, date, timedelta  # 🆕 timedelta agregado
from sqlalchemy import func, text, case
from extensions import db  # Importar desde extensions, no desde app
from .models import RelacionFactura, Consecutivo
import pandas as pd
from fpdf import FPDF
import io
import os
import logging

# 🔐 IMPORTAR DECORADORES DE PERMISOS
from decoradores_permisos import requiere_permiso, requiere_permiso_html

# 🕐 IMPORTAR UTILIDADES DE FECHA (zona horaria Colombia)
from utils_fecha import obtener_fecha_naive_colombia, formatear_fecha_colombia

# ✅ NO importar Tercero aquí para evitar circular import
# En su lugar, se accederá dinámicamente cuando se necesite

# ✅ Usa el logger "security" compartido → escribe en logs/security.log (igual que app.py)
security_logger = logging.getLogger("security")

# Función helper para logging de seguridad
def log_security(mensaje):
    """Registra eventos de seguridad en logger compartido (logs/security.log)"""
    security_logger.info(mensaje)

# -------------------------------------------------
# � HELPER: FORMATEAR FECHAS DE FORMA SEGURA
# -------------------------------------------------
def formatear_fecha_segura(fecha, formato='%Y-%m-%d'):
    """
    Formatea una fecha de forma segura, manejando strings, datetime, date y None
    
    Args:
        fecha: Puede ser datetime, date, string ISO, o None
        formato: Formato de salida (por defecto: 'YYYY-MM-DD')
    
    Returns:
        str: Fecha formateada o string vacío si es None
    """
    if fecha is None:
        return ''
    
    # Si ya es string, intentar parsearlo
    if isinstance(fecha, str):
        try:
            from dateutil.parser import parse
            fecha = parse(fecha)
        except:
            # Si no se puede parsear, retornar el string original
            return fecha
    
    # Si tiene método strftime (datetime o date), usarlo
    if hasattr(fecha, 'strftime'):
        try:
            return fecha.strftime(formato)
        except:
            return str(fecha)
    
    # Fallback: convertir a string
    return str(fecha)

# -------------------------------------------------
# �📦 BLUEPRINT
# -------------------------------------------------
relaciones_bp = Blueprint('relaciones', __name__)

# --- Error Handlers Globales para JSON ---
@relaciones_bp.app_errorhandler(HTTPException)
def handle_http_exception(e):
    response = e.get_response()
    # Reemplaza el cuerpo por JSON
    response.data = jsonify({
        "success": False,
        "error": e.description,
        "type": e.name,
        "code": e.code
    }).data
    response.content_type = "application/json"
    return response

@relaciones_bp.app_errorhandler(Exception)
def handle_generic_exception(e):
    # Error inesperado (500)
    import traceback
    return jsonify({
        "success": False,
        "error": str(e),
        "type": "InternalServerError",
        "trace": traceback.format_exc()
    }), 500

# -------------------------------------------------
# 🔐 HELPER: VALIDAR SESIÓN
# -------------------------------------------------
def validar_sesion():
    """Valida que el usuario tenga sesión activa"""
    if 'usuario_id' not in session or 'usuario' not in session:
        return False, {"error": "Sesión no válida", "redirect": "/login"}, 401
    return True, None, None

# -------------------------------------------------
# 🔧 HELPER: GENERAR CONSECUTIVO
# -------------------------------------------------
def generar_consecutivo():
    """
    Genera el siguiente consecutivo para relaciones de facturas (REL-XXX)
    Usa la tabla consecutivos de la base de datos
    ⚠️ PROTEGIDO CONTRA DUPLICADOS con transacción atómica
    """
    max_intentos = 5  # Intentos máximos en caso de colisión
    
    for intento in range(max_intentos):
        try:
            # 🔒 Obtener consecutivo con bloqueo de fila (FOR UPDATE)
            consecutivo_obj = db.session.query(Consecutivo).filter_by(
                tipo='RELACION',
                prefijo='REL'
            ).with_for_update().first()

            if not consecutivo_obj:
                # Crear el consecutivo si no existe
                consecutivo_obj = Consecutivo(
                    tipo='RELACION',
                    tipo_documento='RELACION',
                    prefijo='REL',
                    ultimo_consecutivo=0
                )
                db.session.add(consecutivo_obj)
                db.session.flush()

            # Incrementar el consecutivo
            consecutivo_obj.ultimo_consecutivo += 1
            consecutivo_obj.fecha_actualizacion = obtener_fecha_naive_colombia()  # 🕐 Hora de Colombia

            # Generar número con formato REL-XXX
            numero = str(consecutivo_obj.ultimo_consecutivo).zfill(3)
            nuevo_consecutivo = f"{consecutivo_obj.prefijo}-{numero}"
            
            # ✅ Verificar que NO exista ya en relaciones_facturas (doble check)
            existe = db.session.query(RelacionFactura).filter_by(
                numero_relacion=nuevo_consecutivo
            ).first()
            
            if existe:
                # Si ya existe, reintentar (esto solo pasaría en casos extremos)
                log_security(f"CONSECUTIVO DUPLICADO DETECTADO | consecutivo={nuevo_consecutivo} | intento={intento + 1}")
                db.session.rollback()
                continue
            
            # Commit de la transacción
            db.session.commit()
            
            log_security(f"CONSECUTIVO GENERADO | consecutivo={nuevo_consecutivo} | ultimo_consecutivo={consecutivo_obj.ultimo_consecutivo}")
            return nuevo_consecutivo
            
        except Exception as e:
            db.session.rollback()
            log_security(f"ERROR GENERAR CONSECUTIVO | intento={intento + 1} | error={str(e)}")
            if intento == max_intentos - 1:
                raise  # Re-lanzar excepción si ya agotamos intentos
            continue
    
    # Si llegamos aquí, algo salió muy mal
    raise Exception(f"No se pudo generar consecutivo después de {max_intentos} intentos")

# -------------------------------------------------
# 📄 RUTA: MOSTRAR FORMULARIO (GET)
# -------------------------------------------------
@relaciones_bp.route('/')
@relaciones_bp.route('/generar_relacion', methods=['GET'])
@requiere_permiso_html('relaciones', 'acceder_modulo')
def mostrar_formulario():
    """Muestra el formulario para generar relación de facturas"""
    # ✅ VALIDACIÓN DE SESIÓN MANEJADA POR DECORADOR @requiere_permiso_html
    # No es necesario validar sesión aquí, el decorador ya lo hace
    
    # 🔒 LOG DE AUDITORÍA: Acceso al formulario
    log_security(f"ACCESO FORMULARIO RELACIONES | usuario={session.get('usuario')} | IP={request.remote_addr}")
    
    try:
        # Obtener parámetros de filtro CON FECHA POR DEFECTO HOY
        from datetime import date
        hoy = date.today().strftime('%Y-%m-%d')
        
        desde = request.args.get('desde', hoy)  # 🆕 FECHA POR DEFECTO HOY
        hasta = request.args.get('hasta', hoy)  # 🆕 FECHA POR DEFECTO HOY
        co = request.args.get('co', '')
        destino = request.args.get('destino', 'CONTABILIDAD')
        formato = request.args.get('formato', 'Excel')
        
        # 🆕 PAGINACIÓN - Parámetros
        pagina = int(request.args.get('pagina', 1))
        items_por_pagina = 500  # 500 facturas por página
        
        # Consultar centros operativos
        query_co = text("SELECT DISTINCT centro_operacion_id FROM facturas_recibidas ORDER BY centro_operacion_id")
        lista_co = [str(row[0]) for row in db.session.execute(query_co).fetchall()]
        
        # Si hay filtros, consultar facturas CON PAGINACIÓN
        facturas = []
        total_facturas = 0
        total_paginas = 0
        
        if desde and hasta:
            # 🆕 PASO 1: Contar total de facturas (para paginación)
            query_count = text("""
                SELECT COUNT(*)
                FROM facturas_recibidas fr
                WHERE fr.fecha_radicacion BETWEEN :desde AND :hasta
                  AND (:co = '' OR fr.centro_operacion_id::text = :co)
            """)
            total_facturas = db.session.execute(query_count, {"desde": desde, "hasta": hasta, "co": co}).scalar()
            total_paginas = (total_facturas + items_por_pagina - 1) // items_por_pagina  # Redondear hacia arriba
            
            # 🆕 PASO 2: Consultar facturas con LIMIT y OFFSET
            offset = (pagina - 1) * items_por_pagina
            
            query = text("""
                SELECT DISTINCT
                    fr.nit,
                    fr.razon_social,
                    fr.prefijo,
                    fr.folio,
                    co.codigo AS centro_operacion_codigo,
                    fr.empresa_id,
                    fr.valor_neto,
                    fr.fecha_radicacion,
                    fr.fecha_expedicion
                FROM facturas_recibidas fr
                LEFT JOIN centros_operacion co ON fr.centro_operacion_id = co.id
                WHERE fr.fecha_radicacion BETWEEN :desde AND :hasta
                  AND (:co = '' OR co.codigo = :co)
                ORDER BY co.codigo, fr.prefijo, fr.folio
                LIMIT :limit OFFSET :offset
            """)
            
            result = db.session.execute(query, {
                "desde": desde, 
                "hasta": hasta, 
                "co": co,
                "limit": items_por_pagina,
                "offset": offset
            })
            
            # Convertir resultados a diccionarios con nombres de columnas correctos
            facturas = []
            for row in result:
                nit = row[0]
                razon_social = row[1] or 'NO REGISTRADO'
                prefijo = row[2]
                folio = row[3]
                centro_operacion_codigo = row[4]  # ✅ AHORA ES CÓDIGO NO ID
                empresa_id = row[5]  # ✅ CAMPO EMPRESA AGREGADO
                valor = row[6]
                fecha_radicacion = row[7]
                fecha_expedicion = row[8]  # 🆕 NUEVA COLUMNA

                # Verificar si ya fue relacionada
                relacion_existente = RelacionFactura.query.filter_by(
                    nit=nit,
                    prefijo=prefijo,
                    folio=folio
                ).first()

                # Formatear fecha_factura como string ISO (YYYY-MM-DD) usando helper seguro
                fecha_factura_str = formatear_fecha_segura(fecha_radicacion, '%Y-%m-%d')
                
                # 🆕 Formatear fecha_expedicion usando helper seguro
                fecha_expedicion_str = formatear_fecha_segura(fecha_expedicion, '%Y-%m-%d')

                # Construir diccionario completo (sin duplicados)
                factura_dict = {
                    'nit': nit,
                    'razon_social': razon_social,
                    'prefijo': prefijo,
                    'folio': folio,
                    'centro_operacion_codigo': centro_operacion_codigo,  # ✅ CÓDIGO EN VEZ DE ID
                    'co': centro_operacion_codigo or 'N/A',  # ✅ USAR CÓDIGO DIRECTAMENTE
                    'empresa_id': empresa_id or 'N/A',  # ✅ CAMPO EMPRESA AGREGADO
                    'valor': valor or 0,
                    'fecha_factura': fecha_factura_str,
                    'fecha_expedicion': fecha_expedicion_str,  # 🆕 AGREGAR AL DICCIONARIO
                    'clave': f"{nit}-{prefijo}-{folio}",
                    'numero_relacion': relacion_existente.numero_relacion if relacion_existente else '',
                    'color': 'relacionada' if relacion_existente else '',  # 🆕 CLASE CSS CORRECTA
                    'tooltip': f'Ya relacionada en {relacion_existente.numero_relacion}' if relacion_existente else ''
                }
                # Formatear fecha_relacion si existe usando helper seguro
                factura_dict['fecha_relacion'] = ''
                if relacion_existente and relacion_existente.fecha_generacion:
                    factura_dict['fecha_relacion'] = formatear_fecha_segura(relacion_existente.fecha_generacion, '%Y-%m-%d')
                facturas.append(factura_dict)
        
        return render_template('generar_relacion_REFACTORED.html',
                             facturas=facturas,
                             desde=desde,
                             hasta=hasta,
                             co=co,
                             destino=destino,
                             formato=formato,
                             lista_co=lista_co,
                             pagina=pagina,  # 🆕 PAGINACIÓN
                             total_paginas=total_paginas,  # 🆕 PAGINACIÓN
                             total_facturas=total_facturas)  # 🆕 PAGINACIÓN
    
    except Exception as e:
        log_security(f"ERROR RELACIONES FORMULARIO | usuario={session.get('usuario')} | error={str(e)}")
        flash(f'❌ Error al cargar las facturas: {str(e)}', 'warning')
        return render_template('generar_relacion_REFACTORED.html',
                             facturas=[],
                             desde=desde,
                             hasta=hasta,
                             co='',
                             destino=destino,
                             formato=formato,
                             lista_co=[])

# -------------------------------------------------
# 📥 RUTA: GENERAR RELACIÓN (POST)
# -------------------------------------------------
@relaciones_bp.route('/generar_relacion', methods=['POST'])
@requiere_permiso('relaciones', 'generar_relacion')
def generar_relacion():
    """Genera una relación de facturas en formato Excel o PDF"""
    # Validar sesión
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    # 🔒 LOG DE AUDITORÍA: Intento de generación
    log_security(f"INTENTO GENERAR RELACION | usuario={session.get('usuario')} | IP={request.remote_addr}")
    
    try:
        # Obtener datos del formulario
        seleccionadas = request.form.getlist('factura')  # Lista de claves: "nit-prefijo-folio"
        destino = request.form.get('destino', 'CONTABILIDAD')
        formato = request.form.get('formato', 'Excel')
        usuario = session.get('usuario', 'anonimo')
        
        if not seleccionadas:
            flash("❌ Debe seleccionar al menos una factura.", "warning")
            return redirect(url_for('relaciones.mostrar_formulario'))
        
        # Generar consecutivo
        consecutivo = generar_consecutivo()
        fecha_hoy = date.today()
        
        # Consultar facturas seleccionadas
        facturas_guardar = []
        ya_relacionadas = []
        
        for clave in seleccionadas:
            # Parsear clave: "nit-prefijo-folio"
            partes = clave.split('-')
            if len(partes) < 3:
                continue
            
            nit = partes[0]
            prefijo = partes[1]
            folio = '-'.join(partes[2:])  # Por si el folio tiene guiones
            
            # Verificar si ya fue relacionada
            existente = RelacionFactura.query.filter_by(
                nit=nit,
                prefijo=prefijo,
                folio=folio
            ).first()
            
            if existente:
                ya_relacionadas.append(
                    f"Factura {prefijo}-{folio} ya fue relacionada "
                    f"el {existente.fecha_generacion} en la relación {existente.numero_relacion}"
                )
                continue
            
            # Consultar datos completos de la factura
            query = text("""
                SELECT 
                    fr.nit,
                    fr.razon_social,
                    fr.prefijo,
                    fr.folio,
                    fr.centro_operacion_id as co,
                    fr.valor_neto as valor,
                    fr.fecha_radicacion,
                    fr.fecha_expedicion
                FROM facturas_recibidas fr
                WHERE fr.nit = :nit
                  AND fr.prefijo = :prefijo
                  AND fr.folio = :folio
                LIMIT 1
            """)
            
            factura_data = db.session.execute(query, {
                "nit": nit,
                "prefijo": prefijo,
                "folio": folio
            }).fetchone()
            
            if not factura_data:
                continue
            
            # Crear registro de relación
            relacion = RelacionFactura(
                numero_relacion=consecutivo,
                fecha_generacion=fecha_hoy,
                para=destino,
                usuario=usuario,
                nit=factura_data[0],
                razon_social=factura_data[1] or 'NO REGISTRADO',
                prefijo=factura_data[2],
                folio=factura_data[3],
                co=str(factura_data[4]).zfill(3) if factura_data[4] else '000',
                valor_total=factura_data[5],
                fecha_factura=factura_data[6],  # fecha_radicacion
                fecha_expedicion=factura_data[7]  # fecha_expedicion
            )
            
            db.session.add(relacion)
            facturas_guardar.append(relacion.to_dict())
        
        # Guardar en base de datos
        db.session.commit()
        
        # Mostrar advertencias si hay facturas ya relacionadas
        if ya_relacionadas:
            flash(" ".join(ya_relacionadas), 'warning')
        
        if not facturas_guardar:
            flash("❌ No se pudieron agregar facturas a la relación.", "warning")
            return redirect(url_for('relaciones.mostrar_formulario'))
        
        # Generar archivo según formato
        nombre_archivo = f"Relacion_Facturas_{consecutivo}.{'pdf' if formato == 'pdf' else 'xlsx'}"
        
        # ----- FORMATO PDF -----
        if formato == 'pdf':
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, f"RELACIÓN DE FACTURAS {consecutivo}", ln=True, align="C")
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 10, f"DESTINO: {destino} — FECHA: {fecha_hoy.isoformat()}", ln=True)
            pdf.ln(5)
            
            for f in facturas_guardar:
                texto = f"{f['nit']} — {f['razon_social']} — {f['co']} — {f['prefijo']}-{f['folio']} — ${f['valor_total']:,.0f}"
                pdf.multi_cell(0, 8, texto)
            
            # Guardar en memoria
            pdf_output = io.BytesIO()
            pdf_output.write(pdf.output(dest='S').encode('latin1'))
            pdf_output.seek(0)
            
            log_security(f"RELACION GENERADA PDF | usuario={usuario} | consecutivo={consecutivo} | facturas={len(facturas_guardar)}")
            
            flash(f"✅ Relación generada correctamente: {nombre_archivo}", "success")
            return send_file(pdf_output, as_attachment=True, download_name=nombre_archivo, mimetype='application/pdf')
        
        # ----- FORMATO DIGITAL (SIN IMPRESIÓN) -----
        elif formato == 'digital':
            # No generar archivo, solo registrar en BD y redirigir a recepción digital
            log_security(f"RELACION GENERADA DIGITAL | usuario={usuario} | consecutivo={consecutivo} | facturas={len(facturas_guardar)}")
            
            flash(f"✅ Relación digital generada: {consecutivo} ({len(facturas_guardar)} facturas)", "success")
            flash(f"📱 Acceda al módulo 'Recepción Digital' para validar las facturas sin impresión", "info")
            
            # Redirigir a recepción digital con el número de relación
            return redirect(url_for('relaciones.recepcion_digital') + f'?numero_relacion={consecutivo}')
        
        # ----- FORMATO EXCEL -----
        else:
            # Preparar datos para Excel
            df = pd.DataFrame(facturas_guardar)
            
            # Renombrar columnas
            df.rename(columns={
                "nit": "NIT",
                "razon_social": "Razón Social",
                "prefijo": "Prefijo",
                "folio": "Folio",
                "valor_total": "Valor",
                "co": "Centro Op.",
                "fecha_factura": "Fecha Factura"
            }, inplace=True)
            
            # Seleccionar columnas para exportar
            columnas_exportar = ["NIT", "Razón Social", "Prefijo", "Folio", "Valor", "Centro Op.", "Fecha Factura"]
            df_export = df[columnas_exportar]
            
            # Guardar en memoria
            excel_output = io.BytesIO()
            df_export.to_excel(excel_output, index=False, engine='openpyxl')
            excel_output.seek(0)
            
            log_security(f"RELACION GENERADA EXCEL | usuario={usuario} | consecutivo={consecutivo} | facturas={len(facturas_guardar)}")
            
            flash(f"✅ Relación generada correctamente: {nombre_archivo}", "success")
            return send_file(excel_output, as_attachment=True, download_name=nombre_archivo, 
                           mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR GENERAR RELACION | usuario={session.get('usuario')} | error={str(e)}")
        flash(f'❌ Error al generar la relación: {str(e)}', 'warning')
        return redirect(url_for('relaciones.mostrar_formulario'))


# -------------------------------------------------
# 🔄 REIMPRIMIR RELACIÓN EXISTENTE
@relaciones_bp.route('/reimprimir_relacion', methods=['GET', 'POST'])
@requiere_permiso_html('relaciones', 'reimprimir_relacion')
def reimprimir_relacion():
    """
    Permite seleccionar y reimprimir una relación ya generada
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return redirect('/')
    
    # 🔒 LOG DE AUDITORÍA: Acceso a reimprimir
    log_security(f"ACCESO REIMPRIMIR RELACION | usuario={session.get('usuario')} | IP={request.remote_addr} | metodo={request.method}")
    
    if request.method == 'POST':
        # Reimprimir relación seleccionada
        numero_relacion = request.form.get('numero_relacion')
        formato = request.form.get('formato', 'Excel')
        
        if not numero_relacion:
            flash('❌ Debe seleccionar un número de relación', 'warning')
            return redirect(url_for('relaciones.reimprimir_relacion'))
        
        try:
            # Consultar la relación
            query_relacion = text("""
                SELECT numero_relacion, fecha_generacion, para, usuario
                FROM relaciones_facturas
                WHERE numero_relacion = :numero_relacion
                LIMIT 1
            """)
            relacion = db.session.execute(query_relacion, {"numero_relacion": numero_relacion}).fetchone()
            
            if not relacion:
                flash(f'❌ No se encontró la relación {numero_relacion}', 'warning')
                return redirect(url_for('relaciones.reimprimir_relacion'))
            
            # Consultar facturas de esa relación
            # ✅ CORREGIDO: Usar relaciones_facturas (la tabla que tiene los datos originales)
            query_facturas = text("""
                SELECT 
                    nit,
                    razon_social,
                    prefijo,
                    folio,
                    valor_total,
                    co,
                    fecha_factura
                FROM relaciones_facturas
                WHERE numero_relacion = :numero_relacion
                ORDER BY co, prefijo, folio
            """)
            facturas_result = db.session.execute(query_facturas, {"numero_relacion": numero_relacion})
            
            facturas = []
            for f in facturas_result:
                razon_social = f[1]
                if not razon_social:
                    query_tercero = text("""
                        SELECT razon_social FROM terceros WHERE nit = :nit LIMIT 1
                    """)
                    tercero = db.session.execute(query_tercero, {"nit": f[0]}).fetchone()
                    razon_social = tercero[0] if tercero and tercero[0] else 'NO REGISTRADO'
                facturas.append({
                    "nit": f[0],
                    "razon_social": razon_social,
                    "prefijo": f[2],
                    "folio": f[3],
                    "valor_total": f[4],
                    "co": f[5],
                    "fecha_factura": formatear_fecha_segura(f[6], '%Y-%m-%d') if f[6] else ''
                })
            
            if not facturas:
                flash(f'❌ No se encontraron facturas para la relación {numero_relacion}', 'warning')
                return redirect(url_for('relaciones.reimprimir_relacion'))
            
            # Generar el archivo según formato
            if formato == 'digital':
                # 🆕 FORMATO DIGITAL: Redirigir a recepción digital
                log_security(f"RELACION REIMPRESA DIGITAL | usuario={session.get('usuario')} | relacion={numero_relacion} | facturas={len(facturas)}")
                flash(f"📱 Acceda a la recepción digital de la relación {numero_relacion}", "success")
                return redirect(url_for('relaciones.recepcion_digital', numero_relacion=numero_relacion))
            
            elif formato == 'Excel':
                df = pd.DataFrame(facturas)
                df.rename(columns={
                    "nit": "NIT",
                    "razon_social": "Razón Social",
                    "prefijo": "Prefijo",
                    "folio": "Folio",
                    "valor_total": "Valor",
                    "co": "Centro Op.",
                    "fecha_factura": "Fecha Factura"
                }, inplace=True)
                
                columnas_exportar = ["NIT", "Razón Social", "Prefijo", "Folio", "Valor", "Centro Op.", "Fecha Factura"]
                df_export = df[columnas_exportar]
                
                excel_output = io.BytesIO()
                df_export.to_excel(excel_output, index=False, engine='openpyxl')
                excel_output.seek(0)
                
                nombre_archivo = f"{numero_relacion}_{relacion[2]}_{formatear_fecha_segura(relacion[1], '%d%m%Y')}_REIMPRESION.xlsx"
                
                log_security(f"RELACION REIMPRESA EXCEL | usuario={session.get('usuario')} | relacion={numero_relacion} | facturas={len(facturas)}")
                
                flash(f"✅ Relación reimpresa correctamente: {numero_relacion}", "success")
                return send_file(excel_output, as_attachment=True, download_name=nombre_archivo,
                               mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            
            else:  # PDF
                # Implementar PDF similar a generación original
                flash('⚠️ Formato PDF en desarrollo', 'warning')
                return redirect(url_for('relaciones.reimprimir_relacion'))
        
        except Exception as e:
            log_security(f"ERROR REIMPRIMIR RELACION | usuario={session.get('usuario')} | error={str(e)}")
            flash(f'❌ Error al reimprimir la relación: {str(e)}', 'warning')
            return redirect(url_for('relaciones.reimprimir_relacion'))
    
    # GET: Mostrar formulario con lista de relaciones
    try:
        # Consultar todas las relaciones existentes
        # ✅ CORREGIDO: Usar solo relaciones_facturas (la tabla ya tiene los datos de las facturas)
        query_relaciones = text("""
            SELECT 
                numero_relacion,
                fecha_generacion,
                para,
                usuario,
                COUNT(*) as total_facturas,
                SUM(valor_total) as valor_total
            FROM relaciones_facturas
            GROUP BY numero_relacion, fecha_generacion, para, usuario
            ORDER BY numero_relacion DESC
        """)
        relaciones_result = db.session.execute(query_relaciones)
        
        relaciones = []
        for r in relaciones_result:
            relaciones.append({
                "numero_relacion": r[0],
                "fecha_generacion": formatear_fecha_segura(r[1], '%Y-%m-%d') if r[1] else '',
                "para": r[2],
                "usuario": r[3],
                "total_facturas": r[4] or 0,
                "valor_total": r[5] or 0
            })
        
        log_security(f"REIMPRIMIR FORMULARIO | usuario={session.get('usuario')} | relaciones_disponibles={len(relaciones)}")
        
        return render_template('reimprimir_relacion.html',
                             relaciones=relaciones)
    
    except Exception as e:
        log_security(f"ERROR CARGAR RELACIONES | usuario={session.get('usuario')} | error={str(e)}")
        flash(f'❌ Error al cargar las relaciones: {str(e)}', 'warning')
        return redirect(url_for('relaciones.mostrar_formulario'))


# =============================================================================
# 📱 RUTAS: RECEPCIÓN DIGITAL DE RELACIONES
# =============================================================================

# -------------------------------------------------
# 🔍 RUTA: BUSCAR RELACIÓN PARA RECEPCIÓN DIGITAL
@relaciones_bp.route('/recepcion_digital', methods=['GET', 'POST'])
@requiere_permiso_html('relaciones', 'recepcion_digital')
def recepcion_digital():
    """
    Formulario para buscar y recibir digitalmente una relación
    Permite validar facturas sin impresión física una relación
    Permite validar facturas sin impresión física
    """
    # Validar sesión
    if 'usuario_id' not in session or 'usuario' not in session:
        flash('⚠️ Sesión expirada. Por favor, inicia sesión nuevamente.', 'warning')
        return redirect(url_for('index'))
    
    # Log de acceso
    log_security(f"ACCESO RECEPCION DIGITAL | usuario={session.get('usuario')} | IP={request.remote_addr}")
    
    # Obtener número de relación de query string o form
    numero_relacion = request.args.get('numero_relacion') or request.form.get('numero_relacion', '').strip().upper()
    
    if numero_relacion:
        # Buscar relación por número
        try:
            # ✅ DEBUG: Log del inicio de búsqueda
            log_security(f"DEBUG INICIO BUSQUEDA | usuario={session.get('usuario')} | relacion={numero_relacion}")
            
            # ✅ Consultar facturas de la relación
            # Acceder a tabla terceros usando Table reflection para evitar circular import
            from sqlalchemy import Table, MetaData
            
            log_security(f"DEBUG IMPORT OK | Importando Table y MetaData")
            
            metadata = MetaData()
            terceros_table = Table('terceros', metadata, autoload_with=db.engine)
            
            log_security(f"DEBUG REFLECTION OK | Tabla terceros reflejada")
            
            # Consulta con LEFT JOIN usando la tabla reflejada
            facturas_query = db.session.query(
                RelacionFactura,
                terceros_table.c.razon_social.label('razon_social_tercero')
            ).outerjoin(
                terceros_table,
                RelacionFactura.nit == terceros_table.c.nit
            ).filter(
                RelacionFactura.numero_relacion == numero_relacion
            ).order_by(
                terceros_table.c.razon_social.asc().nullslast(),
                RelacionFactura.id.asc()
            ).all()
            
            log_security(f"DEBUG QUERY OK | Resultados: {len(facturas_query)} filas")
            
            # Actualizar razon_social en las facturas obtenidas
            facturas = []
            for factura, razon_social_tercero in facturas_query:
                # Si la razon_social está vacía en relaciones, usar la de terceros
                if not factura.razon_social and razon_social_tercero:
                    factura.razon_social = razon_social_tercero
                # ✅ SIEMPRE buscar en facturas_recibidas para obtener código y empresa
                query_extra = db.session.execute(
                    text("""
                        SELECT co.codigo, fr.empresa_id, fr.valor_neto, fr.fecha_radicacion 
                        FROM facturas_recibidas fr
                        LEFT JOIN centros_operacion co ON fr.centro_operacion_id = co.id
                        WHERE fr.nit = :nit AND fr.prefijo = :prefijo AND fr.folio = :folio
                        LIMIT 1
                    """),
                    {"nit": factura.nit, "prefijo": factura.prefijo, "folio": factura.folio}
                ).fetchone()
                if query_extra:
                    co_codigo, empresa_id, valor_db, fecha_db = query_extra
                    # ✅ SOBRESCRIBIR SIEMPRE con el código (no el ID)
                    if co_codigo:
                        factura.co = co_codigo
                    # ✅ AGREGAR EMPRESA
                    factura.empresa_id = empresa_id or 'N/A'
                    # Solo actualizar valor y fecha si están vacíos
                    if not factura.valor_total and valor_db:
                        factura.valor_total = valor_db
                    if not factura.fecha_factura and fecha_db:
                        factura.fecha_factura = fecha_db
                facturas.append(factura)
            
            if not facturas:
                flash(f'❌ No se encontró la relación {numero_relacion}', 'warning')
                log_security(f"RELACION NO ENCONTRADA | usuario={session.get('usuario')} | relacion={numero_relacion}")
                return redirect(url_for('relaciones.recepcion_digital'))
            
            # Verificar si ya fue recibida
            from .models import RecepcionDigital, FacturaRecibidaDigital
            recepcion_existente = RecepcionDigital.query.filter_by(
                numero_relacion=numero_relacion,
                usuario_receptor=session.get('usuario')
            ).first()
            
            # Cargar facturas recibidas digitalmente
            # Tomar el estado más reciente por número de relación (más robusto)
            facturas_firmadas = []
            facturas_firmadas_query = FacturaRecibidaDigital.query.filter_by(
                numero_relacion=numero_relacion,
                recibida=True
            ).all()
            facturas_firmadas = [f.to_dict() for f in facturas_firmadas_query]
            
            if recepcion_existente and recepcion_existente.completa:
                fecha_rec = recepcion_existente.fecha_recepcion
                import datetime
                fecha_rec_str = "(sin fecha)"
                if fecha_rec:
                    # Usar helper seguro para formatear fecha
                    fecha_rec_str = formatear_fecha_segura(fecha_rec, "%Y-%m-%d %H:%M")
                flash(f'⚠️ La relación {numero_relacion} ya fue recibida completamente por usted el {fecha_rec_str}', 'warning')
            
            log_security(f"RELACION ENCONTRADA | usuario={session.get('usuario')} | relacion={numero_relacion} | facturas={len(facturas)}")
            
            # ✅ Convertir a diccionarios (asegurando que incluyan fecha_factura y razon_social)
            facturas_dict = [f.to_dict() for f in facturas]
            
            # ✅ Marcar facturas que ya están firmadas
            if facturas_firmadas:
                facturas_firmadas_keys = {f"{f['prefijo']}-{f['folio']}" for f in facturas_firmadas}
                for factura in facturas_dict:
                    clave = f"{factura['prefijo']}-{factura['folio']}"
                    factura['firmada'] = clave in facturas_firmadas_keys
            else:
                # Ninguna firmada aún
                for factura in facturas_dict:
                    factura['firmada'] = False
            
            # Relación completa si facturas firmadas == total
            relacion_completa = len(facturas_firmadas) >= len(facturas)

            return render_template('recepcion_digital_FINAL.html',
                                 numero_relacion=numero_relacion,
                                 facturas=facturas_dict,
                                 total_facturas=len(facturas),
                                 facturas_firmadas=facturas_firmadas,
                                 cantidad_firmadas=len(facturas_firmadas),
                                 recepcion_existente=recepcion_existente,
                                 relacion_completa=relacion_completa)
        
        except Exception as e:
            log_security(f"ERROR BUSCAR RELACION | usuario={session.get('usuario')} | relacion={numero_relacion} | error={str(e)}")
            flash(f'❌ Error al buscar la relación: {str(e)}', 'danger')
            return redirect(url_for('relaciones.recepcion_digital'))
    
    # GET: Mostrar formulario de búsqueda
    return render_template('recepcion_digital_FINAL.html')


# -------------------------------------------------
@relaciones_bp.route('/confirmar_recepcion', methods=['POST'])
@requiere_permiso('relaciones', 'confirmar_recepcion')
def confirmar_recepcion():
    """
    Confirma la recepción digital de facturas checkeadas
    Genera firma digital y registra en auditoría
    Confirma la recepción digital de facturas checkeadas
    Genera firma digital y registra en auditoría
    """
    # Validar sesión
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        numero_relacion = data.get('numero_relacion')
        facturas_recibidas_raw = data.get('facturas_recibidas', [])  # Puede ser [ids] o [{id, observaciones}]
        
        # Normalizar facturas recibidas a conjunto de IDs y mapa de observaciones
        facturas_ids = set()
        observaciones_map = {}
        for item in facturas_recibidas_raw:
            try:
                if isinstance(item, dict):
                    fid = int(item.get('id')) if item.get('id') is not None else None
                    if fid is not None:
                        facturas_ids.add(fid)
                        if item.get('observaciones'):
                            observaciones_map[fid] = item.get('observaciones')
                else:
                    fid = int(item)
                    facturas_ids.add(fid)
            except Exception:
                # Ignorar entradas inválidas
                continue
        
        if not numero_relacion or not facturas_ids:
            return jsonify({"error": "Datos incompletos"}), 400
        
        # Consultar facturas de la relación
        facturas = RelacionFactura.query.filter_by(numero_relacion=numero_relacion).all()
        
        if not facturas:
            return jsonify({"error": f"No se encontró la relación {numero_relacion}"}), 404
        
        # Crear o actualizar recepción digital
        from .models import RecepcionDigital, FacturaRecibidaDigital
        import hashlib
        
        # Buscar recepción existente
        recepcion = RecepcionDigital.query.filter_by(
            numero_relacion=numero_relacion,
            usuario_receptor=session.get('usuario')
        ).first()
        
        if not recepcion:
            # Crear nueva recepción
            recepcion = RecepcionDigital(
                numero_relacion=numero_relacion,
                usuario_receptor=session.get('usuario'),
                nombre_receptor=session.get('nombre_completo', session.get('usuario')),
                ip_recepcion=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                facturas_totales=len(facturas)
            )
            db.session.add(recepcion)
            db.session.flush()  # Obtener ID
        
        # Actualizar cantidad de facturas recibidas
        recepcion.facturas_recibidas = len(facturas_ids)
        recepcion.completa = (len(facturas_ids) == len(facturas))
        recepcion.fecha_recepcion = obtener_fecha_naive_colombia()  # 🕐 Hora de Colombia
        
        # Generar firma digital (hash SHA256)
        datos_firma = f"{numero_relacion}|{session.get('usuario')}|{recepcion.fecha_recepcion.isoformat()}|{len(facturas_ids)}"
        firma = hashlib.sha256(datos_firma.encode()).hexdigest()
        recepcion.firma_digital = firma
        
        # Registrar facturas recibidas individualmente
        for factura in facturas:
            factura_dict = factura.to_dict()
            factura_id = factura_dict['id']
            
            # Verificar si ya existe el registro
            factura_recibida = FacturaRecibidaDigital.query.filter_by(
                recepcion_id=recepcion.id,
                prefijo=factura.prefijo,
                folio=factura.folio
            ).first()
            
            if not factura_recibida:
                # Crear nuevo registro
                factura_recibida = FacturaRecibidaDigital(
                    recepcion_id=recepcion.id,
                    numero_relacion=numero_relacion,
                    nit=factura.nit,
                    razon_social=factura.razon_social,
                    prefijo=factura.prefijo,
                    folio=factura.folio,
                    co=factura.co,
                    valor_total=factura.valor_total,
                    fecha_factura=factura.fecha_factura
                )
                db.session.add(factura_recibida)
            
            # Actualizar estado de recibida si está en la lista
            if factura_id in facturas_ids:
                factura_recibida.recibida = True
                factura_recibida.fecha_check = obtener_fecha_naive_colombia()  # 🕐 Hora de Colombia
                factura_recibida.usuario_check = session.get('usuario')
                # Guardar observaciones si llegaron desde el frontend
                if factura_id in observaciones_map:
                    factura_recibida.observaciones = observaciones_map[factura_id]
        
        # Commit de la transacción
        db.session.commit()
        
        # Log de auditoría
        log_security(
            f"RECEPCION DIGITAL CONFIRMADA | "
            f"usuario={session.get('usuario')} | "
            f"relacion={numero_relacion} | "
            f"facturas_recibidas={len(facturas_ids)}/{len(facturas)} | "
            f"completa={recepcion.completa} | "
            f"firma={firma[:16]}... | "
            f"IP={request.remote_addr}"
        )
        
        return jsonify({
            "success": True,
            "message": f"Recepción confirmada: {len(facturas_ids)}/{len(facturas)} facturas",
            "recepcion_id": recepcion.id,
            "firma_digital": firma,
            "completa": recepcion.completa
        }), 200
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CONFIRMAR RECEPCION | usuario={session.get('usuario')} | error={str(e)}")
        return jsonify({"error": f"Error al confirmar recepción: {str(e)}"}), 500


# -------------------------------------------------
@relaciones_bp.route('/solicitar_token_firma', methods=['POST'])
@requiere_permiso('relaciones', 'generar_token_firma')
def solicitar_token_firma():
    """
    Genera un token de 6 dígitos y lo envía por correo electrónico
    al usuario para validar la firma digital de la recepción
    Genera un token de 6 dígitos y lo envía por correo electrónico
    al usuario para validar la firma digital de la recepción
    """
    # Validar sesión
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        from .models import TokenFirmaDigital, RelacionFactura, FacturaRecibidaDigital
        import secrets
        
        data = request.get_json()
        numero_relacion = data.get('numero_relacion')
        facturas_cantidad = data.get('facturas_cantidad', 0)
        
        if not numero_relacion:
            return jsonify({"error": "Número de relación requerido"}), 400
        
        # Obtener datos del usuario de la sesión
        usuario = session.get('usuario')

        # 🚫 Bloquear si la relación ya está completamente recibida
        try:
            total_rel = RelacionFactura.query.filter_by(numero_relacion=numero_relacion).count()
            firmadas_rel = FacturaRecibidaDigital.query.filter_by(numero_relacion=numero_relacion, recibida=True).count()
            if total_rel > 0 and firmadas_rel >= total_rel:
                return jsonify({
                    "error": f"La relación {numero_relacion} ya fue recibida completamente"
                }), 400
        except Exception:
            pass
        
        # Buscar correo del usuario en la base de datos
        # ✅ Evitar import circular - usar text query directo
        from sqlalchemy import text
        result = db.session.execute(
            text("SELECT correo FROM usuarios WHERE usuario = :usuario"),
            {"usuario": usuario}
        ).fetchone()
        
        if not result or not result[0]:
            return jsonify({
                "error": "No se encontró correo electrónico asociado al usuario"
            }), 404
        
        correo_usuario = result[0]
        nombre_usuario = usuario  # Usar el nombre de usuario directamente
        
        # Generar token de 6 dígitos
        token = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Calcular fecha de expiración (10 minutos) - usar hora de Colombia
        fecha_expiracion = obtener_fecha_naive_colombia() + timedelta(minutes=10)
        
        # Crear registro de token
        token_firma = TokenFirmaDigital(
            token=token,
            usuario=usuario,
            numero_relacion=numero_relacion,
            correo_destino=correo_usuario,
            fecha_creacion=obtener_fecha_naive_colombia(),  # 🕐 Hora de Colombia
            fecha_expiracion=fecha_expiracion,
            ip_creacion=request.remote_addr
        )
        
        db.session.add(token_firma)
        db.session.commit()
        
        # Intentar enviar token por correo (opcional si no está configurado)
        correo_enviado = False
        error_correo = None
        
        from flask import current_app
        if current_app.config.get('MAIL_USERNAME') and current_app.config.get('MAIL_PASSWORD'):
            try:
                from flask_mail import Message
        
                # Crear mensaje HTML
                html_body = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; background: #f5f7fa; padding: 20px; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                        .header {{ text-align: center; background: linear-gradient(135deg, #166534, #14532d); color: white; padding: 25px; border-radius: 8px; margin-bottom: 30px; }}
                        .token-box {{ background: #f0fdf4; border: 2px solid #166534; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0; }}
                        .token {{ font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #166534; font-family: monospace; }}
                        .info {{ background: #eff6ff; padding: 15px; border-radius: 6px; margin: 20px 0; }}
                        .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e8ed; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>🔐 Token de Firma Digital</h1>
                            <p>Recepción Digital de Facturas</p>
                        </div>
                        
                        <p>Hola <strong>{nombre_usuario}</strong>,</p>
                        
                        <p>Has solicitado firmar digitalmente la recepción de la relación <strong>{numero_relacion}</strong> con <strong>{facturas_cantidad} facturas</strong>.</p>
                        
                        <div class="token-box">
                            <p style="margin: 0; font-size: 14px; color: #666;">Tu token de firma es:</p>
                            <div class="token">{token}</div>
                        </div>
                        
                        <div class="info">
                            <p style="margin: 0;"><strong>⏱ Validez:</strong> 10 minutos</p>
                            <p style="margin: 0;"><strong>🔢 Intentos permitidos:</strong> 3</p>
                        </div>
                        
                        <p><strong>Instrucciones:</strong></p>
                        <ol>
                            <li>Copia el token de 6 dígitos mostrado arriba</li>
                            <li>Pégalo en el formulario de recepción digital</li>
                            <li>Haz clic en "Validar Token"</li>
                            <li>Si el token es correcto, se generará la firma digital</li>
                        </ol>
                        
                        <p style="color: #dc2626;"><strong>⚠️ IMPORTANTE:</strong> Si no solicitaste este token, ignora este mensaje.</p>
                        
                        <div class="footer">
                            <p>Supertiendas Cañaveral - Sistema de Gestión Documental</p>
                            <p>Este es un correo automático, por favor no responder</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Texto plano alternativo
                text_body = f"""
                🔐 TOKEN DE FIRMA DIGITAL
                
                Hola {nombre_usuario},
                
                Has solicitado firmar digitalmente la recepción de la relación {numero_relacion} con {facturas_cantidad} facturas.
                
                Tu token de firma es: {token}
                
                Validez: 10 minutos
                Intentos permitidos: 3
                
                Instrucciones:
                1. Copia el token de 6 dígitos
                2. Pégalo en el formulario de recepción digital
                3. Haz clic en "Validar Token"
                
                Supertiendas Cañaveral - Sistema de Gestión Documental
                """
                
                msg = Message(
                    subject=f'🔐 Token de Firma Digital - {numero_relacion}',
                    recipients=[correo_usuario],
                    html=html_body,
                    body=text_body
                )
                
                # Enviar correo
                with current_app.app_context():
                    from flask_mail import Mail
                    mail = Mail(current_app)
                    mail.send(msg)
                
                correo_enviado = True
                
                # Log de auditoría
                log_security(
                    f"TOKEN FIRMA ENVIADO | "
                    f"usuario={usuario} | "
                    f"relacion={numero_relacion} | "
                    f"correo={correo_usuario} | "
                    f"token={token[:3]}*** | "
                    f"expira={fecha_expiracion.isoformat()} | "
                    f"IP={request.remote_addr}"
                )
            except Exception as mail_error:
                error_correo = str(mail_error)
                log_security(f"ERROR ENVIAR CORREO TOKEN | usuario={usuario} | error={error_correo}")
        
        # Retornar respuesta (con o sin correo enviado)
        return jsonify({
            "success": True,
            "message": f"Token generado correctamente{(' y enviado a ' + correo_usuario) if correo_enviado else '. Mostrar en pantalla'}",
            "token": token if not correo_enviado else None,  # Solo mostrar si no se envió por correo
            "token_id": token_firma.id,
            "expira_en_minutos": 10,
            "correo_destino": correo_usuario,
            "correo_enviado": correo_enviado,
            "error_correo": error_correo
        }), 200
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR SOLICITAR TOKEN FIRMA | usuario={session.get('usuario')} | error={str(e)}")
        return jsonify({"error": f"Error al solicitar token: {str(e)}"}), 500


# -------------------------------------------------
@relaciones_bp.route('/validar_token_y_firmar', methods=['POST'])
@requiere_permiso('relaciones', 'verificar_token')
def validar_token_y_firmar():
    """
    Valida el token de 6 dígitos y si es correcto,
    confirma la recepción digital con firma SHA256
    Valida el token de 6 dígitos y si es correcto,
    confirma la recepción digital con firma SHA256
    """
    # Validar sesión
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        from .models import TokenFirmaDigital, RecepcionDigital, FacturaRecibidaDigital
        import hashlib
        
        data = request.get_json()
        token_ingresado = data.get('token', '').strip()
        numero_relacion = data.get('numero_relacion')
        facturas_recibidas_raw = data.get('facturas_recibidas', [])  # Puede ser [ids] o [{id, observaciones}]
        
        # Normalizar a conjunto de IDs y mapa de observaciones
        facturas_ids = set()
        observaciones_map = {}
        for item in facturas_recibidas_raw:
            try:
                if isinstance(item, dict):
                    fid = int(item.get('id')) if item.get('id') is not None else None
                    if fid is not None:
                        facturas_ids.add(fid)
                        if item.get('observaciones'):
                            observaciones_map[fid] = item.get('observaciones')
                else:
                    fid = int(item)
                    facturas_ids.add(fid)
            except Exception:
                continue
        
        if not token_ingresado or not numero_relacion or not facturas_ids:
            return jsonify({"error": "Datos incompletos (token, relación, facturas)"}), 400
        
        # Buscar token vigente
        usuario = session.get('usuario')
        token_obj = TokenFirmaDigital.query.filter_by(
            token=token_ingresado,
            usuario=usuario,
            numero_relacion=numero_relacion
        ).first()
        
        if not token_obj:
            log_security(f"TOKEN FIRMA INVALIDO (no existe) | usuario={usuario} | relacion={numero_relacion} | token={token_ingresado}")
            return jsonify({"error": "Token inválido"}), 401
        
        # Incrementar intentos
        token_obj.intentos_validacion += 1
        db.session.commit()
        
        # Validar vigencia
        fecha_actual_colombia = obtener_fecha_naive_colombia()
        if not token_obj.esta_vigente():
            mensaje = "Token expirado" if fecha_actual_colombia > token_obj.fecha_expiracion else \
                     "Token ya utilizado" if token_obj.usado else \
                     "Máximo de intentos alcanzado"
            
            log_security(f"TOKEN FIRMA INVALIDO ({mensaje}) | usuario={usuario} | relacion={numero_relacion}")
            return jsonify({"error": mensaje}), 401
        
        # ✅ TOKEN VÁLIDO: Marcar como usado
        token_obj.usado = True
        token_obj.fecha_uso = obtener_fecha_naive_colombia()  # 🕐 Hora de Colombia
        token_obj.ip_uso = request.remote_addr
        
        # Consultar facturas de la relación
        facturas = RelacionFactura.query.filter_by(numero_relacion=numero_relacion).all()
        
        if not facturas:
            return jsonify({"error": f"No se encontró la relación {numero_relacion}"}), 404
        
        # Crear o actualizar recepción digital
        recepcion = RecepcionDigital.query.filter_by(
            numero_relacion=numero_relacion,
            usuario_receptor=usuario
        ).first()
        
        if not recepcion:
            recepcion = RecepcionDigital(
                numero_relacion=numero_relacion,
                usuario_receptor=usuario,
                nombre_receptor=session.get('nombre_completo', usuario),
                ip_recepcion=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                facturas_totales=len(facturas)
            )
            db.session.add(recepcion)
            db.session.flush()
        
        # Actualizar cantidad de facturas recibidas
        recepcion.facturas_recibidas = len(facturas_ids)
        recepcion.completa = (len(facturas_ids) == len(facturas))
        recepcion.fecha_recepcion = obtener_fecha_naive_colombia()  # 🕐 Hora de Colombia
        
        # 🔐 GENERAR FIRMA DIGITAL SHA256 (incluye el token validado)
        datos_firma = f"{numero_relacion}|{usuario}|{recepcion.fecha_recepcion.isoformat()}|{len(facturas_ids)}|{token_ingresado}"
        firma = hashlib.sha256(datos_firma.encode()).hexdigest()
        recepcion.firma_digital = firma
        
        # Registrar facturas recibidas individualmente
        # Solo marcar como recibidas las facturas seleccionadas
        for factura in facturas:
            factura_dict = factura.to_dict()
            factura_id = factura_dict['id']
            if factura_id in facturas_ids:
                # ✅ OBTENER CÓDIGO CORRECTO DEL C.O. desde facturas_recibidas
                co_codigo = 'N/A'
                try:
                    query_co = db.session.execute(
                        text("""
                            SELECT co.codigo
                            FROM facturas_recibidas fr
                            LEFT JOIN centros_operacion co ON fr.centro_operacion_id = co.id
                            WHERE fr.nit = :nit AND fr.prefijo = :prefijo AND fr.folio = :folio
                            LIMIT 1
                        """),
                        {"nit": factura.nit, "prefijo": factura.prefijo, "folio": factura.folio}
                    ).fetchone()
                    if query_co and query_co[0]:
                        co_codigo = query_co[0]
                except Exception:
                    co_codigo = factura.co  # Fallback al valor guardado
                
                factura_recibida = FacturaRecibidaDigital.query.filter_by(
                    recepcion_id=recepcion.id,
                    prefijo=factura.prefijo,
                    folio=factura.folio
                ).first()
                if not factura_recibida:
                    factura_recibida = FacturaRecibidaDigital(
                        recepcion_id=recepcion.id,
                        numero_relacion=numero_relacion,
                        nit=factura.nit,
                        razon_social=factura.razon_social,
                        prefijo=factura.prefijo,
                        folio=factura.folio,
                        co=co_codigo,  # ✅ USAR CÓDIGO CORRECTO
                        valor_total=factura.valor_total,
                        fecha_factura=factura.fecha_factura
                    )
                    db.session.add(factura_recibida)
                if not factura_recibida.recibida:
                    factura_recibida.recibida = True
                    factura_recibida.fecha_check = obtener_fecha_naive_colombia()  # 🕐 Hora de Colombia
                    factura_recibida.usuario_check = usuario
                    # Guardar observaciones si llegaron desde el frontend
                    if factura_id in observaciones_map:
                        factura_recibida.observaciones = observaciones_map[factura_id]
        
        # Commit de la transacción
        db.session.commit()
        
        # Log de auditoría
        log_security(
            f"FIRMA DIGITAL CONFIRMADA CON TOKEN | "
            f"usuario={usuario} | "
            f"relacion={numero_relacion} | "
            f"facturas={len(facturas_ids)}/{len(facturas)} | "
            f"firma={firma[:16]}... | "
            f"token_validado=SI | "
            f"IP={request.remote_addr}"
        )
        
        # 📧 ENVIAR CORREO CON LA RELACIÓN DE FACTURAS RECIBIDAS
        # ✅ Evitar import circular - usar text query directo
        result = db.session.execute(
            text("SELECT correo FROM usuarios WHERE usuario = :usuario"),
            {"usuario": usuario}
        ).fetchone()
        
        if result and result[0]:
            correo_destino = result[0]
            nombre_usuario = usuario  # Usar el nombre de usuario directamente
            try:
                # Consultar SOLO las facturas firmadas en ESTA sesión (con este token)
                # Filtrar por facturas cuya fecha_check coincida con la fecha de esta recepción
                facturas_firmadas_query = text("""
                    SELECT 
                        frd.nit,
                        t.razon_social,
                        frd.prefijo,
                        frd.folio,
                        frd.valor_total,
                        frd.fecha_check,
                        frd.co
                    FROM facturas_recibidas_digitales frd
                    LEFT JOIN terceros t ON frd.nit = t.nit
                    WHERE frd.recepcion_id = :recepcion_id 
                    AND frd.recibida = true
                    AND frd.fecha_check >= (
                        SELECT MAX(fecha_recepcion) 
                        FROM recepciones_digitales 
                        WHERE id = :recepcion_id
                    )
                    ORDER BY frd.fecha_check DESC, frd.prefijo, frd.folio
                """)
                
                facturas_firmadas = db.session.execute(
                    facturas_firmadas_query, 
                    {'recepcion_id': recepcion.id}
                ).fetchall()
                
                facturas_html = ""
                for factura in facturas_firmadas:
                    razon_social = factura.razon_social if factura.razon_social else 'TERCERO NO REGISTRADO'
                    fecha_firma = formatear_fecha_segura(factura.fecha_check, '%Y-%m-%d %H:%M:%S') if factura.fecha_check else 'N/A'
                    # ✅ Acceder al campo co por nombre de columna
                    co_codigo = factura.co if factura.co else 'N/A'
                    # ✅ OBTENER EMPRESA DESDE facturas_recibidas
                    empresa_id = 'N/A'
                    try:
                        query_extra = db.session.execute(
                            text("""
                                SELECT fr.empresa_id 
                                FROM facturas_recibidas fr
                                WHERE fr.nit = :nit AND fr.prefijo = :prefijo AND fr.folio = :folio
                                LIMIT 1
                            """),
                            {"nit": factura.nit, "prefijo": factura.prefijo, "folio": factura.folio}
                        ).fetchone()
                        if query_extra:
                            empresa_id = query_extra[0] or 'N/A'
                    except Exception:
                        pass
                    
                    facturas_html += f"""
                        <tr style='background: #d1fae5;'>
                            <td style='padding: 10px; border: 1px solid #ddd;'>{factura.nit}</td>
                            <td style='padding: 10px; border: 1px solid #ddd;'>{razon_social}</td>
                            <td style='padding: 10px; border: 1px solid #ddd;'><strong>{co_codigo}</strong></td>
                            <td style='padding: 10px; border: 1px solid #ddd;'><strong>{empresa_id}</strong></td>
                            <td style='padding: 10px; border: 1px solid #ddd;'>{factura.prefijo}-{factura.folio}</td>
                            <td style='padding: 10px; border: 1px solid #ddd;'>${factura.valor_total:,.2f}</td>
                            <td style='padding: 10px; border: 1px solid #ddd; font-size: 11px;'>{fecha_firma}</td>
                            <td style='padding: 10px; border: 1px solid #ddd; color: green; font-weight: bold;'>✅ RECIBIDA</td>
                        </tr>
                    """
                if not facturas_html:
                    facturas_html = "<tr><td colspan='8' style='text-align:center; color:#999;'>No se firmó ninguna factura en esta sesión.</td></tr>"
                
                html_confirmacion = f"""
                <!DOCTYPE html>
                <html>
                <head><meta charset="UTF-8"></head>
                <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f7fa;">
                    <div style="max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                        <div style="text-align: center; background: linear-gradient(135deg, #166534, #14532d); color: white; padding: 25px; border-radius: 8px; margin-bottom: 30px;">
                            <h1 style="margin: 0;">✅ Recepción Digital Confirmada</h1>
                        </div>
                        
                        <p><strong>Usuario:</strong> {nombre_usuario}</p>
                        <p><strong>Relación:</strong> {numero_relacion}</p>
                        <p><strong>Fecha y Hora:</strong> {formatear_fecha_segura(recepcion.fecha_recepcion, '%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>Facturas Firmadas en esta Sesión:</strong> {len(facturas_firmadas)} de {len(facturas)}</p>
                        
                        <h3>📋 Detalle de Facturas Recibidas en esta Sesión:</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #166534; color: white;">
                                    <th style="padding: 10px; border: 1px solid #ddd;">NIT</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">Razón Social</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">C.O.</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">Empresa</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">Factura</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">Valor</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">Fecha Firma</th>
                                    <th style="padding: 10px; border: 1px solid #ddd;">Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {facturas_html}
                            </tbody>
                        </table>
                        
                        <div style="background: #eff6ff; padding: 15px; border-radius: 6px; margin: 20px 0;">
                            <p style="margin: 0;"><strong>🔐 Firma Digital SHA256:</strong></p>
                            <p style="margin: 0; font-family: monospace; word-break: break-all; font-size: 12px;">{firma}</p>
                        </div>
                        
                        <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e8ed;">
                            <p>Supertiendas Cañaveral - Sistema de Gestión Documental</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                msg = Message(
                    subject=f'✅ Recepción Digital Confirmada - {numero_relacion}',
                    recipients=[correo_destino],
                    html=html_confirmacion
                )
                
                from flask import current_app
                with current_app.app_context():
                    from flask_mail import Mail
                    mail = Mail(current_app)
                    mail.send(msg)
                
                log_security(f"CORREO CONFIRMACION ENVIADO | usuario={usuario} | correo={correo_destino} | relacion={numero_relacion}")
            
            except Exception as e_mail:
                log_security(f"ERROR ENVIO CORREO CONFIRMACION | usuario={usuario} | error={str(e_mail)}")
        
        return jsonify({
            "success": True,
            "message": f"✅ Usted ha firmado el recibido de {len(facturas_ids)} facturas",
            "recepcion_id": recepcion.id,
            "firma_digital": firma,
            "completa": recepcion.completa,
            "correo_enviado": True if result and result[0] else False
        }), 200
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR VALIDAR TOKEN Y FIRMAR | usuario={session.get('usuario')} | error={str(e)}")
        return jsonify({"error": f"Error al validar token: {str(e)}"}), 500


# -------------------------------------------------
@relaciones_bp.route('/consultar_recepcion/<numero_relacion>', methods=['GET'])
@requiere_permiso('relaciones', 'consultar_recepcion')
def consultar_recepcion(numero_relacion):
    """
    Consulta el estado de recepción digital de una relación
    Retorna quién la recibió y cuándo
    Consulta el estado de recepción digital de una relación
    Retorna quién la recibió y cuándo
    """
    # Validar sesión
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        from .models import RecepcionDigital, FacturaRecibidaDigital
        
        # Buscar todas las recepciones de esta relación
        recepciones = RecepcionDigital.query.filter_by(numero_relacion=numero_relacion).all()
        
        if not recepciones:
            return jsonify({
                "success": False,
                "message": f"No hay recepciones digitales para la relación {numero_relacion}"
            }), 404
        
        # Convertir a diccionarios
        recepciones_dict = []
        for r in recepciones:
            # Buscar facturas recibidas
            facturas = FacturaRecibidaDigital.query.filter_by(recepcion_id=r.id).all()
            
            recepciones_dict.append({
                **r.to_dict(),
                'facturas': [f.to_dict() for f in facturas]
            })
        
        log_security(f"CONSULTA RECEPCION | usuario={session.get('usuario')} | relacion={numero_relacion} | recepciones={len(recepciones)}")
        
        return jsonify({
            "success": True,
            "numero_relacion": numero_relacion,
            "recepciones": recepciones_dict
        }), 200
    
    except Exception as e:
        log_security(f"ERROR CONSULTAR RECEPCION | usuario={session.get('usuario')} | relacion={numero_relacion} | error={str(e)}")
        return jsonify({"error": f"Error al consultar recepción: {str(e)}"}), 500


@relaciones_bp.route('/historial_recepciones', methods=['GET'])
@requiere_permiso_html('relaciones', 'consultar_recepcion')
def historial_recepciones():
    """
    Muestra el historial completo de recepciones digitales
    Con filtros por fecha, usuario, relación
    """
    # Validar sesión
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        from .models import RecepcionDigital
        
        # Obtener filtros
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        usuario_filtro = request.args.get('usuario')
        numero_relacion = request.args.get('numero_relacion')
        
        
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR SOLICITAR TOKEN RETIRO | usuario={session.get('usuario')} | error={str(e)}")
        return jsonify({"error": f"Error al solicitar token: {str(e)}"}), 500


@relaciones_bp.route('/confirmar_retiro_firma', methods=['POST'])
@requiere_permiso('relaciones', 'verificar_token')
def confirmar_retiro_firma():
    """
    Confirma el retiro de firma digital con token válido
    """
    # Validar sesión
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        token = data.get('token')
        numero_relacion = data.get('numero_relacion')
        
        if not token or not numero_relacion:
            return jsonify({"error": "Token y número de relación son requeridos"}), 400
        
        usuario = session.get('usuario')
        
        # Buscar token válido
        from .models import TokenFirmaDigital
        from datetime import datetime
        
        token_registro = TokenFirmaDigital.query.filter_by(
            token=token,
            usuario=usuario,
            numero_relacion=numero_relacion,
            usado=False
        ).first()
        
        if not token_registro:
            return jsonify({"error": "Token inválido o ya usado"}), 400
        
        # Verificar expiración
        fecha_actual_colombia = obtener_fecha_naive_colombia()
        if token_registro.fecha_expiracion < fecha_actual_colombia:
            return jsonify({"error": "Token expirado. Solicite uno nuevo."}), 400
        
        # Verificar intentos
        if token_registro.intentos_validacion >= 3:
            token_registro.usado = True
            db.session.commit()
            return jsonify({"error": "Máximo de intentos alcanzado. Solicite un nuevo token."}), 400
        
        # Incrementar intentos
        token_registro.intentos_validacion += 1
        db.session.commit()
        
        # Buscar facturas firmadas por este usuario en esta relación
        from .models import RelacionFactura
        facturas = RelacionFactura.query.filter_by(
            numero_relacion=numero_relacion,
            recibida=True,
            usuario_check=usuario
        ).all()
        
        if not facturas:
            return jsonify({
                "error": "No se encontraron facturas firmadas por usted en esta relación"
            }), 404
        
        # Retirar firma (cambiar estado a no recibida)
        cantidad = len(facturas)
        documentos_retirados = []
        
        for factura in facturas:
            documentos_retirados.append(f"{factura.prefijo}-{factura.folio}")
            factura.recibida = False
            factura.usuario_check = None
            factura.fecha_check = None
        
        # Marcar token como usado
        token_registro.usado = True
        token_registro.fecha_uso = obtener_fecha_naive_colombia()  # 🕐 Hora de Colombia
        
        # Commit
        db.session.commit()
        
        # Log de auditoría
        log_security(
            f"FIRMA RETIRADA | "
            f"usuario={usuario} | "
            f"relacion={numero_relacion} | "
            f"facturas={cantidad} | "
            f"documentos={', '.join(documentos_retirados[:5])}{'...' if len(documentos_retirados) > 5 else ''} | "
            f"IP={request.remote_addr}"
        )
        
        # Construir mensaje
        mensaje_documentos = ', '.join(documentos_retirados[:3])
        if len(documentos_retirados) > 3:
            mensaje_documentos += f" y {len(documentos_retirados) - 3} más"
        
        return jsonify({
            "success": True,
            "message": f"✅ Firma retirada de {cantidad} documento(s): {mensaje_documentos}",
            "facturas_afectadas": cantidad,
            "documentos": documentos_retirados
        }), 200
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR CONFIRMAR RETIRO FIRMA | usuario={session.get('usuario')} | error={str(e)}")
        return jsonify({"error": f"Error al retirar firma: {str(e)}"}), 500


# ========================================
# 🆕 ENDPOINTS - SINCRONIZACIÓN Y RECHAZO
# ========================================

@relaciones_bp.route('/rechazar_factura', methods=['POST'])
@requiere_permiso('relaciones', 'rechazar_factura')
def rechazar_factura():
    """
    Marca una factura como rechazada en una relación
    Actualiza el estado contable en maestro_dian_vs_erp a "Rechazada"
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data or 'id' not in data or 'motivo_rechazo' not in data:
            return jsonify({"error": "Faltan datos: id y motivo_rechazo son requeridos"}), 400
        
        factura_id = data['id']
        motivo_rechazo = data['motivo_rechazo'].strip()
        usuario = session.get('usuario', 'desconocido')
        
        if not motivo_rechazo:
            return jsonify({"error": "El motivo del rechazo es obligatorio"}), 400
        
        # Buscar la factura en relaciones
        factura_relacion = RelacionFactura.query.get(factura_id)
        
        if not factura_relacion:
            return jsonify({"error": "Factura no encontrada en relaciones"}), 404
        
        # Verificar que no esté ya rechazada
        if hasattr(factura_relacion, 'rechazada') and factura_relacion.rechazada:
            return jsonify({"error": "Esta factura ya fue rechazada anteriormente"}), 400
        
        # Marcar como rechazada en la tabla relaciones_facturas
        factura_relacion.rechazada = True
        factura_relacion.motivo_rechazo = motivo_rechazo
        factura_relacion.fecha_rechazo = obtener_fecha_naive_colombia()
        factura_relacion.usuario_rechazo = usuario
        
        # 🔄 Sincronizar con maestro_dian_vs_erp
        from modules.dian_vs_erp.sync_service import sincronizar_factura_rechazada
        
        exito_sync, mensaje_sync, accion_sync = sincronizar_factura_rechazada(
            nit=factura_relacion.nit,
            prefijo=factura_relacion.prefijo,
            folio=factura_relacion.folio,
            motivo=motivo_rechazo,
            usuario=usuario,
            origen='RELACIONES'
        )
        
        db.session.commit()
        
        log_security(f"FACTURA RECHAZADA | id={factura_id} | prefijo={factura_relacion.prefijo} | "
                    f"folio={factura_relacion.folio} | motivo={motivo_rechazo[:50]} | "
                    f"usuario={usuario} | sync={exito_sync}")
        
        mensaje_final = f"✅ Factura {factura_relacion.prefijo}-{factura_relacion.folio} rechazada correctamente."
        if exito_sync:
            mensaje_final += f" {mensaje_sync}"
        else:
            mensaje_final += f" ⚠️ Advertencia: {mensaje_sync}"
        
        return jsonify({
            "success": True,
            "message": mensaje_final,
            "factura": {
                "id": factura_relacion.id,
                "prefijo": factura_relacion.prefijo,
                "folio": factura_relacion.folio,
                "rechazada": True,
                "motivo_rechazo": motivo_rechazo,
                "sincronizado": exito_sync
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR RECHAZAR FACTURA | usuario={session.get('usuario')} | error={str(e)}")
        return jsonify({"error": f"Error al rechazar factura: {str(e)}"}), 500


@relaciones_bp.route('/revertir_rechazo_factura', methods=['POST'])
@requiere_permiso('relaciones', 'revertir_rechazo')
def revertir_rechazo_factura():
    """
    Revierte el rechazo de una factura (solo para administradores)
    """
    try:
        data = request.get_json()
        
        if not data or 'id' not in data:
            return jsonify({"error": "Falta el ID de la factura"}), 400
        
        factura_id = data['id']
        usuario = session.get('usuario', 'desconocido')
        
        # Buscar la factura
        factura_relacion = RelacionFactura.query.get(factura_id)
        
        if not factura_relacion:
            return jsonify({"error": "Factura no encontrada"}), 404
        
        if not factura_relacion.rechazada:
            return jsonify({"error": "Esta factura no está rechazada"}), 400
        
        # Revertir rechazo
        factura_relacion.rechazada = False
        factura_relacion.motivo_rechazo = None
        factura_relacion.fecha_rechazo = None
        factura_relacion.usuario_rechazo = None
        
        # 🔄 Actualizar maestro_dian_vs_erp a estado "En Trámite"
        from modules.dian_vs_erp.sync_service import sincronizar_factura_en_tramite
        
        exito_sync, mensaje_sync, _ = sincronizar_factura_en_tramite(
            nit=factura_relacion.nit,
            prefijo=factura_relacion.prefijo,
            folio=factura_relacion.folio,
            numero_relacion=factura_relacion.numero_relacion,
            usuario=usuario
        )
        
        db.session.commit()
        
        log_security(f"RECHAZO REVERTIDO | id={factura_id} | usuario={usuario}")
        
        return jsonify({
            "success": True,
            "message": f"✅ Rechazo revertido. Factura vuelve a estado 'En Trámite'. {mensaje_sync}"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR REVERTIR RECHAZO | error={str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500
