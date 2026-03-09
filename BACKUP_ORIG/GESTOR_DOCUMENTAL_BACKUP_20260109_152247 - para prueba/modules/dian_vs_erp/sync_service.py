"""
Servicio de sincronización en TIEMPO REAL
Entre módulos de recepción/causaciones y maestro_dian_vs_erp

Este servicio se invoca cada vez que se registra, modifica o rechaza una factura
para mantener sincronizado el estado contable en maestro_dian_vs_erp
"""

from extensions import db
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


def normalizar_clave_factura(nit, prefijo, folio):
    """
    Normaliza la clave de factura según el estándar DIAN vs ERP
    Retorna: (nit_limpio, prefijo_limpio, folio_8_digitos)
    
    Ejemplo:
    Input: NIT=900.123.456-7, Prefijo=FE, Folio=FE-00012345678
    Output: ('9001234567', 'FE', '12345678')
    """
    # 1. Limpiar NIT (solo números)
    nit_limpio = re.sub(r'[^0-9]', '', str(nit))
    
    # 2. Limpiar PREFIJO (solo letras mayúsculas)
    prefijo_limpio = re.sub(r'[0-9\-\.]', '', str(prefijo)).strip().upper()
    
    # 3. Limpiar FOLIO (solo números)
    folio_numeros = re.sub(r'[^0-9]', '', str(folio))
    
    # 4. Extraer últimos 8 dígitos sin ceros a la izquierda
    if len(folio_numeros) >= 8:
        folio_8 = folio_numeros[-8:]
    else:
        folio_8 = folio_numeros
    
    # Quitar ceros a la izquierda
    folio_8 = folio_8.lstrip('0') or '0'
    
    return nit_limpio, prefijo_limpio, folio_8


def sincronizar_factura_recibida(nit, prefijo, folio, fecha_recibida, usuario, origen='RECIBIR_FACTURAS', razon_social=None):
    """
    Sincroniza una factura recibida con maestro_dian_vs_erp
    Cambia estado_contable a "Recibida"
    
    Se llama desde:
    - Módulo Recibir Facturas (al guardar)
    - Módulo Recibir Facturas Digitales (al confirmar recepción)
    
    Parámetros:
    - nit: NIT del emisor
    - prefijo: Prefijo de la factura (FE, NC, ND, etc.)
    - folio: Número de folio
    - fecha_recibida: Fecha de recepción
    - usuario: Usuario que recibió
    - origen: Módulo de origen (RECIBIR_FACTURAS, RECIBIR_FACTURAS_DIGITALES)
    - razon_social: Razón social del tercero (opcional)
    
    Retorna: (exito: bool, mensaje: str, accion: str)
    """
    try:
        # 🔥 NORMALIZAR CLAVE SEGÚN ESTÁNDAR DIAN (Dec 29, 2025)
        # NIT (solo números) + PREFIJO (solo letras) + FOLIO (últimos 8 sin ceros)
        nit_limpio, prefijo_limpio, folio_8 = normalizar_clave_factura(nit, prefijo, folio)
        
        logger.info(f"🔄 SYNC RECIBIDA: Buscando factura {nit_limpio}-{prefijo_limpio}-{folio_8}")
        
        # Buscar en maestro con CLAVE NORMALIZADA (como se guarda en actualizar_maestro)
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit_limpio,
            prefijo=prefijo_limpio,
            folio=folio_8
        ).first()
        
        if factura:
            # CASO A: Factura YA EXISTE en maestro → ACTUALIZAR SOLO estado_contable
            # ⚠️ NO sobrescribir otros campos que vienen del archivo DIAN
            
            # 🔥 JERARQUÍA DE ESTADOS (Dec 29, 2025):
            # 1. No Registrada → puede cambiar a Recibida
            # 2. Recibida → puede cambiar a En Trámite, Novedad, Rechazada
            # 3. Novedad → puede cambiar a En Trámite, Rechazada, Causada
            # 4. En Trámite → puede cambiar a Causada, Rechazada
            # 5. Rechazada → FINAL (no cambia)
            # 6. Causada → FINAL (no cambia)
            
            estado_actual = (factura.estado_contable or "").strip()
            
            # Solo cambiar a "Recibida" si está en estado INFERIOR (No Registrada o vacío)
            if estado_actual in ["", "No Registrada"]:
                if not factura.recibida:
                    factura.recibida = True
                    factura.fecha_recibida = fecha_recibida
                    factura.estado_contable = "Recibida"
                    factura.usuario_recibio = usuario
                    factura.origen_sincronizacion = origen
                    
                    db.session.commit()
                    logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} ACTUALIZADA a 'Recibida'")
                    return True, "Factura actualizada en DIAN vs ERP", "ACTUALIZADA"
                else:
                    logger.info(f"ℹ️ SYNC: Factura {prefijo_limpio}-{folio_8} ya estaba marcada como recibida")
                    return True, "Factura ya estaba marcada como recibida", "YA_SINCRONIZADA"
            else:
                # Estado superior detectado - NO sobrescribir
                logger.info(f"⚠️ SYNC: Factura {prefijo_limpio}-{folio_8} está en estado superior '{estado_actual}' - NO se sobrescribe")
                
                # Actualizar campos de recepción SIN cambiar estado_contable
                if not factura.recibida:
                    factura.recibida = True
                    factura.fecha_recibida = fecha_recibida
                    factura.usuario_recibio = usuario
                    db.session.commit()
                    logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} marcada como recibida SIN cambiar estado_contable")
                
                return True, f"Factura en estado '{estado_actual}' - campos actualizados sin sobrescribir estado", "RESPETADO_ESTADO_SUPERIOR"
        
        else:
            # CASO B: Factura NO EXISTE en maestro → INSERTAR (raro, pero posible)
            nueva_factura = MaestroDianVsErp(
                nit_emisor=nit_limpio,
                prefijo=prefijo_limpio,
                folio=folio_8,
                razon_social=razon_social or '',
                fecha_emision=fecha_recibida,  # Usar fecha recibida como aproximación
                recibida=True,
                fecha_recibida=fecha_recibida,
                estado_contable="Recibida",
                usuario_recibio=usuario,
                origen_sincronizacion=origen
            )
            
            db.session.add(nueva_factura)
            db.session.commit()
            logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} INSERTADA como 'Recibida'")
            return True, "Factura registrada en DIAN vs ERP", "INSERTADA"
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ ERROR SYNC: {str(e)}")
        return False, f"Error en sincronización: {str(e)}", "ERROR"


def sincronizar_factura_en_tramite(nit, prefijo, folio, numero_relacion, usuario):
    """
    Sincroniza una factura cuando se genera una relación
    Cambia estado_contable a "En Trámite"
    
    Se llama desde:
    - Módulo Relaciones (al generar relación física o digital)
    
    Parámetros:
    - nit: NIT del emisor
    - prefijo: Prefijo de la factura
    - folio: Número de folio
    - numero_relacion: Número de la relación generada (ej: REL-001)
    - usuario: Usuario que generó la relación
    
    Retorna: (exito: bool, mensaje: str, accion: str)
    """
    try:
        # Normalizar clave
        nit_limpio, prefijo_limpio, folio_8 = normalizar_clave_factura(nit, prefijo, folio)
        
        logger.info(f"🔄 SYNC: Marcando factura {nit_limpio}-{prefijo_limpio}-{folio_8} como 'En Trámite'")
        
        # Buscar en maestro
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit_limpio,
            prefijo=prefijo_limpio,
            folio=folio_8
        ).first()
        
        if factura:
            # 🔥 JERARQUÍA: Solo cambiar a "En Trámite" si NO está en estado final o superior
            # Puede cambiar desde: No Registrada, Recibida, Novedad
            # NO puede cambiar desde: Causada, Rechazada
            estado_actual = (factura.estado_contable or "").strip()
            
            if estado_actual not in ['Causada', 'Rechazada']:
                factura.estado_contable = "En Trámite"
                factura.origen_sincronizacion = f"RELACIONES_{numero_relacion}"
                
                db.session.commit()
                logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} ACTUALIZADA a 'En Trámite' (desde '{estado_actual}')")
                return True, f"Factura en trámite (relación {numero_relacion})", "ACTUALIZADA"
            else:
                logger.info(f"⚠️ SYNC: Factura {prefijo_limpio}-{folio_8} ya está en estado FINAL '{estado_actual}' - NO se sobrescribe")
                return True, f"Factura en estado final: {estado_actual}", "RESPETADO_ESTADO_FINAL"
        else:
            # Factura no existe en maestro, insertar con estado "En Trámite"
            nueva_factura = MaestroDianVsErp(
                nit_emisor=nit_limpio,
                prefijo=prefijo_limpio,
                folio=folio_8,
                fecha_emision=datetime.now().date(),
                estado_contable="En Trámite",
                origen_sincronizacion=f"RELACIONES_{numero_relacion}",
                recibida=True,  # Implícito porque está en relación
                fecha_recibida=datetime.now()
            )
            
            db.session.add(nueva_factura)
            db.session.commit()
            logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} INSERTADA como 'En Trámite'")
            return True, "Factura registrada en trámite", "INSERTADA"
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ ERROR SYNC EN TRÁMITE: {str(e)}")
        return False, f"Error: {str(e)}", "ERROR"


def sincronizar_factura_causada(nit, prefijo, folio, usuario):
    """
    Sincroniza una factura cuando es causada
    Cambia estado_contable a "Causada"
    
    Se llama desde:
    - Módulo Causaciones (al mover a carpeta CAUSADAS)
    
    Parámetros:
    - nit: NIT del emisor
    - prefijo: Prefijo de la factura
    - folio: Número de folio
    - usuario: Usuario que causó
    
    Retorna: (exito: bool, mensaje: str, accion: str)
    """
    try:
        # Normalizar clave
        nit_limpio, prefijo_limpio, folio_8 = normalizar_clave_factura(nit, prefijo, folio)
        
        logger.info(f"🔄 SYNC: Marcando factura {nit_limpio}-{prefijo_limpio}-{folio_8} como 'Causada'")
        
        # Buscar en maestro
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit_limpio,
            prefijo=prefijo_limpio,
            folio=folio_8
        ).first()
        
        if factura:
            # Actualizar a "Causada"
            factura.causada = True
            factura.fecha_causacion = datetime.now()
            factura.usuario_causacion = usuario
            factura.estado_contable = "Causada"
            factura.doc_causado_por = usuario
            factura.origen_sincronizacion = "CAUSACIONES"
            
            db.session.commit()
            logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} CAUSADA por {usuario}")
            return True, f"Factura causada por {usuario}", "CAUSADA"
        else:
            # Factura no existe, insertar causada directamente
            nueva_factura = MaestroDianVsErp(
                nit_emisor=nit_limpio,
                prefijo=prefijo_limpio,
                folio=folio_8,
                fecha_emision=datetime.now().date(),
                causada=True,
                fecha_causacion=datetime.now(),
                usuario_causacion=usuario,
                estado_contable="Causada",
                doc_causado_por=usuario,
                origen_sincronizacion="CAUSACIONES"
            )
            
            db.session.add(nueva_factura)
            db.session.commit()
            logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} INSERTADA como 'Causada'")
            return True, "Factura causada registrada", "INSERTADA"
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ ERROR SYNC CAUSADA: {str(e)}")
        return False, f"Error: {str(e)}", "ERROR"


def sincronizar_factura_rechazada(nit, prefijo, folio, motivo, usuario, origen='RELACIONES'):
    """
    Sincroniza una factura cuando es rechazada
    Cambia estado_contable a "Rechazada"
    
    Se llama desde:
    - Módulo Relaciones (nuevo botón de rechazo)
    - Módulo Causaciones (estado = rechazado)
    
    Parámetros:
    - nit: NIT del emisor
    - prefijo: Prefijo de la factura
    - folio: Número de folio
    - motivo: Motivo del rechazo
    - usuario: Usuario que rechazó
    - origen: Módulo desde donde se rechazó
    
    Retorna: (exito: bool, mensaje: str, accion: str)
    """
    try:
        # Normalizar clave
        nit_limpio, prefijo_limpio, folio_8 = normalizar_clave_factura(nit, prefijo, folio)
        
        logger.info(f"🔄 SYNC: Marcando factura {nit_limpio}-{prefijo_limpio}-{folio_8} como 'Rechazada'")
        
        # Buscar en maestro
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit_limpio,
            prefijo=prefijo_limpio,
            folio=folio_8
        ).first()
        
        if factura:
            # Actualizar a "Rechazada"
            factura.rechazada = True
            factura.fecha_rechazo = datetime.now()
            factura.motivo_rechazo = motivo
            factura.estado_contable = "Rechazada"
            factura.origen_sincronizacion = origen
            
            db.session.commit()
            logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} RECHAZADA por {usuario}")
            return True, f"Factura rechazada: {motivo}", "RECHAZADA"
        else:
            # Factura no existe, insertar rechazada
            nueva_factura = MaestroDianVsErp(
                nit_emisor=nit_limpio,
                prefijo=prefijo_limpio,
                folio=folio_8,
                fecha_emision=datetime.now().date(),
                rechazada=True,
                fecha_rechazo=datetime.now(),
                motivo_rechazo=motivo,
                estado_contable="Rechazada",
                origen_sincronizacion=origen
            )
            
            db.session.add(nueva_factura)
            db.session.commit()
            logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} INSERTADA como 'Rechazada'")
            return True, "Factura rechazada registrada", "INSERTADA"
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ ERROR SYNC RECHAZADA: {str(e)}")
        return False, f"Error: {str(e)}", "ERROR"


def eliminar_factura_temporal(nit, prefijo, folio):
    """
    Elimina una factura del maestro DIAN vs ERP cuando se borra de temporales
    SOLO elimina si el origen es FACTURAS_TEMPORALES (no eliminar si ya está en definitivas)
    
    Se llama desde:
    - Módulo Recibir Facturas (al eliminar temporal)
    
    Parámetros:
    - nit: NIT del emisor
    - prefijo: Prefijo de la factura
    - folio: Número de folio
    
    Retorna: (exito: bool, mensaje: str, accion: str)
    """
    try:
        # Normalizar clave
        nit_limpio, prefijo_limpio, folio_8 = normalizar_clave_factura(nit, prefijo, folio)
        
        logger.info(f"🔄 SYNC: Intentando eliminar factura temporal {nit_limpio}-{prefijo_limpio}-{folio_8}")
        
        # Buscar en maestro
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit_limpio,
            prefijo=prefijo_limpio,
            folio=folio_8
        ).first()
        
        if factura:
            # SOLO eliminar si el origen es FACTURAS_TEMPORALES
            if factura.origen_sincronizacion == 'FACTURAS_TEMPORALES':
                db.session.delete(factura)
                db.session.commit()
                logger.info(f"✅ SYNC: Factura temporal {prefijo_limpio}-{folio_8} ELIMINADA del maestro")
                return True, "Factura temporal eliminada del maestro DIAN", "ELIMINADA"
            else:
                logger.info(f"ℹ️ SYNC: Factura {prefijo_limpio}-{folio_8} NO eliminada (origen: {factura.origen_sincronizacion})")
                return True, f"Factura NO eliminada (origen: {factura.origen_sincronizacion})", "NO_ELIMINADA"
        else:
            logger.info(f"ℹ️ SYNC: Factura {prefijo_limpio}-{folio_8} no existe en maestro")
            return True, "Factura no existe en maestro", "NO_EXISTE"
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ ERROR SYNC ELIMINAR: {str(e)}")
        return False, f"Error: {str(e)}", "ERROR"


def marcar_novedad_causacion(nit, prefijo, folio, descripcion_novedad, usuario):
    """
    Marca una factura con novedad en el módulo de causaciones
    La novedad indica que hay un problema que necesita validación
    
    Se llama desde:
    - Módulo Causaciones (botón "Reportar Novedad")
    
    Parámetros:
    - nit: NIT del emisor
    - prefijo: Prefijo de la factura
    - folio: Número de folio
    - descripcion_novedad: Descripción del problema
    - usuario: Usuario que reporta la novedad
    
    Retorna: (exito: bool, mensaje: str)
    """
    try:
        # Normalizar clave
        nit_limpio, prefijo_limpio, folio_8 = normalizar_clave_factura(nit, prefijo, folio)
        
        logger.info(f"🔄 SYNC: Marcando novedad en {nit_limpio}-{prefijo_limpio}-{folio_8}")
        
        # Buscar en maestro
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit_limpio,
            prefijo=prefijo_limpio,
            folio=folio_8
        ).first()
        
        if factura:
            # Actualizar estado contable a "Con Novedad"
            factura.estado_contable = "Con Novedad"
            factura.origen_sincronizacion = "CAUSACIONES_NOVEDAD"
            
            db.session.commit()
            logger.info(f"✅ SYNC: Factura {prefijo_limpio}-{folio_8} marcada con NOVEDAD")
            return True, f"Novedad registrada: {descripcion_novedad}"
        else:
            logger.info(f"⚠️ SYNC: Factura {prefijo_limpio}-{folio_8} no existe en maestro para marcar novedad")
            return False, "Factura no encontrada en maestro DIAN"
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ ERROR SYNC NOVEDAD: {str(e)}")
        return False, f"Error: {str(e)}"


def obtener_estado_actual(nit, prefijo, folio):
    """
    Consulta el estado actual de una factura en maestro_dian_vs_erp
    
    Retorna: dict con estado actual o None si no existe
    """
    try:
        nit_limpio, prefijo_limpio, folio_8 = normalizar_clave_factura(nit, prefijo, folio)
        
        factura = MaestroDianVsErp.query.filter_by(
            nit_emisor=nit_limpio,
            prefijo=prefijo_limpio,
            folio=folio_8
        ).first()
        
        if factura:
            return {
                'existe': True,
                'estado_contable': factura.estado_contable,
                'recibida': factura.recibida,
                'causada': factura.causada,
                'rechazada': factura.rechazada if hasattr(factura, 'rechazada') else False,
                'origen': factura.origen_sincronizacion,
                'fecha_ultima_actualizacion': factura.fecha_actualizacion
            }
        else:
            return {
                'existe': False,
                'estado_contable': 'No Registrada'
            }
    
    except Exception as e:
        logger.error(f"❌ ERROR CONSULTA ESTADO: {str(e)}")
        return {'existe': False, 'error': str(e)}
