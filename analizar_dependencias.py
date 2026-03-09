"""
Script para analizar todas las dependencias del proyecto
y generar un requirements.txt completo
"""
import os
import re
from pathlib import Path
from collections import defaultdict

# Mapeo de nombres de módulos import a nombre de paquete pip
MODULE_TO_PACKAGE = {
    'flask': 'flask',
    'flask_sqlalchemy': 'flask-sqlalchemy',
    'flask_bcrypt': 'flask-bcrypt',
    'flask_cors': 'flask-cors',
    'flask_mail': 'flask-mail',
    'sqlalchemy': 'sqlalchemy',
    'psycopg2': 'psycopg2-binary',
    'dotenv': 'python-dotenv',
    'requests': 'requests',
    'openpyxl': 'openpyxl',
    'pandas': 'pandas',
    'xlsxwriter': 'xlsxwriter',
    'fpdf': 'fpdf2',
    'reportlab': 'reportlab',
    'gunicorn': 'gunicorn',
    'schedule': 'schedule',
    'dateutil': 'python-dateutil',
    'numpy': 'numpy',
    'polars': 'polars',
    'pl': 'polars',  # polars se importa como pl
    'psutil': 'psutil',
    'colorlog': 'colorlog',
    'email_validator': 'email-validator',
    'pytz': 'pytz',
    'pytest': 'pytest',
    'multipart': 'python-multipart',
    'PyPDF2': 'PyPDF2',
    'flask_caching': 'flask-caching',
    'flask_limiter': 'flask-limiter',
    'bcrypt': 'bcrypt',
    'werkzeug': 'werkzeug',
    'jinja2': 'jinja2',
    'apscheduler': 'APScheduler',
    'pyarrow': 'pyarrow',
    'et_xmlfile': 'et-xmlfile',
}

# Módulos que son parte de la librería estándar de Python (no necesitan instalarse)
STDLIB_MODULES = {
    'sys', 'os', 'io', 'json', 'time', 'hashlib', 'datetime', 'pathlib',
    'secrets', 'logging', 'functools', 'collections', 'urllib', 'traceback',
    'subprocess', 'shutil', 'zipfile', 'email', 'smtplib', 're', 'concurrent',
}

def extract_imports_from_file(filepath):
    """Extrae todos los imports de un archivo Python"""
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Buscar imports del tipo: import xxx
        for match in re.finditer(r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE):
            module_name = match.group(1)
            imports.add(module_name)
        
        # Buscar imports del tipo: from xxx import yyy
        for match in re.finditer(r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import', content, re.MULTILINE):
            module_name = match.group(1).split('.')[0]  # Solo el paquete raíz
            imports.add(module_name)
            
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
    
    return imports

def scan_project():
    """Escanea todo el proyecto buscando imports"""
    project_root = Path(__file__).parent
    all_imports = set()
    
    # Buscar todos los archivos .py
    for py_file in project_root.rglob('*.py'):
        # Ignorar virtualenv y cache
        str_path = str(py_file)
        if '.venv' in str_path or '__pycache__' in str_path or 'Proyecto Dian' in str_path:
            continue
            
        imports = extract_imports_from_file(py_file)
        all_imports.update(imports)
    
    return all_imports

def filter_external_packages(imports):
    """Filtra solo paquetes externos (no stdlib, no locales)"""
    external = set()
    
    for module in imports:
        # Ignorar módulos de la librería estándar
        if module in STDLIB_MODULES:
            continue
        
        # Ignorar imports locales del proyecto (empiezan con mayúscula o son del proyecto)
        if module[0].isupper():  # Clases locales
            continue
            
        if module in ['app', 'extensions', 'decoradores_permisos', 'utils_licencia', 
                      'utils_fecha', 'config_carpetas', 'backup_manager']:
            continue
        
        # Ignorar módulos del proyecto (empiezan con 'modules.')
        if module == 'modules':
            continue
            
        external.add(module)
    
    return external

def map_to_packages(modules):
    """Mapea nombres de módulos a nombres de paquetes pip"""
    packages = set()
    
    for module in modules:
        package = MODULE_TO_PACKAGE.get(module)
        if package:
            packages.add(package)
        else:
            # Si no está en el mapeo, asumimos que el nombre del módulo es el nombre del paquete
            packages.add(module)
    
    return sorted(packages)

if __name__ == '__main__':
    print("🔍 Analizando dependencias del proyecto...\n")
    
    # Escanear proyecto
    all_imports = scan_project()
    print(f"📦 Total de imports encontrados: {len(all_imports)}")
    
    # Filtrar externos
    external_modules = filter_external_packages(all_imports)
    print(f"📦 Módulos externos detectados: {len(external_modules)}")
    print(f"   {sorted(external_modules)}\n")
    
    # Mapear a paquetes pip
    packages = map_to_packages(external_modules)
    print(f"📦 Paquetes pip necesarios: {len(packages)}")
    
    print("\n✅ LISTA DE PAQUETES:\n")
    for package in packages:
        print(f"   {package}")
    
    print("\n" + "="*50)
    print("✅ DEPENDENCIAS CRÍTICAS IDENTIFICADAS:")
    print("="*50)
    
    critical = {
        'flask', 'flask-sqlalchemy', 'flask-bcrypt', 'flask-cors', 'flask-mail',
        'psycopg2-binary', 'python-dotenv', 'pyarrow', 'polars', 'APScheduler',
        'pytz', 'openpyxl', 'pandas', 'werkzeug'
    }
    
    for pkg in sorted(critical):
        status = "✅" if pkg in packages else "❌ FALTA"
        print(f"{status} {pkg}")
