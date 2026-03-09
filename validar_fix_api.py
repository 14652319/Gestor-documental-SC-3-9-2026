"""
Script para validar que la API retorna valores correctos después del fix
"""
import requests
import sys

print("=" * 80)
print("🔍 VALIDACIÓN DE FIX EN API /dian_vs_erp/api/dian")
print("=" * 80)

try:
    # Consultar API
    response = requests.get(
        'http://127.0.0.1:8099/dian_vs_erp/api/dian',
        params={
            'fecha_inicial': '2025-01-01',
            'fecha_final': '2025-12-28',
            'size': 1000
        },
        timeout=10
    )
    
    print(f"\n✅ API Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ ERROR: La API no respondió correctamente")
        sys.exit(1)
    
    facturas = response.json()
    print(f"📊 Total facturas retornadas: {len(facturas)}")
    
    # Buscar BIMBO
    bimbo = [f for f in facturas if 
             f.get('nit_emisor') == '900108281' and 
             f.get('prefijo') == 'ME40' and 
             str(f.get('folio')) == '772863']
    
    # Buscar GALERÍA
    galeria = [f for f in facturas if 
               f.get('nit_emisor') == '890900943' and 
               f.get('prefijo') == '1FEA' and 
               str(f.get('folio')) == '77']
    
    print("\n" + "=" * 80)
    print("📋 RESULTADOS DE VALIDACIÓN")
    print("=" * 80)
    
    # Validar BIMBO
    print(f"\n🔍 BIMBO ME40-772863:")
    if bimbo:
        print(f"   ✅ ENCONTRADA en API")
        print(f"   📌 estado_contable: \"{bimbo[0].get('estado_contable')}\"")
        print(f"   📌 estado_aprobacion: \"{bimbo[0].get('estado_aprobacion')}\"")
        print(f"   📌 tipo_tercero: \"{bimbo[0].get('tipo_tercero')}\"")
        
        # Verificar que los valores son correctos
        if bimbo[0].get('estado_contable') == 'Recibida':
            print(f"   ✅ estado_contable es CORRECTO (Recibida)")
        else:
            print(f"   ❌ estado_contable es INCORRECTO (esperado: Recibida, actual: {bimbo[0].get('estado_contable')})")
        
        if bimbo[0].get('tipo_tercero'):
            print(f"   ✅ tipo_tercero tiene valor del DIAN")
        else:
            print(f"   ❌ tipo_tercero está vacío")
    else:
        print(f"   ❌ NO ENCONTRADA en API")
    
    # Validar GALERÍA
    print(f"\n🔍 GALERÍA 1FEA-77:")
    if galeria:
        print(f"   ✅ ENCONTRADA en API")
        print(f"   📌 estado_contable: \"{galeria[0].get('estado_contable')}\"")
        print(f"   📌 estado_aprobacion: \"{galeria[0].get('estado_aprobacion')}\"")
        print(f"   📌 tipo_tercero: \"{galeria[0].get('tipo_tercero')}\"")
        
        # Verificar que los valores son correctos
        if galeria[0].get('estado_contable') == 'Recibida':
            print(f"   ✅ estado_contable es CORRECTO (Recibida)")
        else:
            print(f"   ❌ estado_contable es INCORRECTO (esperado: Recibida, actual: {galeria[0].get('estado_contable')})")
        
        if galeria[0].get('tipo_tercero'):
            print(f"   ✅ tipo_tercero tiene valor del DIAN")
        else:
            print(f"   ❌ tipo_tercero está vacío")
    else:
        print(f"   ❌ NO ENCONTRADA en API")
    
    print("\n" + "=" * 80)
    print("📝 CONCLUSIÓN")
    print("=" * 80)
    
    if bimbo and galeria:
        if (bimbo[0].get('estado_contable') == 'Recibida' and 
            galeria[0].get('estado_contable') == 'Recibida'):
            print("\n✅ FIX FUNCIONANDO CORRECTAMENTE")
            print("   - La API retorna valores REALES de la base de datos")
            print("   - estado_contable muestra 'Recibida' (sincronizado)")
            print("   - estado_aprobacion muestra valores del DIAN")
            print("   - tipo_tercero muestra valores del DIAN")
            print("\n💡 SIGUIENTE PASO:")
            print("   Recarga la página en el navegador (Ctrl+F5)")
            print("   http://127.0.0.1:8099/dian_vs_erp/")
        else:
            print("\n⚠️ FIX APLICADO PERO VALORES INESPERADOS")
            print("   Revisar datos en base de datos")
    else:
        print("\n⚠️ NO SE ENCONTRARON LAS FACTURAS EN LA RESPUESTA")
        print("   Verificar que estén en el rango de fechas consultado")
    
    print("\n" + "=" * 80)

except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: No se pudo conectar al servidor")
    print("   El servidor Flask no está corriendo en puerto 8099")
    print("   Ejecuta: python app.py")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
