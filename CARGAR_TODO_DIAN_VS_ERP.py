"""
Carga MASIVA de TODOS los archivos DIAN vs ERP
Diciembre 30, 2025
"""

import requests
from pathlib import Path
import time

print("=" * 80)
print("🚀 CARGA MASIVA DE ARCHIVOS DIAN VS ERP")
print("=" * 80)

# Configuración
BASE_URL = "http://localhost:8099"
BASE_PATH = Path(r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025")

# Mapeo de carpetas
CARPETAS = {
    "dian": BASE_PATH / "Dian",
    "erp_fn": BASE_PATH / "ERP Financiero",
    "erp_cm": BASE_PATH / "ERP Comercial",
    "acuses": BASE_PATH / "Acuses"
}

# Crear sesión con login
session = requests.Session()

# LOGIN
print("\n1️⃣ LOGIN...")
login_response = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"nit": "805028041", "usuario": "admin", "password": "Admin123456$"},
    timeout=10
)

if login_response.status_code != 200:
    print(f"❌ Login falló: {login_response.text}")
    exit(1)

print("✅ Login exitoso")

# LISTAR ARCHIVOS
print("\n2️⃣ LISTANDO ARCHIVOS...")
archivos_por_tipo = {}
total_archivos = 0

for tipo, carpeta in CARPETAS.items():
    if not carpeta.exists():
        print(f"⚠️ Carpeta {tipo} no encontrada: {carpeta}")
        continue
    
    archivos = list(carpeta.glob("*"))
    archivos_validos = [
        a for a in archivos 
        if a.is_file() and a.suffix.lower() in ['.xlsx', '.xlsm', '.csv', '.ods']  # Excluir .xls corrupto
    ]
    
    archivos_por_tipo[tipo] = archivos_validos
    total_archivos += len(archivos_validos)
    
    print(f"\n   📁 {tipo.upper()}: {len(archivos_validos)} archivo(s)")
    for archivo in archivos_validos:
        print(f"      • {archivo.name}")

print(f"\n✅ Total: {total_archivos} archivos encontrados")

if total_archivos == 0:
    print("❌ No se encontraron archivos para cargar")
    exit(1)

# CONFIRMAR
input(f"\n⏸️  Presiona ENTER para cargar {total_archivos} archivos...")

# CARGAR ARCHIVOS
print("\n3️⃣ CARGANDO ARCHIVOS AL SERVIDOR...")
print("=" * 80)

inicio = time.time()

# Preparar archivos para multipart/form-data
files_dict = {}

for tipo, archivos in archivos_por_tipo.items():
    if len(archivos) == 0:
        continue
    
    # Si hay múltiples archivos del mismo tipo, usar solo el primero
    # (el endpoint actual procesa todos los archivos de cada carpeta automáticamente)
    archivo = archivos[0]
    print(f"\n📤 Preparando {tipo}: {archivo.name}")
    files_dict[tipo] = open(archivo, 'rb')

print(f"\n🚀 Enviando petición al servidor...")

try:
    upload_response = session.post(
        f"{BASE_URL}/dian_vs_erp/subir_archivos",
        files=files_dict,
        timeout=600  # 10 minutos
    )
    
    fin = time.time()
    tiempo_total = fin - inicio
    
    print("\n" + "=" * 80)
    print("📥 RESPUESTA DEL SERVIDOR")
    print("=" * 80)
    print(f"Status Code: {upload_response.status_code}")
    print(f"Tiempo total: {tiempo_total:.1f} segundos")
    
    if upload_response.status_code == 200:
        print("\n✅ CARGA EXITOSA")
        
        # Parsear respuesta JSON
        try:
            resultado = upload_response.json()
            print(f"\n{resultado.get('mensaje', '')}")
        except:
            print(f"\n{upload_response.text}")
    else:
        print(f"\n❌ ERROR {upload_response.status_code}")
        print(f"\n{upload_response.text}")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    # Cerrar archivos
    for f in files_dict.values():
        f.close()

print("\n" + "=" * 80)
print("✅ PROCESO COMPLETADO")
print("=" * 80)
