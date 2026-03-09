"""
Script para enviar el reporte PDF por correo usando la configuración del sistema
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def enviar_correo_reporte(pdf_path='reporte_tablas_completo.pdf', destinatario='ricardoriascos07@gmail.com'):
    """Envía el PDF por correo electrónico"""
    print(f"📧 Preparando envío de correo a {destinatario}...")
    
    # Configuración de correo
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', '465'))
    mail_username = os.getenv('MAIL_USERNAME', '')
    mail_password = os.getenv('MAIL_PASSWORD', '')
    mail_sender = os.getenv('MAIL_DEFAULT_SENDER', mail_username)
    use_ssl = os.getenv('MAIL_USE_SSL', 'True') == 'True'
    use_tls = os.getenv('MAIL_USE_TLS', 'False') == 'True'
    
    print(f"   Servidor: {mail_server}:{mail_port}")
    print(f"   SSL: {use_ssl}, TLS: {use_tls}")
    print(f"   Usuario: {mail_username}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: No se encuentra el archivo {pdf_path}")
        return False
    
    tamano_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"   Tamaño del PDF: {tamano_mb:.2f} MB")
    
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = mail_sender
        msg['To'] = destinatario
        msg['Subject'] = f"Reporte Exhaustivo de Base de Datos - {datetime.now().strftime('%d/%m/%Y')}"
        
        # Cuerpo del correo
        cuerpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #166534;">📊 Reporte de Base de Datos - Sistema Gestor Documental</h2>
            <p>Estimado Ricardo,</p>
            <p>Adjunto encontrarás el <b>análisis exhaustivo y completo</b> de las <b>94 tablas</b> de la base de datos PostgreSQL del Sistema Gestor Documental.</p>
            
            <h3>📋 Este reporte incluye:</h3>
            <ul>
                <li>✅ Nombre completo de cada tabla</li>
                <li>✅ Lista detallada de todos los campos con tipos de datos</li>
                <li>✅ Número exacto de registros almacenados</li>
                <li>✅ Fecha de última modificación (cuando es detectable)</li>
                <li>✅ Módulos del sistema que interactúan con cada tabla</li>
                <li>✅ Operaciones realizadas (INSERT, UPDATE, DELETE, SELECT)</li>
                <li>✅ Relaciones entre tablas (Foreign Keys)</li>
                <li>✅ Estado funcional de cada tabla (Activa/Poco Uso/Configurada/No Funcional)</li>
                <li>✅ Resumen ejecutivo con estadísticas generales</li>
            </ul>
            
            <div style="background-color: #f0fdf4; padding: 15px; border-left: 4px solid #166534; margin: 20px 0;">
                <p style="margin: 0;"><b>📊 Total de tablas analizadas:</b> 94</p>
                <p style="margin: 5px 0;"><b>📁 Archivos de código analizados:</b> 478</p>
                <p style="margin: 5px 0;"><b>📄 Tamaño del reporte:</b> {tamano_mb:.2f} MB</p>
                <p style="margin: 5px 0;"><b>🕐 Generado:</b> {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
            </div>
            
            <p>El documento PDF adjunto contiene toda la información solicitada de manera detallada y organizada, con:</p>
            <ul>
                <li>Resumen ejecutivo con estadísticas generales</li>
                <li>Análisis detallado de cada una de las 94 tablas</li>
                <li>Información de campos, relaciones y uso en el código</li>
                <li>Estado funcional de cada tabla</li>
            </ul>
            
            <p style="margin-top: 30px;">Saludos cordiales,<br>
            <b>Sistema Gestor Documental</b><br>
            Supertiendas Cañaveral</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(cuerpo, 'html'))
        
        # Adjuntar PDF
        print(f"   Adjuntando PDF...")
        with open(pdf_path, 'rb') as f:
            pdf = MIMEApplication(f.read(), _subtype='pdf')
            pdf.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
            msg.attach(pdf)
        
        # Conectar y enviar
        print(f"   Conectando al servidor SMTP...")
        
        if use_ssl:
            # SSL (puerto 465)
            server = smtplib.SMTP_SSL(mail_server, mail_port)
        else:
            # No SSL inicialmente (puerto 587)
            server = smtplib.SMTP(mail_server, mail_port)
            if use_tls:
                server.starttls()
        
        print(f"   Autenticando...")
        server.login(mail_username, mail_password)
        
        print(f"   Enviando mensaje...")
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Correo enviado exitosamente a {destinatario}")
        print(f"   Asunto: {msg['Subject']}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
        print(f"   El archivo PDF está disponible en: {os.path.abspath(pdf_path)}")
        return False

if __name__ == '__main__':
    print("="*70)
    print("ENVÍO DE REPORTE POR CORREO ELECTRÓNICO")
    print("="*70)
    print()
    
    exito = enviar_correo_reporte()
    
    print()
    print("="*70)
    if exito:
        print("✅ CORREO ENVIADO EXITOSAMENTE")
    else:
        print("⚠️ NO SE PUDO ENVIAR EL CORREO")
        print("   El archivo PDF está disponible localmente")
    print("="*70)
