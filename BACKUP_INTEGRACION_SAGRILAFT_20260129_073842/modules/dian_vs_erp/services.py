"""
Módulo DIAN vs ERP - Servicios de Validación y Procesamiento
Sistema de Validación de Facturas DIAN vs Sistema ERP
Integrado al Gestor Documental - Supertiendas Cañaveral
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from extensions import db
from .models import ReporteDian, FacturaERP, ValidacionFactura, ProcesamientoPeriodo
import logging
import os
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app

logger = logging.getLogger(__name__)

class ValidacionService:
    """Servicio principal para validaciones DIAN vs ERP"""
    
    @classmethod
    def ejecutar_validacion_periodo(cls, periodo, usuario):
        """
        Ejecuta validación completa para un periodo específico
        Compara facturas DIAN vs ERP y genera validaciones
        """
        try:
            # Verificar o crear procesamiento
            procesamiento = ProcesamientoPeriodo.query.filter_by(periodo=periodo).first()
            if not procesamiento:
                procesamiento = ProcesamientoPeriodo(
                    periodo=periodo,
                    usuario_procesamiento=usuario,
                    estado_procesamiento='validando'
                )
                db.session.add(procesamiento)
            else:
                procesamiento.estado_procesamiento = 'validando'
            
            db.session.commit()
            
            # Obtener datos del periodo
            reportes_dian = ReporteDian.query.filter_by(periodo=periodo).all()
            facturas_erp = FacturaERP.query.filter_by(periodo=periodo).all()
            
            if not reportes_dian and not facturas_erp:
                return {
                    'success': False,
                    'error': f'No hay datos para validar en el periodo {periodo}'
                }
            
            # Limpiar validaciones previas del periodo
            ValidacionFactura.query.filter_by(periodo=periodo).delete()
            db.session.commit()
            
            # Convertir a diccionarios para procesamiento
            dian_dict = {}
            for reporte in reportes_dian:
                key = f"{reporte.nit_tercero}_{reporte.numero_factura}"
                dian_dict[key] = reporte
            
            erp_dict = {}
            for factura in facturas_erp:
                key = f"{factura.nit_tercero}_{factura.numero_factura}"
                erp_dict[key] = factura
            
            # Contadores de estadísticas
            stats = {
                'coincidentes': 0,
                'discrepantes': 0,
                'solo_dian': 0,
                'solo_erp': 0,
                'diferencia_valor': 0
            }
            
            validaciones = []
            
            # Procesar facturas DIAN
            for key, reporte in dian_dict.items():
                if key in erp_dict:
                    # Factura existe en ambos sistemas
                    factura_erp = erp_dict[key]
                    validacion = cls._comparar_facturas(reporte, factura_erp, usuario)
                    
                    if validacion.estado_validacion == 'coincidente':
                        stats['coincidentes'] += 1
                    elif validacion.estado_validacion == 'diferencia_valor':
                        stats['diferencia_valor'] += 1
                    else:
                        stats['discrepantes'] += 1
                        
                    validaciones.append(validacion)
                else:
                    # Solo en DIAN
                    validacion = ValidacionFactura(
                        periodo=periodo,
                        nit_tercero=reporte.nit_tercero,
                        numero_factura=reporte.numero_factura,
                        reporte_dian_id=reporte.id,
                        estado_validacion='solo_dian',
                        observaciones='Factura reportada en DIAN pero no encontrada en ERP',
                        usuario_validacion=usuario,
                        detalles_validacion={
                            'valor_dian': float(reporte.valor_total),
                            'fecha_dian': reporte.fecha_factura.strftime('%Y-%m-%d') if reporte.fecha_factura else None
                        }
                    )
                    validaciones.append(validacion)
                    stats['solo_dian'] += 1
            
            # Procesar facturas ERP que no están en DIAN
            for key, factura in erp_dict.items():
                if key not in dian_dict:
                    validacion = ValidacionFactura(
                        periodo=periodo,
                        nit_tercero=factura.nit_tercero,
                        numero_factura=factura.numero_factura,
                        factura_erp_id=factura.id,
                        estado_validacion='solo_erp',
                        observaciones='Factura en ERP pero no reportada en DIAN',
                        usuario_validacion=usuario,
                        detalles_validacion={
                            'valor_erp': float(factura.valor_total),
                            'fecha_erp': factura.fecha_factura.strftime('%Y-%m-%d') if factura.fecha_factura else None
                        }
                    )
                    validaciones.append(validacion)
                    stats['solo_erp'] += 1
            
            # Guardar validaciones en lotes
            for validacion in validaciones:
                db.session.add(validacion)
            
            # Actualizar estadísticas del procesamiento
            procesamiento.total_dian = len(reportes_dian)
            procesamiento.total_erp = len(facturas_erp)
            procesamiento.total_coincidentes = stats['coincidentes']
            procesamiento.total_discrepantes = stats['discrepantes'] + stats['diferencia_valor']
            procesamiento.total_solo_dian = stats['solo_dian']
            procesamiento.total_solo_erp = stats['solo_erp']
            procesamiento.estado_procesamiento = 'completado'
            procesamiento.fecha_finalizacion = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"VALIDACION COMPLETADA | periodo={periodo} | usuario={usuario} | "
                       f"coincidentes={stats['coincidentes']} | discrepantes={stats['discrepantes']}")
            
            return {
                'success': True,
                'estadisticas': stats,
                'total_validaciones': len(validaciones)
            }
            
        except Exception as e:
            db.session.rollback()
            if procesamiento:
                procesamiento.estado_procesamiento = 'error'
                procesamiento.observaciones_procesamiento = str(e)
                db.session.commit()
            
            logger.error(f"Error en validación periodo {periodo}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def _comparar_facturas(cls, reporte_dian, factura_erp, usuario):
        """Compara una factura DIAN vs ERP y retorna validación"""
        
        # Tolerancia para diferencias de valor (0.01 = 1 centavo)
        tolerancia = Decimal('0.01')
        
        # Comparar valores
        valor_dian = reporte_dian.valor_total or Decimal('0')
        valor_erp = factura_erp.valor_total or Decimal('0')
        diferencia = abs(valor_dian - valor_erp)
        
        # Determinar estado de validación
        if diferencia <= tolerancia:
            estado = 'coincidente'
            tipo_discrepancia = None
            observaciones = 'Factura coincidente entre DIAN y ERP'
        elif diferencia > tolerancia:
            estado = 'diferencia_valor'
            tipo_discrepancia = 'valor'
            observaciones = f'Diferencia de valor: DIAN=${valor_dian}, ERP=${valor_erp}'
        else:
            estado = 'discrepante'
            tipo_discrepancia = 'general'
            observaciones = 'Discrepancia general entre DIAN y ERP'
        
        # Crear validación
        validacion = ValidacionFactura(
            periodo=reporte_dian.periodo,
            nit_tercero=reporte_dian.nit_tercero,
            numero_factura=reporte_dian.numero_factura,
            reporte_dian_id=reporte_dian.id,
            factura_erp_id=factura_erp.id,
            estado_validacion=estado,
            tipo_discrepancia=tipo_discrepancia,
            diferencia_valor=diferencia,
            observaciones=observaciones,
            usuario_validacion=usuario,
            detalles_validacion={
                'valor_dian': float(valor_dian),
                'valor_erp': float(valor_erp),
                'fecha_dian': reporte_dian.fecha_factura.strftime('%Y-%m-%d') if reporte_dian.fecha_factura else None,
                'fecha_erp': factura_erp.fecha_factura.strftime('%Y-%m-%d') if factura_erp.fecha_factura else None,
                'razon_social_dian': reporte_dian.razon_social,
                'razon_social_erp': factura_erp.razon_social
            }
        )
        
        return validacion
    
    @classmethod
    def obtener_estadisticas_periodo(cls, periodo):
        """Obtiene estadísticas de validaciones para un periodo"""
        try:
            stats = {
                'total_validaciones': ValidacionFactura.query.filter_by(periodo=periodo).count(),
                'coincidentes': ValidacionFactura.query.filter_by(
                    periodo=periodo, estado_validacion='coincidente'
                ).count(),
                'discrepantes': ValidacionFactura.query.filter_by(
                    periodo=periodo, estado_validacion='discrepante'
                ).count(),
                'diferencia_valor': ValidacionFactura.query.filter_by(
                    periodo=periodo, estado_validacion='diferencia_valor'
                ).count(),
                'solo_dian': ValidacionFactura.query.filter_by(
                    periodo=periodo, estado_validacion='solo_dian'
                ).count(),
                'solo_erp': ValidacionFactura.query.filter_by(
                    periodo=periodo, estado_validacion='solo_erp'
                ).count(),
                'total_dian': ReporteDian.query.filter_by(periodo=periodo).count(),
                'total_erp': FacturaERP.query.filter_by(periodo=periodo).count()
            }
            
            # Calcular porcentajes
            total = stats['total_validaciones']
            if total > 0:
                stats['porcentaje_coincidentes'] = round((stats['coincidentes'] / total) * 100, 2)
                stats['porcentaje_discrepantes'] = round(
                    ((stats['discrepantes'] + stats['diferencia_valor']) / total) * 100, 2
                )
            else:
                stats['porcentaje_coincidentes'] = 0
                stats['porcentaje_discrepantes'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas periodo {periodo}: {e}")
            return {}

class CargaService:
    """Servicio para carga de archivos DIAN y ERP"""
    
    @classmethod
    def cargar_reporte_dian(cls, archivo, periodo, usuario):
        """Carga archivo de reporte DIAN"""
        try:
            # Leer archivo Excel/CSV
            if archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls'):
                df = pd.read_excel(archivo)
            elif archivo.filename.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                return {
                    'success': False,
                    'error': 'Formato de archivo no soportado. Use Excel (.xlsx) o CSV (.csv)'
                }
            
            # Validar columnas requeridas
            columnas_requeridas = [
                'nit_tercero', 'numero_factura', 'fecha_factura', 'valor_total'
            ]
            
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            if columnas_faltantes:
                return {
                    'success': False,
                    'error': f'Columnas faltantes: {", ".join(columnas_faltantes)}'
                }
            
            # Limpiar datos existentes del periodo
            ReporteDian.query.filter_by(periodo=periodo).delete()
            
            registros_cargados = 0
            errores = []
            
            for index, row in df.iterrows():
                try:
                    # Validar datos requeridos
                    if pd.isna(row['nit_tercero']) or pd.isna(row['numero_factura']) or pd.isna(row['valor_total']):
                        errores.append(f"Fila {index + 2}: Datos requeridos faltantes")
                        continue
                    
                    # Procesar fecha
                    fecha_factura = None
                    if not pd.isna(row['fecha_factura']):
                        if isinstance(row['fecha_factura'], str):
                            fecha_factura = datetime.strptime(row['fecha_factura'], '%Y-%m-%d').date()
                        else:
                            fecha_factura = row['fecha_factura'].date()
                    
                    # Crear reporte DIAN
                    reporte = ReporteDian(
                        periodo=periodo,
                        nit_tercero=str(row['nit_tercero']).strip(),
                        razon_social=str(row.get('razon_social', '')).strip()[:255],
                        numero_factura=str(row['numero_factura']).strip(),
                        fecha_factura=fecha_factura,
                        valor_bruto=Decimal(str(row.get('valor_bruto', 0))),
                        valor_iva=Decimal(str(row.get('valor_iva', 0))),
                        valor_total=Decimal(str(row['valor_total'])),
                        cufe=str(row.get('cufe', '')).strip()[:100],
                        archivo_origen=archivo.filename,
                        usuario_carga=usuario
                    )
                    
                    db.session.add(reporte)
                    registros_cargados += 1
                    
                except Exception as e:
                    errores.append(f"Fila {index + 2}: {str(e)}")
                    continue
            
            db.session.commit()
            
            mensaje = f"Registros cargados: {registros_cargados}"
            if errores:
                mensaje += f". Errores: {len(errores)}"
            
            logger.info(f"REPORTE DIAN CARGADO | usuario={usuario} | periodo={periodo} | registros={registros_cargados}")
            
            return {
                'success': True,
                'total_registros': registros_cargados,
                'errores': errores[:10],  # Máximo 10 errores para mostrar
                'mensaje': mensaje
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cargando reporte DIAN: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def cargar_facturas_erp(cls, archivo, periodo, usuario):
        """Carga archivo de facturas ERP"""
        try:
            # Leer archivo
            if archivo.filename.endswith('.xlsx') or archivo.filename.endswith('.xls'):
                df = pd.read_excel(archivo)
            elif archivo.filename.endswith('.csv'):
                df = pd.read_csv(archivo)
            else:
                return {
                    'success': False,
                    'error': 'Formato de archivo no soportado. Use Excel (.xlsx) o CSV (.csv)'
                }
            
            # Validar columnas requeridas
            columnas_requeridas = [
                'nit_tercero', 'numero_factura', 'fecha_factura', 'valor_total'
            ]
            
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            if columnas_faltantes:
                return {
                    'success': False,
                    'error': f'Columnas faltantes: {", ".join(columnas_faltantes)}'
                }
            
            # Limpiar datos existentes del periodo
            FacturaERP.query.filter_by(periodo=periodo).delete()
            
            registros_cargados = 0
            errores = []
            
            for index, row in df.iterrows():
                try:
                    # Validar datos requeridos
                    if pd.isna(row['nit_tercero']) or pd.isna(row['numero_factura']) or pd.isna(row['valor_total']):
                        errores.append(f"Fila {index + 2}: Datos requeridos faltantes")
                        continue
                    
                    # Procesar fechas
                    fecha_factura = None
                    fecha_recepcion = None
                    
                    if not pd.isna(row['fecha_factura']):
                        if isinstance(row['fecha_factura'], str):
                            fecha_factura = datetime.strptime(row['fecha_factura'], '%Y-%m-%d').date()
                        else:
                            fecha_factura = row['fecha_factura'].date()
                    
                    if 'fecha_recepcion' in row and not pd.isna(row['fecha_recepcion']):
                        if isinstance(row['fecha_recepcion'], str):
                            fecha_recepcion = datetime.strptime(row['fecha_recepcion'], '%Y-%m-%d').date()
                        else:
                            fecha_recepcion = row['fecha_recepcion'].date()
                    
                    # Crear factura ERP
                    factura = FacturaERP(
                        periodo=periodo,
                        nit_tercero=str(row['nit_tercero']).strip(),
                        razon_social=str(row.get('razon_social', '')).strip()[:255],
                        numero_factura=str(row['numero_factura']).strip(),
                        fecha_factura=fecha_factura,
                        fecha_recepcion=fecha_recepcion,
                        valor_bruto=Decimal(str(row.get('valor_bruto', 0))),
                        valor_iva=Decimal(str(row.get('valor_iva', 0))),
                        valor_total=Decimal(str(row['valor_total'])),
                        centro_costo=str(row.get('centro_costo', '')).strip()[:50],
                        observaciones=str(row.get('observaciones', '')).strip(),
                        archivo_origen=archivo.filename,
                        usuario_carga=usuario
                    )
                    
                    db.session.add(factura)
                    registros_cargados += 1
                    
                except Exception as e:
                    errores.append(f"Fila {index + 2}: {str(e)}")
                    continue
            
            db.session.commit()
            
            mensaje = f"Registros cargados: {registros_cargados}"
            if errores:
                mensaje += f". Errores: {len(errores)}"
            
            logger.info(f"FACTURAS ERP CARGADAS | usuario={usuario} | periodo={periodo} | registros={registros_cargados}")
            
            return {
                'success': True,
                'total_registros': registros_cargados,
                'errores': errores[:10],
                'mensaje': mensaje
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cargando facturas ERP: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class ReporteService:
    """Servicio para generación de reportes"""
    
    @classmethod
    def generar_reporte_excel(cls, periodo, usuario):
        """Genera reporte completo en Excel"""
        try:
            # Crear archivo Excel en memoria
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Hoja 1: Resumen general
                stats = ValidacionService.obtener_estadisticas_periodo(periodo)
                resumen_df = pd.DataFrame([
                    ['Total Validaciones', stats.get('total_validaciones', 0)],
                    ['Facturas Coincidentes', stats.get('coincidentes', 0)],
                    ['Facturas con Diferencia de Valor', stats.get('diferencia_valor', 0)],
                    ['Facturas Discrepantes', stats.get('discrepantes', 0)],
                    ['Solo en DIAN', stats.get('solo_dian', 0)],
                    ['Solo en ERP', stats.get('solo_erp', 0)],
                    ['% Coincidencia', f"{stats.get('porcentaje_coincidentes', 0)}%"],
                    ['Fecha Generación', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                    ['Usuario', usuario]
                ], columns=['Métrica', 'Valor'])
                
                resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Hoja 2: Validaciones detalladas
                validaciones = ValidacionFactura.query.filter_by(periodo=periodo).all()
                validaciones_data = []
                
                for val in validaciones:
                    validaciones_data.append({
                        'NIT Tercero': val.nit_tercero,
                        'Número Factura': val.numero_factura,
                        'Estado Validación': val.estado_validacion,
                        'Tipo Discrepancia': val.tipo_discrepancia or '',
                        'Diferencia Valor': float(val.diferencia_valor or 0),
                        'Observaciones': val.observaciones,
                        'Fecha Validación': val.fecha_validacion.strftime('%Y-%m-%d %H:%M:%S') if val.fecha_validacion else ''
                    })
                
                validaciones_df = pd.DataFrame(validaciones_data)
                validaciones_df.to_excel(writer, sheet_name='Validaciones', index=False)
                
                # Hoja 3: Solo DIAN (no en ERP)
                solo_dian = ValidacionFactura.query.filter_by(
                    periodo=periodo, estado_validacion='solo_dian'
                ).all()
                
                solo_dian_data = []
                for val in solo_dian:
                    reporte = val.reporte_dian
                    solo_dian_data.append({
                        'NIT Tercero': val.nit_tercero,
                        'Razón Social': reporte.razon_social if reporte else '',
                        'Número Factura': val.numero_factura,
                        'Fecha Factura': reporte.fecha_factura.strftime('%Y-%m-%d') if reporte and reporte.fecha_factura else '',
                        'Valor Total': float(reporte.valor_total) if reporte else 0,
                        'CUFE': reporte.cufe if reporte else ''
                    })
                
                solo_dian_df = pd.DataFrame(solo_dian_data)
                solo_dian_df.to_excel(writer, sheet_name='Solo DIAN', index=False)
                
                # Hoja 4: Solo ERP (no en DIAN)
                solo_erp = ValidacionFactura.query.filter_by(
                    periodo=periodo, estado_validacion='solo_erp'
                ).all()
                
                solo_erp_data = []
                for val in solo_erp:
                    factura = val.factura_erp
                    solo_erp_data.append({
                        'NIT Tercero': val.nit_tercero,
                        'Razón Social': factura.razon_social if factura else '',
                        'Número Factura': val.numero_factura,
                        'Fecha Factura': factura.fecha_factura.strftime('%Y-%m-%d') if factura and factura.fecha_factura else '',
                        'Valor Total': float(factura.valor_total) if factura else 0,
                        'Centro Costo': factura.centro_costo if factura else '',
                        'Estado ERP': factura.estado_erp if factura else ''
                    })
                
                solo_erp_df = pd.DataFrame(solo_erp_data)
                solo_erp_df.to_excel(writer, sheet_name='Solo ERP', index=False)
                
                # Formatear hojas
                workbook = writer.book
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#20c997',
                    'font_color': 'white',
                    'border': 1
                })
                
                for sheet_name in ['Resumen', 'Validaciones', 'Solo DIAN', 'Solo ERP']:
                    worksheet = writer.sheets[sheet_name]
                    for col_num, value in enumerate(eval(f"{sheet_name.replace(' ', '_').lower()}_df").columns.values):
                        worksheet.write(0, col_num, value, header_format)
            
            output.seek(0)
            
            # Guardar archivo en directorio de reportes
            reportes_dir = 'reportes_dian_vs_erp'
            if not os.path.exists(reportes_dir):
                os.makedirs(reportes_dir)
            
            nombre_archivo = f"reporte_dian_vs_erp_{periodo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            archivo_path = os.path.join(reportes_dir, nombre_archivo)
            
            with open(archivo_path, 'wb') as f:
                f.write(output.getvalue())
            
            # Actualizar procesamiento con ruta del archivo
            procesamiento = ProcesamientoPeriodo.query.filter_by(periodo=periodo).first()
            if procesamiento:
                procesamiento.archivo_reporte_final = archivo_path
                db.session.commit()
            
            logger.info(f"REPORTE EXCEL GENERADO | usuario={usuario} | periodo={periodo} | archivo={archivo_path}")
            
            return {
                'success': True,
                'archivo_path': archivo_path,
                'nombre_archivo': nombre_archivo
            }
            
        except Exception as e:
            logger.error(f"Error generando reporte Excel: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def enviar_reporte_email(cls, periodo, usuario, destinatarios):
        """Envía reporte por correo electrónico usando configuración del Gestor Documental"""
        try:
            # Generar reporte
            resultado_reporte = cls.generar_reporte_excel(periodo, usuario)
            if not resultado_reporte['success']:
                return resultado_reporte
            
            # Configuración de correo del sistema
            smtp_server = current_app.config.get('MAIL_SERVER')
            smtp_port = current_app.config.get('MAIL_PORT')
            smtp_user = current_app.config.get('MAIL_USERNAME')
            smtp_password = current_app.config.get('MAIL_PASSWORD')
            use_ssl = current_app.config.get('MAIL_USE_SSL', False)
            use_tls = current_app.config.get('MAIL_USE_TLS', False)
            
            if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
                return {
                    'success': False,
                    'error': 'Configuración de correo incompleta'
                }
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ', '.join(destinatarios)
            msg['Subject'] = f"Reporte DIAN vs ERP - Periodo {periodo}"
            
            # Cuerpo del mensaje
            stats = ValidacionService.obtener_estadisticas_periodo(periodo)
            cuerpo = f"""
            <html>
            <body>
                <h2>Reporte de Validación DIAN vs ERP</h2>
                <p><strong>Periodo:</strong> {periodo}</p>
                <p><strong>Generado por:</strong> {usuario}</p>
                <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h3>Resumen de Validación:</h3>
                <ul>
                    <li><strong>Total Validaciones:</strong> {stats.get('total_validaciones', 0)}</li>
                    <li><strong>Facturas Coincidentes:</strong> {stats.get('coincidentes', 0)} ({stats.get('porcentaje_coincidentes', 0)}%)</li>
                    <li><strong>Facturas Discrepantes:</strong> {stats.get('discrepantes', 0) + stats.get('diferencia_valor', 0)}</li>
                    <li><strong>Solo en DIAN:</strong> {stats.get('solo_dian', 0)}</li>
                    <li><strong>Solo en ERP:</strong> {stats.get('solo_erp', 0)}</li>
                </ul>
                
                <p>Se adjunta el reporte detallado en formato Excel.</p>
                
                <hr>
                <p><em>Este mensaje es generado automáticamente por el Gestor Documental - Supertiendas Cañaveral</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(cuerpo, 'html'))
            
            # Adjuntar archivo Excel
            with open(resultado_reporte['archivo_path'], 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f"attachment; filename= {resultado_reporte['nombre_archivo']}"
            )
            msg.attach(part)
            
            # Enviar correo
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port)
                if use_tls:
                    server.starttls()
            
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, destinatarios, msg.as_string())
            server.quit()
            
            logger.info(f"REPORTE ENVIADO POR EMAIL | usuario={usuario} | periodo={periodo} | destinatarios={len(destinatarios)}")
            
            return {
                'success': True,
                'mensaje': f'Reporte enviado exitosamente a {len(destinatarios)} destinatarios'
            }
            
        except Exception as e:
            logger.error(f"Error enviando reporte por email: {e}")
            return {
                'success': False,
                'error': str(e)
            }