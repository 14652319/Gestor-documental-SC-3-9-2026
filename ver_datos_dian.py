# -*- coding: utf-8 -*-
"""
Ver datos REALES de la tabla dian para entender su estructura
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app
from extensions import db
from modules.dian_vs_erp.models import Dian
from datetime import date

print("\n" + "="*80)
print("CONSULTANDO DATOS REALES DE LA TABLA DIAN")
print("="*80)

with app.app_context():
    # Consultar primeros 5 registros
    registros = Dian.query.limit(5).all()

with app.app_context():
    # Consultar primeros 5 registros
    registros = Dian.query.limit(5).all()

    print(f"\n✅ Encontrados {len(registros)} registros (mostrando primeros 5)")

    for idx, reg in enumerate(registros, 1):
        print(f"\n📋 REGISTRO #{idx}:")
        print(f"   ID: {reg.id}")
        print(f"   Tipo Documento: {reg.tipo_documento}")
        print(f"   NIT Emisor: {reg.nit_emisor}")
        print(f"   Nombre Emisor: {reg.nombre_emisor}")
        print(f"   Prefijo: {reg.prefijo}")
        print(f"   Folio: {reg.folio}")
        print(f"   Fecha Emisión: {reg.fecha_emision}")
        print(f"   Total: {getattr(reg, 'total', 'NO EXISTE')}")
        print(f"   Valor: {getattr(reg, 'valor', 'NO EXISTE')}")
        print(f"   Estado: {getattr(reg, 'estado', 'NO EXISTE')}")
        print(f"   N Días: {getattr(reg, 'n_dias', 'NO EXISTE')}")
        print(f"   CUFE/CUDE: {reg.cufe_cude[:50] if reg.cufe_cude else 'NULL'}...")

    # Contar registros totales
    total = Dian.query.count()
    print(f"\n📊 TOTAL DE REGISTROS EN TABLA: {total:,}")

    # Contar por año
    print("\n📅 DISTRIBUCIÓN POR AÑO:")
    from sqlalchemy import func, extract
    años = db.session.query(
        extract('year', Dian.fecha_emision).label('año'),
        func.count().label('total')
    ).group_by('año').order_by('año').all()

    for año, total in años:
        print(f"   {int(año)}: {total:,} facturas")

print("\n" + "="*80)
