"""
Modelos de Base de Datos para Monitoreo
"""

from extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB


class AlertaSeguridad(db.Model):
    """
    Tabla para registrar alertas de seguridad enviadas
    """
    __tablename__ = "alertas_seguridad"
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_alerta = db.Column(db.String(50), nullable=False)  # IP_BLOQUEADA, ATAQUE_BRUTE_FORCE, etc.
    ip = db.Column(db.String(50))
    usuario = db.Column(db.String(100))
    nit = db.Column(db.String(20))
    detalles = db.Column(db.Text)
    enviada_telegram = db.Column(db.Boolean, default=False)
    fecha_alerta = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resuelta = db.Column(db.Boolean, default=False)
    fecha_resolucion = db.Column(db.DateTime)
    notas_resolucion = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo_alerta': self.tipo_alerta,
            'ip': self.ip,
            'usuario': self.usuario,
            'nit': self.nit,
            'detalles': self.detalles,
            'enviada_telegram': self.enviada_telegram,
            'fecha_alerta': self.fecha_alerta.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_alerta else None,
            'resuelta': self.resuelta,
            'fecha_resolucion': self.fecha_resolucion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_resolucion else None,
            'notas_resolucion': self.notas_resolucion
        }


class LogAccion(db.Model):
    """
    Tabla para registrar acciones administrativas realizadas desde el panel de monitoreo
    """
    __tablename__ = "logs_acciones_admin"
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_admin = db.Column(db.String(100), nullable=False)
    accion = db.Column(db.String(100), nullable=False)  # BLOQUEAR_IP, DESBLOQUEAR_IP, ACTIVAR_USUARIO, etc.
    objetivo = db.Column(db.String(255))  # IP o usuario afectado
    detalles = db.Column(db.Text)
    resultado = db.Column(db.String(20))  # EXITOSO, ERROR
    fecha_accion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_admin = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_admin': self.usuario_admin,
            'accion': self.accion,
            'objetivo': self.objetivo,
            'detalles': self.detalles,
            'resultado': self.resultado,
            'fecha_accion': self.fecha_accion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_accion else None,
            'ip_admin': self.ip_admin
        }


class SesionActiva(db.Model):
    """
    Tabla para trackear sesiones de usuarios en tiempo real
    """
    __tablename__ = "sesiones_activas"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    usuario_nombre = db.Column(db.String(100), nullable=False)
    session_id = db.Column(db.String(255), nullable=False, unique=True, index=True)  # ID de sesión de Flask
    ip_address = db.Column(db.String(50), nullable=False, index=True)
    user_agent = db.Column(db.Text)
    modulo_actual = db.Column(db.String(100), index=True)  # Módulo donde está trabajando
    ruta_actual = db.Column(db.String(255))  # URL actual
    conectado = db.Column(db.Boolean, default=True, index=True)
    fecha_inicio = db.Column(db.DateTime, default=datetime.now, nullable=False)
    fecha_ultima_actividad = db.Column(db.DateTime, default=datetime.now, nullable=False)
    fecha_desconexion = db.Column(db.DateTime)
    pais = db.Column(db.String(100))  # País de la IP (API geolocalización)
    ciudad = db.Column(db.String(100))  # Ciudad
    latitud = db.Column(db.Numeric(10, 8))  # Coordenadas para mapas
    longitud = db.Column(db.Numeric(11, 8))
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        ahora = datetime.now()
        ultima_actividad = self.fecha_ultima_actividad
        
        # Calcular tiempo desde última actividad
        if ultima_actividad:
            delta = ahora - ultima_actividad
            minutos_inactivo = int(delta.total_seconds() / 60)
        else:
            minutos_inactivo = 0
        
        # Determinar estado real (desconectar si >10 minutos sin actividad)
        estado_real = self.conectado and minutos_inactivo < 10
        
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario_nombre': self.usuario_nombre,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'modulo_actual': self.modulo_actual or 'Dashboard',
            'ruta_actual': self.ruta_actual,
            'conectado': estado_real,
            'fecha_inicio': self.fecha_inicio.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_inicio else None,
            'fecha_ultima_actividad': self.fecha_ultima_actividad.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_ultima_actividad else None,
            'fecha_desconexion': self.fecha_desconexion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_desconexion else None,
            'minutos_inactivo': minutos_inactivo,
            'tiempo_sesion': str(ahora - self.fecha_inicio).split('.')[0] if self.fecha_inicio else None,
            'pais': self.pais or 'Desconocido',
            'ciudad': self.ciudad or 'Desconocido',
            'latitud': float(self.latitud) if self.latitud else None,
            'longitud': float(self.longitud) if self.longitud else None
        }


# =============================================
# 🆕 NUEVOS MODELOS PARA MONITOREO COMPLETO
# =============================================

class LogSistema(db.Model):
    """Logs de aplicación con diferentes niveles"""
    __tablename__ = 'logs_sistema'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(20), nullable=False)  # ERROR, WARNING, INFO, DEBUG
    modulo = db.Column(db.String(100))
    mensaje = db.Column(db.Text, nullable=False)
    detalles = db.Column(JSONB)
    usuario = db.Column(db.String(100))
    ip = db.Column(db.String(50))
    stack_trace = db.Column(db.Text)
    archivo_origen = db.Column(db.String(255))
    linea_codigo = db.Column(db.Integer)
    resuelto = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M:%S') if self.fecha else None,
            'tipo': self.tipo,
            'modulo': self.modulo,
            'mensaje': self.mensaje,
            'detalles': self.detalles,
            'usuario': self.usuario,
            'ip': self.ip,
            'stack_trace': self.stack_trace,
            'archivo_origen': self.archivo_origen,
            'linea_codigo': self.linea_codigo,
            'resuelto': self.resuelto
        }
    
    def __repr__(self):
        return f'<LogSistema {self.tipo}: {self.mensaje[:50]}>'


class LogAuditoria(db.Model):
    """Auditoría de cambios en datos"""
    __tablename__ = 'logs_auditoria'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    tabla = db.Column(db.String(100), nullable=False)
    registro_id = db.Column(db.Integer)
    accion = db.Column(db.String(20), nullable=False)  # INSERT, UPDATE, DELETE
    datos_anteriores = db.Column(JSONB)
    datos_nuevos = db.Column(JSONB)
    usuario = db.Column(db.String(100))
    ip = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    sesion_id = db.Column(db.String(255))
    motivo = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M:%S') if self.fecha else None,
            'tabla': self.tabla,
            'registro_id': self.registro_id,
            'accion': self.accion,
            'datos_anteriores': self.datos_anteriores,
            'datos_nuevos': self.datos_nuevos,
            'usuario': self.usuario,
            'ip': self.ip,
            'user_agent': self.user_agent,
            'sesion_id': self.sesion_id,
            'motivo': self.motivo
        }
    
    def __repr__(self):
        return f'<LogAuditoria {self.accion} en {self.tabla}>'


class AlertaSistema(db.Model):
    """Sistema de alertas configurable"""
    __tablename__ = 'alertas_sistema'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(50), nullable=False)  # SEGURIDAD, RENDIMIENTO, ESPACIO, ERROR, SISTEMA
    severidad = db.Column(db.String(20), nullable=False)  # CRITICA, ALTA, MEDIA, BAJA
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    detalles = db.Column(JSONB)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, vista, resuelta, ignorada
    usuario_creador = db.Column(db.String(100))
    usuario_asignado = db.Column(db.String(100))
    fecha_visto = db.Column(db.DateTime)
    fecha_resuelto = db.Column(db.DateTime)
    notas_resolucion = db.Column(db.Text)
    contador_ocurrencias = db.Column(db.Integer, default=1)
    ultima_ocurrencia = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None,
            'tipo': self.tipo,
            'severidad': self.severidad,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'detalles': self.detalles,
            'estado': self.estado,
            'usuario_creador': self.usuario_creador,
            'usuario_asignado': self.usuario_asignado,
            'fecha_visto': self.fecha_visto.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_visto else None,
            'fecha_resuelto': self.fecha_resuelto.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_resuelto else None,
            'notas_resolucion': self.notas_resolucion,
            'contador_ocurrencias': self.contador_ocurrencias,
            'ultima_ocurrencia': self.ultima_ocurrencia.strftime('%Y-%m-%d %H:%M:%S') if self.ultima_ocurrencia else None
        }
    
    def __repr__(self):
        return f'<AlertaSistema {self.severidad}: {self.titulo}>'


class MetricaRendimiento(db.Model):
    """Métricas de rendimiento del sistema"""
    __tablename__ = 'metricas_rendimiento'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cpu_percent = db.Column(db.Numeric(5,2))
    memoria_percent = db.Column(db.Numeric(5,2))
    memoria_total_mb = db.Column(db.Integer)
    memoria_usada_mb = db.Column(db.Integer)
    disco_percent = db.Column(db.Numeric(5,2))
    disco_total_gb = db.Column(db.Integer)
    disco_usado_gb = db.Column(db.Integer)
    conexiones_bd = db.Column(db.Integer)
    requests_por_minuto = db.Column(db.Integer)
    tiempo_respuesta_promedio_ms = db.Column(db.Integer)
    usuarios_activos = db.Column(db.Integer)
    errores_ultimo_minuto = db.Column(db.Integer)
    alertas_activas = db.Column(db.Integer)
    temperatura_cpu = db.Column(db.Numeric(4,1))
    load_average = db.Column(db.Numeric(4,2))
    red_entrada_mb = db.Column(db.Numeric(8,2))
    red_salida_mb = db.Column(db.Numeric(8,2))
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M:%S') if self.fecha else None,
            'cpu_percent': float(self.cpu_percent) if self.cpu_percent else None,
            'memoria_percent': float(self.memoria_percent) if self.memoria_percent else None,
            'memoria_total_mb': self.memoria_total_mb,
            'memoria_usada_mb': self.memoria_usada_mb,
            'disco_percent': float(self.disco_percent) if self.disco_percent else None,
            'disco_total_gb': self.disco_total_gb,
            'disco_usado_gb': self.disco_usado_gb,
            'conexiones_bd': self.conexiones_bd,
            'requests_por_minuto': self.requests_por_minuto,
            'tiempo_respuesta_promedio_ms': self.tiempo_respuesta_promedio_ms,
            'usuarios_activos': self.usuarios_activos,
            'errores_ultimo_minuto': self.errores_ultimo_minuto,
            'alertas_activas': self.alertas_activas,
            'temperatura_cpu': float(self.temperatura_cpu) if self.temperatura_cpu else None,
            'load_average': float(self.load_average) if self.load_average else None,
            'red_entrada_mb': float(self.red_entrada_mb) if self.red_entrada_mb else None,
            'red_salida_mb': float(self.red_salida_mb) if self.red_salida_mb else None
        }
    
    def __repr__(self):
        return f'<MetricaRendimiento {self.fecha}: CPU {self.cpu_percent}%>'


class IPBlanca(db.Model):
    """IPs autorizadas (whitelist)"""
    __tablename__ = 'ips_blancas'
    __table_args__ = {'extend_existing': True}
    
    ip = db.Column(db.String(50), primary_key=True)  # ip es la primary key real
    descripcion = db.Column(db.String(255))
    usuario_agrego = db.Column(db.String(100))
    fecha_agregada = db.Column(db.DateTime, default=datetime.utcnow)
    activa = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime)
    total_accesos = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'descripcion': self.descripcion,
            'usuario_agrego': self.usuario_agrego,
            'fecha_agregada': self.fecha_agregada.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_agregada else None,
            'activa': self.activa,
            'ultimo_acceso': self.ultimo_acceso.strftime('%Y-%m-%d %H:%M:%S') if self.ultimo_acceso else None,
            'total_accesos': self.total_accesos
        }
    
    def __repr__(self):
        return f'<IPBlanca {self.ip}: {self.descripcion}>'

