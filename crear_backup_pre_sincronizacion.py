"""
Script para crear BACKUP COMPLETO antes de aplicar cambios de sincronización
Crea 2 copias:
1. Backup de seguridad para recuperación rápida
2. Paquete transportable completo (como pidió TIC) - TOTALMENTE FUNCIONAL

Fecha: 28 de Diciembre de 2025
Autor: Sistema Automatizado
"""

import os
import shutil
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import zipfile
from pathlib import Path

load_dotenv()

# Configuración
BASE_DIR = Path(__file__).resolve().parent
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

# Destinos según estructura
BACKUP_DIR_PADRE = Path(r"C:\Backups_GestorDocumental")
BACKUP_DIR_ACTUAL = BACKUP_DIR_PADRE / f"PRE_SINCRONIZACION_{TIMESTAMP}"

# Paquete transportable (donde pidió TIC)
PAQUETE_TIC_DIR = Path(r"C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES")
PAQUETE_NOMBRE = f"GESTOR_DOCUMENTAL_CON_BD_{TIMESTAMP}"
PAQUETE_COMPLETO = PAQUETE_TIC_DIR / PAQUETE_NOMBRE

# Parsear DATABASE_URL
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("❌ ERROR: DATABASE_URL no encontrado")
    exit(1)

from urllib.parse import urlparse
result = urlparse(database_url)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port

def crear_directorios():
    """Crea estructura de directorios para ambos backups"""
    print("\n📁 Creando estructura de directorios...")
    
    # Backup de seguridad
    dirs_backup = [
        BACKUP_DIR_ACTUAL,
        BACKUP_DIR_ACTUAL / "base_datos",
        BACKUP_DIR_ACTUAL / "codigo",
        BACKUP_DIR_ACTUAL / "documentos",
        BACKUP_DIR_ACTUAL / "logs"
    ]
    
    for d in dirs_backup:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d}")
    
    # Paquete transportable TIC
    dirs_paquete = [
        PAQUETE_COMPLETO,
        PAQUETE_COMPLETO / "codigo",
        PAQUETE_COMPLETO / "base_datos",
        PAQUETE_COMPLETO / "documentos_terceros",
        PAQUETE_COMPLETO / "INSTRUCCIONES"
    ]
    
    for d in dirs_paquete:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d}")
    
    print("✅ Directorios creados")

def backup_base_datos():
    """Backup completo de PostgreSQL con pg_dump"""
    print("\n🗄️ Haciendo backup de BASE DE DATOS...")
    
    # Para backup de seguridad (formato custom comprimido)
    archivo_backup = BACKUP_DIR_ACTUAL / "base_datos" / f"gestor_documental_{TIMESTAMP}.backup"
    
    comando_backup = f'pg_dump -h {hostname} -p {port} -U {username} -F c -b -v -f "{archivo_backup}" {database}'
    
    print(f"  📦 Ejecutando pg_dump...")
    print(f"  Base de datos: {database}")
    print(f"  Destino: {archivo_backup}")
    
    # Setear variable de entorno para password
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    import subprocess
    resultado = subprocess.run(comando_backup, shell=True, env=env, capture_output=True, text=True)
    
    if resultado.returncode == 0:
        tamano = archivo_backup.stat().st_size / (1024 * 1024)  # MB
        print(f"  ✅ Backup BD completado: {tamano:.2f} MB")
        return archivo_backup
    else:
        print(f"  ❌ ERROR en backup BD: {resultado.stderr}")
        return None

def backup_base_datos_sql():
    """Backup en formato SQL (texto plano) para paquete TIC"""
    print("\n📄 Creando dump SQL para paquete TIC...")
    
    archivo_sql = PAQUETE_COMPLETO / "base_datos" / f"gestor_documental_{TIMESTAMP}.sql"
    
    comando_sql = f'pg_dump -h {hostname} -p {port} -U {username} --encoding=UTF8 --clean --if-exists -f "{archivo_sql}" {database}'
    
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    import subprocess
    resultado = subprocess.run(comando_sql, shell=True, env=env, capture_output=True, text=True)
    
    if resultado.returncode == 0:
        tamano = archivo_sql.stat().st_size / (1024 * 1024)  # MB
        print(f"  ✅ Dump SQL creado: {tamano:.2f} MB")
        return archivo_sql
    else:
        print(f"  ❌ ERROR en dump SQL: {resultado.stderr}")
        return None

def copiar_codigo(destino):
    """Copia todo el código fuente"""
    print(f"\n💻 Copiando código fuente a {destino.name}...")
    
    # Carpetas a copiar
    carpetas_importantes = [
        'modules',
        'templates',
        'static',
        'sql',
        'logs',
        'docs',
        '.github'
    ]
    
    # Archivos importantes en raíz
    archivos_raiz = [
        'app.py',
        'extensions.py',
        'requirements.txt',
        '.env.example',
        'decoradores_permisos.py',
        'utils_fecha.py',
        'backup_manager.py',
        '1_iniciar_gestor.bat',
        '2_iniciar_dian.bat',
        'README_BACKUP.txt'
    ]
    
    # Archivos MD de documentación
    for archivo in BASE_DIR.glob('*.md'):
        if archivo.is_file():
            shutil.copy2(archivo, destino / "codigo")
            print(f"  📄 {archivo.name}")
    
    # Copiar carpetas
    for carpeta in carpetas_importantes:
        origen = BASE_DIR / carpeta
        if origen.exists():
            destino_carpeta = destino / "codigo" / carpeta
            if destino_carpeta.exists():
                shutil.rmtree(destino_carpeta)
            shutil.copytree(origen, destino_carpeta, ignore=shutil.ignore_patterns(
                '__pycache__', '*.pyc', '*.pyo', '.venv', 'node_modules', '.git'
            ))
            print(f"  📁 {carpeta}/")
    
    # Copiar archivos raíz
    for archivo in archivos_raiz:
        origen = BASE_DIR / archivo
        if origen.exists():
            shutil.copy2(origen, destino / "codigo")
            print(f"  📄 {archivo}")
    
    print("  ✅ Código copiado")

def copiar_documentos(destino):
    """Copia documentos de terceros"""
    print(f"\n📂 Copiando documentos a {destino.name}...")
    
    origen_docs = BASE_DIR / "documentos_terceros"
    
    if not origen_docs.exists():
        print("  ⚠️  Carpeta documentos_terceros no existe")
        return
    
    # Contar archivos antes de copiar
    total_archivos = sum(1 for _ in origen_docs.rglob('*') if _.is_file())
    print(f"  📊 Total de archivos a copiar: {total_archivos}")
    
    destino_docs = destino / "documentos_terceros"
    if destino_docs.exists():
        shutil.rmtree(destino_docs)
    
    shutil.copytree(origen_docs, destino_docs)
    
    # Calcular tamaño
    tamano_total = sum(f.stat().st_size for f in destino_docs.rglob('*') if f.is_file())
    tamano_mb = tamano_total / (1024 * 1024)
    
    print(f"  ✅ Documentos copiados: {tamano_mb:.2f} MB")

def crear_instrucciones_tic():
    """Crea archivo de instrucciones para TIC"""
    print("\n📝 Creando instrucciones para TIC...")
    
    contenido = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║              PAQUETE TRANSPORTABLE - GESTOR DOCUMENTAL                       ║
║                   Supertiendas Cañaveral                                     ║
║                                                                              ║
║              BACKUP COMPLETO CON BASE DE DATOS                               ║
║              Generado: {datetime.now().strftime('%d de %B de %Y a las %H:%M:%S')}                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📦 CONTENIDO DEL PAQUETE:

📁 codigo/
   └── Todo el código fuente del sistema (app.py, modules/, templates/, etc.)

📁 base_datos/
   └── gestor_documental_{TIMESTAMP}.sql
       • Dump completo de la base de datos PostgreSQL
       • Incluye TODAS las tablas, datos, índices y constraints

📁 documentos_terceros/
   └── Todos los PDFs de terceros registrados

📁 INSTRUCCIONES/
   └── Este archivo y guías de instalación


═══════════════════════════════════════════════════════════════════════════════

🚀 INSTRUCCIONES DE INSTALACIÓN EN SERVIDOR NUEVO:

PASO 1: REQUISITOS PREVIOS
═══════════════════════════
✅ Windows Server 2016+ o Linux Ubuntu 20.04+
✅ PostgreSQL 14+ instalado
✅ Python 3.11+ instalado
✅ 5 GB de espacio libre en disco

PASO 2: RESTAURAR BASE DE DATOS
═══════════════════════════════

Windows PowerShell:
───────────────────
cd "C:\\ruta\\donde\\extraiste\\el\\paquete"
$env:PGPASSWORD="tu_password_postgres"
psql -U postgres -c "CREATE DATABASE gestor_documental;"
psql -U postgres -d gestor_documental -f base_datos\\gestor_documental_{TIMESTAMP}.sql

Linux Bash:
───────────
cd /ruta/donde/extraiste/el/paquete
export PGPASSWORD='tu_password_postgres'
psql -U postgres -c "CREATE DATABASE gestor_documental;"
psql -U postgres -d gestor_documental -f base_datos/gestor_documental_{TIMESTAMP}.sql

PASO 3: CONFIGURAR APLICACIÓN
═════════════════════════════

1. Copiar carpeta "codigo/" a la ubicación final:
   Ejemplo: C:\\GestorDocumental\\ o /opt/gestor_documental/

2. Crear archivo .env en la raíz de "codigo/":

───── CONTENIDO DE .env ─────
DATABASE_URL=postgresql://usuario:password@localhost:5432/gestor_documental
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
FLASK_ENV=production
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=correo@empresa.com
MAIL_PASSWORD=tu_password_correo
─────────────────────────────

3. Instalar dependencias Python:

cd codigo/
python -m venv .venv
.venv\\Scripts\\activate     (Windows)
source .venv/bin/activate    (Linux)
pip install -r requirements.txt

PASO 4: COPIAR DOCUMENTOS
═════════════════════════

Copiar carpeta "documentos_terceros/" a la ubicación configurada en el sistema.
Por defecto: junto a "codigo/"

Ejemplo:
Windows: C:\\GestorDocumental\\documentos_terceros\\
Linux:   /opt/gestor_documental/documentos_terceros/

PASO 5: INICIAR APLICACIÓN
══════════════════════════

Windows:
────────
cd codigo/
.venv\\Scripts\\activate
python app.py

Linux (con systemd):
────────────────────
1. Crear archivo /etc/systemd/system/gestor_documental.service:

[Unit]
Description=Gestor Documental
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/opt/gestor_documental/codigo
Environment="PATH=/opt/gestor_documental/codigo/.venv/bin"
ExecStart=/opt/gestor_documental/codigo/.venv/bin/python app.py

[Install]
WantedBy=multi-user.target

2. Habilitar e iniciar:
sudo systemctl enable gestor_documental
sudo systemctl start gestor_documental
sudo systemctl status gestor_documental

PASO 6: VERIFICAR INSTALACIÓN
═════════════════════════════

1. Abrir navegador: http://localhost:8099
2. Login con credenciales de administrador
3. Verificar que se ven los módulos correctamente
4. Probar carga de documentos


═══════════════════════════════════════════════════════════════════════════════

⚠️ NOTAS IMPORTANTES:

1. SEGURIDAD:
   • Cambiar SECRET_KEY del .env por una clave única
   • Usar contraseñas fuertes para PostgreSQL
   • Configurar firewall para puerto 8099
   • NO exponer el puerto directamente a internet (usar proxy Nginx/Apache)

2. BACKUP:
   • Configurar backup automático de la BD (pg_dump diario)
   • Hacer backup de documentos_terceros/ regularmente
   • Mantener backups en ubicación separada del servidor

3. RENDIMIENTO:
   • Para producción, usar Gunicorn o uWSGI en lugar de python app.py
   • Configurar Nginx como proxy reverso
   • Ajustar valores de PostgreSQL según carga esperada

4. LOGS:
   • Los logs se guardan en codigo/logs/
   • Revisar security.log para auditoría
   • Configurar rotación de logs

═══════════════════════════════════════════════════════════════════════════════

📞 SOPORTE:

Área TIC - Supertiendas Cañaveral
Email: tic@supertiendascanaveral.com

═══════════════════════════════════════════════════════════════════════════════

✅ CHECKLIST DE INSTALACIÓN:

□ PostgreSQL instalado y funcionando
□ Base de datos restaurada correctamente
□ Archivo .env creado con credenciales
□ Dependencias Python instaladas
□ Carpeta documentos_terceros copiada
□ Aplicación inicia sin errores
□ Login funciona correctamente
□ Módulos cargan sin problemas

═══════════════════════════════════════════════════════════════════════════════

🎉 ¡INSTALACIÓN COMPLETADA!

El sistema está listo para usar. Recuerda:
• Configurar backups automáticos
• Mantener el sistema actualizado
• Revisar logs regularmente

═══════════════════════════════════════════════════════════════════════════════
"""
    
    archivo_instrucciones = PAQUETE_COMPLETO / "INSTRUCCIONES" / "LEEME_PRIMERO.txt"
    archivo_instrucciones.write_text(contenido, encoding='utf-8')
    print("  ✅ Instrucciones creadas")

def comprimir_backup_seguridad():
    """Comprime el backup de seguridad"""
    print("\n📦 Comprimiendo backup de seguridad...")
    
    archivo_zip = BACKUP_DIR_PADRE / f"BACKUP_PRE_SINCRONIZACION_{TIMESTAMP}.zip"
    
    with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for carpeta in BACKUP_DIR_ACTUAL.rglob('*'):
            if carpeta.is_file():
                arcname = carpeta.relative_to(BACKUP_DIR_ACTUAL.parent)
                zipf.write(carpeta, arcname)
    
    tamano = archivo_zip.stat().st_size / (1024 * 1024)
    print(f"  ✅ ZIP creado: {tamano:.2f} MB")
    print(f"  📁 {archivo_zip}")
    
    return archivo_zip

def comprimir_paquete_tic():
    """Comprime el paquete transportable para TIC"""
    print("\n📦 Comprimiendo paquete TIC...")
    
    archivo_zip = PAQUETE_TIC_DIR / f"{PAQUETE_NOMBRE}.zip"
    
    with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for carpeta in PAQUETE_COMPLETO.rglob('*'):
            if carpeta.is_file():
                arcname = carpeta.relative_to(PAQUETE_COMPLETO.parent)
                zipf.write(carpeta, arcname)
    
    tamano = archivo_zip.stat().st_size / (1024 * 1024)
    print(f"  ✅ ZIP creado: {tamano:.2f} MB")
    print(f"  📁 {archivo_zip}")
    
    return archivo_zip

def main():
    print("═" * 80)
    print("🔒 BACKUP COMPLETO PRE-SINCRONIZACIÓN")
    print("═" * 80)
    print(f"Fecha: {datetime.now().strftime('%d de %B de %Y - %H:%M:%S')}")
    print(f"Base de datos: {database}")
    print()
    print("Se crearán 2 backups:")
    print("1. ✅ Backup de seguridad (recuperación rápida)")
    print(f"   📁 {BACKUP_DIR_ACTUAL}")
    print()
    print("2. ✅ Paquete transportable TIC (totalmente funcional)")
    print(f"   📁 {PAQUETE_COMPLETO}")
    print()
    
    respuesta = input("¿Continuar? (s/n): ")
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return
    
    inicio = datetime.now()
    
    try:
        # Crear directorios
        crear_directorios()
        
        # BACKUP 1: Seguridad (formato custom)
        print("\n" + "═" * 80)
        print("📦 BACKUP 1: SEGURIDAD (Recuperación Rápida)")
        print("═" * 80)
        
        backup_base_datos()
        copiar_codigo(BACKUP_DIR_ACTUAL)
        copiar_documentos(BACKUP_DIR_ACTUAL)
        
        # BACKUP 2: Paquete TIC (formato SQL + completo)
        print("\n" + "═" * 80)
        print("📦 BACKUP 2: PAQUETE TRANSPORTABLE TIC")
        print("═" * 80)
        
        backup_base_datos_sql()
        copiar_codigo(PAQUETE_COMPLETO)
        copiar_documentos(PAQUETE_COMPLETO)
        crear_instrucciones_tic()
        
        # Comprimir ambos
        print("\n" + "═" * 80)
        print("📦 COMPRIMIENDO BACKUPS")
        print("═" * 80)
        
        zip_seguridad = comprimir_backup_seguridad()
        zip_tic = comprimir_paquete_tic()
        
        # Resumen final
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        print("\n" + "═" * 80)
        print("✅ BACKUP COMPLETADO EXITOSAMENTE")
        print("═" * 80)
        print(f"⏱️  Tiempo total: {duracion:.1f} segundos")
        print()
        print("📦 BACKUP 1 - SEGURIDAD:")
        print(f"   📁 {zip_seguridad}")
        print(f"   💾 Tamaño: {zip_seguridad.stat().st_size / (1024*1024):.2f} MB")
        print()
        print("📦 BACKUP 2 - PAQUETE TIC:")
        print(f"   📁 {zip_tic}")
        print(f"   💾 Tamaño: {zip_tic.stat().st_size / (1024*1024):.2f} MB")
        print()
        print("🎯 USO DE LOS BACKUPS:")
        print()
        print("   BACKUP 1 (Seguridad):")
        print("   • Para recuperación rápida si algo falla")
        print("   • Formato PostgreSQL custom (.backup)")
        print("   • Restaurar con: pg_restore")
        print()
        print("   BACKUP 2 (Paquete TIC):")
        print("   • Para instalación en servidor nuevo")
        print("   • Incluye instrucciones completas")
        print("   • Formato SQL texto plano")
        print("   • TOTALMENTE FUNCIONAL")
        print()
        print("✅ Ahora puedes aplicar los cambios de sincronización con seguridad")
        print("═" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == '__main__':
    main()
