"""
GUÍA RÁPIDA: BORRAR DATOS DIAN desde Configuración
"""
import webbrowser
import time

print("=" * 80)
print("🗑️  BORRAR DATOS DEL ARCHIVO DIAN")
print("=" * 80)
print()
print("IMPORTANTE: Estás a punto de eliminar los 86,435 registros DIAN de la BD")
print()
print("=" * 80)
print()

# Esperar un momento
time.sleep(1)

# Abrir navegador
url = "http://localhost:8099/dian_vs_erp/configuracion"
print(f"🌐 Abriendo navegador en: {url}")
print()
webbrowser.open(url)

time.sleep(2)

print("=" * 80)
print("📋 INSTRUCCIONES PARA BORRAR LOS DATOS:")
print("=" * 80)
print()
print("PASO 1: En el navegador, haz clic en la pestaña:")
print("        👉 '🗑️ Gestión de Datos' (quinta pestaña)")
print()
print("PASO 2: Configura el rango:")
print("        • Tipo de Rango: 'Año Completo'")
print("        • Año: 2026 (o el rango que quieras eliminar)")
print()
print("PASO 3: Selecciona SOLO la tabla DIAN:")
print("        ☑ 📊 Facturas DIAN (debe estar marcada)")
print("        ☐ Acuses (desmarcada)")
print("        ☐ ERP Financiero (desmarcada)")
print("        ☐ ERP Comercial (desmarcada)")
print()
print("PASO 4: Click en '🔐 Solicitar Eliminación'")
print()
print("PASO 5: Revisa tu correo y copia el código de 6 dígitos")
print()
print("PASO 6: Pega el código en el formulario")
print()
print("PASO 7: Click en '✅ Confirmar y Ejecutar Eliminación'")
print()
print("=" * 80)
print()
print("⚠️  RECORDATORIO:")
print("   • Esta acción es IRREVERSIBLE")
print("   • Se eliminarán los 86,435 registros de maestro_dian_vs_erp")
print("   • Tendrás que volver a cargar el CSV después")
print()
print("=" * 80)
print()
print("💡 ALTERNATIVA:")
print("   Si solo quieres corregir las fechas (2026 → 2025),")
print("   ejecuta: python corregir_fechas_2026_a_2025.py")
print()
print("=" * 80)

input("\nPresiona ENTER cuando hayas terminado...")
