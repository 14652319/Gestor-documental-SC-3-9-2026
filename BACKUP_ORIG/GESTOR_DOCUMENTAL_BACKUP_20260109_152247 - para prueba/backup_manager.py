"""
Sistema de Backup Automático - Gestor Documental
Versión: 1.0
Fecha: Diciembre 1, 2025

Realiza backups de:
- Base de datos PostgreSQL
- Archivos del sistema (documentos_terceros, documentos_contables, facturas_digitales)
- Código fuente del Gestor Documental

Con configuración de destinos, horarios y retención.
"""

import os
import subprocess
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from extensions import db
from sqlalchemy import text, Column, Integer, String, DateTime, Boolean, BigInteger
import logging

# Configurar logging específico para backups
backup_logger = logging.getLogger('backup')
backup_logger.setLevel(logging.INFO)

# Handler para archivo de log
log_handler = logging.FileHandler('logs/backup.log', encoding='utf-8')
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
backup_logger.addHandler(log_handler)

# ============================================================================
# MODELO DE BASE DE DATOS
# ============================================================================

class ConfiguracionBackup(db.Model):
    """Configuración del sistema de backups"""
    __tablename__ = 'configuracion_backup'
    
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False, unique=True)  # 'base_datos', 'archivos', 'codigo'
    habilitado = Column(Boolean, default=True)
    destino = Column(String(500), nullable=False)
    horario_cron = Column(String(50), default='0 2 * * *')  # 2 AM diario por defecto
    dias_retencion = Column(Integer, default=7)
    ultima_ejecucion = Column(DateTime)
    proximo_backup = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'habilitado': self.habilitado,
            'destino': self.destino,
            'horario_cron': self.horario_cron,
            'dias_retencion': self.dias_retencion,
            'ultima_ejecucion': self.ultima_ejecucion.isoformat() if self.ultima_ejecucion else None,
            'proximo_backup': self.proximo_backup.isoformat() if self.proximo_backup else None
        }

class HistorialBackup(db.Model):
    """Historial de backups ejecutados"""
    __tablename__ = 'historial_backup'
    
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime)
    estado = Column(String(20), nullable=False)  # 'exitoso', 'fallido', 'en_progreso'
    ruta_archivo = Column(String(500))
    tamano_bytes = Column(BigInteger)
    duracion_segundos = Column(Integer)
    mensaje = Column(String(1000))
    error = Column(String(2000))
    usuario = Column(String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'estado': self.estado,
            'ruta_archivo': self.ruta_archivo,
            'tamano_mb': round(self.tamano_bytes / (1024 * 1024), 2) if self.tamano_bytes else 0,
            'duracion_segundos': self.duracion_segundos,
            'mensaje': self.mensaje,
            'error': self.error,
            'usuario': self.usuario
        }

# ============================================================================
# FUNCIONES DE BACKUP
# ============================================================================

def obtener_credenciales_bd():
    """Obtener credenciales de PostgreSQL desde DATABASE_URL"""
    from urllib.parse import urlparse
    database_url = os.getenv('DATABASE_URL', '')
    
    if not database_url:
        raise ValueError("DATABASE_URL no configurada en .env")
    
    parsed = urlparse(database_url)
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path[1:],  # Quitar el / inicial
        'username': parsed.username,
        'password': parsed.password
    }

def backup_base_datos(destino, nombre_archivo=None):
    """
    Realiza backup de la base de datos PostgreSQL
    
    Args:
        destino: Directorio donde guardar el backup
        nombre_archivo: Nombre del archivo (opcional, se genera automático)
    
    Returns:
        tuple: (exito, ruta_archivo, tamano_bytes, mensaje_error)
    """
    inicio = datetime.now()
    
    try:
        # Crear directorio de destino si no existe
        Path(destino).mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo
        if not nombre_archivo:
            fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"backup_bd_{fecha}.backup"
        
        ruta_completa = os.path.join(destino, nombre_archivo)
        
        # Obtener credenciales
        creds = obtener_credenciales_bd()
        
        # Configurar variable de entorno para password
        env = os.environ.copy()
        env['PGPASSWORD'] = creds['password']
        
        # Comando pg_dump (formato custom comprimido)
        comando = [
            'pg_dump',
            '-h', creds['host'],
            '-p', str(creds['port']),
            '-U', creds['username'],
            '-F', 'c',  # Formato custom (comprimido)
            '-b',  # Incluir blobs
            '-v',  # Verbose
            '-f', ruta_completa,
            creds['database']
        ]
        
        # Ejecutar backup
        resultado = subprocess.run(
            comando,
            env=env,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hora máximo
        )
        
        if resultado.returncode != 0:
            error = f"Error en pg_dump: {resultado.stderr}"
            backup_logger.error(error)
            return False, None, 0, error
        
        # Verificar que el archivo se creó
        if not os.path.exists(ruta_completa):
            error = "El archivo de backup no se creó"
            backup_logger.error(error)
            return False, None, 0, error
        
        # Obtener tamaño
        tamano = os.path.getsize(ruta_completa)
        
        duracion = (datetime.now() - inicio).seconds
        mensaje = f"Backup exitoso | Tamaño: {tamano/(1024*1024):.2f} MB | Duración: {duracion}s"
        backup_logger.info(mensaje)
        
        return True, ruta_completa, tamano, None
        
    except subprocess.TimeoutExpired:
        error = "Timeout en backup de base de datos (>1 hora)"
        backup_logger.error(error)
        return False, None, 0, error
        
    except Exception as e:
        error = f"Error inesperado en backup BD: {str(e)}"
        backup_logger.error(error)
        return False, None, 0, error

def backup_archivos(destino, carpetas_a_respaldar, nombre_archivo=None):
    """
    Realiza backup de carpetas de archivos
    
    Args:
        destino: Directorio donde guardar el backup
        carpetas_a_respaldar: Lista de rutas a respaldar
        nombre_archivo: Nombre del archivo ZIP (opcional)
    
    Returns:
        tuple: (exito, ruta_archivo, tamano_bytes, mensaje_error)
    """
    inicio = datetime.now()
    
    try:
        # Crear directorio de destino si no existe
        Path(destino).mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo
        if not nombre_archivo:
            fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"backup_archivos_{fecha}.zip"
        
        ruta_completa = os.path.join(destino, nombre_archivo)
        
        # Crear archivo ZIP
        total_archivos = 0
        with zipfile.ZipFile(ruta_completa, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for carpeta in carpetas_a_respaldar:
                if not os.path.exists(carpeta):
                    backup_logger.warning(f"Carpeta no encontrada: {carpeta}")
                    continue
                
                # Agregar carpeta al ZIP manteniendo estructura
                for root, dirs, files in os.walk(carpeta):
                    for file in files:
                        archivo_completo = os.path.join(root, file)
                        archivo_relativo = os.path.relpath(archivo_completo, os.path.dirname(carpeta))
                        zipf.write(archivo_completo, archivo_relativo)
                        total_archivos += 1
        
        # Obtener tamaño
        tamano = os.path.getsize(ruta_completa)
        
        duracion = (datetime.now() - inicio).seconds
        mensaje = f"Backup archivos exitoso | {total_archivos} archivos | Tamaño: {tamano/(1024*1024):.2f} MB | Duración: {duracion}s"
        backup_logger.info(mensaje)
        
        return True, ruta_completa, tamano, None
        
    except Exception as e:
        error = f"Error en backup de archivos: {str(e)}"
        backup_logger.error(error)
        return False, None, 0, error

def backup_codigo(destino, carpeta_proyecto, nombre_archivo=None):
    """
    Realiza backup del código fuente del proyecto
    
    Args:
        destino: Directorio donde guardar el backup
        carpeta_proyecto: Ruta del proyecto
        nombre_archivo: Nombre del archivo ZIP (opcional)
    
    Returns:
        tuple: (exito, ruta_archivo, tamano_bytes, mensaje_error)
    """
    inicio = datetime.now()
    
    try:
        # Crear directorio de destino si no existe
        Path(destino).mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo
        if not nombre_archivo:
            fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"backup_codigo_{fecha}.zip"
        
        ruta_completa = os.path.join(destino, nombre_archivo)
        
        # Carpetas/archivos a excluir
        excluir = {
            '.venv', '__pycache__', '.git', 'node_modules',
            'documentos_terceros', 'documentos_contables', 'facturas_digitales',
            '*.pyc', '*.log', '*.backup'
        }
        
        # Crear archivo ZIP
        total_archivos = 0
        with zipfile.ZipFile(ruta_completa, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(carpeta_proyecto):
                # Filtrar directorios excluidos
                dirs[:] = [d for d in dirs if d not in excluir]
                
                for file in files:
                    # Saltar archivos excluidos
                    if any(file.endswith(ext.replace('*', '')) for ext in excluir if '*' in ext):
                        continue
                    
                    archivo_completo = os.path.join(root, file)
                    archivo_relativo = os.path.relpath(archivo_completo, carpeta_proyecto)
                    zipf.write(archivo_completo, archivo_relativo)
                    total_archivos += 1
        
        # Obtener tamaño
        tamano = os.path.getsize(ruta_completa)
        
        duracion = (datetime.now() - inicio).seconds
        mensaje = f"Backup código exitoso | {total_archivos} archivos | Tamaño: {tamano/(1024*1024):.2f} MB | Duración: {duracion}s"
        backup_logger.info(mensaje)
        
        return True, ruta_completa, tamano, None
        
    except Exception as e:
        error = f"Error en backup de código: {str(e)}"
        backup_logger.error(error)
        return False, None, 0, error

def limpiar_backups_antiguos(directorio, dias_retencion):
    """
    Elimina backups más antiguos que X días
    
    Args:
        directorio: Directorio donde están los backups
        dias_retencion: Número de días a mantener
    """
    try:
        if not os.path.exists(directorio):
            return
        
        fecha_limite = datetime.now() - timedelta(days=dias_retencion)
        archivos_eliminados = 0
        
        for archivo in os.listdir(directorio):
            ruta_completa = os.path.join(directorio, archivo)
            
            # Solo procesar archivos (no directorios)
            if not os.path.isfile(ruta_completa):
                continue
            
            # Verificar extensiones de backup
            if not (archivo.endswith('.backup') or archivo.endswith('.zip')):
                continue
            
            # Verificar fecha de modificación
            fecha_archivo = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
            
            if fecha_archivo < fecha_limite:
                os.remove(ruta_completa)
                archivos_eliminados += 1
                backup_logger.info(f"Backup antiguo eliminado: {archivo}")
        
        if archivos_eliminados > 0:
            backup_logger.info(f"Limpieza completada: {archivos_eliminados} backups antiguos eliminados")
            
    except Exception as e:
        backup_logger.error(f"Error en limpieza de backups: {str(e)}")

def ejecutar_backup_completo(tipo, usuario='sistema'):
    """
    Ejecuta un backup según el tipo configurado
    
    Args:
        tipo: 'base_datos', 'archivos', 'codigo'
        usuario: Usuario que ejecutó el backup
    
    Returns:
        dict: Resultado del backup
    """
    inicio = datetime.now()
    
    # Crear registro en historial
    historial = HistorialBackup(
        tipo=tipo,
        fecha_inicio=inicio,
        estado='en_progreso',
        usuario=usuario
    )
    db.session.add(historial)
    db.session.commit()
    
    try:
        # Obtener configuración
        config = ConfiguracionBackup.query.filter_by(tipo=tipo).first()
        
        if not config or not config.habilitado:
            error = f"Backup tipo '{tipo}' no configurado o deshabilitado"
            historial.estado = 'fallido'
            historial.error = error
            historial.fecha_fin = datetime.now()
            db.session.commit()
            return {'success': False, 'error': error}
        
        # Ejecutar según tipo
        if tipo == 'base_datos':
            exito, ruta, tamano, error = backup_base_datos(config.destino)
            
        elif tipo == 'archivos':
            # Carpetas a respaldar
            carpetas = [
                'documentos_terceros',
                'documentos_contables',
                'facturas_digitales'
            ]
            exito, ruta, tamano, error = backup_archivos(config.destino, carpetas)
            
        elif tipo == 'codigo':
            carpeta_proyecto = os.getcwd()
            exito, ruta, tamano, error = backup_codigo(config.destino, carpeta_proyecto)
        else:
            error = f"Tipo de backup no válido: {tipo}"
            exito = False
            ruta = None
            tamano = 0
        
        # Actualizar historial
        fin = datetime.now()
        historial.fecha_fin = fin
        historial.estado = 'exitoso' if exito else 'fallido'
        historial.ruta_archivo = ruta
        historial.tamano_bytes = tamano
        historial.duracion_segundos = (fin - inicio).seconds
        
        if exito:
            historial.mensaje = f"Backup completado exitosamente"
            # Actualizar configuración
            config.ultima_ejecucion = fin
            # Limpiar backups antiguos
            limpiar_backups_antiguos(config.destino, config.dias_retencion)
        else:
            historial.error = error
        
        db.session.commit()
        
        return {
            'success': exito,
            'ruta': ruta,
            'tamano_mb': round(tamano / (1024*1024), 2) if tamano else 0,
            'duracion_segundos': (fin - inicio).seconds,
            'error': error
        }
        
    except Exception as e:
        error = f"Error inesperado: {str(e)}"
        backup_logger.error(error)
        
        historial.estado = 'fallido'
        historial.error = error
        historial.fecha_fin = datetime.now()
        db.session.commit()
        
        return {'success': False, 'error': error}

def inicializar_configuracion_backup():
    """Crea configuración por defecto si no existe"""
    try:
        # Ruta base de backups
        base_backups = os.path.join(os.getcwd(), 'backups')
        
        configs_default = [
            {
                'tipo': 'base_datos',
                'destino': os.path.join(base_backups, 'base_datos'),
                'horario_cron': '0 2 * * *',  # 2 AM diario
                'dias_retencion': 7
            },
            {
                'tipo': 'archivos',
                'destino': os.path.join(base_backups, 'documentos'),
                'horario_cron': '0 3 * * *',  # 3 AM diario
                'dias_retencion': 14
            },
            {
                'tipo': 'codigo',
                'destino': os.path.join(base_backups, 'codigo'),
                'horario_cron': '0 4 * * 0',  # 4 AM cada domingo
                'dias_retencion': 30
            }
        ]
        
        for cfg in configs_default:
            existe = ConfiguracionBackup.query.filter_by(tipo=cfg['tipo']).first()
            if not existe:
                config = ConfiguracionBackup(**cfg)
                db.session.add(config)
        
        db.session.commit()
        backup_logger.info("Configuración de backups inicializada")
        
    except Exception as e:
        backup_logger.error(f"Error al inicializar configuración: {str(e)}")
        db.session.rollback()
