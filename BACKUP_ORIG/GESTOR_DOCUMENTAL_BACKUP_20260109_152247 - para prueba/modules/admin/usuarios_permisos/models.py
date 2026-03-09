"""
==============================================
🔐 MODELOS - SISTEMA DE USUARIOS Y PERMISOS
==============================================

Sistema avanzado de gestión de usuarios y permisos granulares
por módulo y acción específica.

Autor: GitHub Copilot
Fecha: Octubre 23, 2025
"""

from extensions import db
from datetime import datetime
from sqlalchemy import text
import hashlib
import secrets

# ============================================================================
# 📊 TABLA: PERMISOS POR MÓDULO Y ACCIÓN
# ============================================================================

class PermisoUsuario(db.Model):
    """
    Permisos granulares por usuario, módulo y acción específica
    """
    __tablename__ = 'permisos_usuarios'
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'modulo', 'accion', name='uq_usuario_modulo_accion'),
        {'extend_existing': True}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    modulo = db.Column(db.String(50), nullable=False)  # ej: "recibir_facturas", "relaciones"
    accion = db.Column(db.String(100), nullable=False)  # ej: "nueva_factura", "exportar_temporales"
    permitido = db.Column(db.Boolean, default=False, nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.now)
    asignado_por = db.Column(db.String(50))  # Usuario que asignó el permiso
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'modulo': self.modulo,
            'accion': self.accion,
            'permitido': self.permitido,
            'fecha_asignacion': self.fecha_asignacion.isoformat() if self.fecha_asignacion else None,
            'asignado_por': self.asignado_por
        }
    
    def __repr__(self):
        return f'<PermisoUsuario {self.usuario_id}: {self.modulo}.{self.accion}={self.permitido}>'

# ============================================================================
# 🎭 TABLA: ROLES Y PLANTILLAS DE PERMISOS
# ============================================================================

class RolUsuario(db.Model):
    """
    Roles predefinidos con plantillas de permisos
    """
    __tablename__ = 'roles_usuarios'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)  # ej: "Administrador", "Contador", "Auditor"
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    def __repr__(self):
        return f'<RolUsuario {self.nombre}>'

# ============================================================================
# 🔗 TABLA: ASIGNACIÓN DE ROLES A USUARIOS
# ============================================================================

class UsuarioRol(db.Model):
    """
    Relación muchos-a-muchos entre usuarios y roles
    """
    __tablename__ = 'usuarios_roles'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles_usuarios.id'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.now)
    asignado_por = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True)
    
    # Índice único para evitar duplicados
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'rol_id', name='uq_usuario_rol'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'rol_id': self.rol_id,
            'fecha_asignacion': self.fecha_asignacion.isoformat() if self.fecha_asignacion else None,
            'asignado_por': self.asignado_por,
            'activo': self.activo
        }

# ============================================================================
# 📧 TABLA: INVITACIONES DE USUARIOS
# ============================================================================

class InvitacionUsuario(db.Model):
    """
    Sistema de invitaciones por correo para crear contraseñas
    """
    __tablename__ = 'invitaciones_usuarios'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    token_invitacion = db.Column(db.String(255), unique=True, nullable=False)
    correo_enviado = db.Column(db.String(255), nullable=False)
    usado = db.Column(db.Boolean, default=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.now)
    fecha_expiracion = db.Column(db.DateTime, nullable=False)
    fecha_uso = db.Column(db.DateTime)
    enviado_por = db.Column(db.String(50))
    ip_uso = db.Column(db.String(50))
    
    def generar_token(self):
        """Genera token seguro para invitación"""
        self.token_invitacion = secrets.token_urlsafe(32)
    
    def esta_vigente(self):
        """Verifica si la invitación aún es válida"""
        return not self.usado and self.fecha_expiracion > datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'token_invitacion': self.token_invitacion,
            'correo_enviado': self.correo_enviado,
            'usado': self.usado,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
            'fecha_expiracion': self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            'fecha_uso': self.fecha_uso.isoformat() if self.fecha_uso else None,
            'enviado_por': self.enviado_por,
            'vigente': self.esta_vigente()
        }

# ============================================================================
# 📝 TABLA: AUDITORÍA DE CAMBIOS DE PERMISOS
# ============================================================================

class AuditoriaPermisos(db.Model):
    """
    Registro de todos los cambios en permisos para auditoría
    """
    __tablename__ = 'auditoria_permisos'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_afectado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    tipo_cambio = db.Column(db.String(50), nullable=False)  # "CREAR_USUARIO", "ACTIVAR", "DESACTIVAR", "CAMBIAR_PERMISO"
    modulo = db.Column(db.String(50))
    accion = db.Column(db.String(100))  # Nombre de la acción/permiso específico
    valor_anterior = db.Column(db.String(255))
    valor_nuevo = db.Column(db.String(255))
    realizado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))  # ID del usuario que realizó el cambio
    fecha_cambio = db.Column(db.DateTime, default=datetime.now)
    ip_origen = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    comentario = db.Column(db.Text)
    permiso_accion = db.Column(db.String(100))  # Redundante pero está en la tabla PostgreSQL
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_afectado_id': self.usuario_afectado_id,
            'tipo_cambio': self.tipo_cambio,
            'modulo': self.modulo,
            'accion': self.accion,
            'permiso_accion': self.permiso_accion,
            'valor_anterior': self.valor_anterior,
            'valor_nuevo': self.valor_nuevo,
            'realizado_por': self.realizado_por,
            'fecha_cambio': self.fecha_cambio.isoformat() if self.fecha_cambio else None,
            'ip_origen': self.ip_origen,
            'user_agent': self.user_agent,
            'comentario': self.comentario
        }

# ============================================================================
# 🗂️ CATÁLOGO DE MÓDULOS Y ACCIONES DISPONIBLES
# ============================================================================

class CatalogoPermisos:
    """
    Catálogo estático de todos los módulos y acciones disponibles
    Basado en análisis automático del código
    """
    
    MODULOS = {
        'admin': {
            'nombre': 'Administración',
            'descripcion': 'Gestión de usuarios, permisos y configuración del sistema',
            'color': '#dc2626',  # rojo
            'icono': 'fas fa-user-shield',
            'acciones': {
                'ver_dashboard': {
                    'nombre': 'Ver Dashboard Admin',
                    'descripcion': 'Acceso al panel de administración principal',
                    'tipo': 'vista',
                    'critico': True
                },
                'gestionar_usuarios': {
                    'nombre': 'Gestionar Usuarios',
                    'descripcion': 'Crear, editar y eliminar usuarios del sistema',
                    'tipo': 'accion',
                    'critico': True
                },
                'gestionar_permisos': {
                    'nombre': 'Gestionar Permisos',
                    'descripcion': 'Asignar y modificar permisos de usuarios',
                    'tipo': 'accion',
                    'critico': True
                },
                'ver_auditoria': {
                    'nombre': 'Ver Auditoría',
                    'descripcion': 'Acceso a logs de auditoría y cambios',
                    'tipo': 'vista',
                    'critico': False
                },
                'monitoreo_sistema': {
                    'nombre': 'Monitoreo del Sistema',
                    'descripcion': 'Panel de monitoreo en tiempo real',
                    'tipo': 'vista',
                    'critico': False
                }
            }
        },
        
        'recibir_facturas': {
            'nombre': 'Recibir Facturas',
            'descripcion': 'Gestión de recepción y procesamiento de facturas de proveedores',
            'color': '#16a34a',  # verde
            'icono': 'fas fa-file-invoice',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general al módulo de recibir facturas',
                    'tipo': 'acceso',
                    'critico': False
                },
                'nueva_factura': {
                    'nombre': 'Nueva Factura',
                    'descripcion': 'Registrar nueva factura en el sistema',
                    'tipo': 'formulario',
                    'critico': False
                },
                'verificar_tercero': {
                    'nombre': 'Verificar Tercero',
                    'descripcion': 'Validar información de terceros (NITs)',
                    'tipo': 'consulta',
                    'critico': False
                },
                'validar_factura': {
                    'nombre': 'Validar Factura',
                    'descripcion': 'Verificar claves y duplicados de facturas',
                    'tipo': 'validacion',
                    'critico': False
                },
                'adicionar_factura': {
                    'nombre': 'Adicionar Factura',
                    'descripcion': 'Agregar facturas temporales al sistema',
                    'tipo': 'accion',
                    'critico': False
                },
                'cargar_facturas': {
                    'nombre': 'Cargar Facturas',
                    'descripcion': 'Ver lista de facturas temporales cargadas',
                    'tipo': 'vista',
                    'critico': False
                },
                'editar_factura': {
                    'nombre': 'Editar Factura',
                    'descripcion': 'Modificar facturas temporales',
                    'tipo': 'edicion',
                    'critico': False
                },
                'eliminar_factura': {
                    'nombre': 'Eliminar Factura',
                    'descripcion': 'Borrar facturas temporales',
                    'tipo': 'eliminacion',
                    'critico': True
                },
                'guardar_facturas': {
                    'nombre': 'Guardar Facturas',
                    'descripcion': 'Confirmar y persistir facturas en BD',
                    'tipo': 'confirmacion',
                    'critico': True
                },
                'exportar_temporales': {
                    'nombre': 'Exportar a Excel',
                    'descripcion': 'Descargar facturas temporales en Excel',
                    'tipo': 'exportacion',
                    'critico': False
                },
                'limpiar_todo': {
                    'nombre': 'Limpiar Todo',
                    'descripcion': 'Borrar todas las facturas temporales',
                    'tipo': 'eliminacion',
                    'critico': True
                }
            }
        },
        
        'relaciones': {
            'nombre': 'Relaciones de Facturas',
            'descripcion': 'Generación y gestión de relaciones digitales de facturas',
            'color': '#2563eb',  # azul
            'icono': 'fas fa-sitemap',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general al módulo de relaciones',
                    'tipo': 'acceso',
                    'critico': False
                },
                'generar_relacion': {
                    'nombre': 'Generar Relación',
                    'descripcion': 'Crear nuevas relaciones de facturas',
                    'tipo': 'formulario',
                    'critico': False
                },
                'filtrar_facturas': {
                    'nombre': 'Filtrar Facturas',
                    'descripcion': 'Buscar facturas por fecha y criterios',
                    'tipo': 'filtro',
                    'critico': False
                },
                'seleccionar_facturas': {
                    'nombre': 'Seleccionar Facturas',
                    'descripcion': 'Marcar facturas para incluir en relación',
                    'tipo': 'seleccion',
                    'critico': False
                },
                'exportar_relacion': {
                    'nombre': 'Exportar Relación',
                    'descripcion': 'Descargar relación en Excel o PDF',
                    'tipo': 'exportacion',
                    'critico': False
                },
                'reimprimir_relacion': {
                    'nombre': 'Reimprimir Relación',
                    'descripcion': 'Volver a generar relaciones existentes',
                    'tipo': 'reimpresion',
                    'critico': False
                },
                'recepcion_digital': {
                    'nombre': 'Recepción Digital',
                    'descripcion': 'Recibir relaciones digitalmente',
                    'tipo': 'formulario',
                    'critico': False
                },
                'buscar_relacion': {
                    'nombre': 'Buscar Relación',
                    'descripcion': 'Localizar relaciones por número',
                    'tipo': 'consulta',
                    'critico': False
                },
                'confirmar_recepcion': {
                    'nombre': 'Confirmar Recepción',
                    'descripcion': 'Firmar digitalmente recepciones',
                    'tipo': 'confirmacion',
                    'critico': True
                },
                'generar_token_firma': {
                    'nombre': 'Generar Token Firma',
                    'descripcion': 'Crear tokens de firma digital',
                    'tipo': 'generacion',
                    'critico': True
                },
                'verificar_token': {
                    'nombre': 'Verificar Token',
                    'descripcion': 'Validar tokens de firma digital',
                    'tipo': 'verificacion',
                    'critico': True
                },
                'consultar_recepcion': {
                    'nombre': 'Consultar Recepción',
                    'descripcion': 'Ver estado de recepciones digitales',
                    'tipo': 'consulta',
                    'critico': False
                }
            }
        },
        
        'configuracion': {
            'nombre': 'Configuración',
            'descripcion': 'Configuración de centros operativos y parámetros del sistema',
            'color': '#7c3aed',  # púrpura
            'icono': 'fas fa-cogs',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general a configuración',
                    'tipo': 'acceso',
                    'critico': False
                },
                'centros_operacion': {
                    'nombre': 'Centros de Operación',
                    'descripcion': 'Gestionar centros operativos (tiendas/bodegas)',
                    'tipo': 'gestion',
                    'critico': False
                },
                'tipos_documento': {
                    'nombre': 'Tipos de Documento',
                    'descripcion': 'Configurar tipos de documentos',
                    'tipo': 'gestion',
                    'critico': False
                },
                'parametros_sistema': {
                    'nombre': 'Parámetros del Sistema',
                    'descripcion': 'Configuración general del sistema',
                    'tipo': 'configuracion',
                    'critico': True
                }
            }
        },
        
        'notas_contables': {
            'nombre': 'Archivo Digital',
            'descripcion': 'Gestión de archivo digital y notas contables',
            'color': '#ea580c',  # naranja
            'icono': 'fas fa-file-archive',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general al archivo digital',
                    'tipo': 'acceso',
                    'critico': False
                },
                'subir_documento': {
                    'nombre': 'Subir Documento',
                    'descripcion': 'Cargar nuevos documentos al archivo',
                    'tipo': 'carga',
                    'critico': False
                },
                'buscar_documento': {
                    'nombre': 'Buscar Documento',
                    'descripcion': 'Localizar documentos en el archivo',
                    'tipo': 'busqueda',
                    'critico': False
                },
                'ver_documento': {
                    'nombre': 'Ver Documento',
                    'descripcion': 'Visualizar documentos almacenados',
                    'tipo': 'vista',
                    'critico': False
                },
                'descargar_documento': {
                    'nombre': 'Descargar Documento',
                    'descripcion': 'Descargar documentos del archivo',
                    'tipo': 'descarga',
                    'critico': False
                },
                'eliminar_documento': {
                    'nombre': 'Eliminar Documento',
                    'descripcion': 'Borrar documentos del archivo',
                    'tipo': 'eliminacion',
                    'critico': True
                },
                'solicitar_correccion_documento': {
                    'nombre': 'Solicitar Corrección de Documento',
                    'descripcion': 'Iniciar proceso de corrección de campos críticos (empresa, tipo, centro, consecutivo)',
                    'tipo': 'correccion',
                    'critico': True
                },
                'validar_correccion_documento': {
                    'nombre': 'Validar Corrección con Código',
                    'descripcion': 'Ingresar código de validación enviado por correo para aplicar corrección',
                    'tipo': 'correccion',
                    'critico': True
                },
                'aprobar_correccion_critica': {
                    'nombre': 'Aprobar Corrección Crítica',
                    'descripcion': 'Autorizar correcciones de documentos que requieren aprobación especial',
                    'tipo': 'correccion',
                    'critico': True
                }
            }
        },
        
        'causaciones': {
            'nombre': 'Causaciones',
            'descripcion': 'Visualización y renombrado de documentos de causaciones desde carpetas de red',
            'color': '#059669',  # verde esmeralda
            'icono': 'fas fa-calculator',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general a causaciones',
                    'tipo': 'acceso',
                    'critico': False
                },
                'ver_pdf': {
                    'nombre': 'Ver PDF',
                    'descripcion': 'Visualizar archivos PDF de causaciones',
                    'tipo': 'vista',
                    'critico': False
                },
                'renombrar_archivo': {
                    'nombre': 'Renombrar Archivo',
                    'descripcion': 'Cambiar nombre de archivos de causaciones',
                    'tipo': 'edicion',
                    'critico': True
                },
                'exportar_excel': {
                    'nombre': 'Exportar a Excel',
                    'descripcion': 'Exportar listado de archivos a Excel',
                    'tipo': 'exportacion',
                    'critico': False
                },
                'filtrar_archivos': {
                    'nombre': 'Filtrar Archivos',
                    'descripcion': 'Buscar y filtrar archivos por criterios',
                    'tipo': 'filtro',
                    'critico': False
                },
                'escanear_carpetas': {
                    'nombre': 'Escanear Carpetas',
                    'descripcion': 'Escanear carpetas de red en busca de documentos',
                    'tipo': 'consulta',
                    'critico': False
                }
            }
        },
        
        'facturas_digitales': {
            'nombre': 'Facturas Digitales',
            'descripcion': 'Sistema de gestión de facturas digitales con firma electrónica Adobe Sign',
            'color': '#0891b2',  # cyan
            'icono': 'fas fa-file-signature',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general a facturas digitales',
                    'tipo': 'acceso',
                    'critico': False
                },
                'ver_dashboard': {
                    'nombre': 'Ver Dashboard',
                    'descripcion': 'Acceder al dashboard de facturas digitales',
                    'tipo': 'vista',
                    'critico': False
                },
                'cargar_factura': {
                    'nombre': 'Cargar Factura',
                    'descripcion': 'Subir nueva factura digital con anexos',
                    'tipo': 'carga',
                    'critico': False
                },
                'validar_tercero': {
                    'nombre': 'Validar Tercero',
                    'descripcion': 'Verificar NIT de tercero en el sistema',
                    'tipo': 'validacion',
                    'critico': False
                },
                'verificar_duplicados': {
                    'nombre': 'Verificar Duplicados',
                    'descripcion': 'Validar que factura no esté duplicada',
                    'tipo': 'validacion',
                    'critico': False
                },
                'consultar_facturas': {
                    'nombre': 'Consultar Facturas',
                    'descripcion': 'Listar y buscar facturas digitales',
                    'tipo': 'consulta',
                    'critico': False
                },
                'ver_detalle_factura': {
                    'nombre': 'Ver Detalle Factura',
                    'descripcion': 'Ver información completa de factura',
                    'tipo': 'vista',
                    'critico': False
                },
                'editar_factura': {
                    'nombre': 'Editar Factura',
                    'descripcion': 'Modificar datos de factura digital',
                    'tipo': 'edicion',
                    'critico': True
                },
                'cambiar_estado': {
                    'nombre': 'Cambiar Estado',
                    'descripcion': 'Actualizar estado de factura (pendiente, enviada, firmada, causada, pagada)',
                    'tipo': 'edicion',
                    'critico': True
                },
                'enviar_a_firmar': {
                    'nombre': 'Enviar a Firmar',
                    'descripcion': 'Enviar factura para firma digital con Adobe Sign',
                    'tipo': 'accion',
                    'critico': True
                },
                'cargar_firmado': {
                    'nombre': 'Cargar Documento Firmado',
                    'descripcion': 'Subir documento firmado digitalmente',
                    'tipo': 'carga',
                    'critico': True
                },
                'descargar_soportes': {
                    'nombre': 'Descargar Soportes',
                    'descripcion': 'Descargar ZIP con todos los anexos',
                    'tipo': 'descarga',
                    'critico': False
                },
                'agregar_observacion': {
                    'nombre': 'Agregar Observación',
                    'descripcion': 'Añadir comentarios al historial de factura',
                    'tipo': 'edicion',
                    'critico': False
                },
                'exportar_reporte': {
                    'nombre': 'Exportar Reporte',
                    'descripcion': 'Exportar listado de facturas a Excel',
                    'tipo': 'exportacion',
                    'critico': False
                },
                'configurar_rutas': {
                    'nombre': 'Configurar Rutas',
                    'descripcion': 'Administrar rutas de almacenamiento de facturas',
                    'tipo': 'configuracion',
                    'critico': True
                }
            }
        },
        
        'monitoreo': {
            'nombre': 'Monitoreo del Sistema',
            'descripcion': 'Panel de monitoreo en tiempo real del estado del sistema',
            'color': '#8b5cf6',  # violeta
            'icono': 'fas fa-desktop',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general al panel de monitoreo',
                    'tipo': 'acceso',
                    'critico': False
                },
                'ver_dashboard': {
                    'nombre': 'Ver Dashboard',
                    'descripcion': 'Acceder al dashboard de monitoreo',
                    'tipo': 'vista',
                    'critico': False
                },
                'consultar_estadisticas': {
                    'nombre': 'Consultar Estadísticas',
                    'descripcion': 'Ver estadísticas generales del sistema',
                    'tipo': 'consulta',
                    'critico': False
                },
                'ver_uso_recursos': {
                    'nombre': 'Ver Uso de Recursos',
                    'descripcion': 'Monitorear CPU, RAM y disco del servidor',
                    'tipo': 'vista',
                    'critico': False
                },
                'ver_sesiones_activas': {
                    'nombre': 'Ver Sesiones Activas',
                    'descripcion': 'Lista de usuarios conectados en tiempo real',
                    'tipo': 'consulta',
                    'critico': False
                },
                'cerrar_sesion_remota': {
                    'nombre': 'Cerrar Sesión Remota',
                    'descripcion': 'Forzar cierre de sesión de otro usuario',
                    'tipo': 'accion',
                    'critico': True
                },
                'ver_logs_errores': {
                    'nombre': 'Ver Logs de Errores',
                    'descripcion': 'Acceder a logs de errores del sistema',
                    'tipo': 'consulta',
                    'critico': False
                },
                'ver_alertas_seguridad': {
                    'nombre': 'Ver Alertas de Seguridad',
                    'descripcion': 'Monitorear intentos de acceso sospechosos',
                    'tipo': 'consulta',
                    'critico': True
                },
                'gestionar_ips': {
                    'nombre': 'Gestionar IPs',
                    'descripcion': 'Administrar listas blanca/negra de IPs',
                    'tipo': 'gestion',
                    'critico': True
                }
            }
        },
        
        'gestion_usuarios': {
            'nombre': 'Gestión de Usuarios y Permisos',
            'descripcion': 'Administración completa de usuarios, roles y permisos del sistema',
            'color': '#dc2626',  # rojo
            'icono': 'fas fa-user-shield',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general a gestión de usuarios',
                    'tipo': 'acceso',
                    'critico': False
                },
                'ver_dashboard': {
                    'nombre': 'Ver Dashboard',
                    'descripcion': 'Acceder al dashboard de gestión de usuarios',
                    'tipo': 'vista',
                    'critico': False
                },
                'consultar_usuarios': {
                    'nombre': 'Consultar Usuarios',
                    'descripcion': 'Listar y buscar usuarios del sistema',
                    'tipo': 'consulta',
                    'critico': False
                },
                'ver_usuario': {
                    'nombre': 'Ver Detalle Usuario',
                    'descripcion': 'Ver información completa de un usuario',
                    'tipo': 'vista',
                    'critico': False
                },
                'crear_usuario': {
                    'nombre': 'Crear Usuario',
                    'descripcion': 'Dar de alta nuevos usuarios en el sistema',
                    'tipo': 'creacion',
                    'critico': True
                },
                'editar_usuario': {
                    'nombre': 'Editar Usuario',
                    'descripcion': 'Modificar datos de usuarios existentes',
                    'tipo': 'edicion',
                    'critico': True
                },
                'activar_usuario': {
                    'nombre': 'Activar/Desactivar Usuario',
                    'descripcion': 'Cambiar estado activo de usuarios',
                    'tipo': 'edicion',
                    'critico': True
                },
                'eliminar_usuario': {
                    'nombre': 'Eliminar Usuario',
                    'descripcion': 'Borrar usuarios del sistema (acción irreversible)',
                    'tipo': 'eliminacion',
                    'critico': True
                },
                'consultar_permisos': {
                    'nombre': 'Consultar Permisos',
                    'descripcion': 'Ver permisos asignados a usuarios',
                    'tipo': 'consulta',
                    'critico': False
                },
                'asignar_permisos': {
                    'nombre': 'Asignar Permisos',
                    'descripcion': 'Otorgar o revocar permisos a usuarios',
                    'tipo': 'gestion',
                    'critico': True
                },
                'consultar_roles': {
                    'nombre': 'Consultar Roles',
                    'descripcion': 'Listar roles disponibles en el sistema',
                    'tipo': 'consulta',
                    'critico': False
                },
                'asignar_roles': {
                    'nombre': 'Asignar Roles',
                    'descripcion': 'Asignar roles predefinidos a usuarios',
                    'tipo': 'gestion',
                    'critico': True
                },
                'enviar_invitacion': {
                    'nombre': 'Enviar Invitación',
                    'descripcion': 'Enviar correo de invitación para configurar contraseña',
                    'tipo': 'accion',
                    'critico': False
                },
                'resetear_password': {
                    'nombre': 'Resetear Contraseña',
                    'descripcion': 'Forzar cambio de contraseña de usuario',
                    'tipo': 'accion',
                    'critico': True
                },
                'consultar_auditoria': {
                    'nombre': 'Consultar Auditoría',
                    'descripcion': 'Ver logs de cambios en usuarios y permisos',
                    'tipo': 'consulta',
                    'critico': False
                },
                'ver_estadisticas': {
                    'nombre': 'Ver Estadísticas',
                    'descripcion': 'Dashboard de estadísticas de usuarios',
                    'tipo': 'vista',
                    'critico': False
                }
            }
        },
        
        'reportes': {
            'nombre': 'Reportes',
            'descripcion': 'Generación de reportes y análisis',
            'color': '#7c2d12',  # marrón
            'icono': 'fas fa-chart-bar',
            'acciones': {
                'acceder_modulo': {
                    'nombre': 'Acceder al Módulo',
                    'descripcion': 'Acceso general a reportes',
                    'tipo': 'acceso',
                    'critico': False
                },
                'reporte_facturas': {
                    'nombre': 'Reporte de Facturas',
                    'descripcion': 'Generar reportes de facturas',
                    'tipo': 'reporte',
                    'critico': False
                },
                'reporte_terceros': {
                    'nombre': 'Reporte de Terceros',
                    'descripcion': 'Generar reportes de terceros',
                    'tipo': 'reporte',
                    'critico': False
                },
                'exportar_datos': {
                    'nombre': 'Exportar Datos',
                    'descripcion': 'Exportar datos en diferentes formatos',
                    'tipo': 'exportacion',
                    'critico': False
                }
            }
        }
    }
    
    @classmethod
    def obtener_todos_permisos(cls):
        """Retorna lista plana de todos los permisos disponibles"""
        permisos = []
        for modulo_key, modulo_data in cls.MODULOS.items():
            for accion_key, accion_data in modulo_data['acciones'].items():
                permisos.append({
                    'modulo': modulo_key,
                    'modulo_nombre': modulo_data['nombre'],
                    'accion': accion_key,
                    'accion_nombre': accion_data['nombre'],
                    'descripcion': accion_data['descripcion'],
                    'tipo': accion_data['tipo'],
                    'critico': accion_data['critico'],
                    'color': modulo_data['color'],
                    'icono': modulo_data['icono']
                })
        return permisos
    
    @classmethod
    def obtener_estructura_modulos(cls):
        """
        Retorna estructura jerárquica de módulos y acciones
        LEE DESDE LA TABLA catalogo_permisos (FUENTE ÚNICA DE VERDAD)
        """
        from sqlalchemy import text
        from extensions import db
        
        try:
            # Obtener todos los permisos desde la BD
            permisos_bd = db.session.execute(
                text("""
                    SELECT modulo, modulo_nombre, modulo_descripcion, 
                           accion, accion_descripcion, tipo_accion, es_critico
                    FROM catalogo_permisos
                    WHERE activo = true
                    ORDER BY modulo, accion
                """)
            ).fetchall()
            
            # Construir estructura jerárquica
            modulos_dict = {}
            
            for p in permisos_bd:
                # Si el módulo no existe, crearlo
                if p.modulo not in modulos_dict:
                    modulos_dict[p.modulo] = {
                        'nombre': p.modulo_nombre,
                        'descripcion': p.modulo_descripcion or '',
                        'color': cls._obtener_color_modulo(p.modulo),
                        'icono': cls._obtener_icono_modulo(p.modulo),
                        'acciones': {}
                    }
                
                # Agregar acción
                modulos_dict[p.modulo]['acciones'][p.accion] = {
                    'nombre': p.accion.replace('_', ' ').title(),
                    'descripcion': p.accion_descripcion,
                    'tipo': p.tipo_accion or 'accion',
                    'critico': p.es_critico or False
                }
            
            return modulos_dict
            
        except Exception as e:
            # Si falla, usar catálogo hardcoded como fallback
            print(f"⚠️  Error leyendo catálogo desde BD, usando fallback: {str(e)}")
            return cls.MODULOS
    
    @classmethod
    def _obtener_color_modulo(cls, modulo):
        """Retorna color para el módulo (mantiene compatibilidad visual)"""
        colores = {
            'gestion_usuarios': '#dc2626',
            'recibir_facturas': '#16a34a',
            'relaciones': '#2563eb',
            'configuracion': '#7c3aed',
            'archivo_digital': '#ea580c',
            'notas_contables': '#ea580c',
            'causaciones': '#059669',
            'facturas_digitales': '#0891b2',
            'reportes': '#7c2d12',
            'monitoreo': '#8b5cf6'
        }
        return colores.get(modulo, '#6b7280')
    
    @classmethod
    def _obtener_icono_modulo(cls, modulo):
        """Retorna icono para el módulo (mantiene compatibilidad visual)"""
        iconos = {
            'gestion_usuarios': 'fas fa-user-shield',
            'recibir_facturas': 'fas fa-file-invoice',
            'relaciones': 'fas fa-sitemap',
            'configuracion': 'fas fa-cogs',
            'archivo_digital': 'fas fa-file-archive',
            'notas_contables': 'fas fa-file-archive',
            'causaciones': 'fas fa-calculator',
            'facturas_digitales': 'fas fa-file-signature',
            'reportes': 'fas fa-chart-bar',
            'monitoreo': 'fas fa-desktop'
        }
        return iconos.get(modulo, 'fas fa-folder')
    
    @classmethod
    def validar_permiso(cls, modulo, accion):
        """Valida si un módulo y acción existen en el catálogo"""
        return (modulo in cls.MODULOS and 
                accion in cls.MODULOS[modulo]['acciones'])

# ============================================================================
# 🔐 FUNCIONES HELPER PARA GESTIÓN DE PERMISOS
# ============================================================================

def verificar_permiso_usuario(usuario_id, modulo, accion):
    """
    Verifica si un usuario tiene permiso para una acción específica
    """
    permiso = PermisoUsuario.query.filter_by(
        usuario_id=usuario_id,
        modulo=modulo,
        accion=accion,
        permitido=True
    ).first()
    
    return permiso is not None

def asignar_permiso_usuario(usuario_id, modulo, accion, permitido=True, asignado_por=None):
    """
    Asigna o actualiza un permiso específico para un usuario
    """
    permiso = PermisoUsuario.query.filter_by(
        usuario_id=usuario_id,
        modulo=modulo,
        accion=accion
    ).first()
    
    if permiso:
        # Actualizar existente
        valor_anterior = permiso.permitido
        permiso.permitido = permitido
        permiso.fecha_asignacion = datetime.now()
        permiso.asignado_por = asignado_por
    else:
        # Crear nuevo
        valor_anterior = None
        permiso = PermisoUsuario(
            usuario_id=usuario_id,
            modulo=modulo,
            accion=accion,
            permitido=permitido,
            asignado_por=asignado_por
        )
        db.session.add(permiso)
    
    # Registrar auditoría
    try:
        # Determinar quién realizó el cambio (ID del usuario, no texto)
        from flask import session
        realizado_por_id = None
        
        if asignado_por and isinstance(asignado_por, int):
            realizado_por_id = asignado_por
        elif asignado_por and isinstance(asignado_por, str):
            # Buscar ID del usuario por nombre
            from sqlalchemy import text
            result = db.session.execute(
                text("SELECT id FROM usuarios WHERE usuario = :usuario LIMIT 1"),
                {'usuario': asignado_por}
            ).fetchone()
            realizado_por_id = result[0] if result else None
        elif 'usuario_id' in session:
            realizado_por_id = session.get('usuario_id')
        
        # Si no se pudo determinar, usar NULL (lo permite la BD)
        auditoria = AuditoriaPermisos(
            usuario_afectado_id=usuario_id,
            tipo_cambio='PERMISO',  # ✅ Valores permitidos: CREAR, ACTIVAR, DESACTIVAR, PERMISO, ROL, INVITACION
            modulo=modulo,
            accion=accion,  # Campo opcional accion (redundante pero está en tabla)
            permiso_accion=accion,  # Campo permiso_accion (para compatibilidad)
            valor_anterior=str(valor_anterior) if valor_anterior is not None else None,
            valor_nuevo=str(permitido) if permitido is not None else None,
            realizado_por=realizado_por_id,  # INT o NULL
            comentario=f"Asignado por: {asignado_por}" if asignado_por else "Sistema automático"
        )
        db.session.add(auditoria)
    except Exception as e:
        # No fallar si la auditoría falla, solo registrar
        import logging
        logging.warning(f"No se pudo registrar auditoría de permiso: {str(e)}")
    
    return permiso

def obtener_permisos_usuario(usuario_id):
    """
    Obtiene todos los permisos de un usuario organizados por módulo
    
    🔧 FIX: Usa SQL directo para evitar cache de SQLAlchemy
    """
    from sqlalchemy import text
    
    # Query SQL directa para obtener datos frescos sin cache
    permisos = db.session.execute(
        text("""
            SELECT modulo, accion, permitido 
            FROM permisos_usuarios 
            WHERE usuario_id = :usuario_id
        """),
        {'usuario_id': usuario_id}
    ).fetchall()
    
    resultado = {}
    for modulo, accion, permitido in permisos:
        if modulo not in resultado:
            resultado[modulo] = {}
        resultado[modulo][accion] = permitido
    
    return resultado

def crear_permisos_por_defecto_usuario(usuario_id, rol='usuario_basico'):
    """
    Crea permisos por defecto para un nuevo usuario según su rol
    
    Roles disponibles:
    - usuario_basico: Acceso básico a consultas
    - usuario_operativo: Acceso a módulos operativos completos
    - contador: Acceso a módulos contables
    - administrador: Acceso completo al sistema
    """
    permisos_basicos = []
    
    if rol == 'administrador' or rol == 'admin':
        # Administrador: TODOS los permisos
        permisos_basicos = [
            # Gestión de Usuarios (acceso completo)
            ('gestion_usuarios', 'acceder_modulo', True),
            ('gestion_usuarios', 'ver_dashboard', True),
            ('gestion_usuarios', 'consultar_usuarios', True),
            ('gestion_usuarios', 'crear_usuario', True),
            ('gestion_usuarios', 'editar_usuario', True),
            ('gestion_usuarios', 'activar_usuario', True),
            ('gestion_usuarios', 'asignar_permisos', True),
            ('gestion_usuarios', 'consultar_auditoria', True),
            
            # Recibir Facturas (acceso completo)
            ('recibir_facturas', 'acceder_modulo', True),
            ('recibir_facturas', 'nueva_factura', True),
            ('recibir_facturas', 'editar_factura', True),
            ('recibir_facturas', 'eliminar_factura', True),
            ('recibir_facturas', 'guardar_facturas', True),
            ('recibir_facturas', 'exportar_temporales', True),
            
            # Relaciones (acceso completo)
            ('relaciones', 'acceder_modulo', True),
            ('relaciones', 'generar_relacion', True),
            ('relaciones', 'confirmar_recepcion', True),
            ('relaciones', 'exportar_relacion', True),
            
            # Archivo Digital (acceso completo)
            ('notas_contables', 'acceder_modulo', True),
            ('notas_contables', 'subir_documento', True),
            ('notas_contables', 'editar_documento', True),  
            ('notas_contables', 'eliminar_documento', True),
            ('notas_contables', 'solicitar_correccion_documento', True),
            
            # Facturas Digitales (acceso completo)
            ('facturas_digitales', 'acceder_modulo', True),
            ('facturas_digitales', 'cargar_factura', True),
            ('facturas_digitales', 'editar_factura', True),
            ('facturas_digitales', 'enviar_a_firmar', True),
            ('facturas_digitales', 'cambiar_estado', True),
            
            # Causaciones (acceso completo)
            ('causaciones', 'acceder_modulo', True),
            ('causaciones', 'ver_pdf', True),
            ('causaciones', 'renombrar_archivo', True),
            
            # Monitoreo (acceso completo)
            ('monitoreo', 'acceder_modulo', True),
            ('monitoreo', 'ver_dashboard', True),
            ('monitoreo', 'consultar_estadisticas', True),
            ('monitoreo', 'ver_sesiones_activas', True),
            ('monitoreo', 'gestionar_ips', True),
            
            # Configuración (acceso completo)
            ('configuracion', 'acceder_modulo', True),
            ('configuracion', 'centros_operacion', True),
            ('configuracion', 'tipos_documento', True),
            ('configuracion', 'parametros_sistema', True)
        ]
    elif rol == 'contador':
        # Contador: Acceso a módulos contables
        permisos_basicos = [
            # Recibir Facturas
            ('recibir_facturas', 'acceder_modulo', True),
            ('recibir_facturas', 'nueva_factura', True),
            ('recibir_facturas', 'editar_factura', True),
            ('recibir_facturas', 'guardar_facturas', True),
            ('recibir_facturas', 'exportar_temporales', True),
            
            # Relaciones
            ('relaciones', 'acceder_modulo', True),
            ('relaciones', 'generar_relacion', True),
            ('relaciones', 'confirmar_recepcion', True),
            ('relaciones', 'exportar_relacion', True),
            
            # Archivo Digital
            ('notas_contables', 'acceder_modulo', True),
            ('notas_contables', 'subir_documento', True),
            ('notas_contables', 'buscar_documento', True),
            ('notas_contables', 'ver_documento', True),
            ('notas_contables', 'descargar_documento', True),
            ('notas_contables', 'solicitar_correccion_documento', True),
            
            # Facturas Digitales
            ('facturas_digitales', 'acceder_modulo', True),
            ('facturas_digitales', 'cargar_factura', True),
            ('facturas_digitales', 'consultar_facturas', True),
            ('facturas_digitales', 'ver_detalle_factura', True),
            ('facturas_digitales', 'enviar_a_firmar', True),
            
            # Causaciones
            ('causaciones', 'acceder_modulo', True),
            ('causaciones', 'ver_pdf', True),
            ('causaciones', 'renombrar_archivo', True),
            ('causaciones', 'exportar_excel', True),
            
            # Sin acceso a gestión de usuarios
            ('gestion_usuarios', 'acceder_modulo', False),
            ('monitoreo', 'acceder_modulo', False)
        ]
    elif rol == 'usuario_operativo':
        # Usuario operativo: Acceso a operaciones diarias
        permisos_basicos = [
            # Recibir Facturas
            ('recibir_facturas', 'acceder_modulo', True),
            ('recibir_facturas', 'nueva_factura', True),
            ('recibir_facturas', 'verificar_tercero', True),
            ('recibir_facturas', 'cargar_facturas', True),
            ('recibir_facturas', 'guardar_facturas', True),
            
            # Relaciones
            ('relaciones', 'acceder_modulo', True),
            ('relaciones', 'generar_relacion', True),
            ('relaciones', 'filtrar_facturas', True),
            
            # Archivo Digital (solo consulta)
            ('notas_contables', 'acceder_modulo', True),
            ('notas_contables', 'buscar_documento', True),
            ('notas_contables', 'ver_documento', True),
            ('notas_contables', 'descargar_documento', True),
            
            # Facturas Digitales (solo consulta)
            ('facturas_digitales', 'acceder_modulo', True),
            ('facturas_digitales', 'consultar_facturas', True),
            ('facturas_digitales', 'ver_detalle_factura', True),
            
            # Sin acceso crítico
            ('gestion_usuarios', 'acceder_modulo', False),
            ('monitoreo', 'acceder_modulo', False),
            ('configuracion', 'acceder_modulo', False)
        ]
    else:
        # Usuario básico: Solo lectura
        permisos_basicos = [
            # Recibir Facturas (básico)
            ('recibir_facturas', 'acceder_modulo', True),
            ('recibir_facturas', 'verificar_tercero', True),
            ('recibir_facturas', 'cargar_facturas', True),
            
            # Relaciones (básico)
            ('relaciones', 'acceder_modulo', True),
            ('relaciones', 'filtrar_facturas', True),
            
            # Archivo Digital (solo consulta)
            ('notas_contables', 'acceder_modulo', True),
            ('notas_contables', 'buscar_documento', True),
            ('notas_contables', 'ver_documento', True),
            
            # Facturas Digitales (solo consulta)
            ('facturas_digitales', 'acceder_modulo', True),
            ('facturas_digitales', 'consultar_facturas', True),
            
            # Sin acceso admin
            ('gestion_usuarios', 'acceder_modulo', False),
            ('monitoreo', 'acceder_modulo', False),
            ('configuracion', 'acceder_modulo', False),
            ('causaciones', 'acceder_modulo', False)
        ]
    
    for modulo, accion, permitido in permisos_basicos:
        asignar_permiso_usuario(usuario_id, modulo, accion, permitido, None)  # None = sistema automático