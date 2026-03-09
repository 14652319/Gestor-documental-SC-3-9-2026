"""
Script para buscar errores en el log durante el guardado
"""
import os

log_file = 'logs/security.log'

print("=" * 100)
print("ÚLTIMOS LOGS RELACIONADOS CON GUARDAR FACTURAS")
print("=" * 100)
print()

try:
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Buscar últimas 100 líneas que contengan palabras clave
    keywords = ['guardar', 'GUARDAR', 'SINCRONIZACION', 'ERROR', 'factura', 'FACTURA', '805002366', '805013653', 'ME60', '1FEA', '77', '772863']
    
    logs_relevantes = []
    for line in lines[-200:]:  # Últimas 200 líneas
        if any(keyword in line for keyword in keywords):
            logs_relevantes.append(line)
    
    if logs_relevantes:
        print(f"📋 Se encontraron {len(logs_relevantes)} logs relevantes:\n")
        for log in logs_relevantes[-30:]:  # Últimos 30
            print(log.strip())
    else:
        print("⚠️  No se encontraron logs relevantes")
        print("\n📋 Últimas 10 líneas del log (cualquier tipo):")
        for line in lines[-10:]:
            print(line.strip())
    
except FileNotFoundError:
    print(f"❌ Archivo no encontrado: {log_file}")
except Exception as e:
    print(f"❌ Error al leer log: {e}")

print("\n" + "=" * 100)
