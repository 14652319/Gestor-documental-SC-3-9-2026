"""
Modelos del módulo de Causaciones
"""
from extensions import db
from datetime import datetime

class DocumentoCausacion(db.Model):
    """Documentos PDF para causar"""
    __tablename__ = 'documentos_causacion'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.Text, nullable=False)
    
    # Datos extraídos del PDF
    es_factura_electronica = db.Column(db.Boolean, default=False)
    prefijo = db.Column(db.String(10))
    folio = db.Column(db.String(50))
    nit = db.Column(db.String(20))
    razon_social = db.Column(db.String(255))
    cufe = db.Column(db.String(255))
    valor_antes_iva = db.Column(db.Numeric(15, 2))
    valor_iva = db.Column(db.Numeric(15, 2))
    valor_total = db.Column(db.Numeric(15, 2))
    
    # Resolución de facturación
    resolucion = db.Column(db.String(50))
    rango_desde = db.Column(db.Integer)
    rango_hasta = db.Column(db.Integer)
    fecha_resolucion = db.Column(db.Date)
    
    # Clasificación
    centro_operacion_id = db.Column(db.Integer, db.ForeignKey('centros_operacion.id'))
    tiene_distribucion = db.Column(db.Boolean, default=False)
    
    # Usuarios
    subido_por = db.Column(db.String(50))
    autorizado_por = db.Column(db.String(50))
    
    # Estado
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, causado, rechazado
    observaciones = db.Column(db.Text)
    
    # Visualización en tiempo real
    siendo_visualizado_por = db.Column(db.String(50))  # Usuario actual viendo el PDF
    fecha_inicio_visualizacion = db.Column(db.DateTime)
    
    # Auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(50), nullable=False)
    
    # Relaciones
    centro_operacion = db.relationship('CentroOperacion', backref='documentos_causacion')
    observaciones_relacionadas = db.relationship('ObservacionCausacion', backref='documento', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre_archivo': self.nombre_archivo,
            'ruta_archivo': self.ruta_archivo,
            'es_factura_electronica': self.es_factura_electronica,
            'prefijo': self.prefijo,
            'folio': self.folio,
            'nit': self.nit,
            'razon_social': self.razon_social,
            'cufe': self.cufe,
            'valor_antes_iva': float(self.valor_antes_iva) if self.valor_antes_iva else None,
            'valor_iva': float(self.valor_iva) if self.valor_iva else None,
            'valor_total': float(self.valor_total) if self.valor_total else None,
            'resolucion': self.resolucion,
            'rango_desde': self.rango_desde,
            'rango_hasta': self.rango_hasta,
            'fecha_resolucion': self.fecha_resolucion.isoformat() if self.fecha_resolucion else None,
            'centro_operacion': {
                'id': self.centro_operacion.id,
                'codigo': self.centro_operacion.codigo,
                'nombre': self.centro_operacion.nombre
            } if self.centro_operacion else None,
            'tiene_distribucion': self.tiene_distribucion,
            'subido_por': self.subido_por,
            'autorizado_por': self.autorizado_por,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'siendo_visualizado_por': self.siendo_visualizado_por,
            'fecha_inicio_visualizacion': self.fecha_inicio_visualizacion.isoformat() if self.fecha_inicio_visualizacion else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            'tiene_observaciones': self.observaciones_relacionadas.count() > 0
        }


class ObservacionCausacion(db.Model):
    """Observaciones de documentos de causación desde cualquier módulo"""
    __tablename__ = 'observaciones_causacion'
    
    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos_causacion.id'), nullable=False)
    observacion = db.Column(db.Text, nullable=False)
    origen = db.Column(db.String(50), nullable=False)  # recepcion_facturas, radicacion, causacion, etc.
    created_by = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'documento_id': self.documento_id,
            'observacion': self.observacion,
            'origen': self.origen,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'ip_address': self.ip_address
        }
