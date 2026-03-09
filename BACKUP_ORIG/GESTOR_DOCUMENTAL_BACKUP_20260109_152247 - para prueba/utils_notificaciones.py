# =============================================
# utils_notificaciones.py
# Funciones de utilidad para envío de notificaciones por correo
# =============================================

from flask_mail import Message
from flask import current_app
import logging

def enviar_notificacion_firma(mail, destinatario, nombre_firmador, departamento, facturas_pendientes):
    """
    Envía correo al firmador con lista de documentos pendientes en su departamento
    
    Args:
        mail: Instancia de Flask-Mail
        destinatario: Email del firmador
        nombre_firmador: Nombre completo del firmador
        departamento: Código del departamento (TIC, MER, MYP, DOM, FIN, CYS)
        facturas_pendientes: Lista de diccionarios con datos de facturas
            [{
                'id': 123,
                'numero_factura': 'FE-001234',  # NUEVO: campo único
                'proveedor': 'PROVEEDOR S.A.',
                'valor': 1500000.00,
                'fecha_expedicion': '2025-01-15'
            }, ...]
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Verificar configuración de correo
        if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
            logging.warning(f"Correo no configurado. No se envió notificación a {destinatario}")
            return (False, "Correo no configurado en el servidor")
        
        # Mapeo de departamentos
        departamentos_nombres = {
            'CYS': 'Compras y Suministros',
            'DOM': 'Domicilios',
            'FIN': 'Financiero',
            'MER': 'Mercadeo',
            'MYP': 'Mercadeo Estratégico',
            'TIC': 'Tecnología de la Información'
        }
        nombre_departamento = departamentos_nombres.get(departamento, departamento)
        
        cantidad_docs = len(facturas_pendientes)
        
        # Generar filas de la tabla de facturas
        filas_facturas = ""
        for factura in facturas_pendientes:
            valor_formateado = f"${factura['valor']:,.2f}"
            # CORREGIDO: usar numero_factura en lugar de prefijo-folio
            numero = factura.get('numero_factura', f"{factura.get('prefijo', '')}-{factura.get('folio', '')}")
            filas_facturas += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{numero}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{factura['proveedor']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: right;">{valor_formateado}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">{factura['fecha_expedicion']}</td>
            </tr>
            """
        
        # HTML del correo
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Documentos Pendientes de Firma</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px;">
            <div style="max-width: 800px; margin: 0 auto; background-color: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden;">
                
                <!-- Encabezado -->
                <div style="background: linear-gradient(145deg, #16a34a, #15803d); color: white; padding: 30px; text-align: center;">
                    <div style="font-size: 3em; margin-bottom: 10px;">📝</div>
                    <h1 style="margin: 0; font-size: 1.8em;">Documentos Pendientes de Firma</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Sistema de Gestión Documental</p>
                </div>
                
                <!-- Contenido -->
                <div style="padding: 30px;">
                    <!-- Saludo -->
                    <div style="margin-bottom: 25px;">
                        <p style="font-size: 1.1em; color: #374151; margin: 0;">Hola <strong>{nombre_firmador}</strong>,</p>
                    </div>
                    
                    <!-- Alert Box -->
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin-bottom: 25px; border-radius: 6px;">
                        <p style="margin: 0; color: #92400e; font-size: 1.05em;">
                            <strong>⚠️ Tienes {cantidad_docs} documento{'s' if cantidad_docs != 1 else ''} pendiente{'s' if cantidad_docs != 1 else ''} de firma</strong><br>
                            Departamento: <strong>{nombre_departamento} ({departamento})</strong>
                        </p>
                    </div>
                    
                    <!-- Tabla de Documentos -->
                    <div style="margin-bottom: 30px;">
                        <h3 style="color: #16a34a; margin-bottom: 15px;">📋 Listado de Documentos:</h3>
                        <table style="width: 100%; border-collapse: collapse; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background-color: #f9fafb;">
                                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb; color: #374151; font-weight: 600;">Número Factura</th>
                                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb; color: #374151; font-weight: 600;">Proveedor</th>
                                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #e5e7eb; color: #374151; font-weight: 600;">Valor</th>
                                    <th style="padding: 12px; text-align: center; border-bottom: 2px solid #e5e7eb; color: #374151; font-weight: 600;">Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_facturas}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Instrucciones -->
                    <div style="background-color: #f0fdf4; border: 2px solid #22c55e; border-radius: 10px; padding: 20px; margin-bottom: 25px;">
                        <h3 style="color: #16a34a; margin-top: 0;">📌 Próximos Pasos:</h3>
                        <ol style="color: #374151; line-height: 1.8; margin: 0; padding-left: 20px;">
                            <li>Ingresa al sistema de gestión documental usando el botón de abajo</li>
                            <li>Navega al módulo de <strong>Facturas Digitales</strong></li>
                            <li>Revisa cada documento pendiente</li>
                            <li>Firma digitalmente los documentos aprobados</li>
                            <li>Si encuentras inconsistencias, regístralas en el sistema</li>
                        </ol>
                    </div>
                    
                    <!-- Botón de Acción -->
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://mtlm3ljz-8099.use2.devtunnels.ms/facturas-digitales/dashboard" 
                           style="display: inline-block; background: linear-gradient(135deg, #16a34a, #22c55e); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 1.1em; box-shadow: 0 4px 15px rgba(22, 163, 74, 0.3);">
                            🔐 Ingresar al Sistema
                        </a>
                    </div>
                    
                    <!-- Nota Importante -->
                    <div style="background-color: #f9fafb; border-left: 4px solid #6b7280; padding: 15px; border-radius: 6px; margin-top: 25px;">
                        <p style="margin: 0; color: #4b5563; font-size: 0.9em;">
                            <strong>💡 Nota:</strong> Este correo es una notificación automática del sistema. Los documentos deben ser firmados dentro de los plazos establecidos por la política de la empresa.
                        </p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; color: #6b7280; font-size: 0.9em;">
                        <strong>Gestor Documental - Supertiendas Cañaveral</strong><br>
                        Este es un mensaje automático, por favor no responder.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Texto plano alternativo
        texto_plano = f"""
DOCUMENTOS PENDIENTES DE FIRMA

Hola {nombre_firmador},

Tienes {cantidad_docs} documento{'s' if cantidad_docs != 1 else ''} pendiente{'s' if cantidad_docs != 1 else ''} de firma en el departamento de {nombre_departamento} ({departamento}).

LISTADO DE DOCUMENTOS:
"""
        for i, factura in enumerate(facturas_pendientes, 1):
            valor_formateado = f"${factura['valor']:,.2f}"
            # CORREGIDO: usar numero_factura en lugar de prefijo-folio
            numero = factura.get('numero_factura', f"{factura.get('prefijo', '')}-{factura.get('folio', '')}")
            texto_plano += f"\n{i}. {numero} | {factura['proveedor']} | {valor_formateado} | {factura['fecha_expedicion']}"
        
        texto_plano += f"""

PRÓXIMOS PASOS:
1. Ingresa al sistema de gestión documental
2. Navega al módulo de Facturas Digitales
3. Revisa cada documento pendiente
4. Firma digitalmente los documentos aprobados

Acceso al sistema: https://mtlm3ljz-8099.use2.devtunnels.ms/facturas-digitales/dashboard

---
Gestor Documental - Supertiendas Cañaveral
Este es un mensaje automático, por favor no responder.
        """
        
        # Crear y enviar mensaje
        msg = Message(
            subject=f'📝 {cantidad_docs} Documento{"s" if cantidad_docs != 1 else ""} Pendiente{"s" if cantidad_docs != 1 else ""} de Firma - {departamento}',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[destinatario]
        )
        
        # Configurar Reply-To si está disponible
        if current_app.config.get('MAIL_REPLY_TO'):
            msg.reply_to = current_app.config['MAIL_REPLY_TO']
        
        msg.body = texto_plano
        msg.html = html_body
        
        mail.send(msg)
        
        logging.info(f"Notificación de firma enviada a {destinatario} | Departamento: {departamento} | Cantidad: {cantidad_docs}")
        return (True, f"Notificación enviada exitosamente a {destinatario}")
        
    except Exception as e:
        error_msg = f"Error al enviar notificación: {str(e)}"
        logging.error(f"Error enviando notificación a {destinatario}: {error_msg}")
        return (False, error_msg)
