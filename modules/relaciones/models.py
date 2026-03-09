# =============================================
# 🚀 models.py — Modelos SQLAlchemy para Relaciones
# =============================================
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, ForeignKey
from extensions import db  # Importar desde extensions, no desde app

# -------------------------------------------------
# 📊 MODELO: RELACION DE FACTURAS
# -------------------------------------------------
class RelacionFactura(db.Model):
    """
    Modelo para relaciones de facturas generadas
    Almacena el histórico de todas las relaciones creadas
    """
    __tablename__ = 'relaciones_facturas'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Datos de la relación
    numero_relacion = Column(String(20), nullable=False, index=True)  # REL-001, REL-002, etc.
    fecha_generacion = Column(Date, nullable=False, default=datetime.utcnow)
    para = Column(String(50), nullable=False)  # CONTABILIDAD, PAGOS, SUMINISTROS, OTRO
    usuario = Column(String(100), nullable=False)  # Usuario que generó la relación
    
    # Datos de la factura relacionada
    nit = Column(String(20), nullable=False, index=True)
    razon_social = Column(String(255))
    prefijo = Column(String(10), nullable=False)
    folio = Column(String(50), nullable=False)
    co = Column(String(10))  # Centro de operación
    empresa_id = Column(String(10), ForeignKey('empresas.sigla'), nullable=True, index=True)  # Empresa SC/LG
    valor_total = Column(Numeric(15, 2))
    fecha_factura = Column(Date)  # Fecha de radicación
    fecha_expedicion = Column(Date)  # Fecha de expedición de la factura
    
    # Estado de recepción digital
    recibida = Column(db.Boolean, default=False)  # Si fue recibida digitalmente
    usuario_check = Column(String(100))  # Usuario que la marcó como recibida
    fecha_check = Column(DateTime)  # Fecha/hora de recepción
    
    # Auditoría
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        # Helper para convertir fechas de forma segura
        def fecha_segura(fecha):
            if fecha is None:
                return None
            if isinstance(fecha, str):
                return fecha  # Ya es string
            if hasattr(fecha, 'isoformat'):
                return fecha.isoformat()
            return str(fecha)
        
        return {
            'id': self.id,
            'numero_relacion': self.numero_relacion,
            'fecha_generacion': fecha_segura(self.fecha_generacion),
            'para': self.para,
            'usuario': self.usuario,
            'nit': self.nit,
            'razon_social': self.razon_social,
            'prefijo': self.prefijo,
            'folio': self.folio,
            'co': self.co,
            'empresa_id': self.empresa_id if hasattr(self, 'empresa_id') else None,
            'valor_total': float(self.valor_total) if self.valor_total else 0,
            'fecha_factura': fecha_segura(self.fecha_factura),
            'fecha_expedicion': fecha_segura(self.fecha_expedicion),
            'fecha_registro': fecha_segura(self.fecha_registro),
            'recibida': self.recibida if hasattr(self, 'recibida') else False,
            'usuario_check': self.usuario_check if hasattr(self, 'usuario_check') else None,
            'fecha_check': fecha_segura(self.fecha_check) if hasattr(self, 'fecha_check') else None
        }
    
    def __repr__(self):
        return f"<RelacionFactura {self.numero_relacion}: {self.prefijo}-{self.folio}>"


# -------------------------------------------------
# 📊 MODELO: CONSECUTIVO (para numeración automática)
# -------------------------------------------------
class Consecutivo(db.Model):
    """
    Modelo para manejar consecutivos de diferentes tipos de documento
    """
    __tablename__ = 'consecutivos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(50), unique=True, nullable=False, index=True)
    tipo_documento = Column(String(50), nullable=False)  # Mapea a tipo_documento en BD
    prefijo = Column(String(10), nullable=False)
    ultimo_consecutivo = Column(Integer, default=0, nullable=False)  # Mapea a ultimo_consecutivo en BD
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'tipo_documento': self.tipo_documento,
            'prefijo': self.prefijo,
            'ultimo_consecutivo': self.ultimo_consecutivo,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    def __repr__(self):
        return f"<Consecutivo {self.tipo}: {self.prefijo}-{self.ultimo_consecutivo}>"


# -------------------------------------------------
# 📊 MODELO: RECEPCIÓN DIGITAL DE RELACIONES
# -------------------------------------------------
class RecepcionDigital(db.Model):
    """
    Modelo para registrar recepciones digitales de relaciones
    Auditoría completa de quién recibió cada relación
    """
    __tablename__ = 'recepciones_digitales'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación recibida
    numero_relacion = Column(String(20), nullable=False, index=True)  # REL-001, REL-002, etc.
    
    # Datos del receptor
    usuario_receptor = Column(String(100), nullable=False)  # Usuario que recibió
    nombre_receptor = Column(String(255))  # Nombre completo del receptor
    
    # Datos de la recepción
    fecha_recepcion = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_recepcion = Column(String(50))  # IP desde donde se recibió
    user_agent = Column(Text)  # Navegador/dispositivo usado
    
    # Estado de recepción
    facturas_recibidas = Column(Integer, default=0)  # Cantidad de facturas con check
    facturas_totales = Column(Integer, default=0)  # Total de facturas en la relación
    completa = Column(db.Boolean, default=False)  # Si se recibieron todas las facturas
    
    # Firma digital (hash de datos para validación)
    firma_digital = Column(String(255))  # Hash SHA256 de los datos de recepción
    
    # Auditoría
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'numero_relacion': self.numero_relacion,
            'usuario_receptor': self.usuario_receptor,
            'nombre_receptor': self.nombre_receptor,
            'fecha_recepcion': self.fecha_recepcion.isoformat() if self.fecha_recepcion else None,
            'ip_recepcion': self.ip_recepcion,
            'facturas_recibidas': self.facturas_recibidas,
            'facturas_totales': self.facturas_totales,
            'completa': self.completa,
            'firma_digital': self.firma_digital,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
    
    def __repr__(self):
        return f"<RecepcionDigital {self.numero_relacion} por {self.usuario_receptor}>"


# -------------------------------------------------
# 📊 MODELO: FACTURAS RECIBIDAS DIGITALMENTE
# -------------------------------------------------
class FacturaRecibidaDigital(db.Model):
    """
    Modelo para registrar cada factura recibida digitalmente
    Detalle de qué facturas específicas fueron checkeadas
    """
    __tablename__ = 'facturas_recibidas_digitales'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con recepción digital
    recepcion_id = Column(Integer, ForeignKey('recepciones_digitales.id'), nullable=False, index=True)
    numero_relacion = Column(String(20), nullable=False, index=True)
    
    # Datos de la factura
    nit = Column(String(20), nullable=False, index=True)
    razon_social = Column(String(255))
    prefijo = Column(String(10), nullable=False)
    folio = Column(String(50), nullable=False)
    co = Column(String(10))  # Centro de operación
    valor_total = Column(Numeric(15, 2))
    fecha_factura = Column(Date)
    
    # Datos de recepción de esta factura específica
    recibida = Column(db.Boolean, default=False)  # Si tiene check
    fecha_check = Column(DateTime)  # Cuándo se hizo el check
    usuario_check = Column(String(100))  # Quién hizo el check
    observaciones = Column(Text)  # Observaciones al recibir (ej: "documento dañado")
    
    # Auditoría
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'recepcion_id': self.recepcion_id,
            'numero_relacion': self.numero_relacion,
            'nit': self.nit,
            'razon_social': self.razon_social,
            'prefijo': self.prefijo,
            'folio': self.folio,
            'co': self.co,
            'valor_total': float(self.valor_total) if self.valor_total else 0,
            'fecha_factura': self.fecha_factura.isoformat() if self.fecha_factura else None,
            'recibida': self.recibida,
            'fecha_check': self.fecha_check.isoformat() if self.fecha_check else None,
            'usuario_check': self.usuario_check,
            'observaciones': self.observaciones,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
    
    def __repr__(self):
        return f"<FacturaRecibidaDigital {self.prefijo}-{self.folio} ({self.numero_relacion})>"


# -------------------------------------------------
# 🔐 MODELO: TOKEN DE FIRMA DIGITAL
# -------------------------------------------------
class TokenFirmaDigital(db.Model):
    """
    Modelo para tokens de firma digital de recepciones
    Token de 6 dígitos enviado por correo para validar recepción
    """
    __tablename__ = 'tokens_firma_digital'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Token
    token = Column(String(6), nullable=False, index=True)  # Token de 6 dígitos
    
    # Usuario y relación asociados
    usuario = Column(String(100), nullable=False, index=True)
    numero_relacion = Column(String(20), nullable=False, index=True)
    correo_destino = Column(String(255), nullable=False)
    
    # Validez del token
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime, nullable=False)  # 10 minutos después
    usado = Column(db.Boolean, default=False)
    intentos_validacion = Column(Integer, default=0)
    fecha_uso = Column(DateTime)
    
    # Auditoría
    ip_creacion = Column(String(50))
    ip_uso = Column(String(50))
    
    def esta_vigente(self):
        """Verifica si el token aún está vigente (usa hora de Colombia)"""
        from utils_fecha import obtener_fecha_naive_colombia
        fecha_actual = obtener_fecha_naive_colombia()
        return (
            not self.usado and
            fecha_actual < self.fecha_expiracion and
            self.intentos_validacion < 3
        )
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'token': self.token,
            'usuario': self.usuario,
            'numero_relacion': self.numero_relacion,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_expiracion': self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            'usado': self.usado,
            'vigente': self.esta_vigente()
        }
    
    def __repr__(self):
        return f"<TokenFirmaDigital {self.token} para {self.usuario} - {self.numero_relacion}>"

