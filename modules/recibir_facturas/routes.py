# =============================================
# 🚀 routes.py — Flask Blueprint para Recibir Facturas
# =============================================
from flask import Blueprint, render_template, request, jsonify, session, send_file
from datetime import datetime, date
from sqlalchemy import func
from extensions import db  # Importar desde extensions, no desde app
from .models import FacturaTemporal, FacturaRecibida, ObservacionFactura, ObservacionFacturaTemporal, get_tercero_by_nit
from decoradores_permisos import requiere_permiso, requiere_permiso_html  # 🔐 NUEVO: Decoradores de permisos
import pandas as pd
import io
import logging
import traceback  # ✅ AGREGADO: Para logging detallado de errores

# 🔄 SINCRONIZACIÓN EN TIEMPO REAL con DIAN vs ERP
from modules.dian_vs_erp.sync_service import (
    sincronizar_factura_recibida,
    eliminar_factura_temporal,
    obtener_estado_actual
)

# ✅ Usa el logger "security" compartido → escribe en logs/security.log (igual que app.py)
security_logger = logging.getLogger("security")

# Función helper para logging de seguridad
def log_security(mensaje):
    """Registra eventos de seguridad en logger compartido (logs/security.log)"""
    security_logger.info(mensaje)

# -------------------------------------------------
# 📦 BLUEPRINT
# -------------------------------------------------
recibir_facturas_bp = Blueprint('recibir_facturas', __name__)

# -------------------------------------------------
# 🔐 HELPER: VALIDAR SESIÓN
# -------------------------------------------------
def validar_sesion():
    """Valida que el usuario tenga sesión activa"""
    if 'usuario_id' not in session or 'usuario' not in session:
        return False, {"error": "Sesión no válida", "redirect": "/login"}, 401
    return True, None, None

# -------------------------------------------------
# 📄 RUTA RAÍZ: REDIRECCIONAR A NUEVA_FACTURA
# -------------------------------------------------
@recibir_facturas_bp.route('/')
@requiere_permiso_html('recibir_facturas', 'acceder_modulo')  # 🔐 VALIDAR PERMISO DE ACCESO
def index():
    """Ruta raíz del módulo - redirige a nueva_factura"""
    from flask import redirect, url_for
    return redirect(url_for('recibir_facturas.nueva_factura'))

# -------------------------------------------------
# 📄 RUTA: NUEVA FACTURA (formulario)
# -------------------------------------------------
@recibir_facturas_bp.route('/nueva_factura')
@requiere_permiso_html('recibir_facturas', 'nueva_factura')  # 🔐 VALIDAR PERMISO
def nueva_factura():
    """Formulario para registrar nueva factura"""
    # Validar sesión - si no es válida, redirigir al login
    if 'usuario_id' not in session or 'usuario' not in session:
        from flask import redirect, flash
        flash('⚠️ Debes iniciar sesión para acceder al módulo de Recibir Facturas', 'warning')
        return redirect('/')  # Redirige al login principal
    
    # ✅ CARGAR CENTROS DE OPERACIÓN
    from .models import CentroOperacion
    centros = CentroOperacion.query.order_by(CentroOperacion.codigo).all()
    centros_operacion = [{'id': c.id, 'codigo': c.codigo, 'nombre': c.nombre} for c in centros]
    
    # ✅ CARGAR EMPRESAS (NUEVO) - Usando query SQL directa para evitar circular imports
    from sqlalchemy import text
    result = db.session.execute(text("""
        SELECT sigla, nombre 
        FROM empresas 
        WHERE activo = true 
        ORDER BY sigla
    """))
    empresas_list = [{'codigo': row[0], 'nombre': row[1]} for row in result]
    
    return render_template('nueva_factura.html',  # ✅ ARCHIVO CON VALIDACIONES DE ANTIGÜEDAD
                          usuario=session.get('usuario'),
                          nit=session.get('nit'),
                          centros_operacion=centros_operacion,
                          empresas=empresas_list,
                          fecha_hoy=date.today().isoformat())

# -------------------------------------------------
# 🔍 ENDPOINT: VERIFICAR TERCERO
# -------------------------------------------------
@recibir_facturas_bp.route('/verificar_tercero', methods=['GET'])
@requiere_permiso('recibir_facturas', 'nueva_factura')  # 🔐 VALIDAR PERMISO
def verificar_tercero():
    """
    Verifica si un NIT existe en la tabla terceros
    y retorna su información con estado de actualización
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    nit = request.args.get('nit', '').strip()
    
    if not nit:
        return jsonify({"error": "NIT requerido"}), 400
    
    try:
        # ✅ Usar función helper que hace query SQL directa (sin circular import)
        tercero = get_tercero_by_nit(nit)
        
        if not tercero:
            return jsonify({
                "existe": False,
                "mensaje": "El NIT no está registrado. ¿Desea crear el tercero?"
            }), 404
        
        # ⚠️ Verificar que tenga razón social
        razon_social = tercero['razon_social'] if tercero['razon_social'] else "SIN RAZÓN SOCIAL"
        if not tercero['razon_social'] or tercero['razon_social'].strip() == "":
            return jsonify({
                "existe": True,
                "razon_social": "⚠️ SIN RAZÓN SOCIAL",
                "requiere_actualizacion": True,
                "mensaje": "⚠️ ADVERTENCIA: El tercero existe pero NO tiene razón social registrada. Se recomienda actualizar sus datos.",
                "fecha_actualizacion": None,
                "estado_documentacion": None
            }), 200
        
        # Calcular antigüedad y si requiere actualización (>= 1 año desde fecha_actualizacion)
        requiere_actualizacion = False
        dias_antiguedad = 0
        if tercero['fecha_actualizacion']:
            hoy = date.today()
            fecha_act = tercero['fecha_actualizacion'].date() if isinstance(tercero['fecha_actualizacion'], datetime) else tercero['fecha_actualizacion']
            dias_antiguedad = (hoy - fecha_act).days
            requiere_actualizacion = dias_antiguedad >= 365
        
        return jsonify({
            "existe": True,
            "razon_social": tercero['razon_social'],
            "fecha_actualizacion": tercero['fecha_actualizacion'].isoformat() if tercero['fecha_actualizacion'] else None,
            "dias_antiguedad": dias_antiguedad,  # ✅ NUEVO: Días desde última actualización
            "requiere_actualizacion": requiere_actualizacion,
            "estado_documentacion": None,  # No disponible en query directa
            "mensaje": "⚠️ ATENCIÓN: La documentación del tercero está DESACTUALIZADA (>= 1 año). ¿Desea continuar?" if requiere_actualizacion else "Tercero encontrado"
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error al verificar tercero: {str(e)}"}), 500

# -------------------------------------------------
# 🔍 ENDPOINT: VALIDAR CLAVE FACTURA (NIT + Prefijo + Folio)
# -------------------------------------------------
@recibir_facturas_bp.route('/validar_factura_registrada', methods=['GET'])
@requiere_permiso('recibir_facturas', 'nueva_factura')  # 🔐 VALIDAR PERMISO
def validar_factura_registrada():
    """
    Valida si una factura (NIT + Prefijo + Folio) ya existe
    en facturas_temporales o facturas_recibidas
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    nit = request.args.get('nit', '').strip()
    prefijo = request.args.get('prefijo', '').strip()
    folio = request.args.get('folio', '').strip()
    
    # 🔍 DEBUG: Log de validación
    log_security(f"VALIDAR CLAVE | NIT: {nit} | Prefijo: {prefijo} | Folio: {folio}")
    
    if not nit or not folio:
        return jsonify({"error": "NIT y folio requeridos"}), 400
    
    try:
        # Normalizar folio (sin ceros a la izquierda)
        folio_normalizado = folio.lstrip('0') if folio else ''
        
        # Buscar en facturas recibidas
        existe_recibida, factura_recibida = FacturaRecibida.validar_clave_unica(nit, prefijo, folio)
        log_security(f"VALIDAR RECIBIDAS | Existe: {existe_recibida}")
        
        # Buscar en facturas temporales
        existe_temporal, factura_temporal = FacturaTemporal.validar_clave_unica(nit, prefijo, folio)
        log_security(f"VALIDAR TEMPORAL | Existe: {existe_temporal}")
        
        if existe_recibida:
            fecha_rad = factura_recibida.fecha_radicacion.strftime('%d/%m/%Y') if factura_recibida.fecha_radicacion else 'N/A'
            return jsonify({
                "registrada": True,
                "en_recibidas": True,
                "en_temporal": False,
                "fecha_radicacion": factura_recibida.fecha_radicacion.isoformat() if factura_recibida.fecha_radicacion else None,
                "mensaje": f"❌ FACTURA DUPLICADA: La factura {prefijo}{folio} ya existe en FACTURAS RECIBIDAS (Radicada: {fecha_rad})"
            }), 200
        
        if existe_temporal:
            fecha_rad = factura_temporal.fecha_radicacion.strftime('%d/%m/%Y') if factura_temporal.fecha_radicacion else 'N/A'
            return jsonify({
                "registrada": True,
                "en_recibidas": False,
                "en_temporal": True,
                "fecha_radicacion": factura_temporal.fecha_radicacion.isoformat() if factura_temporal.fecha_radicacion else None,
                "mensaje": f"❌ FACTURA DUPLICADA: La factura {prefijo}{folio} ya existe en LISTA TEMPORAL (Fecha: {fecha_rad})"
            }), 200
        
        # No existe
        return jsonify({
            "registrada": False,
            "en_recibidas": False,
            "en_temporal": False,
            "mensaje": f"✅ Factura {prefijo}{folio} disponible. Puedes adicionarla."
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error al validar factura: {str(e)}"}), 500

# -------------------------------------------------
# 💾 ENDPOINT: GUARDAR FACTURA TEMPORAL
# -------------------------------------------------
@recibir_facturas_bp.route('/guardar_factura_temporal', methods=['POST'])
@requiere_permiso('recibir_facturas', 'nueva_factura')  # 🔐 VALIDAR PERMISO
def guardar_factura_temporal():
    """
    Guarda una factura en la tabla facturas_temporales
    (reemplaza escritura a temp_{usuario}.csv)
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    data = request.get_json()
    
    try:
        # 🔍 DEBUG: Ver qué empresa_id llega en POST
        log_security(f"🔍 GUARDAR FACTURA | empresa_id recibido: {data.get('empresa_id')}")
        
        # Validar campos requeridos
        campos_requeridos = ['nit', 'razon_social', 'prefijo', 'folio', 'empresa_id', 'centro_operacion_id', 
                            'fecha_expedicion', 'valor_bruto']
        
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({"error": f"Campo requerido: {campo}"}), 400
        
        # Validar clave única
        existe_recibida, _ = FacturaRecibida.validar_clave_unica(
            data['nit'], data['prefijo'], data['folio']
        )
        existe_temporal, _ = FacturaTemporal.validar_clave_unica(
            data['nit'], data['prefijo'], data['folio']
        )
        
        if existe_recibida or existe_temporal:
            return jsonify({"error": "La factura ya está registrada"}), 400
        
        # Mapear nombres de campos del frontend a nombres de BD
        if 'usuario_compra' in data:
            data['comprador'] = data.pop('usuario_compra')
        if 'usuario_recibe' in data:
            data['quien_recibe'] = data.pop('usuario_recibe')
        
        # Crear factura temporal
        data['usuario_id'] = session['usuario_id']
        data['usuario_nombre'] = session.get('usuario', 'USUARIO')  # Nombre del usuario
        data['fecha_radicacion'] = data.get('fecha_radicacion', date.today().isoformat())
        
        # Calcular valor neto antes de guardar
        valor_neto = float(data.get('valor_bruto', 0))
        valor_neto += float(data.get('iva', 0))
        valor_neto -= float(data.get('descuento', 0))
        valor_neto -= float(data.get('retencion_fuente', 0))
        valor_neto -= float(data.get('rete_iva', 0))
        valor_neto -= float(data.get('rete_ica', 0))
        data['valor_neto'] = round(valor_neto, 2)
        
        # Obtener nombre del centro de operación si solo enviaron ID
        if 'centro_operacion_id' in data and 'centro_operacion' not in data:
            from .models import CentroOperacion
            centro = CentroOperacion.query.get(data['centro_operacion_id'])
            if centro:
                data['centro_operacion'] = centro.nombre
        
        factura = FacturaTemporal.from_dict(data)
        db.session.add(factura)
        db.session.flush()  # ✅ Obtener ID de factura antes de commit
        
        # ✅ NUEVO: Si hay observaciones, guardarlas con timestamp + usuario
        observaciones_texto = data.get('observaciones', '').strip()
        if observaciones_texto:
            observacion = ObservacionFacturaTemporal(
                factura_temporal_id=factura.id,
                observacion=observaciones_texto,
                usuario_id=session['usuario_id']
                # fecha_creacion se setea automáticamente con default=datetime.utcnow
            )
            db.session.add(observacion)
            log_security(f"OBSERVACION GUARDADA | Factura: {factura.numero_factura} | Usuario: {session['usuario_id']} | Texto: {observaciones_texto[:50]}...")
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "mensaje": "Factura agregada a lista temporal",
            "factura": factura.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al guardar factura: {str(e)}"}), 500

# -------------------------------------------------
# 📋 ENDPOINT: CARGAR FACTURAS TEMPORALES
# -------------------------------------------------
@recibir_facturas_bp.route('/cargar_facturas_temporales', methods=['GET'])
@requiere_permiso('recibir_facturas', 'cargar_facturas_temporales')  # 🔐 VALIDAR PERMISO
def cargar_facturas_temporales():
    """
    Retorna todas las facturas temporales del usuario actual
    (reemplaza lectura de temp_{usuario}.csv)
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        usuario_id = session['usuario_id']
        
        # Obtener todas las facturas temporales del usuario
        # ✅ ORDEN: Primera adicionada arriba (ASC por ID = más antigua primero)
        facturas = FacturaTemporal.query.filter_by(usuario_id=usuario_id).order_by(FacturaTemporal.id.asc()).all()
        
        facturas_list = []
        for f in facturas:
            factura_dict = f.to_dict()
            
            # ✅ NUEVO: Agregar observaciones con timestamp + usuario
            observaciones_registradas = ObservacionFacturaTemporal.query.filter_by(
                factura_temporal_id=f.id
            ).order_by(ObservacionFacturaTemporal.fecha_creacion.desc()).all()
            
            if observaciones_registradas:
                obs_list = []
                for obs in observaciones_registradas:
                    obs_list.append({
                        'observacion': obs.observacion,
                        'usuario_id': obs.usuario_id,
                        'fecha_creacion': obs.fecha_creacion.isoformat() if obs.fecha_creacion else None
                    })
                factura_dict['observaciones_historial'] = obs_list
                # Última observación como texto principal
                factura_dict['observaciones'] = observaciones_registradas[0].observacion
            
            facturas_list.append(factura_dict)
        
        return jsonify({
            "facturas": facturas_list,
            "total": len(facturas_list)
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error al cargar facturas: {str(e)}"}), 500

# -------------------------------------------------
# 💾 ENDPOINT: GUARDAR FACTURAS MASIVO (Temporal → Recibidas)
# -------------------------------------------------
@recibir_facturas_bp.route('/guardar_facturas_masivo', methods=['POST'])
@requiere_permiso('recibir_facturas', 'guardar_facturas')  # 🔐 VALIDAR PERMISO
def guardar_facturas_masivo():
    """
    Mueve facturas seleccionadas de facturas_temporales → facturas_recibidas
    (reemplaza escritura a facturas_recibidas.csv + borrado de temp_{usuario}.csv)
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    data = request.get_json()
    facturas_ids = data.get('facturas_ids', [])
    
    if not facturas_ids:
        return jsonify({"error": "No se seleccionaron facturas"}), 400
    
    try:
        usuario_id = session['usuario_id']
        facturas_guardadas = []
        facturas_duplicadas = []
        
        for factura_id in facturas_ids:
            # Obtener factura temporal
            factura_temp = FacturaTemporal.query.filter_by(
                id=factura_id, 
                usuario_id=usuario_id
            ).first()
            
            if not factura_temp:
                continue
            
            # Verificar si ya existe en recibidas
            existe, _ = FacturaRecibida.validar_clave_unica(
                factura_temp.nit,
                factura_temp.prefijo, 
                factura_temp.folio
            )
            
            if existe:
                facturas_duplicadas.append({
                    'numero_factura': f"{factura_temp.prefijo}{factura_temp.folio}",
                    'nit': factura_temp.nit
                })
                continue
            
            # ✅ CALCULAR valor_neto ANTES de crear objeto (FIX: InstrumentedAttribute)
            valor_neto_calculado = (
                float(factura_temp.valor_bruto or 0) +
                float(factura_temp.iva or 0) -
                float(factura_temp.descuento or 0) -
                float(factura_temp.retencion_fuente or 0) -
                float(factura_temp.rete_iva or 0) -
                float(factura_temp.rete_ica or 0)
            )
            
            # ✅ Crear factura recibida (numero_factura es GENERATED COLUMN, no se setea)
            factura_recibida = FacturaRecibida(
                nit=factura_temp.nit,
                razon_social=factura_temp.razon_social,
                prefijo=factura_temp.prefijo or '',
                folio=factura_temp.folio,
                # numero_factura NO se setea - es GENERATED COLUMN en PostgreSQL
                empresa_id=factura_temp.empresa_id,  # ✅ NUEVO: Incluir empresa
                centro_operacion_id=factura_temp.centro_operacion_id,
                centro_operacion=factura_temp.centro_operacion or '',
                fecha_expedicion=factura_temp.fecha_expedicion,
                fecha_radicacion=factura_temp.fecha_radicacion,
                fecha_vencimiento=factura_temp.fecha_vencimiento,
                valor_bruto=factura_temp.valor_bruto,
                descuento=factura_temp.descuento or 0,
                iva=factura_temp.iva or 0,
                retencion_fuente=factura_temp.retencion_fuente or 0,
                rete_iva=factura_temp.rete_iva or 0,
                rete_ica=factura_temp.rete_ica or 0,
                valor_neto=valor_neto_calculado,  # ✅ Calculado explícitamente
                usuario_solicita=factura_temp.usuario_solicita or 'NA',
                comprador=factura_temp.comprador or 'NA',
                quien_recibe=factura_temp.quien_recibe or 'NA',
                forma_pago=factura_temp.forma_pago or 'CREDITO',
                plazo=factura_temp.plazo or 30,
                estado='RECIBIDA',
                observaciones=factura_temp.observaciones,
                usuario_nombre=factura_temp.usuario_nombre,
                usuario_id=usuario_id
            )
            
            db.session.add(factura_recibida)
            db.session.flush()  # Obtener ID de factura_recibida
            db.session.commit()  # ✅ COMMIT AQUÍ para que exista en BD antes de observaciones
            
            # 🔄 SINCRONIZACIÓN EN TIEMPO REAL - Estado: "Recibida"
            try:
                usuario_nombre = session.get('usuario', 'DESCONOCIDO')
                resultado_sync = sincronizar_factura_recibida(
                    nit=factura_temp.nit,
                    prefijo=factura_temp.prefijo or '',
                    folio=factura_temp.folio,
                    fecha_recibida=factura_recibida.fecha_radicacion or datetime.now(),
                    usuario=usuario_nombre,
                    origen='RECIBIR_FACTURAS',
                    razon_social=factura_temp.razon_social
                )
                
                exito, mensaje, accion = resultado_sync
                
                if exito:
                    log_security(
                        f"SINCRONIZACIÓN EXITOSA | {accion} | "
                        f"NIT={factura_temp.nit} | PREFIJO={factura_temp.prefijo} | "
                        f"FOLIO={factura_temp.folio} | estado=Recibida | usuario={usuario_nombre}"
                    )
                else:
                    # No fallar la transacción si la sincronización falla
                    log_security(
                        f"ADVERTENCIA SINCRONIZACIÓN | {mensaje} | "
                        f"NIT={factura_temp.nit} | PREFIJO={factura_temp.prefijo} | FOLIO={factura_temp.folio}"
                    )
            except Exception as e_sync:
                # No fallar la transacción principal si la sincronización falla
                log_security(f"ERROR SINCRONIZACIÓN | {str(e_sync)} | NIT={factura_temp.nit}")
                # Continuar con el guardado de la factura
            
            # ✅ Copiar observaciones a tabla de observaciones (con usuario_nombre)
            observaciones_temp = ObservacionFacturaTemporal.query.filter_by(
                factura_temporal_id=factura_temp.id
            ).all()
            
            for obs_temp in observaciones_temp:
                obs_recibida = ObservacionFactura(
                    factura_id=factura_recibida.id,
                    observacion=obs_temp.observacion,
                    usuario_nombre=factura_temp.usuario_nombre,  # ✅ Campo requerido
                    usuario_id=obs_temp.usuario_id
                )
                db.session.add(obs_recibida)
            
            # ✅ CAPTURAR TODOS LOS DATOS **ANTES** DE DELETE
            numero_factura_guardado = f"{factura_temp.prefijo or ''}{factura_temp.folio}"
            nit_guardado = str(factura_temp.nit)
            razon_social_guardada = str(factura_temp.razon_social)
            valor_neto_guardado = valor_neto_calculado  # ✅ Usar valor calculado
            
            # ✅ ELIMINAR OBSERVACIONES TEMPORALES PRIMERO (evitar UPDATE a NULL)
            for obs in observaciones_temp:
                db.session.delete(obs)
            
            # ✅ AHORA SÍ ELIMINAR FACTURA TEMPORAL
            db.session.delete(factura_temp)
            
            # ✅ USAR VARIABLES CAPTURADAS (no factura_temp)
            facturas_guardadas.append({
                'numero_factura': numero_factura_guardado,
                'nit': nit_guardado,
                'razon_social': razon_social_guardada,
                'valor_neto': valor_neto_guardado
            })
        
        # ✅ COMMIT FINAL: Confirmar eliminación de temporales y observaciones temporales
        db.session.commit()
        
        log_security(f"FACTURAS GUARDADAS EXITOSAMENTE | Usuario: {session.get('usuario_id')} | Guardadas: {len(facturas_guardadas)} | Duplicadas: {len(facturas_duplicadas)}")
        
        return jsonify({
            "success": True,
            "guardadas": len(facturas_guardadas),
            "duplicadas": len(facturas_duplicadas),
            "facturas_guardadas": facturas_guardadas,
            "facturas_duplicadas": facturas_duplicadas,
            "mensaje": f"✅ Se guardaron {len(facturas_guardadas)} factura(s) en FACTURAS RECIBIDAS exitosamente"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR | guardar_facturas_masivo | Usuario: {session.get('usuario_id')} | IDs: {facturas_ids} | Error: {str(e)} | Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Error al guardar facturas: {str(e)}"}), 500

# -------------------------------------------------
# 🔄 ENDPOINT: ACTUALIZAR FACTURAS TEMPORALES
# -------------------------------------------------
@recibir_facturas_bp.route('/api/actualizar_temporales', methods=['POST'])
@requiere_permiso('recibir_facturas', 'nueva_factura')  # 🔐 VALIDAR PERMISO
def actualizar_temporales():
    """
    Sobrescribe todas las facturas temporales del usuario con nueva lista
    (reemplaza sobrescritura de temp_{usuario}.csv)
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    data = request.get_json()
    facturas_nuevas = data.get('facturas', [])
    
    try:
        usuario_id = session['usuario_id']
        
        # Eliminar todas las facturas temporales actuales del usuario
        FacturaTemporal.query.filter_by(usuario_id=usuario_id).delete()
        
        # Insertar nuevas facturas
        facturas_insertadas = []
        
        for factura_data in facturas_nuevas:
            factura_data['usuario_id'] = usuario_id
            factura = FacturaTemporal.from_dict(factura_data)
            db.session.add(factura)
            facturas_insertadas.append(factura)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "facturas_actualizadas": len(facturas_insertadas),
            "mensaje": "Facturas temporales actualizadas"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar facturas: {str(e)}"}), 500

# -------------------------------------------------
# 🗑️ ENDPOINT: LIMPIAR FACTURAS TEMPORALES
# -------------------------------------------------
@recibir_facturas_bp.route('/api/limpiar_temporales', methods=['POST'])
@requiere_permiso('recibir_facturas', 'eliminar_factura')  # 🔐 VALIDAR PERMISO
def limpiar_temporales():
    """
    Elimina todas las facturas temporales del usuario
    (reemplaza borrado de temp_{usuario}.csv)
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        usuario_id = session['usuario_id']
        
        # Eliminar todas las facturas temporales del usuario
        eliminadas = FacturaTemporal.query.filter_by(usuario_id=usuario_id).delete()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "eliminadas": eliminadas,
            "mensaje": f"Se eliminaron {eliminadas} facturas temporales"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al limpiar facturas: {str(e)}"}), 500

# -------------------------------------------------
# 📝 ENDPOINT: AGREGAR OBSERVACIÓN (NUEVO)
# -------------------------------------------------
@recibir_facturas_bp.route('/api/agregar_observacion', methods=['POST'])
@requiere_permiso('recibir_facturas', 'editar_factura')  # 🔐 VALIDAR PERMISO
def agregar_observacion():
    """
    Agrega una observación a una factura (temporal o recibida)
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    data = request.get_json()
    tipo = data.get('tipo')  # 'temporal' o 'recibida'
    factura_id = data.get('factura_id')
    observacion_texto = data.get('observacion', '').strip()
    
    if not tipo or not factura_id or not observacion_texto:
        return jsonify({"error": "Tipo, factura_id y observación requeridos"}), 400
    
    if len(observacion_texto) > 5000:
        return jsonify({"error": "Observación muy larga (máx 5000 caracteres)"}), 400
    
    try:
        usuario_id = session['usuario_id']
        
        if tipo == 'temporal':
            observacion = ObservacionFacturaTemporal(
                factura_temporal_id=factura_id,
                observacion=observacion_texto,
                usuario_id=usuario_id
            )
        elif tipo == 'recibida':
            observacion = ObservacionFactura(
                factura_id=factura_id,
                observacion=observacion_texto,
                usuario_id=usuario_id
            )
        else:
            return jsonify({"error": "Tipo de factura inválido"}), 400
        
        db.session.add(observacion)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "observacion": observacion.to_dict(),
            "mensaje": "Observación agregada"
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al agregar observación: {str(e)}"}), 500

# -------------------------------------------------
# 📊 ENDPOINT: OBTENER OBSERVACIONES (NUEVO)
# -------------------------------------------------
@recibir_facturas_bp.route('/api/obtener_observaciones', methods=['GET'])
@requiere_permiso('recibir_facturas', 'consultar_facturas')  # 🔐 VALIDAR PERMISO
def obtener_observaciones():
    """
    Obtiene todas las observaciones de una factura (ordenadas por fecha DESC)
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    tipo = request.args.get('tipo')  # 'temporal' o 'recibida'
    factura_id = request.args.get('factura_id')
    
    if not tipo or not factura_id:
        return jsonify({"error": "Tipo y factura_id requeridos"}), 400
    
    try:
        if tipo == 'temporal':
            observaciones = ObservacionFacturaTemporal.query.filter_by(
                factura_temporal_id=factura_id
            ).order_by(ObservacionFacturaTemporal.fecha_creacion.desc()).all()
        elif tipo == 'recibida':
            observaciones = ObservacionFactura.query.filter_by(
                factura_id=factura_id
            ).order_by(ObservacionFactura.fecha_creacion.desc()).all()
        else:
            return jsonify({"error": "Tipo de factura inválido"}), 400
        
        observaciones_list = [obs.to_dict() for obs in observaciones]
        
        return jsonify({
            "observaciones": observaciones_list,
            "total": len(observaciones_list)
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error al obtener observaciones: {str(e)}"}), 500

# -------------------------------------------------
# 📊 ENDPOINT: OBTENER KPIs (NUEVO)
# -------------------------------------------------
@recibir_facturas_bp.route('/api/obtener_kpis', methods=['GET'])
@requiere_permiso('recibir_facturas', 'consultar_facturas')  # 🔐 VALIDAR PERMISO
def obtener_kpis():
    """
    Obtiene KPIs de facturas (pendientes, próximas a vencer, vencidas, montos)
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        # Ejecutar función SQL obtener_kpis_facturas()
        result = db.session.execute(
            db.text("SELECT * FROM obtener_kpis_facturas()")
        ).fetchone()
        
        if result:
            kpis = {
                'total_recibidas': result[0],
                'pendientes': result[1],
                'proximas_vencer': result[2],
                'vencidas': result[3],
                'monto_pendiente': float(result[4]) if result[4] else 0,
                'monto_vencido': float(result[5]) if result[5] else 0
            }
        else:
            kpis = {
                'total_recibidas': 0,
                'pendientes': 0,
                'proximas_vencer': 0,
                'vencidas': 0,
                'monto_pendiente': 0,
                'monto_vencido': 0
            }
        
        return jsonify(kpis), 200
    
    except Exception as e:
        return jsonify({"error": f"Error al obtener KPIs: {str(e)}"}), 500

# -------------------------------------------------
# 📥 ENDPOINT: EXPORTAR A EXCEL (NUEVO)
# -------------------------------------------------
@recibir_facturas_bp.route('/api/exportar_excel', methods=['POST'])
@requiere_permiso('recibir_facturas', 'exportar_facturas')  # 🔐 VALIDAR PERMISO
def exportar_excel():
    """
    Exporta facturas seleccionadas a un archivo Excel
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    data = request.get_json()
    tipo = data.get('tipo', 'recibida')  # 'temporal' o 'recibida'
    facturas_ids = data.get('facturas_ids', [])
    
    if not facturas_ids:
        return jsonify({"error": "No se seleccionaron facturas"}), 400
    
    try:
        # Obtener facturas
        if tipo == 'temporal':
            facturas = FacturaTemporal.query.filter(FacturaTemporal.id.in_(facturas_ids)).all()
        else:
            facturas = FacturaRecibida.query.filter(FacturaRecibida.id.in_(facturas_ids)).all()
        
        if not facturas:
            return jsonify({"error": "No se encontraron facturas"}), 404
        
        # ✅ CONVERSIÓN MANUAL (evitar to_dict() que causa InstrumentedAttribute)
        facturas_dicts = []
        for f in facturas:
            try:
                factura_dict = {
                    'numero_factura': f.numero_factura or f"{f.prefijo or ''}{f.folio}",
                    'nit': str(f.nit),
                    'razon_social': str(f.razon_social),
                    'fecha_expedicion': f.fecha_expedicion.isoformat() if f.fecha_expedicion else '',
                    'fecha_radicacion': f.fecha_radicacion.isoformat() if f.fecha_radicacion else '',
                    'fecha_vencimiento': f.fecha_vencimiento.isoformat() if f.fecha_vencimiento else '',
                    'valor_bruto': float(f.valor_bruto) if f.valor_bruto else 0.0,
                    'iva': float(f.iva) if f.iva else 0.0,
                    'descuento': float(f.descuento) if f.descuento else 0.0,
                    'retencion_fuente': float(f.retencion_fuente) if f.retencion_fuente else 0.0,
                    'rete_iva': float(f.rete_iva) if f.rete_iva else 0.0,
                    'rete_ica': float(f.rete_ica) if f.rete_ica else 0.0,
                    'valor_neto': float(f.valor_neto) if f.valor_neto else 0.0,
                    'forma_pago': str(f.forma_pago or 'CREDITO'),
                    'plazo': int(f.plazo) if f.plazo else 30,
                    'usuario_solicita': str(f.usuario_solicita or ''),
                    'comprador': str(f.comprador or ''),
                    'quien_recibe': str(f.quien_recibe or ''),
                    'centro_operacion': str(f.centro_operacion or ''),
                    'observaciones': str(f.observaciones or '')
                }
                facturas_dicts.append(factura_dict)
            except Exception as e_dict:
                log_security(f"ERROR | exportar_excel | Error al convertir factura {f.id}: {str(e_dict)} | Traceback: {traceback.format_exc()}")
                continue
        
        if not facturas_dicts:
            log_security(f"ERROR | exportar_excel | No se pudieron procesar las facturas seleccionadas")
            return jsonify({"error": "No se pudieron procesar las facturas"}), 500
        
        # Crear DataFrame
        df = pd.DataFrame(facturas_dicts)
        
        # Reordenar columnas
        columnas_orden = [
            'numero_factura', 'nit', 'razon_social', 'fecha_expedicion', 
            'fecha_radicacion', 'fecha_vencimiento', 'valor_bruto', 'iva', 
            'descuento', 'retencion_fuente', 'rete_iva', 'rete_ica', 
            'valor_neto', 'forma_pago', 'plazo', 'usuario_solicita', 
            'comprador', 'quien_recibe', 'centro_operacion'  # ✅ CORRECTO: centro_operacion (nombre del CO)
        ]
        
        # Filtrar columnas existentes
        columnas_existentes = [col for col in columnas_orden if col in df.columns]
        df = df[columnas_existentes]
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Facturas')
        
        output.seek(0)
        
        # Nombre del archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"facturas_{tipo}_{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        log_security(f"ERROR | exportar_excel | Tipo: {tipo} | IDs: {facturas_ids} | Error: {str(e)} | Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Error al exportar: {str(e)}"}), 500


# =============================================
# 🗑️ BORRAR FACTURA TEMPORAL (DELETE)
# =============================================
@recibir_facturas_bp.route('/borrar_factura_temporal/<int:factura_id>', methods=['DELETE'])
@requiere_permiso('recibir_facturas', 'eliminar_factura')  # 🔐 VALIDAR PERMISO
def borrar_factura_temporal(factura_id):
    """
    Borra una factura temporal específica por ID
    
    Args:
        factura_id (int): ID de la factura a borrar
    
    Returns:
        JSON: {"success": True, "message": "..."}
    """
    try:
        # Buscar la factura
        factura = FacturaTemporal.query.get(factura_id)
        
        if not factura:
            return jsonify({"error": "Factura no encontrada"}), 404
        
        # Guardar info para logging
        nit = factura.nit
        prefijo = factura.prefijo or ''
        folio = factura.folio
        
        # 🔄 ELIMINAR SINCRONIZACIÓN SI ORIGEN ES TEMPORAL
        try:
            exito, mensaje = eliminar_factura_temporal(
                nit=nit,
                prefijo=prefijo,
                folio=folio
            )
            
            if exito:
                log_security(
                    f"SINCRONIZACIÓN ELIMINADA | NIT={nit} | PREFIJO={prefijo} | "
                    f"FOLIO={folio} | motivo=factura_temporal_borrada | {mensaje}"
                )
        except Exception as e_sync:
            # No fallar la transacción si la sincronización falla
            log_security(f"ERROR AL ELIMINAR SINCRONIZACIÓN | {str(e_sync)} | NIT={nit}")
        
        # Borrar
        db.session.delete(factura)
        db.session.commit()
        
        # Log de auditoría
        usuario = session.get('usuario', 'DESCONOCIDO')
        nit_sesion = session.get('nit', 'DESCONOCIDO')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        log_security(
            f"FACTURA BORRADA | usuario={usuario} | nit={nit_sesion} | ip={ip} | "
            f"factura_id={factura_id} | nit_emisor={nit} | prefijo={prefijo} | folio={folio}"
        )
        
        return jsonify({
            "success": True,
            "message": f"Factura {prefijo}{folio} borrada exitosamente"
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al borrar factura: {str(e)}"}), 500


# =============================================
# ✏️ ACTUALIZAR FACTURA TEMPORAL (PUT)
# =============================================
@recibir_facturas_bp.route('/actualizar_factura_temporal/<int:factura_id>', methods=['PUT'])
@requiere_permiso('recibir_facturas', 'editar_factura')  # 🔐 VALIDAR PERMISO
def actualizar_factura_temporal(factura_id):
    """
    Actualiza una factura temporal existente
    
    Args:
        factura_id (int): ID de la factura a actualizar
    
    Returns:
        JSON: {"success": True, "factura": {...}}
    """
    try:
        # Buscar la factura
        factura = FacturaTemporal.query.get(factura_id)
        
        if not factura:
            return jsonify({"error": "Factura no encontrada"}), 404
        
        # Obtener datos del request
        data = request.get_json()
        
        # Validar clave única (excluyendo la factura actual)
        nit = data.get('nit')
        prefijo = data.get('prefijo', '')
        folio = data.get('folio')
        
        existe_temporal, _ = FacturaTemporal.validar_clave_unica(
            nit, prefijo, folio, 
            excluir_id=factura_id  # ⚠️ CRÍTICO: Excluir factura actual de validación
        )
        
        if existe_temporal:
            return jsonify({
                "error": f"La factura {prefijo}{folio} del NIT {nit} ya existe en la lista temporal"
            }), 400
        
        # Verificar en facturas recibidas
        existe_recibida, fecha_radicacion = FacturaRecibida.validar_clave_unica(nit, prefijo, folio)
        
        if existe_recibida:
            return jsonify({
                "error": f"La factura {prefijo}{folio} del NIT {nit} ya fue recibida el {fecha_radicacion}"
            }), 400
        
        # Actualizar campos
        factura.nit = nit
        factura.razon_social = data.get('razon_social')
        factura.prefijo = prefijo
        factura.folio = folio
        factura.centro_operacion_id = data.get('centro_operacion_id')
        factura.fecha_expedicion = data.get('fecha_expedicion')
        factura.fecha_radicacion = data.get('fecha_radicacion')
        factura.fecha_vencimiento = data.get('fecha_vencimiento')
        factura.valor_bruto = data.get('valor_bruto')
        factura.descuento = data.get('descuento', 0)
        factura.iva = data.get('iva', 0)
        factura.retencion_fuente = data.get('retencion_fuente', 0)
        factura.rete_iva = data.get('rete_iva', 0)
        factura.rete_ica = data.get('rete_ica', 0)
        factura.usuario_solicita = data.get('usuario_solicita')
        factura.comprador = data.get('usuario_compra')  # Mapping
        factura.quien_recibe = data.get('usuario_recibe')  # Mapping
        
        # Calcular valor neto
        vb = float(factura.valor_bruto or 0)
        iva = float(factura.iva or 0)
        descuento = float(factura.descuento or 0)
        rf = float(factura.retencion_fuente or 0)
        riva = float(factura.rete_iva or 0)
        rica = float(factura.rete_ica or 0)
        factura.valor_neto = round(vb + iva - descuento - rf - riva - rica, 2)
        
        # Actualizar timestamp
        factura.fecha_modificacion = datetime.now()
        
        # 🔄 ACTUALIZAR SINCRONIZACIÓN SI YA EXISTE EN MAESTRO
        try:
            estado_actual = obtener_estado_actual(nit, prefijo, folio)
            
            if estado_actual and estado_actual.get('origen_sincronizacion') == 'RECIBIR_FACTURAS':
                # Si está en maestro como RECIBIR_FACTURAS, actualizar datos
                usuario_nombre = session.get('usuario', 'DESCONOCIDO')
                exito, mensaje, accion = sincronizar_factura_recibida(
                    nit=nit,
                    prefijo=prefijo,
                    folio=folio,
                    fecha_recibida=factura.fecha_radicacion or datetime.now(),
                    usuario=usuario_nombre,
                    origen='RECIBIR_FACTURAS',
                    razon_social=factura.razon_social
                )
                
                if exito:
                    log_security(
                        f"SINCRONIZACIÓN ACTUALIZADA | edición_temporal | "
                        f"NIT={nit} | PREFIJO={prefijo} | FOLIO={folio}"
                    )
        except Exception as e_sync:
            # No fallar la transacción si la sincronización falla
            log_security(f"ERROR AL ACTUALIZAR SINCRONIZACIÓN | {str(e_sync)} | NIT={nit}")
        
        # ✅ NUEVO: Manejar observaciones CON HISTORIAL (conserva texto anterior)
        observaciones_texto = data.get('observaciones', '').strip()
        if observaciones_texto:
            # ✅ VALIDAR que usuario_id exista en sesión
            from flask import session
            usuario_id = session.get('usuario_id')
            
            if not usuario_id:
                return jsonify({
                    "error": "Sesión inválida. Por favor inicie sesión nuevamente."
                }), 401
            
            # 🔍 Obtener observación anterior (si existe)
            obs_anterior = ObservacionFacturaTemporal.query.filter_by(factura_temporal_id=factura_id).first()
            texto_anterior = obs_anterior.observacion if obs_anterior else ""
            
            # 📝 Crear nueva línea con formato [fecha hora - usuario] mensaje
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            usuario_nombre = session.get('usuario', 'Usuario')
            linea_nueva = f"[{timestamp} - {usuario_nombre}] {observaciones_texto}"
            
            # 📋 Concatenar: nuevo mensaje al inicio + texto anterior (historial completo)
            if texto_anterior:
                texto_combinado = f"{linea_nueva}\n{texto_anterior}"
            else:
                texto_combinado = linea_nueva
            
            # 🗑️ Eliminar observación anterior
            if obs_anterior:
                ObservacionFacturaTemporal.query.filter_by(factura_temporal_id=factura_id).delete()
            
            # ✅ Crear nueva observación con historial completo
            nueva_obs = ObservacionFacturaTemporal(
                factura_temporal_id=factura_id,
                observacion=texto_combinado,  # ✅ Conserva historial
                usuario_id=usuario_id
                # fecha_creacion se auto-llena con DEFAULT CURRENT_TIMESTAMP (agregado en BD)
            )
            db.session.add(nueva_obs)
            log_security(f"OBSERVACION ACTUALIZADA CON HISTORIAL | Factura: {factura.numero_factura} | Usuario: {usuario_nombre} (ID={usuario_id}) | Texto nuevo: {observaciones_texto[:50]}...")
        
        db.session.commit()
        
        # Log de auditoría
        usuario = session.get('usuario', 'DESCONOCIDO')
        nit_sesion = session.get('nit', 'DESCONOCIDO')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        log_security(
            f"FACTURA ACTUALIZADA | usuario={usuario} | nit={nit_sesion} | ip={ip} | "
            f"factura_id={factura_id} | nit_emisor={nit} | prefijo={prefijo} | folio={folio} | "
            f"valor_neto={factura.valor_neto}"
        )
        
        return jsonify({
            "success": True,
            "factura": factura.to_dict(),
            "message": f"Factura {prefijo}{folio} actualizada exitosamente"
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar factura: {str(e)}"}), 500

# =============================================
# 📊 EXPORTAR EXCEL DE FACTURAS TEMPORALES
# =============================================
@recibir_facturas_bp.route('/api/exportar_temporales', methods=['POST'])
@requiere_permiso('recibir_facturas', 'exportar_facturas')  # 🔐 VALIDAR PERMISO
def exportar_temporales():
    """
    Exporta facturas temporales seleccionadas a Excel
    
    Body JSON:
    {
        "ids": [1, 2, 3, ...]  // IDs de facturas a exportar
    }
    
    Returns:
        Archivo Excel con facturas seleccionadas
    """
    valido, respuesta, codigo = validar_sesion()
    if not valido:
        return jsonify(respuesta), codigo
    
    try:
        data = request.get_json()
        ids_seleccionados = data.get('ids', [])
        
        if not ids_seleccionados:
            return jsonify({"error": "No se seleccionaron facturas para exportar"}), 400
        
        # Consultar facturas seleccionadas
        facturas = FacturaTemporal.query.filter(
            FacturaTemporal.id.in_(ids_seleccionados),
            FacturaTemporal.usuario_id == session['usuario_id']  # Solo sus facturas
        ).all()
        
        if not facturas:
            return jsonify({"error": "No se encontraron facturas"}), 404
        
        # Preparar datos para Excel (sin usar to_dict() para evitar InstrumentedAttribute)
        datos = []
        for f in facturas:
            datos.append({
                'NIT': f.nit,
                'Razón Social': f.razon_social,
                'Prefijo': f.prefijo,
                'Folio': f.folio,
                'Número Factura': f.numero_factura,
                'Centro Operación': f.centro_operacion,
                'Fecha Expedición': f.fecha_expedicion,
                'Fecha Radicación': f.fecha_radicacion,
                'Fecha Vencimiento': f.fecha_vencimiento,
                'Valor Bruto': float(f.valor_bruto) if f.valor_bruto else 0,
                'IVA': float(f.iva) if f.iva else 0,
                'Descuento': float(f.descuento) if f.descuento else 0,
                'Retención Fuente': float(f.retencion_fuente) if f.retencion_fuente else 0,
                'Rete IVA': float(f.rete_iva) if f.rete_iva else 0,
                'Rete ICA': float(f.rete_ica) if f.rete_ica else 0,
                'Valor Neto': float(f.valor_neto) if f.valor_neto else 0,
                'Usuario Solicita': f.usuario_solicita,
                'Comprador': f.comprador,
                'Quien Recibe': f.quien_recibe
            })
        
        # Crear DataFrame y Excel en memoria
        df = pd.DataFrame(datos)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Facturas Temporales', index=False)
        
        output.seek(0)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'facturas_temporales_{timestamp}.xlsx'
        
        # Log
        log_security(f"EXCEL EXPORTADO | Usuario: {session.get('usuario')} | Facturas: {len(facturas)} | Archivo: {filename}")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        log_security(f"ERROR EXPORTAR EXCEL | Usuario: {session.get('usuario')} | Error: {str(e)}")
        return jsonify({"error": f"Error al exportar Excel: {str(e)}"}), 500
