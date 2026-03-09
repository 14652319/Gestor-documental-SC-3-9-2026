# -*- coding: utf-8 -*-
"""
Script de Validación del Sistema de Carga de Archivos
Módulo DIAN vs ERP - Diagnóstico Completo
Fecha: 17 de Febrero de 2026
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import hashlib

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprime encabezado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    """Imprime información"""
    print(f"  {text}")

def format_size(bytes):
    """Formatea tamaño de archivo"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def get_file_hash(filepath):
    """Calcula MD5 hash de archivo"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()[:10]
    except:
        return "N/A"

def count_csv_lines(filepath):
    """Cuenta líneas de archivo CSV"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Contar líneas (excluir header)
            count = sum(1 for _ in f) - 1
            return count
    except:
        try:
            # Intentar con latin-1
            with open(filepath, 'r', encoding='latin-1') as f:
                count = sum(1 for _ in f) - 1
                return count
        except:
            return 0

def validate_uploads_structure():
    """Valida estructura de carpetas uploads"""
    print_header("VALIDACIÓN DE ESTRUCTURA DE CARPETAS")
    
    base_dir = Path.cwd()
    uploads_dir = base_dir / "uploads"
    
    # Carpetas esperadas
    expected_folders = {
        "dian": "Archivos DIAN (OBLIGATORIO)",
        "erp_fn": "ERP Módulo Financiero",
        "erp_cm": "ERP Módulo Comercial",
        "acuses": "Acuses de Recibo DIAN",
        "rg_erp_er": "Errores ERP"
    }
    
    if not uploads_dir.exists():
        print_error(f"Carpeta uploads/ no encontrada en: {base_dir}")
        return False
    
    print_success(f"Carpeta uploads encontrada: {uploads_dir}")
    print()
    
    all_folders_exist = True
    for folder, description in expected_folders.items():
        folder_path = uploads_dir / folder
        if folder_path.exists():
            print_success(f"{folder}/ - {description}")
        else:
            print_error(f"{folder}/ - {description} (NO EXISTE)")
            all_folders_exist = False
    
    return all_folders_exist

def validate_files_in_folder(folder_name, uploads_dir):
    """Valida archivos en una carpeta específica"""
    folder_path = uploads_dir / folder_name
    
    if not folder_path.exists():
        return [], [], []
    
    # Buscar archivos por tipo
    xlsx_files = list(folder_path.glob("*.xlsx"))
    xlsm_files = list(folder_path.glob("*.xlsm"))
    csv_files = list(folder_path.glob("*.csv"))
    xls_files = list(folder_path.glob("*.xls"))  # Obsoletos
    
    valid_files = xlsx_files + xlsm_files + csv_files
    
    return valid_files, xls_files, folder_path

def analyze_csv_file(filepath):
    """Analiza archivo CSV"""
    print_info(f"\n📊 Analizando: {filepath.name}")
    print_info(f"   Tamaño: {format_size(filepath.stat().st_size)}")
    print_info(f"   Hash MD5: {get_file_hash(filepath)}")
    
    # Contar líneas
    lines = count_csv_lines(filepath)
    if lines > 0:
        print_info(f"   Registros: {lines:,}")
    else:
        print_warning(f"   No se pudo leer el archivo")
    
    # Fecha de modificación
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
    print_info(f"   Última modificación: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar primeras líneas
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            header = f.readline().strip()
            if header:
                cols = header.split(',')
                print_info(f"   Columnas: {len(cols)}")
                print_info(f"   Primera columna: {cols[0] if cols else 'N/A'}")
    except:
        pass

def validate_dian_folder():
    """Validación específica para carpeta DIAN"""
    print_header("VALIDACIÓN CARPETA DIAN (OBLIGATORIA)")
    
    base_dir = Path.cwd()
    uploads_dir = base_dir / "uploads"
    
    valid_files, xls_files, folder_path = validate_files_in_folder("dian", uploads_dir)
    
    if not folder_path.exists():
        print_error("Carpeta dian/ no existe")
        return False
    
    # Verificar archivos válidos
    if valid_files:
        print_success(f"Archivos válidos encontrados: {len(valid_files)}")
        for file in valid_files:
            analyze_csv_file(file)
    else:
        print_error("No hay archivos válidos (.xlsx, .xlsm, .csv)")
        print_warning("El sistema requiere al menos UN archivo DIAN para funcionar")
        return False
    
    # Verificar archivos obsoletos
    if xls_files:
        print()
        print_warning(f"Archivos .xls obsoletos encontrados: {len(xls_files)}")
        for file in xls_files:
            print_error(f"   • {file.name}")
        print_info("\n💡 SOLUCIÓN:")
        print_info("   1. Abre estos archivos en Excel")
        print_info("   2. Guarda como: Libro de Excel (.xlsx)")
        print_info("   3. Elimina los archivos .xls viejos")
        return False
    
    return True

def validate_erp_folders():
    """Validación de carpetas ERP"""
    print_header("VALIDACIÓN CARPETAS ERP")
    
    base_dir = Path.cwd()
    uploads_dir = base_dir / "uploads"
    
    folders = {
        "erp_fn": "ERP Financiero",
        "erp_cm": "ERP Comercial",
        "rg_erp_er": "Errores ERP"
    }
    
    for folder, description in folders.items():
        print(f"\n{Colors.BOLD}📁 {description}{Colors.RESET}")
        valid_files, xls_files, folder_path = validate_files_in_folder(folder, uploads_dir)
        
        if not folder_path.exists():
            print_warning(f"   Carpeta {folder}/ no existe")
            continue
        
        if valid_files:
            print_success(f"   Archivos válidos: {len(valid_files)}")
            # Solo mostrar el más reciente
            latest = max(valid_files, key=lambda f: f.stat().st_mtime)
            print_info(f"   Más reciente: {latest.name}")
            
            # Analizar CSV si existe
            if latest.suffix == '.csv':
                lines = count_csv_lines(latest)
                if lines > 0:
                    print_info(f"   Registros: {lines:,}")
        else:
            print_warning(f"   No hay archivos (opcional)")
        
        if xls_files:
            print_warning(f"   Archivos .xls obsoletos: {len(xls_files)}")

def validate_acuses_folder():
    """Validación de carpeta acuses"""
    print_header("VALIDACIÓN CARPETA ACUSES")
    
    base_dir = Path.cwd()
    uploads_dir = base_dir / "uploads"
    
    valid_files, xls_files, folder_path = validate_files_in_folder("acuses", uploads_dir)
    
    if not folder_path.exists():
        print_warning("Carpeta acuses/ no existe")
        print_info("Esta carpeta es OPCIONAL pero mejora la información de estados")
        return
    
    if valid_files:
        print_success(f"Archivos válidos encontrados: {len(valid_files)}")
        latest = max(valid_files, key=lambda f: f.stat().st_mtime)
        print_info(f"Más reciente: {latest.name}")
        
        if latest.suffix == '.csv':
            lines = count_csv_lines(latest)
            if lines > 0:
                print_info(f"Registros: {lines:,}")
    else:
        print_warning("No hay archivos de acuses")
        print_info("Esto es opcional pero recomendado para estados correctos")

def check_file_permissions():
    """Verifica permisos de escritura"""
    print_header("VALIDACIÓN DE PERMISOS")
    
    base_dir = Path.cwd()
    uploads_dir = base_dir / "uploads"
    
    try:
        # Intentar crear archivo de prueba
        test_file = uploads_dir / "test_permissions.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print_success("Permisos de escritura: OK")
    except Exception as e:
        print_error(f"Permisos de escritura: ERROR - {e}")
        print_warning("El sistema puede no poder guardar archivos")

def validate_system_config():
    """Valida configuración del sistema"""
    print_header("VALIDACIÓN DE CONFIGURACIÓN")
    
    # Verificar que estemos en el directorio correcto
    base_dir = Path.cwd()
    
    # Verificar archivos clave
    files_to_check = [
        ("app.py", "Aplicación principal"),
        ("extensions.py", "Extensiones SQL"),
        ("modules/dian_vs_erp/routes.py", "Rutas DIAN vs ERP"),
        ("modules/dian_vs_erp/models.py", "Modelos DIAN vs ERP")
    ]
    
    all_exist = True
    for file, description in files_to_check:
        filepath = base_dir / file
        if filepath.exists():
            print_success(f"{file} - {description}")
        else:
            print_error(f"{file} - {description} (NO ENCONTRADO)")
            all_exist = False
    
    if not all_exist:
        print()
        print_warning("Asegúrate de ejecutar este script desde la raíz del proyecto")
    
    return all_exist

def main():
    """Función principal"""
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}{'*'*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}VALIDACIÓN DEL SISTEMA DE CARGA DE ARCHIVOS{Colors.RESET}".center(80))
    print(f"{Colors.BOLD}{Colors.GREEN}Módulo DIAN vs ERP{Colors.RESET}".center(80))
    print(f"{Colors.BOLD}{Colors.GREEN}{'*'*70}{Colors.RESET}")
    print()
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Directorio: {Path.cwd()}")
    print()
    
    # 1. Validar configuración del sistema
    config_ok = validate_system_config()
    if not config_ok:
        print()
        print_error("Sistema no configurado correctamente")
        return
    
    # 2. Validar estructura de carpetas
    structure_ok = validate_uploads_structure()
    
    # 3. Validar carpeta DIAN (OBLIGATORIO)
    dian_ok = validate_dian_folder()
    
    # 4. Validar carpetas ERP (OPCIONAL)
    validate_erp_folders()
    
    # 5. Validar carpeta acuses (OPCIONAL)
    validate_acuses_folder()
    
    # 6. Verificar permisos
    check_file_permissions()
    
    # Resumen final
    print_header("RESUMEN FINAL")
    
    if structure_ok and dian_ok:
        print_success("✓ Sistema de carga: OPERATIVO")
        print_success("✓ Archivos DIAN: VÁLIDOS")
        print_info("\n💡 Puedes proceder con la carga de archivos")
    elif structure_ok:
        print_warning("⚠ Estructura: OK pero faltan archivos DIAN")
        print_info("\n💡 Sube al menos UN archivo DIAN para continuar")
    else:
        print_error("✗ Sistema requiere configuración")
        print_info("\n💡 Revisa los errores anteriores")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validación cancelada por el usuario{Colors.RESET}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Error inesperado: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
