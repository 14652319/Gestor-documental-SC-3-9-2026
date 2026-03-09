"""
Aplicar permisos ÚNICOS sin duplicados
"""
from sqlalchemy import text
from app import app, db

# Definir permisos únicos por módulo
PERMISOS_NUEVOS = {
    'archivo_digital': [
        ('editar', 'Editar documentos en archivo digital', 'escritura', False),
    ],
    'causaciones': [
        ('eliminar', 'Eliminar documentos de causaciones', 'escritura', True),
        ('exportar', 'Exportar datos de causaciones', 'lectura', False),
        ('ver', 'Ver detalles de documentos', 'lectura', False),
        ('renombrar', 'Renombrar documentos', 'escritura', False),
        ('metadata', 'Ver metadata de documentos', 'lectura', False),
    ],
    'configuracion': [
        ('crear', 'Crear registros en configuración', 'escritura', False),
        ('editar', 'Editar registros en configuración', 'escritura', False),
        ('listar', 'Listar registros de configuración', 'lectura', False),
        ('toggle', 'Activar/desactivar registros', 'escritura', False),
        ('opciones', 'Obtener opciones de catálogos', 'lectura', False),
    ],
    'core': [
        ('login', 'Iniciar sesión en el sistema', 'escritura', True),
        ('logout', 'Cerrar sesión', 'escritura', False),
        ('recuperar_password', 'Recuperar contraseña olvidada', 'escritura', False),
        ('cambiar_password', 'Cambiar contraseña', 'escritura', True),
        ('registrar_proveedor', 'Registrar nuevo proveedor', 'escritura', False),
        ('cargar_documentos', 'Cargar documentos de proveedor', 'escritura', False),
        ('finalizar_registro', 'Finalizar proceso de registro', 'escritura', True),
        ('consultar_radicado', 'Consultar estado de radicado', 'lectura', False),
        ('administrar_usuarios', 'Administrar usuarios del sistema', 'escritura', True),
        ('listar_usuarios', 'Listar usuarios del sistema', 'lectura', False),
        ('activar_usuario', 'Activar/desactivar usuarios', 'escritura', True),
    ],
    'dian_vs_erp': [
        ('subir_archivos', 'Subir archivos para comparación', 'escritura', False),
        ('forzar_procesar', 'Forzar procesamiento de archivos', 'escritura', True),
        ('descargar_plantilla', 'Descargar plantillas', 'lectura', False),
        ('enviar_emails', 'Enviar correos con facturas', 'escritura', False),
        ('enviar_email_agrupado', 'Enviar correos agrupados', 'escritura', False),
        ('ver_estadisticas', 'Ver estadísticas de envíos', 'lectura', False),
        ('configurar_smtp', 'Configurar servidor SMTP', 'escritura', True),
        ('gestionar_usuarios_dian', 'Gestionar usuarios DIAN', 'escritura', True),
    ],
    'facturas_digitales': [
        ('crear_factura', 'Crear nueva factura digital', 'escritura', False),
        ('editar_factura', 'Editar factura digital', 'escritura', False),
        ('eliminar_factura', 'Eliminar factura digital', 'escritura', True),
        ('buscar_tercero', 'Buscar información de tercero', 'lectura', False),
        ('cargar_factura', 'Cargar factura desde PDF', 'escritura', False),
        ('actualizar_estado', 'Actualizar estado de factura', 'escritura', False),
        ('abrir_adobe', 'Enviar a Adobe Sign', 'escritura', False),
        ('descargar_pdf', 'Descargar PDF de factura', 'lectura', False),
        ('enviar_correo', 'Enviar factura por correo', 'escritura', False),
    ],
    'gestion_usuarios': [
        ('crear_usuario', 'Crear nuevo usuario', 'escritura', True),
        ('editar_usuario', 'Editar información de usuario', 'escritura', True),
        ('eliminar_usuario', 'Eliminar usuario', 'escritura', True),
        ('cambiar_estado_usuario', 'Cambiar estado de usuario', 'escritura', True),
        ('gestionar_permisos', 'Gestionar permisos de usuario', 'escritura', True),
        ('enviar_invitacion', 'Enviar invitación a usuario', 'escritura', False),
        ('validar_invitacion', 'Validar token de invitación', 'lectura', False),
        ('activar_invitacion', 'Activar usuario por invitación', 'escritura', False),
        ('ver_auditoria', 'Ver auditoría de cambios', 'lectura', False),
        ('ver_roles', 'Ver roles del sistema', 'lectura', False),
        ('validar_nit', 'Validar NIT de tercero', 'lectura', False),
        ('ver_estadisticas', 'Ver estadísticas de usuarios', 'lectura', False),
    ],
    'monitoreo': [
        ('ver_stats', 'Ver estadísticas del sistema', 'lectura', False),
        ('ver_usuarios_tiempo_real', 'Ver usuarios en tiempo real', 'lectura', False),
        ('ver_ips_tiempo_real', 'Ver IPs en tiempo real', 'lectura', False),
        ('ver_disk_usage', 'Ver uso de disco', 'lectura', False),
        ('ver_alertas', 'Ver alertas del sistema', 'lectura', False),
        ('crear_alerta', 'Crear nueva alerta', 'escritura', False),
        ('ver_logs_archivos', 'Ver archivos de logs', 'lectura', False),
        ('ver_logs_seguridad', 'Ver logs de seguridad', 'lectura', True),
        ('gestionar_ips', 'Gestionar IPs (bloquear/desbloquear)', 'escritura', True),
        ('ver_metricas_sistema', 'Ver métricas del sistema', 'lectura', False),
        ('ver_geolocalizacion', 'Ver geolocalización de IPs', 'lectura', False),
        ('ver_analytics', 'Ver analytics en tiempo real', 'lectura', False),
        ('detectar_amenazas', 'Detectar amenazas de seguridad', 'lectura', True),
        ('gestionar_backups', 'Gestionar backups del sistema', 'escritura', True),
        ('ejecutar_backup', 'Ejecutar backup manual', 'escritura', True),
        ('ver_estado_backup', 'Ver estado de backups', 'lectura', False),
        ('configurar_backup', 'Configurar sistema de backup', 'escritura', True),
    ],
    'notas_contables': [
        ('cargar_nota', 'Cargar nota contable', 'escritura', False),
        ('validar_nota', 'Validar nota contable', 'escritura', False),
        ('editar_nota', 'Editar nota contable', 'escritura', False),
        ('eliminar_nota', 'Eliminar nota contable', 'escritura', True),
        ('solicitar_correccion', 'Solicitar corrección de nota', 'escritura', False),
        ('agregar_adjuntos', 'Agregar archivos adjuntos', 'escritura', False),
        ('descargar_adjunto', 'Descargar archivo adjunto', 'lectura', False),
        ('visualizar_adjunto', 'Visualizar archivo adjunto', 'lectura', False),
        ('ver_historial', 'Ver historial de cambios', 'lectura', False),
        ('ver_detalle', 'Ver detalle de nota', 'lectura', False),
    ],
    'recibir_facturas': [
        ('adicionar_factura', 'Adicionar nueva factura', 'escritura', False),
        ('actualizar_factura_temporal', 'Actualizar factura temporal', 'escritura', False),
        ('eliminar_factura_temporal', 'Eliminar factura temporal', 'escritura', False),
        ('actualizar_temporales', 'Actualizar múltiples facturas temporales', 'escritura', False),
        ('agregar_observacion', 'Agregar observación a factura', 'escritura', False),
    ],
    'relaciones': [
        ('confirmar_recepcion', 'Confirmar recepción de relación', 'escritura', False),
        ('solicitar_token_firma', 'Solicitar token de firma digital', 'escritura', False),
        ('validar_token_firmar', 'Validar token y firmar', 'escritura', True),
        ('consultar_recepcion', 'Consultar estado de recepción', 'lectura', False),
        ('ver_historial_recepciones', 'Ver historial de recepciones', 'lectura', False),
        ('confirmar_retiro_firma', 'Confirmar retiro con firma', 'escritura', True),
    ],
    'terceros': [
        ('crear_tercero', 'Crear nuevo tercero', 'escritura', False),
        ('editar_tercero', 'Editar información de tercero', 'escritura', False),
        ('cambiar_estado_tercero', 'Cambiar estado de tercero', 'escritura', True),
        ('obtener_tercero', 'Obtener información de tercero', 'lectura', False),
        ('listar_terceros', 'Listar terceros', 'lectura', False),
        ('ver_documentos_tercero', 'Ver documentos de tercero', 'lectura', False),
        ('ver_estadisticas_terceros', 'Ver estadísticas de terceros', 'lectura', False),
    ],
}

def aplicar_permisos_unicos():
    with app.app_context():
        print("\n" + "="*80)
        print("🔐 APLICANDO PERMISOS ÚNICOS AL CATÁLOGO")
        print("="*80)
        
        insertados = 0
        duplicados = 0
        errores = 0
        
        for modulo, permisos in PERMISOS_NUEVOS.items():
            print(f"\n📂 Procesando módulo: {modulo.upper()}")
            
            modulo_nombre = modulo.replace('_', ' ').title()
            
            for accion, descripcion, tipo_accion, es_critico in permisos:
                try:
                    query = text("""
                        INSERT INTO catalogo_permisos 
                        (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
                        VALUES 
                        (:modulo, :modulo_nombre, :modulo_desc, :accion, :descripcion, :tipo_accion, :es_critico, true, NOW())
                        ON CONFLICT (modulo, accion) DO NOTHING
                        RETURNING id
                    """)
                    
                    result = db.session.execute(query, {
                        'modulo': modulo,
                        'modulo_nombre': modulo_nombre,
                        'modulo_desc': f'Módulo {modulo_nombre}',
                        'accion': accion,
                        'descripcion': descripcion,
                        'tipo_accion': tipo_accion,
                        'es_critico': es_critico
                    })
                    
                    if result.rowcount > 0:
                        insertados += 1
                        print(f"   ✅ {accion}")
                    else:
                        duplicados += 1
                        print(f"   ⚠️ {accion} (ya existe)")
                    
                    db.session.commit()
                    
                except Exception as e:
                    errores += 1
                    print(f"   ❌ {accion}: {str(e)[:100]}")
                    db.session.rollback()
        
        print("\n" + "="*80)
        print("✅ PROCESO COMPLETADO")
        print("="*80)
        print(f"\n📊 RESUMEN:")
        print(f"   - Permisos insertados: {insertados}")
        print(f"   - Permisos duplicados: {duplicados}")
        print(f"   - Errores: {errores}")
        
        # Contar total final
        result = db.session.execute(text("SELECT COUNT(*) FROM catalogo_permisos WHERE activo = true"))
        total = result.scalar()
        print(f"\n✅ TOTAL DE PERMISOS EN CATÁLOGO: {total}")
        
        # Mostrar distribución por módulo
        print("\n📋 DISTRIBUCIÓN POR MÓDULO:")
        query = text("""
            SELECT modulo, COUNT(*) as total
            FROM catalogo_permisos
            WHERE activo = true
            GROUP BY modulo
            ORDER BY modulo
        """)
        result = db.session.execute(query)
        for row in result:
            print(f"   - {row[0]}: {row[1]} permisos")

if __name__ == "__main__":
    aplicar_permisos_unicos()
