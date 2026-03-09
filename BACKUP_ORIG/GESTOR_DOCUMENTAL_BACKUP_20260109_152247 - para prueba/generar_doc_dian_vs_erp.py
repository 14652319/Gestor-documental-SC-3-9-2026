"""
Script para generar PDF explicando las tablas del módulo DIAN vs ERP
y enviar por correo
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

load_dotenv()

def crear_pdf_dian_vs_erp():
    """Crea un PDF detallado del módulo DIAN vs ERP"""
    
    filename = 'MODULO_DIAN_VS_ERP_TABLAS.pdf'
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#166534'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitulo_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#166534'),
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    
    seccion_style = ParagraphStyle(
        'CustomSection',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    texto_justificado = ParagraphStyle(
        'Justified',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=10
    )
    
    # ========================================
    # PORTADA
    # ========================================
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("MÓDULO DIAN VS ERP", titulo_style))
    story.append(Paragraph("Documentación Técnica de Tablas y Flujos de Datos", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Sistema Gestor Documental - Supertiendas Cañaveral", styles['Normal']))
    story.append(Paragraph(f"Generado: {datetime.now().strftime('%d de %B de %Y - %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 1*inch))
    
    # Resumen visual
    resumen_data = [
        ['CARACTERÍSTICA', 'VALOR'],
        ['Estado del Módulo', '✅ FUNCIONAL Y OPERATIVO'],
        ['Base de Datos', 'PostgreSQL'],
        ['Tablas Principales', '6 tablas'],
        ['Puerto de Operación', '8099 (integrado)'],
        ['Archivos Procesados', 'CSV/Excel (DIAN, ERP, Acuses)'],
    ]
    
    tabla_resumen = Table(resumen_data, colWidths=[3*inch, 3*inch])
    tabla_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    story.append(tabla_resumen)
    story.append(PageBreak())
    
    # ========================================
    # 1. TABLA PRINCIPAL: maestro_dian_vs_erp
    # ========================================
    story.append(Paragraph("1. TABLA PRINCIPAL: maestro_dian_vs_erp", subtitulo_style))
    story.append(Paragraph("Esta es la <b>tabla central</b> del módulo donde se almacenan <b>TODOS</b> los datos procesados.", texto_justificado))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("📊 <b>FUNCIÓN PRINCIPAL:</b>", seccion_style))
    story.append(Paragraph("""
    Almacena el maestro consolidado de facturas electrónicas, combinando datos de:
    <br/>• <b>Archivos DIAN</b> (reportes de facturas electrónicas emitidas)
    <br/>• <b>Archivos ERP</b> (facturas registradas en el sistema interno)
    <br/>• <b>Archivos de Acuse</b> (confirmaciones de recepción)
    <br/><br/>
    Esta tabla permite realizar el <b>cruce y validación</b> entre lo reportado por la DIAN 
    y lo registrado en el ERP de la empresa, identificando discrepancias, facturas faltantes 
    o errores de registro.
    """, texto_justificado))
    story.append(Spacer(1, 0.15*inch))
    
    # Campos de la tabla
    story.append(Paragraph("📋 <b>CAMPOS DE LA TABLA (40+ campos):</b>", seccion_style))
    
    campos_maestro = [
        ['CAMPO', 'TIPO', 'DESCRIPCIÓN', 'ORIGEN'],
        ['id', 'INTEGER', 'ID único auto-incremental', 'Sistema'],
        ['nit_emisor', 'VARCHAR(20)', 'NIT del proveedor que emitió la factura', 'DIAN'],
        ['razon_social', 'VARCHAR(255)', 'Nombre del proveedor', 'DIAN'],
        ['fecha_emision', 'DATE', 'Fecha de emisión de la factura', 'DIAN'],
        ['prefijo', 'VARCHAR(10)', 'Prefijo de la factura (ej: FE, NC)', 'DIAN'],
        ['folio', 'VARCHAR(20)', 'Número de la factura', 'DIAN'],
        ['valor', 'NUMERIC(15,2)', 'Valor total de la factura', 'DIAN'],
        ['cufe', 'VARCHAR(255)', 'Código Único de Factura Electrónica', 'DIAN'],
        ['tipo_documento', 'VARCHAR(100)', 'Tipo: Factura, Nota Crédito, etc.', 'DIAN'],
        ['estado_aprobacion', 'VARCHAR(100)', 'Estado de aprobación DIAN', 'DIAN'],
        ['forma_pago', 'VARCHAR(100)', '1=Contado, 2=Crédito', 'ERP'],
        ['tipo_servicio', 'VARCHAR(100)', 'Tipo de servicio prestado', 'ERP'],
        ['departamento', 'VARCHAR(100)', 'Departamento responsable', 'ERP'],
        ['tipo_tercero', 'VARCHAR(50)', 'Clasificación del tercero', 'ERP'],
        ['modulo', 'VARCHAR(50)', 'COMERCIAL o FINANCIERO', 'ERP'],
        ['estado_contable', 'VARCHAR(100)', 'Estado contable del documento', 'ERP'],
        ['causada', 'BOOLEAN', 'TRUE si la factura fue causada', 'Sistema'],
        ['fecha_causacion', 'DATETIME', 'Fecha/hora de causación', 'Sistema'],
        ['usuario_causacion', 'VARCHAR(100)', 'Usuario que causó el documento', 'Sistema'],
        ['recibida', 'BOOLEAN', 'TRUE si fue recibida físicamente', 'Sistema'],
        ['fecha_recibida', 'DATETIME', 'Fecha/hora de recepción', 'Sistema'],
        ['acuses_recibidos', 'INTEGER', 'Cantidad de acuses recibidos', 'Acuse'],
        ['acuses_requeridos', 'INTEGER', 'Acuses requeridos (default: 3)', 'Sistema'],
        ['dias_desde_emision', 'INTEGER', 'Días transcurridos desde emisión', 'Calculado'],
        ['doc_causado_por', 'VARCHAR(100)', 'Usuario que causó', 'Sistema'],
    ]
    
    tabla_campos = Table(campos_maestro, colWidths=[1.3*inch, 1.1*inch, 2.2*inch, 0.9*inch])
    tabla_campos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(tabla_campos)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("🎯 <b>DÓNDE SE CARGAN LOS DATOS:</b>", seccion_style))
    story.append(Paragraph("""
    <b>1. Archivos DIAN:</b> Se cargan desde archivos CSV/Excel descargados del portal DIAN
    <br/>&nbsp;&nbsp;&nbsp;• Ubicación física: <font face="Courier"><b>uploads/dian/</b></font>
    <br/>&nbsp;&nbsp;&nbsp;• Función de carga: <font face="Courier">actualizar_maestro()</font> en routes.py línea 504
    <br/>&nbsp;&nbsp;&nbsp;• Campos cargados: nit_emisor, razon_social, fecha_emision, prefijo, folio, valor, cufe, tipo_documento, estado_aprobacion
    <br/><br/>
    <b>2. Archivos ERP (Financiero):</b> Facturas del módulo financiero
    <br/>&nbsp;&nbsp;&nbsp;• Ubicación física: <font face="Courier"><b>uploads/erp_fn/</b></font>
    <br/>&nbsp;&nbsp;&nbsp;• Se combinan con datos DIAN para enriquecer información
    <br/>&nbsp;&nbsp;&nbsp;• Campos adicionales: forma_pago, tipo_servicio, departamento, modulo
    <br/><br/>
    <b>3. Archivos ERP (Comercial):</b> Facturas del módulo comercial
    <br/>&nbsp;&nbsp;&nbsp;• Ubicación física: <font face="Courier"><b>uploads/erp_cm/</b></font>
    <br/>&nbsp;&nbsp;&nbsp;• Similar a ERP Financiero pero para transacciones comerciales
    <br/><br/>
    <b>4. Archivos de Acuse:</b> Confirmaciones de recepción de documentos
    <br/>&nbsp;&nbsp;&nbsp;• Ubicación física: <font face="Courier"><b>uploads/acuses/</b></font>
    <br/>&nbsp;&nbsp;&nbsp;• Actualizan campos: acuses_recibidos, fecha_recibida
    <br/>&nbsp;&nbsp;&nbsp;• Para documentos tipo crédito que requieren múltiples acuses
    """, texto_justificado))
    
    story.append(PageBreak())
    
    # ========================================
    # 2. TABLAS DE CONFIGURACIÓN
    # ========================================
    story.append(Paragraph("2. TABLAS DE CONFIGURACIÓN", subtitulo_style))
    
    # 2.1 envios_programados_dian_vs_erp
    story.append(Paragraph("2.1. envios_programados_dian_vs_erp", seccion_style))
    story.append(Paragraph("""
    <b>Función:</b> Almacena las configuraciones de envíos automáticos de alertas y reportes.
    <br/><br/>
    <b>Casos de uso:</b>
    <br/>• Enviar reporte diario de facturas pendientes de más de 3 días
    <br/>• Alertar sobre documentos a crédito sin acuses mínimos
    <br/>• Notificaciones programadas a usuarios específicos
    """, texto_justificado))
    story.append(Spacer(1, 0.1*inch))
    
    campos_envios = [
        ['CAMPO', 'TIPO', 'DESCRIPCIÓN'],
        ['id', 'INTEGER', 'ID único'],
        ['nombre', 'VARCHAR(200)', 'Nombre descriptivo del envío'],
        ['tipo', 'VARCHAR(50)', 'PENDIENTES_DIAS, CREDITO_SIN_ACUSES'],
        ['dias_minimos', 'INTEGER', 'Días mínimos para considerar pendiente (default: 3)'],
        ['requiere_acuses_minimo', 'INTEGER', 'Acuses mínimos requeridos (default: 2)'],
        ['estados_incluidos', 'TEXT', 'JSON con estados a incluir'],
        ['estados_excluidos', 'TEXT', 'JSON con estados a excluir'],
        ['hora_envio', 'VARCHAR(5)', 'Hora de envío formato HH:MM'],
        ['frecuencia', 'VARCHAR(20)', 'DIARIO, SEMANAL, MENSUAL'],
    ]
    
    tabla_envios = Table(campos_envios, colWidths=[1.8*inch, 1.3*inch, 2.4*inch])
    tabla_envios.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(tabla_envios)
    story.append(Spacer(1, 0.2*inch))
    
    # 2.2 usuarios_asignados_dian_vs_erp
    story.append(Paragraph("2.2. usuarios_asignados_dian_vs_erp", seccion_style))
    story.append(Paragraph("""
    <b>Función:</b> Define qué usuarios reciben alertas para facturas de NITs específicos.
    <br/><br/>
    <b>Ejemplo práctico:</b> Si el usuario juan.perez@empresa.com está asignado al NIT 900123456,
    recibirá alertas automáticas cuando haya facturas pendientes de ese proveedor.
    """, texto_justificado))
    story.append(Spacer(1, 0.1*inch))
    
    campos_usuarios_asig = [
        ['CAMPO', 'TIPO', 'DESCRIPCIÓN'],
        ['id', 'INTEGER', 'ID único'],
        ['nit', 'VARCHAR(20)', 'NIT del proveedor'],
        ['correo', 'VARCHAR(255)', 'Email del usuario que recibe alertas'],
        ['nombre', 'VARCHAR(100)', 'Nombre del usuario'],
        ['activo', 'BOOLEAN', 'TRUE si las alertas están activas'],
    ]
    
    tabla_usuarios_asig = Table(campos_usuarios_asig, colWidths=[1.5*inch, 1.3*inch, 2.7*inch])
    tabla_usuarios_asig.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(tabla_usuarios_asig)
    story.append(Spacer(1, 0.2*inch))
    
    # 2.3 usuarios_causacion_dian_vs_erp
    story.append(Paragraph("2.3. usuarios_causacion_dian_vs_erp", seccion_style))
    story.append(Paragraph("""
    <b>Función:</b> Usuarios autorizados para marcar documentos como "causados" en el sistema.
    <br/><br/>
    <b>Causación:</b> Proceso contable donde se registra una factura en los libros de la empresa.
    Esta tabla mantiene estadísticas de cuántos documentos ha causado cada usuario.
    """, texto_justificado))
    story.append(Spacer(1, 0.1*inch))
    
    campos_usuarios_caus = [
        ['CAMPO', 'TIPO', 'DESCRIPCIÓN'],
        ['id', 'INTEGER', 'ID único'],
        ['nombre_causador', 'VARCHAR(100)', 'Nombre del usuario (único)'],
        ['email', 'VARCHAR(255)', 'Email del usuario'],
        ['activo', 'BOOLEAN', 'TRUE si puede causar documentos'],
        ['total_documentos', 'INTEGER', 'Total de documentos causados'],
        ['ultimo_documento_fecha', 'DATE', 'Fecha del último documento causado'],
    ]
    
    tabla_usuarios_caus = Table(campos_usuarios_caus, colWidths=[1.8*inch, 1.3*inch, 2.4*inch])
    tabla_usuarios_caus.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(tabla_usuarios_caus)
    
    story.append(PageBreak())
    
    # ========================================
    # 3. TABLAS DE AUDITORÍA Y LOGS
    # ========================================
    story.append(Paragraph("3. TABLAS DE AUDITORÍA Y LOGS", subtitulo_style))
    
    # 3.1 historial_envios_dian_vs_erp
    story.append(Paragraph("3.1. historial_envios_dian_vs_erp", seccion_style))
    story.append(Paragraph("""
    <b>Función:</b> Registra cada envío de correo realizado por el sistema.
    <br/><br/>
    <b>Información almacenada:</b>
    <br/>• Tipo de envío (alerta, reporte, notificación)
    <br/>• Lista de destinatarios
    <br/>• Fecha y hora del envío
    <br/>• Estado (exitoso o fallido)
    <br/>• Cantidad de documentos incluidos en el reporte
    """, texto_justificado))
    story.append(Spacer(1, 0.1*inch))
    
    campos_historial = [
        ['CAMPO', 'TIPO', 'DESCRIPCIÓN'],
        ['id', 'INTEGER', 'ID único del envío'],
        ['tipo_envio', 'VARCHAR(50)', 'Tipo: ALERTA, REPORTE, NOTIFICACION'],
        ['destinatarios', 'TEXT', 'Lista de emails separados por coma'],
        ['cantidad_docs', 'INTEGER', 'Número de documentos incluidos'],
        ['estado', 'VARCHAR(20)', 'EXITOSO, FALLIDO'],
        ['fecha_envio', 'DATETIME', 'Fecha y hora del envío'],
        ['mensaje_error', 'TEXT', 'Descripción del error si falló'],
    ]
    
    tabla_historial = Table(campos_historial, colWidths=[1.5*inch, 1.3*inch, 2.7*inch])
    tabla_historial.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(tabla_historial)
    story.append(Spacer(1, 0.2*inch))
    
    # 3.2 logs_sistema_dian_vs_erp
    story.append(Paragraph("3.2. logs_sistema_dian_vs_erp", seccion_style))
    story.append(Paragraph("""
    <b>Función:</b> Registro de eventos del sistema para depuración y auditoría.
    <br/><br/>
    <b>Eventos registrados:</b>
    <br/>• Carga de archivos (DIAN, ERP, Acuses)
    <br/>• Procesamiento de datos
    <br/>• Errores de importación
    <br/>• Actualizaciones masivas
    <br/>• Sincronizaciones automáticas
    """, texto_justificado))
    story.append(Spacer(1, 0.1*inch))
    
    campos_logs = [
        ['CAMPO', 'TIPO', 'DESCRIPCIÓN'],
        ['id', 'INTEGER', 'ID único del log'],
        ['nivel', 'VARCHAR(20)', 'INFO, WARNING, ERROR, CRITICAL'],
        ['evento', 'VARCHAR(100)', 'Tipo de evento'],
        ['mensaje', 'TEXT', 'Descripción detallada'],
        ['usuario', 'VARCHAR(100)', 'Usuario que realizó la acción'],
        ['fecha_hora', 'DATETIME', 'Fecha y hora del evento'],
        ['datos_adicionales', 'TEXT', 'JSON con datos extra'],
    ]
    
    tabla_logs = Table(campos_logs, colWidths=[1.3*inch, 1.3*inch, 2.9*inch])
    tabla_logs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(tabla_logs)
    
    story.append(PageBreak())
    
    # ========================================
    # 4. FLUJO DE DATOS
    # ========================================
    story.append(Paragraph("4. FLUJO COMPLETO DE DATOS", subtitulo_style))
    
    story.append(Paragraph("📥 <b>PASO 1: CARGA DE ARCHIVOS</b>", seccion_style))
    story.append(Paragraph("""
    <b>A. Archivo DIAN (Reportes de Facturas Electrónicas)</b>
    <br/>• <b>Formato:</b> CSV o Excel
    <br/>• <b>Ubicación:</b> uploads/dian/
    <br/>• <b>Contenido:</b> Todas las facturas electrónicas emitidas por proveedores
    <br/>• <b>Columnas principales:</b> NIT emisor, Nombre emisor, Fecha emisión, Prefijo, Folio, Valor, CUFE, Tipo documento, Estado aprobación
    <br/>• <b>Destino en BD:</b> Tabla <b>maestro_dian_vs_erp</b>
    <br/>• <b>Función de carga:</b> actualizar_maestro() línea 504 de routes.py
    <br/><br/>
    <b>B. Archivos ERP Financiero</b>
    <br/>• <b>Formato:</b> CSV o Excel
    <br/>• <b>Ubicación:</b> uploads/erp_fn/
    <br/>• <b>Contenido:</b> Facturas registradas en el módulo financiero
    <br/>• <b>Columnas adicionales:</b> Forma de pago, Tipo servicio, Departamento, Estado contable
    <br/>• <b>Destino en BD:</b> Se cruza con maestro_dian_vs_erp
    <br/><br/>
    <b>C. Archivos ERP Comercial</b>
    <br/>• <b>Formato:</b> CSV o Excel
    <br/>• <b>Ubicación:</b> uploads/erp_cm/
    <br/>• <b>Contenido:</b> Facturas del módulo comercial
    <br/>• <b>Destino en BD:</b> Se cruza con maestro_dian_vs_erp
    <br/><br/>
    <b>D. Archivos de Acuse</b>
    <br/>• <b>Formato:</b> CSV o Excel
    <br/>• <b>Ubicación:</b> uploads/acuses/
    <br/>• <b>Contenido:</b> Confirmaciones de recepción de documentos
    <br/>• <b>Actualiza:</b> Campos acuses_recibidos, fecha_recibida en maestro_dian_vs_erp
    """, texto_justificado))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("⚙️ <b>PASO 2: PROCESAMIENTO Y CONSOLIDACIÓN</b>", seccion_style))
    story.append(Paragraph("""
    La función <font face="Courier"><b>actualizar_maestro()</b></font> realiza:
    <br/>1. Lee los archivos CSV más recientes de cada carpeta
    <br/>2. Extrae prefijo y folio de los números de documento
    <br/>3. Cruza datos DIAN con datos ERP por Prefijo+Folio+NIT
    <br/>4. Enriquece la información con datos de ambos sistemas
    <br/>5. Calcula días desde emisión
    <br/>6. Mapea campos (ej: forma_pago 1→Contado, 2→Crédito)
    <br/>7. Inserta registros en maestro_dian_vs_erp
    <br/>8. Genera logs en logs_sistema_dian_vs_erp
    """, texto_justificado))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("📊 <b>PASO 3: CONSULTA Y VISUALIZACIÓN</b>", seccion_style))
    story.append(Paragraph("""
    <b>Endpoint principal:</b> /dian_vs_erp/api/dian
    <br/>• Permite filtrar por rango de fechas
    <br/>• Permite búsqueda por NIT, razón social, prefijo o folio
    <br/>• Retorna datos paginados (500 registros por página)
    <br/>• Se conecta directamente a la tabla maestro_dian_vs_erp
    <br/><br/>
    <b>Otros endpoints:</b>
    <br/>• /dian_vs_erp/api/actualizar_nit - Actualiza campos para un NIT
    <br/>• /dian_vs_erp/api/actualizar_campo - Actualiza campo individual por CUFE
    <br/>• /dian_vs_erp/api/estadisticas - Resumen general del módulo
    """, texto_justificado))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("📧 <b>PASO 4: ALERTAS Y NOTIFICACIONES</b>", seccion_style))
    story.append(Paragraph("""
    El sistema envía automáticamente:
    <br/>• <b>Alertas diarias:</b> Facturas pendientes de más de X días (configurado en envios_programados_dian_vs_erp)
    <br/>• <b>Alertas de acuses:</b> Documentos a crédito sin acuses mínimos requeridos
    <br/>• <b>Notificaciones personalizadas:</b> Según asignación en usuarios_asignados_dian_vs_erp
    <br/><br/>
    Cada envío se registra en historial_envios_dian_vs_erp para auditoría.
    """, texto_justificado))
    
    story.append(PageBreak())
    
    # ========================================
    # 5. DIAGRAMA DE FLUJO
    # ========================================
    story.append(Paragraph("5. DIAGRAMA DE RELACIONES", subtitulo_style))
    
    story.append(Paragraph("""
    <font face="Courier" size="9">
    ┌─────────────────────────────────────────────────────────────┐<br/>
    │         <b>ARCHIVOS DE ORIGEN (CSV/Excel)</b>                       │<br/>
    ├─────────────────────────────────────────────────────────────┤<br/>
    │                                                             │<br/>
    │  📁 uploads/dian/       → Facturas electrónicas DIAN       │<br/>
    │  📁 uploads/erp_fn/     → Facturas ERP Financiero          │<br/>
    │  📁 uploads/erp_cm/     → Facturas ERP Comercial           │<br/>
    │  📁 uploads/acuses/     → Acuses de recepción              │<br/>
    │                                                             │<br/>
    └──────────────────┬──────────────────────────────────────────┘<br/>
                       │<br/>
                       ↓ <b>Función: actualizar_maestro()</b><br/>
                       │<br/>
    ┌──────────────────┴──────────────────────────────────────────┐<br/>
    │         <b>TABLA CENTRAL: maestro_dian_vs_erp</b>                   │<br/>
    ├─────────────────────────────────────────────────────────────┤<br/>
    │ • Almacena TODAS las facturas consolidadas                  │<br/>
    │ • Combina datos DIAN + ERP                                  │<br/>
    │ • Registra causación y recepción                            │<br/>
    │ • Controla acuses recibidos                                 │<br/>
    └──────────────────┬──────────────────────────────────────────┘<br/>
                       │<br/>
         ┌─────────────┼─────────────┬──────────────┐<br/>
         │             │             │              │<br/>
         ↓             ↓             ↓              ↓<br/>
    ┌────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐<br/>
    │Usuarios│  │Envíos    │  │Historial │  │Logs       │<br/>
    │Asigna- │  │Program.  │  │Envíos    │  │Sistema    │<br/>
    │dos     │  │          │  │          │  │           │<br/>
    └────────┘  └──────────┘  └──────────┘  └───────────┘<br/>
       ↓             ↓             ↓              ↓<br/>
    Define       Configura    Registra      Audita<br/>
    alertas      frecuencias  envíos        eventos<br/>
    </font>
    """, styles['Code']))
    
    story.append(PageBreak())
    
    # ========================================
    # 6. RESUMEN EJECUTIVO
    # ========================================
    story.append(Paragraph("6. RESUMEN EJECUTIVO", subtitulo_style))
    
    resumen_ejecutivo = [
        ['ASPECTO', 'DETALLE'],
        ['🎯 Tabla Principal', 'maestro_dian_vs_erp (almacena TODO)'],
        ['📥 Origen DIAN', 'uploads/dian/ → Facturas electrónicas'],
        ['📥 Origen ERP', 'uploads/erp_fn/ y uploads/erp_cm/ → Facturas internas'],
        ['📥 Origen Acuses', 'uploads/acuses/ → Confirmaciones de recepción'],
        ['⚙️ Procesamiento', 'Función actualizar_maestro() en routes.py línea 504'],
        ['👥 Usuarios', '2 tablas: usuarios_asignados y usuarios_causacion'],
        ['📧 Alertas', 'Tabla envios_programados_dian_vs_erp'],
        ['📊 Auditoría', '2 tablas: historial_envios y logs_sistema'],
        ['🔧 Total Tablas', '6 tablas PostgreSQL'],
        ['✅ Estado', 'Módulo FUNCIONAL Y OPERATIVO'],
    ]
    
    tabla_resumen_ejecutivo = Table(resumen_ejecutivo, colWidths=[2*inch, 4*inch])
    tabla_resumen_ejecutivo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(tabla_resumen_ejecutivo)
    story.append(Spacer(1, 0.3*inch))
    
    # Notas finales
    story.append(Paragraph("📝 <b>NOTAS IMPORTANTES:</b>", seccion_style))
    story.append(Paragraph("""
    1. <b>La tabla maestro_dian_vs_erp es la única tabla donde se almacenan las facturas.</b> 
       Las demás tablas son de configuración, usuarios y auditoría.
    <br/><br/>
    2. <b>Los archivos se procesan automáticamente</b> cuando se actualizan las carpetas uploads/.
    <br/><br/>
    3. <b>El sistema NO borra datos antiguos</b> a menos que se ejecute una limpieza manual.
       Cada procesamiento puede sobrescribir registros existentes basándose en Prefijo+Folio+NIT.
    <br/><br/>
    4. <b>Las alertas se envían según configuración</b> en envios_programados_dian_vs_erp 
       (frecuencia diaria, semanal o mensual).
    <br/><br/>
    5. <b>La causación es un proceso manual</b> realizado por usuarios autorizados en 
       usuarios_causacion_dian_vs_erp.
    """, texto_justificado))
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Documento generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph("Sistema Gestor Documental - Supertiendas Cañaveral", styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    print(f"✅ PDF generado: {filename}")
    return filename

def enviar_correo(pdf_path, destinatario='ricardoriascos07@gmail.com'):
    """Envía el PDF por correo"""
    print(f"\n📧 Enviando correo a {destinatario}...")
    
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', '465'))
    mail_username = os.getenv('MAIL_USERNAME', '')
    mail_password = os.getenv('MAIL_PASSWORD', '')
    mail_sender = os.getenv('MAIL_DEFAULT_SENDER', mail_username)
    use_ssl = os.getenv('MAIL_USE_SSL', 'True') == 'True'
    
    try:
        msg = MIMEMultipart()
        msg['From'] = mail_sender
        msg['To'] = destinatario
        msg['Subject'] = f"Módulo DIAN vs ERP - Documentación de Tablas - {datetime.now().strftime('%d/%m/%Y')}"
        
        tamano_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        
        cuerpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #166534;">📊 Módulo DIAN vs ERP - Documentación Técnica</h2>
            <p>Estimado Ricardo,</p>
            <p>Adjunto encontrarás la <b>documentación completa y detallada</b> del módulo <b>DIAN vs ERP</b>, 
            incluyendo explicación de todas las tablas que utiliza y el flujo completo de datos.</p>
            
            <h3>📋 Este documento incluye:</h3>
            <ul>
                <li>✅ <b>Tabla principal:</b> maestro_dian_vs_erp (donde se cargan TODOS los datos)</li>
                <li>✅ <b>Origen de datos DIAN:</b> Ubicación de archivos y proceso de carga</li>
                <li>✅ <b>Origen de datos ERP:</b> Archivos financiero y comercial</li>
                <li>✅ <b>Origen de Acuses:</b> Confirmaciones de recepción</li>
                <li>✅ <b>Tablas de configuración:</b> Usuarios, envíos programados</li>
                <li>✅ <b>Tablas de auditoría:</b> Historial y logs del sistema</li>
                <li>✅ <b>Flujo completo:</b> Desde carga hasta visualización</li>
                <li>✅ <b>Diagrama de relaciones</b> entre tablas</li>
                <li>✅ <b>Detalles técnicos:</b> Campos, tipos de datos, funciones</li>
            </ul>
            
            <div style="background-color: #f0fdf4; padding: 15px; border-left: 4px solid #166534; margin: 20px 0;">
                <p style="margin: 0;"><b>📊 Total de tablas:</b> 6 tablas PostgreSQL</p>
                <p style="margin: 5px 0;"><b>🎯 Tabla principal:</b> maestro_dian_vs_erp</p>
                <p style="margin: 5px 0;"><b>📁 Tamaño del documento:</b> {tamano_mb:.2f} MB</p>
                <p style="margin: 5px 0;"><b>✅ Estado del módulo:</b> FUNCIONAL Y OPERATIVO</p>
            </div>
            
            <h3>🔍 Respuestas a tus preguntas:</h3>
            <ul>
                <li><b>¿Qué tablas usa?</b> 6 tablas (1 principal + 5 auxiliares)</li>
                <li><b>¿Dónde se cargan datos DIAN?</b> En maestro_dian_vs_erp desde uploads/dian/</li>
                <li><b>¿Dónde se cargan datos ERP?</b> En maestro_dian_vs_erp desde uploads/erp_fn/ y uploads/erp_cm/</li>
                <li><b>¿Dónde se cargan acuses?</b> Actualizan campos en maestro_dian_vs_erp desde uploads/acuses/</li>
            </ul>
            
            <p style="margin-top: 30px;">Saludos cordiales,<br>
            <b>Sistema Gestor Documental</b><br>
            Supertiendas Cañaveral</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(cuerpo, 'html'))
        
        # Adjuntar PDF
        with open(pdf_path, 'rb') as f:
            pdf = MIMEApplication(f.read(), _subtype='pdf')
            pdf.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
            msg.attach(pdf)
        
        # Enviar
        if use_ssl:
            server = smtplib.SMTP_SSL(mail_server, mail_port)
        else:
            server = smtplib.SMTP(mail_server, mail_port)
            server.starttls()
        
        server.login(mail_username, mail_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Correo enviado exitosamente a {destinatario}")
        return True
        
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
        return False

if __name__ == '__main__':
    print("="*70)
    print("GENERACIÓN DE DOCUMENTACIÓN - MÓDULO DIAN VS ERP")
    print("="*70)
    print()
    
    # Generar PDF
    pdf_path = crear_pdf_dian_vs_erp()
    
    # Enviar por correo
    enviar_correo(pdf_path)
    
    print()
    print("="*70)
    print("✅ PROCESO COMPLETADO")
    print("="*70)
    print(f"📄 PDF generado: {pdf_path}")
    print(f"📧 Correo enviado a: ricardoriascos07@gmail.com")
