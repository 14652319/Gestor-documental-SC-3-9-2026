#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear las tablas del módulo de Facturas Digitales
"""

from app import app, db
from modules.facturas_digitales.models import (
    ConfigRutasFacturas,
    FacturaDigital,
    FacturaDigitalHistorial,
    FacturaDigitalAdjunto,
    FacturaDigitalNotificacion,
    FacturaDigitalMetrica
)

if __name__ == '__main__':
    with app.app_context():
        print("🔧 Creando tablas de Facturas Digitales...")
        
        # Crear todas las tablas
        db.create_all()
        
        # Verificar si ya existe configuración por defecto
        config = ConfigRutasFacturas.query.first()
        if not config:
            print("📁 Creando configuración por defecto...")
            config_default = ConfigRutasFacturas(
                nombre='default',
                ruta_local='D:/facturas_digitales',
                activa=True,
                observaciones='Ruta de almacenamiento predeterminada'
            )
            db.session.add(config_default)
            db.session.commit()
            print("✅ Configuración creada: D:/facturas_digitales")
        else:
            print(f"ℹ️ Configuración existente: {config.ruta_local}")
        
        print("✅ Tablas de Facturas Digitales creadas exitosamente")
        print("\n📋 Tablas creadas:")
        print("   - config_rutas_facturas")
        print("   - facturas_digitales")
        print("   - facturas_digitales_historial")
        print("   - facturas_digitales_adjuntos")
        print("   - facturas_digitales_notificaciones")
        print("   - facturas_digitales_metricas")
        print("\n🌐 Accede al módulo en: http://127.0.0.1:8099/facturas-digitales/")
