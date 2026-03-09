"""
Modelos SQLAlchemy para el módulo de Notas Contables
Gestiona: documentos_contables, adjuntos_documentos, historial_documentos
"""
from datetime import datetime
from extensions import db

class DocumentoContable(db.Model):
    """Registro principal de documentos contables cargados"""
    __tablename__ = 'documentos_contables'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento_id = db.Column(db.Integer, db.ForeignKey('tipos_documento.id'), nullable=False)
    centro_operacion_id = db.Column(db.Integer, db.ForeignKey('centros_operacion.id'), nullable=False)
    consecutivo = db.Column(db.String(20), nullable=False)          # 00000123
    fecha_documento = db.Column(db.Date, nullable=False)
    empresa = db.Column(db.String(10), nullable=False)              # SC, LG
    nombre_archivo = db.Column(db.String(255), nullable=False)      # CO-TIPO-CONSECUTIVO.pdf
    ruta_archivo = db.Column(db.String(500), nullable=False)        # Ruta completa
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default='activo')  # activo/anulado/eliminado
    created_by = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relaciones
    tipo_documento = db.relationship('TipoDocumento', foreign_keys=[tipo_documento_id], lazy='joined')
    centro_operacion = db.relationship('CentroOperacion', foreign_keys=[centro_operacion_id], lazy='joined')
    adjuntos = db.relationship('AdjuntoDocumento', backref='documento', lazy=True, cascade='all, delete-orphan')
    historial = db.relationship('HistorialDocumento', backref='documento', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('tipo_documento_id', 'centro_operacion_id', 'consecutivo', 
                           name='uq_tipo_centro_consecutivo'),
    )
    
    def to_dict(self, include_relations=False):
        """Convierte el objeto a diccionario para JSON"""
        # ⭐ Obtener nombre completo de la empresa desde la tabla empresas
        empresa_nombre_completo = self.empresa  # Por defecto usar la sigla
        try:
            from modules.configuracion.models import Empresa
            empresa_obj = Empresa.query.filter_by(sigla=self.empresa).first()
            if empresa_obj:
                empresa_nombre_completo = f"{empresa_obj.sigla} - {empresa_obj.nombre}"
        except Exception as e:
            # Si hay error, usar solo la sigla
            pass
        
        data = {
            'id': self.id,
            'tipo_documento_id': self.tipo_documento_id,
            'centro_operacion_id': self.centro_operacion_id,
            'consecutivo': self.consecutivo,
            'fecha_documento': self.fecha_documento.strftime('%Y-%m-%d') if self.fecha_documento else None,
            'empresa': empresa_nombre_completo,  # ⭐ AHORA RETORNA "LG - LA GALERÍA Y CIA SAS"
            'empresa_sigla': self.empresa,  # ⭐ AÑADIR SIGLA POR SEPARADO por si se necesita
            'nombre_archivo': self.nombre_archivo,
            'ruta_archivo': self.ruta_archivo,
            'observaciones': self.observaciones,
            'estado': self.estado,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        
        if include_relations:
            data['tipo_documento'] = self.tipo_documento.to_dict() if self.tipo_documento else None
            data['centro_operacion'] = self.centro_operacion.to_dict() if self.centro_operacion else None
            data['adjuntos'] = [adj.to_dict() for adj in self.adjuntos]
        
        return data

    def __init__(self, **kwargs):
        """Permite alias en español para compatibilidad de pruebas y rutas.
        - usuario_creador -> created_by
        - modified_by -> updated_by (si se persiste en algún flujo)
        """
        if 'usuario_creador' in kwargs and 'created_by' not in kwargs:
            kwargs['created_by'] = kwargs.pop('usuario_creador')
        if 'modified_by' in kwargs and 'updated_by' not in kwargs:
            # No todos los flujos lo persisten, pero aceptamos el alias para evitar errores
            kwargs['updated_by'] = kwargs.pop('modified_by')
        super().__init__(**kwargs)

class AdjuntoDocumento(db.Model):
    """Archivos adjuntos asociados a cada documento"""
    __tablename__ = 'adjuntos_documentos'
    
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos_contables.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    tipo_archivo = db.Column(db.String(50))                         # xlsx, jpg, png
    tamano_bytes = db.Column(db.Integer)
    descripcion = db.Column(db.String(255))
    created_by = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'documento_id': self.documento_id,
            'nombre_archivo': self.nombre_archivo,
            'ruta_archivo': self.ruta_archivo,
            'tipo_archivo': self.tipo_archivo,
            'tamano_bytes': self.tamano_bytes,
            'tamano_mb': round(self.tamano_bytes / 1024 / 1024, 2) if self.tamano_bytes else 0,
            'descripcion': self.descripcion,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class HistorialDocumento(db.Model):
    """Auditoría completa de cambios en documentos"""
    __tablename__ = 'historial_documentos'
    
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos_contables.id'), nullable=False)
    accion = db.Column(db.String(50), nullable=False)               # CREADO, EDITADO, ANULADO, VISUALIZADO
    campo_modificado = db.Column(db.String(100))
    valor_anterior = db.Column(db.Text)
    valor_nuevo = db.Column(db.Text)
    motivo = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    created_by = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'documento_id': self.documento_id,
            'accion': self.accion,
            'campo_modificado': self.campo_modificado,
            'valor_anterior': self.valor_anterior,
            'valor_nuevo': self.valor_nuevo,
            'motivo': self.motivo,
            'ip_address': self.ip_address,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class ObservacionDocumento(db.Model):
    """Observaciones con auditoría completa"""
    __tablename__ = 'observaciones_documentos'
    
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos_contables.id'), nullable=False)
    observacion = db.Column(db.Text, nullable=False)
    momento = db.Column(db.String(20), nullable=False)  # CARGA, EDICION
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    created_by = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con documento
    documento = db.relationship('DocumentoContable', backref=db.backref('observaciones_auditadas', lazy=True))
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'documento_id': self.documento_id,
            'observacion': self.observacion,
            'momento': self.momento,
            'ip_address': self.ip_address,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class TokenCorreccionDocumento(db.Model):
    """Tokens de validación para correcciones de campos críticos en documentos"""
    __tablename__ = 'tokens_correccion_documento'
    
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos_contables.id'), nullable=False)
    token = db.Column(db.String(6), nullable=False)  # Código de 6 dígitos
    
    # Campos que se van a cambiar
    empresa_anterior = db.Column(db.String(10))  # Sigla: SC, LG, etc.
    empresa_nueva = db.Column(db.String(10))     # Sigla: SC, LG, etc.
    tipo_documento_anterior_id = db.Column(db.Integer)
    tipo_documento_nuevo_id = db.Column(db.Integer)
    centro_operacion_anterior_id = db.Column(db.Integer)
    centro_operacion_nuevo_id = db.Column(db.Integer)
    consecutivo_anterior = db.Column(db.String(20))
    consecutivo_nuevo = db.Column(db.String(20))
    fecha_documento_anterior = db.Column(db.Date)
    fecha_documento_nueva = db.Column(db.Date)
    
    # Justificación del cambio
    justificacion = db.Column(db.Text, nullable=False)
    
    # Control de validación
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_expiracion = db.Column(db.DateTime, nullable=False)  # +10 minutos
    intentos_validacion = db.Column(db.Integer, default=0, nullable=False)
    usado = db.Column(db.Boolean, default=False, nullable=False)
    fecha_uso = db.Column(db.DateTime)
    
    # Auditoría
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    created_by = db.Column(db.String(50), nullable=False)
    validado_por = db.Column(db.String(50))
    
    # Relación
    documento = db.relationship('DocumentoContable', backref=db.backref('tokens_correccion', lazy=True))
    
    def esta_vigente(self):
        """Verifica si el token aún está vigente"""
        from utils_fecha import obtener_fecha_naive_colombia
        fecha_actual = obtener_fecha_naive_colombia()
        return (
            not self.usado and
            fecha_actual < self.fecha_expiracion and
            self.intentos_validacion < 3
        )
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'documento_id': self.documento_id,
            'token': self.token,
            'empresa_anterior': self.empresa_anterior,
            'empresa_nueva': self.empresa_nueva,
            'tipo_documento_anterior_id': self.tipo_documento_anterior_id,
            'tipo_documento_nuevo_id': self.tipo_documento_nuevo_id,
            'centro_operacion_anterior_id': self.centro_operacion_anterior_id,
            'centro_operacion_nuevo_id': self.centro_operacion_nuevo_id,
            'consecutivo_anterior': self.consecutivo_anterior,
            'consecutivo_nuevo': self.consecutivo_nuevo,
            'justificacion': self.justificacion,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            'fecha_expiracion': self.fecha_expiracion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_expiracion else None,
            'intentos_validacion': self.intentos_validacion,
            'usado': self.usado,
            'fecha_uso': self.fecha_uso.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_uso else None,
            'created_by': self.created_by,
            'validado_por': self.validado_por
        }

