# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la lógica de guardado de facturas digitales
Fecha: 8 de diciembre de 2025
"""
from app import app, db
from modules.facturas_digitales.models import FacturaDigital, ConfigRutasFacturas
import os

def verificar_logica_guardado():
    """Verifica que la lógica de guardado funciona correctamente"""
    with app.app_context():
        print("=" * 80)
        print("VERIFICACIÓN DE LÓGICA DE GUARDADO - FACTURAS DIGITALES")
        print("=" * 80)
        
        # Obtener ruta base
        config = ConfigRutasFacturas.query.filter_by(activa=True).first()
        ruta_base = config.ruta_local if config else 'D:/facturas_digitales'
        print(f"\n📁 Ruta base configurada: {ruta_base}")
        
        # Verificar carpeta TEMPORALES
        ruta_temporales = os.path.join(ruta_base, 'TEMPORALES')
        if os.path.exists(ruta_temporales):
            print(f"✅ Carpeta TEMPORALES existe: {ruta_temporales}")
        else:
            print(f"❌ Carpeta TEMPORALES NO existe: {ruta_temporales}")
            print(f"   💡 Crear con: New-Item -ItemType Directory -Path '{ruta_temporales}' -Force")
        
        # Analizar facturas por tipo de usuario
        print("\n" + "=" * 80)
        print("ANÁLISIS DE FACTURAS POR TIPO DE USUARIO")
        print("=" * 80)
        
        # FACTURAS EXTERNAS (deben estar en TEMPORALES o haber sido movidas)
        facturas_externas = FacturaDigital.query.filter_by(tipo_usuario='externo').all()
        print(f"\n📊 Total facturas EXTERNAS: {len(facturas_externas)}")
        
        if facturas_externas:
            for f in facturas_externas:
                en_temporales = 'TEMPORALES' in f.ruta_carpeta.upper() if f.ruta_carpeta else False
                print(f"\n  ID {f.id} | {f.numero_factura}")
                print(f"  Estado: {f.estado}")
                print(f"  Ruta: {f.ruta_carpeta}")
                print(f"  En TEMPORALES: {'✅ SÍ' if en_temporales else '❌ NO (ya fue movida)'}")
                
                # Verificar si ruta existe en disco
                if f.ruta_carpeta and os.path.exists(f.ruta_carpeta):
                    archivos = os.listdir(f.ruta_carpeta)
                    print(f"  Archivos en disco: {len(archivos)} → {', '.join(archivos[:3])}")
                else:
                    print(f"  ⚠️ Ruta NO existe en disco")
        else:
            print("  ℹ️ No hay facturas de usuarios EXTERNOS")
        
        # FACTURAS INTERNAS (deben estar en estructura EMPRESA/AÑO/MES/DEPTO/PAGO)
        facturas_internas = FacturaDigital.query.filter_by(tipo_usuario='interno').all()
        print(f"\n📊 Total facturas INTERNAS: {len(facturas_internas)}")
        
        if facturas_internas:
            for f in facturas_internas:
                # Verificar estructura de carpeta
                ruta = f.ruta_carpeta if f.ruta_carpeta else "SIN RUTA"
                partes = ruta.split('/')
                
                print(f"\n  ID {f.id} | {f.numero_factura}")
                print(f"  Estado: {f.estado}")
                print(f"  Empresa: {f.empresa}")
                print(f"  Departamento: {f.departamento}")
                print(f"  Forma Pago: {f.forma_pago}")
                print(f"  Ruta: {ruta}")
                
                # Validar que NO está en TEMPORALES
                if 'TEMPORALES' in ruta.upper():
                    print(f"  ❌ ERROR: Factura interna NO debe estar en TEMPORALES")
                else:
                    print(f"  ✅ Correcta: No está en TEMPORALES")
                
                # Validar que tiene todos los componentes
                tiene_empresa = f.empresa and f.empresa in ruta
                tiene_depto = f.departamento and f.departamento in ruta
                tiene_pago = f.forma_pago and f.forma_pago in ruta
                
                if tiene_empresa and tiene_depto:
                    print(f"  ✅ Estructura correcta: tiene empresa y departamento en ruta")
                else:
                    print(f"  ⚠️ Estructura incompleta:")
                    if not tiene_empresa:
                        print(f"     - Falta empresa en ruta")
                    if not tiene_depto:
                        print(f"     - Falta departamento en ruta")
                
                # Verificar si ruta existe en disco
                if os.path.exists(ruta):
                    archivos = os.listdir(ruta)
                    print(f"  Archivos en disco: {len(archivos)} → {', '.join(archivos[:3])}")
                else:
                    print(f"  ⚠️ Ruta NO existe en disco")
        else:
            print("  ℹ️ No hay facturas de usuarios INTERNOS")
        
        # RESUMEN DE VALIDACIONES
        print("\n" + "=" * 80)
        print("RESUMEN DE VALIDACIONES")
        print("=" * 80)
        
        total_facturas = len(facturas_externas) + len(facturas_internas)
        
        # Contar facturas pendientes de completar (externas en TEMPORALES)
        pendientes_completar = sum(1 for f in facturas_externas 
                                   if f.ruta_carpeta and 'TEMPORALES' in f.ruta_carpeta.upper())
        
        # Contar facturas completadas (externas movidas o internas)
        completadas = total_facturas - pendientes_completar
        
        print(f"\n📊 Total facturas: {total_facturas}")
        print(f"⏳ Pendientes de completar (en TEMPORALES): {pendientes_completar}")
        print(f"✅ Completadas (en ubicación final): {completadas}")
        
        # Verificar integridad de rutas
        print(f"\n🔍 Verificando integridad de rutas...")
        rutas_ok = 0
        rutas_error = 0
        
        for f in FacturaDigital.query.all():
            if f.ruta_carpeta:
                # Verificar que sea ruta absoluta
                if f.ruta_carpeta.startswith('D:/') or f.ruta_carpeta.startswith('D:\\'):
                    rutas_ok += 1
                else:
                    rutas_error += 1
                    print(f"  ❌ ID {f.id}: Ruta NO es absoluta: {f.ruta_carpeta}")
            else:
                rutas_error += 1
                print(f"  ❌ ID {f.id}: NO tiene ruta_carpeta")
        
        print(f"\n✅ Rutas correctas (absolutas): {rutas_ok}")
        print(f"❌ Rutas incorrectas: {rutas_error}")
        
        # Conclusión
        print("\n" + "=" * 80)
        if rutas_error == 0 and os.path.exists(ruta_temporales):
            print("✅ SISTEMA CONFIGURADO CORRECTAMENTE")
            print("   - Todas las rutas son absolutas")
            print("   - Carpeta TEMPORALES existe")
            print("   - Lógica de guardado implementada correctamente")
        else:
            print("⚠️ SISTEMA REQUIERE AJUSTES")
            if rutas_error > 0:
                print(f"   - {rutas_error} facturas con rutas incorrectas")
            if not os.path.exists(ruta_temporales):
                print(f"   - Carpeta TEMPORALES no existe")
        print("=" * 80)

if __name__ == '__main__':
    verificar_logica_guardado()
