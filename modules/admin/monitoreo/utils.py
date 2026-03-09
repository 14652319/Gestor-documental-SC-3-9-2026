"""
Utilidades para el módulo de monitoreo
Fecha: Octubre 23, 2025
"""

import requests
from datetime import datetime
import hashlib

# ==============================================
# 🌍 FUNCIÓN: OBTENER GEOLOCALIZACIÓN DE IP
# ==============================================

def obtener_geolocalizacion_ip(ip_address):
    """
    Obtiene información geográfica de una IP usando API gratuita
    API utilizada: ip-api.com (gratuita, sin API key, límite: 45 req/min)
    """
    try:
        # No geo-localizar IPs locales
        if ip_address in ['127.0.0.1', 'localhost'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
            return {
                'pais': 'Colombia (Red Local)',
                'ciudad': 'Buga',
                'latitud': 3.9009,
                'longitud': -76.2978,
                'es_local': True
            }
        
        # Llamar a la API
        url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,regionName,city,lat,lon,timezone,isp"
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'pais': data.get('country', 'Desconocido'),
                    'region': data.get('regionName', ''),
                    'ciudad': data.get('city', 'Desconocido'),
                    'latitud': data.get('lat'),
                    'longitud': data.get('lon'),
                    'zona_horaria': data.get('timezone', ''),
                    'isp': data.get('isp', ''),
                    'es_local': False
                }
            else:
                # Error en la API
                return {
                    'pais': 'Desconocido',
                    'ciudad': 'Desconocido',
                    'latitud': None,
                    'longitud': None,
                    'es_local': False,
                    'error': data.get('message', 'Error desconocido')
                }
        else:
            return {
                'pais': 'Desconocido',
                'ciudad': 'Desconocido',
                'latitud': None,
                'longitud': None,
                'es_local': False,
                'error': f'HTTP {response.status_code}'
            }
    
    except requests.Timeout:
        return {
            'pais': 'Desconocido (Timeout)',
            'ciudad': 'Desconocido',
            'latitud': None,
            'longitud': None,
            'es_local': False,
            'error': 'Timeout'
        }
    except Exception as e:
        return {
            'pais': 'Desconocido',
            'ciudad': 'Desconocido',
            'latitud': None,
            'longitud': None,
            'es_local': False,
            'error': str(e)
        }


# ==============================================
# 🔧 FUNCIÓN: DETECTAR MÓDULO DESDE URL
# ==============================================

def detectar_modulo_desde_url(ruta):
    """
    Detecta el nombre del módulo basándose en la ruta URL
    """
    if not ruta:
        return 'Dashboard'
    
    ruta = ruta.lower()
    
    if '/recibir_facturas' in ruta or '/nueva_factura' in ruta:
        return 'Recibir Facturas'
    elif '/relaciones' in ruta:
        return 'Relaciones'
    elif '/archivo_digital' in ruta or '/archivo' in ruta:
        return 'Archivo Digital'
    elif '/causaciones' in ruta:
        return 'Causaciones'
    elif '/configuracion' in ruta:
        return 'Configuración'
    elif '/admin/monitoreo' in ruta:
        return 'Monitoreo'
    elif '/dashboard' in ruta:
        return 'Dashboard'
    else:
        return 'Otro'


# ==============================================
# 🔐 FUNCIÓN: GENERAR SESSION ID ÚNICO
# ==============================================

def generar_session_id(usuario_id, ip_address, timestamp):
    """
    Genera un ID de sesión único basado en usuario, IP y timestamp
    """
    datos = f"{usuario_id}|{ip_address}|{timestamp}"
    return hashlib.sha256(datos.encode()).hexdigest()


# ==============================================
# ⏱️ FUNCIÓN: FORMATEAR DURACIÓN
# ==============================================

def formatear_duracion(timedelta_obj):
    """
    Convierte un objeto timedelta a formato legible
    Ej: "2h 15m 30s"
    """
    if not timedelta_obj:
        return "0s"
    
    total_segundos = int(timedelta_obj.total_seconds())
    
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    
    partes = []
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}m")
    if segundos > 0 or not partes:
        partes.append(f"{segundos}s")
    
    return " ".join(partes)


# ==============================================
# 📊 FUNCIÓN: OBTENER TAMAÑO DE CARPETA
# ==============================================

def obtener_tamano_carpeta(ruta):
    """
    Calcula el tamaño total de una carpeta en bytes
    """
    import os
    total_size = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(ruta):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    except Exception as e:
        print(f"Error calculando tamaño de {ruta}: {str(e)}")
        return 0


# ==============================================
# 💾 FUNCIÓN: FORMATEAR BYTES A UNIDAD LEGIBLE
# ==============================================

def formatear_bytes(bytes_cantidad):
    """
    Convierte bytes a KB, MB, GB, TB según corresponda
    """
    if bytes_cantidad < 1024:
        return f"{bytes_cantidad} B"
    elif bytes_cantidad < 1024 ** 2:
        return f"{bytes_cantidad / 1024:.2f} KB"
    elif bytes_cantidad < 1024 ** 3:
        return f"{bytes_cantidad / (1024 ** 2):.2f} MB"
    elif bytes_cantidad < 1024 ** 4:
        return f"{bytes_cantidad / (1024 ** 3):.2f} GB"
    else:
        return f"{bytes_cantidad / (1024 ** 4):.2f} TB"
