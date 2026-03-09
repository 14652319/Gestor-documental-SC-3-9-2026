"""
Helper de Logging Enriquecido para DIAN VS ERP
===============================================

Sistema centralizado de logging con contexto completo:
- Usuario, IP, NIT, empresa
- Métricas de performance
- Stack traces de errores
- Detalles en JSON

Uso:
    from modules.dian_vs_erp.logger_helper import registrar_log
    
    registrar_log(
        nivel='SUCCESS',
        operacion='CREAR_USUARIO',
        mensaje='Usuario de causación creado exitosamente',
        nit='900123456',
        duracion_ms=234
    )
"""

import json
import traceback
from datetime import datetime
from flask import has_request_context
from extensions import db

# Importar modelos solo cuando sea necesario para evitar circular imports
def _get_log_model():
    from modules.dian_vs_erp.models import LogSistemaDianVsErp
    return LogSistemaDianVsErp


def registrar_log(nivel, operacion, mensaje, **kwargs):
    """
    Registra un log enriquecido con contexto automático.
    
    Args:
        nivel (str): Nivel del log - 'SUCCESS', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        operacion (str): Tipo de operación - 'CREAR_USUARIO', 'ENVIO_EMAIL', etc.
        mensaje (str): Mensaje descriptivo del log
        
        **kwargs opcionales:
            nit_relacionado (str): NIT asociado a la operación
            empresa_relacionada (str): Nombre de la empresa
            duracion_ms (int): Duración de la operación en milisegundos
            recurso_tipo (str): Tipo de recurso - 'CONFIGURACION', 'USUARIO', etc.
            recurso_id (int): ID del recurso afectado
            detalles (dict): Diccionario con información adicional
            incluir_stacktrace (bool): True para incluir stack trace (automático en ERROR/CRITICAL)
    
    Returns:
        LogSistemaDianVsErp: El objeto log creado
    
    Ejemplo:
        >>> registrar_log(
        ...     'SUCCESS',
        ...     'CREAR_USUARIO',
        ...     'Usuario creado exitosamente',
        ...     nit='900123456',
        ...     recurso_tipo='USUARIO',
        ...     recurso_id=42,
        ...     detalles={'email': 'user@example.com'}
        ... )
    """
    try:
        # Extraer contexto automático de Flask (si existe request context)
        usuario = 'SISTEMA'
        usuario_id = None
        ip_origen = None
        user_agent = ''
        
        try:
            # Intentar obtener datos de sesión y request (solo funciona en request context)
            if has_request_context():
                from flask import session, request
                
                if session:
                    usuario = session.get('usuario', 'SISTEMA')
                    usuario_id = session.get('usuario_id')
                
                if request:
                    # IP del cliente (maneja proxies)
                    ip_origen = request.remote_addr
                    if request.headers.get('X-Forwarded-For'):
                        ip_origen = request.headers.get('X-Forwarded-For').split(',')[0].strip()
                    
                    # User agent
                    user_agent = request.headers.get('User-Agent', '')
        except RuntimeError:
            # Fuera de request context - usar valores por defecto
            pass
        
        # Stack trace si es error o si se solicita explícitamente
        stack_trace = None
        if nivel in ['ERROR', 'CRITICAL'] or kwargs.get('incluir_stacktrace', False):
            stack_trace = traceback.format_exc()
        
        # Convertir detalles a JSON si es dict
        detalles = kwargs.get('detalles')
        if isinstance(detalles, dict):
            detalles = json.dumps(detalles, ensure_ascii=False)
        
        # Obtener modelo LogSistemaDianVsErp
        LogSistemaDianVsErp = _get_log_model()
        
        # Crear registro de log
        log_entry = LogSistemaDianVsErp(
            timestamp=datetime.now(),
            fecha=datetime.now().date(),
            usuario=usuario,
            usuario_id=usuario_id,
            ip_origen=ip_origen,
            user_agent=user_agent,
            nit_relacionado=kwargs.get('nit_relacionado'),
            empresa_relacionada=kwargs.get('empresa_relacionada'),
            nivel=nivel,
            modulo='DIAN_VS_ERP',
            operacion=operacion,
            mensaje=mensaje,
            detalles=detalles,
            duracion_ms=kwargs.get('duracion_ms'),
            recurso_tipo=kwargs.get('recurso_tipo'),
            recurso_id=kwargs.get('recurso_id'),
            stack_trace=stack_trace
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
        
    except Exception as e:
        # Fallback: Si falla el logging, al menos imprimimos en consola
        print(f"❌ ERROR REGISTRANDO LOG: {e}")
        print(f"   Nivel: {nivel} | Operación: {operacion} | Mensaje: {mensaje}")
        return None


def registrar_tiempo_operacion(operacion):
    """
    Decorador para medir automáticamente el tiempo de una operación.
    
    Uso:
        @registrar_tiempo_operacion('GENERAR_RELACION')
        def generar_relacion():
            # ... código ...
            return resultado
    """
    def decorador(func):
        def wrapper(*args, **kwargs):
            inicio = datetime.now()
            resultado = None
            nivel = 'SUCCESS'
            mensaje = f"Operación {operacion} completada"
            
            try:
                resultado = func(*args, **kwargs)
                return resultado
            except Exception as e:
                nivel = 'ERROR'
                mensaje = f"Error en {operacion}: {str(e)}"
                raise  # Re-lanzar la excepción después de registrarla
            finally:
                duracion_ms = int((datetime.now() - inicio).total_seconds() * 1000)
                registrar_log(nivel, operacion, mensaje, duracion_ms=duracion_ms)
        
        wrapper.__name__ = func.__name__
        return wrapper
    return decorador


def obtener_logs_recientes(limite=100, nivel=None, operacion=None, usuario=None):
    """
    Obtiene logs recientes con filtros opcionales.
    
    Args:
        limite (int): Cantidad máxima de logs a retornar
        nivel (str): Filtrar por nivel (SUCCESS, INFO, WARNING, ERROR, CRITICAL)
        operacion (str): Filtrar por tipo de operación
        usuario (str): Filtrar por usuario
    
    Returns:
        list: Lista de logs en formato diccionario
    """
    LogSistemaDianVsErp = _get_log_model()
    
    query = LogSistemaDianVsErp.query
    
    if nivel:
        query = query.filter_by(nivel=nivel)
    if operacion:
        query = query.filter_by(operacion=operacion)
    if usuario:
        query = query.filter_by(usuario=usuario)
    
    logs = query.order_by(LogSistemaDianVsErp.timestamp.desc()).limit(limite).all()
    return [log.to_dict() for log in logs]


def obtener_estadisticas_logs(fecha_desde=None, fecha_hasta=None):
    """
    Obtiene estadísticas agregadas de logs.
    
    Args:
        fecha_desde (date): Fecha inicio del rango
        fecha_hasta (date): Fecha fin del rango
    
    Returns:
        dict: Estadísticas con conteos por nivel, operaciones lentas, etc.
    """
    from sqlalchemy import func
    
    LogSistemaDianVsErp = _get_log_model()
    
    query = db.session.query(
        LogSistemaDianVsErp.nivel,
        func.count(LogSistemaDianVsErp.id).label('cantidad')
    )
    
    if fecha_desde:
        query = query.filter(LogSistemaDianVsErp.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(LogSistemaDianVsErp.fecha <= fecha_hasta)
    
    conteos_por_nivel = {nivel: cantidad for nivel, cantidad in query.group_by(LogSistemaDianVsErp.nivel).all()}
    
    # Operaciones lentas (> 5 segundos)
    operaciones_lentas = LogSistemaDianVsErp.query.filter(
        LogSistemaDianVsErp.duracion_ms > 5000
    ).count()
    
    # Total de logs
    total = sum(conteos_por_nivel.values())
    
    # Tasa de éxito
    exitosos = conteos_por_nivel.get('SUCCESS', 0) + conteos_por_nivel.get('INFO', 0)
    errores = conteos_por_nivel.get('ERROR', 0) + conteos_por_nivel.get('CRITICAL', 0)
    tasa_exito = round((exitosos / total * 100) if total > 0 else 0, 2)
    
    return {
        'total_logs': total,
        'por_nivel': conteos_por_nivel,
        'operaciones_lentas': operaciones_lentas,
        'tasa_exito_porcentaje': tasa_exito,
        'total_exitosos': exitosos,
        'total_errores': errores
    }
