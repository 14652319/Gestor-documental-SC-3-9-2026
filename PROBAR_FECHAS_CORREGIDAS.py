"""
Script para procesar CSV de prueba y verificar fechas
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("\n" + "="*80)
print("🧪 PROCESANDO CSV DE PRUEBA - VERIFICACIÓN DE FECHAS")
print("="*80 + "\n")

# Importar Flask app
from app import app
from extensions import db
from modules.dian_vs_erp.routes import actualizar_maestro

# Ejecutar dentro del contexto de Flask
with app.app_context():
    print("📁 CSV de prueba: uploads/dian/PRUEBA_FECHAS_ENERO_FEB_2025.csv")
    print("   14 facturas con fechas de enero-febrero 2025\n")
    
    # Verificar tabla antes
    from modules.dian_vs_erp.models import MaestroDianVsErp
    from sqlalchemy import func
    
    registros_antes = db.session.query(func.count(MaestroDianVsErp.id)).scalar()
    print(f"📊 Registros en tabla ANTES: {registros_antes}\n")
    
    print("-" * 80)
    print("⚙️  EJECUTANDO actualizar_maestro()...")
    print("-" * 80 + "\n")
    
    # Procesar
    resultado = actualizar_maestro()
    
    print("\n" + "-" * 80)
    print(f"✅ RESULTADO: {resultado}")
    print("-" * 80 + "\n")
    
    # Verificar tabla después
    registros_despues = db.session.query(func.count(MaestroDianVsErp.id)).scalar()
    print(f"📊 Registros en tabla DESPUÉS: {registros_despues}")
    print(f"   Nuevos registros agregados: {registros_despues - registros_antes}\n")
    
    # Mostrar fechas en la tabla
    resultado_fechas = db.session.query(
        MaestroDianVsErp.fecha_emision,
        func.count(MaestroDianVsErp.id).label('registros')
    ).group_by(
        MaestroDianVsErp.fecha_emision
    ).order_by(
        MaestroDianVsErp.fecha_emision
    ).all()
    
    print("=" * 80)
    print("📅 FECHAS CARGADAS EN LA TABLA")
    print("=" * 80)
    
    if not resultado_fechas:
        print("⚠️  No hay registros con fecha_emision")
    else:
        print(f"\n{'FECHA':<15} | {'REGISTROS':>10} | {'ESPERADO':>10}")
        print("-" * 45)
        
        # Definir fechas esperadas
        fechas_esperadas = {
            '2025-01-02': 1, '2025-01-05': 1, '2025-01-10': 1, '2025-01-15': 1,
            '2025-01-20': 1, '2025-01-25': 1, '2025-01-30': 1,
            '2025-02-03': 1, '2025-02-08': 1, '2025-02-12': 1, '2025-02-15': 1,
            '2025-02-20': 1, '2025-02-25': 1, '2025-02-28': 1
        }
        
        # Mostrar fechas
        errores = 0
        for fecha, cantidad in resultado_fechas:
            fecha_str = str(fecha) if fecha else 'NULL'
            esperado = fechas_esperadas.get(fecha_str, '?')
            
            # Verificar si es correcto
            if fecha_str == 'NULL':
                icono = "⚠️ "
                errores += 1
            elif str(fecha).startswith('2026-02-17'):
                icono = "❌"
                errores += 1
            elif str(fecha).startswith('2025-'):
                icono = "✅"
            else:
                icono = "⚠️ "
                errores += 1
            
            print(f"{icono} {fecha_str:<15} | {cantidad:>10} | {str(esperado):>10}")
        
        print("-" * 45)
        print(f"{'TOTAL':<15} | {sum([c for _, c in resultado_fechas]):>10}")
        
        print("\n" + "=" * 80)
        if errores == 0:
            print("✅✅✅ ¡PERFECTO! TODAS LAS FECHAS SON CORRECTAS (2025-01-XX y 2025-02-XX)")
        else:
            print(f"⚠️  ADVERTENCIA: {errores} fecha(s) NULL o incorrecta(s)")
        print("=" * 80)

print("\n✅ Script completado\n")
