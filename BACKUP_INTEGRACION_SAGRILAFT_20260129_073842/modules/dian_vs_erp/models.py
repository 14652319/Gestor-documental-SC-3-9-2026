"""
Modelos del Módulo DIAN VS ERP - PostgreSQL
Migrado desde SQLite a PostgreSQL
Fecha: 24 de Diciembre de 2025
"""

from extensions import db
from datetime import datetime

class MaestroDianVsErp(db.Model):
    """Tabla principal de facturas DIAN vs ERP"""
    __tablename__ = 'maestro_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Datos del emisor
    nit_emisor = db.Column(db.String(20), nullable=False, index=True)
    razon_social = db.Column(db.String(255))
    
    # Datos de la factura
    fecha_emision = db.Column(db.Date, index=True)
    prefijo = db.Column(db.String(10), index=True)
    folio = db.Column(db.String(20), nullable=False, index=True)
    valor = db.Column(db.Numeric(15, 2))
    
    # Estados y clasificación
    estado_aprobacion = db.Column(db.String(100))  # Ampliado para "Aprobado con notificación"
    forma_pago = db.Column(db.String(100))  # Ampliado
    tipo_documento = db.Column(db.String(100))  # Ampliado
    tipo_servicio = db.Column(db.String(100))
    departamento = db.Column(db.String(100))
    tipo_tercero = db.Column(db.String(50))  # NUEVO: Tipo de tercero
    cufe = db.Column(db.String(255))  # NUEVO: CUFE/CUDE
    modulo = db.Column(db.String(50))  # NUEVO: COMERCIAL/FINANCIERO
    estado_contable = db.Column(db.String(100))  # NUEVO: Estado contable (ampliado)
    dias_desde_emision = db.Column(db.Integer)  # NUEVO: Días desde emisión
    doc_causado_por = db.Column(db.String(100))  # NUEVO: Usuario que causó
    
    # Causación
    causada = db.Column(db.Boolean, default=False, index=True)
    fecha_causacion = db.Column(db.DateTime)
    usuario_causacion = db.Column(db.String(100))
    
    # Recibida
    recibida = db.Column(db.Boolean, default=False, index=True)
    fecha_recibida = db.Column(db.DateTime)
    
    # 🔄 SINCRONIZACIÓN EN TIEMPO REAL (agregados 28/12/2025)
    usuario_recibio = db.Column(db.String(100))  # Usuario que recibió la factura
    origen_sincronizacion = db.Column(db.String(50), index=True)  # RECIBIR_FACTURAS, RELACIONES, etc.
    rechazada = db.Column(db.Boolean, default=False)  # Si fue rechazada
    motivo_rechazo = db.Column(db.Text)  # Motivo del rechazo
    fecha_rechazo = db.Column(db.DateTime)  # Fecha y hora del rechazo
    
    # Acuses (para documentos tipo crédito)
    acuses_recibidos = db.Column(db.Integer, default=0)
    acuses_requeridos = db.Column(db.Integer, default=3)
    
    # Metadatos
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'nit_emisor': self.nit_emisor,
            'razon_social': self.razon_social,
            'fecha_emision': self.fecha_emision.strftime('%Y-%m-%d') if self.fecha_emision else None,
            'prefijo': self.prefijo,
            'folio': self.folio,
            'valor': float(self.valor) if self.valor else 0.0,
            'estado_aprobacion': self.estado_aprobacion,
            'forma_pago': self.forma_pago,
            'tipo_documento': self.tipo_documento,
            'tipo_servicio': self.tipo_servicio,
            'departamento': self.departamento,
            'causada': self.causada,
            'fecha_causacion': self.fecha_causacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_causacion else None,
            'usuario_causacion': self.usuario_causacion,
            'recibida': self.recibida,
            'fecha_recibida': self.fecha_recibida.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_recibida else None,
            'acuses_recibidos': self.acuses_recibidos,
            'acuses_requeridos': self.acuses_requeridos,
        }
    
    def __repr__(self):
        return f'<Factura {self.prefijo}-{self.folio} | NIT: {self.nit_emisor}>'


class EnvioProgramadoDianVsErp(db.Model):
    """Configuraciones de envíos automáticos"""
    __tablename__ = 'envios_programados_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # PENDIENTES_DIAS, CREDITO_SIN_ACUSES
    
    # Criterios de filtrado
    dias_minimos = db.Column(db.Integer, default=3)
    requiere_acuses_minimo = db.Column(db.Integer, default=2)
    estados_incluidos = db.Column(db.Text)  # JSON
    estados_excluidos = db.Column(db.Text)  # JSON
    tipos_tercero = db.Column(db.Text)  # 🆕 JSON: ["PROVEEDORES", "ACREEDORES", "PROVEEDORES Y ACREEDORES", "NO REGISTRADOS"]
    
    # 🆕 FILTROS DE FECHA (26/01/2026) - Para limitar documentos por rango de fechas de emisión
    fecha_inicio = db.Column(db.Date)  # Desde qué fecha considerar documentos (opcional)
    fecha_fin = db.Column(db.Date)  # Hasta qué fecha considerar documentos (opcional)
    
    # Configuración de envío
    hora_envio = db.Column(db.String(5), nullable=False)  # HH:MM
    frecuencia = db.Column(db.String(20), nullable=False)  # DIARIO, SEMANAL, MENSUAL
    dias_semana = db.Column(db.Text)  # JSON: [1,2,3,4,5]
    
    # Destinatarios
    tipo_destinatario = db.Column(db.String(50))  # SOLICITANTE, CAUSADOR, APROBADOR
    email_cc = db.Column(db.Text)
    
    # 🆕 SUPERVISIÓN (28/12/2025) - NO afecta configs existentes
    es_supervision = db.Column(db.Boolean, default=False)  # FALSE = config normal
    email_supervisor = db.Column(db.String(255))  # Email del supervisor
    frecuencia_dias = db.Column(db.Integer, default=1)  # 1=diario, 4=cada 4 días, 7=semanal
    
    # Estado
    activo = db.Column(db.Boolean, default=True, index=True)
    ultimo_envio = db.Column(db.DateTime)
    proximo_envio = db.Column(db.DateTime)
    
    # Estadísticas
    total_ejecuciones = db.Column(db.Integer, default=0)
    total_documentos_procesados = db.Column(db.Integer, default=0)
    total_emails_enviados = db.Column(db.Integer, default=0)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_creacion = db.Column(db.String(100))
    fecha_modificacion = db.Column(db.DateTime)
    usuario_modificacion = db.Column(db.String(100))
    
    # Relación con historial
    historial = db.relationship('HistorialEnvioDianVsErp', backref='configuracion', lazy='dynamic')
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'dias_minimos': self.dias_minimos,
            'requiere_acuses_minimo': self.requiere_acuses_minimo,
            'estados_incluidos': self.estados_incluidos,
            'estados_excluidos': self.estados_excluidos,
            'tipos_tercero': self.tipos_tercero,  # 🆕 FILTRO TIPOS DE TERCERO
            # 🆕 FILTROS DE FECHA (26/01/2026)
            'fecha_inicio': self.fecha_inicio.strftime('%Y-%m-%d') if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.strftime('%Y-%m-%d') if self.fecha_fin else None,
            'hora_envio': self.hora_envio,
            'frecuencia': self.frecuencia,
            'dias_semana': self.dias_semana,
            'tipo_destinatario': self.tipo_destinatario,
            'email_cc': self.email_cc,
            'es_supervision': self.es_supervision,
            'email_supervisor': self.email_supervisor,
            'frecuencia_dias': self.frecuencia_dias,
            'activo': self.activo,
            'ultimo_envio': self.ultimo_envio.strftime('%Y-%m-%d %H:%M:%S') if self.ultimo_envio else None,
            'proximo_envio': self.proximo_envio.strftime('%Y-%m-%d %H:%M:%S') if self.proximo_envio else None,
            'total_ejecuciones': self.total_ejecuciones,
            'total_documentos_procesados': self.total_documentos_procesados,
            'total_emails_enviados': self.total_emails_enviados,
        }
    
    def __repr__(self):
        return f'<EnvíoProgramado {self.id}: {self.nombre}>'


class UsuarioAsignadoDianVsErp(db.Model):
    """Usuarios asignados por NIT para recibir alertas"""
    __tablename__ = 'usuarios_asignados_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), nullable=False, index=True)
    correo = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True, index=True)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_creacion = db.Column(db.String(100))
    fecha_modificacion = db.Column(db.DateTime)
    usuario_modificacion = db.Column(db.String(100))
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'nit': self.nit,
            'correo': self.correo,
            'nombre': self.nombre,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
        }
    
    def __repr__(self):
        return f'<UsuarioAsignado {self.nit} | {self.correo}>'


class UsuarioCausacionDianVsErp(db.Model):
    """Usuarios para causación de documentos"""
    __tablename__ = 'usuarios_causacion_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_causador = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True, index=True)
    
    # Estadísticas
    total_documentos = db.Column(db.Integer, default=0)
    ultimo_documento_fecha = db.Column(db.Date)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_creacion = db.Column(db.String(100))
    fecha_modificacion = db.Column(db.DateTime)
    usuario_modificacion = db.Column(db.String(100))
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre_causador': self.nombre_causador,
            'email': self.email,
            'activo': self.activo,
            'total_documentos': self.total_documentos,
            'ultimo_documento_fecha': self.ultimo_documento_fecha.strftime('%Y-%m-%d') if self.ultimo_documento_fecha else None,
        }
    
    def __repr__(self):
        return f'<UsuarioCausación {self.nombre_causador}>'


class HistorialEnvioDianVsErp(db.Model):
    """Historial de ejecuciones de envíos programados"""
    __tablename__ = 'historial_envios_dian_vs_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    configuracion_id = db.Column(db.Integer, db.ForeignKey('envios_programados_dian_vs_erp.id'), nullable=False, index=True)
    
    # Información del envío
    fecha_ejecucion = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    documentos_procesados = db.Column(db.Integer, default=0)
    documentos_enviados = db.Column(db.Integer, default=0)
    emails_enviados = db.Column(db.Integer, default=0)
    emails_fallidos = db.Column(db.Integer, default=0)
    
    # Detalle de envíos (JSON)
    destinatarios_enviados = db.Column(db.Text)
    destinatarios_fallidos = db.Column(db.Text)
    
    # Resultado
    estado = db.Column(db.String(20), nullable=False, index=True)  # EXITOSO, PARCIAL, FALLIDO
    mensaje = db.Column(db.Text)
    duracion_segundos = db.Column(db.Float)
    
    # Errores
    errores = db.Column(db.Text)
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'configuracion_id': self.configuracion_id,
            'fecha_ejecucion': self.fecha_ejecucion.strftime('%Y-%m-%d %H:%M:%S'),
            'documentos_procesados': self.documentos_procesados,
            'documentos_enviados': self.documentos_enviados,
            'emails_enviados': self.emails_enviados,
            'emails_fallidos': self.emails_fallidos,
            'destinatarios_enviados': self.destinatarios_enviados,
            'destinatarios_fallidos': self.destinatarios_fallidos,
            'estado': self.estado,
            'mensaje': self.mensaje,
            'duracion_segundos': self.duracion_segundos,
            'errores': self.errores,
        }
    
    def __repr__(self):
        return f'<HistorialEnvío {self.id} | {self.estado}>'


# ================================================================================
# MODELO: LogSistemaDianVsErp - Sistema de logs robusto con contexto completo
# ================================================================================
class LogSistemaDianVsErp(db.Model):
    """
    Sistema de logs mejorado para el módulo DIAN VS ERP.
    
    Características:
    - Contexto completo: usuario, IP, NIT, empresa
    - Performance tracking: duracion_ms
    - Error tracking: stack_trace completo
    - Búsquedas rápidas: 7 índices optimizados
    """
    __tablename__ = 'logs_sistema_dian_vs_erp'
    
    # Identificador
    id = db.Column(db.Integer, primary_key=True)
    
    # Información temporal
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fecha = db.Column(db.Date, nullable=False, default=datetime.now().date)
    
    # Contexto de usuario
    usuario = db.Column(db.String(100))
    usuario_id = db.Column(db.Integer)
    ip_origen = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    
    # Contexto de negocio
    nit_relacionado = db.Column(db.String(20))
    empresa_relacionada = db.Column(db.String(255))
    
    # Clasificación del log
    nivel = db.Column(db.String(20), nullable=False)  # SUCCESS, INFO, WARNING, ERROR, CRITICAL
    modulo = db.Column(db.String(50), nullable=False, default='DIAN_VS_ERP')
    operacion = db.Column(db.String(100))  # ENVIO_EMAIL, CREAR_CONFIG, etc.
    
    # Mensaje y detalles
    mensaje = db.Column(db.Text, nullable=False)
    detalles = db.Column(db.Text)  # JSON con información adicional
    
    # Performance
    duracion_ms = db.Column(db.Integer)  # Duración en milisegundos
    
    # Recursos afectados
    recurso_tipo = db.Column(db.String(50))  # CONFIGURACION, USUARIO, RELACION
    recurso_id = db.Column(db.Integer)
    
    # Stack trace para errores
    stack_trace = db.Column(db.Text)
    
    def to_dict(self):
        """Convierte el log a diccionario para JSON"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'usuario': self.usuario,
            'usuario_id': self.usuario_id,
            'ip_origen': self.ip_origen,
            'user_agent': self.user_agent,
            'nit_relacionado': self.nit_relacionado,
            'empresa_relacionada': self.empresa_relacionada,
            'nivel': self.nivel,
            'modulo': self.modulo,
            'operacion': self.operacion,
            'mensaje': self.mensaje,
            'detalles': self.detalles,
            'duracion_ms': self.duracion_ms,
            'recurso_tipo': self.recurso_tipo,
            'recurso_id': self.recurso_id,
            'stack_trace': self.stack_trace
        }
    
    def __repr__(self):
        return f'<LogSistema {self.id} | {self.nivel} | {self.operacion}>'


# ============================================================================
# MODELOS PARA TABLAS OPTIMIZADAS (Visor V2)
# ============================================================================

class Dian(db.Model):
    """Facturas electrónicas reportadas por DIAN"""
    __tablename__ = 'dian'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento = db.Column(db.String(50))
    cufe_cude = db.Column(db.String(255))
    folio = db.Column(db.String(50))
    prefijo = db.Column(db.String(20))
    divisa = db.Column(db.String(10))
    forma_pago = db.Column(db.String(50))
    medio_pago = db.Column(db.String(50))
    fecha_emision = db.Column(db.Date, index=True)
    fecha_recepcion = db.Column(db.Date)
    nit_emisor = db.Column(db.String(20), index=True)
    nombre_emisor = db.Column(db.String(255))
    nit_receptor = db.Column(db.String(20))
    nombre_receptor = db.Column(db.String(255))
    iva = db.Column(db.Numeric(15, 2), default=0)
    ica = db.Column(db.Numeric(15, 2), default=0)
    ic = db.Column(db.Numeric(15, 2), default=0)
    inc = db.Column(db.Numeric(15, 2), default=0)
    timbre = db.Column(db.Numeric(15, 2), default=0)
    inc_bolsas = db.Column(db.Numeric(15, 2), default=0)
    in_carbono = db.Column(db.Numeric(15, 2), default=0)
    in_combustibles = db.Column(db.Numeric(15, 2), default=0)
    ic_datos = db.Column(db.Numeric(15, 2), default=0)
    icl = db.Column(db.Numeric(15, 2), default=0)
    inpp = db.Column(db.Numeric(15, 2), default=0)
    ibua = db.Column(db.Numeric(15, 2), default=0)
    icui = db.Column(db.Numeric(15, 2), default=0)
    rete_iva = db.Column(db.Numeric(15, 2), default=0)
    rete_renta = db.Column(db.Numeric(15, 2), default=0)
    rete_ica = db.Column(db.Numeric(15, 2), default=0)
    total = db.Column(db.Numeric(15, 2), default=0)
    estado = db.Column(db.String(50))
    grupo = db.Column(db.String(100))
    clave = db.Column(db.String(100), unique=True)
    clave_acuse = db.Column(db.String(255), index=True)
    modulo = db.Column(db.String(50), default='DIAN')
    tipo_tercero = db.Column(db.String(50))
    n_dias = db.Column(db.Integer)
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)


class ErpComercial(db.Model):
    """Facturas del módulo comercial del ERP"""
    __tablename__ = 'erp_comercial'
    
    id = db.Column(db.Integer, primary_key=True)
    proveedor = db.Column(db.String(20), nullable=False, index=True)
    razon_social_proveedor = db.Column(db.String(255))
    fecha_docto_prov = db.Column(db.Date, index=True)
    docto_proveedor = db.Column(db.String(100))
    valor_bruto = db.Column(db.Numeric(15, 2), default=0)
    valor_imptos = db.Column(db.Numeric(15, 2), default=0)
    co = db.Column(db.String(50), index=True)
    usuario_creacion = db.Column(db.String(100))
    clase_docto = db.Column(db.String(50))
    nro_documento = db.Column(db.String(50))
    prefijo = db.Column(db.String(20), index=True)
    folio = db.Column(db.String(50), index=True)
    clave_erp_comercial = db.Column(db.String(100), unique=True)
    modulo = db.Column(db.String(50), default='Comercial')
    doc_causado_por = db.Column(db.String(200))
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)


class ErpFinanciero(db.Model):
    """Facturas del módulo financiero del ERP"""
    __tablename__ = 'erp_financiero'
    
    id = db.Column(db.Integer, primary_key=True)
    proveedor = db.Column(db.String(20), nullable=False, index=True)
    razon_social_proveedor = db.Column(db.String(255))
    fecha_proveedor = db.Column(db.Date, index=True)
    docto_proveedor = db.Column(db.String(100))
    valor_subtotal = db.Column(db.Numeric(15, 2), default=0)
    valor_impuestos = db.Column(db.Numeric(15, 2), default=0)
    co = db.Column(db.String(50), index=True)
    usuario_creacion = db.Column(db.String(100))
    clase_docto = db.Column(db.String(50))
    nro_documento = db.Column(db.String(50))
    prefijo = db.Column(db.String(20), index=True)
    folio = db.Column(db.String(50), index=True)
    clave_erp_financiero = db.Column(db.String(100), unique=True)
    modulo = db.Column(db.String(50), default='Financiero')
    doc_causado_por = db.Column(db.String(200))
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)


class Acuses(db.Model):
    """Acuses de recibo de facturas electrónicas"""
    __tablename__ = 'acuses'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, index=True)
    adquiriente = db.Column(db.String(255))
    factura = db.Column(db.String(100), index=True)
    emisor = db.Column(db.String(255))
    nit_emisor = db.Column(db.String(20), index=True)
    nit_pt = db.Column(db.String(20))
    estado_docto = db.Column(db.String(100))
    descripcion_reclamo = db.Column(db.Text)
    tipo_documento = db.Column(db.String(50))
    cufe = db.Column(db.String(255))
    valor = db.Column(db.Numeric(15, 2), default=0)
    acuse_recibido = db.Column(db.String(50))
    recibo_bien_servicio = db.Column(db.String(50))
    aceptacion_expresa = db.Column(db.String(50))
    reclamo = db.Column(db.String(50))
    aceptacion_tacita = db.Column(db.String(50))
    clave_acuse = db.Column(db.String(255), index=True)
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)


class TipoDocumentoDian(db.Model):
    """
    Catálogo de tipos de documentos DIAN
    Define qué tipos de documentos se procesan y muestran en el frontend
    """
    __tablename__ = 'tipos_documento_dian'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento = db.Column(db.String(255), nullable=False, unique=True, index=True)
    procesar_frontend = db.Column(db.Boolean, default=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TipoTerceroDianErp(db.Model):
    """
    Catálogo de clasificación de terceros según presencia en ERP
    Lógica de clasificación:
    - Proveedor: Si NIT está en erp_comercial
    - Acreedor: Si NIT está en erp_financiero
    - Proveedor y Acreedor: Si NIT está en ambos
    - No Registrado: Si NIT no está en ninguno (hereda de DIAN histórico)
    """
    __tablename__ = 'tipo_tercero_dian_erp'
    
    id = db.Column(db.Integer, primary_key=True)
    nit_emisor = db.Column(db.String(20), nullable=False, unique=True, index=True)
    razon_social = db.Column(db.String(255))
    tipo_tercero = db.Column(db.String(50), nullable=False, index=True)  # Proveedor, Acreedor, Proveedor y Acreedor, No Registrado
    en_erp_comercial = db.Column(db.Boolean, default=False, nullable=False)
    en_erp_financiero = db.Column(db.Boolean, default=False, nullable=False)
    heredado_dian = db.Column(db.Boolean, default=False)  # Si el tipo fue heredado de documentos DIAN anteriores
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

