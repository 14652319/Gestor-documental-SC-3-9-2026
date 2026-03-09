"""
Modelos para Gestión de Terceros
Conecta con la tabla terceros existente
"""

from extensions import db
from datetime import datetime
from sqlalchemy import func

# Usamos el modelo Tercero original importándolo desde app
def get_tercero_model():
    """Función helper para obtener el modelo Tercero"""
    from app import Tercero
    return Tercero

class TerceroStats:
    """Clase helper para estadísticas de terceros"""
    
    @staticmethod
    def obtener_estadisticas():
        """Obtiene estadísticas de la tabla terceros"""
        try:
            from app import Tercero
            
            # Total de terceros
            total = Tercero.query.count()
            
            # Terceros activos (asumiendo que tienen usuarios activos)
            # Por ahora contamos todos como activos
            activos = total
            
            # Terceros recientes (últimos 30 días)
            hace_30_dias = datetime.now().date()
            try:
                from datetime import timedelta
                hace_30_dias = datetime.now() - timedelta(days=30)
                recientes = Tercero.query.filter(
                    Tercero.fecha_registro >= hace_30_dias
                ).count()
            except:
                recientes = 0
            
            # Estados por tipo de persona
            personas_naturales = Tercero.query.filter_by(tipo_persona='natural').count()
            personas_juridicas = Tercero.query.filter_by(tipo_persona='juridica').count()
            
            return {
                'total_terceros': total,
                'terceros_activos': activos,
                'terceros_recientes': recientes,
                'personas_naturales': personas_naturales,
                'personas_juridicas': personas_juridicas,
                'tasa_crecimiento': round((recientes / total * 100), 2) if total > 0 else 0
            }
            
        except Exception as e:
            print(f"Error en estadísticas: {e}")
            return {
                'total_terceros': 0,
                'terceros_activos': 0,
                'terceros_recientes': 0,
                'personas_naturales': 0,
                'personas_juridicas': 0,
                'tasa_crecimiento': 0
            }

class TerceroHelper:
    """Clase helper para operaciones con terceros"""
    
    @staticmethod
    def listar_terceros(page=1, per_page=200, search='', estado='', orden='fecha_desc'):
        """Lista terceros con paginación y filtros"""
        try:
            from app import Tercero
            
            query = Tercero.query
            
            # Filtro por búsqueda (simplificado)
            if search:
                query = query.filter(
                    db.or_(
                        Tercero.nit.contains(search),
                        Tercero.razon_social.contains(search)
                    )
                )
            
            # Filtro por estado (usando el campo estado de la BD)
            if estado and estado != 'todos' and estado != '':
                if estado == 'activos':
                    query = query.filter_by(estado='activo')
                elif estado == 'inactivos':
                    query = query.filter_by(estado='inactivo')
                else:
                    # Si es un tipo de persona específico
                    query = query.filter_by(tipo_persona=estado)
            
            # Ordenamiento
            if orden == 'fecha_desc':
                if hasattr(Tercero, 'fecha_registro'):
                    query = query.order_by(Tercero.fecha_registro.desc())
                else:
                    query = query.order_by(Tercero.id.desc())
            elif orden == 'fecha_asc':
                if hasattr(Tercero, 'fecha_registro'):
                    query = query.order_by(Tercero.fecha_registro.asc())
                else:
                    query = query.order_by(Tercero.id.asc())
            elif orden == 'razon_social':
                query = query.order_by(Tercero.razon_social.asc())
            elif orden == 'nit':
                query = query.order_by(Tercero.nit.asc())
            
            # Paginación
            terceros_paginados = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return terceros_paginados
            
        except Exception as e:
            print(f"Error listando terceros: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def obtener_tercero_por_id(tercero_id):
        """Obtiene un tercero por ID"""
        try:
            from app import Tercero
            return Tercero.query.get(tercero_id)
        except Exception as e:
            print(f"Error obteniendo tercero: {e}")
            return None
    
    @staticmethod
    def buscar_por_nit(nit):
        """Busca un tercero por NIT"""
        try:
            from app import Tercero
            return Tercero.query.filter_by(nit=nit).first()
        except Exception as e:
            print(f"Error buscando por NIT: {e}")
            return None
    
    # Información de contacto extendida
    telefono_secundario = db.Column(db.String(20))
    contacto_principal = db.Column(db.String(100))
    cargo_contacto = db.Column(db.String(100))
    
    # Información comercial
    categoria_tercero = db.Column(db.String(50))  # Proveedor, Cliente, Empleado, etc.
    clasificacion = db.Column(db.String(50))  # A, B, C según volumen/importancia
    limite_credito = db.Column(db.Numeric(15, 2), default=0)
    
    # Configuración de notificaciones
    frecuencia_notificacion = db.Column(db.Integer, default=365)  # días
    ultimo_envio_notificacion = db.Column(db.DateTime)
    notificaciones_activas = db.Column(db.Boolean, default=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    usuario_creacion = db.Column(db.String(100))
    usuario_actualizacion = db.Column(db.String(100))
    
    # Relación con tercero principal
    tercero = db.relationship('Tercero', backref='informacion_extendida', lazy=True)

class EstadoDocumentacion(db.Model):
    """
    Control de estados de documentación por tercero
    """
    __tablename__ = 'estados_documentacion'
    
    id = db.Column(db.Integer, primary_key=True)
    tercero_id = db.Column(db.Integer, db.ForeignKey('terceros.id'), nullable=False)
    
    # Estados de documentación
    documentos_completos = db.Column(db.Boolean, default=False)
    documentos_aprobados = db.Column(db.Boolean, default=False)
    requiere_actualizacion = db.Column(db.Boolean, default=False)
    
    # Contadores
    total_documentos = db.Column(db.Integer, default=0)
    documentos_aprobados_count = db.Column(db.Integer, default=0)
    documentos_rechazados_count = db.Column(db.Integer, default=0)
    
    # Fechas importantes
    fecha_ultima_carga = db.Column(db.DateTime)
    fecha_ultima_aprobacion = db.Column(db.DateTime)
    fecha_proxima_actualizacion = db.Column(db.DateTime)
    
    # Observaciones
    observaciones = db.Column(db.Text)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    tercero = db.relationship('Tercero', backref='estado_documentacion', lazy=True)

class HistorialNotificaciones(db.Model):
    """
    Registro de todas las notificaciones enviadas a terceros
    """
    __tablename__ = 'historial_notificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    tercero_id = db.Column(db.Integer, db.ForeignKey('terceros.id'), nullable=False)
    
    # Información del envío
    tipo_notificacion = db.Column(db.String(50), nullable=False)  # 'manual', 'automatica', 'masiva'
    asunto = db.Column(db.String(200))
    mensaje = db.Column(db.Text)
    
    # Estado del envío
    estado_envio = db.Column(db.String(20), default='pendiente')  # 'enviado', 'error', 'pendiente'
    correo_destinatario = db.Column(db.String(100))
    fecha_envio = db.Column(db.DateTime, default=datetime.now)
    fecha_lectura = db.Column(db.DateTime)
    
    # Información del remitente
    usuario_envia = db.Column(db.String(100))
    ip_origen = db.Column(db.String(50))
    
    # Detalles técnicos
    error_envio = db.Column(db.Text)
    id_mensaje_correo = db.Column(db.String(200))
    
    # Relaciones
    tercero = db.relationship('Tercero', backref='historial_notificaciones', lazy=True)

class AprobacionDocumentos(db.Model):
    """
    Sistema de aprobación individual de documentos
    """
    __tablename__ = 'aprobaciones_documentos'
    
    id = db.Column(db.Integer, primary_key=True)
    tercero_id = db.Column(db.Integer, db.ForeignKey('terceros.id'), nullable=False)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos_tercero.id'), nullable=False)
    
    # Estado de aprobación
    estado = db.Column(db.String(20), default='pendiente')  # 'aprobado', 'rechazado', 'pendiente', 'revision'
    observaciones = db.Column(db.Text)
    requiere_reemplazo = db.Column(db.Boolean, default=False)
    
    # Información del revisor
    usuario_revisa = db.Column(db.String(100))
    fecha_revision = db.Column(db.DateTime)
    
    # Información de calidad del documento
    calidad_documento = db.Column(db.String(20))  # 'excelente', 'buena', 'regular', 'mala'
    es_legible = db.Column(db.Boolean, default=True)
    informacion_completa = db.Column(db.Boolean, default=True)
    documento_vigente = db.Column(db.Boolean, default=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    tercero = db.relationship('Tercero', backref='aprobaciones_documentos', lazy=True)
    documento = db.relationship('DocumentoTercero', backref='aprobaciones', lazy=True)

class ConfiguracionNotificaciones(db.Model):
    """
    Configuración global para el sistema de notificaciones
    """
    __tablename__ = 'configuracion_notificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Configuración de envío masivo
    correos_por_bloque = db.Column(db.Integer, default=5)
    segundos_entre_bloques = db.Column(db.Integer, default=5)
    
    # Plantillas de correo
    plantilla_actualizacion = db.Column(db.Text)
    plantilla_aprobacion = db.Column(db.Text)
    plantilla_rechazo = db.Column(db.Text)
    
    # Configuración de frecuencias
    dias_recordatorio_defecto = db.Column(db.Integer, default=365)
    dias_anticipacion_vencimiento = db.Column(db.Integer, default=30)
    
    # Estado del sistema
    notificaciones_activas = db.Column(db.Boolean, default=True)
    envio_automatico_activo = db.Column(db.Boolean, default=False)
    
    # Auditoría
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    usuario_actualizacion = db.Column(db.String(100))