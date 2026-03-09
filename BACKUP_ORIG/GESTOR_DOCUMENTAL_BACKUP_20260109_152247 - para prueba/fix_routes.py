"""
Script para reemplazar la función solicitar_correccion_documento corrupta
"""

import re

# Leer archivo
with open('modules/notas_contables/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Función nueva (simplificada y funcional)
nueva_funcion = """@notas_bp.route('/solicitar-correccion/<int:documento_id>', methods=['POST'])
@requiere_permiso('notas_contables', 'solicitar_correccion_documento')
def solicitar_correccion_documento(documento_id):
    \"\"\"Solicita corrección con envío de token por correo\"\"\"
    from modules.notas_contables.models import TokenCorreccionDocumento
    from sqlalchemy import text
    from flask_mail import Message
    import random
    from datetime import timedelta
    
    try:
        # 1. Verificar sesión
        if 'usuario' not in session:
            return jsonify({'success': False, 'message': 'Sesión no válida'}), 401
        
        usuario = session.get('usuario')
        print(f"\\n🔄 Solicitud de corrección - Usuario: {usuario}, Doc: {documento_id}")
        
        # 2. Obtener documento
        documento = DocumentoContable.query.get(documento_id)
        if not documento:
            return jsonify({'success': False, 'message': 'Documento no encontrado'}), 404
        
        # 3. Obtener datos
        data = request.get_json()
        justificacion = data.get('justificacion', '').strip()
        
        if len(justificacion) < 10:
            return jsonify({
                'success': False,
                'message': 'La justificación debe tener al menos 10 caracteres'
            }), 400
        
        # 4. Generar token
        token = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        print(f"🔑 Token generado: {token}")
        
        # 5. Buscar correo del usuario
        correo = None
        try:
            result = db.session.execute(
                text("SELECT correo FROM usuarios WHERE usuario = :u LIMIT 1"),
                {"u": usuario}
            ).fetchone()
            if result and result[0]:
                correo = result[0]
                print(f"📧 Correo encontrado: {correo}")
        except Exception as e:
            print(f"⚠️ Error buscando correo: {e}")
        
        if not correo:
            print(f"❌ No se encontró correo para {usuario}")
            correo = "sin-correo@ejemplo.com"
        
        # 6. Crear registro de token
        fecha_creacion = obtener_fecha_naive_colombia()
        fecha_expiracion = fecha_creacion + timedelta(minutes=10)
        
        token_correccion = TokenCorreccionDocumento(
            token=token,
            documento_id=documento_id,
            empresa_anterior=documento.empresa,
            empresa_nueva=data.get('empresa_nueva_sigla', documento.empresa),
            tipo_documento_anterior_id=documento.tipo_documento_id,
            tipo_documento_nuevo_id=data.get('tipo_nuevo_id', documento.tipo_documento_id),
            centro_operacion_anterior_id=documento.centro_operacion_id,
            centro_operacion_nuevo_id=data.get('centro_nuevo_id', documento.centro_operacion_id),
            consecutivo_anterior=documento.consecutivo,
            consecutivo_nuevo=data.get('consecutivo_nuevo', documento.consecutivo),
            fecha_documento_anterior=documento.fecha_documento,
            fecha_documento_nueva=documento.fecha_documento,
            justificacion=justificacion,
            fecha_creacion=fecha_creacion,
            fecha_expiracion=fecha_expiracion,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=usuario
        )
        
        db.session.add(token_correccion)
        db.session.commit()
        print(f"✅ Token guardado en BD (ID: {token_correccion.id})")
        
        # 7. Enviar correo
        correo_enviado = False
        mensaje = ""
        
        try:
            html = f\"\"\"
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #ea580c;">🔄 Código de Corrección</h2>
                <p>Hola <strong>{usuario}</strong>,</p>
                <p>Tu código de verificación es:</p>
                <div style="background: #fff7ed; border: 2px solid #ea580c; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                    <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #ea580c;">{token}</div>
                </div>
                <p><strong>Documento:</strong> {documento.nombre_archivo}</p>
                <p><strong>Justificación:</strong> {justificacion}</p>
                <p style="color: #dc2626;"><strong>⏱ Válido por 10 minutos</strong></p>
            </body>
            </html>
            \"\"\"
            
            msg = Message(
                subject=f"Código de Corrección - {token}",
                recipients=[correo],
                html=html
            )
            
            from app import mail
            mail.send(msg)
            
            correo_enviado = True
            mensaje = f"Código enviado a {correo}"
            print(f"✅ {mensaje}")
            
        except Exception as e:
            correo_enviado = False
            mensaje = f"Código generado (sin envío de correo)"
            print(f"❌ Error enviando correo: {e}")
            print(f"\\n{'='*80}")
            print(f"⚠️ CÓDIGO DE CORRECCIÓN (Correo falló)")
            print(f"{'='*80}")
            print(f"📧 Destino: {correo}")
            print(f"👤 Usuario: {usuario}")
            print(f"📄 Documento: {documento.nombre_archivo}")
            print(f"🔑 TOKEN: {token}")
            print(f"{'='*80}\\n")
        
        # 8. Retornar respuesta
        return jsonify({
            'success': True,
            'message': mensaje,
            'token_id': token_correccion.id,
            'expira_en_minutos': 10,
            'correo_enviado': correo_enviado
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


"""

# Encontrar inicio y fin de función corrupta
inicio = content.find("@notas_bp.route('/solicitar-correccion/<int:documento_id>'")
if inicio == -1:
    print('❌ ERROR: No se encontró la función')
    exit(1)

print(f"✅ Función encontrada en posición {inicio}")

# Encontrar el siguiente @notas_bp.route después de esa función
fin_buscar_desde = inicio + 100
sig_ruta = content.find('@notas_bp.route', fin_buscar_desde)
if sig_ruta == -1:
    print('❌ ERROR: No se encontró siguiente ruta')
    exit(1)

print(f"✅ Siguiente ruta encontrada en posición {sig_ruta}")

# Reemplazar
nuevo_content = content[:inicio] + nueva_funcion + content[sig_ruta:]

# Guardar
with open('modules/notas_contables/routes.py', 'w', encoding='utf-8') as f:
    f.write(nuevo_content)

print('✅ Función reemplazada exitosamente')
print(f"📊 Tamaño original: {len(content)} bytes")
print(f"📊 Tamaño nuevo: {len(nuevo_content)} bytes")
