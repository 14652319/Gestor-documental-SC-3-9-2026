"""
ENDPOINTS ADICIONALES para Recibir Facturas Mejorado
Agregar estos endpoints al archivo routes.py existente
Fecha: 18 de Octubre 2025
"""

# ======================================================
# 🏢 ENDPOINT: LISTAR CENTROS DE OPERACIÓN
# ======================================================

@recibir_facturas_bp.route('/centros-operacion', methods=['GET'])
def listar_centros_operacion():
    """
    📋 Listar todos los centros de operación activos
    
    Query params:
    - incluir_inactivos: true/false (default: false)
    
    Response:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "codigo": "01",
                "nombre": "PRINCIPAL",
                "descripcion": "Centro de operación principal",
                "activo": true
            }
        ]
    }
    """
    try:
        # Importar CentroOperacion desde models
        from modules.recibir_facturas.models import CentroOperacion
        
        incluir_inactivos = request.args.get('incluir_inactivos', 'false').lower() == 'true'
        
        query = CentroOperacion.query
        if not incluir_inactivos:
            query = query.filter_by(activo=True)
        
        centros = query.order_by(CentroOperacion.codigo).all()
        
        return jsonify({
            'success': True,
            'data': [co.to_dict() for co in centros]
        }), 200
        
    except Exception as e:
        log_security(f"ERROR LISTAR C.O. | error={str(e)} | IP={obtener_ip()}")
        return jsonify({'success': False, 'message': f'Error al listar centros de operación: {str(e)}'}), 500


# ======================================================
# 🔍 ENDPOINT: BUSCAR PROVEEDORES (AUTOCOMPLETADO)
# ======================================================

@recibir_facturas_bp.route('/proveedores', methods=['GET'])
def buscar_proveedores():
    """
    🔎 Buscar proveedores por NIT o razón social (para autocompletado)
    
    Query params:
    - buscar: texto a buscar (mínimo 3 caracteres)
    - limite: cantidad máxima de resultados (default: 20)
    
    Response:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "nit": "900123456-7",
                "razon_social": "PROVEEDOR ABC SAS"
            }
        ]
    }
    """
    try:
        from app import Tercero
        
        buscar = request.args.get('buscar', '').strip()
        limite = int(request.args.get('limite', 20))
        
        if len(buscar) < 3:
            return jsonify({
                'success': False,
                'message': 'Debe ingresar al menos 3 caracteres para buscar'
            }), 400
        
        # Buscar por NIT o razón social (case-insensitive)
        query = Tercero.query.filter(
            db.or_(
                Tercero.nit.ilike(f'%{buscar}%'),
                Tercero.razon_social.ilike(f'%{buscar}%')
            )
        ).limit(limite)
        
        terceros = query.all()
        
        resultados = [{
            'id': t.id,
            'nit': t.nit,
            'razon_social': t.razon_social
        } for t in terceros]
        
        return jsonify({
            'success': True,
            'data': resultados
        }), 200
        
    except Exception as e:
        log_security(f"ERROR BUSCAR PROVEEDORES | buscar={buscar} | error={str(e)} | IP={obtener_ip()}")
        return jsonify({'success': False, 'message': f'Error al buscar proveedores: {str(e)}'}), 500


# ======================================================
# ✏️ ENDPOINT: EDITAR FACTURA (PARCIAL)
# ======================================================

@recibir_facturas_bp.route('/<int:factura_id>', methods=['PATCH'])
def editar_factura_parcial(factura_id):
    """
    ✏️ Editar factura (actualización parcial)
    
    NOTA: NIT y razon_social NO se pueden modificar
    
    Body JSON (solo campos a modificar):
    {
        "prefijo": "FACT",
        "folio": "2025-001",
        "fecha_factura": "2025-10-18",
        "fecha_vencimiento": "2025-11-17",
        "valor_bruto": 1200000.00,
        "valor_iva": 228000.00,
        "valor_neto": 1428000.00,
        "comprador": "Juan Pérez",
        "usuario_solicita": "María González",
        "quien_recibe": "Pedro Ramírez",
        "centro_operacion_id": 2,
        "observaciones": "Actualización de valores"
    }
    """
    try:
        factura = Factura.query.get(factura_id)
        if not factura:
            return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
        
        data = request.get_json()
        
        # Campos que NO se pueden modificar
        campos_bloqueados = ['nit', 'razon_social', 'tercero_id', 'numero_factura']
        for campo in campos_bloqueados:
            if campo in data:
                return jsonify({
                    'success': False,
                    'message': f'El campo {campo} no se puede modificar'
                }), 400
        
        # Actualizar campos permitidos
        if 'prefijo' in data:
            factura.prefijo = data['prefijo']
        if 'folio' in data:
            factura.folio = data['folio']
        if 'fecha_factura' in data:
            factura.fecha_factura = datetime.strptime(data['fecha_factura'], '%Y-%m-%d').date()
        if 'fecha_vencimiento' in data:
            if data['fecha_vencimiento']:
                factura.fecha_vencimiento = datetime.strptime(data['fecha_vencimiento'], '%Y-%m-%d').date()
            else:
                factura.fecha_vencimiento = None
        if 'fecha_radicacion' in data:
            factura.fecha_radicacion = datetime.strptime(data['fecha_radicacion'], '%Y-%m-%d').date()
        if 'valor_bruto' in data:
            factura.valor_bruto = Decimal(str(data['valor_bruto']))
        if 'valor_iva' in data:
            factura.valor_iva = Decimal(str(data['valor_iva']))
        if 'valor_neto' in data:
            factura.valor_neto = Decimal(str(data['valor_neto']))
        if 'comprador' in data:
            factura.comprador = data['comprador']
        if 'usuario_solicita' in data:
            factura.usuario_solicita = data['usuario_solicita']
        if 'quien_recibe' in data:
            factura.quien_recibe = data['quien_recibe']
        if 'centro_operacion_id' in data:
            factura.centro_operacion_id = data['centro_operacion_id']
        if 'observaciones' in data:
            factura.observaciones = data['observaciones']
        
        db.session.commit()
        
        log_security(f"FACTURA EDITADA | id={factura_id} | numero={factura.numero_factura} | IP={obtener_ip()}")
        
        return jsonify({
            'success': True,
            'message': 'Factura actualizada exitosamente',
            'data': factura.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR EDITAR FACTURA | id={factura_id} | error={str(e)} | IP={obtener_ip()}")
        return jsonify({'success': False, 'message': f'Error al editar factura: {str(e)}'}), 500


# ======================================================
# 🗑️ ENDPOINT: ELIMINAR FACTURA
# ======================================================

@recibir_facturas_bp.route('/<int:factura_id>', methods=['DELETE'])
def eliminar_factura(factura_id):
    """
    🗑️ Eliminar factura
    
    Response:
    {
        "success": true,
        "message": "Factura eliminada exitosamente"
    }
    """
    try:
        factura = Factura.query.get(factura_id)
        if not factura:
            return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
        
        numero_factura = factura.numero_factura
        
        # Eliminar factura (las relaciones se eliminan por CASCADE)
        db.session.delete(factura)
        db.session.commit()
        
        log_security(f"FACTURA ELIMINADA | id={factura_id} | numero={numero_factura} | IP={obtener_ip()}")
        
        return jsonify({
            'success': True,
            'message': 'Factura eliminada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR ELIMINAR FACTURA | id={factura_id} | error={str(e)} | IP={obtener_ip()}")
        return jsonify({'success': False, 'message': f'Error al eliminar factura: {str(e)}'}), 500


# ======================================================
# 📊 ENDPOINT: ESTADÍSTICAS (USANDO FUNCIÓN SQL)
# ======================================================

@recibir_facturas_bp.route('/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """
    📊 Obtener estadísticas de facturas usando función SQL optimizada
    
    Response:
    {
        "success": true,
        "data": {
            "pendientes": 15,
            "proximas_vencer": 3,
            "vencidas": 2,
            "monto_pendiente": 5420000.00
        }
    }
    """
    try:
        # Ejecutar función SQL
        result = db.session.execute(db.text("SELECT * FROM obtener_estadisticas_facturas()")).fetchone()
        
        estadisticas = {
            'pendientes': result[0] if result else 0,
            'proximas_vencer': result[1] if result else 0,
            'vencidas': result[2] if result else 0,
            'monto_pendiente': float(result[3]) if result else 0.0
        }
        
        return jsonify({
            'success': True,
            'data': estadisticas
        }), 200
        
    except Exception as e:
        log_security(f"ERROR ESTADÍSTICAS | error={str(e)} | IP={obtener_ip()}")
        return jsonify({'success': False, 'message': f'Error al obtener estadísticas: {str(e)}'}), 500


# ======================================================
# NOTA: AGREGAR MODELO CentroOperacion A models.py
# ======================================================

"""
Agregar al archivo modules/recibir_facturas/models.py:

# ✅ CORRECCIÓN (Oct 22, 2025): Importar CentroOperacion desde configuracion
from modules.configuracion.models import CentroOperacion
class Factura(db.Model):
    # ... campos existentes ...
    
    # AGREGAR estos campos:
    prefijo = db.Column(db.String(10))
    folio = db.Column(db.String(50))
    comprador = db.Column(db.String(200))
    usuario_solicita = db.Column(db.String(200))
    quien_recibe = db.Column(db.String(200))
    centro_operacion_id = db.Column(db.Integer, db.ForeignKey('centros_operacion.id'))
    fecha_radicacion = db.Column(db.Date, default=date.today)
    usuario_nombre = db.Column(db.String(200))
    centro_operacion = db.Column(db.String(200))  # Desnormalizado
    
    # AGREGAR relación:
    centro_operacion_obj = db.relationship('CentroOperacion', back_populates='facturas')
"""
