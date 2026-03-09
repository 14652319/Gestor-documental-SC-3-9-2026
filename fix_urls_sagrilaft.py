"""
Script para corregir todas las URLs en los templates de SAGRILAFT
Agrega el prefijo /sagrilaft a todas las rutas de API
"""

def fix_revisar_documentos():
    file_path = r'C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\modules\sagrilaft\templates\revisar_documentos.html'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replacements
    replacements = [
        ('/api/radicados/', '/sagrilaft/api/radicados/'),
        ('/api/documentos/', '/sagrilaft/api/documentos/'),
        ("window.location.href = '/';", "window.location.href = '/sagrilaft';"),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ revisar_documentos.html corregido")
    print(f"   {len([r for r in replacements])} reemplazos aplicados")

if __name__ == '__main__':
    print("\n🔧 Corrigiendo URLs en templates SAGRILAFT...")
    fix_revisar_documentos()
    print("\n✅ Todas las correcciones aplicadas")
