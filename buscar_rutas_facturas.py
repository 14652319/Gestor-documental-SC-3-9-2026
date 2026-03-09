# -*- coding: utf-8 -*-
"""
Script para encontrar dónde están guardados los archivos de facturas digitales
"""
from app import app, db
from modules.facturas_digitales.models import FacturaDigital, ConfigRutasFacturas
import os

with app.app_context():
    print("=" * 80)
    print("BUSCANDO RUTAS DE ARCHIVOS - FACTURAS DIGITALES")
    print("=" * 80)
    
    # 1. Verificar configuración
    config = ConfigRutasFacturas.query.filter_by(activa=True).first()
    if config:
        print(f"\n📁 RUTA CONFIGURADA:")
        print(f"   Local: {config.ruta_local}")
        print(f"   Red: {config.ruta_red if config.ruta_red else 'No configurada'}")
    else:
        print("\n⚠️ NO HAY CONFIGURACIÓN DE RUTAS")
        print("   Usando ruta por defecto: D:/facturas_digitales")
    
    # 2. Listar todas las facturas con sus rutas
    facturas = FacturaDigital.query.all()
    print(f"\n📊 Total facturas: {len(facturas)}")
    print("\n" + "=" * 80)
    print("RUTAS DE ARCHIVOS")
    print("=" * 80)
    
    for f in facturas:
        print(f"\n📄 ID: {f.id} | Factura: {f.numero_factura}")
        print(f"   NIT: {f.nit_proveedor}")
        print(f"   Estado: {f.estado}")
        print(f"   Tipo Usuario: {f.tipo_usuario}")
        
        # Ruta de carpeta
        if f.ruta_carpeta:
            print(f"   📁 Carpeta: {f.ruta_carpeta}")
            
            # Verificar si existe
            if os.path.exists(f.ruta_carpeta):
                archivos = os.listdir(f.ruta_carpeta)
                print(f"   ✅ Carpeta EXISTE en disco")
                print(f"   📎 Archivos ({len(archivos)}):")
                for arch in archivos:
                    ruta_completa = os.path.join(f.ruta_carpeta, arch)
                    tamanio = os.path.getsize(ruta_completa) / 1024  # KB
                    print(f"      - {arch} ({tamanio:.1f} KB)")
            else:
                print(f"   ❌ Carpeta NO EXISTE en disco")
        else:
            print(f"   ⚠️ NO tiene ruta_carpeta en BD")
        
        # Ruta de archivo principal
        if f.ruta_archivo:
            print(f"   📄 Archivo principal: {f.ruta_archivo}")
            if os.path.exists(f.ruta_archivo):
                tamanio = os.path.getsize(f.ruta_archivo) / 1024  # KB
                print(f"      ✅ Archivo EXISTE ({tamanio:.1f} KB)")
            else:
                print(f"      ❌ Archivo NO EXISTE")
    
    # 3. Buscar carpetas en disco que no estén en BD
    print("\n" + "=" * 80)
    print("VERIFICANDO CARPETAS EN DISCO")
    print("=" * 80)
    
    ruta_base = config.ruta_local if config else "D:/facturas_digitales"
    
    if os.path.exists(ruta_base):
        print(f"\n✅ Ruta base existe: {ruta_base}")
        print(f"\n📂 Contenido de {ruta_base}:")
        
        for item in os.listdir(ruta_base):
            ruta_item = os.path.join(ruta_base, item)
            if os.path.isdir(ruta_item):
                print(f"   📁 {item}/")
    else:
        print(f"\n❌ Ruta base NO EXISTE: {ruta_base}")
    
    print("\n" + "=" * 80)
