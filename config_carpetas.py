"""
Configuración de carpetas de red para el módulo de Causaciones
Centraliza las rutas de red mapeadas para cada sede y estado
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def obtener_carpetas_base():
    """
    Obtiene el diccionario de carpetas base desde variables de entorno
    Retorna un diccionario con las rutas de red mapeadas para cada sede
    """
    carpetas_base = {
        "CYS": os.getenv('CARPETA_CYS', r"W:\ACREEDORES_CYS\APROBADAS"),
        "DOM": os.getenv('CARPETA_DOM', r"V:\ACREEDORES_DOM\APROBADAS"),
        "TIC": os.getenv('CARPETA_TIC', r"U:\ACREEDORES_TIC\APROBADAS"),
        "MER": os.getenv('CARPETA_MER', r"X:\APROBADAS"),
        "MYP": os.getenv('CARPETA_MYP', r"Z:\APROBADAS"),
        "FIN": os.getenv('CARPETA_FIN', r"T:\ACREEDORES_FIN\APROBADAS"),
        "CYS_C": os.getenv('CARPETA_CYS_C', r"W:\ACREEDORES_CYS\CAUSADAS"),
        "DOM_C": os.getenv('CARPETA_DOM_C', r"V:\ACREEDORES_DOM\CAUSADAS"),
        "TIC_C": os.getenv('CARPETA_TIC_C', r"U:\ACREEDORES_TIC\CAUSADAS"),
        "MER_C": os.getenv('CARPETA_MER_C', r"X:\CAUSADAS"),
        "MYP_C": os.getenv('CARPETA_MYP_C', r"Z:\CAUSADAS"),
        "FIN_C": os.getenv('CARPETA_FIN_C', r"T:\ACREEDORES_FIN\CAUSADAS"),
    }
    return carpetas_base

def obtener_sedes_disponibles():
    """
    Retorna lista de sedes disponibles (sin sufijo _C)
    """
    return ["CYS", "DOM", "TIC", "MER", "MYP", "FIN"]

def obtener_nombre_sede(codigo_sede):
    """
    Retorna el nombre completo de la sede según su código
    """
    nombres_sedes = {
        "CYS": "Comercial y Servicios",
        "DOM": "Domicilios",
        "TIC": "Tecnología",
        "MER": "Mercadeo",
        "MYP": "Mantenimiento y Producción",
        "FIN": "Finanzas"
    }
    return nombres_sedes.get(codigo_sede, codigo_sede)

def verificar_acceso_carpetas():
    """
    Verifica qué carpetas de red están accesibles
    Retorna un diccionario con el estado de cada carpeta
    """
    carpetas = obtener_carpetas_base()
    estado = {}
    
    for sede, ruta in carpetas.items():
        try:
            accesible = os.path.exists(ruta)
            estado[sede] = {
                "ruta": ruta,
                "accesible": accesible,
                "nombre": obtener_nombre_sede(sede.replace("_C", ""))
            }
        except Exception as e:
            estado[sede] = {
                "ruta": ruta,
                "accesible": False,
                "error": str(e),
                "nombre": obtener_nombre_sede(sede.replace("_C", ""))
            }
    
    return estado

def escanear_sedes_y_carpetas(sedes_seleccionadas, filtro=""):
    """
    Escanea las carpetas de red según la documentación del sistema original.
    
    Paso 2: Copiar la Función de Escaneo - Esta función recorre automáticamente
    las subcarpetas de cada sede para encontrar archivos PDF.
    
    Args:
        sedes_seleccionadas: Lista de sedes a escanear (ej: ['CYS', 'DOM', 'TIC'])
        filtro: Filtro de texto para buscar en nombres de archivos (opcional)
    
    Returns:
        Lista de diccionarios con información de archivos encontrados
        Cada elemento contiene: sede, rel_pdf, fecha, ruta
    """
    carpetas_base = obtener_carpetas_base()
    archivos = []
    carpetas = []
    
    for sede in sedes_seleccionadas:
        base = carpetas_base.get(sede)
        if not base or not os.path.exists(base):
            continue
        
        # Recolectar subcarpetas de cada sede
        for root, dirs, _ in os.walk(base):
            for d in dirs:
                rel = os.path.relpath(os.path.join(root, d), base).replace("\\", "/")
                carpetas.append(rel)
        
        # Buscar archivos PDF
        for root, _, files in os.walk(base):
            for f in files:
                if f.lower().endswith('.pdf') and filtro.lower() in f.lower():
                    ruta = os.path.join(root, f)
                    fecha = os.path.getmtime(ruta)
                    rel_pdf = os.path.relpath(ruta, base).replace(os.sep, '/')
                    archivos.append({
                        'sede': sede,
                        'rel_pdf': rel_pdf,
                        'fecha': fecha,
                        'ruta': ruta
                    })
    
    return archivos, sorted(set(carpetas))
