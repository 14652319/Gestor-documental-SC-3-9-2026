"""
BORRAR DATOS DE 2026 Y CONSERVAR 2025
======================================
Este script elimina SOLO los registros del año 2026
y mantiene intactos todos los datos de 2025 y años anteriores
"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from extensions import db
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import extract
from datetime import datetime

with app.app_context():
    print("=" * 100)
    print("BORRAR DATOS DE 2026 - CONSERVAR 2025")
    print("=" * 100)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ============================================================================
    # PASO 1: VERIFICAR DATOS ACTUALES
    # ============================================================================
    print("📊 PASO 1: Verificando datos actuales...")
    print("-" * 100)
    
    total_registros = MaestroDianVsErp.query.count()
    registros_2025 = MaestroDianVsErp.query.filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2025
    ).count()
    registros_2026 = MaestroDianVsErp.query.filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2026
    ).count()
    otros_años = total_registros - registros_2025 - registros_2026
    
    print(f"Total registros en BD: {total_registros:,}")
    print(f"  - Año 2025: {registros_2025:,} registros ✅ (SE CONSERVARÁN)")
    print(f"  - Año 2026: {registros_2026:,} registros ❌ (SE ELIMINARÁN)")
    print(f"  - Otros años: {otros_años:,} registros ✅ (SE CONSERVARÁN)")
    print()
    
    # ============================================================================
    # PASO 2: CONFIRMAR OPERACIÓN
    # ============================================================================
    print("⚠️ ADVERTENCIA:")
    print("-" * 100)
    print(f"Esta operación eliminará PERMANENTEMENTE {registros_2026:,} registros del año 2026")
    print(f"Los {registros_2025:,} registros de 2025 NO se afectarán")
    print()
    
    # Mostrar ejemplos de lo que se eliminará
    print("Ejemplos de registros que se eliminarán (primeros 5):")
    ejemplos = MaestroDianVsErp.query.filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2026
    ).limit(5).all()
    
    for reg in ejemplos:
        print(f"  - {reg.nit_emisor} | {reg.prefijo}-{reg.folio} | Fecha: {reg.fecha_emision} | Razón: {reg.razon_social}")
    
    print()
    print("¿Desea continuar? (escriba 'SI' en mayúsculas para confirmar)")
    confirmacion = input("Confirmación: ").strip()
    
    if confirmacion != 'SI':
        print()
        print("❌ Operación CANCELADA por el usuario")
        print("No se eliminó ningún registro")
        print()
        exit(0)
    
    print()
    
    # ============================================================================
    # PASO 3: ELIMINAR REGISTROS DE 2026
    # ============================================================================
    print("🗑️ PASO 3: Eliminando registros de 2026...")
    print("-" * 100)
    
    try:
        # Contar antes de eliminar
        antes = MaestroDianVsErp.query.count()
        
        # ELIMINAR registros de 2026
        eliminados = MaestroDianVsErp.query.filter(
            extract('year', MaestroDianVsErp.fecha_emision) == 2026
        ).delete(synchronize_session=False)
        
        # COMMIT
        db.session.commit()
        
        # Contar después de eliminar
        despues = MaestroDianVsErp.query.count()
        
        print(f"✅ Eliminación completada exitosamente")
        print()
        print(f"Registros eliminados: {eliminados:,}")
        print(f"Total antes: {antes:,}")
        print(f"Total después: {despues:,}")
        print(f"Diferencia: {antes - despues:,}")
        print()
        
    except Exception as e:
        print(f"❌ ERROR durante la eliminación: {e}")
        db.session.rollback()
        print("Se hizo ROLLBACK - No se eliminó ningún registro")
        print()
        exit(1)
    
    # ============================================================================
    # PASO 4: VERIFICAR RESULTADO
    # ============================================================================
    print("✅ PASO 4: Verificando resultado...")
    print("-" * 100)
    
    total_final = MaestroDianVsErp.query.count()
    registros_2025_final = MaestroDianVsErp.query.filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2025
    ).count()
    registros_2026_final = MaestroDianVsErp.query.filter(
        extract('year', MaestroDianVsErp.fecha_emision) == 2026
    ).count()
    
    print(f"Total registros FINAL: {total_final:,}")
    print(f"  - Año 2025: {registros_2025_final:,} registros ✅")
    print(f"  - Año 2026: {registros_2026_final:,} registros")
    print()
    
    if registros_2026_final == 0:
        print("✅ ÉXITO: Todos los registros de 2026 fueron eliminados")
        print(f"✅ Se conservaron {registros_2025_final:,} registros de 2025")
    else:
        print(f"⚠️ ADVERTENCIA: Aún quedan {registros_2026_final:,} registros de 2026")
    
    print()
    
    # ============================================================================
    # PASO 5: RESUMEN FINAL
    # ============================================================================
    print("=" * 100)
    print("📊 RESUMEN FINAL")
    print("=" * 100)
    print()
    print(f"✅ Operación completada")
    print(f"🗑️ Registros eliminados: {eliminados:,}")
    print(f"💾 Registros conservados: {total_final:,}")
    print()
    print("🎯 PRÓXIMO PASO:")
    print("   1. Ir a: http://127.0.0.1:8099/dian_vs_erp/cargar_archivos")
    print("   2. Subir los 4 archivos de 2026:")
    print("      - Dian.xlsx (archivo DIAN)")
    print("      - acuses.xlsx (archivo de ACUSES)")
    print("      - erp comercial.xlsx")
    print("      - erp financiero.xlsx")
    print("   3. Click en 'Procesar & Consolidar'")
    print()
    print("=" * 100)
