"""
Modelos SAGRILAFT - Preregistro de Terceros
Importa modelos existentes de app.py y crea solo TerceroPreregistro
"""

from extensions import db
from datetime import datetime

# NO redefinir estos modelos - ya existen en app.py
# Los importaremos en routes.py directamente desde app
# from app import SolicitudRegistro, DocumentoTercero

class TerceroPreregistro(db.Model):
    """
    Terceros EN PREREGISTRO - Pendientes de aprobación
    Se usa durante el proceso de SAGRILAFT hasta aprobar/rechazar
    Al aprobar, se migran a la tabla 'terceros' del módulo principal
    """
    __tablename__ = 'terceros_preregistro'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), unique=True, nullable=False, index=True)
    razon_social = db.Column(db.String(255), nullable=False)
    tipo_persona = db.Column(db.String(20))  # 'natural' o 'juridica'
    primer_nombre = db.Column(db.String(80))
    segundo_nombre = db.Column(db.String(80))
    primer_apellido = db.Column(db.String(80))
    segundo_apellido = db.Column(db.String(80))
    correo = db.Column(db.String(120))
    celular = db.Column(db.String(30))
    acepta_terminos = db.Column(db.Boolean, default=True)
    acepta_contacto = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado_preregistro = db.Column(db.String(20), default="en_revision")  # en_revision, aprobado, rechazado
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TerceroPreregistro {self.nit} - {self.razon_social}>'


class AlertaVencimiento(db.Model):
    """
    Registro de alertas de vencimiento enviadas a proveedores
    Controla envío de alerta inicial (20 días) y recordatorio (8 días después)
    """
    __tablename__ = 'alertas_vencimiento_sagrilaft'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    tercero_id = db.Column(db.Integer, db.ForeignKey('terceros.id'), nullable=False)
    radicado = db.Column(db.String(20), nullable=False)
    
    # Control de envíos
    fecha_primera_alerta = db.Column(db.DateTime, nullable=True)  # Primera alerta (20 días restantes)
    fecha_recordatorio = db.Column(db.DateTime, nullable=True)    # Recordatorio (8 días después)
    recordatorio_enviado = db.Column(db.Boolean, default=False)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AlertaVencimiento {self.radicado} - Tercero {self.tercero_id}>'
