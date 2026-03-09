"""
Sistema de Notificaciones por Correo - SAGRILAFT
Envía correos a proveedores sobre estados de radicados y alertas de vencimiento
"""
from flask_mail import Message
from datetime import datetime

def enviar_correo_decision_radicado(mail, destinatario, nit, razon_social, radicado, estado, observacion=''):
    """
    Envía correo al proveedor notificando la decisión sobre su radicado
    
    Args:
        mail: Instancia de Flask-Mail
        destinatario: Email del proveedor
        nit: NIT del tercero
        razon_social: Nombre/razón social
        radicado: Número de radicado (ej: RAD-031857)
        estado: 'aprobado', 'rechazado', 'aprobado_condicionado'
        observacion: Motivo/condiciones/observaciones
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Determinar asunto y mensaje según estado
        if estado == 'aprobado':
            asunto = f"✅ Radicado {radicado} APROBADO - Supertiendas Cañaveral"
            titulo_estado = "APROBADO"
            color_estado = "#22c55e"
            icono_estado = "✅"
            mensaje_estado = "Su solicitud de actualización de documentación ha sido APROBADA exitosamente."
        elif estado == 'rechazado':
            asunto = f"❌ Radicado {radicado} RECHAZADO - Supertiendas Cañaveral"
            titulo_estado = "RECHAZADO"
            color_estado = "#ef4444"
            icono_estado = "❌"
            mensaje_estado = "Su solicitud de actualización de documentación ha sido RECHAZADA."
        elif estado == 'aprobado_condicionado':
            asunto = f"⚠️ Radicado {radicado} APROBADO CON CONDICIONES - Supertiendas Cañaveral"
            titulo_estado = "APROBADO CON CONDICIONES"
            color_estado = "#f59e0b"
            icono_estado = "⚠️"
            mensaje_estado = "Su solicitud ha sido APROBADA CON CONDICIONES que debe cumplir."
        else:
            return (False, f"Estado inválido: {estado}")
        
        # HTML del correo
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Decisión Radicado {radicado}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background-color: #f3f4f6;
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 650px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(145deg, {color_estado}, #166534);
                    color: white;
                    padding: 35px;
                    text-align: center;
                }}
                .header-icon {{
                    font-size: 4em;
                    margin-bottom: 10px;
                }}
                .header-title {{
                    font-size: 1.8em;
                    font-weight: bold;
                    margin: 0;
                }}
                .content {{
                    padding: 35px;
                }}
                .radicado-box {{
                    background-color: #f0fdf4;
                    border: 2px solid {color_estado};
                    border-radius: 10px;
                    padding: 20px;
                    margin: 25px 0;
                    text-align: center;
                }}
                .radicado-label {{
                    color: #166534;
                    font-size: 0.95em;
                    margin-bottom: 8px;
                    font-weight: 600;
                }}
                .radicado-number {{
                    color: {color_estado};
                    font-size: 2.2em;
                    font-weight: bold;
                    letter-spacing: 3px;
                    font-family: monospace;
                }}
                .info-box {{
                    background-color: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 6px;
                }}
                .info-title {{
                    font-weight: bold;
                    color: #92400e;
                    margin-bottom: 10px;
                    font-size: 1.1em;
                }}
                .info-text {{
                    color: #451a03;
                    margin: 0;
                    white-space: pre-wrap;
                }}
                .data-row {{
                    display: flex;
                    padding: 12px 0;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .data-label {{
                    font-weight: bold;
                    color: #374151;
                    min-width: 150px;
                }}
                .data-value {{
                    color: #1f2937;
                    flex: 1;
                }}
                .footer {{
                    background-color: #f9fafb;
                    padding: 25px;
                    text-align: center;
                    border-top: 3px solid {color_estado};
                }}
                .footer-title {{
                    font-weight: bold;
                    color: #166534;
                    margin-bottom: 12px;
                    font-size: 1.1em;
                }}
                .footer-contact {{
                    color: #6b7280;
                    font-size: 0.95em;
                    margin: 8px 0;
                }}
                .footer-signature {{
                    margin-top: 20px;
                    padding-top: 15px;
                    border-top: 1px solid #d1d5db;
                }}
                .firma-nombre {{
                    font-weight: bold;
                    color: #166534;
                    margin-bottom: 5px;
                }}
                .firma-cargo {{
                    color: #6b7280;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="header-icon">{icono_estado}</div>
                    <h1 class="header-title">{titulo_estado}</h1>
                </div>
                
                <div class="content">
                    <p style="font-size: 1.05em; margin-top: 0;">
                        Estimado(a) proveedor/acreedor,
                    </p>
                    
                    <p style="font-size: 1.05em;">
                        {mensaje_estado}
                    </p>
                    
                    <div class="radicado-box">
                        <div class="radicado-label">NÚMERO DE RADICADO</div>
                        <div class="radicado-number">{radicado}</div>
                    </div>
                    
                    <div class="data-row">
                        <div class="data-label">NIT:</div>
                        <div class="data-value">{nit}</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">Razón Social:</div>
                        <div class="data-value">{razon_social}</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">Estado:</div>
                        <div class="data-value" style="color: {color_estado}; font-weight: bold;">{titulo_estado}</div>
                    </div>
                    <div class="data-row" style="border-bottom: none;">
                        <div class="data-label">Fecha Decisión:</div>
                        <div class="data-value">{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
                    </div>
"""
        
        # Agregar observación si existe
        if observacion and observacion.strip():
            if estado == 'rechazado':
                titulo_obs = "📋 MOTIVO DEL RECHAZO"
            elif estado == 'aprobado_condicionado':
                titulo_obs = "⚠️ CONDICIONES A CUMPLIR"
            else:
                titulo_obs = "📋 OBSERVACIONES"
            
            html_body += f"""
                    <div class="info-box">
                        <div class="info-title">{titulo_obs}:</div>
                        <p class="info-text">{observacion}</p>
                    </div>
"""
        
        html_body += f"""
                </div>
                
                <div class="footer">
                    <div class="footer-title">Para dudas o consultas:</div>
                    <div class="footer-contact">
                        📞 Celular: 3243196701<br>
                        📧 Email: creacionterceros@supertiendascanaveral.com
                    </div>
                    
                    <div class="footer-signature">
                        <div class="firma-nombre">Silvana Paola Guarnizo Zamudio</div>
                        <div class="firma-cargo">Oficial de Cumplimiento Principal</div>
                        <div class="firma-cargo">Supertiendas Cañaveral</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Texto plano alternativo
        texto_plano = f"""
RADICADO {radicado} - {titulo_estado}

Estimado(a) proveedor/acreedor,

{mensaje_estado}

INFORMACIÓN DEL RADICADO:
- Número de Radicado: {radicado}
- NIT: {nit}
- Razón Social: {razon_social}
- Estado: {titulo_estado}
- Fecha Decisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        
        if observacion and observacion.strip():
            if estado == 'rechazado':
                texto_plano += f"\nMOTIVO DEL RECHAZO:\n{observacion}\n"
            elif estado == 'aprobado_condicionado':
                texto_plano += f"\nCONDICIONES A CUMPLIR:\n{observacion}\n"
            else:
                texto_plano += f"\nOBSERVACIONES:\n{observacion}\n"
        
        texto_plano += """
Para dudas o consultas:
📞 Celular: 3243196701
📧 Email: creacionterceros@supertiendascanaveral.com

Silvana Paola Guarnizo Zamudio
Oficial de Cumplimiento Principal
Supertiendas Cañaveral
"""
        
        # Crear y enviar mensaje
        msg = Message(
            subject=asunto,
            recipients=[destinatario],
            body=texto_plano,
            html=html_body
        )
        
        mail.send(msg)
        
        return (True, f"Correo enviado exitosamente a {destinatario}")
        
    except Exception as e:
        return (False, f"Error enviando correo: {str(e)}")


def enviar_correo_alerta_vencimiento(mail, destinatario, nit, razon_social, radicado, dias_restantes, fecha_vencimiento):
    """
    Envía correo de alerta cuando quedan 20 días para el vencimiento (340 días desde última actualización)
    
    Args:
        mail: Instancia de Flask-Mail
        destinatario: Email del proveedor
        nit: NIT del tercero
        razon_social: Nombre/razón social
        radicado: Último radicado del proveedor
        dias_restantes: Días que quedan para vencer
        fecha_vencimiento: Fecha exacta de vencimiento (360 días)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        asunto = f"🔔 URGENTE: Actualización de Documentación - {dias_restantes} días restantes - Supertiendas Cañaveral"
        
        # HTML del correo
        html_body = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alerta Vencimiento Documentación</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    background-color: #f3f4f6;
                    margin: 0;
                    padding: 20px;
                    line-height: 1.8;
                }}
                .container {{
                    max-width: 750px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(145deg, #ef4444, #dc2626);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header-icon {{
                    font-size: 5em;
                    margin-bottom: 15px;
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0%, 100% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.1); }}
                }}
                .header-title {{
                    font-size: 2em;
                    font-weight: bold;
                    margin: 0;
                    text-transform: uppercase;
                }}
                .content {{
                    padding: 40px;
                }}
                .alert-box {{
                    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                    border: 3px solid #f59e0b;
                    border-radius: 12px;
                    padding: 30px;
                    margin: 25px 0;
                    text-align: center;
                }}
                .alert-title {{
                    color: #92400e;
                    font-size: 1.5em;
                    font-weight: bold;
                    margin-bottom: 15px;
                }}
                .dias-restantes {{
                    color: #dc2626;
                    font-size: 4em;
                    font-weight: bold;
                    margin: 15px 0;
                    font-family: monospace;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                }}
                .fecha-vencimiento {{
                    color: #b91c1c;
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-top: 10px;
                }}
                .comunicado-box {{
                    background-color: #f0f9ff;
                    border: 2px solid #3b82f6;
                    border-radius: 10px;
                    padding: 30px;
                    margin: 30px 0;
                }}
                .comunicado-title {{
                    color: #1e40af;
                    font-size: 1.4em;
                    font-weight: bold;
                    margin-bottom: 20px;
                    text-align: center;
                    text-transform: uppercase;
                }}
                .documentos-lista {{
                    background-color: white;
                    border-left: 4px solid #3b82f6;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .documento-item {{
                    padding: 12px 0;
                    border-bottom: 1px solid #e5e7eb;
                    color: #1f2937;
                }}
                .documento-item:last-child {{
                    border-bottom: none;
                }}
                .documento-numero {{
                    font-weight: bold;
                    color: #1e40af;
                    margin-right: 10px;
                }}
                .warning-box {{
                    background-color: #fee2e2;
                    border-left: 5px solid #dc2626;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 6px;
                }}
                .warning-title {{
                    font-weight: bold;
                    color: #991b1b;
                    font-size: 1.2em;
                    margin-bottom: 10px;
                }}
                .warning-text {{
                    color: #7f1d1d;
                    margin: 10px 0;
                }}
                .data-row {{
                    display: flex;
                    padding: 14px 0;
                    border-bottom: 1px solid #e5e7eb;
                }}
                .data-label {{
                    font-weight: bold;
                    color: #374151;
                    min-width: 180px;
                }}
                .data-value {{
                    color: #1f2937;
                    flex: 1;
                }}
                .footer {{
                    background-color: #f9fafb;
                    padding: 30px;
                    text-align: center;
                    border-top: 3px solid #ef4444;
                }}
                .footer-title {{
                    font-weight: bold;
                    color: #166534;
                    margin-bottom: 15px;
                    font-size: 1.2em;
                }}
                .footer-contact {{
                    color: #6b7280;
                    font-size: 1em;
                    margin: 10px 0;
                }}
                .footer-signature {{
                    margin-top: 25px;
                    padding-top: 20px;
                    border-top: 1px solid #d1d5db;
                }}
                .firma-nombre {{
                    font-weight: bold;
                    color: #166534;
                    font-size: 1.1em;
                    margin-bottom: 5px;
                }}
                .firma-cargo {{
                    color: #6b7280;
                    font-size: 0.95em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="header-icon">🔔</div>
                    <h1 class="header-title">Comunicado Externo Urgente</h1>
                    <p style="margin: 10px 0 0 0; font-size: 1.1em;">Actualización de Documentación e Información</p>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <div class="alert-title">⏰ TIEMPO RESTANTE PARA ACTUALIZACIÓN</div>
                        <div class="dias-restantes">{dias_restantes}</div>
                        <div style="font-size: 1.2em; color: #92400e; font-weight: 600;">DÍAS RESTANTES</div>
                        <div class="fecha-vencimiento">
                            Fecha límite: {fecha_vencimiento.strftime('%d de %B de %Y')}
                        </div>
                    </div>
                    
                    <div class="data-row">
                        <div class="data-label">NIT:</div>
                        <div class="data-value">{nit}</div>
                    </div>
                    <div class="data-row">
                        <div class="data-label">Razón Social:</div>
                        <div class="data-value">{razon_social}</div>
                    </div>
                    <div class="data-row" style="border-bottom: none;">
                        <div class="data-label">Último Radicado:</div>
                        <div class="data-value" style="font-weight: bold; color: #166534;">{radicado}</div>
                    </div>
                    
                    <div class="comunicado-box">
                        <div class="comunicado-title">
                            Comunicado Externo Urgente<br>
                            Actualización Documentación e Información<br>
                            Proveedores y Acreedores
                        </div>
                        
                        <p style="margin: 20px 0; text-align: justify;">
                            <strong>Estimados proveedores y acreedores:</strong>
                        </p>
                        
                        <p style="text-align: justify;">
                            En cumplimiento de las disposiciones legales vigentes relacionadas con el <strong>Sistema de 
                            Autocontrol y Gestión del Riesgo Integral de Lavado de Activos, Financiación del Terrorismo 
                            y Financiación de la Proliferación de Armas de Destrucción Masiva (SAGRILAFT)</strong>, nos 
                            permitimos solicitar de manera <strong style="color: #dc2626;">URGENTE</strong> la actualización 
                            de la siguiente información y documentación requerida por nuestro sistema de cumplimiento:
                        </p>
                        
                        <div class="documentos-lista">
                            <div class="documento-item">
                                <span class="documento-numero">1.1.</span>
                                Certificado de existencia y representación legal (cámara y comercio) válido hasta 
                                con <strong>(60) días</strong> de expedición.
                            </div>
                            <div class="documento-item">
                                <span class="documento-numero">1.2.</span>
                                Fotocopia del registro único tributario <strong>RUT</strong> (válido hasta con 
                                <strong>(60) sesenta días</strong> de expedición).
                            </div>
                            <div class="documento-item">
                                <span class="documento-numero">1.3.</span>
                                <strong>SC-ERP-CTB-FOR-007</strong> Formulario Unificado Conocimiento Proveedores y Acreedores
                            </div>
                            <div class="documento-item">
                                <span class="documento-numero">1.4.</span>
                                <strong>SC-ERP-SAG-FOR-002</strong> Declaración Sobre Origen-Destino de Fondos Persona Natural 
                                o <strong>SC-ERP-SAG-FOR-001</strong> Declaración Sobre Origen-Destino de Fondos Persona Jurídica 
                                según corresponda.
                            </div>
                            <div class="documento-item">
                                <span class="documento-numero">1.5.</span>
                                Fotocopia de la cédula de ciudadanía del representante legal y/o documento de 
                                identificación equivalente en Colombia en caso de ser extranjero.
                            </div>
                        </div>
                        
                        <p style="text-align: justify; margin-top: 25px;">
                            El propósito de esta solicitud es garantizar el adecuado funcionamiento de nuestros 
                            procesos de debida diligencia y cumplimiento, conforme a lo establecido por la 
                            <strong>Superintendencia de Sociedades</strong> y demás entes reguladores, evitando así 
                            sanciones legales y garantizando relaciones comerciales transparentes y seguras.
                        </p>
                    </div>
                    
                    <div class="warning-box">
                        <div class="warning-title">⚠️ IMPORTANTE - PLAZO MÁXIMO</div>
                        <div class="warning-text">
                            <strong>Fecha límite para envío de documentación:</strong><br>
                            <span style="font-size: 1.3em; font-weight: bold; color: #991b1b;">
                                {fecha_vencimiento.strftime('%d de %B de %Y')}
                            </span>
                        </div>
                        <div class="warning-text" style="margin-top: 15px;">
                            El incumplimiento de este plazo puede resultar en la <strong>suspensión temporal</strong> 
                            de su condición como proveedor/acreedor hasta que la documentación sea actualizada.
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="footer-title">📬 Envío de Documentación y Consultas:</div>
                    <div class="footer-contact">
                        <strong>Celular:</strong> 3243196701<br>
                        <strong>Email:</strong> creacionterceros@supertiendascanaveral.com
                    </div>
                    
                    <p style="color: #6b7280; margin: 20px 0; font-size: 0.95em;">
                        Cualquier observación o inquietud puede comunicarse por los medios anteriores.
                    </p>
                    
                    <div class="footer-signature">
                        <div class="firma-nombre">Silvana Paola Guarnizo Zamudio</div>
                        <div class="firma-cargo">Oficial de Cumplimiento Principal</div>
                        <div class="firma-cargo">Supertiendas Cañaveral</div>
                    </div>
                    
                    <p style="color: #9ca3af; font-size: 0.85em; margin-top: 25px;">
                        Muchas gracias, cordialmente.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Texto plano alternativo
        meses = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        fecha_texto = f"{fecha_vencimiento.day} de {meses[fecha_vencimiento.month]} de {fecha_vencimiento.year}"
        
        texto_plano = f"""
COMUNICADO EXTERNO URGENTE
ACTUALIZACIÓN DOCUMENTACIÓN E INFORMACIÓN PROVEEDORES Y ACREEDORES

⏰ TIEMPO RESTANTE: {dias_restantes} DÍAS
📅 FECHA LÍMITE: {fecha_texto}

INFORMACIÓN DEL PROVEEDOR:
- NIT: {nit}
- Razón Social: {razon_social}
- Último Radicado: {radicado}

Estimados proveedores y acreedores:

En cumplimiento de las disposiciones legales vigentes relacionadas con el Sistema de Autocontrol y Gestión del Riesgo Integral de Lavado de Activos, Financiación del Terrorismo y Financiación de la Proliferación de Armas de Destrucción Masiva (SAGRILAFT), nos permitimos solicitar de manera URGENTE la actualización de la siguiente información y documentación requerida por nuestro sistema de cumplimiento:

DOCUMENTACIÓN REQUERIDA:

1.1. Certificado de existencia y representación legal (cámara y comercio) válido hasta con (60) días de expedición.

1.2. Fotocopia del registro único tributario RUT (válido hasta con (60) sesenta días de expedición).

1.3. SC-ERP-CTB-FOR-007 Formulario Unificado Conocimiento Proveedores y Acreedores

1.4. SC-ERP-SAG-FOR-002 Declaración Sobre Origen-Destino de Fondos Persona Natural o SC-ERP-SAG-FOR-001 Declaración Sobre Origen-Destino de Fondos Persona Jurídica según corresponda.

1.5. Fotocopia de la cédula de ciudadanía del representante legal y/o documento de identificación equivalente en Colombia en caso de ser extranjero.

El propósito de esta solicitud es garantizar el adecuado funcionamiento de nuestros procesos de debida diligencia y cumplimiento, conforme a lo establecido por la Superintendencia de Sociedades y demás entes reguladores, evitando así sanciones legales y garantizando relaciones comerciales transparentes y seguras.

Plazo máximo para envío de la documentación: {fecha_texto}

CONTACTO:
📞 Celular: 3243196701
📧 Email: creacionterceros@supertiendascanaveral.com

Cualquier observación o inquietud se pueden comunicar al Celular 3243196701 o escribir al correo creacionterceros@supertiendascanaveral.com.

Muchas gracias, cordialmente.

Silvana Paola Guarnizo Zamudio
Oficial de Cumplimiento Principal
Supertiendas Cañaveral
"""
        
        # Crear y enviar mensaje
        msg = Message(
            subject=asunto,
            recipients=[destinatario],
            body=texto_plano,
            html=html_body
        )
        
        mail.send(msg)
        
        return (True, f"Correo de alerta enviado exitosamente a {destinatario}")
        
    except Exception as e:
        return (False, f"Error enviando correo de alerta: {str(e)}")
