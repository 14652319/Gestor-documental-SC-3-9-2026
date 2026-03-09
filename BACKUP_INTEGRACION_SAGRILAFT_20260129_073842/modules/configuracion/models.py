"""
Modelos SQLAlchemy para el módulo de Configuración
Gestiona: tipos_documento y centros_operacion
"""
from datetime import datetime
from extensions import db

class TipoDocumento(db.Model):
    """Catálogo de tipos de documentos contables (NOC, NCM, NTN, LEG)"""
    __tablename__ = 'tipos_documento'
    
    id = db.Column(db.Integer, primary_key=True)
    siglas = db.Column(db.String(10), unique=True, nullable=False)  # NOC, NCM
    nombre = db.Column(db.String(100), nullable=False)              # Nota de Contabilidad
    modulo = db.Column(db.String(50), nullable=False)               # Contabilidad, Tesorería
    estado = db.Column(db.String(20), nullable=False, default='activo')  # activo/inactivo
    created_by = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # ⚠️ Relación deshabilitada: causaba conflicto de backref con DocumentoContable.tipo_documento
    # documentos = db.relationship('DocumentoContable', backref='tipo_documento', lazy=True)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'siglas': self.siglas,
            'nombre': self.nombre,
            'modulo': self.modulo,
            'estado': self.estado,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class CentroOperacion(db.Model):
    """Catálogo de centros de operación con ubicación y tipo de propiedad"""
    __tablename__ = 'centros_operacion'
    __table_args__ = {'extend_existing': True}  # Permitir redefinición si ya existe
    
    # ✅ CAMPOS QUE SÍ EXISTEN EN LA TABLA REAL (verificado 2025)
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)  # 001, 002
    nombre = db.Column(db.String(100), nullable=False)              # Centro Principal
    ciudad = db.Column(db.String(50))
    direccion = db.Column(db.String(255))
    estado = db.Column(db.String(20))  # activo/inactivo
    tipo_propiedad = db.Column(db.String(20))  # propio/arrendado
    fecha_registro = db.Column(db.DateTime)  # ✅ Campo real de la tabla
    
    # ✅ CAMPOS ADICIONALES (ampliación para cubrir columnas del Excel)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(30))
    barrio = db.Column(db.String(100))
    email = db.Column(db.String(120))
    cod_depto = db.Column(db.String(10))
    cod_pais = db.Column(db.String(10))
    cod_ciudad = db.Column(db.String(10))

    # Flags operativos
    almacen = db.Column(db.Boolean, default=False)
    bodega = db.Column(db.Boolean, default=False)
    c_comercial = db.Column(db.Boolean, default=False)
    otros = db.Column(db.Boolean, default=False)
    mayorista = db.Column(db.Boolean, default=False)
    asaderos = db.Column(db.Boolean, default=False)
    panaderias = db.Column(db.Boolean, default=False)
    domicilios = db.Column(db.Boolean, default=False)

    # Auditoría básica
    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relación con documentos (solo si DocumentoContable está definido)
    # documentos = db.relationship('DocumentoContable', backref='centro_operacion', lazy=True)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'ciudad': self.ciudad,
            'direccion': self.direccion,
            'estado': self.estado,
            'tipo_propiedad': self.tipo_propiedad,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_registro else None,
            'contacto': self.contacto,
            'telefono': self.telefono,
            'barrio': self.barrio,
            'email': self.email,
            'cod_depto': self.cod_depto,
            'cod_pais': self.cod_pais,
            'cod_ciudad': self.cod_ciudad,
            'almacen': bool(self.almacen) if self.almacen is not None else False,
            'bodega': bool(self.bodega) if self.bodega is not None else False,
            'c_comercial': bool(self.c_comercial) if self.c_comercial is not None else False,
            'otros': bool(self.otros) if self.otros is not None else False,
            'mayorista': bool(self.mayorista) if self.mayorista is not None else False,
            'asaderos': bool(self.asaderos) if self.asaderos is not None else False,
            'panaderias': bool(self.panaderias) if self.panaderias is not None else False,
            'domicilios': bool(self.domicilios) if self.domicilios is not None else False,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_by': self.updated_by,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

class Empresa(db.Model):
    """Catálogo de empresas del grupo empresarial"""
    __tablename__ = 'empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    sigla = db.Column(db.String(10), unique=True, nullable=False)   # SC, LG
    nombre = db.Column(db.String(255), nullable=False)              # SUPERTIENDAS CAÑAVERAL SAS
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'sigla': self.sigla,
            'nombre': self.nombre,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_actualizacion else None
        }

class FormaPago(db.Model):
    """Catálogo de formas de pago"""
    __tablename__ = 'formas_pago'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)  # ESTANDAR, TARJETA_CREDITO
    nombre = db.Column(db.String(100), nullable=False)              # Estándar, Tarjeta de Crédito
    estado = db.Column(db.String(20), nullable=False, default='activo')
    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'estado': self.estado,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class TipoServicio(db.Model):
    """Catálogo de tipos de servicio"""
    __tablename__ = 'tipos_servicio'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)  # servicio, compra, ambos
    nombre = db.Column(db.String(100), nullable=False)              # Servicio, Compra, Ambos
    estado = db.Column(db.String(20), nullable=False, default='activo')
    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'estado': self.estado,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class Departamento(db.Model):
    """Catálogo de departamentos de la empresa"""
    __tablename__ = 'departamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)  # FINANCIERO, TECNOLOGIA
    nombre = db.Column(db.String(100), nullable=False)              # Financiero, Tecnología
    estado = db.Column(db.String(20), nullable=False, default='activo')
    created_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'estado': self.estado,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
