"""
Verificar qué templates NO tienen timeout de sesión
"""
import os
import re

templates_dir = r"c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\templates"

# Buscar todos los HTML
sin_timeout = []
con_timeout = []

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            relpath = os.path.relpath(filepath, templates_dir)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Buscar patrón de timeout
                    if 'SESSION_TIMEOUT' in content and '25 * 60 * 1000' in content:
                        con_timeout.append(relpath)
                    else:
                        # Ignorar backups y versiones antiguas
                        if not any(x in file.lower() for x in ['old', 'backup', 'bak', '_v1', '_v2']):
                            sin_timeout.append(relpath)
            except:
                pass

print("\n" + "="*100)
print("🔍 VERIFICACIÓN DE TIMEOUT DE SESIÓN (25 MINUTOS)")
print("="*100 + "\n")

print(f"✅ Templates CON timeout: {len(con_timeout)}\n")
for t in sorted(con_timeout)[:10]:
    print(f"   ✅ {t}")
if len(con_timeout) > 10:
    print(f"   ... y {len(con_timeout) - 10} más\n")

print(f"\n❌ Templates SIN timeout (activos): {len(sin_timeout)}\n")
for t in sorted(sin_timeout):
    print(f"   ❌ {t}")

print(f"\n📊 RESUMEN:")
print(f"   Total templates: {len(con_timeout) + len(sin_timeout)}")
print(f"   Con timeout:     {len(con_timeout)} ({len(con_timeout)/(len(con_timeout)+len(sin_timeout))*100:.1f}%)")
print(f"   Sin timeout:     {len(sin_timeout)} ({len(sin_timeout)/(len(con_timeout)+len(sin_timeout))*100:.1f}%)")
print("\n" + "="*100 + "\n")
