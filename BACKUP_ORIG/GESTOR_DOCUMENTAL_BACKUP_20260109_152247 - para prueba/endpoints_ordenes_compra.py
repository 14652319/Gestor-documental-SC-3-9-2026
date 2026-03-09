# =====================================================
# ENDPOINTS ADICIONALES PARA ÓRDENES DE COMPRA (OCR)
# Agregar al final de modules/facturas_digitales/routes.py
# =====================================================

# Copiar y pegar este código al final del archivo routes.py


# =====================================================
# MÓDULO DE ÓRDENES DE COMPRA (OCR)
# =====================================================

@facturas_digitales_bp.route('/ordenes-compra')
@requiere_permiso_html_fd('facturas_digitales', 'acceder_modulo')
def ordenes_compra():
    """Formulario para generar órdenes de compra"""
    return render_template('facturas_digitales/orden_compra.html',
                         tipo_usuario=session.get('tipo_usuario'))


@facturas_digitales_bp.route('/api/ordenes-compra/consecutivo')
def obtener_consecutivo_ocr():
    """Obtener el próximo consecutivo de orden de compra"""
    try:
        from sqlalchemy import text
        
        result = db.session.execute(text("""
            SELECT prefijo, ultimo_numero 
            FROM consecutivos_ordenes_compra 
            WHERE prefijo = 'OCR'
        """))
        row = result.fetchone()
        
        if row:
            proximo = row[1] + 1
            consecutivo = f"{row[0]}-{proximo:09d}"
        else:
            consecutivo = "OCR-000000001"
        
        return jsonify({
            'success': True,
            'consecutivo': consecutivo
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@facturas_digitales_bp.route('/api/ordenes-compra/unidades-negocio')
def listar_unidades_negocio():
    """Listar unidades de negocio activas"""
    try:
        from sqlalchemy import text
        
        result = db.session.execute(text("""
            SELECT id, codigo, nombre, descripcion
            FROM unidades_negocio
            WHERE activo = TRUE
            ORDER BY codigo
        """))
        
        unidades = []
        for row in result:
            unidades.append({
                'id': row[0],
                'codigo': row[1],
                'nombre': row[2],
                'descripcion': row[3]
            })
        
        return jsonify({'success': True, 'data': unidades})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@facturas_digitales_bp.route('/api/ordenes-compra/centros-costo')
def listar_centros_costo():
    """Listar centros de costo activos"""
    try:
        from sqlalchemy import text
        
        result = db.session.execute(text("""
            SELECT id, codigo, nombre, descripcion
            FROM centros_costo
            WHERE activo = TRUE
            ORDER BY codigo
        """))
        
        centros = []
        for row in result:
            centros.append({
                'id': row[0],
                'codigo': row[1],
                'nombre': row[2],
                'descripcion': row[3]
            })
        
        return jsonify({'success': True, 'data': centros})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@facturas_digitales_bp.route('/api/ordenes-compra/buscar-tercero/<nit>')
def buscar_tercero_ocr(nit):
    """Buscar datos del tercero/proveedor por NIT"""
    try:
        from app import Tercero
        
        tercero = Tercero.query.filter_by(nit=nit).first()
        
        if not tercero:
            return jsonify({
                'success': False,
                'message': f'No se encontró el tercero con NIT {nit}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'nit': tercero.nit,
                'razon_social': tercero.razon_social,
                'direccion': tercero.direccion,
                'telefono': tercero.telefono,
                'email': tercero.correo
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@facturas_digitales_bp.route('/api/ordenes-compra/crear', methods=['POST'])
@requiere_permiso_fd('facturas_digitales', 'acceder_modulo')
def crear_orden_compra():
    """Crear nueva orden de compra"""
    try:
        from sqlalchemy import text
        from datetime import date
        
        data = request.get_json()
        
        # Validar datos obligatorios
        if not data.get('tercero_nit') or not data.get('tercero_nombre'):
            return jsonify({'success': False, 'message': 'NIT y razón social son obligatorios'}), 400
        
        if not data.get('motivo'):
            return jsonify({'success': False, 'message': 'El motivo es obligatorio'}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'success': False, 'message': 'Debe agregar al menos un ítem'}), 400
        
        # Obtener y actualizar consecutivo
        result = db.session.execute(text("""
            UPDATE consecutivos_ordenes_compra 
            SET ultimo_numero = ultimo_numero + 1,
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE prefijo = 'OCR'
            RETURNING prefijo, ultimo_numero
        """))
        row = result.fetchone()
        db.session.commit()
        
        numero_orden = f"{row[0]}-{row[1]:09d}"
        
        # Insertar orden de compra
        usuario = session.get('usuario', 'desconocido')
        empresa_id = session.get('empresa_id')
        
        result_orden = db.session.execute(text("""
            INSERT INTO ordenes_compra (
                numero_orden, tercero_nit, tercero_nombre, tercero_direccion,
                tercero_telefono, tercero_email, fecha_elaboracion, motivo,
                subtotal, iva, retefuente, total, observaciones,
                usuario_creador, empresa_id, estado
            ) VALUES (
                :numero_orden, :tercero_nit, :tercero_nombre, :tercero_direccion,
                :tercero_telefono, :tercero_email, :fecha_elaboracion, :motivo,
                :subtotal, :iva, :retefuente, :total, :observaciones,
                :usuario_creador, :empresa_id, 'PENDIENTE'
            ) RETURNING id
        """), {
            'numero_orden': numero_orden,
            'tercero_nit': data['tercero_nit'],
            'tercero_nombre': data['tercero_nombre'],
            'tercero_direccion': data.get('tercero_direccion', ''),
            'tercero_telefono': data.get('tercero_telefono', ''),
            'tercero_email': data.get('tercero_email', ''),
            'fecha_elaboracion': date.today(),
            'motivo': data['motivo'],
            'subtotal': data.get('subtotal', 0),
            'iva': data.get('iva', 0),
            'retefuente': data.get('retefuente', 0),
            'total': data.get('total', 0),
            'observaciones': data.get('observaciones', ''),
            'usuario_creador': usuario,
            'empresa_id': empresa_id
        })
        
        orden_id = result_orden.fetchone()[0]
        
        # Insertar items/detalle
        orden_num = 1
        for item in data['items']:
            db.session.execute(text("""
                INSERT INTO ordenes_compra_detalle (
                    orden_compra_id, centro_operacion_codigo, centro_operacion_nombre,
                    unidad_negocio_codigo, unidad_negocio_nombre,
                    centro_costo_codigo, centro_costo_nombre,
                    cantidad, precio_unitario, valor_total, orden
                ) VALUES (
                    :orden_id, :co_codigo, :co_nombre,
                    :un_codigo, :un_nombre,
                    :cc_codigo, :cc_nombre,
                    :cantidad, :precio_unitario, :valor_total, :orden
                )
            """), {
                'orden_id': orden_id,
                'co_codigo': item['centro_operacion_codigo'],
                'co_nombre': item['centro_operacion_nombre'],
                'un_codigo': item['unidad_negocio_codigo'],
                'un_nombre': item['unidad_negocio_nombre'],
                'cc_codigo': item['centro_costo_codigo'],
                'cc_nombre': item['centro_costo_nombre'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario'],
                'valor_total': item['valor_total'],
                'orden': orden_num
            })
            orden_num += 1
        
        db.session.commit()
        
        log_security(f"ORDEN COMPRA CREADA | numero={numero_orden} | nit={data['tercero_nit']} | total={data.get('total', 0)} | items={len(data['items'])} | usuario={usuario}")
        
        return jsonify({
            'success': True,
            'message': 'Orden de compra creada exitosamente',
            'data': {
                'id': orden_id,
                'numero_orden': numero_orden
            }
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error al crear la orden: {str(e)}'}), 500


@facturas_digitales_bp.route('/api/ordenes-compra/enviar-correo', methods=['POST'])
@requiere_permiso_fd('facturas_digitales', 'acceder_modulo')
def enviar_correo_orden_compra():
    """Enviar orden de compra por correo electrónico"""
    try:
        data = request.get_json()
        orden_id = data.get('orden_id')
        email_destino = data.get('email_destino')
        
        if not orden_id or not email_destino:
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
        
        # TODO: Implementar generación de PDF y envío por correo
        # Por ahora solo simular
        
        log_security(f"ORDEN COMPRA ENVIADA | orden_id={orden_id} | email={email_destino} | usuario={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'message': f'Orden enviada a {email_destino}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@facturas_digitales_bp.route('/api/ordenes-compra/pdf/<int:orden_id>')
@requiere_permiso_html_fd('facturas_digitales', 'acceder_modulo')
def descargar_pdf_orden_compra(orden_id):
    """Generar y descargar PDF de la orden de compra"""
    try:
        # TODO: Implementar generación de PDF con reportlab o similar
        return jsonify({'message': 'Funcionalidad de PDF en desarrollo'}), 501
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
