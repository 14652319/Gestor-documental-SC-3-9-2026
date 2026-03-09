"""
Utilidades de manejo de fechas para el Gestor Documental
"""
from datetime import datetime
import pytz

def obtener_fecha_naive_colombia():
    """
    Retorna la fecha y hora actual de Colombia sin información de zona horaria
    
    Returns:
        datetime: Fecha y hora actual en Colombia (naive datetime)
    """
    # Zona horaria de Colombia (UTC-5)
    tz_colombia = pytz.timezone('America/Bogota')
    
    # Obtener fecha actual en Colombia
    ahora_colombia = datetime.now(tz_colombia)
    
    # Convertir a naive datetime (sin zona horaria)
    return ahora_colombia.replace(tzinfo=None)


def obtener_fecha_aware_colombia():
    """
    Retorna la fecha y hora actual de Colombia con información de zona horaria
    
    Returns:
        datetime: Fecha y hora actual en Colombia (aware datetime)
    """
    tz_colombia = pytz.timezone('America/Bogota')
    return datetime.now(tz_colombia)


def formatear_fecha_colombia(fecha, formato='%Y-%m-%d %H:%M:%S'):
    """
    Formatea una fecha según el formato especificado
    
    Args:
        fecha (datetime): Fecha a formatear
        formato (str): Formato de salida (por defecto: '%Y-%m-%d %H:%M:%S')
    
    Returns:
        str: Fecha formateada
    """
    if fecha is None:
        return ""
    return fecha.strftime(formato)
