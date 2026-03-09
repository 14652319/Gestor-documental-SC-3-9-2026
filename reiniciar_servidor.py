"""
Script para reiniciar el servidor Flask del Gestor Documental
"""
import subprocess
import psutil
import time
import os

print("🔄 Reiniciando servidor Flask...")
print()

# 1. Buscar y detener procesos Python de Flask
print("1️⃣ Buscando procesos Python de Flask...")
count = 0
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] and 'python' in proc.info['name'].lower():
            cmdline = proc.info['cmdline']
            if cmdline and 'app.py' in ' '.join(cmdline):
                print(f"   ⚠️  Deteniendo proceso {proc.info['pid']}: {' '.join(cmdline[:3])}")
                proc.terminate()
                count += 1
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if count > 0:
    print(f"   ✅ {count} proceso(s) detenido(s)")
    time.sleep(2)
else:
    print("   ℹ️  No hay procesos Flask corriendo")

print()

# 2. Iniciar nuevo servidor
print("2️⃣ Iniciando nuevo servidor Flask...")
print("   📂 Directorio:", os.getcwd())
print("   🐍 Comando: python app.py")
print()

# Abrir en nueva ventana de PowerShell
subprocess.Popen(
    ['powershell', '-Command', 'Start-Process', 'powershell', '-ArgumentList', 
     "'-NoExit', '-Command', 'cd \"{}\" ; python app.py'".format(os.getcwd())],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

print("✅ Servidor iniciando en nueva ventana de PowerShell")
print()
print("⏳ Espera 5-10 segundos y luego:")
print("   1. Abre http://127.0.0.1:8099/dian_vs_erp/configuracion")
print("   2. Presiona Ctrl+Shift+R para forzar recarga")
print("   3. Prueba editar una configuración")
print()
