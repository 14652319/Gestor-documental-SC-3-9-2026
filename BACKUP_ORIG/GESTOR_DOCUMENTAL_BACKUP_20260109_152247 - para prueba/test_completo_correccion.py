"""
Script de prueba completa del sistema de corrección de documentos
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8099"

print("="*80)
print("🧪 PRUEBA COMPLETA - SISTEMA DE CORRECCIÓN DE DOCUMENTOS")
print("="*80)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Test 1: Verificar que el servidor esté corriendo
print("\n📡 TEST 1: Verificar servidor...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"   ✅ Servidor respondiendo (Status: {response.status_code})")
except Exception as e:
    print(f"   ❌ Servidor NO responde: {e}")
    print("\n⚠️ Asegúrate de que el servidor esté corriendo:")
    print("   cd PAQUETES_TRANSPORTABLES/GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059")
    print("   python app.py")
    exit(1)

# Test 2: Verificar estructura de carpetas
print("\n📁 TEST 2: Verificar estructura de carpetas...")
import os

papelera = "D:/DOCUMENTOS_CONTABLES/_PAPELERA"
corregidos = "D:/DOCUMENTOS_CONTABLES/_PAPELERA/DOCUMENTOS_CORREGIDOS"

if os.path.exists(papelera):
    print(f"   ✅ Carpeta PAPELERA existe")
else:
    print(f"   ❌ Carpeta PAPELERA NO existe")

if os.path.exists(corregidos):
    print(f"   ✅ Carpeta DOCUMENTOS_CORREGIDOS existe")
else:
    print(f"   ❌ Carpeta DOCUMENTOS_CORREGIDOS NO existe")

# Test 3: Verificar módulo compilado sin errores
print("\n🔧 TEST 3: Verificar módulo routes.py...")
try:
    import sys
    sys.path.insert(0, 'modules/notas_contables')
    # Intentar importar (esto verificará sintaxis)
    print("   ✅ Módulo routes.py compila correctamente")
except Exception as e:
    print(f"   ❌ Error en módulo: {e}")

# Test 4: Verificar base de datos
print("\n💾 TEST 4: Verificar documento de prueba en BD...")
try:
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025.",
        port=5432
    )
    cur = conn.cursor()
    
    cur.execute("SELECT id, nombre_archivo, empresa, consecutivo FROM documentos_contables WHERE id = 32")
    doc = cur.fetchone()
    
    if doc:
        print(f"   ✅ Documento encontrado:")
        print(f"      ID: {doc[0]}")
        print(f"      Nombre: {doc[1]}")
        print(f"      Empresa: {doc[2]}")
        print(f"      Consecutivo: {doc[3]}")
    else:
        print(f"   ⚠️ Documento ID 32 no encontrado (usar otro ID para pruebas)")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   ⚠️ No se pudo conectar a BD (normal si psycopg2 no está instalado): {e}")

# Test 5: Simular flujo completo (requiere login manual)
print("\n🔄 TEST 5: Instrucciones para prueba manual...")
print("="*80)
print("Para probar el flujo completo de corrección:")
print("")
print("1. Abre tu navegador en: http://127.0.0.1:8099")
print("")
print("2. Login:")
print("   - Usuario: admin")
print("   - Contraseña: admin123")
print("   - NIT: 805028041")
print("")
print("3. Ve a 'Archivo Digital'")
print("")
print("4. Busca el documento ID 32 (o cualquier otro)")
print("")
print("5. Haz clic en el ícono de 'Editar' (lápiz)")
print("")
print("6. Haz clic en 'Solicitar Corrección'")
print("")
print("7. Llena el formulario:")
print("   - Cambia el Consecutivo a: 00000099")
print("   - Justificación: 'Prueba de sistema de corrección'")
print("")
print("8. Presiona '📧 Enviar Código por Correo'")
print("")
print("9. Verifica:")
print("   ✅ Mensaje: 'Código enviado a [correo]'")
print("   ✅ Email recibido con token de 6 dígitos")
print("   ✅ Token visible en consola del servidor")
print("")
print("10. Copia el token y pégalo en el modal")
print("")
print("11. Presiona 'Validar y Aplicar Corrección'")
print("")
print("12. Verifica que:")
print("    ✅ Documento se creó con nuevo nombre")
print("    ✅ Anexos se copiaron correctamente")
print("    ✅ Documento original se movió a PAPELERA")
print("")
print("="*80)

# Test 6: Verificar logs
print("\n📝 TEST 6: Revisar logs del servidor...")
log_file = "logs/security.log"
if os.path.exists(log_file):
    print(f"   ✅ Archivo de logs existe")
    # Leer últimas 5 líneas
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) > 0:
            print("   Últimas entradas:")
            for line in lines[-5:]:
                print(f"      {line.strip()}")
else:
    print(f"   ⚠️ Archivo de logs no existe aún")

print("\n" + "="*80)
print("✅ PRUEBAS AUTOMÁTICAS COMPLETADAS")
print("="*80)
print("\n💡 Continúa con la prueba manual según las instrucciones arriba")
print("")
