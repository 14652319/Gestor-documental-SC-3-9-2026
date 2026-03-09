# -*- coding: utf-8 -*-
"""
Modelos de Base de Datos - Facturas Digitales
"""
from extensions import db
from datetime import datetime

class ConfigRutasFacturas(db.Model):
    """Configuración de rutas de almacenamiento"""
    __tablename__ = 'config_rutas_facturas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    ruta_local = db.Column(db.Text, nullable=False)
    ruta_red = db.Column(db.Text)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_creacion = db.Column(db.String(100))
    observaciones = db.Column(db.Text)


class FacturaDigital(db.Model):
    """
    Factura digital recibida - MODELO CORREGIDO
    Basado en la estructura REAL de sql/facturas_digitales_schema.sql
    CAMBIO CRÍTICO: La tabla usa 'numero_factura', NO 'prefijo' + 'folio'
    """
    __tablename__ = 'facturas_digitales'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Identificación - CORREGIDO: usa numero_factura (ej: "FE-1", "NC-45")
    numero_factura = db.Column(db.String(50), nullable=False)
    radicado_rfd = db.Column(db.String(20), unique=True)  # RFD-000001, RFD-000002, etc.
    nit_proveedor = db.Column(db.String(20), nullable=False)
    razon_social_proveedor = db.Column(db.String(255), nullable=False)
    empresa = db.Column(db.String(10))  # Sigla de la empresa (SC, SCE, etc.)
    
    # Fechas
    fecha_emision = db.Column(db.Date, nullable=False)
    fecha_vencimiento = db.Column(db.Date)
    
    # Valores
    valor_total = db.Column(db.Numeric(15, 2), nullable=False)
    valor_iva = db.Column(db.Numeric(15, 2), default=0)
    valor_base = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Información del archivo
    nombre_archivo_original = db.Column(db.String(255), nullable=False)
    nombre_archivo_sistema = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.Text, nullable=False)
    ruta_carpeta = db.Column(db.Text)  # Ruta relativa de la carpeta
    ruta_archivo_principal = db.Column(db.Text)  # Nombre del archivo principal
    ruta_archivo_anexo1 = db.Column(db.Text)  # Anexo 1
    ruta_archivo_anexo2 = db.Column(db.Text)  # Anexo 2
    ruta_archivo_seg_social = db.Column(db.Text)  # Seguridad social
    tipo_archivo = db.Column(db.String(10), nullable=False)  # pdf, xml, zip
    tamanio_kb = db.Column(db.Numeric(10, 2))
    
    # Estado y control
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, aprobado, rechazado, en_revision
    motivo_rechazo = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    
    # Usuario que carga (puede ser externo o interno)
    usuario_carga = db.Column(db.String(100), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False)  # externo, interno
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    ip_carga = db.Column(db.String(45))
    
    # Usuario que revisa (solo interno)
    usuario_revision = db.Column(db.String(100))
    fecha_revision = db.Column(db.DateTime)
    
    # Metadatos
    hash_archivo = db.Column(db.String(64))  # SHA256 para evitar duplicados
    activo = db.Column(db.Boolean, default=True)
    
    # ============================================================================
    # CAMPOS FASE 1 - Workflow y Control de Firma
    # ============================================================================
    tipo_documento = db.Column(db.String(30))  # FACTURA_ELECTRONICA, NOTA_CREDITO, etc.
    tipo_servicio = db.Column(db.String(50))  # SERVICIOS_PUBLICOS, ARRENDAMIENTO, etc.
    departamento = db.Column(db.String(50))  # FINANCIERO, TECNOLOGIA, COMPRAS_Y_SUMINISTROS, etc.
    forma_pago = db.Column(db.String(30))  # ESTANDAR, TARJETA_CREDITO
    estado_firma = db.Column(db.String(30))  # PENDIENTE, EN_FIRMA, FIRMADO, RECHAZADO
    archivo_firmado_path = db.Column(db.Text)  # Ruta del PDF firmado con Adobe Sign
    numero_causacion = db.Column(db.String(50))  # Número de causación asociada
    fecha_pago = db.Column(db.Date)  # Fecha en que se pagó la factura
    
    # Constraint: Un proveedor no puede tener dos facturas con el mismo número
    __table_args__ = (
        db.UniqueConstraint('numero_factura', 'nit_proveedor', name='uk_factura_proveedor'),
    )
    
    def __repr__(self):
        return f'<FacturaDigital {self.numero_factura} - {self.razon_social_proveedor}>'


class FacturaDigitalHistorial(db.Model):
    """Histórico de cambios de estado"""
    __tablename__ = 'facturas_digitales_historial'
    
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas_digitales.id', ondelete='CASCADE'), nullable=False)
    estado_anterior = db.Column(db.String(20))
    estado_nuevo = db.Column(db.String(20), nullable=False)
    usuario = db.Column(db.String(100), nullable=False)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.Text)
    observaciones = db.Column(db.Text)


class FacturaDigitalAdjunto(db.Model):
    """Archivos adjuntos adicionales"""
    __tablename__ = 'facturas_digitales_adjuntos'
    
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas_digitales.id', ondelete='CASCADE'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.Text, nullable=False)
    tipo_archivo = db.Column(db.String(10), nullable=False)
    tamanio_kb = db.Column(db.Numeric(10, 2))
    descripcion = db.Column(db.String(255))
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_carga = db.Column(db.String(100), nullable=False)


class FacturaDigitalNotificacion(db.Model):
    """Notificaciones a usuarios"""
    __tablename__ = 'facturas_digitales_notificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas_digitales.id', ondelete='CASCADE'), nullable=False)
    usuario_destino = db.Column(db.String(100), nullable=False)
    tipo_notificacion = db.Column(db.String(50), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    leida = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_lectura = db.Column(db.DateTime)


class ConsecutivoRFD(db.Model):
    """Consecutivo para Radicados de Facturas Digitales (RFD)"""
    __tablename__ = 'consecutivos_rfd'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), unique=True, nullable=False)
    ultimo_numero = db.Column(db.Integer, nullable=False, default=0)
    prefijo = db.Column(db.String(10), default='RFD')
    longitud_numero = db.Column(db.Integer, default=6)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FacturaDigitalMetrica(db.Model):
    """Métricas y estadísticas"""
    __tablename__ = 'facturas_digitales_metricas'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, unique=True)
    total_facturas_cargadas = db.Column(db.Integer, default=0)
    total_facturas_aprobadas = db.Column(db.Integer, default=0)
    total_facturas_rechazadas = db.Column(db.Integer, default=0)
    total_facturas_pendientes = db.Column(db.Integer, default=0)
    valor_total_facturas = db.Column(db.Numeric(15, 2), default=0)
    tiempo_promedio_revision_minutos = db.Column(db.Integer, default=0)
