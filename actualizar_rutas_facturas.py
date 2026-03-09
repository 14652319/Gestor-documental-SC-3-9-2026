# -*- coding: utf-8 -*-
"""
Script para actualizar rutas relativas a rutas completas en facturas_digitales
Fecha: 8 de diciembre de 2025
"""
from app import app, db
from modules.facturas_digitales.models import FacturaDigital, ConfigRutasFacturas
import os

def actualizar_rutas_facturas():
    """Actualiza rutas relativas a rutas completas"""
    with app.app_context():
        print("=" * 60)
        print("ACTUALIZACIÓN DE RUTAS DE FACTURAS DIGITALES")
        print("=" * 60)
        
        # Obtener ruta base
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        ruta_base = config.ruta_local if config else 'D:/facturas_digitales'
        print(f"\n📁 Ruta base: {ruta_base}")
        
        # Obtener todas las facturas
        facturas = FacturaDigital.query.all()
        print(f"\n📊 Total facturas: {len(facturas)}")
        
        actualizadas = 0
        sin_cambios = 0
        errores = 0
        
        for factura in facturas:
            try:
                ruta_actual = factura.ruta_carpeta
                
                # Si la ruta ya es absoluta (empieza con D:/ o C:/), dejarla como está
                if ruta_actual and (ruta_actual.startswith('D:/') or 
                                   ruta_actual.startswith('D:\\') or 
                                   ruta_actual.startswith('C:/') or 
                                   ruta_actual.startswith('C:\\')):
                    print(f"✅ ID {factura.id}: Ruta ya es absoluta: {ruta_actual}")
                    sin_cambios += 1
                    continue
                
                # Si la ruta es relativa, convertir a absoluta
                if ruta_actual:
                    # Eliminar / inicial si existe
                    ruta_relativa = ruta_actual.lstrip('/')
                    
                    # Construir ruta absoluta
                    nueva_ruta = os.path.join(ruta_base, ruta_relativa)
                    nueva_ruta = nueva_ruta.replace('\\', '/')  # Normalizar separadores
                    
                    # Actualizar en BD
                    factura.ruta_carpeta = nueva_ruta
                    
                    print(f"🔄 ID {factura.id}:")
                    print(f"   Antes: {ruta_actual}")
                    print(f"   Después: {nueva_ruta}")
                    
                    actualizadas += 1
                else:
                    print(f"⚠️ ID {factura.id}: No tiene ruta_carpeta")
                    sin_cambios += 1
                    
            except Exception as e:
                print(f"❌ Error procesando factura ID {factura.id}: {str(e)}")
                errores += 1
        
        # Guardar cambios
        if actualizadas > 0:
            try:
                db.session.commit()
                print(f"\n✅ CAMBIOS GUARDADOS EN BASE DE DATOS")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ ERROR GUARDANDO CAMBIOS: {str(e)}")
                return
        else:
            print(f"\nℹ️ No hay cambios para guardar")
        
        # Resumen
        print("\n" + "=" * 60)
        print("RESUMEN")
        print("=" * 60)
        print(f"✅ Actualizadas: {actualizadas}")
        print(f"ℹ️ Sin cambios: {sin_cambios}")
        print(f"❌ Errores: {errores}")
        print(f"📊 Total: {len(facturas)}")
        print("=" * 60)

if __name__ == '__main__':
    actualizar_rutas_facturas()
