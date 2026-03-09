"""
Script de validación de carga DIAN
Verifica que las columnas se lean correctamente después de subir el archivo
"""

from extensions import db
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import datetime, date

def validar_carga_2026():
    """Valida que los datos de 2026 se hayan cargado correctamente"""
    
    with app.app_context():
        print("=" * 80)
        print("📊 VALIDACIÓN DE CARGA DIAN - AÑO 2026")
        print("=" * 80)
        
        # Contar total de registros 2026
        total_2026 = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1),
            MaestroDianVsErp.fecha_emision <= date(2026, 12, 31)
        ).count()
        
        print(f"\n📋 Total registros 2026: {total_2026:,}")
        
        if total_2026 == 0:
            print("\n⚠️ NO HAY DATOS DE 2026")
            print("Asegúrate de haber subido el archivo Dian.xlsx")
            return
        
        # Validar FECHAS (no todas deben ser iguales)
        fechas_unicas = db.session.query(MaestroDianVsErp.fecha_emision).filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
        ).distinct().count()
        
        print(f"\n📅 VALIDACIÓN DE FECHAS:")
        print(f"   Fechas únicas: {fechas_unicas:,}")
        
        if fechas_unicas == 1:
            # Todas las fechas son iguales (PROBLEMA)
            fecha_unica = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
            ).first().fecha_emision
            print(f"   ❌ PROBLEMA: Todas las fechas son '{fecha_unica}'")
            print(f"   Esto indica que no se leyó correctamente 'Fecha Emisión' del Excel")
        else:
            # Hay variedad de fechas (CORRECTO)
            print(f"   ✅ CORRECTO: Hay variedad de fechas")
            
            # Mostrar muestra de fechas
            muestra_fechas = db.session.query(
                MaestroDianVsErp.fecha_emision,
                db.func.count(MaestroDianVsErp.id).label('cantidad')
            ).filter(
                MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
            ).group_by(MaestroDianVsErp.fecha_emision).limit(10).all()
            
            print("\n   Muestra de fechas encontradas:")
            for fecha, cantidad in muestra_fechas:
                print(f"     • {fecha}: {cantidad:,} registros")
        
        # Validar VALORES (no todos deben ser 0)
        valores_cero = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1),
            db.or_(
                MaestroDianVsErp.valor == 0,
                MaestroDianVsErp.valor.is_(None)
            )
        ).count()
        
        valores_positivos = total_2026 - valores_cero
        porcentaje_positivos = (valores_positivos / total_2026 * 100) if total_2026 > 0 else 0
        
        print(f"\n💰 VALIDACIÓN DE VALORES:")
        print(f"   Registros con valor > 0: {valores_positivos:,} ({porcentaje_positivos:.1f}%)")
        print(f"   Registros con valor = 0: {valores_cero:,} ({100-porcentaje_positivos:.1f}%)")
        
        if porcentaje_positivos < 50:
            print(f"   ❌ PROBLEMA: Muy pocos registros con valor > 0")
            print(f"   Esto indica que no se leyó correctamente 'Total' del Excel")
        else:
            print(f"   ✅ CORRECTO: Mayoría de registros tienen valores")
            
            # Mostrar estadísticas de valores
            stats = db.session.query(
                db.func.min(MaestroDianVsErp.valor).label('minimo'),
                db.func.max(MaestroDianVsErp.valor).label('maximo'),
                db.func.avg(MaestroDianVsErp.valor).label('promedio')
            ).filter(
                MaestroDianVsErp.fecha_emision >= date(2026, 1, 1),
                MaestroDianVsErp.valor > 0
            ).first()
            
            if stats:
                print(f"\n   Estadísticas de valores:")
                print(f"     • Mínimo: ${stats.minimo:,.2f}")
                print(f"     • Máximo: ${stats.maximo:,.2f}")
                print(f"     • Promedio: ${stats.promedio:,.2f}")
        
        # Validar FORMA DE PAGO
        formas_pago = db.session.query(
            MaestroDianVsErp.forma_pago,
            db.func.count(MaestroDianVsErp.id).label('cantidad')
        ).filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
        ).group_by(MaestroDianVsErp.forma_pago).all()
        
        print(f"\n💳 FORMA DE PAGO:")
        for forma, cantidad in formas_pago:
            porcentaje = (cantidad / total_2026 * 100) if total_2026 > 0 else 0
            forma_texto = "Contado" if forma == "1" else "Crédito" if forma == "2" else forma
            print(f"   • {forma_texto}: {cantidad:,} ({porcentaje:.1f}%)")
        
        # Validar CUFE (debe tener contenido)
        con_cufe = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1),
            MaestroDianVsErp.cufe.isnot(None),
            MaestroDianVsErp.cufe != ''
        ).count()
        
        porcentaje_cufe = (con_cufe / total_2026 * 100) if total_2026 > 0 else 0
        
        print(f"\n🔐 CUFE/CUDE:")
        print(f"   Registros con CUFE: {con_cufe:,} ({porcentaje_cufe:.1f}%)")
        
        if porcentaje_cufe < 80:
            print(f"   ⚠️ ADVERTENCIA: Pocos registros tienen CUFE")
        else:
            print(f"   ✅ CORRECTO: Mayoría tienen CUFE")
        
        # Validar TIPO DOCUMENTO
        tipos_documento = db.session.query(
            MaestroDianVsErp.tipo_documento,
            db.func.count(MaestroDianVsErp.id).label('cantidad')
        ).filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1)
        ).group_by(MaestroDianVsErp.tipo_documento).all()
        
        print(f"\n📄 TIPO DE DOCUMENTO:")
        for tipo, cantidad in tipos_documento:
            porcentaje = (cantidad / total_2026 * 100) if total_2026 > 0 else 0
            print(f"   • {tipo or '(sin tipo)'}: {cantidad:,} ({porcentaje:.1f}%)")
        
        # Validar MÓDULO (ERP)
        con_modulo = MaestroDianVsErp.query.filter(
            MaestroDianVsErp.fecha_emision >= date(2026, 1, 1),
            MaestroDianVsErp.modulo.isnot(None),
            MaestroDianVsErp.modulo != ''
        ).count()
        
        porcentaje_modulo = (con_modulo / total_2026 * 100) if total_2026 > 0 else 0
        
        print(f"\n🏢 INTEGRACIÓN ERP:")
        print(f"   Registros con módulo asignado: {con_modulo:,} ({porcentaje_modulo:.1f}%)")
        print(f"   Registros sin módulo: {total_2026 - con_modulo:,} ({100-porcentaje_modulo:.1f}%)")
        
        if con_modulo > 0:
            modulos = db.session.query(
                MaestroDianVsErp.modulo,
                db.func.count(MaestroDianVsErp.id).label('cantidad')
            ).filter(
                MaestroDianVsErp.fecha_emision >= date(2026, 1, 1),
                MaestroDianVsErp.modulo.isnot(None)
            ).group_by(MaestroDianVsErp.modulo).all()
            
            print("\n   Por módulo:")
            for modulo, cantidad in modulos:
                print(f"     • {modulo}: {cantidad:,}")
        
        # RESUMEN FINAL
        print("\n" + "=" * 80)
        print("🎯 RESUMEN DE VALIDACIÓN")
        print("=" * 80)
        
        problemas = []
        advertencias = []
        
        if fechas_unicas == 1:
            problemas.append("❌ CRÍTICO: Todas las fechas son iguales")
        
        if porcentaje_positivos < 50:
            problemas.append("❌ CRÍTICO: Mayoría de valores en 0")
        
        if porcentaje_cufe < 50:
            advertencias.append("⚠️ ADVERTENCIA: Pocos registros con CUFE")
        
        if porcentaje_modulo < 10:
            advertencias.append("⚠️ ADVERTENCIA: Muy pocos registros con módulo ERP")
        
        if len(problemas) == 0 and len(advertencias) == 0:
            print("\n✅ ¡TODO CORRECTO! Los datos se cargaron exitosamente")
            print("\n   El archivo Excel se leyó correctamente:")
            print("   • Fechas variadas ✅")
            print("   • Valores > 0 ✅")
            print("   • CUFE presente ✅")
            print("   • Forma de pago correcta ✅")
        else:
            if problemas:
                print("\n🚨 PROBLEMAS CRÍTICOS ENCONTRADOS:\n")
                for p in problemas:
                    print(f"   {p}")
                print("\n   ACCIÓN REQUERIDA:")
                print("   1. Eliminar datos de 2026 en /dian_vs_erp/configuracion")
                print("   2. Verificar que el archivo Excel tenga las columnas correctas")
                print("   3. Volver a subir el archivo")
            
            if advertencias:
                print("\n⚠️ ADVERTENCIAS:\n")
                for a in advertencias:
                    print(f"   {a}")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    validar_carga_2026()
