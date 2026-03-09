"""
Script para enviar correo de prueba de confirmación de firma digital
"""
from flask import Flask
from flask_mail import Mail, Message
from sqlalchemy import text
from extensions import db
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:G3st0radm$2025.@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de correo (Gmail - misma que el servidor)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'gestordocumentalsc01@gmail.com'
app.config['MAIL_PASSWORD'] = 'urjrkjlogcfdtynq'
app.config['MAIL_DEFAULT_SENDER'] = 'gestordocumentalsc01@gmail.com'

db.init_app(app)
mail = Mail(app)

def formatear_fecha_segura(fecha, formato='%Y-%m-%d %H:%M:%S'):
    """Formatear fecha de forma segura"""
    if not fecha:
        return 'N/A'
    if isinstance(fecha, str):
        return fecha
    try:
        return fecha.strftime(formato)
    except:
        return str(fecha)

with app.app_context():
    try:
        print("\n" + "="*100)
        print("ENVIANDO CORREO DE PRUEBA - CONFIRMACIÓN FIRMA DIGITAL REL-022")
        print("="*100)
        
        # Usuario de prueba
        usuario = 'admin'
        numero_relacion = 'REL-022'
        
        # Obtener correo del usuario
        result = db.session.execute(
            text("SELECT correo FROM usuarios WHERE usuario = :usuario"),
            {"usuario": usuario}
        ).fetchone()
        
        if not result or not result[0]:
            print(f"\n[ERROR] No se encontró correo para el usuario {usuario}")
            exit(1)
        
        correo_destino = result[0]
        nombre_usuario = usuario
        
        print(f"\n[INFO] Usuario: {nombre_usuario}")
        print(f"[INFO] Correo destino: {correo_destino}")
        print(f"[INFO] Relación: {numero_relacion}")
        
        # Consultar facturas de la relación REL-022
        facturas_query = text("""
            SELECT 
                rf.nit,
                t.razon_social,
                rf.prefijo,
                rf.folio,
                rf.co,
                rf.valor_total,
                rf.fecha_factura
            FROM relaciones_facturas rf
            LEFT JOIN terceros t ON rf.nit = t.nit
            WHERE rf.numero_relacion = :numero_relacion
            ORDER BY rf.prefijo, rf.folio
        """)
        
        facturas = db.session.execute(
            facturas_query,
            {"numero_relacion": numero_relacion}
        ).fetchall()
        
        print(f"\n[INFO] Facturas encontradas: {len(facturas)}")
        
        if not facturas:
            print(f"\n[ERROR] No se encontraron facturas para {numero_relacion}")
            exit(1)
        
        # Generar HTML de las facturas
        facturas_html = ""
        for factura in facturas:
            razon_social = factura.razon_social if factura.razon_social else 'TERCERO NO REGISTRADO'
            
            # ✅ OBTENER C.O. CODIGO Y EMPRESA desde facturas_recibidas
            co_codigo = 'N/A'
            empresa_id = 'N/A'
            try:
                query_extra = db.session.execute(
                    text("""
                        SELECT co.codigo, fr.empresa_id 
                        FROM facturas_recibidas fr
                        LEFT JOIN centros_operacion co ON fr.centro_operacion_id = co.id
                        WHERE fr.nit = :nit AND fr.prefijo = :prefijo AND fr.folio = :folio
                        LIMIT 1
                    """),
                    {"nit": factura.nit, "prefijo": factura.prefijo, "folio": factura.folio}
                ).fetchone()
                if query_extra:
                    co_codigo = query_extra[0] or 'N/A'
                    empresa_id = query_extra[1] or 'N/A'
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
                    <td style='padding: 10px; border: 1px solid #ddd;'>{formatear_fecha_segura(factura.fecha_factura, '%Y-%m-%d')}</td>
                    <td style='padding: 10px; border: 1px solid #ddd; color: green; font-weight: bold;'>✅ RECIBIDA</td>
                </tr>
            """
        
        # Firma de prueba
        fecha_firma = datetime.now()
        firma_prueba = "567b0cc3c1bc7d6f24ef2d8915b31cc84c8f8b1a7cf881f72d5fe2d4cd9a3b35"  # SHA256 de prueba
        
        # HTML del correo
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
                <p><strong>Fecha y Hora:</strong> {formatear_fecha_segura(fecha_firma, '%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Facturas Firmadas:</strong> {len(facturas)}</p>
                
                <h3>📋 Detalle de Facturas Recibidas:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #166534; color: white;">
                            <th style="padding: 10px; border: 1px solid #ddd;">NIT</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Razón Social</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">C.O.</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Empresa</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Factura</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Valor</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Fecha</th>
                            <th style="padding: 10px; border: 1px solid #ddd;">Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {facturas_html}
                    </tbody>
                </table>
                
                <div style="background: #eff6ff; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>🔐 Firma Digital SHA256:</strong></p>
                    <p style="margin: 0; font-family: monospace; word-break: break-all; font-size: 12px;">{firma_prueba}</p>
                </div>
                
                <div style="text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e1e8ed;">
                    <p>Supertiendas Cañaveral - Sistema de Gestión Documental</p>
                    <p style="color: #999; font-style: italic;">Este es un correo de prueba</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Crear y enviar mensaje
        print(f"\n[INFO] Creando mensaje de correo...")
        msg = Message(
            subject=f'✅ Recepción Digital Confirmada - {numero_relacion} [PRUEBA]',
            recipients=[correo_destino],
            html=html_confirmacion
        )
        
        print(f"[INFO] Enviando correo a {correo_destino}...")
        mail.send(msg)
        
        print("\n" + "="*100)
        print("✅ CORREO ENVIADO EXITOSAMENTE")
        print("="*100)
        print(f"\nRevisa la bandeja de entrada de: {correo_destino}")
        print(f"Asunto: ✅ Recepción Digital Confirmada - {numero_relacion} [PRUEBA]\n")
        
    except Exception as e:
        print(f"\n[ERROR] No se pudo enviar el correo: {e}\n")
        import traceback
        traceback.print_exc()
