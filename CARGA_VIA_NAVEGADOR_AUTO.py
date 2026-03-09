"""
CARGA COMPLETA VIA NAVEGADOR AUTOMATIZADA
Usa el endpoint del navegador que ya funciona
"""
import requests
import os
from datetime import datetime

print("\n" + "="*80)
print("CARGA AUTOMATIZADA VIA ENDPOINT DEL NAVEGADOR")
print("="*80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ============================================================================
# PASO 1: VERIFICAR QUE EL SERVIDOR ESTÉ CORRIENDO
# ============================================================================

print("\n" + "="*80)
print("PASO 1: VERIFICAR SERVIDOR")
print("="*80)

try:
    response = requests.get('http://localhost:8099/dian_vs_erp/', timeout=5)
    print(f"OK Servidor respondiendo en puerto 8099 (Status: {response.status_code})")
except Exception as e:
    print(f"ERROR: Servidor NO está corriendo en puerto 8099")
    print(f"Por favor inicia el servidor con: .\\1_iniciar_gestor.bat")
    exit()

# ============================================================================
# PASO 2: VERIFICAR ARCHIVOS
# ============================================================================

print("\n" + "="*80)
print("PASO 2: VERIFICAR ARCHIVOS")
print("="*80)

archivos = {
    'dian': r'uploads\dian\Dian_23022026.xlsx',
    'erp_fn': r'uploads\erp_fn\erp_financiero_23022026.xlsx',
    'erp_cm': r'uploads\erp_cm\ERP_comercial_23022026.xlsx',
    'acuses': r'uploads\acuses\acuses_23022026.xlsx'
}

for nombre, ruta in archivos.items():
    if os.path.exists(ruta):
        size_mb = os.path.getsize(ruta) / (1024*1024)
        print(f"OK {nombre}: {ruta} ({size_mb:.2f} MB)")
    else:
        print(f"ERROR {nombre}: NO ENCONTRADO - {ruta}")
        exit()

# ============================================================================
# PASO 3: CARGAR ARCHIVOS AL SERVIDOR
# ============================================================================

print("\n" + "="*80)
print("PASO 3: CARGAR ARCHIVOS AL SERVIDOR")
print("="*80)

url = 'http://localhost:8099/dian_vs_erp/subir_archivos'

files = {
    'file_dian': ('Dian_23022026.xlsx', open(archivos['dian'], 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    'file_erp_fn': ('erp_financiero_23022026.xlsx', open(archivos['erp_fn'], 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    'file_erp_cm': ('ERP_comercial_23022026.xlsx', open(archivos['erp_cm'], 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    'file_acuses': ('acuses_23022026.xlsx', open(archivos['acuses'], 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
}

print("\nSubiendo archivos al servidor...")
print("NOTA: Esto puede tardar varios minutos (procesando 66K+ facturas)")

try:
    response = requests.post(
        url,
        files=files,
        timeout=600  # 10 minutos timeout
    )
    
    # Cerrar archivos abiertos
    for file_tuple in files.values():
        file_tuple[1].close()
    
    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*80)
        print("RESULTADO")
        print("="*80)
        
        if result.get('success'):
            print("OK CARGA EXITOSA")
            print(f"\n{result.get('message', '')}")
        else:
            print("ERROR EN LA CARGA")
            print(f"\n{result.get('message', 'Sin mensaje')}")
            if 'error' in result:
                print(f"Error: {result['error']}")
    else:
        print(f"\nERROR: Status code {response.status_code}")
        print(f"Respuesta: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("\nERROR: Timeout - El proceso tardo mas de 10 minutos")
    print("Probable causa: Muchos registros duplicados o servidor lento")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PASO 4: VERIFICAR DATOS CARGADOS
# ============================================================================

print("\n" + "="*80)
print("PASO 4: VERIFICAR DATOS CARGADOS")
print("="*80)

# Consultar tabla maestro
url_maestro = 'http://localhost:8099/dian_vs_erp/api/maestro_consolidado'
params = {
    'fecha_desde': '2026-01-01',
    'fecha_hasta': '2026-02-23',
    'buscar': ''
}

try:
    response = requests.get(url_maestro, params=params, timeout=30)
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            count = result.get('total', 0)
            print(f"OK Tabla maestro tiene {count:,} registros")
            
            if count > 0:
                print("\nOK CARGA COMPLETADA EXITOSAMENTE")
                print(f"   Total registros en maestro_dian_vs_erp: {count:,}")
            else:
                print("\nADVERTENCIA: Tabla maestro vacia")
        else:
            print(f"ERROR consultando maestro: {result.get('message')}")
    else:
        print(f"ERROR: Status {response.status_code}")
except Exception as e:
    print(f"ERROR consultando maestro: {e}")

print("\n" + "="*80)
print("FIN DEL PROCESO")
print("="*80)
print()
