"""
Monitorear el progreso de la carga en tiempo real
"""

from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import func
from datetime import datetime, timedelta
import time

with app.app_context():
    print("\n" + "="*80)
    print("📊 MONITOREO DE CARGA EN TIEMPO REAL")
    print("="*80 + "\n")
    
    # Obtener conteo inicial
    ahora = datetime.now()
    hace_5_min = ahora - timedelta(minutes=5)
    
    print(f"⏰ Hora actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Registros insertados en los últimos 5 minutos
    print("📈 REGISTROS INSERTADOS (ÚLTIMOS 5 MINUTOS):")
    print("-" * 80)
    
    registros_5min = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_registro >= hace_5_min
    ).count()
    
    print(f"   Total registros nuevos: {registros_5min:,}")
    
    if registros_5min > 0:
        # Velocidad de inserción
        velocidad = registros_5min / 5  # registros por minuto
        print(f"   🚀 Velocidad: {velocidad:.1f} registros/minuto")
        
        # Último registro insertado
        ultimo_reg = MaestroDianVsErp.query.order_by(
            MaestroDianVsErp.fecha_registro.desc()
        ).first()
        
        if ultimo_reg:
            tiempo_ultimo = (ahora - ultimo_reg.fecha_registro).total_seconds()
            print(f"\n   📄 Último registro insertado hace {tiempo_ultimo:.0f} segundos:")
            print(f"      NIT: {ultimo_reg.nit_emisor}")
            print(f"      Razón Social: {ultimo_reg.razon_social or '(Sin razón social)'}")
            print(f"      Prefijo-Folio: {ultimo_reg.prefijo}-{ultimo_reg.folio}")
            print(f"      Fecha Emisión: {ultimo_reg.fecha_emision}")
            print(f"      Tipo Tercero: {ultimo_reg.tipo_tercero or '(Sin tipo)'}")
    
    # 2. Registros por minuto (últimos 5 minutos)
    print(f"\n\n📊 DISTRIBUCIÓN POR MINUTO:")
    print("-" * 80)
    
    for i in range(5, 0, -1):
        inicio = ahora - timedelta(minutes=i)
        fin = ahora - timedelta(minutes=i-1)
        
        count = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_registro >= inicio,
            MaestroDianVsErp.fecha_registro < fin
        ).count()
        
        barra = "█" * min(int(count/10), 50)
        print(f"   Hace {i} min: {count:>5} registros {barra}")
    
    # 3. Total acumulado hoy
    print(f"\n\n📅 RESUMEN DEL DÍA (HOY):")
    print("-" * 80)
    
    hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    registros_hoy = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.fecha_registro >= hoy_inicio
    ).count()
    
    print(f"   Total registros insertados hoy: {registros_hoy:,}")
    
    # Desglose por hora
    print(f"\n   📊 Distribución por hora (hoy):")
    
    horas_con_datos = db.session.query(
        func.date_trunc('hour', MaestroDianVsErp.fecha_registro).label('hora'),
        func.count(MaestroDianVsErp.id).label('total')
    ).filter(
        MaestroDianVsErp.fecha_registro >= hoy_inicio
    ).group_by('hora').order_by('hora').all()
    
    for hora, total in horas_con_datos:
        hora_str = hora.strftime('%H:%M')
        barra = "█" * min(int(total/100), 50)
        print(f"      {hora_str}: {total:>6,} registros {barra}")
    
    # 4. Estado de la carga actual
    print(f"\n\n🎯 ESTADO DE LA CARGA:")
    print("-" * 80)
    
    if registros_5min > 0:
        print(f"   ✅ CARGA ACTIVA - Sistema insertando datos")
        if velocidad < 50:
            print(f"   ⚠️  Velocidad baja ({velocidad:.1f} reg/min) - Normal para archivos grandes")
        elif velocidad < 500:
            print(f"   ✅ Velocidad normal ({velocidad:.1f} reg/min)")
        else:
            print(f"   🚀 Velocidad alta ({velocidad:.1f} reg/min)")
        
        # Estimación de tiempo restante (asumiendo 105 facturas totales)
        # Nota: Este es un estimado aproximado
        total_esperado = 105  # facturas según el usuario
        if velocidad > 0:
            tiempo_restante = (total_esperado - registros_5min) / velocidad
            if tiempo_restante > 0:
                print(f"   ⏱️  Tiempo estimado restante: {tiempo_restante:.1f} minutos")
    else:
        print(f"   ⏸️  NO hay carga activa en los últimos 5 minutos")
        print(f"   💡 La carga puede haber finalizado o está pausada")
    
    # 5. Verificar si hay problemas
    print(f"\n\n🔍 VERIFICACIÓN DE CALIDAD:")
    print("-" * 80)
    
    if registros_5min > 0:
        # Registros con datos faltantes en últimos 5 min
        sin_razon_social = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_registro >= hace_5_min,
            db.or_(
                MaestroDianVsErp.razon_social == None,
                MaestroDianVsErp.razon_social == '',
                MaestroDianVsErp.razon_social == 'None'
            )
        ).count()
        
        sin_tipo_tercero = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_registro >= hace_5_min,
            db.or_(
                MaestroDianVsErp.tipo_tercero == None,
                MaestroDianVsErp.tipo_tercero == '',
                MaestroDianVsErp.tipo_tercero == 'None'
            )
        ).count()
        
        porcentaje_completos = ((registros_5min - sin_razon_social) / registros_5min * 100) if registros_5min > 0 else 0
        
        print(f"   Registros completos: {registros_5min - sin_razon_social:,} ({porcentaje_completos:.1f}%)")
        print(f"   Sin razón social: {sin_razon_social:,}")
        print(f"   Sin tipo tercero: {sin_tipo_tercero:,}")
        
        if porcentaje_completos >= 95:
            print(f"\n   ✅ CALIDAD EXCELENTE - Datos completos")
        elif porcentaje_completos >= 80:
            print(f"\n   ⚠️  CALIDAD ACEPTABLE - Algunos datos faltantes")
        else:
            print(f"\n   ❌ CALIDAD BAJA - Revisar archivo CSV")

print("\n" + "="*80 + "\n")
