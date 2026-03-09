# -*- coding: utf-8 -*-
"""
Rutas del Módulo de Facturas Digitales - VERSIÃ“N COMPLETA
Incluye: validación de duplicados, búsqueda de terceros, carga masiva
"""
from flask import render_template, request, jsonify, session, send_file, redirect, url_for, Response, current_app, flash
from flask_mail import Mail
from werkzeug.utils import secure_filename
from . import facturas_digitales_bp
from .models import FacturaDigital, ConfigRutasFacturas
from extensions import db
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc, and_, or_, text
from decoradores_permisos import requiere_permiso_html, requiere_permiso
import os
import hashlib
import json

# ===========================================================================
# RUTA BASE DE FACTURAS DIGITALES
# Se lee desde .env (FACTURAS_DIGITALES_RUTA). Si no existe la variable,
# usa el valor guardado en la BD (config_rutas_facturas). Como último
# recurso usa el fallback hardcodeado. Al iniciar, sincroniza BD con .env.
# Para cambiar la ruta: modificar FACTURAS_DIGITALES_RUTA en .env y reiniciar.
# ===========================================================================
def obtener_ruta_base():
    """Retorna la ruta base para facturas digitales leyendo del .env primero."""
    ruta_env = os.getenv('FACTURAS_DIGITALES_RUTA', '').strip()
    if ruta_env:
        return ruta_env
    config = ConfigRutasFacturas.query.filter_by(activa=True).first()
    if config and config.ruta_local:
        return config.ruta_local
    return 'D:/facturas_digitales'


def sincronizar_ruta_base():
    """Sincroniza la ruta del .env con la BD al iniciar el servidor."""
    ruta_env = os.getenv('FACTURAS_DIGITALES_RUTA', '').strip()
    if not ruta_env:
        return
    try:
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        if config:
            if config.ruta_local != ruta_env:
                config.ruta_local = ruta_env
                db.session.commit()
        else:
            nueva = ConfigRutasFacturas(ruta_local=ruta_env, activa=True)
            db.session.add(nueva)
            db.session.commit()
    except Exception:
        db.session.rollback()

# Imports para envÍo de firma masiva (modelos del sistema principal)
# Estos modelos están definidos en app.py
try:
    # Importación tardÍa para evitar circular imports
    def get_usuario_model():
        from app import Usuario
        return Usuario
    
    def get_tercero_model():
        from app import Tercero
        return Tercero
    
    def get_usuario_departamento_model():
        # Este modelo puede estar en usuario_departamento table (sistema multi-departamentos)
        # Por ahora usamos query directo con text()
        return None
except ImportError:
    pass

# Configuración
ALLOWED_EXTENSIONS = {'pdf', 'xml', 'zip', 'png', 'jpg', 'jpeg', 'xlsx', 'xls'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Logging de seguridad
import logging
security_logger = logging.getLogger('security')

def log_security(mensaje):
    """Registra eventos de seguridad"""
    security_logger.info(mensaje)

def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calcular_hash_archivo(file_path):
    """Calcula el hash SHA256 de un archivo"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def generar_radicado_rfd():
    """
    Genera el siguiente radicado RFD con formato RFD-000001
    Usa la tabla consecutivos_rfd para mantener el consecutivo
    """
    from .models import ConsecutivoRFD
    
    try:
        # Buscar o crear el consecutivo
        consecutivo = ConsecutivoRFD.query.filter_by(tipo='facturas_digitales').first()
        
        if not consecutivo:
            # Crear el primer consecutivo
            consecutivo = ConsecutivoRFD(
                tipo='facturas_digitales',
                ultimo_numero=0,
                prefijo='RFD',
                longitud_numero=6
            )
            db.session.add(consecutivo)
            db.session.flush()
        
        # Incrementar el número
        consecutivo.ultimo_numero += 1
        consecutivo.fecha_actualizacion = datetime.utcnow()
        
        # Generar radicado con formato: RFD-000001
        numero_formateado = str(consecutivo.ultimo_numero).zfill(consecutivo.longitud_numero)
        radicado = f"{consecutivo.prefijo}-{numero_formateado}"
        
        db.session.commit()
        
        log_security(f"RADICADO RFD GENERADO | radicado={radicado} | consecutivo={consecutivo.ultimo_numero}")
        
        return radicado
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR GENERANDO RADICADO RFD | error={str(e)}")
        raise

def enviar_correo_radicacion_lote(usuario_email, usuario_nombre, radicado_rfd, facturas_list):
    """
    ðŸ”¥ NUEVO: EnvÍa correo al usuario con MÃšLTIPLES facturas radicadas bajo un mismo RFD
    
    Args:
        usuario_email: Email del destinatario
        usuario_nombre: Nombre del usuario
        radicado_rfd: Número de radicado (ej: RFD-000002)
        facturas_list: Lista de dicts con datos de cada factura:
                      [{'numero_factura', 'nit_proveedor', 'razon_social', 'valor_total', 'fecha_emision'}, ...]
    
    Returns:
        True si el envÍo fue exitoso, False en caso contrario
    """
    try:
        from flask_mail import Message
        
        # Validar configuración de correo
        if not current_app.config.get('MAIL_SERVER'):
            log_security(f"ADVERTENCIA: Correo no configurado. No se envió notificación | usuario={usuario_nombre} | radicado={radicado_rfd}")
            return False
        
        # Fecha y hora actual
        fecha_hora_radicacion = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Calcular total del lote
        num_facturas = len(facturas_list)
        valor_total_lote = sum(f.get('valor_total', 0) for f in facturas_list)
        
        # Asunto del correo
        asunto = f"âœ… Radicación Exitosa - {num_facturas} Factura(s) Digital(es) - {radicado_rfd}"
        
        # ðŸ”¥ GENERAR TABLA HORIZONTAL CON HEADERS
        filas_tabla = ""
        for idx, factura in enumerate(facturas_list, start=1):
            filas_tabla += f"""
            <tr>
                <td style="text-align: center;">{idx}</td>
                <td><strong>{factura.get('numero_factura', 'N/A')}</strong></td>
                <td>{factura.get('nit_proveedor', 'N/A')}</td>
                <td>{factura.get('razon_social', 'N/A')}</td>
                <td style="text-align: right;"><strong>${factura.get('valor_total', 0):,.2f}</strong></td>
                <td style="text-align: center;">{factura.get('fecha_emision', 'N/A')}</td>
            </tr>
            """
        
        # Cuerpo HTML con tabla horizontal
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; }}
                .header {{ background-color: #166534; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .info-box {{ background-color: white; border-left: 4px solid #166534; padding: 15px; margin: 20px 0; }}
                table.info {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                table.info td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                table.info td:first-child {{ font-weight: bold; width: 30%; color: #166534; }}
                
                /* ðŸ”¥ TABLA HORIZONTAL DE FACTURAS */
                table.facturas {{ width: 100%; border-collapse: collapse; margin: 20px 0; background-color: white; }}
                table.facturas th {{ 
                    background-color: #166534; 
                    color: white; 
                    padding: 12px 8px; 
                    text-align: left; 
                    font-weight: bold;
                    border: 1px solid #0f4527;
                }}
                table.facturas td {{ 
                    padding: 10px 8px; 
                    border: 1px solid #ddd; 
                }}
                table.facturas tr:nth-child(even) {{ background-color: #f9f9f9; }}
                table.facturas tr:hover {{ background-color: #e8f5e9; }}
                
                .totales {{ 
                    background-color: #fef3c7; 
                    padding: 15px; 
                    margin: 20px 0; 
                    border-left: 4px solid #166534;
                    font-size: 16px;
                }}
                .alert {{ background-color: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; background-color: #f3f4f6; }}
                h1, h2, h3 {{ color: #166534; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>âœ… RADICACIÃ“N EXITOSA</h1>
                <h2>{radicado_rfd}</h2>
                <p style="margin: 5px 0; font-size: 18px;">{num_facturas} Factura(s) Radicada(s)</p>
            </div>
            
            <div class="content">
                <p>Estimado(a) <strong>{usuario_nombre}</strong>,</p>
                
                <p>Sus <strong>{num_facturas} factura(s) digital(es)</strong> han sido radicadas exitosamente bajo el número <strong style="color: #dc2626;">{radicado_rfd}</strong>.</p>
                
                <div class="info-box">
                    <h3>ðŸ“‹ Información de Radicación</h3>
                    <table class="info">
                        <tr>
                            <td><strong>Fecha y Hora</strong></td>
                            <td>{fecha_hora_radicacion}</td>
                        </tr>
                        <tr>
                            <td><strong>Radicado</strong></td>
                            <td><strong style="color: #dc2626; font-size: 18px;">{radicado_rfd}</strong></td>
                        </tr>
                        <tr>
                            <td><strong>Usuario</strong></td>
                            <td>{usuario_nombre}</td>
                        </tr>
                        <tr>
                            <td><strong>Cantidad de Facturas</strong></td>
                            <td><strong>{num_facturas}</strong></td>
                        </tr>
                    </table>
                </div>
                
                <h3 style="color: #166534;">ðŸ“„ Listado de Facturas Radicadas</h3>
                
                <table class="facturas">
                    <thead>
                        <tr>
                            <th style="width: 5%;">#</th>
                            <th style="width: 15%;">Factura</th>
                            <th style="width: 12%;">NIT</th>
                            <th style="width: 35%;">Razón Social</th>
                            <th style="width: 15%;">Valor</th>
                            <th style="width: 12%;">Fecha</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_tabla}
                    </tbody>
                </table>
                
                <div class="totales">
                    <strong>ðŸ’° VALOR TOTAL DEL LOTE:</strong> 
                    <span style="font-size: 20px; color: #166534; font-weight: bold;">
                        ${valor_total_lote:,.2f}
                    </span>
                </div>
                
                <div class="alert">
                    <strong>âš ï¸ Importante:</strong> Conserve este correo como comprobante de radicación. 
                    El número de radicado <strong>{radicado_rfd}</strong> agrupa todas las facturas listadas arriba 
                    y será necesario para cualquier consulta.
                </div>
                
                <h3 style="color: #166534; margin-top: 30px;">ðŸ“Œ Próximos Pasos</h3>
                <ol>
                    <li>Sus facturas serán revisadas por nuestro equipo administrativo</li>
                    <li>Recibirá notificación cuando sean aprobadas</li>
                    <li>Puede consultar el estado en cualquier momento usando el radicado <strong>{radicado_rfd}</strong></li>
                </ol>
            </div>
            
            <div class="footer">
                <p><strong>Gestor Documental - Supertiendas Cañaveral</strong></p>
                <p>Este es un correo automático, por favor no responder.</p>
                <p>Â© 2025 Supertiendas Cañaveral. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """
        
        # Cuerpo de texto plano (fallback)
        text_body = f"""
        RADICACIÃ“N EXITOSA - {radicado_rfd}
        
        Estimado(a) {usuario_nombre},
        
        Sus {num_facturas} factura(s) digital(es) han sido radicadas exitosamente.
        
        INFORMACIÃ“N DE RADICACIÃ“N:
        - Fecha y Hora: {fecha_hora_radicacion}
        - Radicado: {radicado_rfd}
        - Usuario: {usuario_nombre}
        - Cantidad: {num_facturas} factura(s)
        
        FACTURAS RADICADAS:
        """
        
        for idx, factura in enumerate(facturas_list, start=1):
            text_body += f"""
        {idx}. {factura.get('numero_factura', 'N/A')} - {factura.get('razon_social', 'N/A')}
           NIT: {factura.get('nit_proveedor', 'N/A')} | Valor: ${factura.get('valor_total', 0):,.2f} | Fecha: {factura.get('fecha_emision', 'N/A')}
            """
        
        text_body += f"""
        
        VALOR TOTAL: ${valor_total_lote:,.2f}
        
        IMPORTANTE: Conserve este correo como comprobante.
        
        Gestor Documental - Supertiendas Cañaveral
        """
        
        # Crear mensaje
        msg = Message(
            subject=asunto,
            recipients=[usuario_email],
            html=html_body,
            body=text_body
        )
        
        # Configurar Reply-To si está disponible
        if current_app.config.get('MAIL_REPLY_TO'):
            msg.reply_to = current_app.config['MAIL_REPLY_TO']
        
        # Enviar
        from flask_mail import Mail
        mail = Mail(current_app)
        mail.send(msg)
        
        log_security(f"CORREO RADICACIÃ“N LOTE ENVIADO | destinatario={usuario_email} | radicado={radicado_rfd} | facturas={num_facturas} | valor_total=${valor_total_lote:,.2f}")
        
        return True
        
    except Exception as e:
        log_security(f"ERROR ENVÃO CORREO RADICACIÃ“N LOTE | destinatario={usuario_email} | radicado={radicado_rfd} | error={str(e)}")
        import traceback
        traceback.print_exc()
        return False

def enviar_correo_radicacion_factura(usuario_email, usuario_nombre, radicado_rfd, factura_data):
    """
    EnvÍa correo al usuario que radicó la factura con los detalles
    
    Args:
        usuario_email: Email del usuario
        usuario_nombre: Nombre del usuario
        radicado_rfd: Número de radicado (RFD-000001)
        factura_data: Dict con datos de la factura {
            'numero_factura': 'FE-1',
            'nit_proveedor': '123456',
            'razon_social': 'Proveedor SA',
            'valor_total': 1000000,
            'fecha_emision': '2025-12-09',
            'num_archivos': 3
        }
    """
    try:
        from flask_mail import Message
        
        # Verificar configuración de correo
        if not current_app.config.get('MAIL_SERVER'):
            log_security(f"ADVERTENCIA: Correo no configurado. No se envió radicación | radicado={radicado_rfd}")
            return False
        
        fecha_hora_radicacion = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Asunto
        asunto = f"âœ… Radicación Exitosa - {radicado_rfd}"
        
        # Cuerpo HTML
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 700px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #166534 0%, #22c55e 100%);
                    color: white;
                    padding: 30px 20px;
                    border-radius: 10px 10px 0 0;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .header .radicado {{
                    font-size: 36px;
                    font-weight: bold;
                    margin: 10px 0 0 0;
                    background: rgba(255,255,255,0.2);
                    padding: 10px;
                    border-radius: 5px;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                    border-top: none;
                }}
                .info-box {{
                    background: #f8f9fa;
                    border-left: 4px solid #166534;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 5px;
                }}
                .info-row {{
                    display: flex;
                    padding: 8px 0;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #166534;
                    min-width: 150px;
                }}
                .info-value {{
                    color: #333;
                    flex: 1;
                }}
                .factura-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .factura-table th {{
                    background: #166534;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: 600;
                }}
                .factura-table td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .factura-table tr:hover {{
                    background: #f8f9fa;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 10px 10px;
                    border: 1px solid #e0e0e0;
                    border-top: none;
                    color: #666;
                    font-size: 14px;
                }}
                .success-icon {{
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
                .alert {{
                    background: #fff3cd;
                    border: 1px solid #ffc107;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="success-icon">âœ…</div>
                <h1>Radicación Exitosa</h1>
                <div class="radicado">{radicado_rfd}</div>
            </div>
            
            <div class="content">
                <p>Estimado(a) <strong>{usuario_nombre}</strong>,</p>
                
                <p>Su factura digital ha sido radicada exitosamente en nuestro sistema.</p>
                
                <div class="info-box">
                    <div class="info-row">
                        <span class="info-label">ðŸ“… Fecha y Hora:</span>
                        <span class="info-value">{fecha_hora_radicacion}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">ðŸ“‹ Radicado:</span>
                        <span class="info-value"><strong>{radicado_rfd}</strong></span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">ðŸ‘¤ Usuario:</span>
                        <span class="info-value">{usuario_nombre}</span>
                    </div>
                </div>
                
                <h3 style="color: #166534; margin-top: 30px;">ðŸ“„ Detalles de la Factura Radicada</h3>
                
                <table class="factura-table">
                    <thead>
                        <tr>
                            <th>Campo</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Número de Factura</strong></td>
                            <td>{factura_data.get('numero_factura', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td><strong>NIT Proveedor</strong></td>
                            <td>{factura_data.get('nit_proveedor', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td><strong>Razón Social</strong></td>
                            <td>{factura_data.get('razon_social', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td><strong>Fecha de Emisión</strong></td>
                            <td>{factura_data.get('fecha_emision', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td><strong>Valor Total</strong></td>
                            <td><strong>${factura_data.get('valor_total', 0):,.2f}</strong></td>
                        </tr>
                        <tr>
                            <td><strong>Archivos Adjuntos</strong></td>
                            <td>{factura_data.get('num_archivos', 1)} archivo(s) PDF</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="alert">
                    <strong>âš ï¸ Importante:</strong> Conserve este correo como comprobante de radicación. 
                    El número de radicado <strong>{radicado_rfd}</strong> será necesario para cualquier consulta.
                </div>
                
                <h3 style="color: #166534; margin-top: 30px;">ðŸ“Œ Próximos Pasos</h3>
                <ol>
                    <li>Su factura será revisada por nuestro equipo administrativo</li>
                    <li>Recibirá notificación cuando su factura sea aprobada</li>
                    <li>Puede consultar el estado en cualquier momento usando el radicado</li>
                </ol>
            </div>
            
            <div class="footer">
                <p><strong>Gestor Documental - Supertiendas Cañaveral</strong></p>
                <p>Este es un correo automático, por favor no responder.</p>
                <p>Â© 2025 Supertiendas Cañaveral. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """
        
        # Cuerpo de texto plano (fallback)
        text_body = f"""
        RADICACIÃ“N EXITOSA - {radicado_rfd}
        
        Estimado(a) {usuario_nombre},
        
        Su factura digital ha sido radicada exitosamente.
        
        INFORMACIÃ“N DE RADICACIÃ“N:
        - Fecha y Hora: {fecha_hora_radicacion}
        - Radicado: {radicado_rfd}
        - Usuario: {usuario_nombre}
        
        DETALLES DE LA FACTURA:
        - Número: {factura_data.get('numero_factura', 'N/A')}
        - NIT: {factura_data.get('nit_proveedor', 'N/A')}
        - Razón Social: {factura_data.get('razon_social', 'N/A')}
        - Fecha Emisión: {factura_data.get('fecha_emision', 'N/A')}
        - Valor Total: ${factura_data.get('valor_total', 0):,.2f}
        - Archivos: {factura_data.get('num_archivos', 1)}
        
        IMPORTANTE: Conserve este correo como comprobante.
        
        Gestor Documental - Supertiendas Cañaveral
        """
        
        # Crear mensaje
        msg = Message(
            subject=asunto,
            recipients=[usuario_email],
            html=html_body,
            body=text_body
        )
        
        # Configurar Reply-To si está disponible
        if current_app.config.get('MAIL_REPLY_TO'):
            msg.reply_to = current_app.config['MAIL_REPLY_TO']
        
        # Enviar
        mail = Mail(current_app)
        mail.send(msg)
        
        log_security(f"CORREO RADICACIÃ“N ENVIADO | destinatario={usuario_email} | radicado={radicado_rfd}")
        
        return True
        
    except Exception as e:
        log_security(f"ERROR ENVÃO CORREO RADICACIÃ“N | destinatario={usuario_email} | radicado={radicado_rfd} | error={str(e)}")
        return False

def crear_estructura_carpetas(empresa, anio, mes, departamento='SIN_DEPARTAMENTO', forma_pago='SIN_FORMA_PAGO'):
    """
    Crea la estructura de carpetas: empresa/año/mes/departamento/forma_pago
    Según especificación: D:/facturas_digitales/SC/2025/12/TIC/CREDITO/
    """
    # Obtener ruta base desde configuración
    config = ConfigRutasFacturas.query.filter_by(activa=True).first()
    if not config:
        ruta_base = obtener_ruta_base()
    else:
        ruta_base = config.ruta_local
    
    # Estructura completa: empresa/año/mes/departamento/forma_pago
    ruta_completa = os.path.join(
        ruta_base, 
        empresa,           # SC, LG, etc.
        str(anio),         # 2025
        f"{mes:02d}",      # 01, 02, ..., 12
        departamento,      # TIC, DOM, CYS, etc.
        forma_pago         # CREDITO, CONTADO, etc.
    )
    os.makedirs(ruta_completa, exist_ok=True)
    
    return ruta_completa, ruta_completa  # Anexos en la misma carpeta

def guardar_observacion_historial(factura_id, observacion, usuario):
    """Agrega una observación al historial JSON"""
    factura = FacturaDigital.query.get(factura_id)
    if not factura:
        return False
    
    # Obtener historial actual
    historial = factura.historial_observaciones or []
    
    # Agregar nueva observación
    nueva_obs = {
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'hora': datetime.now().strftime('%H:%M:%S'),
        'usuario': usuario,
        'texto': observacion
    }
    historial.append(nueva_obs)
    
    # Actualizar factura
    factura.historial_observaciones = historial
    factura.usuario_ultima_modificacion = usuario
    factura.fecha_ultima_modificacion = datetime.now()
    
    return True

# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================
@facturas_digitales_bp.route('/')
@facturas_digitales_bp.route('/dashboard')
@requiere_permiso_html('facturas_digitales', 'acceder_modulo')
def dashboard_facturas():
    """Dashboard principal del módulo de facturas digitales"""
    
    usuario = session['usuario']
    tipo_usuario = session.get('tipo_usuario', 'interno')
    
    # âš ï¸ USUARIOS EXTERNOS NO TIENEN ACCESO AL DASHBOARD COMPLETO
    # Solo pueden ver sus propias facturas en una vista simplificada
    if tipo_usuario == 'externo':
        return redirect(url_for('facturas_digitales.mis_facturas_externo'))
    
    try:
        # Obtener estadÍsticas usando SQL directo para evitar problemas de encoding
        if tipo_usuario == 'externo':
            nit_proveedor = session.get('nit')
            
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as pendientes,
                    COUNT(CASE WHEN estado = 'enviado_a_firmar' THEN 1 END) as enviadas,
                    COUNT(CASE WHEN estado = 'firmada' THEN 1 END) as firmadas,
                    COUNT(CASE WHEN estado = 'causada' THEN 1 END) as causadas,
                    COUNT(CASE WHEN estado = 'pagada' THEN 1 END) as pagadas,
                    COALESCE(SUM(valor_total), 0) as valor_total,
                    COALESCE(SUM(CASE WHEN estado = 'pendiente' THEN valor_total ELSE 0 END), 0) as valor_pendientes,
                    COALESCE(SUM(CASE WHEN estado = 'enviado_a_firmar' THEN valor_total ELSE 0 END), 0) as valor_enviadas,
                    COALESCE(SUM(CASE WHEN estado = 'firmada' THEN valor_total ELSE 0 END), 0) as valor_firmadas,
                    COALESCE(SUM(CASE WHEN estado = 'causada' THEN valor_total ELSE 0 END), 0) as valor_causadas,
                    COALESCE(SUM(CASE WHEN estado = 'pagada' THEN valor_total ELSE 0 END), 0) as valor_pagadas
                FROM facturas_digitales
                WHERE nit_proveedor = :nit
            """), {"nit": nit_proveedor})
            
            stats = result.fetchone()
            total_facturas = stats[0]
            facturas_pendientes = stats[1]
            facturas_enviadas = stats[2]
            facturas_firmadas = stats[3]
            facturas_causadas = stats[4]
            facturas_pagadas = stats[5]
            valor_total = float(stats[6])
            valor_pendientes = float(stats[7])
            valor_enviadas = float(stats[8])
            valor_firmadas = float(stats[9])
            valor_causadas = float(stats[10])
            valor_pagadas = float(stats[11])
            
            # SOLUCIÃ“N RADICAL: Cargar facturas con SQL directo (no ORM)
            facturas_result = db.session.execute(text("""
                SELECT 
                    id, numero_factura, nit_proveedor, razon_social_proveedor,
                    fecha_emision, fecha_vencimiento, valor_total, estado,
                    departamento, ruta_carpeta, fecha_carga,
                    fecha_envio_firma, usuario_envio_firma,
                    fecha_firmado, usuario_firmador, empresa
                FROM facturas_digitales
                WHERE nit_proveedor = :nit
                ORDER BY fecha_carga DESC
                LIMIT 10
            """), {"nit": nit_proveedor})
            
            # Convertir resultados SQL a diccionarios serializables
            ultimas_facturas = []
            config = ConfigRutasFacturas.query.filter_by(activa=True).first()
            ruta_base = obtener_ruta_base()
            
            for row in facturas_result:
                factura_id = row[0]
                ruta_carpeta = row[9]
                
                # Contar archivos en la carpeta
                num_archivos = 1
                if ruta_carpeta:
                    carpeta_completa = os.path.join(ruta_base, ruta_carpeta)
                    if os.path.exists(carpeta_completa):
                        archivos = [f for f in os.listdir(carpeta_completa) if os.path.isfile(os.path.join(carpeta_completa, f))]
                        num_archivos = len(archivos)
                
                # Obtener historial de envÍos
                historial_result = db.session.execute(text("""
                    SELECT fecha_envio, usuario_envio, destinatario_email
                    FROM historial_envios_firma
                    WHERE factura_id = :factura_id
                    ORDER BY fecha_envio DESC
                """), {'factura_id': factura_id})
                
                historial_envios = [
                    {
                        'fecha': h[0].isoformat() if h[0] else None,
                        'usuario': h[1],
                        'email': h[2]
                    } for h in historial_result.fetchall()
                ]
                
                # Crear diccionario serializable directamente
                factura_dict = {
                    'id': row[0],
                    'numero_factura': row[1],
                    'nit_proveedor': row[2],
                    'razon_social_proveedor': row[3],
                    'fecha_emision': row[4].isoformat() if row[4] else None,
                    'fecha_vencimiento': row[5].isoformat() if row[5] else None,
                    'valor_total': float(row[6]),
                    'estado': row[7],
                    'departamento': row[8],
                    'ruta_carpeta': row[9],
                    'fecha_carga': row[10].isoformat() if row[10] else None,
                    'fecha_envio_firma': row[11].isoformat() if row[11] else None,
                    'usuario_envio_firma': row[12],
                    'fecha_firmado': row[13].isoformat() if row[13] else None,
                    'usuario_firmador': row[14],
                    'empresa': row[15],
                    'num_archivos': num_archivos,
                    'historial_envios': historial_envios
                }
                
                ultimas_facturas.append(factura_dict)
            
        else:
            # Usuario interno: todas las facturas
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as pendientes,
                    COUNT(CASE WHEN estado = 'enviado_a_firmar' THEN 1 END) as enviadas,
                    COUNT(CASE WHEN estado = 'firmada' THEN 1 END) as firmadas,
                    COUNT(CASE WHEN estado = 'causada' THEN 1 END) as causadas,
                    COUNT(CASE WHEN estado = 'pagada' THEN 1 END) as pagadas,
                    COALESCE(SUM(valor_total), 0) as valor_total,
                    COALESCE(SUM(CASE WHEN estado = 'pendiente' THEN valor_total ELSE 0 END), 0) as valor_pendientes,
                    COALESCE(SUM(CASE WHEN estado = 'enviado_a_firmar' THEN valor_total ELSE 0 END), 0) as valor_enviadas,
                    COALESCE(SUM(CASE WHEN estado = 'firmada' THEN valor_total ELSE 0 END), 0) as valor_firmadas,
                    COALESCE(SUM(CASE WHEN estado = 'causada' THEN valor_total ELSE 0 END), 0) as valor_causadas,
                    COALESCE(SUM(CASE WHEN estado = 'pagada' THEN valor_total ELSE 0 END), 0) as valor_pagadas
                FROM facturas_digitales
            """))
            
            stats = result.fetchone()
            total_facturas = stats[0]
            facturas_pendientes = stats[1]
            facturas_enviadas = stats[2]
            facturas_firmadas = stats[3]
            facturas_causadas = stats[4]
            facturas_pagadas = stats[5]
            valor_total = float(stats[6])
            valor_pendientes = float(stats[7])
            valor_enviadas = float(stats[8])
            valor_firmadas = float(stats[9])
            valor_causadas = float(stats[10])
            valor_pagadas = float(stats[11])
            
            # SOLUCIÃ“N RADICAL: Cargar facturas con SQL directo (no ORM)
            facturas_result = db.session.execute(text("""
                SELECT 
                    id, numero_factura, nit_proveedor, razon_social_proveedor,
                    fecha_emision, fecha_vencimiento, valor_total, estado,
                    departamento, ruta_carpeta, fecha_carga,
                    fecha_envio_firma, usuario_envio_firma,
                    fecha_firmado, usuario_firmador, empresa
                FROM facturas_digitales
                ORDER BY fecha_carga DESC
                LIMIT 10
            """))
            
            # Convertir resultados SQL a diccionarios serializables
            ultimas_facturas = []
            config = ConfigRutasFacturas.query.filter_by(activa=True).first()
            ruta_base = obtener_ruta_base()
            
            for row in facturas_result:
                factura_id = row[0]
                ruta_carpeta = row[9]
                
                # Contar archivos en la carpeta
                num_archivos = 1
                if ruta_carpeta:
                    carpeta_completa = os.path.join(ruta_base, ruta_carpeta)
                    if os.path.exists(carpeta_completa):
                        archivos = [f for f in os.listdir(carpeta_completa) if os.path.isfile(os.path.join(carpeta_completa, f))]
                        num_archivos = len(archivos)
                
                # Obtener historial de envÍos
                historial_result = db.session.execute(text("""
                    SELECT fecha_envio, usuario_envio, destinatario_email
                    FROM historial_envios_firma
                    WHERE factura_id = :factura_id
                    ORDER BY fecha_envio DESC
                """), {'factura_id': factura_id})
                
                historial_envios = [
                    {
                        'fecha': h[0].isoformat() if h[0] else None,
                        'usuario': h[1],
                        'email': h[2]
                    } for h in historial_result.fetchall()
                ]
                
                # Crear diccionario serializable directamente
                factura_dict = {
                    'id': row[0],
                    'numero_factura': row[1],
                    'nit_proveedor': row[2],
                    'razon_social_proveedor': row[3],
                    'fecha_emision': row[4].isoformat() if row[4] else None,
                    'fecha_vencimiento': row[5].isoformat() if row[5] else None,
                    'valor_total': float(row[6]),
                    'estado': row[7],
                    'departamento': row[8],
                    'ruta_carpeta': row[9],
                    'fecha_carga': row[10].isoformat() if row[10] else None,
                    'fecha_envio_firma': row[11].isoformat() if row[11] else None,
                    'usuario_envio_firma': row[12],
                    'fecha_firmado': row[13].isoformat() if row[13] else None,
                    'usuario_firmador': row[14],
                    'empresa': row[15],
                    'num_archivos': num_archivos,
                    'historial_envios': historial_envios
                }
                
                ultimas_facturas.append(factura_dict)
    
    except Exception as e:
        print(f"âš ï¸ Error en dashboard facturas digitales: {e}")
        import traceback
        traceback.print_exc()
        # Mostrar dashboard con valores por defecto en caso de error
        total_facturas = 0
        facturas_pendientes = 0
        facturas_enviadas = 0
        facturas_firmadas = 0
        facturas_causadas = 0
        facturas_pagadas = 0
        valor_total = 0.0
        valor_pendientes = 0.0
        valor_enviadas = 0.0
        valor_firmadas = 0.0
        valor_causadas = 0.0
        valor_pagadas = 0.0
        ultimas_facturas = []
    
    return render_template('facturas_digitales/dashboard.html',
                         total_facturas=total_facturas,
                         facturas_pendientes=facturas_pendientes,
                         facturas_enviadas=facturas_enviadas,
                         facturas_firmadas=facturas_firmadas,
                         facturas_causadas=facturas_causadas,
                         facturas_pagadas=facturas_pagadas,
                         valor_total=valor_total,
                         valor_pendientes=valor_pendientes,
                         valor_enviadas=valor_enviadas,
                         valor_firmadas=valor_firmadas,
                         valor_causadas=valor_causadas,
                         valor_pagadas=valor_pagadas,
                         ultimas_facturas=[],  # ðŸ”¥ Cargar vacio, usamos API con paginación
                         tipo_usuario=tipo_usuario)


# ============================================================================
# ðŸ”¥ API: LISTAR FACTURAS CON PAGINACIÃ“N Y FILTROS DE FECHA (90 DÃAS DEFAULT)
# ============================================================================
@facturas_digitales_bp.route('/api/listar-facturas-paginadas')
@requiere_permiso('facturas_digitales', 'acceder_modulo')
def listar_facturas_paginadas():
    """
    ðŸ”¥ ENDPOINT OPTIMIZADO PARA DASHBOARD
    - Filtro por defecto: últimos 90 dÍas
    - Paginación: 50 facturas por página
    - Advertencia si rango > 90 dÍas
    """
    tipo_usuario = session.get('tipo_usuario', 'interno')
    
    # ðŸ”¥ PAGINACIÃ“N: 50 por página (antes cargaba TODAS)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)  # Máx 100
    
    # ðŸ”¥ FECHAS: Ãšltimos 90 dÍas por defecto
    fecha_actual = datetime.now()
    fecha_90_dias_atras = fecha_actual - timedelta(days=90)
    
    fecha_inicio_str = request.args.get('fecha_inicio')
    fecha_fin_str = request.args.get('fecha_fin')
    
    if fecha_inicio_str:
        fecha_inicio_dt = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        es_rango_default = False
    else:
        fecha_inicio_dt = fecha_90_dias_atras
        es_rango_default = True
    
    if fecha_fin_str:
        fecha_fin_dt = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
        es_rango_default = False
    else:
        fecha_fin_dt = fecha_actual
    
    # Validar rango
    if fecha_inicio_dt > fecha_fin_dt:
        return jsonify({'error': 'Fecha inicial no puede ser mayor que fecha final'}), 400
    
    diferencia_dias = (fecha_fin_dt - fecha_inicio_dt).days
    advertencia = None
    if diferencia_dias > 90:
        advertencia = f"El rango seleccionado ({diferencia_dias} dÍas) supera los 90 dÍas recomendados. Se mostrará paginado."
    
    # Query con filtro de fechas
    try:
        if tipo_usuario == 'externo':
            nit_proveedor = session.get('nit')
            facturas_result = db.session.execute(text("""
                SELECT 
                    id, numero_factura, nit_proveedor, razon_social_proveedor,
                    fecha_emision, fecha_vencimiento, valor_total, estado,
                    departamento, ruta_carpeta, fecha_carga,
                    fecha_envio_firma, usuario_envio_firma,
                    fecha_firmado, usuario_firmador, empresa, radicado_rfd
                FROM facturas_digitales
                WHERE nit_proveedor = :nit
                  AND fecha_carga >= :fecha_inicio
                  AND fecha_carga <= :fecha_fin
                ORDER BY fecha_carga DESC
                LIMIT :per_page OFFSET :offset
            """), {
                "nit": nit_proveedor,
                "fecha_inicio": fecha_inicio_dt.date(),
                "fecha_fin": fecha_fin_dt.date(),
                "per_page": per_page,
                "offset": (page - 1) * per_page
            })
            
            # Contar total
            count_result = db.session.execute(text("""
                SELECT COUNT(*) FROM facturas_digitales
                WHERE nit_proveedor = :nit
                  AND fecha_carga >= :fecha_inicio
                  AND fecha_carga <= :fecha_fin
            """), {
                "nit": nit_proveedor,
                "fecha_inicio": fecha_inicio_dt.date(),
                "fecha_fin": fecha_fin_dt.date()
            })
        else:
            # Usuario interno: todas las facturas
            facturas_result = db.session.execute(text("""
                SELECT 
                    id, numero_factura, nit_proveedor, razon_social_proveedor,
                    fecha_emision, fecha_vencimiento, valor_total, estado,
                    departamento, ruta_carpeta, fecha_carga,
                    fecha_envio_firma, usuario_envio_firma,
                    fecha_firmado, usuario_firmador, empresa, radicado_rfd
                FROM facturas_digitales
                WHERE fecha_carga >= :fecha_inicio
                  AND fecha_carga <= :fecha_fin
                ORDER BY fecha_carga DESC
                LIMIT :per_page OFFSET :offset
            """), {
                "fecha_inicio": fecha_inicio_dt.date(),
                "fecha_fin": fecha_fin_dt.date(),
                "per_page": per_page,
                "offset": (page - 1) * per_page
            })
            
            # Contar total
            count_result = db.session.execute(text("""
                SELECT COUNT(*) FROM facturas_digitales
                WHERE fecha_carga >= :fecha_inicio
                  AND fecha_carga <= :fecha_fin
            """), {
                "fecha_inicio": fecha_inicio_dt.date(),
                "fecha_fin": fecha_fin_dt.date()
            })
        
        total = count_result.scalar()
        total_pages = (total + per_page - 1) // per_page  # Redondear hacia arriba
        
        # Formatear facturas
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        ruta_base = obtener_ruta_base()
        
        facturas = []
        for row in facturas_result:
            factura_id = row[0]
            ruta_carpeta = row[9]
            
            # Contar archivos
            num_archivos = 1
            if ruta_carpeta:
                carpeta_completa = os.path.join(ruta_base, ruta_carpeta)
                if os.path.exists(carpeta_completa):
                    archivos = [f for f in os.listdir(carpeta_completa) if os.path.isfile(os.path.join(carpeta_completa, f))]
                    num_archivos = len(archivos)
            
            # Historial de envÍos
            historial_result = db.session.execute(text("""
                SELECT fecha_envio, usuario_envio, destinatario_email
                FROM historial_envios_firma
                WHERE factura_id = :factura_id
                ORDER BY fecha_envio DESC
            """), {'factura_id': factura_id})
            
            historial_envios = [
                {
                    'fecha': h[0].isoformat() if h[0] else None,
                    'usuario': h[1],
                    'email': h[2]
                } for h in historial_result.fetchall()
            ]
            
            facturas.append({
                'id': row[0],
                'numero_factura': row[1],
                'nit_proveedor': row[2],
                'razon_social_proveedor': row[3],
                'fecha_emision': row[4].isoformat() if row[4] else None,
                'fecha_vencimiento': row[5].isoformat() if row[5] else None,
                'valor_total': float(row[6]),
                'estado': row[7],
                'departamento': row[8],
                'ruta_carpeta': row[9],
                'fecha_carga': row[10].isoformat() if row[10] else None,
                'fecha_envio_firma': row[11].isoformat() if row[11] else None,
                'usuario_envio_firma': row[12],
                'fecha_firmado': row[13].isoformat() if row[13] else None,
                'usuario_firmador': row[14],
                'empresa': row[15],
                'radicado_rfd': row[16],  # ðŸ”¥ Incluir radicado
                'num_archivos': num_archivos,
                'historial_envios': historial_envios
            })
        
        return jsonify({
            'facturas': facturas,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': total_pages
            },
            'filtro': {
                'fecha_inicio': fecha_inicio_dt.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin_dt.strftime('%Y-%m-%d'),
                'dias_rango': diferencia_dias,
                'es_rango_default': es_rango_default
            },
            'advertencia': advertencia
        }), 200
        
    except Exception as e:
        print(f"âŒ Error en listar_facturas_paginadas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ðŸ†• MINI-FORMULARIO: COMPLETAR CAMPOS FALTANTES
# ============================================================================
@facturas_digitales_bp.route('/test-simple')
def test_simple():
    """TEST SIMPLE PARA VERIFICAR QUE EL BLUEPRINT FUNCIONA"""
    return "<h1>âœ… BLUEPRINT FUNCIONA!</h1><p>Si ves esto, el módulo está OK</p>"

@facturas_digitales_bp.route('/completar-campos/<int:id>', methods=['GET', 'POST'])
def completar_campos(id):
    """âœ… FORMULARIO PARA COMPLETAR EMPRESA, DEPARTAMENTO, TIPO_DOCUMENTO, FORMA_PAGO, TIPO_SERVICIO"""
    print(f"\nðŸ”¥ ENDPOINT COMPLETAR_CAMPOS LLAMADO! ID={id}")
    
    try:
        # Importar modelos de configuración
        from modules.configuracion.models import Empresa
        
        # 1. OBTENER FACTURA ACTUAL
        factura = FacturaDigital.query.get_or_404(id)
        print(f"âœ… Factura encontrada: {factura.numero_factura}")
        print(f"ðŸ“‹ Campos actuales: empresa={factura.empresa}, depto={factura.departamento}, tipo_doc={factura.tipo_documento}")
        
        # 2. CARGAR CATÁLOGOS USANDO LAS TABLAS CORRECTAS
        # EMPRESAS (tabla: empresas)
        empresas_orm = Empresa.query.filter_by(activo=True).order_by(Empresa.nombre).all()
        empresas = [{'codigo': e.sigla, 'nombre': e.nombre} for e in empresas_orm]
        print(f"âœ… Empresas cargadas: {len(empresas)}")
        
        # DEPARTAMENTOS (tabla: departamentos_facturacion)
        # Estructura esperada: id, sigla, nombre (o similar)
        result_deptos = db.session.execute(text("SELECT * FROM departamentos_facturacion"))
        departamentos = []
        for row in result_deptos:
            row_dict = dict(row._mapping)
            keys = list(row_dict.keys())
            # Buscar columnas que contengan "sigla" o usar primera columna
            sigla_col = next((k for k in keys if 'sigla' in k.lower()), keys[0] if len(keys) > 0 else None)
            nombre_col = next((k for k in keys if 'nombre' in k.lower() or 'descripcion' in k.lower()), keys[1] if len(keys) > 1 else None)
            if sigla_col and nombre_col:
                departamentos.append({
                    'codigo': row_dict[sigla_col],  # Para compatibilidad con template
                    'sigla': row_dict[sigla_col],   # Para value del select
                    'nombre': row_dict[nombre_col]  # Para texto visible
                })
        print(f"âœ… Departamentos cargados: {len(departamentos)}")
        
        # TIPOS DOCUMENTO (tabla: tipo_doc_facturacion)
        result_tipos = db.session.execute(text("SELECT * FROM tipo_doc_facturacion"))
        tipos_documento = []
        for row in result_tipos:
            row_dict = dict(row._mapping)
            keys = list(row_dict.keys())
            sigla_col = next((k for k in keys if 'sigla' in k.lower()), keys[0] if len(keys) > 0 else None)
            nombre_col = next((k for k in keys if 'nombre' in k.lower() or 'descripcion' in k.lower()), keys[1] if len(keys) > 1 else None)
            if sigla_col and nombre_col:
                tipos_documento.append({
                    'codigo': row_dict[sigla_col],
                    'sigla': row_dict[sigla_col],
                    'nombre': row_dict[nombre_col]
                })
        print(f"âœ… Tipos Documento cargados: {len(tipos_documento)}")
        
        # FORMAS DE PAGO (tabla: forma_pago_facturacion)
        result_formas = db.session.execute(text("SELECT * FROM forma_pago_facturacion"))
        formas_pago = []
        for row in result_formas:
            row_dict = dict(row._mapping)
            keys = list(row_dict.keys())
            sigla_col = next((k for k in keys if 'sigla' in k.lower()), keys[0] if len(keys) > 0 else None)
            nombre_col = next((k for k in keys if 'nombre' in k.lower() or 'descripcion' in k.lower()), keys[1] if len(keys) > 1 else None)
            if sigla_col and nombre_col:
                formas_pago.append({
                    'codigo': row_dict[sigla_col],
                    'sigla': row_dict[sigla_col],
                    'nombre': row_dict[nombre_col]
                })
        print(f"âœ… Formas Pago cargadas: {len(formas_pago)}")
        
        # TIPOS DE SERVICIO (tabla: tipo_servicio_facturacion)
        result_servicios = db.session.execute(text("SELECT * FROM tipo_servicio_facturacion"))
        tipos_servicio = []
        for row in result_servicios:
            row_dict = dict(row._mapping)
            keys = list(row_dict.keys())
            sigla_col = next((k for k in keys if 'sigla' in k.lower()), keys[0] if len(keys) > 0 else None)
            nombre_col = next((k for k in keys if 'nombre' in k.lower() or 'descripcion' in k.lower()), keys[1] if len(keys) > 1 else None)
            if sigla_col and nombre_col:
                tipos_servicio.append({
                    'codigo': row_dict[sigla_col],
                    'sigla': row_dict[sigla_col],
                    'nombre': row_dict[nombre_col]
                })
        print(f"âœ… Tipos Servicio cargados: {len(tipos_servicio)}")
        
        # 3. RENDERIZAR TEMPLATE CON DATOS
        return render_template(
            'facturas_digitales/completar_campos.html',
            factura=factura,
            empresas=empresas,
            departamentos=departamentos,
            tipos_documento=tipos_documento,
            formas_pago=formas_pago,
            tipos_servicio=tipos_servicio
        )
        
    except Exception as e:
        print(f"âŒ ERROR en completar_campos: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"âŒ ERROR: {str(e)}", 500# ============================================================================
# VISTA DE CARGA (VERSIÃ“N ORIGINAL)
# ============================================================================
@facturas_digitales_bp.route('/cargar')
@facturas_digitales_bp.route('/cargar-nueva')
@requiere_permiso_html('facturas_digitales', 'cargar_factura')
def cargar():
    """Vista para cargar nuevas facturas digitales"""
    
    # âœ… CORRECCIÃ“N: Usar session['rol'] que es lo que guarda el login
    rol = session.get('rol', 'interno')
    tipo_usuario = 'externo' if rol == 'externo' else 'interno'
    nit_usuario = None
    
    # Si es usuario externo, obtener su NIT directamente de la sesión
    if rol == 'externo':
        # El NIT ya está en session['nit'] guardado durante el login
        nit_usuario = session.get('nit')
        
        # Si por alguna razón no está en sesión, consultar BD
        if not nit_usuario:
            try:
                usuario_id = session.get('usuario_id')
                result = db.session.execute(text("""
                    SELECT t.nit 
                    FROM usuarios u
                    JOIN terceros t ON u.tercero_id = t.id
                    WHERE u.id = :usuario_id
                """), {'usuario_id': usuario_id})
                
                tercero = result.fetchone()
                if tercero:
                    nit_usuario = tercero[0]
            except Exception as e:
                log_security(f"Error obteniendo NIT de usuario externo | error={str(e)}")
    
    return render_template(
        'facturas_digitales/cargar.html', 
        usuario=session.get('usuario'),
        tipo_usuario=tipo_usuario,
        nit_usuario=nit_usuario
    )

# ============================================================================
# VISTA SIMPLIFICADA PARA USUARIOS EXTERNOS
# ============================================================================
@facturas_digitales_bp.route('/mis-facturas')
@requiere_permiso_html('facturas_digitales', 'acceder_modulo')
def mis_facturas_externo():
    """Vista simplificada para que usuarios externos vean solo sus facturas"""
    
    usuario = session['usuario']
    tipo_usuario = session.get('tipo_usuario', 'interno')
    
    # Solo usuarios externos pueden acceder aquÍ
    if tipo_usuario != 'externo':
        return redirect(url_for('facturas_digitales.dashboard_facturas'))
    
    nit_proveedor = session.get('nit')
    
    try:
        # Obtener estadÍsticas del proveedor
        result = db.session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN estado = 'pendiente_revision' THEN 1 END) as pendientes,
                COUNT(CASE WHEN estado = 'aprobado' THEN 1 END) as aprobadas,
                COALESCE(SUM(valor_total), 0) as valor_total
            FROM facturas_digitales
            WHERE nit_proveedor = :nit
        """), {"nit": nit_proveedor})
        
        stats = result.fetchone()
        total_facturas = stats[0]
        facturas_pendientes = stats[1]
        facturas_aprobadas = stats[2]
        valor_total = float(stats[3])
        
        return render_template('facturas_digitales/mis_facturas_externo.html',
                             usuario=usuario,
                             tipo_usuario=tipo_usuario,
                             nit_proveedor=nit_proveedor,
                             total_facturas=total_facturas,
                             facturas_pendientes=facturas_pendientes,
                             facturas_aprobadas=facturas_aprobadas,
                             valor_total=valor_total)
    
    except Exception as e:
        log_security(f"ERROR en mis_facturas_externo | usuario={usuario} | error={str(e)}")
        return render_template('facturas_digitales/mis_facturas_externo.html',
                             usuario=usuario,
                             tipo_usuario=tipo_usuario,
                             nit_proveedor=nit_proveedor,
                             total_facturas=0,
                             facturas_pendientes=0,
                             facturas_aprobadas=0,
                             valor_total=0,
                             error="Error al cargar estadÍsticas")

# ============================================================================
# API: LISTAR EMPRESAS ACTIVAS
# ============================================================================
@facturas_digitales_bp.route('/api/empresas')
@requiere_permiso('facturas_digitales', 'consultar_facturas')
def listar_empresas():
    """Retorna lista de empresas activas desde la tabla empresas"""
    try:
        # Consultar empresas activas (columnas correctas: id, sigla, nombre)
        resultado = db.session.execute(
            text("SELECT id, sigla, nombre FROM empresas WHERE activo = true ORDER BY sigla")
        ).fetchall()
        
        empresas = []
        for row in resultado:
            empresas.append({
                'id': row[0],
                'sigla': row[1],
                'nombre': row[2]
            })
        
        return jsonify({'success': True, 'empresas': empresas})
        
    except Exception as e:
        print(f"Error cargando empresas: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# API: OBTENER USUARIO ACTUAL
# ============================================================================
@facturas_digitales_bp.route('/api/usuario-actual')
@requiere_permiso('facturas_digitales', 'acceder_modulo')
def obtener_usuario_actual():
    """Retorna el usuario de la sesión actual"""
    try:
        usuario = session.get('usuario', 'Usuario')
        return jsonify({'success': True, 'usuario': usuario})
    except Exception as e:
        return jsonify({'success': False, 'usuario': 'Usuario', 'error': str(e)})

# ============================================================================
# API: BUSCAR TERCERO POR NIT
# ============================================================================
@facturas_digitales_bp.route('/api/buscar-tercero')
@requiere_permiso('facturas_digitales', 'validar_tercero')
def buscar_tercero():
    """Busca un tercero en la BD por NIT y retorna su razón social"""
    nit = request.args.get('nit', '').strip()
    
    if not nit:
        return jsonify({'existe': False, 'error': 'NIT requerido'}), 400
    
    try:
        # Consultar en la tabla terceros
        resultado = db.session.execute(
            text("SELECT razon_social FROM terceros WHERE nit = :nit LIMIT 1"),
            {'nit': nit}
        ).fetchone()
        
        if resultado:
            return jsonify({
                'existe': True,
                'razon_social': resultado[0],
                'nit': nit
            })
        else:
            return jsonify({
                'existe': False,
                'mensaje': 'NIT no encontrado en la base de datos',
                'nit': nit
            })
            
    except Exception as e:
        print(f"Error buscando tercero: {str(e)}")
        return jsonify({'existe': False, 'error': str(e)}), 500

# ============================================================================
# API: VALIDAR FACTURA REGISTRADA (IGUAL A RECIBIR_FACTURAS)
# ============================================================================
@facturas_digitales_bp.route('/validar_factura_registrada', methods=['GET'])
@requiere_permiso('facturas_digitales', 'verificar_duplicados')
def validar_factura_registrada():
    """
    Valida si una factura (NIT + Prefijo + Folio) ya existe
    en facturas_digitales, facturas_recibidas o lista temporal
    """
    from modules.recibir_facturas.models import FacturaRecibida, FacturaTemporal
    
    nit = request.args.get('nit', '').strip()
    prefijo = request.args.get('prefijo', '').strip().upper()
    folio = request.args.get('folio', '').strip()
    
    if not nit or not folio:
        return jsonify({"error": "NIT y folio requeridos"}), 400
    
    try:
        # Normalizar folio (sin ceros a la izquierda)
        folio_normalizado = folio.lstrip('0') if folio else ''
        
        # 1. Buscar en facturas_digitales
        numero_factura = f"{prefijo}-{folio}" if prefijo else folio
        factura_digital = FacturaDigital.query.filter_by(
            nit_proveedor=nit,
            numero_factura=numero_factura
        ).first()
        
        if factura_digital:
            fecha_rad = factura_digital.fecha_carga.strftime('%d/%m/%Y') if factura_digital.fecha_carga else 'N/A'
            return jsonify({
                "registrada": True,
                "en_digitales": True,
                "fecha": fecha_rad,
                "mensaje": f"âŒ FACTURA DUPLICADA: La factura {prefijo}{folio} ya existe en FACTURAS DIGITALES (Fecha: {fecha_rad})"
            }), 200
        
        # 2. Buscar en facturas_recibidas
        existe_recibida, factura_recibida = FacturaRecibida.validar_clave_unica(nit, prefijo, folio)
        
        if existe_recibida:
            fecha_rad = factura_recibida.fecha_radicacion.strftime('%d/%m/%Y') if factura_recibida.fecha_radicacion else 'N/A'
            return jsonify({
                "registrada": True,
                "en_recibidas": True,
                "fecha": fecha_rad,
                "mensaje": f"âŒ FACTURA DUPLICADA: La factura {prefijo}{folio} ya existe en FACTURAS RECIBIDAS (Radicada: {fecha_rad})"
            }), 200
        
        # 3. Buscar en facturas temporales (recibir_facturas)
        existe_temporal, factura_temporal = FacturaTemporal.validar_clave_unica(nit, prefijo, folio)
        
        if existe_temporal:
            fecha_rad = factura_temporal.fecha_radicacion.strftime('%d/%m/%Y') if factura_temporal.fecha_radicacion else 'N/A'
            return jsonify({
                "registrada": True,
                "en_temporal": True,
                "fecha": fecha_rad,
                "mensaje": f"âŒ FACTURA DUPLICADA: La factura {prefijo}{folio} ya existe en LISTA TEMPORAL (Fecha: {fecha_rad})"
            }), 200
        
        # 4. No existe - disponible
        return jsonify({
            "registrada": False,
            "mensaje": f"âœ… Factura {prefijo}{folio} disponible. Puedes adicionarla."
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error al validar factura: {str(e)}"}), 500

# ============================================================================
# API: VALIDAR FACTURA DUPLICADA (EN AMBAS TABLAS) - LEGACY
# ============================================================================
@facturas_digitales_bp.route('/api/validar-duplicada')
@requiere_permiso('facturas_digitales', 'verificar_duplicados')
def validar_duplicada():
    """Valida si una factura ya existe en facturas_digitales O facturas_recibidas"""
    nit = request.args.get('nit', '').strip()
    prefijo = request.args.get('prefijo', '').strip().upper()
    folio = request.args.get('folio', '').strip().upper()
    
    if not nit or not folio:
        return jsonify({'duplicada': False, 'error': 'Parámetros incompletos'}), 400
    
    try:
        # 1. Buscar en facturas_digitales
        numero_factura = f"{prefijo}-{folio}" if prefijo else folio
        
        factura_digital = FacturaDigital.query.filter_by(
            nit_proveedor=nit,
            numero_factura=numero_factura
        ).first()
        
        if factura_digital:
            return jsonify({
                'duplicada': True,
                'id_factura': factura_digital.id,
                'fecha': factura_digital.fecha_carga.strftime('%d/%m/%Y'),
                'tabla': 'FACTURAS DIGITALES',
                'mensaje': f'Factura {numero_factura} ya registrada en FACTURAS DIGITALES el {factura_digital.fecha_carga.strftime("%d/%m/%Y")}'
            })
        
        # 2. Buscar en facturas_recibidas (importar modelo)
        from modules.recibir_facturas.models import FacturaRecibida
        
        # Normalizar folio (sin ceros a la izquierda)
        folio_normalizado = folio.lstrip('0') if folio else ''
        
        factura_recibida = FacturaRecibida.query.filter_by(
            nit=nit,
            prefijo=prefijo
        ).filter(
            db.func.ltrim(FacturaRecibida.folio, '0') == folio_normalizado
        ).first()
        
        if factura_recibida:
            return jsonify({
                'duplicada': True,
                'id_factura': factura_recibida.id,
                'fecha': factura_recibida.fecha_radicacion.strftime('%d/%m/%Y') if factura_recibida.fecha_radicacion else 'N/A',
                'tabla': 'FACTURAS RECIBIDAS',
                'mensaje': f'Factura {prefijo}{folio} ya registrada en FACTURAS RECIBIDAS (Recepción FÍsica)'
            })
        
        # 3. No hay duplicado
        return jsonify({
            'duplicada': False,
            'mensaje': 'Factura no registrada, puede continuar'
        })
            
    except Exception as e:
        print(f"Error validando duplicado: {str(e)}")
        return jsonify({'existe': False, 'error': str(e)}), 500

# ============================================================================
# API: CARGAR FACTURA DIGITAL
# ============================================================================
@facturas_digitales_bp.route('/api/cargar-factura', methods=['POST'])
@requiere_permiso('facturas_digitales', 'cargar_factura')
def cargar_factura_api():
    """API para cargar una factura digital con todos sus archivos"""
    if 'usuario' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    usuario = session['usuario']
    tipo_usuario = session.get('tipo_usuario', 'interno')
    
    # ðŸ” LOG para diagnóstico
    print(f"ðŸ” CARGA FACTURA | usuario={usuario} | tipo_usuario={tipo_usuario} | rol={session.get('rol', 'NO_ROL')}")
    
    try:
        # Validar campos requeridos según tipo de usuario
        if tipo_usuario == 'externo':
            # Usuario externo: solo campos básicos
            campos_requeridos = ['prefijo', 'folio', 'nit_proveedor', 'razon_social', 'fecha_emision', 'valor_total']
        else:
            # Usuario interno: todos los campos
            campos_requeridos = ['empresa', 'departamento', 'forma_pago', 'prefijo', 'folio', 'nit_proveedor', 
                                'razon_social', 'fecha_emision', 'tipo_documento', 
                                'tipo_servicio', 'valor_total']
        
        for campo in campos_requeridos:
            if campo not in request.form or not request.form[campo]:
                return jsonify({'error': f'Campo requerido faltante: {campo}'}), 400
        
        # Validar archivo PDF principal
        if 'archivo_pdf' not in request.files:
            return jsonify({'error': 'Archivo PDF principal requerido'}), 400
        
        archivo_pdf = request.files['archivo_pdf']
        if archivo_pdf.filename == '':
            return jsonify({'error': 'Archivo PDF sin nombre'}), 400
        
        if not allowed_file(archivo_pdf.filename):
            return jsonify({'error': 'Tipo de archivo PDF no permitido'}), 400
        
        # Extraer datos del formulario
        prefijo = request.form['prefijo'].upper()
        folio = request.form['folio'].upper()
        nit_proveedor = request.form['nit_proveedor']
        razon_social = request.form['razon_social']
        fecha_emision = datetime.strptime(request.form['fecha_emision'], '%Y-%m-%d').date()
        valor_total = float(request.form['valor_total'])
        valor_iva = float(request.form.get('valor_iva', 0))
        observaciones = request.form.get('observaciones', '')
        
        # Campos solo para usuarios internos
        empresa = request.form.get('empresa', '').upper() if tipo_usuario == 'interno' else None
        departamento = request.form.get('departamento', '').upper() if tipo_usuario == 'interno' else None
        forma_pago = request.form.get('forma_pago', '').upper() if tipo_usuario == 'interno' else None
        tipo_documento = request.form.get('tipo_documento') if tipo_usuario == 'interno' else None
        tipo_servicio = request.form.get('tipo_servicio') if tipo_usuario == 'interno' else None
        
        # Validar duplicado usando numero_factura
        numero_factura = f"{prefijo}-{folio}"
        factura_existente = FacturaDigital.query.filter_by(
            nit_proveedor=nit_proveedor,
            numero_factura=numero_factura
        ).first()
        
        if factura_existente:
            return jsonify({
                'error': 'Factura duplicada',
                'mensaje': f'Factura {numero_factura} ya fue registrada el {factura_existente.fecha_carga.strftime("%Y-%m-%d")}'
            }), 409
        
        # Crear estructura de carpetas según tipo de usuario
        # Obtener ruta base desde configuración
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        ruta_base = obtener_ruta_base()
        
        if tipo_usuario == 'externo':
            # ========================================
            # ESCENARIO 2: Usuario EXTERNO carga factura
            # ========================================
            # Guardar en: D:/facturas_digitales/TEMPORALES/{NIT}/{NIT-PREFIJO-FOLIO}/
            # Estado: pendiente_revision
            nombre_carpeta = f"{nit_proveedor}-{prefijo}-{folio}"
            ruta_principal = os.path.join(ruta_base, 'TEMPORALES', nit_proveedor, nombre_carpeta)
            
            print(f"ðŸ“¦ ESCENARIO 2 - USUARIO EXTERNO")
            print(f"   Ruta base: {ruta_base}")
            print(f"   Ruta TEMPORALES: {ruta_principal}")
            
            # Crear estructura completa
            os.makedirs(ruta_principal, exist_ok=True)
            print(f"âœ… Carpeta TEMPORALES creada")
            
            ruta_anexos = ruta_principal  # Misma carpeta para anexos
            
            # Guardar RUTA COMPLETA en BD (no relativa)
            ruta_completa_bd = ruta_principal
            
            log_security(f"EXTERNO CARGA | nit={nit_proveedor} | factura={prefijo}-{folio} | ruta={ruta_principal}")
        else:
            # ========================================
            # ESCENARIO 1: Usuario INTERNO carga factura con TODOS los campos
            # ========================================
            # Guardar en: D:/facturas_digitales/{EMPRESA}/{AÃ‘O}/{MES}/{DEPARTAMENTO}/{FORMA_PAGO}/
            # ðŸ”¥ USA FECHA DE EMISIÃ“N (fecha_emision del formulario) para año y mes
            año = fecha_emision.year
            mes = f"{fecha_emision.month:02d}"  # 01, 02, ..., 12
            
            # ðŸ”¥ VALIDAR que campos NO estén vacÍos
            if not empresa or not empresa.strip():
                return jsonify({'error': 'El campo EMPRESA es obligatorio para usuarios internos'}), 400
            if not departamento or not departamento.strip():
                return jsonify({'error': 'El campo DEPARTAMENTO es obligatorio para usuarios internos'}), 400
            if not forma_pago or not forma_pago.strip():
                return jsonify({'error': 'El campo FORMA DE PAGO es obligatorio para usuarios internos'}), 400
            
            # Construir ruta con datos del formulario
            ruta_principal = os.path.join(
                ruta_base,
                empresa,           # SC, LG (del formulario)
                str(año),          # 2025 (de fecha_emision)
                mes,               # 11, 12 (de fecha_emision)
                departamento,      # TIC, DOM (del formulario)
                forma_pago         # CREDITO, CONTADO (del formulario)
            )
            
            print(f"ðŸ“¦ ESCENARIO 1 - USUARIO INTERNO")
            print(f"   Ruta base: {ruta_base}")
            print(f"   Empresa: {empresa}")
            print(f"   Año: {año} (de fecha_emision: {fecha_emision})")
            print(f"   Mes: {mes}")
            print(f"   Departamento: {departamento}")
            print(f"   Forma Pago: {forma_pago}")
            print(f"   Ruta final: {ruta_principal}")
            
            # Crear estructura completa
            os.makedirs(ruta_principal, exist_ok=True)
            print(f"âœ… Estructura de carpetas creada")
            
            ruta_anexos = ruta_principal  # Misma carpeta para anexos
            
            # Guardar RUTA COMPLETA en BD (no relativa)
            ruta_completa_bd = ruta_principal
            
            log_security(f"INTERNO CARGA | empresa={empresa} | depto={departamento} | pago={forma_pago} | factura={prefijo}-{folio} | fecha={fecha_emision} | ruta={ruta_principal}")
        
        # Nombre del archivo principal: NIT-PREFIJO-FOLIO-PRINCIPAL.pdf
        nombre_archivo_pdf = f"{nit_proveedor}-{prefijo}-{folio}-PRINCIPAL.pdf"
        ruta_archivo_pdf = os.path.join(ruta_principal, nombre_archivo_pdf)
        
        # Guardar archivo PDF principal
        archivo_pdf.save(ruta_archivo_pdf)
        hash_pdf = calcular_hash_archivo(ruta_archivo_pdf)
        tamanio_pdf = os.path.getsize(ruta_archivo_pdf) / 1024  # KB
        
        # Procesar archivos adicionales
        archivo_zip_path = None
        archivo_seguridad_path = None
        archivos_soportes_paths = []
        
        # Archivo ZIP (XML/PSD)
        if 'archivo_zip' in request.files and request.files['archivo_zip'].filename:
            archivo_zip = request.files['archivo_zip']
            nombre_zip = secure_filename(f"{nit_proveedor}-{prefijo}-{folio}_XML.zip")
            ruta_zip = os.path.join(ruta_anexos, nombre_zip)
            archivo_zip.save(ruta_zip)
            archivo_zip_path = ruta_zip
        
        # Archivo Seguridad Social
        if 'archivo_seguridad' in request.files and request.files['archivo_seguridad'].filename:
            archivo_seg = request.files['archivo_seguridad']
            ext_seg = archivo_seg.filename.rsplit('.', 1)[1].lower()
            nombre_seg = secure_filename(f"{nit_proveedor}-{prefijo}-{folio}_SEG.{ext_seg}")
            ruta_seg = os.path.join(ruta_anexos, nombre_seg)
            archivo_seg.save(ruta_seg)
            archivo_seguridad_path = ruta_seg
        
        # Archivos Soportes Múltiples
        if 'archivos_soportes' in request.files:
            soportes = request.files.getlist('archivos_soportes')
            for idx, soporte in enumerate(soportes, 1):
                if soporte.filename:
                    ext_sop = soporte.filename.rsplit('.', 1)[1].lower()
                    nombre_sop = secure_filename(f"{nit_proveedor}-{prefijo}-{folio}_SOP{idx}.{ext_sop}")
                    ruta_sop = os.path.join(ruta_anexos, nombre_sop)
                    soporte.save(ruta_sop)
                    archivos_soportes_paths.append(ruta_sop)
        
        # Crear registro en base de datos
        numero_factura = f"{prefijo}-{folio}"  # Ejemplo: "FE-1", "NC-45"
        
        # Estado según tipo de usuario
        estado_inicial = 'pendiente_revision' if tipo_usuario == 'externo' else 'pendiente'
        
        nueva_factura = FacturaDigital(
            # Identificación
            numero_factura=numero_factura,
            nit_proveedor=nit_proveedor,
            razon_social_proveedor=razon_social,
            empresa=empresa,  # Puede ser None para externos
            departamento=departamento,  # Puede ser None para externos
            forma_pago=forma_pago,  # Puede ser None para externos
            tipo_documento=tipo_documento,  # Puede ser None para externos
            tipo_servicio=tipo_servicio,  # Puede ser None para externos
            
            # Fechas
            fecha_emision=fecha_emision,
            
            # Valores
            valor_total=valor_total,
            valor_iva=valor_iva,
            valor_base=valor_total - valor_iva,
            
            # Archivo principal
            nombre_archivo_original=archivo_pdf.filename,
            nombre_archivo_sistema=nombre_archivo_pdf,
            ruta_archivo=ruta_archivo_pdf,
            ruta_carpeta=ruta_completa_bd,  # ðŸ”¥ RUTA COMPLETA (no relativa)
            ruta_archivo_principal=nombre_archivo_pdf,  # Nombre del archivo
            tipo_archivo='pdf',
            tamanio_kb=tamanio_pdf,
            hash_archivo=hash_pdf,
            
            # Observaciones
            observaciones=observaciones,
            
            # Control
            estado=estado_inicial,
            usuario_carga=usuario,
            tipo_usuario=tipo_usuario
        )
        
        db.session.add(nueva_factura)
        db.session.flush()  # Obtener el ID antes de commit
        
        # ðŸ”¥ GENERAR RADICADO RFD
        try:
            radicado_rfd = generar_radicado_rfd()
            nueva_factura.radicado_rfd = radicado_rfd
            log_security(f"RADICADO ASIGNADO | factura_id={nueva_factura.id} | radicado={radicado_rfd} | numero={numero_factura}")
        except Exception as e:
            log_security(f"ERROR GENERANDO RADICADO | factura_id={nueva_factura.id} | error={str(e)}")
            # Continuar sin radicado (no es crÍtico)
            radicado_rfd = None
        
        db.session.commit()
        
        # ðŸ”¥ NOTA: EL CORREO AHORA SE ENVÃA AL FINALIZAR EL LOTE COMPLETO
        # Ver endpoint: /api/finalizar-lote-rfd
        # (Ya no se envÍa correo por cada factura individual)
        
        return jsonify({
            'success': True,
            'mensaje': f'Factura radicada exitosamente - Radicado: {radicado_rfd or "PENDIENTE"}',
            'factura_id': nueva_factura.id,
            'numero_factura': numero_factura,
            'radicado_rfd': radicado_rfd,
            'fecha_carga': nueva_factura.fecha_carga.strftime('%Y-%m-%d %H:%M:%S')
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error cargando factura: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error al cargar factura',
            'detalle': str(e)
        }), 500

# ============================================================================
# ðŸ”¥ NUEVO: FINALIZAR LOTE Y ENVIAR CORREO CONSOLIDADO
# ============================================================================
@facturas_digitales_bp.route('/api/finalizar-lote-rfd', methods=['POST'])
def finalizar_lote_rfd():
    """
    ðŸ”¥ Asigna un RFD al lote de facturas recientes SIN radicado y envÍa correo consolidado
    
    Flujo:
    1. Usuario carga N facturas (cada una sin radicado aún)
    2. Usuario hace click en "Finalizar y Radicar" (desde frontend)
    3. Este endpoint:
       - Busca facturas SIN radicado del usuario (últimos 5 min)
       - Genera UN SOLO RFD para todo el lote
       - Asigna el mismo RFD a todas las facturas
       - EnvÍa UN SOLO correo con tabla horizontal listando todas
    
    Request JSON: {}  (vacÍo, toma datos de sesión)
    
    Returns:
        {
            "success": true,
            "radicado_rfd": "RFD-000003",
            "facturas_radicadas": 5,
            "correo_enviado": true,
            "facturas": [...]
        }
    """
    try:
        # Validar sesión
        if 'usuario' not in session:
            return jsonify({'error': 'Sesión no válida'}), 401
        
        usuario = session['usuario']
        
        # ðŸ” BUSCAR FACTURAS SIN RADICADO del usuario actual (últimos 5 minutos)
        tiempo_limite = datetime.now() - timedelta(minutes=5)
        
        facturas_pendientes = FacturaDigital.query.filter(
            FacturaDigital.usuario_carga == usuario,
            FacturaDigital.radicado_rfd.is_(None),  # Sin radicado
            FacturaDigital.fecha_carga >= tiempo_limite
        ).order_by(FacturaDigital.fecha_carga.desc()).all()
        
        if not facturas_pendientes:
            return jsonify({
                'error': 'No hay facturas pendientes de radicar',
                'mensaje': 'Todas las facturas ya tienen radicado asignado'
            }), 404
        
        # ðŸ”¢ GENERAR UN SOLO RFD PARA TODO EL LOTE
        radicado_rfd = generar_radicado_rfd()
        
        # ðŸ·ï¸ ASIGNAR EL MISMO RFD A TODAS LAS FACTURAS DEL LOTE
        facturas_data = []
        for factura in facturas_pendientes:
            factura.radicado_rfd = radicado_rfd
            
            # Preparar datos para el correo
            facturas_data.append({
                'numero_factura': factura.numero_factura,
                'nit_proveedor': factura.nit_proveedor,
                'razon_social': factura.razon_social_proveedor,
                'valor_total': float(factura.valor_total),
                'fecha_emision': factura.fecha_emision.strftime('%d/%m/%Y') if factura.fecha_emision else 'N/A'
            })
            
            log_security(f"RADICADO ASIGNADO A LOTE | factura_id={factura.id} | numero={factura.numero_factura} | radicado={radicado_rfd}")
        
        db.session.commit()
        
        # ðŸ“§ ENVIAR CORREO CONSOLIDADO CON TODAS LAS FACTURAS
        correo_enviado = False
        try:
            Usuario = get_usuario_model()
            usuario_obj = Usuario.query.filter_by(usuario=usuario).first()
            
            if usuario_obj and usuario_obj.correo:
                correo_enviado = enviar_correo_radicacion_lote(
                    usuario_email=usuario_obj.correo,
                    usuario_nombre=usuario_obj.usuario,
                    radicado_rfd=radicado_rfd,
                    facturas_list=facturas_data
                )
                
                if correo_enviado:
                    log_security(f"CORREO LOTE ENVIADO | usuario={usuario} | email={usuario_obj.correo} | radicado={radicado_rfd} | facturas={len(facturas_data)}")
                else:
                    log_security(f"ERROR ENVÃO CORREO LOTE | usuario={usuario} | radicado={radicado_rfd}")
            else:
                log_security(f"ADVERTENCIA: Usuario sin correo | usuario={usuario} | radicado={radicado_rfd}")
        except Exception as e:
            log_security(f"EXCEPCIÃ“N ENVÃO CORREO LOTE | usuario={usuario} | radicado={radicado_rfd} | error={str(e)}")
            # No falla la operación si el correo no se envÍa
        
        return jsonify({
            'success': True,
            'radicado_rfd': radicado_rfd,
            'facturas_radicadas': len(facturas_pendientes),
            'correo_enviado': correo_enviado,
            'facturas': facturas_data,
            'mensaje': f'Lote de {len(facturas_pendientes)} factura(s) radicado exitosamente con {radicado_rfd}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_security(f"ERROR FINALIZANDO LOTE RFD | usuario={session.get('usuario')} | error={str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error al finalizar lote',
            'detalle': str(e)
        }), 500

# ============================================================================
# LISTADO DE FACTURAS
# ============================================================================
@facturas_digitales_bp.route('/listado')
@requiere_permiso_html('facturas_digitales', 'consultar_facturas')
def listado():
    """Vista de listado de facturas digitales"""
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    return render_template('facturas_digitales/listado.html')

# ============================================================================
# API: OBTENER FACTURAS (CON PAGINACIÃ“N)
# ============================================================================
@facturas_digitales_bp.route('/api/facturas')
@requiere_permiso('facturas_digitales', 'consultar_facturas')
def get_facturas_api():
    """
    ðŸ”¥ API mejorada para obtener facturas con paginación inteligente
    
    Estrategia de rendimiento:
    - Por defecto: Ãšltimos 90 dÍas (evita cargar miles de registros)
    - Filtro personalizado: Máximo 90 dÍas por consulta
    - Paginación: 50 facturas por página (optimizado para grandes volúmenes)
    - Advertencia si el rango supera 90 dÍas
    """
    if 'usuario' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    tipo_usuario = session.get('tipo_usuario', 'interno')
    nit_proveedor = session.get('nit')
    
    # ðŸ”¥ PAGINACIÃ“N OPTIMIZADA: 50 por página
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Limitar máximo de registros por página (prevenir abusos)
    if per_page > 100:
        per_page = 100
    
    # Filtros
    estado = request.args.get('estado')
    empresa = request.args.get('empresa')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    busqueda = request.args.get('busqueda', '').strip()
    
    # ðŸ”¥ RANGO DE FECHAS POR DEFECTO: ÃšLTIMOS 90 DÃAS
    fecha_actual = datetime.now().date()
    fecha_90_dias_atras = fecha_actual - timedelta(days=90)
    
    # Si no hay fechas especificadas, usar últimos 90 dÍas
    if not fecha_inicio and not fecha_fin:
        fecha_inicio_dt = fecha_90_dias_atras
        fecha_fin_dt = fecha_actual
        rango_default = True
    else:
        # Parsear fechas personalizadas
        if fecha_inicio:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        else:
            fecha_inicio_dt = fecha_90_dias_atras
        
        if fecha_fin:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        else:
            fecha_fin_dt = fecha_actual
        
        rango_default = False
    
    # ðŸ”¥ VALIDAR RANGO MÁXIMO DE 90 DÃAS
    diferencia_dias = (fecha_fin_dt - fecha_inicio_dt).days
    advertencia_rango = None
    
    if diferencia_dias > 90:
        advertencia_rango = f"âš ï¸ El rango seleccionado ({diferencia_dias} dÍas) es muy amplio. Se recomienda filtrar máximo 90 dÍas para mejor rendimiento."
    
    # Query base
    query = FacturaDigital.query
    
    # Filtrar por tipo de usuario
    if tipo_usuario == 'externo':
        query = query.filter_by(nit_proveedor=nit_proveedor)
    
    # ðŸ”¥ FILTRO DE FECHAS OBLIGATORIO (previene carga masiva)
    query = query.filter(FacturaDigital.fecha_carga >= fecha_inicio_dt)
    query = query.filter(FacturaDigital.fecha_carga <= fecha_fin_dt)
    
    # Aplicar filtros adicionales
    if estado:
        query = query.filter_by(estado=estado)
    
    if empresa:
        query = query.filter_by(empresa=empresa)
    
    if busqueda:
        query = query.filter(
            or_(
                FacturaDigital.numero_factura.ilike(f'%{busqueda}%'),
                FacturaDigital.nit_proveedor.ilike(f'%{busqueda}%'),
                FacturaDigital.razon_social_proveedor.ilike(f'%{busqueda}%'),
                FacturaDigital.radicado_rfd.ilike(f'%{busqueda}%')
            )
        )
    
    # Ordenar y paginar
    query = query.order_by(desc(FacturaDigital.fecha_carga))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Formatear resultados
    facturas = []
    for f in pagination.items:
        facturas.append({
            'id': f.id,
            'numero_factura': f.numero_factura,
            'nit_proveedor': f.nit_proveedor,
            'razon_social': f.razon_social_proveedor,
            'fecha_carga': f.fecha_carga.strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_emision': f.fecha_emision.strftime('%Y-%m-%d') if f.fecha_emision else None,
            'valor_total': float(f.valor_total),
            'valor_iva': float(f.valor_iva),
            'estado': f.estado,
            'usuario_carga': f.usuario_carga,
            'departamento': f.departamento,
            'forma_pago': f.forma_pago,
            'radicado_rfd': f.radicado_rfd  # ðŸ”¥ Incluir radicado en respuesta
        })
    
    # ðŸ”¥ Respuesta mejorada con información de rango y advertencias
    respuesta = {
        'facturas': facturas,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        # ðŸ”¥ Información adicional del filtro
        'filtro': {
            'fecha_inicio': fecha_inicio_dt.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin_dt.strftime('%Y-%m-%d'),
            'dias_rango': diferencia_dias,
            'es_rango_default': rango_default
        }
    }
    
    # Agregar advertencia si el rango es muy amplio
    if advertencia_rango:
        respuesta['advertencia'] = advertencia_rango
    
    return jsonify(respuesta)

# ============================================================================
# DETALLE DE FACTURA
# ============================================================================
@facturas_digitales_bp.route('/detalle/<int:id>')
@requiere_permiso_html('facturas_digitales', 'ver_detalle_factura')
def detalle(id):
    """Vista de detalle de una factura"""
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    factura = FacturaDigital.query.get_or_404(id)
    
    # Verificar permisos
    tipo_usuario = session.get('tipo_usuario', 'interno')
    if tipo_usuario == 'externo':
        nit_proveedor = session.get('nit')
        if factura.nit_proveedor != nit_proveedor:
            return "No autorizado", 403
    
    return render_template('facturas_digitales/detalle.html', factura=factura)

# ============================================================================
# DESCARGAR ARCHIVO
# ============================================================================
@facturas_digitales_bp.route('/descargar/<int:id>')
@requiere_permiso_html('facturas_digitales', 'descargar_soportes')
def descargar(id):
    """
    ðŸ”¥ DESCARGA TODOS LOS ARCHIVOS (PRINCIPAL + ANEXOS + SEG. SOCIAL) como ZIP
    """
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    factura = FacturaDigital.query.get_or_404(id)
    
    # Verificar permisos
    tipo_usuario = session.get('tipo_usuario', 'interno')
    if tipo_usuario == 'externo':
        nit_proveedor = session.get('nit')
        if factura.nit_proveedor != nit_proveedor:
            return "No autorizado", 403
    
    # Obtener configuración de rutas
    config = ConfigRutasFacturas.query.filter_by(activa=True).first()
    ruta_base = obtener_ruta_base()
    
    if not factura.ruta_carpeta:
        return jsonify({'error': 'Factura sin carpeta de archivos'}), 404
    
    carpeta_factura = os.path.join(ruta_base, factura.ruta_carpeta)
    
    if not os.path.exists(carpeta_factura):
        return jsonify({'error': 'Carpeta no encontrada'}), 404
    
    # Crear archivo ZIP temporal con TODOS los PDFs
    import tempfile
    import zipfile
    
    # Crear archivo temporal
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    try:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar TODOS los archivos PDF de la carpeta
            archivos = os.listdir(carpeta_factura)
            contador = 0
            for archivo in archivos:
                if archivo.lower().endswith('.pdf'):
                    ruta_completa = os.path.join(carpeta_factura, archivo)
                    zipf.write(ruta_completa, arcname=archivo)
                    contador += 1
        
        temp_zip.close()
        
        # Nombre del ZIP: debe coincidir con el nombre de la carpeta (NIT-PREFIJO-FOLIO)
        # Extraer nombre de carpeta desde ruta_carpeta (ej: 805013653/805013653-DS-14/ -> 805013653-DS-14)
        nombre_carpeta = os.path.basename(factura.ruta_carpeta.rstrip('/\\'))
        nombre_zip = f"{nombre_carpeta}.zip"
        
        log_security(f"ðŸ“¦ ZIP DESCARGADO | factura_id={id} | archivos={contador} | nombre={nombre_zip} | usuario={session.get('usuario', 'desconocido')}")
        
        # Enviar el ZIP
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name=nombre_zip,
            mimetype='application/zip'
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al crear ZIP: {str(e)}'}), 500

# ============================================================================
# CAMBIAR ESTADO (Solo usuarios internos)
# ============================================================================
@facturas_digitales_bp.route('/api/cambiar-estado/<int:id>', methods=['POST'])
@requiere_permiso('facturas_digitales', 'cambiar_estado')
def cambiar_estado_api(id):
    """Cambia el estado de una factura (aprobar/rechazar)"""
    if 'usuario' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    tipo_usuario = session.get('tipo_usuario', 'interno')
    if tipo_usuario != 'interno':
        return jsonify({'error': 'No autorizado'}), 403
    
    factura = FacturaDigital.query.get_or_404(id)
    
    data = request.get_json()
    nuevo_estado = data.get('estado')
    motivo = data.get('motivo', '')
    
    if nuevo_estado not in ['aprobado', 'rechazado', 'pendiente']:
        return jsonify({'error': 'Estado inválido'}), 400
    
    estado_anterior = factura.estado
    factura.estado = nuevo_estado
    factura.motivo_rechazo = motivo if nuevo_estado == 'rechazado' else None
    factura.usuario_ultima_modificacion = session['usuario']
    factura.fecha_ultima_modificacion = datetime.now()
    
    # Agregar al historial de observaciones
    if motivo:
        guardar_observacion_historial(id, f"Estado cambiado a {nuevo_estado}: {motivo}", session['usuario'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'mensaje': f'Estado cambiado a {nuevo_estado}',
        'nuevo_estado': nuevo_estado
    })

# ============================================================================
# CONFIGURACIÃ“N (Solo administradores)
# ============================================================================
@facturas_digitales_bp.route('/configuracion')
@requiere_permiso_html('facturas_digitales', 'configurar_rutas')
def configuracion():
    """Vista de configuración del módulo"""
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    # Solo administradores
    tipo_usuario = session.get('tipo_usuario', 'interno')
    if tipo_usuario != 'interno':
        return "No autorizado", 403
    
    config = ConfigRutasFacturas.query.filter_by(activa=True).first()
    
    return render_template('facturas_digitales/configuracion.html', config=config)

# ============================================================================
# API: ACTUALIZAR CONFIGURACIÃ“N DE RUTAS
# ============================================================================
@facturas_digitales_bp.route('/api/actualizar-ruta', methods=['POST'])
@requiere_permiso('facturas_digitales', 'configurar_rutas')
def actualizar_ruta_api():
    """Actualiza la configuración de rutas de almacenamiento"""
    if 'usuario' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    tipo_usuario = session.get('tipo_usuario', 'interno')
    if tipo_usuario != 'interno':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    ruta_local = data.get('ruta_local')
    ruta_red = data.get('ruta_red', '')
    
    if not ruta_local:
        return jsonify({'error': 'Ruta local requerida'}), 400
    
    # Desactivar configuración anterior
    ConfigRutasFacturas.query.update({'activa': False})
    
    # Crear nueva configuración
    nueva_config = ConfigRutasFacturas(
        nombre='default',
        ruta_local=ruta_local,
        ruta_red=ruta_red if ruta_red else None,
        activa=True,
        usuario_creacion=session['usuario']
    )
    
    db.session.add(nueva_config)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'mensaje': 'Configuración actualizada correctamente'
    })

# ============================================================================
# API: RADICAR FACTURA DIGITAL (GUARDAR EN TEMPORALES O FINAL)
# ============================================================================
@facturas_digitales_bp.route('/api/radicar', methods=['POST'])
@requiere_permiso('facturas_digitales', 'cargar_factura')
def radicar_factura():
    """Guarda una factura digital en la base de datos con sus archivos"""
    if 'usuario' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    try:
        # Obtener datos del formulario
        nit = request.form.get('nit', '').strip()
        razon_social = request.form.get('razonSocial', '').strip()
        prefijo = request.form.get('prefijo', '').strip().upper()
        folio = request.form.get('folio', '').strip()
        empresa = request.form.get('empresa', '').strip()
        fecha_expedicion = request.form.get('fechaExpedicion')
        fecha_radicacion = request.form.get('fechaRadicacion')
        tipo_documento = request.form.get('tipoDocumento')
        forma_pago = request.form.get('formaPago')
        tipo_servicio = request.form.get('tipoServicio')
        departamento = request.form.get('departamento')
        valor_bruto = request.form.get('valorBruto', 0)
        valor_iva = request.form.get('valorIva', 0)
        valor_total = request.form.get('valorTotal', 0)
        observaciones = request.form.get('observaciones', '').strip()
        
        # Validar campos requeridos
        if not all([nit, razon_social, folio, fecha_expedicion, valor_total]):
            return jsonify({
                'success': False, 
                'message': 'Faltan campos obligatorios'
            }), 400
        
        # Construir número de factura
        numero_factura = f"{prefijo}-{folio}" if prefijo else folio
        
        # Validar duplicados
        factura_existente = FacturaDigital.query.filter_by(
            nit_proveedor=nit,
            numero_factura=numero_factura
        ).first()
        
        if factura_existente:
            return jsonify({
                'success': False,
                'message': f'La factura {numero_factura} del NIT {nit} ya está registrada'
            }), 400
        
        # Obtener archivos
        archivo_principal = request.files.get('archivo_principal')
        seguridad_social = request.files.get('seguridad_social')
        
        if not archivo_principal:
            return jsonify({
                'success': False,
                'message': 'El archivo principal es obligatorio'
            }), 400
        
        # Obtener configuración de rutas
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        if not config:
            return jsonify({
                'success': False,
                'message': 'No hay configuración de rutas activa'
            }), 500
        
        # Crear estructura de carpetas: EMPRESA/AÃ‘O/MES/DEPARTAMENTO/NIT-PREFIJO-FOLIO/
        from datetime import datetime
        
        # Mapeo de meses a nombres en español
        MESES_NOMBRES = {
            '01': '1. ENERO', '02': '2. FEBRERO', '03': '3. MARZO',
            '04': '4. ABRIL', '05': '5. MAYO', '06': '6. JUNIO',
            '07': '7. JULIO', '08': '8. AGOSTO', '09': '9. SEPTIEMBRE',
            '10': '10. OCTUBRE', '11': '11. NOVIEMBRE', '12': '12. DICIEMBRE'
        }
        
        fecha_rad = datetime.strptime(fecha_radicacion, '%Y-%m-%d') if fecha_radicacion else datetime.now()
        año = fecha_rad.strftime('%Y')
        mes_numero = fecha_rad.strftime('%m')
        mes_nombre = MESES_NOMBRES.get(mes_numero, mes_numero)
        
        # Estructura: empresa/año/mes/departamento/forma_pago/nit-factura
        carpeta_factura = f"{empresa}/{año}/{mes_nombre}/{departamento}/{forma_pago}/{nit}-{numero_factura}"
        ruta_completa = os.path.join(config.ruta_local, carpeta_factura)
        
        # Crear carpetas si no existen
        os.makedirs(ruta_completa, exist_ok=True)
        
        # Guardar archivo principal
        ext_principal = os.path.splitext(archivo_principal.filename)[1].lower()
        nombre_principal = f"{nit}-{numero_factura}-PRINCIPAL{ext_principal}"
        ruta_principal = os.path.join(ruta_completa, nombre_principal)
        archivo_principal.save(ruta_principal)
        
        # Guardar seguridad social si existe
        ruta_seg_social = None
        if seguridad_social:
            ext_seg = os.path.splitext(seguridad_social.filename)[1].lower()
            nombre_seg = f"{nit}-{numero_factura}-SEG_SOCIAL{ext_seg}"
            ruta_seg_social = os.path.join(ruta_completa, nombre_seg)
            seguridad_social.save(ruta_seg_social)
        
        # Guardar anexos (si existen)
        anexos_guardados = []
        for i in range(10):  # Máximo 10 anexos
            anexo = request.files.get(f'anexo_{i}')
            if anexo:
                ext_anexo = os.path.splitext(anexo.filename)[1].lower()
                nombre_anexo = f"{nit}-{numero_factura}-ANEXO{i+1}{ext_anexo}"
                ruta_anexo = os.path.join(ruta_completa, nombre_anexo)
                anexo.save(ruta_anexo)
                anexos_guardados.append(nombre_anexo)
        
        # Calcular hash del archivo principal para evitar duplicados
        import hashlib
        with open(ruta_principal, 'rb') as f:
            hash_archivo = hashlib.sha256(f.read()).hexdigest()
        
        # Calcular tamaño en KB
        tamanio_kb = os.path.getsize(ruta_principal) / 1024
        
        # Crear registro en base de datos
        nueva_factura = FacturaDigital(
            numero_factura=numero_factura,
            nit_proveedor=nit,
            razon_social_proveedor=razon_social,
            empresa=empresa,  # Guardar sigla de la empresa
            fecha_emision=datetime.strptime(fecha_expedicion, '%Y-%m-%d').date(),
            fecha_vencimiento=None,
            valor_total=float(valor_total),
            valor_iva=float(valor_iva) if valor_iva else 0,
            valor_base=float(valor_bruto) if valor_bruto else float(valor_total),
            nombre_archivo_original=archivo_principal.filename,
            nombre_archivo_sistema=nombre_principal,
            ruta_archivo=ruta_principal,
            ruta_carpeta=carpeta_factura,  # Ruta relativa de la carpeta
            ruta_archivo_principal=nombre_principal,  # Nombre del archivo principal
            tipo_archivo=ext_principal.replace('.', ''),
            tamanio_kb=tamanio_kb,
            estado='pendiente',
            observaciones=observaciones if observaciones else None,
            usuario_carga=session.get('usuario', 'Sistema'),
            tipo_usuario='interno',
            fecha_carga=datetime.now(),
            ip_carga=request.remote_addr,
            hash_archivo=hash_archivo,
            departamento=departamento,
            forma_pago=forma_pago,
            estado_firma='PENDIENTE',
            activo=True
        )
        
        db.session.add(nueva_factura)
        db.session.flush()  # Obtener el ID antes de commit
        
        # ðŸ”¥ GENERAR RADICADO RFD
        try:
            radicado_rfd = generar_radicado_rfd()
            nueva_factura.radicado_rfd = radicado_rfd
            log_security(f"RADICADO ASIGNADO | factura_id={nueva_factura.id} | radicado={radicado_rfd} | numero={numero_factura}")
        except Exception as e:
            log_security(f"ERROR GENERANDO RADICADO | factura_id={nueva_factura.id} | error={str(e)}")
            # Continuar sin radicado (no es crÍtico)
            radicado_rfd = None
        
        db.session.commit()
        
        # ðŸ”¥ NOTA: EL CORREO AHORA SE ENVÃA AL FINALIZAR EL LOTE COMPLETO
        # Ver endpoint: /api/finalizar-lote-rfd
        # (Ya no se envÍa correo por cada factura individual)
        
        return jsonify({
            'success': True,
            'message': f'Factura {numero_factura} radicada correctamente - Radicado: {radicado_rfd or "PENDIENTE"}',
            'id_factura': nueva_factura.id,
            'radicado_rfd': radicado_rfd
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error radicando factura: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al radicar la factura: {str(e)}'
        }), 500


# ============================================================================
# API: OBTENER DATOS DE FACTURA PARA EDICIÃ“N
# ============================================================================
@facturas_digitales_bp.route('/api/factura/<int:id>', methods=['GET'])
@requiere_permiso('facturas_digitales', 'ver_detalle_factura')
def obtener_factura_para_editar(id):
    """Obtiene todos los datos de una factura para cargarlos en el formulario de edición"""
    try:
        factura = FacturaDigital.query.get(id)
        
        if not factura:
            return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
        
        # Obtener lista de archivos en la carpeta
        archivos = {
            'principal': None,
            'anexos': [],
            'seguridad_social': None
        }
        
        if factura.ruta_carpeta and os.path.exists(factura.ruta_carpeta):
            for archivo in os.listdir(factura.ruta_carpeta):
                ruta_completa = os.path.join(factura.ruta_carpeta, archivo)
                if os.path.isfile(ruta_completa):
                    if 'PRINCIPAL' in archivo.upper():
                        archivos['principal'] = archivo
                    elif 'SEG_SOCIAL' in archivo.upper() or 'SEGURIDAD' in archivo.upper():
                        archivos['seguridad_social'] = archivo
                    elif 'ANEXO' in archivo.upper():
                        archivos['anexos'].append(archivo)
        
        return jsonify({
            'success': True,
            'factura': {
                'id': factura.id,
                'nit': factura.nit_proveedor,
                'razon_social': factura.razon_social_proveedor,
                'prefijo': factura.prefijo,
                'folio': factura.folio,
                'numero_factura': factura.numero_factura,
                'empresa': factura.empresa,
                'fecha_expedicion': factura.fecha_emision.strftime('%Y-%m-%d') if factura.fecha_emision else None,
                'fecha_radicacion': factura.fecha_carga.strftime('%Y-%m-%d') if factura.fecha_carga else None,
                'tipo_documento': factura.tipo_documento,
                'forma_pago': factura.forma_pago,
                'tipo_servicio': factura.tipo_servicio,
                'departamento': factura.departamento,
                'valor_bruto': float(factura.valor_total or 0),
                'valor_iva': float(factura.valor_iva or 0),
                'valor_total': float(factura.valor_total or 0),
                'observaciones': factura.observaciones or '',
                'estado': factura.estado,
                'archivos': archivos,
                'ruta_carpeta': factura.ruta_carpeta
            }
        })
    except Exception as e:
        print(f"Error obteniendo factura: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# API: ACTUALIZAR FACTURA Y MOVER DE TEMPORALES A FINAL
# ============================================================================
@facturas_digitales_bp.route('/api/factura/<int:id>/actualizar', methods=['POST'])
def actualizar_factura_completa(id):
    """
    ðŸ†• ACTUALIZA campos faltantes y MUEVE archivos de TEMPORALES a ubicación final
    Lógica: EMPRESA/AÃ‘O/MES/DEPARTAMENTO/FORMA_PAGO/
    """
    # Verificar sesión
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No autenticado'}), 401
    
    try:
        factura = FacturaDigital.query.get(id)
        
        if not factura:
            return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
        
        # Obtener campos del formulario (form-data o JSON)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        empresa = data.get('empresa', '').strip()
        departamento = data.get('departamento', '').strip()
        forma_pago = data.get('formaPago', '').strip()
        tipo_documento = data.get('tipoDocumento', '').strip()
        tipo_servicio = data.get('tipoServicio', '').strip()
        observaciones = data.get('observaciones', '').strip()
        
        # ========================================
        # ðŸ”¥ ESCENARIO 3: VALIDAR CAMPOS OBLIGATORIOS PARA MOVER DE TEMPORALES
        # ========================================
        # Validar que todos los campos requeridos estén presentes
        if not empresa or not empresa.strip():
            return jsonify({'success': False, 'message': 'EMPRESA es obligatorio'}), 400
        
        if not departamento or not departamento.strip():
            return jsonify({'success': False, 'message': 'DEPARTAMENTO es obligatorio'}), 400
        
        if not forma_pago or not forma_pago.strip():
            return jsonify({'success': False, 'message': 'FORMA DE PAGO es obligatorio'}), 400
        
        # Validar que la factura tenga fecha de emisión (requerida para estructura de carpetas)
        if not factura.fecha_emision:
            return jsonify({
                'success': False, 
                'message': 'La factura no tiene fecha de emisión. No se puede determinar la ubicación final.'
            }), 400
        
        # Actualizar campos en BD
        factura.empresa = empresa
        factura.departamento = departamento
        factura.forma_pago = forma_pago
        factura.tipo_documento = tipo_documento if tipo_documento else None
        factura.tipo_servicio = tipo_servicio if tipo_servicio else None
        factura.observaciones = observaciones if observaciones else None
        factura.estado = 'pendiente_firma'  # Cambiar a pendiente_firma
        
        log_security(
            f"ESCENARIO 3 - COMPLETAR CAMPOS | factura_id={id} | "
            f"empresa={empresa} | departamento={departamento} | forma_pago={forma_pago} | "
            f"fecha_emision={factura.fecha_emision.strftime('%Y-%m-%d') if factura.fecha_emision else 'SIN_FECHA'}"
        )
        
        # ========================================
        # ðŸ”¥ MOVER ARCHIVOS A UBICACIÃ“N FINAL CORRECTA
        # ========================================
        # Obtener configuración de rutas
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        ruta_base = obtener_ruta_base()
        
        # ðŸ“ CONSTRUIR RUTA FINAL: {EMPRESA}/{AÃ‘O}/{MES}/{DEPARTAMENTO}/{FORMA_PAGO}/
        # âš ï¸ USAR FECHA DE EMISIÃ“N DE LA FACTURA (NO datetime.now())
        año = factura.fecha_emision.year
        mes = f"{factura.fecha_emision.month:02d}"
        
        # ðŸ”§ CONSTRUIR NOMBRE DE CARPETA DE LA FACTURA: {NIT}-{PREFIJO}-{FOLIO}
        nombre_carpeta_factura = f"{factura.nit_proveedor}-{factura.numero_factura}"
        
        nueva_ruta = os.path.join(
            ruta_base,
            empresa,           # SC, LG, etc.
            str(año),          # 2025
            mes,               # 01, 02, etc.
            departamento,      # TIC, DOM, CYS, etc.
            forma_pago,        # CREDITO, CONTADO, etc.
            nombre_carpeta_factura  # 14652319-RI-45
        )
        
        # ðŸ”§ CREAR TODA LA ESTRUCTURA DE CARPETAS (empresa/año/mes/depto/pago/nit-prefijo-folio)
        print(f"ðŸ“ Creando estructura de carpetas: {nueva_ruta}")
        try:
            os.makedirs(nueva_ruta, exist_ok=True)
            print(f"âœ… Estructura creada exitosamente")
        except Exception as e:
            print(f"âŒ Error creando carpetas: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error al crear estructura de carpetas: {str(e)}'
            }), 500
        
        # ðŸ”¥ MOVER ARCHIVOS SI LA RUTA ACTUAL ES DIFERENTE A LA NUEVA
        if factura.ruta_carpeta and os.path.normpath(factura.ruta_carpeta) != os.path.normpath(nueva_ruta):
            
            # ðŸ”§ NORMALIZAR RUTA ORIGEN (convertir relativa a absoluta si es necesario)
            ruta_origen = factura.ruta_carpeta
            
            # Si la ruta es relativa o está mal formada, intentar corregirla
            if not os.path.isabs(ruta_origen) or ruta_origen.startswith('/'):
                # Ruta relativa o con formato Unix â†’ convertir a absoluta
                print(f"âš ï¸ Ruta origen es relativa o mal formada: {ruta_origen}")
                
                # Intentar diferentes combinaciones para encontrar la carpeta
                posibles_rutas = [
                    os.path.join('D:', ruta_origen.lstrip('/')),  # D:/2025/12...
                    os.path.join('D:\\', ruta_origen.lstrip('/')),  # D:\2025\12...
                    os.path.join(ruta_base, ruta_origen.lstrip('/')),  # D:/facturas_digitales/2025/12...
                ]
                
                ruta_encontrada = None
                for posible_ruta in posibles_rutas:
                    ruta_normalizada = os.path.normpath(posible_ruta)
                    print(f"   Probando: {ruta_normalizada}")
                    if os.path.exists(ruta_normalizada):
                        ruta_encontrada = ruta_normalizada
                        print(f"   âœ… Encontrada en: {ruta_encontrada}")
                        break
                
                if ruta_encontrada:
                    ruta_origen = ruta_encontrada
                    print(f"âœ… Ruta origen corregida a: {ruta_origen}")
                else:
                    print(f"âŒ NO se encontró la carpeta origen en ninguna ubicación")
                    log_security(f"âš ï¸ CARPETA ORIGEN NO ENCONTRADA | factura_id={id} | ruta_bd={factura.ruta_carpeta}")
                    return jsonify({
                        'success': False, 
                        'message': f'No se encontró la carpeta origen. Ruta en BD: {factura.ruta_carpeta}'
                    }), 400
            
            # Validar que carpeta origen existe (después de normalizar)
            if not os.path.exists(ruta_origen):
                print(f"âŒ Carpeta origen NO existe: {ruta_origen}")
                log_security(f"âš ï¸ CARPETA ORIGEN NO EXISTE | factura_id={id} | ruta={ruta_origen}")
                return jsonify({
                    'success': False, 
                    'message': f'La carpeta origen no existe: {ruta_origen}'
                }), 400
            
            print(f"ðŸ“¦ Moviendo archivos...")
            print(f"   Desde: {ruta_origen}")
            print(f"   Hacia: {nueva_ruta}")
            
            # Mover todos los archivos
            import shutil
            archivos_movidos = 0
            errores = []
            
            for archivo in os.listdir(ruta_origen):
                origen = os.path.join(ruta_origen, archivo)
                destino = os.path.join(nueva_ruta, archivo)
                
                if os.path.isfile(origen):
                    try:
                        # Si archivo ya existe en destino, agregar sufijo
                        if os.path.exists(destino):
                            nombre, ext = os.path.splitext(archivo)
                            contador = 1
                            while os.path.exists(destino):
                                destino = os.path.join(nueva_ruta, f"{nombre}_{contador}{ext}")
                                contador += 1
                        
                        shutil.move(origen, destino)
                        archivos_movidos += 1
                        print(f"âœ… Movido: {archivo} -> {nueva_ruta}")
                    except Exception as e:
                        errores.append(f"{archivo}: {str(e)}")
                        print(f"âŒ Error moviendo {archivo}: {str(e)}")
            
            # Eliminar carpeta origen vacÍa (y carpetas padre si están vacÍas)
            ruta_origen_original = ruta_origen  # Guardar para logs
            try:
                # Verificar si carpeta origen quedó vacÍa
                if os.path.exists(ruta_origen) and not os.listdir(ruta_origen):
                    os.rmdir(ruta_origen)  # Elimina carpeta de factura
                    print(f"âœ… Carpeta origen eliminada (vacÍa): {ruta_origen}")
                    
                    # Intentar eliminar carpetas padres vacÍas (TEMPORALES/NIT o año/mes/depto)
                    carpeta_padre = os.path.dirname(ruta_origen)
                    while carpeta_padre and carpeta_padre != ruta_base and carpeta_padre != 'D:\\':
                        if os.path.exists(carpeta_padre) and not os.listdir(carpeta_padre):
                            os.rmdir(carpeta_padre)
                            print(f"âœ… Carpeta padre eliminada (vacÍa): {carpeta_padre}")
                            carpeta_padre = os.path.dirname(carpeta_padre)
                        else:
                            break
                else:
                    print(f"â„¹ï¸ Carpeta origen NO eliminada (aún tiene archivos o no existe)")
            except Exception as e:
                print(f"âš ï¸ No se pudo eliminar carpeta origen: {str(e)}")
            
            # ðŸ”¥ ACTUALIZAR RUTA EN BASE DE DATOS
            factura.ruta_carpeta = nueva_ruta
            print(f"âœ… Ruta actualizada en BD: {nueva_ruta}")
            
            log_security(
                f"ARCHIVOS MOVIDOS | factura_id={id} | "
                f"nit={factura.nit_proveedor} | numero={factura.numero_factura} | "
                f"archivos_movidos={archivos_movidos} | errores={len(errores)} | "
                f"desde={ruta_origen_original} | "
                f"hacia={nueva_ruta}"
            )
            
            if errores:
                print(f"âš ï¸ Errores durante movimiento: {errores}")
        else:
            # ðŸ”§ NO SE MOVIERON ARCHIVOS (ruta ya es correcta o no existe carpeta origen)
            print(f"â„¹ï¸ NO se movieron archivos:")
            print(f"   Ruta actual: {factura.ruta_carpeta}")
            print(f"   Ruta esperada: {nueva_ruta}")
            if factura.ruta_carpeta:
                if os.path.normpath(factura.ruta_carpeta) == os.path.normpath(nueva_ruta):
                    print(f"   âœ… Ruta ya es correcta")
                else:
                    print(f"   âš ï¸ Las rutas son diferentes pero no se movieron archivos")
            
            # Actualizar ruta en BD de todas formas
            factura.ruta_carpeta = nueva_ruta
            print(f"âœ… Ruta actualizada en BD: {nueva_ruta}")
        
        db.session.commit()
        
        log_security(f"FACTURA ACTUALIZADA | id={id} | usuario={session.get('usuario')} | empresa={empresa} | depto={departamento} | estado=pendiente_firma")
        
        return jsonify({
            'success': True,
            'message': 'Factura actualizada correctamente. Archivos movidos a ubicación final.',
            'nueva_ruta': factura.ruta_carpeta,
            'estado': factura.estado
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"âŒ Error actualizando factura: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@facturas_digitales_bp.route('/listar-archivos/<int:id>')
@requiere_permiso_html('facturas_digitales', 'ver_detalle_factura')
def listar_archivos(id):
    """
    ðŸ”¥ SOLUCIÃ“N RADICAL: Lista TODOS los archivos PDF de la factura para navegación
    Retorna JSON con metadata de cada archivo
    """
    try:
        factura = FacturaDigital.query.get_or_404(id)
        
        # Obtener configuración de rutas
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        ruta_base = obtener_ruta_base()
        
        # Construir ruta de la carpeta
        if not factura.ruta_carpeta:
            return jsonify({
                'success': False,
                'error': 'Factura sin carpeta de archivos'
            }), 404
        
        carpeta_factura = os.path.join(ruta_base, factura.ruta_carpeta)
        
        if not os.path.exists(carpeta_factura):
            return jsonify({
                'success': False,
                'error': f'Carpeta no encontrada: {carpeta_factura}'
            }), 404
        
        # ðŸ“‹ LISTAR TODOS LOS PDFs en orden
        archivos_info = []
        archivos = os.listdir(carpeta_factura)
        
        log_security(f"ðŸ“ CARPETA: {carpeta_factura}")
        log_security(f"ðŸ“„ ARCHIVOS ENCONTRADOS: {archivos}")
        
        # Función auxiliar para detectar ANEXO (con _ o con -)
        # DEBE tener -ANEXO o _ANEXO especÍficamente, NO solo la palabra ANEXO
        def es_anexo(nombre):
            nombre_upper = nombre.upper()
            # Buscar patrones especÍficos: -ANEXO, _ANEXO seguidos de número o extensión
            import re
            # Patrón: guion/underscore + ANEXO + número opcional + extensión
            patron = r'[-_]ANEXO\d*\.PDF$'
            es = bool(re.search(patron, nombre_upper))
            if es:
                log_security(f"  ðŸ“Ž ANEXO detectado: {nombre}")
            return es
        
        # Función auxiliar para detectar SEGURIDAD SOCIAL (múltiples variantes)
        def es_seguridad_social(nombre):
            nombre_upper = nombre.upper()
            import re
            # Patrón flexible: SEG_SOCIAL, SEG-SOCIAL, _SS, -SS, etc.
            patron = r'[-_](SEG_SOCIAL|SEG-SOCIAL|SEGURIDAD|SS)\.?PDF$'
            es = bool(re.search(patron, nombre_upper))
            if es:
                log_security(f"  ðŸ¥ SEG.SOCIAL detectado: {nombre}")
            return es
        
        # 1. Archivo PRINCIPAL (el que NO es anexo ni seguridad social)
        for archivo in archivos:
            if archivo.lower().endswith('.pdf'):
                if not es_anexo(archivo) and not es_seguridad_social(archivo):
                    archivos_info.append({
                        'tipo': 'ðŸ“„ PRINCIPAL',
                        'nombre': archivo,
                        'orden': 1
                    })
                    log_security(f"  âœ… PRINCIPAL detectado: {archivo}")
                    break
        
        # 2. ANEXOS (ordenados) - Detecta _ANEXO, -ANEXO, ANEXO
        anexos = []
        for archivo in archivos:
            if archivo.lower().endswith('.pdf') and es_anexo(archivo):
                anexos.append(archivo)
                log_security(f"  ðŸ“Ž ANEXO detectado: {archivo}")
        
        for idx, archivo in enumerate(sorted(anexos), start=1):
            archivos_info.append({
                'tipo': f'ðŸ“Ž ANEXO {idx}',
                'nombre': archivo,
                'orden': 2 + idx
            })
        
        # 3. SEGURIDAD SOCIAL
        seg_social = []
        for archivo in archivos:
            if archivo.lower().endswith('.pdf') and es_seguridad_social(archivo):
                seg_social.append(archivo)
                log_security(f"  ðŸ¥ SEG.SOCIAL detectado: {archivo}")
        
        for idx, archivo in enumerate(sorted(seg_social), start=1):
            archivos_info.append({
                'tipo': f'ðŸ¥ SEGURIDAD SOCIAL {idx}',
                'nombre': archivo,
                'orden': 1000 + idx
            })
        
        if not archivos_info:
            return jsonify({
                'success': False,
                'error': 'No se encontraron archivos PDF'
            }), 404
        
        log_security(f"ðŸ“‚ ARCHIVOS LISTADOS | factura_id={id} | total={len(archivos_info)} | usuario={session.get('usuario', 'desconocido')}")
        
        return jsonify({
            'success': True,
            'factura_id': id,
            'numero_factura': factura.numero_factura,
            'total_archivos': len(archivos_info),
            'archivos': archivos_info
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error al listar archivos: {str(e)}'
        }), 500


@facturas_digitales_bp.route('/ver-pdf/<int:id>')
@facturas_digitales_bp.route('/ver-pdf/<int:id>/<path:nombre_archivo>')
@requiere_permiso_html('facturas_digitales', 'ver_detalle_factura')
def ver_pdf(id, nombre_archivo=None):
    """
    ðŸ”¥ SOLUCIÃ“N RADICAL: Sirve UN archivo especÍfico o el principal
    Permite navegación archivo por archivo
    """
    try:
        factura = FacturaDigital.query.get_or_404(id)
        
        # Obtener configuración de rutas
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        ruta_base = obtener_ruta_base()
        
        # Construir ruta de la carpeta
        if not factura.ruta_carpeta:
            return jsonify({
                'success': False,
                'error': 'Factura sin carpeta de archivos'
            }), 404
        
        carpeta_factura = os.path.join(ruta_base, factura.ruta_carpeta)
        
        if not os.path.exists(carpeta_factura):
            return jsonify({
                'success': False,
                'error': f'Carpeta no encontrada: {carpeta_factura}'
            }), 404
        
        # Función auxiliar para detectar ANEXO (con _ o con -)
        def es_anexo(nombre):
            nombre_upper = nombre.upper()
            import re
            patron = r'[-_]ANEXO\d*\.PDF$'
            return bool(re.search(patron, nombre_upper))
        
        # Función auxiliar para detectar SEGURIDAD SOCIAL
        def es_seguridad_social(nombre):
            nombre_upper = nombre.upper()
            import re
            patron = r'[-_](SEG_SOCIAL|SEG-SOCIAL|SEGURIDAD|SS)\.?PDF$'
            return bool(re.search(patron, nombre_upper))
        
        # Si se especifica nombre_archivo, buscar ese archivo
        if nombre_archivo:
            ruta_archivo = os.path.join(carpeta_factura, nombre_archivo)
        else:
            # Sin nombre especÍfico: buscar el PRINCIPAL (el que NO es anexo ni seg. social)
            archivos = os.listdir(carpeta_factura)
            ruta_archivo = None
            for archivo in archivos:
                if archivo.lower().endswith('.pdf'):
                    if not es_anexo(archivo) and not es_seguridad_social(archivo):
                        ruta_archivo = os.path.join(carpeta_factura, archivo)
                        nombre_archivo = archivo
                        break
        
        if not ruta_archivo or not os.path.exists(ruta_archivo):
            return jsonify({
                'success': False,
                'error': f'Archivo no encontrado: {nombre_archivo}'
            }), 404
        
        log_security(f"ðŸ“„ PDF SERVIDO | factura_id={id} | archivo={nombre_archivo} | usuario={session.get('usuario', 'desconocido')}")
        
        # Servir el archivo especÍfico
        return send_file(
            ruta_archivo,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=nombre_archivo
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error al servir PDF: {str(e)}'
        }), 500


@facturas_digitales_bp.route('/abrir-adobe/<int:id>', methods=['POST'])
@requiere_permiso_html('facturas_digitales', 'ver_detalle_factura')
def abrir_adobe(id):
    """
    Endpoint para abrir PDF con Adobe para edición y firma
    """
    try:
        factura = FacturaDigital.query.get_or_404(id)
        
        # Usar ruta_archivo directamente
        ruta_archivo = factura.ruta_archivo
        
        if not os.path.exists(ruta_archivo):
            # Intentar construir desde ruta_carpeta si existe
            if factura.ruta_carpeta and factura.ruta_archivo_principal:
                config = ConfigRutasFacturas.query.filter_by(activa=True).first()
                ruta_base = obtener_ruta_base()
                ruta_archivo = os.path.join(ruta_base, factura.ruta_carpeta, factura.ruta_archivo_principal)
            
            if not os.path.exists(ruta_archivo):
                return jsonify({
                    'success': False,
                    'error': f'Archivo no encontrado: {ruta_archivo}'
                }), 404
        
        # Intentar abrir con Adobe Reader
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                # Rutas comunes de Adobe Reader en Windows
                adobe_paths = [
                    r'C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe',
                    r'C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe',
                    r'C:\Program Files (x86)\Adobe\Reader 11.0\Reader\AcroRd32.exe'
                ]
                
                adobe_exe = None
                for path in adobe_paths:
                    if os.path.exists(path):
                        adobe_exe = path
                        break
                
                if adobe_exe:
                    subprocess.Popen([adobe_exe, ruta_archivo])
                    return jsonify({
                        'success': True,
                        'message': 'Documento abierto con Adobe Reader'
                    })
                else:
                    # Si no encuentra Adobe, abrir con aplicación predeterminada
                    os.startfile(ruta_archivo)
                    return jsonify({
                        'success': True,
                        'message': 'Documento abierto con aplicación predeterminada'
                    })
            else:
                # Para Linux/Mac
                subprocess.Popen(['xdg-open', ruta_archivo])
                return jsonify({
                    'success': True,
                    'message': 'Documento abierto'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error al abrir documento: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@facturas_digitales_bp.route('/api/enviar-firma-masiva', methods=['POST'])
@requiere_permiso('facturas_digitales', 'enviar_a_firmar')
def enviar_firma_masiva():
    """
    Endpoint para enviar múltiples facturas a firmar
    Agrupa facturas por departamento y envÍa UN correo por firmador
    """
    try:
        from utils_notificaciones import enviar_notificacion_firma
        from flask_mail import Mail
        from collections import defaultdict
        
        data = request.get_json()
        ids = data.get('ids', [])
        
        if not ids:
            return jsonify({
                'success': False,
                'message': 'No se proporcionaron facturas para enviar'
            }), 400
        
        # Validar que todas las facturas existan
        facturas = FacturaDigital.query.filter(FacturaDigital.id.in_(ids)).all()
        
        if len(facturas) != len(ids):
            return jsonify({
                'success': False,
                'message': 'Algunas facturas no existen'
            }), 404
        
        # 1. Agrupar facturas por departamento
        facturas_por_depto = defaultdict(list)
        for factura in facturas:
            if factura.estado not in ['firmada', 'pagada']:
                facturas_por_depto[factura.departamento].append({
                    'id': factura.id,
                    'numero_factura': factura.numero_factura,  # CORREGIDO: usar numero_factura en lugar de prefijo/folio
                    'proveedor': factura.razon_social_proveedor,  # CORREGIDO: campo correcto
                    'valor': float(factura.valor_total),  # CORREGIDO: campo correcto
                    'fecha_expedicion': factura.fecha_emision.strftime('%Y-%m-%d') if factura.fecha_emision else 'N/A'  # CORREGIDO: campo correcto
                })
        
        if not facturas_por_depto:
            return jsonify({
                'success': False,
                'message': 'Todas las facturas seleccionadas ya están firmadas o pagadas'
            }), 400
        
        # 2. Por cada departamento, obtener firmadores y enviar correo
        correos_enviados = 0
        detalle_envios = []
        errores = []
        
        for departamento, lista_facturas in facturas_por_depto.items():
            # Consultar usuarios con permisos de firma en el departamento
            # Usando query directo con SQL por simplicidad
            firmadores_result = db.session.execute(text("""
                SELECT DISTINCT u.id, u.usuario, u.correo, u.email_notificaciones, u.tercero_id
                FROM usuarios u
                INNER JOIN usuario_departamento ud ON u.id = ud.usuario_id
                WHERE ud.departamento = :departamento
                AND ud.puede_firmar = true
                AND ud.activo = true
                AND u.activo = true
            """), {'departamento': departamento}).fetchall()
            
            if not firmadores_result:
                # âš ï¸ ALERTA: Departamento sin firmadores configurados
                mensaje_alerta = f"âš ï¸ Departamento {departamento}: No tiene usuarios configurados para firmar"
                errores.append(mensaje_alerta)
                log_security(f"ALERTA SIN FIRMADOR | departamento={departamento} | facturas={len(lista_facturas)}")
                
                # Agregar a detalle de envÍos como "sin enviar"
                detalle_envios.append({
                    'departamento': departamento,
                    'firmador': 'SIN CONFIGURAR',
                    'email': 'N/A',
                    'cantidad': len(lista_facturas),
                    'estado': 'sin_firmador'
                })
                continue
            
            # Enviar correo a cada firmador del departamento
            mail_instance = Mail(current_app)
            for firmador_row in firmadores_result:
                firmador_id, usuario, correo, email_notificaciones, tercero_id = firmador_row
                
                # Email destino (priorizar email_notificaciones)
                email_destino = email_notificaciones or correo
                
                if not email_destino:
                    errores.append(f"{usuario} (Depto {departamento}): Sin email configurado")
                    continue
                
                # CORREGIDO: Usar el nombre de usuario directamente (no el tercero)
                # El firmador es un usuario interno, no la empresa
                nombre_firmador = usuario
                
                # Log antes de enviar
                log_security(f"INTENTANDO ENVIAR FIRMA | destinatario={email_destino} | firmador={nombre_firmador} | depto={departamento} | facturas={len(lista_facturas)}")
                
                # Enviar notificación
                try:
                    success, mensaje = enviar_notificacion_firma(
                        mail_instance,
                        email_destino,
                        nombre_firmador,
                        departamento,
                        lista_facturas
                    )
                    
                    if success:
                        correos_enviados += 1
                        detalle_envios.append({
                            'departamento': departamento,
                            'firmador': nombre_firmador,
                            'email': email_destino,
                            'cantidad': len(lista_facturas)
                        })
                        log_security(f"âœ… CORREO FIRMA ENVIADO | destinatario={email_destino} | depto={departamento}")
                    else:
                        errores.append(f"{nombre_firmador} ({departamento}): {mensaje}")
                        log_security(f"âŒ ERROR ENVIO FIRMA | destinatario={email_destino} | error={mensaje}")
                except Exception as e:
                    error_msg = str(e)
                    errores.append(f"{nombre_firmador} ({departamento}): {error_msg}")
                    log_security(f"âŒ EXCEPCION ENVIO FIRMA | destinatario={email_destino} | error={error_msg}")
        
        # 3. Actualizar estado de todas las facturas con trazabilidad completa
        contador_actualizadas = 0
        usuario_actual = session.get('usuario', 'desconocido')
        from utils_fecha import obtener_fecha_naive_colombia
        fecha_actual = obtener_fecha_naive_colombia()
        
        # IDs de facturas a actualizar (excluyendo firmadas/pagadas)
        ids_actualizar = []
        
        for factura in facturas:
            # VALIDACIÃ“N: No permitir re-envÍo si ya está firmada o pagada
            if factura.estado in ['firmada', 'pagada']:
                errores.append(f"Factura {factura.numero_factura}: Ya está en estado {factura.estado}, no se puede re-enviar")
                continue
            
            ids_actualizar.append(factura.id)
            log_security(f"FACTURA ENVIADA A FIRMA | id={factura.id} | numero={factura.numero_factura} | usuario={usuario_actual} | fecha={fecha_actual}")
        
        # UPDATE masivo con SQLAlchemy para asegurar persistencia
        if ids_actualizar:
            try:
                # Formatear fecha para PostgreSQL
                fecha_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')
                
                # UPDATE explÍcito de la factura (último envÍo)
                update_query = text("""
                    UPDATE facturas_digitales 
                    SET 
                        estado = 'enviado_a_firmar',
                        estado_firma = 'PENDIENTE',
                        fecha_envio_firma = :fecha,
                        usuario_envio_firma = :usuario
                    WHERE id = ANY(:ids)
                """)
                
                result = db.session.execute(update_query, {
                    'fecha': fecha_str,
                    'usuario': usuario_actual,
                    'ids': ids_actualizar
                })
                
                contador_actualizadas = result.rowcount
                
                # NUEVO: Insertar en historial de envÍos (TODAS las veces)
                for factura_id in ids_actualizar:
                    # Buscar email y departamento de la factura
                    factura_info = next((f for f in facturas if f.id == factura_id), None)
                    if factura_info:
                        # Buscar el email del departamento enviado
                        depto = factura_info.departamento
                        email_firmador = None
                        
                        for dept, facturas_list in facturas_por_depto.items():
                            if dept == depto and facturas_list:
                                # Encontrar firmador de este departamento
                                for detalle in detalle_envios:
                                    if detalle['departamento'] == dept:
                                        email_firmador = detalle['email']
                                        break
                                break
                        
                        # Insertar en historial
                        insert_historial = text("""
                            INSERT INTO historial_envios_firma 
                            (factura_id, fecha_envio, usuario_envio, destinatario_email, departamento)
                            VALUES (:factura_id, :fecha, :usuario, :email, :depto)
                        """)
                        
                        db.session.execute(insert_historial, {
                            'factura_id': factura_id,
                            'fecha': fecha_str,
                            'usuario': usuario_actual,
                            'email': email_firmador,
                            'depto': depto
                        })
                
                db.session.commit()
                
                # Refrescar la sesión para que las próximas queries vean los cambios
                db.session.expire_all()
                
                log_security(f"âœ… COMMIT EXITOSO | facturas_actualizadas={contador_actualizadas} | ids={ids_actualizar} | historial_guardado=True")
                
            except Exception as e_commit:
                db.session.rollback()
                log_security(f"âŒ ERROR COMMIT | error={str(e_commit)}")
                raise
        else:
            log_security(f"âš ï¸ No hay facturas para actualizar (todas firmadas/pagadas)")
        
        # 4. Preparar respuesta
        respuesta = {
            'success': True,
            'facturas_actualizadas': contador_actualizadas,
            'correos_enviados': correos_enviados,
            'departamentos_procesados': len(facturas_por_depto),
            'detalle': detalle_envios
        }
        
        if errores:
            respuesta['advertencias'] = errores
        
        # Mensaje final mejorado
        mensaje_final = f"âœ… {contador_actualizadas} factura(s) actualizadas. "
        
        if correos_enviados > 0:
            mensaje_final += f"ðŸ“§ {correos_enviados} correo(s) enviado(s). "
        
        # Identificar departamentos sin firmadores
        deptos_sin_firmador = [d for d in detalle_envios if d.get('estado') == 'sin_firmador']
        if deptos_sin_firmador:
            deptos_nombres = ', '.join([d['departamento'] for d in deptos_sin_firmador])
            mensaje_final += f"\nâš ï¸ ALERTA: Departamento(s) {deptos_nombres} no tienen firmadores configurados. "
            mensaje_final += f"Las facturas se actualizaron pero NO se envió correo."
        
        if errores:
            mensaje_final += f"\nðŸ“‹ {len(errores)} advertencia(s)."
        
        respuesta['message'] = mensaje_final
        
        return jsonify(respuesta)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al enviar facturas: {str(e)}'
        }), 500


@facturas_digitales_bp.route('/enviar-firmar/<int:id>', methods=['POST'])
@requiere_permiso('facturas_digitales', 'enviar_a_firmar')
def enviar_firmar(id):
    """
    Endpoint para enviar documento a firmar (individual)
    Cambia el estado a 'enviado_a_firmar'
    """
    try:
        factura = FacturaDigital.query.get_or_404(id)
        
        # Obtener datos del formulario
        data = request.get_json()
        destinatario = data.get('destinatario')
        mensaje = data.get('mensaje', '')
        
        if not destinatario:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar un destinatario'
            }), 400
        
        # Cambiar estado a 'enviado_a_firmar'
        factura.estado = 'enviado_a_firmar'
        
        # Registrar en log o tabla de seguimiento (opcional)
        # TODO: Implementar envÍo real de correo o integración con sistema de firmas
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Documento enviado a firmar a {destinatario}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@facturas_digitales_bp.route('/descargar-factura/<int:id>')
@requiere_permiso_html('facturas_digitales', 'descargar_soportes')
def descargar_factura(id):
    """
    ðŸ”¥ DESCARGA TODOS LOS ARCHIVOS (PRINCIPAL + ANEXOS + SEG. SOCIAL) como ZIP
    Endpoint alternativo con nombre diferente para evitar conflicto
    """
    if 'usuario' not in session:
        return redirect(url_for('index'))
    
    factura = FacturaDigital.query.get_or_404(id)
    
    # Verificar permisos
    tipo_usuario = session.get('tipo_usuario', 'interno')
    if tipo_usuario == 'externo':
        nit_proveedor = session.get('nit')
        if factura.nit_proveedor != nit_proveedor:
            return "No autorizado", 403
    
    # Obtener configuración de rutas
    config = ConfigRutasFacturas.query.filter_by(activa=True).first()
    ruta_base = obtener_ruta_base()
    
    if not factura.ruta_carpeta:
        return jsonify({'error': 'Factura sin carpeta de archivos'}), 404
    
    carpeta_factura = os.path.join(ruta_base, factura.ruta_carpeta)
    
    if not os.path.exists(carpeta_factura):
        return jsonify({'error': 'Carpeta no encontrada'}), 404
    
    # Crear archivo ZIP temporal con TODOS los PDFs
    import tempfile
    import zipfile
    
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    try:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar TODOS los archivos PDF de la carpeta
            archivos = os.listdir(carpeta_factura)
            contador = 0
            for archivo in archivos:
                if archivo.lower().endswith('.pdf'):
                    ruta_completa = os.path.join(carpeta_factura, archivo)
                    zipf.write(ruta_completa, arcname=archivo)
                    contador += 1
        
        temp_zip.close()
        
        # Nombre del ZIP: debe coincidir con el nombre de la carpeta (NIT-PREFIJO-FOLIO)
        # Extraer nombre de carpeta desde ruta_carpeta (ej: 805013653/805013653-DS-14/ -> 805013653-DS-14)
        nombre_carpeta = os.path.basename(factura.ruta_carpeta.rstrip('/\\'))
        nombre_zip = f"{nombre_carpeta}.zip"
        
        log_security(f"ðŸ“¦ ZIP DESCARGADO | factura_id={id} | archivos={contador} | nombre={nombre_zip} | usuario={session.get('usuario', 'desconocido')}")
        
        # Enviar el ZIP
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name=nombre_zip,
            mimetype='application/zip'
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al crear ZIP: {str(e)}'}), 500

# =====================================================
# MÃ“DULO DE Ã“RDENES DE COMPRA (OCR)
# =====================================================

@facturas_digitales_bp.route('/ordenes-compra')
def ordenes_compra():
    """Formulario para generar órdenes de compra"""
    # Validar sesión
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
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


@facturas_digitales_bp.route('/api/ordenes-compra/centros-operacion')
def listar_centros_operacion_ocr():
    """Listar centros de operación con tipos desde columnas booleanas"""
    try:
        from sqlalchemy import text
        
        result = db.session.execute(text("""
            SELECT 
                id, 
                codigo, 
                nombre, 
                ciudad, 
                estado,
                almacen,
                bodega,
                c_comercial,
                otros,
                mayorista,
                asaderos,
                panaderias,
                domicilios
            FROM centros_operacion
            WHERE estado = 'ACTIVO'
            ORDER BY codigo
        """))
        
        centros = []
        for row in result:
            # Determinar los tipos activos (pueden ser múltiples)
            tipos = []
            if row[5]:  # almacen
                tipos.append('almacen')
            if row[6]:  # bodega
                tipos.append('bodega')
            if row[7]:  # c_comercial
                tipos.append('c_comercial')
            if row[8]:  # otros
                tipos.append('otros')
            if row[9]:  # mayorista
                tipos.append('mayorista')
            if row[10]:  # asaderos
                tipos.append('asaderos')
            if row[11]:  # panaderias
                tipos.append('panaderias')
            if row[12]:  # domicilios
                tipos.append('domicilios')
            
            # Si no tiene ningún tipo, marcar como 'otro'
            if not tipos:
                tipos.append('otro')
            
            centros.append({
                'id': row[0],
                'codigo': row[1],
                'nombre': row[2],
                'ciudad': row[3],
                'tipos': tipos,  # Array de tipos
                'tipo': tipos[0]  # Tipo principal (para compatibilidad)
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
        
        # Construir razón social completa según tipo de persona
        razon_social = tercero.razon_social
        if not razon_social and tercero.tipo_persona == 'natural':
            # Si es persona natural y no tiene razón social, construirla con nombres
            nombres = []
            if tercero.primer_nombre:
                nombres.append(tercero.primer_nombre)
            if tercero.segundo_nombre:
                nombres.append(tercero.segundo_nombre)
            if tercero.primer_apellido:
                nombres.append(tercero.primer_apellido)
            if tercero.segundo_apellido:
                nombres.append(tercero.segundo_apellido)
            razon_social = ' '.join(nombres)
        
        return jsonify({
            'success': True,
            'data': {
                'nit': tercero.nit,
                'razon_social': razon_social or 'Sin nombre',
                'direccion': '',  # Campo no existe en tabla terceros
                'telefono': tercero.celular or '',  # Usar celular como teléfono
                'email': tercero.correo or ''
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@facturas_digitales_bp.route('/api/ordenes-compra/crear', methods=['POST'])
@requiere_permiso('facturas_digitales', 'acceder_modulo')
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
            return jsonify({'success': False, 'message': 'Debe agregar al menos un Ítem'}), 400
        
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
@requiere_permiso('facturas_digitales', 'acceder_modulo')
def enviar_correo_orden_compra():
    """Enviar orden de compra por correo electrónico"""
    try:
        data = request.get_json()
        orden_id = data.get('orden_id')
        email_destino = data.get('email_destino')
        
        if not orden_id or not email_destino:
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
        
        # TODO: Implementar generación de PDF y envÍo por correo
        # Por ahora solo simular
        
        log_security(f"ORDEN COMPRA ENVIADA | orden_id={orden_id} | email={email_destino} | usuario={session.get('usuario')}")
        
        return jsonify({
            'success': True,
            'message': f'Orden enviada a {email_destino}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@facturas_digitales_bp.route('/api/ordenes-compra/pdf/<int:orden_id>')
@requiere_permiso('facturas_digitales', 'acceder_modulo')
def descargar_pdf_orden_compra(orden_id):
    """Generar y descargar PDF de la orden de compra"""
    try:
        # TODO: Implementar generación de PDF con reportlab o similar
        return jsonify({'message': 'Funcionalidad de PDF en desarrollo'}), 501
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

