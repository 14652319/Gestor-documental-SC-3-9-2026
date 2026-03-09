"""
Script para diagnosticar la carga de archivos DIAN y verificar detección de columnas
"""
import requests
import os
import time

# URL del servidor
BASE_URL = "http://127.0.0.1:8099"

# Buscar archivo más reciente cargado
uploads_dir = "uploads/dian"
archivos = [f for f in os.listdir(uploads_dir) if f.endswith(('.csv', '.xlsx', '.xlsm'))]
if not archivos:
    print("❌ No hay archivos en uploads/dian")
    exit()

archivo_mas_reciente = max(
    [os.path.join(uploads_dir, f) for f in archivos],
    key=os.path.getctime
)

print(f"📁 Archivo más reciente: {os.path.basename(archivo_mas_reciente)}")

# Simular carga mediante API
print("\n🚀 Simulando carga de archivo mediante API...")
print(f"⏳ Esperando que el servidor procese...")
time.sleep(2)

# Consultar datos en la tabla
print("\n🔍 Consultando tabla maestro_dian_vs_erp...")
response = requests.get(f"{BASE_URL}/api/dian_vs_erp/maestro")

if response.status_code == 200:
    data = response.json()
    total = data.get('total', 0)
    registros = data.get('data', [])
    
    print(f"✅ Total registros en tabla: {total}")
    
    if registros:
        print("\n📊 PRIMER REGISTRO:")
        primer_registro = registros[0]
        for campo in ['nit_emisor', 'razon_social', 'fecha_emision', 'prefijo', 'folio', 'valor']:
            print(f"   {campo}: {primer_registro.get(campo)}")
        
        # Verificar valores
        valor_1 = registros[0].get('valor')
        print(f"\n💰 Valor del primer registro: {valor_1}")
        
        if valor_1 == 0 or valor_1 is None:
            print("   ❌ ERROR: El valor es 0 o NULL")
            print("   Esto significa que no se detecto la columna 'Total' correctamente")
        else:
            print(f"   ✅ CORRECTO: Valor detectado = {valor_1}")
        
        # Verificar fechas
        fecha_1 = registros[0].get('fecha_emision')
        print(f"\n📅 Fecha del primer registro: {fecha_1}")
        
        if fecha_1 and '2026-02-17' in fecha_1:
            print("   ❌ ERROR: Fecha es hoy (2026-02-17), no la del CSV")
        elif fecha_1 and '2025-01' in fecha_1:
            print("   ✅ CORRECTO: Fecha de enero 2025 detectada")
        else:
            print(f"   ⚠️  VERIFICAR: Fecha = {fecha_1}")
        
        if len(registros) >= 2:
            print("\n📊 SEGUNDO REGISTRO:")
            segundo_registro = registros[1]
            val_2 = segundo_registro.get('valor')
            fecha_2 = segundo_registro.get('fecha_emision')
            print(f"   valor: {val_2}")
            print(f"   fecha_emision: {fecha_2}")
    else:
        print("❌ No hay registros en la tabla")
else:
    print(f"❌ Error al consultar API: {response.status_code}")
    print(f"   Respuesta: {response.text[:200]}")

print("\n✅ Diagnóstico completo")
print("\nPRÓXIMO PASO:")
print("- Si valor = 0 o NULL: El problema es detección de columna 'Total'")
print("- Si fecha = 2026-02-17: El problema es detección de columna 'Fecha Emisión'")
print("- Si ambos están bien: ¡El problema está resuelto!")
