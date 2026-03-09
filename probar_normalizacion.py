"""
Probar normalización de claves
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.dian_vs_erp.sync_service import normalizar_clave_factura

# Probar con ambas facturas
print("\n=== PROBANDO NORMALIZACIÓN ===\n")

print("1️⃣ BIMBO:")
nit1, prefijo1, folio1 = normalizar_clave_factura('830002366', 'ME40', '772863')
print(f"   Input: NIT=830002366, Prefijo=ME40, Folio=772863")
print(f"   Output: NIT={nit1}, Prefijo={prefijo1}, Folio={folio1}")

print("\n2️⃣ GALERÍA:")
nit2, prefijo2, folio2 = normalizar_clave_factura('805013653', '1FEA', '77')
print(f"   Input: NIT=805013653, Prefijo=1FEA, Folio=77")
print(f"   Output: NIT={nit2}, Prefijo={prefijo2}, Folio={folio2}")

print("\n=== BUSCANDO EN BD ===\n")

from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp

with app.app_context():
    # Buscar BIMBO con folio normalizado
    print("🔍 Buscando BIMBO con folio normalizado...")
    bimbo = MaestroDianVsErp.query.filter_by(
        nit_emisor=nit1,
        prefijo=prefijo1,
        folio=folio1
    ).first()
    print(f"   Resultado: {'✅ ENCONTRADA' if bimbo else '❌ NO ENCONTRADA'}")
    if bimbo:
        print(f"   Folio en BD: '{bimbo.folio}'")
    
    # Buscar GALERÍA con folio normalizado
    print("\n🔍 Buscando GALERÍA con folio normalizado...")
    galeria = MaestroDianVsErp.query.filter_by(
        nit_emisor=nit2,
        prefijo=prefijo2,
        folio=folio2
    ).first()
    print(f"   Resultado: {'✅ ENCONTRADA' if galeria else '❌ NO ENCONTRADA'}")
    if galeria:
        print(f"   Folio en BD: '{galeria.folio}'")
    
    # Buscar GALERÍA con folio SIN normalizar
    print("\n🔍 Buscando GALERÍA con folio SIN normalizar ('77')...")
    galeria_sin_norm = MaestroDianVsErp.query.filter_by(
        nit_emisor='805013653',
        prefijo='1FEA',
        folio='77'
    ).first()
    print(f"   Resultado: {'✅ ENCONTRADA' if galeria_sin_norm else '❌ NO ENCONTRADA'}")
