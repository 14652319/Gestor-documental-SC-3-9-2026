"""
═══════════════════════════════════════════════════════════════════
  VERIFICACIÓN DE RUTAS DE BACKUP ACTUALIZADAS
  28 de Enero de 2026
═══════════════════════════════════════════════════════════════════
"""

import os
from pathlib import Path

print("\n" + "="*80)
print("  🔍 VERIFICACIÓN DE RUTAS DE BACKUP")
print("="*80 + "\n")

# Ruta correcta donde deben guardarse los backups
RUTA_BACKUP_CORRECTA = Path(r"C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\Backup")

print(f"📂 Ruta de backup configurada: {RUTA_BACKUP_CORRECTA}")
print()

# Verificar si existe
if RUTA_BACKUP_CORRECTA.exists():
    print(f"✅ La carpeta existe")
    
    # Listar contenido
    contenido = list(RUTA_BACKUP_CORRECTA.iterdir())
    print(f"📊 Contiene {len(contenido)} elemento(s)")
    
    if contenido:
        print("\n📁 Contenido:")
        for item in sorted(contenido):
            tipo = "📁" if item.is_dir() else "📄"
            print(f"   {tipo} {item.name}")
else:
    print(f"⚠️  La carpeta NO existe, se creará automáticamente al hacer backup")

print()
print("="*80)
print("  📋 ARCHIVOS ACTUALIZADOS CON LA NUEVA RUTA:")
print("="*80)

archivos_actualizados = [
    "1_backup_completo_pre_integracion.py",
    "BACKUP_BD_MANUAL.bat",
    "crear_backup_manual.py",
    "backup_bd_postgres.py"
]

for archivo in archivos_actualizados:
    ruta_archivo = Path(__file__).parent / archivo
    if ruta_archivo.exists():
        print(f"   ✅ {archivo}")
    else:
        print(f"   ❌ {archivo} (no encontrado)")

print()
print("="*80)
print("  🎯 PRÓXIMOS PASOS:")
print("="*80)
print("""
1. Para hacer un backup manual de la BD:
   > BACKUP_BD_MANUAL.bat

2. Para hacer un backup completo del proyecto:
   > python 1_backup_completo_pre_integracion.py

3. Para hacer un backup comprimido (.zip):
   > python crear_backup_manual.py

4. Para backup de BD en múltiples ubicaciones:
   > python backup_bd_postgres.py

Todos los backups se guardarán en:
C:\\Users\\Usuario\\Desktop\\Gestor Documental\\PAQUETES_TRANSPORTABLES\\Backup
""")

print("="*80 + "\n")
