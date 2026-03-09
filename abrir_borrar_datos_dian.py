"""
Script para acceder directamente a la opción de BORRAR DATOS
del módulo DIAN vs ERP - Configuración
"""
import webbrowser
import time

print("=" * 80)
print("🗑️  ACCESO A MÓDULO: BORRAR DATOS - DIAN VS ERP")
print("=" * 80)
print()
print("📍 Abriendo interfaz de configuración...")
print()
print("⚠️  IMPORTANTE:")
print("   1. Debes estar AUTENTICADO en el sistema")
print("   2. La interfaz se abrirá en el navegador")
print("   3. Haz clic en la pestaña: '🗑️ Gestión de Datos'")
print()
print("=" * 80)
print()

time.sleep(2)

# URL del módulo de configuración
url = "http://localhost:8099/dian_vs_erp/configuracion"

print(f"🌐 Abriendo: {url}")
print()

# Abrir en el navegador por defecto
webbrowser.open(url)

print("✅ Navegador abierto")
print()
print("📋 INSTRUCCIONES DE USO:")
print()
print("PASO 1: En la interfaz web, haz clic en el tab '🗑️ Gestión de Datos'")
print()
print("PASO 2: Configura los parámetros de eliminación:")
print("   • Tipo de Rango: Días, Meses o Año")
print("   • Fecha Inicio: AAAA-MM-DD")
print("   • Fecha Fin: AAAA-MM-DD")
print("   • Tablas a Eliminar:")
print("     ☑ Facturas DIAN (maestro_dian_vs_erp) ⭐ PRINCIPAL")
print("     ☐ Acuses")
print("     ☐ ERP Financiero")
print("     ☐ ERP Comercial")
print()
print("PASO 3: Click en '🔐 Solicitar Eliminación'")
print()
print("PASO 4: Sistema enviará código de 6 dígitos a tu email")
print()
print("PASO 5: Ingresa el código en el formulario")
print()
print("PASO 6: Click en '✅ Confirmar y Ejecutar Eliminación'")
print()
print("=" * 80)
print()
print("⚠️  ADVERTENCIA:")
print("   Esta acción es IRREVERSIBLE")
print("   Los datos eliminados NO se pueden recuperar")
print("   Se enviará código de confirmación por email")
print()
print("=" * 80)
print()
print("💡 TIP:")
print("   Para corregir las fechas del 2026 al 2025 en los 86,435 registros,")
print("   usa el script: corregir_fechas_2026_a_2025.py")
print()
print("=" * 80)

input("\nPresiona ENTER para cerrar...")
