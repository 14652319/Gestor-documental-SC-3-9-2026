"""
Simula exactamente lo que hace el navegador al cargar archivos
Diciembre 29, 2025
"""

import os
import sys
import shutil
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🌐 SIMULANDO CARGA DESDE NAVEGADOR")
print("=" * 80)

# 1. COPIAR ARCHIVO A LA CARPETA UPLOADS (como hace el navegador)
archivo_origen = r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Dian\Desde 01-11-2025 Hasta 29-12-2025.xlsx"
carpeta_destino = Path("modules/dian_vs_erp/uploads/dian")

print(f"\n1️⃣ Copiando archivo a carpeta uploads...")
print(f"   Origen: {archivo_origen}")
print(f"   Destino: {carpeta_destino}")

# Crear carpeta si no existe
carpeta_destino.mkdir(parents=True, exist_ok=True)

# Copiar archivo
archivo_destino = carpeta_destino / "test_desde_navegador.xlsx"
shutil.copy2(archivo_origen, archivo_destino)
print(f"   ✅ Archivo copiado: {archivo_destino}")

# 2. LLAMAR A LA FUNCIÓN actualizar_maestro() (como hace el navegador)
print(f"\n2️⃣ Llamando a actualizar_maestro()...")

# Importar después de copiar el archivo
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configurar Flask app context
from app import app
from modules.dian_vs_erp.routes import actualizar_maestro

with app.app_context():
    try:
        resultado = actualizar_maestro()
        print("\n" + "=" * 80)
        print("✅ RESULTADO:")
        print("=" * 80)
        print(resultado)
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR:")
        print("=" * 80)
        import traceback
        print(traceback.format_exc())
