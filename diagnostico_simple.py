"""
DIAGNÓSTICO SIMPLE DE CAMPOS PROBLEMÁTICOS
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from extensions import db
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import func, and_, or_
from datetime import datetime

with app.app_context():
    print("=" * 80)
    print("DIAGNOSTICO DE CAMPOS PROBLEMATICOS")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ============================================================================
    # PROBLEMA 1: doc_causado_por = 'admin'
    # ============================================================================
    print("PROBLEMA 1: Campo 'doc_causado_por' mostrando 'admin'")
    print("-" * 80)
    
    count_admin = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.doc_causado_por == 'admin'
    ).count()
    print(f"Total con doc_causado_por='admin': {count_admin:,}")
    
    count_blank = MaestroDianVsErp.query.filter(
        or_(
            MaestroDianVsErp.doc_causado_por == None,
            MaestroDianVsErp.doc_causado_por == ''
        )
    ).count()
    print(f"Total con doc_causado_por en blanco: {count_blank:,}")
    
    count_correcto = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.doc_causado_por.like('%-%-%')
    ).count()
    print(f"Total con formato correcto (C.O. - Usuario - Nro Doc): {count_correcto:,}")
    
    # Ejemplos con 'admin'
    print("\nEjemplos de registros con 'admin':")
    ejemplos_admin = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.doc_causado_por == 'admin'
    ).limit(5).all()
    
    for reg in ejemplos_admin:
        print(f"  {reg.nit_emisor} | {reg.prefijo}-{reg.folio} | Fecha: {reg.fecha_emision}")
        print(f"    Razon: {reg.razon_social}")
        print(f"    doc_causado_por: '{reg.doc_causado_por}' | Modulo: {reg.modulo}")
        print()
    
    print()
    
    # ============================================================================
    # PROBLEMA 2: Razon Social en blanco
    # ============================================================================
    print("PROBLEMA 2: Razon Social en blanco")
    print("-" * 80)
    
    count_sin_razon = MaestroDianVsErp.query.filter(
        or_(
            MaestroDianVsErp.razon_social == None,
            MaestroDianVsErp.razon_social == '',
            MaestroDianVsErp.razon_social == 'None'
        )
    ).count()
    print(f"Total sin razon social: {count_sin_razon:,}")
    
    # Ejemplos
    print("\nEjemplos de registros sin razon social:")
    ejemplos_sin_razon = MaestroDianVsErp.query.filter(
        or_(
            MaestroDianVsErp.razon_social == None,
            MaestroDianVsErp.razon_social == '',
            MaestroDianVsErp.razon_social == 'None'
        )
    ).limit(5).all()
    
    for reg in ejemplos_sin_razon:
        print(f"  {reg.nit_emisor} | {reg.prefijo}-{reg.folio}")
        print(f"    Razon: '{reg.razon_social}' | Tipo Tercero: {reg.tipo_tercero}")
        print()
    
    print()
    
    # ============================================================================
    # PROBLEMA 3: Estado Aprobacion incoherente con acuses
    # ============================================================================
    print("PROBLEMA 3: Coherencia estado_aprobacion vs acuses_recibidos")
    print("-" * 80)
    
    # Consulta de incoherencias
    incoherentes = MaestroDianVsErp.query.filter(
        or_(
            and_(MaestroDianVsErp.estado_aprobacion == 'Pendiente', 
                 MaestroDianVsErp.acuses_recibidos != 0),
            and_(MaestroDianVsErp.estado_aprobacion == 'Acuse Recibido', 
                 MaestroDianVsErp.acuses_recibidos != 1),
            and_(MaestroDianVsErp.estado_aprobacion == 'Acuse Bien/Servicio', 
                 MaestroDianVsErp.acuses_recibidos != 1),
            and_(MaestroDianVsErp.estado_aprobacion == 'Rechazada', 
                 MaestroDianVsErp.acuses_recibidos != 1),
            and_(MaestroDianVsErp.estado_aprobacion == 'Aceptacion Expresa', 
                 MaestroDianVsErp.acuses_recibidos != 2),
            and_(MaestroDianVsErp.estado_aprobacion == 'Aceptacion Tacita', 
                 MaestroDianVsErp.acuses_recibidos != 2)
        )
    ).count()
    
    print(f"Total registros con incoherencia: {incoherentes:,}")
    
    if incoherentes > 0:
        print("\nINCOHERENCIAS ENCONTRADAS - Ejemplos:")
        ejemplos_incoh = MaestroDianVsErp.query.filter(
            or_(
                and_(MaestroDianVsErp.estado_aprobacion == 'Pendiente', 
                     MaestroDianVsErp.acuses_recibidos != 0),
                and_(MaestroDianVsErp.estado_aprobacion == 'Acuse Recibido', 
                     MaestroDianVsErp.acuses_recibidos != 1),
                and_(MaestroDianVsErp.estado_aprobacion == 'Acuse Bien/Servicio', 
                     MaestroDianVsErp.acuses_recibidos != 1),
                and_(MaestroDianVsErp.estado_aprobacion == 'Rechazada', 
                     MaestroDianVsErp.acuses_recibidos != 1),
                and_(MaestroDianVsErp.estado_aprobacion == 'Aceptacion Expresa', 
                     MaestroDianVsErp.acuses_recibidos != 2),
                and_(MaestroDianVsErp.estado_aprobacion == 'Aceptacion Tacita', 
                     MaestroDianVsErp.acuses_recibidos != 2)
            )
        ).limit(10).all()
        
        for reg in ejemplos_incoh:
            print(f"  {reg.nit_emisor} | {reg.prefijo}-{reg.folio}")
            print(f"    Estado: '{reg.estado_aprobacion}' | Acuses: {reg.acuses_recibidos}")
            
            # Validar qué debería ser
            if reg.estado_aprobacion == 'Pendiente':
                print(f"    ERROR: Deberia tener 0 acuses, tiene {reg.acuses_recibidos}")
            elif reg.estado_aprobacion in ['Acuse Recibido', 'Acuse Bien/Servicio', 'Rechazada']:
                print(f"    ERROR: Deberia tener 1 acuse, tiene {reg.acuses_recibidos}")
            elif reg.estado_aprobacion in ['Aceptacion Expresa', 'Aceptacion Tacita']:
                print(f"    ERROR: Deberia tener 2 acuses, tiene {reg.acuses_recibidos}")
            print()
    else:
        print("EXITO: NO hay incoherencias")
    
    print()
    
    # ============================================================================
    # DISTRIBUCION DE ESTADOS
    # ============================================================================
    print("DISTRIBUCION DE ESTADOS")
    print("-" * 80)
    
    print("\nEstado Aprobacion:")
    estados_aprob = db.session.query(
        MaestroDianVsErp.estado_aprobacion,
        func.count(MaestroDianVsErp.id).label('cantidad')
    ).group_by(MaestroDianVsErp.estado_aprobacion).order_by(func.count(MaestroDianVsErp.id).desc()).all()
    
    for estado, count in estados_aprob:
        print(f"  {estado or '(NULL)'}: {count:,} registros")
    
    print("\nEstado Contable:")
    estados_cont = db.session.query(
        MaestroDianVsErp.estado_contable,
        func.count(MaestroDianVsErp.id).label('cantidad')
    ).group_by(MaestroDianVsErp.estado_contable).order_by(func.count(MaestroDianVsErp.id).desc()).all()
    
    for estado, count in estados_cont:
        print(f"  {estado or '(NULL)'}: {count:,} registros")
    
    print()
    
    # ============================================================================
    # RESUMEN FINAL
    # ============================================================================
    total_registros = MaestroDianVsErp.query.count()
    
    print("=" * 80)
    print("RESUMEN DE PROBLEMAS IDENTIFICADOS")
    print("=" * 80)
    print(f"Total registros en BD: {total_registros:,}")
    print()
    print(f"1. doc_causado_por='admin': {count_admin:,} registros ({count_admin/total_registros*100:.3f}%)")
    print(f"2. doc_causado_por en blanco: {count_blank:,} registros ({count_blank/total_registros*100:.2f}%)")
    print(f"3. doc_causado_por correcto: {count_correcto:,} registros ({count_correcto/total_registros*100:.2f}%)")
    print()
    print(f"4. Razon social en blanco: {count_sin_razon:,} registros ({count_sin_razon/total_registros*100:.2f}%)")
    print()
    print(f"5. Incoherencias estado_aprobacion vs acuses: {incoherentes:,} registros ({incoherentes/total_registros*100:.3f}%)")
    print()
    print("=" * 80)
