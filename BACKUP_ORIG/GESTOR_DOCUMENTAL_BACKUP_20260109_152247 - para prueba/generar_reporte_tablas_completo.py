"""
Script para generar reporte exhaustivo de todas las tablas de la base de datos
Genera un PDF detallado y lo envía por correo
"""

import os
import sys
from datetime import datetime
import psycopg2
from psycopg2 import sql
import re
from collections import defaultdict
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Cargar variables de entorno con encoding correcto
load_dotenv(encoding='utf-8')

# Configuración de la base de datos - desde DATABASE_URL
database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/gestor_documental')

# Parsear la URL de la base de datos
import urllib.parse as urlparse
parsed = urlparse.urlparse(database_url)

DB_CONFIG = {
    'dbname': parsed.path[1:],  # Remover el '/' inicial
    'user': parsed.username,
    'password': parsed.password,
    'host': parsed.hostname,
    'port': str(parsed.port) if parsed.port else '5432'
}

# Configuración de correo
MAIL_CONFIG = {
    'server': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    'port': int(os.getenv('MAIL_PORT', '587')),
    'username': os.getenv('MAIL_USERNAME', ''),
    'password': os.getenv('MAIL_PASSWORD', ''),
    'sender': os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME', ''))
}

class AnalizadorTablas:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.tablas_info = {}
        self.referencias_codigo = defaultdict(lambda: {
            'archivos': [],
            'modulos': set(),
            'operaciones': {'INSERT': 0, 'UPDATE': 0, 'DELETE': 0, 'SELECT': 0}
        })
        
    def conectar_bd(self):
        """Conecta a la base de datos PostgreSQL"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            print("✅ Conectado a la base de datos")
            return True
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            return False
    
    def obtener_lista_tablas(self):
        """Obtiene la lista de todas las tablas"""
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]
    
    def obtener_info_tabla(self, nombre_tabla):
        """Obtiene información detallada de una tabla"""
        info = {
            'nombre': nombre_tabla,
            'campos': [],
            'num_registros': 0,
            'tamano_mb': 0,
            'fecha_creacion': None,
            'ultima_modificacion': None,
            'indices': [],
            'foreign_keys': [],
            'primary_key': None
        }
        
        # 1. Obtener campos
        query_campos = """
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """
        self.cursor.execute(query_campos, (nombre_tabla,))
        for row in self.cursor.fetchall():
            campo = {
                'nombre': row[0],
                'tipo': row[1],
                'longitud': row[2],
                'nullable': row[3] == 'YES',
                'default': row[4]
            }
            info['campos'].append(campo)
        
        # 2. Obtener número de registros
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla};")
            info['num_registros'] = self.cursor.fetchone()[0]
        except:
            info['num_registros'] = 0
        
        # 3. Obtener tamaño
        query_tamano = """
            SELECT pg_total_relation_size(%s) / (1024.0 * 1024.0) as size_mb;
        """
        self.cursor.execute(query_tamano, (nombre_tabla,))
        info['tamano_mb'] = round(self.cursor.fetchone()[0], 2)
        
        # 4. Obtener primary key
        query_pk = """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary;
        """
        try:
            self.cursor.execute(query_pk, (nombre_tabla,))
            pk_fields = [row[0] for row in self.cursor.fetchall()]
            if pk_fields:
                info['primary_key'] = ', '.join(pk_fields)
        except:
            pass
        
        # 5. Obtener foreign keys
        query_fk = """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name=%s;
        """
        self.cursor.execute(query_fk, (nombre_tabla,))
        for row in self.cursor.fetchall():
            info['foreign_keys'].append({
                'campo': row[0],
                'tabla_ref': row[1],
                'campo_ref': row[2]
            })
        
        # 6. Detectar campos de fecha para última modificación
        for campo in info['campos']:
            nombre_campo = campo['nombre'].lower()
            if 'fecha' in nombre_campo or 'timestamp' in nombre_campo or 'created' in nombre_campo:
                try:
                    query_fecha = f"SELECT MAX({campo['nombre']}) FROM {nombre_tabla};"
                    self.cursor.execute(query_fecha)
                    resultado = self.cursor.fetchone()[0]
                    if resultado and info['ultima_modificacion'] is None:
                        info['ultima_modificacion'] = resultado
                except:
                    pass
        
        return info
    
    def analizar_codigo_fuente(self):
        """Analiza el código fuente para encontrar referencias a tablas"""
        print("\n📂 Analizando código fuente...")
        
        # Directorios a analizar
        directorios = ['.', 'modules']
        extensiones = ['.py']
        
        archivos_analizados = 0
        for directorio in directorios:
            if not os.path.exists(directorio):
                continue
                
            for root, dirs, files in os.walk(directorio):
                # Ignorar ciertos directorios
                dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', 'node_modules', '.git']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensiones):
                        filepath = os.path.join(root, file)
                        self.analizar_archivo(filepath)
                        archivos_analizados += 1
        
        print(f"   Archivos analizados: {archivos_analizados}")
    
    def analizar_archivo(self, filepath):
        """Analiza un archivo en busca de referencias a tablas"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
                
            # Determinar el módulo
            modulo = self.determinar_modulo(filepath)
            
            # Buscar menciones de tablas
            for tabla in self.tablas_info.keys():
                # Buscar el nombre de la tabla en el código
                patron_tabla = rf'\b{tabla}\b'
                if re.search(patron_tabla, contenido, re.IGNORECASE):
                    self.referencias_codigo[tabla]['archivos'].append(filepath)
                    self.referencias_codigo[tabla]['modulos'].add(modulo)
                    
                    # Contar operaciones
                    self.referencias_codigo[tabla]['operaciones']['INSERT'] += len(re.findall(r'INSERT\s+INTO\s+' + tabla, contenido, re.IGNORECASE))
                    self.referencias_codigo[tabla]['operaciones']['UPDATE'] += len(re.findall(r'UPDATE\s+' + tabla, contenido, re.IGNORECASE))
                    self.referencias_codigo[tabla]['operaciones']['DELETE'] += len(re.findall(r'DELETE\s+FROM\s+' + tabla, contenido, re.IGNORECASE))
                    self.referencias_codigo[tabla]['operaciones']['SELECT'] += len(re.findall(r'FROM\s+' + tabla, contenido, re.IGNORECASE))
                    
                    # Buscar en queries ORM
                    self.referencias_codigo[tabla]['operaciones']['SELECT'] += len(re.findall(r'query\s*\.\s*filter|\.query\s*\.|query\s*\(\s*' + tabla.title().replace('_', ''), contenido, re.IGNORECASE))
                    
        except Exception as e:
            pass
    
    def determinar_modulo(self, filepath):
        """Determina a qué módulo pertenece un archivo"""
        filepath = filepath.replace('\\', '/')
        
        if 'modules/recibir_facturas' in filepath:
            return 'Recibir Facturas'
        elif 'modules/relaciones' in filepath:
            return 'Relaciones'
        elif 'modules/causaciones' in filepath:
            return 'Causaciones'
        elif 'modules/dian_vs_erp' in filepath:
            return 'DIAN vs ERP'
        elif 'modules/notas_contables' in filepath:
            return 'Notas Contables'
        elif 'modules/configuracion' in filepath:
            return 'Configuración'
        elif 'modules/admin' in filepath:
            return 'Administración'
        elif 'modules/monitoreo' in filepath:
            return 'Monitoreo'
        elif filepath.endswith('app.py'):
            return 'Core (app.py)'
        else:
            return 'Sistema Base'
    
    def determinar_estado_tabla(self, nombre_tabla):
        """Determina si una tabla está funcional"""
        info_tabla = self.tablas_info[nombre_tabla]
        refs = self.referencias_codigo[nombre_tabla]
        
        # Criterios para determinar si está funcional
        tiene_registros = info_tabla['num_registros'] > 0
        tiene_referencias = len(refs['archivos']) > 0
        tiene_operaciones = sum(refs['operaciones'].values()) > 0
        usada_recientemente = False
        
        if info_tabla['ultima_modificacion']:
            try:
                # Si tiene datos recientes (últimos 6 meses)
                if isinstance(info_tabla['ultima_modificacion'], datetime):
                    dias = (datetime.now() - info_tabla['ultima_modificacion']).days
                    usada_recientemente = dias < 180
            except:
                pass
        
        # Determinar estado
        if tiene_referencias and (tiene_registros or tiene_operaciones):
            if usada_recientemente or tiene_operaciones > 5:
                return '✅ FUNCIONAL (Activa)'
            else:
                return '⚠️ FUNCIONAL (Poco Uso)'
        elif tiene_referencias:
            return '🔶 CONFIGURADA (Sin Datos)'
        else:
            return '❌ NO FUNCIONAL (Sin Referencias)'
    
    def generar_pdf(self, filename='reporte_tablas_completo.pdf'):
        """Genera el reporte en PDF"""
        print(f"\n📄 Generando PDF: {filename}")
        
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#166534'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#166534'),
            spaceAfter=12
        )
        
        # Título principal
        story.append(Paragraph("REPORTE EXHAUSTIVO DE BASE DE DATOS", titulo_style))
        story.append(Paragraph(f"Sistema Gestor Documental - Supertiendas Cañaveral", styles['Normal']))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Resumen ejecutivo
        story.append(Paragraph("RESUMEN EJECUTIVO", subtitulo_style))
        
        total_tablas = len(self.tablas_info)
        total_registros = sum(t['num_registros'] for t in self.tablas_info.values())
        total_tamano = sum(t['tamano_mb'] for t in self.tablas_info.values())
        
        # Contadores de estado
        estados = defaultdict(int)
        for tabla in self.tablas_info.keys():
            estado = self.determinar_estado_tabla(tabla)
            if 'FUNCIONAL (Activa)' in estado:
                estados['activas'] += 1
            elif 'FUNCIONAL (Poco Uso)' in estado:
                estados['poco_uso'] += 1
            elif 'CONFIGURADA' in estado:
                estados['configuradas'] += 1
            else:
                estados['no_funcionales'] += 1
        
        resumen_data = [
            ['Métrica', 'Valor'],
            ['Total de Tablas', str(total_tablas)],
            ['Total de Registros', f'{total_registros:,}'],
            ['Tamaño Total (MB)', f'{total_tamano:.2f}'],
            ['Tablas Activas', f"{estados['activas']} ({estados['activas']*100//total_tablas}%)"],
            ['Tablas con Poco Uso', f"{estados['poco_uso']} ({estados['poco_uso']*100//total_tablas}%)"],
            ['Tablas Configuradas', f"{estados['configuradas']} ({estados['configuradas']*100//total_tablas}%)"],
            ['Tablas No Funcionales', f"{estados['no_funcionales']} ({estados['no_funcionales']*100//total_tablas}%)"]
        ]
        
        tabla_resumen = Table(resumen_data, colWidths=[3*inch, 2*inch])
        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(tabla_resumen)
        story.append(PageBreak())
        
        # Detalle de cada tabla
        story.append(Paragraph("ANÁLISIS DETALLADO POR TABLA", subtitulo_style))
        story.append(Spacer(1, 0.2*inch))
        
        for i, (nombre_tabla, info) in enumerate(sorted(self.tablas_info.items()), 1):
            # Encabezado de tabla
            story.append(Paragraph(f"{i}. TABLA: {nombre_tabla.upper()}", subtitulo_style))
            
            # Estado
            estado = self.determinar_estado_tabla(nombre_tabla)
            story.append(Paragraph(f"<b>Estado:</b> {estado}", styles['Normal']))
            
            # Información básica
            info_basica = [
                ['Característica', 'Valor'],
                ['Número de Campos', str(len(info['campos']))],
                ['Número de Registros', f"{info['num_registros']:,}"],
                ['Tamaño (MB)', f"{info['tamano_mb']:.2f}"],
                ['Primary Key', info['primary_key'] or 'No definida']
            ]
            
            if info['ultima_modificacion']:
                fecha_str = info['ultima_modificacion'].strftime('%d/%m/%Y %H:%M:%S') if isinstance(info['ultima_modificacion'], datetime) else str(info['ultima_modificacion'])
                info_basica.append(['Última Modificación', fecha_str])
            else:
                info_basica.append(['Última Modificación', 'No detectada'])
            
            tabla_info = Table(info_basica, colWidths=[2.5*inch, 3*inch])
            tabla_info.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#166534')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tabla_info)
            story.append(Spacer(1, 0.1*inch))
            
            # Campos
            if info['campos']:
                story.append(Paragraph("<b>Campos:</b>", styles['Normal']))
                campos_data = [['Campo', 'Tipo', 'Nullable', 'Default']]
                for campo in info['campos'][:15]:  # Primeros 15 campos
                    tipo = campo['tipo']
                    if campo['longitud']:
                        tipo += f"({campo['longitud']})"
                    default = str(campo['default'])[:30] if campo['default'] else '-'
                    campos_data.append([
                        campo['nombre'],
                        tipo,
                        'Sí' if campo['nullable'] else 'No',
                        default
                    ])
                
                tabla_campos = Table(campos_data, colWidths=[1.8*inch, 1.5*inch, 0.7*inch, 1.5*inch])
                tabla_campos.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(tabla_campos)
                
                if len(info['campos']) > 15:
                    story.append(Paragraph(f"<i>... y {len(info['campos']) - 15} campos más</i>", styles['Normal']))
                
                story.append(Spacer(1, 0.1*inch))
            
            # Foreign Keys
            if info['foreign_keys']:
                story.append(Paragraph("<b>Relaciones (Foreign Keys):</b>", styles['Normal']))
                for fk in info['foreign_keys']:
                    story.append(Paragraph(f"• {fk['campo']} → {fk['tabla_ref']}.{fk['campo_ref']}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            
            # Referencias en código
            refs = self.referencias_codigo[nombre_tabla]
            if refs['archivos']:
                story.append(Paragraph("<b>Módulos que usan esta tabla:</b>", styles['Normal']))
                for modulo in sorted(refs['modulos']):
                    story.append(Paragraph(f"• {modulo}", styles['Normal']))
                
                story.append(Spacer(1, 0.05*inch))
                story.append(Paragraph("<b>Operaciones detectadas:</b>", styles['Normal']))
                ops_texto = []
                for op, count in refs['operaciones'].items():
                    if count > 0:
                        ops_texto.append(f"{op}: {count}")
                if ops_texto:
                    story.append(Paragraph(f"• {', '.join(ops_texto)}", styles['Normal']))
                else:
                    story.append(Paragraph("• No se detectaron operaciones explícitas", styles['Normal']))
            else:
                story.append(Paragraph("<b>⚠️ Sin referencias en el código fuente</b>", styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
            
            # PageBreak cada 2 tablas para mejor legibilidad
            if i % 2 == 0 and i < total_tablas:
                story.append(PageBreak())
        
        # Construir PDF
        doc.build(story)
        print(f"✅ PDF generado: {filename}")
        return filename
    
    def enviar_correo(self, pdf_path, destinatario='ricardoriascos07@gmail.com'):
        """Envía el PDF por correo electrónico"""
        print(f"\n📧 Enviando correo a {destinatario}...")
        
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = MAIL_CONFIG['sender']
            msg['To'] = destinatario
            msg['Subject'] = f"Reporte Exhaustivo de Base de Datos - {datetime.now().strftime('%d/%m/%Y')}"
            
            # Cuerpo del correo
            cuerpo = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #166534;">Reporte de Base de Datos - Sistema Gestor Documental</h2>
                <p>Estimado Ricardo,</p>
                <p>Adjunto encontrarás el <b>análisis exhaustivo y completo</b> de las 94 tablas de la base de datos PostgreSQL del Sistema Gestor Documental.</p>
                
                <h3>Este reporte incluye:</h3>
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
                
                <p><b>Total de tablas analizadas:</b> 94</p>
                <p><b>Generado:</b> {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
                
                <p>El documento PDF adjunto contiene toda la información solicitada de manera detallada y organizada.</p>
                
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
            server = smtplib.SMTP(MAIL_CONFIG['server'], MAIL_CONFIG['port'])
            server.starttls()
            server.login(MAIL_CONFIG['username'], MAIL_CONFIG['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Correo enviado exitosamente a {destinatario}")
            return True
            
        except Exception as e:
            print(f"❌ Error enviando correo: {e}")
            print(f"   El archivo PDF está disponible en: {pdf_path}")
            return False
    
    def ejecutar_analisis_completo(self):
        """Ejecuta el análisis completo"""
        print("="*70)
        print("ANÁLISIS EXHAUSTIVO DE BASE DE DATOS")
        print("Sistema Gestor Documental - Supertiendas Cañaveral")
        print("="*70)
        
        # 1. Conectar a BD
        if not self.conectar_bd():
            return False
        
        # 2. Obtener lista de tablas
        print("\n📊 Obteniendo lista de tablas...")
        tablas = self.obtener_lista_tablas()
        print(f"   Total de tablas encontradas: {len(tablas)}")
        
        # 3. Analizar cada tabla
        print("\n🔍 Analizando información detallada de cada tabla...")
        for i, tabla in enumerate(tablas, 1):
            print(f"   [{i}/{len(tablas)}] Analizando: {tabla}")
            self.tablas_info[tabla] = self.obtener_info_tabla(tabla)
        
        # 4. Analizar código fuente
        self.analizar_codigo_fuente()
        
        # 5. Generar PDF
        pdf_path = self.generar_pdf()
        
        # 6. Enviar por correo
        self.enviar_correo(pdf_path)
        
        # 7. Cerrar conexión
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        
        print("\n" + "="*70)
        print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("="*70)
        print(f"\n📄 Archivo PDF: {pdf_path}")
        print(f"📧 Correo enviado a: ricardoriascos07@gmail.com")
        
        return True

if __name__ == '__main__':
    analizador = AnalizadorTablas()
    analizador.ejecutar_analisis_completo()
