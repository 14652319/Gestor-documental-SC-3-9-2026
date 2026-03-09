# =============================================
# 🚀 models.py — Modelos SQLAlchemy para Recibir Facturas
# =============================================
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, Computed
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from extensions import db  # Importar desde extensions, no desde app

# -------------------------------------------------
# 🔄 HELPER: OBTENER MODELO TERCERO (sin circular import)
# -------------------------------------------------
def get_tercero_by_nit(nit):
    """
    Consulta un tercero por NIT sin importar el modelo directamente
    Usa query SQL directa para evitar circular imports
    """
    from sqlalchemy import text
    query = text("SELECT id, nit, razon_social, fecha_actualizacion FROM terceros WHERE nit = :nit")
    result = db.session.execute(query, {"nit": nit}).fetchone()
    
    if result:
        return {
            "id": result[0],
            "nit": result[1],
            "razon_social": result[2],
            "fecha_actualizacion": result[3]
        }
    return None

# -------------------------------------------------
# � MODELO: CENTRO DE OPERACIÓN
# -------------------------------------------------
# -------------------------------------------------
# 🏢 IMPORTAR MODELOS (desde configuracion)
# -------------------------------------------------
# ✅ CORRECCIÓN (Oct 22, 2025): No redefinir CentroOperacion aquí
# Se importa desde modules.configuracion.models para evitar tabla duplicada
from modules.configuracion.models import CentroOperacion

# NOTA: El modelo CentroOperacion ya está definido en modules/configuracion/models.py
# Este módulo solo lo importa para usar como foreign key reference
# NOTA: Empresa se referencia con lazy loading para evitar circular imports
# -------------------------------------------------
# �📊 MODELO: FACTURA TEMPORAL
# -------------------------------------------------
class FacturaTemporal(db.Model):
    """
    Modelo para facturas temporales (antes de "Guardar Facturas")
    Reemplaza temp_generico.csv y temp_{usuario}.csv
    """
    __tablename__ = 'facturas_temporales'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información del emisor (tercero)
    nit = Column(String(20), nullable=False, index=True)
    razon_social = Column(String(255), nullable=False)
    
    # Clave única de factura (NIT + Prefijo + Folio)
    prefijo = Column(String(10), nullable=False)
    folio = Column(String(20), nullable=False)
    
    # Empresa (sigla de la empresa - NUEVO)
    empresa_id = Column(String(10), ForeignKey('empresas.sigla'), nullable=True, index=True)
    empresa = relationship('Empresa', foreign_keys=[empresa_id])
    
    # Centro de operación
    centro_operacion_id = Column(Integer, ForeignKey('centros_operacion.id'), nullable=False)
    centro_operacion_rel = relationship('CentroOperacion', backref='facturas_temporales')
    
    # Fechas
    fecha_expedicion = Column(Date, nullable=False)
    fecha_radicacion = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date)
    
    # Valores monetarios
    valor_bruto = Column(Numeric(15, 2), nullable=False)
    descuento = Column(Numeric(15, 2), default=0)
    iva = Column(Numeric(15, 2), default=0)
    retencion_fuente = Column(Numeric(15, 2), default=0)
    rete_iva = Column(Numeric(15, 2), default=0)
    rete_ica = Column(Numeric(15, 2), default=0)
    
    # Usuarios involucrados (nombres reales de BD)
    usuario_solicita = Column(String(200))
    comprador = Column(String(200))  # ⚠️ REAL: "comprador" (no "usuario_compra")
    quien_recibe = Column(String(200))  # ⚠️ REAL: "quien_recibe" (no "usuario_recibe")
    
    # Forma de pago y plazo
    forma_pago = Column(String(50), default='CREDITO')
    plazo = Column(Integer, default=30)
    
    # Campos adicionales
    centro_operacion = Column(String(200))  # Nombre del centro (duplicado del ID)
    valor_neto = Column(Numeric(15, 2))  # Valor calculado (se guarda también)
    observaciones = Column(Text)
    
    # Usuario que registró temporalmente
    usuario_nombre = Column(String(200))  # Nombre del usuario (duplicado)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    usuario = relationship('Usuario', backref='facturas_temporales')
    
    # Timestamps (nombres reales de BD)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint de clave única (comentado porque tabla ya existe en BD)
    # __table_args__ = (
    #     UniqueConstraint('nit', 'prefijo', 'folio', name='uq_temporal_nit_prefijo_folio'),
    #     CheckConstraint('valor_bruto > 0', name='ck_temporal_valor_bruto_positivo'),
    #     CheckConstraint('plazo >= 0', name='ck_temporal_plazo_positivo'),
    # )
    
    # -------------------------------------------------
    # MÉTODOS
    # -------------------------------------------------
    
    @hybrid_property
    def numero_factura(self):
        """Número de factura completo: prefijo + folio"""
        return f"{self.prefijo}{self.folio}"
    
    @hybrid_property
    def folio_normalizado(self):
        """Folio sin ceros a la izquierda (para comparaciones)"""
        return self.folio.lstrip('0') if self.folio else ''
    
    # NOTA: valor_neto es una COLUMNA (línea 138), no una propiedad calculada
    # El cálculo se hace en routes.py antes de guardar
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        # ✅ Obtener código del centro de operación si existe
        centro_codigo = 'N/A'
        if self.centro_operacion_id:
            co = CentroOperacion.query.get(self.centro_operacion_id)
            if co:
                centro_codigo = co.codigo
        
        return {
            'id': self.id,
            'nit': self.nit,
            'razon_social': self.razon_social,
            'prefijo': self.prefijo,
            'folio': self.folio,
            'numero_factura': self.numero_factura,
            'empresa_id': self.empresa_id,  # ✅ CAMPO EMPRESA AGREGADO
            'centro_operacion_id': self.centro_operacion_id,
            'centro_operacion': self.centro_operacion,
            'centro_operacion_codigo': centro_codigo,  # ✅ NUEVO: Código del CO
            'fecha_expedicion': self.fecha_expedicion.isoformat() if self.fecha_expedicion else None,
            'fecha_radicacion': self.fecha_radicacion.isoformat() if self.fecha_radicacion else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'valor_bruto': float(self.valor_bruto),
            'descuento': float(self.descuento or 0),
            'iva': float(self.iva or 0),
            'retencion_fuente': float(self.retencion_fuente or 0),
            'rete_iva': float(self.rete_iva or 0),
            'rete_ica': float(self.rete_ica or 0),
            'valor_neto': float(self.valor_neto) if self.valor_neto else self.calcular_valor_neto(),
            'usuario_solicita': self.usuario_solicita,
            'comprador': self.comprador,  # ⚠️ Nombre real de BD
            'quien_recibe': self.quien_recibe,  # ⚠️ Nombre real de BD
            'forma_pago': self.forma_pago,
            'plazo': self.plazo,
            'observaciones': self.observaciones or '',  # ✅ NUEVO: Observaciones
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
    
    def calcular_valor_neto(self):
        """Calcula valor neto si no está guardado"""
        valor = float(self.valor_bruto or 0)
        valor += float(self.iva or 0)
        valor -= float(self.descuento or 0)
        valor -= float(self.retencion_fuente or 0)
        valor -= float(self.rete_iva or 0)
        valor -= float(self.rete_ica or 0)
        return round(valor, 2)
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        # Asegurar que valor_neto esté presente: usar el valor enviado o calcularlo a partir de los componentes
        valor_neto = data.get('valor_neto')
        if valor_neto is None:
            try:
                vb = float(data.get('valor_bruto', 0) or 0)
                iva = float(data.get('iva', 0) or 0)
                descuento = float(data.get('descuento', 0) or 0)
                rf = float(data.get('retencion_fuente', 0) or 0)
                riva = float(data.get('rete_iva', 0) or 0)
                rica = float(data.get('rete_ica', 0) or 0)
                valor_neto = round(vb + iva - descuento - rf - riva - rica, 2)
            except Exception:
                # Si algo falla, dejar None y dejar que la validación de BD o rutas lo capture
                valor_neto = None

        return cls(
            nit=data.get('nit'),
            razon_social=data.get('razon_social'),
            prefijo=data.get('prefijo', ''),
            folio=data.get('folio'),
            empresa_id=data.get('empresa_id'),  # ✅ CAMPO EMPRESA AGREGADO
            centro_operacion_id=data.get('centro_operacion_id'),
            fecha_expedicion=datetime.strptime(data.get('fecha_expedicion'), '%Y-%m-%d').date() if data.get('fecha_expedicion') else None,
            fecha_radicacion=datetime.strptime(data.get('fecha_radicacion'), '%Y-%m-%d').date() if data.get('fecha_radicacion') else None,
            fecha_vencimiento=datetime.strptime(data.get('fecha_vencimiento'), '%Y-%m-%d').date() if data.get('fecha_vencimiento') else None,
            valor_bruto=data.get('valor_bruto', 0),
            descuento=data.get('descuento', 0),
            iva=data.get('iva', 0),
            retencion_fuente=data.get('retencion_fuente', 0),
            rete_iva=data.get('rete_iva', 0),
            rete_ica=data.get('rete_ica', 0),
            usuario_solicita=data.get('usuario_solicita'),
            comprador=data.get('comprador') or data.get('usuario_compra'),  # Compatibilidad
            quien_recibe=data.get('quien_recibe') or data.get('usuario_recibe'),  # Compatibilidad
            forma_pago=data.get('forma_pago', 'CREDITO'),
            plazo=data.get('plazo', 30),
            valor_neto=valor_neto,
            centro_operacion=data.get('centro_operacion'),
            observaciones=data.get('observaciones'),
            usuario_nombre=data.get('usuario_nombre') or 'USUARIO',  # Fallback si no viene
            usuario_id=data.get('usuario_id'),
        )
    
    @classmethod
    def validar_clave_unica(cls, nit, prefijo, folio, excluir_id=None):
        """
        Valida si la clave (NIT + Prefijo + Folio) ya existe en temporales
        
        Args:
            nit: NIT del emisor
            prefijo: Prefijo de la factura
            folio: Folio (se normaliza sin ceros)
            excluir_id: ID de factura a excluir (para edición)
        
        Returns:
            tuple: (existe: bool, factura: FacturaTemporal o None)
        """
        folio_normalizado = folio.lstrip('0') if folio else ''
        
        query = cls.query.filter(
            cls.nit == nit,
            cls.prefijo == prefijo,
        )
        
        # Buscar folio normalizado
        facturas = query.all()
        for factura in facturas:
            if factura.folio_normalizado == folio_normalizado:
                if excluir_id and factura.id == excluir_id:
                    continue  # Excluir la factura actual en edición
                return (True, factura)
        
        return (False, None)
    
    def __repr__(self):
        return f"<FacturaTemporal {self.numero_factura} - {self.razon_social} - ${self.valor_neto}>"


# -------------------------------------------------
# 📊 MODELO: FACTURA RECIBIDA
# -------------------------------------------------
class FacturaRecibida(db.Model):
    """
    Modelo para facturas recibidas (después de "Guardar Facturas")
    Reemplaza facturas_recibidas.csv
    """
    __tablename__ = 'facturas_recibidas'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información del emisor (tercero)
    nit = Column(String(20), nullable=False, index=True)
    razon_social = Column(String(255), nullable=False)
    
    # Clave única de factura (NIT + Prefijo + Folio)
    prefijo = Column(String(10), nullable=False)
    folio = Column(String(20), nullable=False)
    
    # Empresa (sigla de la empresa - NUEVO)
    empresa_id = Column(String(10), ForeignKey('empresas.sigla'), nullable=True, index=True)
    empresa = relationship('Empresa', foreign_keys=[empresa_id])
    
    # Centro de operación
    centro_operacion_id = Column(Integer, nullable=False)  # ForeignKey comentado temporalmente
    # centro_operacion = relationship('CentroOperacion', backref='facturas_recibidas')  # ⚠️ COMENTADO: Modelo no existe aún
    
    # Fechas
    fecha_expedicion = Column(Date, nullable=False, index=True)
    fecha_radicacion = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, index=True)
    
    # Valores monetarios
    valor_bruto = Column(Numeric(15, 2), nullable=False)
    descuento = Column(Numeric(15, 2), default=0)
    iva = Column(Numeric(15, 2), default=0)
    retencion_fuente = Column(Numeric(15, 2), default=0)
    rete_iva = Column(Numeric(15, 2), default=0)
    rete_ica = Column(Numeric(15, 2), default=0)
    
    # Usuarios involucrados (nombres reales de BD)
    usuario_solicita = Column(String(200))
    comprador = Column(String(200))  # ⚠️ REAL: "comprador" (no "usuario_compra")
    quien_recibe = Column(String(200))  # ⚠️ REAL: "quien_recibe" (no "usuario_recibe")
    
    # Forma de pago y plazo
    forma_pago = Column(String(50), default='CREDITO')
    plazo = Column(Integer, default=30)
    
    # Campos adicionales (estructura real de BD)
    numero_factura = Column(String(100), Computed("prefijo || folio", persisted=True))  # ✅ GENERATED COLUMN
    centro_operacion = Column(String(200))  # Nombre del centro (duplicado del ID)
    valor_neto = Column(Numeric(15, 2))  # Valor calculado (se guarda también)
    observaciones = Column(Text)
    
    # Estado de la factura
    estado = Column(String(30), default='RECIBIDA', nullable=False)
    
    # Usuario que guardó definitivamente
    usuario_nombre = Column(String(200))  # Nombre del usuario (duplicado)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    usuario = relationship('Usuario', backref='facturas_recibidas')
    
    # Timestamps (nombres reales de BD)
    fecha_guardado = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint de clave única (comentado porque tabla ya existe en BD)
    # __table_args__ = (
    #     UniqueConstraint('nit', 'prefijo', 'folio', name='uq_recibida_nit_prefijo_folio'),
    #     CheckConstraint('valor_bruto > 0', name='ck_recibida_valor_bruto_positivo'),
    #     CheckConstraint('plazo >= 0', name='ck_recibida_plazo_positivo'),
    #     CheckConstraint("estado IN ('RECIBIDA', 'EN_PROCESO', 'PAGADA', 'ANULADA')", name='ck_recibida_estado_valido'),
    # )
    
    # -------------------------------------------------
    # MÉTODOS
    # -------------------------------------------------
    
    @hybrid_property
    def numero_factura_calculado(self):
        """Número de factura completo: prefijo + folio (propiedad calculada)"""
        return f"{self.prefijo}{self.folio}"
    
    @hybrid_property
    def folio_normalizado(self):
        """Folio sin ceros a la izquierda (para comparaciones)"""
        return self.folio.lstrip('0') if self.folio else ''
    
    # ✅ valor_neto ya NO es @hybrid_property
    # Es un Column(Numeric) que debe calcularse explícitamente ANTES de crear el objeto
    # Ver: test_flujo_guardar_facturas.py líneas 155-162 para ejemplo de cálculo
    
    def calcular_dias_vencimiento(self):
        """
        Calcula días hasta/desde vencimiento
        Positivo = futuro, Negativo = vencida
        """
        if not self.fecha_vencimiento:
            return None
        
        hoy = datetime.now().date()
        delta = (self.fecha_vencimiento - hoy).days
        return delta
    
    @hybrid_property
    def esta_vencida(self):
        """Retorna True si la factura está vencida"""
        dias = self.calcular_dias_vencimiento()
        return dias is not None and dias < 0
    
    @hybrid_property
    def proxima_a_vencer(self):
        """Retorna True si la factura vence en menos de 7 días"""
        dias = self.calcular_dias_vencimiento()
        return dias is not None and 0 <= dias <= 7
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'nit': self.nit,
            'razon_social': self.razon_social,
            'prefijo': self.prefijo,
            'folio': self.folio,
            'numero_factura': self.numero_factura or self.numero_factura_calculado,
            'centro_operacion_id': self.centro_operacion_id,
            'centro_operacion': self.centro_operacion,
            'fecha_expedicion': self.fecha_expedicion.isoformat() if self.fecha_expedicion else None,
            'fecha_radicacion': self.fecha_radicacion.isoformat() if self.fecha_radicacion else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'valor_bruto': float(self.valor_bruto),
            'descuento': float(self.descuento or 0),
            'iva': float(self.iva or 0),
            'retencion_fuente': float(self.retencion_fuente or 0),
            'rete_iva': float(self.rete_iva or 0),
            'rete_ica': float(self.rete_ica or 0),
            'valor_neto': float(self.valor_neto) if self.valor_neto else self.calcular_valor_neto_metodo(),
            'usuario_solicita': self.usuario_solicita,
            'comprador': self.comprador,  # ⚠️ Nombre real de BD
            'quien_recibe': self.quien_recibe,  # ⚠️ Nombre real de BD
            'forma_pago': self.forma_pago,
            'plazo': self.plazo,
            'estado': self.estado,
            'dias_vencimiento': self.calcular_dias_vencimiento(),
            'esta_vencida': self.esta_vencida,
            'proxima_a_vencer': self.proxima_a_vencer,
            'fecha_guardado': self.fecha_guardado.isoformat() if self.fecha_guardado else None,
        }
    
    def calcular_valor_neto_metodo(self):
        """Calcula valor neto si no está guardado"""
        valor = float(self.valor_bruto or 0)
        valor += float(self.iva or 0)
        valor -= float(self.descuento or 0)
        valor -= float(self.retencion_fuente or 0)
        valor -= float(self.rete_iva or 0)
        valor -= float(self.rete_ica or 0)
        return round(valor, 2)
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        return cls(
            nit=data.get('nit'),
            razon_social=data.get('razon_social'),
            prefijo=data.get('prefijo', ''),
            folio=data.get('folio'),
            empresa_id=data.get('empresa_id'),  # ✅ CAMPO EMPRESA AGREGADO
            centro_operacion_id=data.get('centro_operacion_id'),
            fecha_expedicion=datetime.strptime(data.get('fecha_expedicion'), '%Y-%m-%d').date() if data.get('fecha_expedicion') else None,
            fecha_radicacion=datetime.strptime(data.get('fecha_radicacion'), '%Y-%m-%d').date() if data.get('fecha_radicacion') else None,
            fecha_vencimiento=datetime.strptime(data.get('fecha_vencimiento'), '%Y-%m-%d').date() if data.get('fecha_vencimiento') else None,
            valor_bruto=data.get('valor_bruto', 0),
            descuento=data.get('descuento', 0),
            iva=data.get('iva', 0),
            retencion_fuente=data.get('retencion_fuente', 0),
            rete_iva=data.get('rete_iva', 0),
            rete_ica=data.get('rete_ica', 0),
            usuario_solicita=data.get('usuario_solicita'),
            comprador=data.get('comprador') or data.get('usuario_compra'),  # Compatibilidad
            quien_recibe=data.get('quien_recibe') or data.get('usuario_recibe'),  # Compatibilidad
            forma_pago=data.get('forma_pago', 'CREDITO'),
            plazo=data.get('plazo', 30),
            estado=data.get('estado', 'RECIBIDA'),
            usuario_id=data.get('usuario_id'),
        )
    
    @classmethod
    def validar_clave_unica(cls, nit, prefijo, folio, excluir_id=None):
        """
        Valida si la clave (NIT + Prefijo + Folio) ya existe en recibidas
        
        Args:
            nit: NIT del emisor
            prefijo: Prefijo de la factura
            folio: Folio (se normaliza sin ceros)
            excluir_id: ID de factura a excluir (para edición)
        
        Returns:
            tuple: (existe: bool, factura: FacturaRecibida o None)
        """
        folio_normalizado = folio.lstrip('0') if folio else ''
        
        query = cls.query.filter(
            cls.nit == nit,
            cls.prefijo == prefijo,
        )
        
        # Buscar folio normalizado
        facturas = query.all()
        for factura in facturas:
            if factura.folio_normalizado == folio_normalizado:
                if excluir_id and factura.id == excluir_id:
                    continue  # Excluir la factura actual en edición
                return (True, factura)
        
        return (False, None)
    
    def __repr__(self):
        return f"<FacturaRecibida {self.numero_factura} - {self.razon_social} - ${self.valor_neto} - {self.estado}>"


# -------------------------------------------------
# 📊 MODELO: OBSERVACIONES FACTURA RECIBIDA
# -------------------------------------------------
class ObservacionFactura(db.Model):
    """
    Modelo para observaciones de facturas recibidas
    Permite múltiples observaciones por factura
    """
    __tablename__ = 'observaciones_factura'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con factura recibida
    factura_id = Column(Integer, ForeignKey('facturas_recibidas.id', ondelete='CASCADE'), nullable=False, index=True)
    factura = relationship('FacturaRecibida', backref='observaciones_relacionadas')  # ⚠️ Renombrado para evitar conflicto con columna 'observaciones'
    
    # Contenido de la observación
    observacion = Column(Text, nullable=False)
    
    # Usuario que creó la observación
    usuario_nombre = Column(String(200), nullable=False)  # ✅ Campo requerido por PostgreSQL
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    usuario = relationship('Usuario', backref='observaciones_facturas')
    
    # Timestamp
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraint de longitud máxima (5000 caracteres)
    __table_args__ = (
        CheckConstraint('LENGTH(observacion) <= 5000', name='ck_observacion_longitud_maxima'),
    )
    
    # -------------------------------------------------
    # MÉTODOS
    # -------------------------------------------------
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'factura_id': self.factura_id,
            'observacion': self.observacion,
            'usuario_nombre': self.usuario.usuario if self.usuario else 'Desconocido',
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        return cls(
            factura_id=data.get('factura_id'),
            observacion=data.get('observacion'),
            usuario_id=data.get('usuario_id'),
        )
    
    def __repr__(self):
        return f"<ObservacionFactura #{self.id} - Factura #{self.factura_id} - {self.fecha_creacion}>"


# -------------------------------------------------
# 📊 MODELO: OBSERVACIONES FACTURA TEMPORAL
# -------------------------------------------------
class ObservacionFacturaTemporal(db.Model):
    """
    Modelo para observaciones de facturas temporales
    Permite múltiples observaciones por factura temporal
    """
    __tablename__ = 'observaciones_factura_temporal'
    
    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relación con factura temporal
    factura_temporal_id = Column(Integer, ForeignKey('facturas_temporales.id', ondelete='CASCADE'), nullable=False, index=True)
    factura_temporal = relationship('FacturaTemporal', backref='observaciones_relacionadas')
    
    # Contenido de la observación
    observacion = Column(Text, nullable=False)
    
    # Usuario que creó la observación
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    usuario = relationship('Usuario', backref='observaciones_facturas_temporales')
    
    # Timestamp
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraint de longitud máxima (5000 caracteres)
    __table_args__ = (
        CheckConstraint('LENGTH(observacion) <= 5000', name='ck_observacion_temporal_longitud_maxima'),
    )
    
    # -------------------------------------------------
    # MÉTODOS
    # -------------------------------------------------
    
    def to_dict(self):
        """Convierte el modelo a diccionario para JSON"""
        return {
            'id': self.id,
            'factura_temporal_id': self.factura_temporal_id,
            'observacion': self.observacion,
            'usuario_nombre': self.usuario.usuario if self.usuario else 'Desconocido',
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea una instancia desde un diccionario"""
        return cls(
            factura_temporal_id=data.get('factura_temporal_id'),
            observacion=data.get('observacion'),
            usuario_id=data.get('usuario_id'),
        )
    
    def __repr__(self):
        return f"<ObservacionFacturaTemporal #{self.id} - Factura Temporal #{self.factura_temporal_id} - {self.fecha_creacion}>"
