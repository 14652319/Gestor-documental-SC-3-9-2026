"""
EXPORTAR BASE DE DATOS COMPLETA
Exporta todas las tablas con todos los datos
"""
import os
import subprocess
from datetime import datetime

# Configuración
DESTINO = r"C:\Users\Usuario\Documents\Gestor documentalv4.3.2026"
USUARIO_BD = "postgres"
PASSWORD_BD = "G3st0radm$2025."
NOMBRE_BD = "gestor_documental"
PG_DUMP = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

print("\n" + "="*80)
print("   EXPORTACIÓN DE BASE DE DATOS COMPLETA")
print("   Gestor Documental - PostgreSQL")
print("="*80)
print(f"\nBase de datos: {NOMBRE_BD}")
print(f"Destino: {DESTINO}")
print("\n📊 Se exportará:")
print("   ✅ TODAS las tablas (schema completo)")
print("   ✅ TODOS los datos (INSERT statements)")
print("   ✅ Usuarios, terceros, facturas, relaciones, etc.")
print("\n⏱️  Tiempo estimado: 3-5 minutos")
print("💾 Tamaño estimado: ~100-120 MB\n")

input("Presione ENTER para iniciar exportación...")

# Crear directorio destino
os.makedirs(DESTINO, exist_ok=True)
print(f"\n[✓] Directorio creado: {DESTINO}\n")

# ====================
# EXPORTAR FORMATO SQL
# ====================
print("="*80)
print("PASO 1/2: Exportando en formato SQL (texto plano)...")
print("="*80 + "\n")

archivo_sql = os.path.join(DESTINO, "gestor_documental_COMPLETO.sql")

comando_sql = [
    PG_DUMP,
    "-U", USUARIO_BD,
    "-h", "localhost",
    "-p", "5432",
    "-F", "p",  # Formato plain text (SQL)
    "--inserts",  # Usar INSERT (más compatible)
    "--no-owner",  # Sin dueño específico
    "--no-acl",    # Sin permisos específicos
    "--verbose",   # Modo verbose
    "-f", archivo_sql,
    NOMBRE_BD
]

try:
    print("[→] Conectando a PostgreSQL...")
    print(f"[→] Exportando desde: {NOMBRE_BD}")
    print(f"[→] Guardando en: {archivo_sql}\n")
    
    env = os.environ.copy()
    env['PGPASSWORD'] = PASSWORD_BD
    
    resultado = subprocess.run(
        comando_sql, 
        env=env, 
        capture_output=True, 
        text=True,
        timeout=600  # 10 minutos máximo
    )
    
    if resultado.returncode == 0:
        tamanio = os.path.getsize(archivo_sql) / (1024 * 1024)
        print(f"\n[✓✓✓] BACKUP SQL CREADO EXITOSAMENTE")
        print(f"      Archivo: gestor_documental_COMPLETO.sql")
        print(f"      Tamaño: {tamanio:.2f} MB\n")
    else:
        print(f"\n[✗] Error en backup SQL:")
        print(resultado.stderr)
        exit(1)
        
except subprocess.TimeoutExpired:
    print("\n[✗] ERROR: Timeout - La exportación tardó más de 10 minutos")
    exit(1)
except Exception as e:
    print(f"\n[✗] ERROR exportando SQL: {e}")
    exit(1)

# =======================
# EXPORTAR FORMATO CUSTOM
# =======================
print("="*80)
print("PASO 2/2: Exportando en formato CUSTOM (comprimido)...")
print("="*80 + "\n")

archivo_custom = os.path.join(DESTINO, "gestor_documental_COMPLETO.backup")

comando_custom = [
    PG_DUMP,
    "-U", USUARIO_BD,
    "-h", "localhost",
    "-p", "5432",
    "-F", "c",  # Formato custom (comprimido)
    "-b",       # Incluir blobs
    "--no-owner",
    "--no-acl",
    "--verbose",
    "-f", archivo_custom,
    NOMBRE_BD
]

try:
    print("[→] Conectando a PostgreSQL...")
    print(f"[→] Exportando desde: {NOMBRE_BD}")
    print(f"[→] Guardando en: {archivo_custom}\n")
    
    resultado = subprocess.run(
        comando_custom,
        env=env,
        capture_output=True,
        text=True,
        timeout=600
    )
    
    if resultado.returncode == 0:
        tamanio = os.path.getsize(archivo_custom) / (1024 * 1024)
        print(f"\n[✓✓✓] BACKUP CUSTOM CREADO EXITOSAMENTE")
        print(f"      Archivo: gestor_documental_COMPLETO.backup")
        print(f"      Tamaño: {tamanio:.2f} MB\n")
    else:
        print(f"\n[!] Advertencia en backup CUSTOM:")
        print(resultado.stderr)
        print("\n[✓] Backup SQL está disponible como alternativa\n")
        
except subprocess.TimeoutExpired:
    print("\n[!] ADVERTENCIA: Timeout en backup CUSTOM")
    print("[✓] Backup SQL está disponible como alternativa\n")
except Exception as e:
    print(f"\n[!] Advertencia exportando CUSTOM: {e}")
    print("[✓] Backup SQL está disponible como alternativa\n")

# ==================
# CREAR DOCUMENTACIÓN
# ==================
print("="*80)
print("Creando documentación...")
print("="*80 + "\n")

documentacion = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║        BASE DE DATOS COMPLETA - GESTOR DOCUMENTAL v4.3.2026         ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

Fecha de exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Base de datos: {NOMBRE_BD}
PostgreSQL: 18

═══════════════════════════════════════════════════════════════════════
   📊 CONTENIDO DE LA BASE DE DATOS
═══════════════════════════════════════════════════════════════════════

Este backup contiene TODAS las tablas con TODOS los datos:

✅ usuarios                    → Todos los usuarios registrados
✅ terceros                    → Todos los proveedores/terceros  
✅ terceros_extendidos         → Información extendida de terceros
✅ facturas_recibidas          → Todas las facturas recibidas
✅ facturas_temporales         → Facturas en proceso
✅ relaciones_facturas         → Relaciones de facturas digitales
✅ recepciones_digitales       → Recepciones con firma digital
✅ causaciones                 → Causaciones contables
✅ permisos_usuarios           → Permisos configurados
✅ configuracion               → Configuración del sistema
✅ maestro_dian_vs_erp         → Datos DIAN vs ERP
✅ documentos_tercero          → Registro de documentos
✅ solicitudes_registro        → Solicitudes en proceso
✅ accesos                     → Log de accesos
✅ ips_blancas                 → IPs autorizadas
✅ ips_negras                  → IPs bloqueadas
✅ tokens_recuperacion         → Tokens de recuperación
✅ ... y TODAS las demás tablas del sistema

═══════════════════════════════════════════════════════════════════════
   📦 ARCHIVOS GENERADOS
═══════════════════════════════════════════════════════════════════════

1. gestor_documental_COMPLETO.sql         (~107 MB)
   - Formato: SQL texto plano
   - Contiene: Schema + datos (INSERT statements)
   - Ventaja: Más compatible, fácil de editar
   - Uso: Restauración en cualquier PostgreSQL

2. gestor_documental_COMPLETO.backup      (~17 MB)
   - Formato: CUSTOM comprimido
   - Contiene: Schema + datos (formato binario)
   - Ventaja: Más rápido, menor tamaño
   - Uso: Restauración con pg_restore

═══════════════════════════════════════════════════════════════════════
   🔄 CÓMO RESTAURAR LA BASE DE DATOS
═══════════════════════════════════════════════════════════════════════

OPCIÓN 1: Restaurar con formato SQL (RECOMENDADO)
──────────────────────────────────────────────────

1. Crear base de datos nueva:
   psql -U postgres
   CREATE DATABASE gestor_documental;
   \\q

2. Restaurar backup:
   psql -U postgres -d gestor_documental -f gestor_documental_COMPLETO.sql

3. Verificar:
   psql -U postgres -d gestor_documental -c "SELECT COUNT(*) FROM usuarios;"


OPCIÓN 2: Restaurar con formato CUSTOM (MÁS RÁPIDO)
────────────────────────────────────────────────────

1. Crear base de datos nueva:
   psql -U postgres -c "CREATE DATABASE gestor_documental;"

2. Restaurar backup:
   pg_restore -U postgres -d gestor_documental -v gestor_documental_COMPLETO.backup

3. Verificar:
   psql -U postgres -d gestor_documental -c "SELECT COUNT(*) FROM usuarios;"

═══════════════════════════════════════════════════════════════════════
   ⚙️ RESTAURACIÓN AUTOMÁTICA (con instalador)
═══════════════════════════════════════════════════════════════════════

Si el código está en:
\\\\192.168.11.250\\tic\\Infraestructura\\Nueva carpeta\\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059

1. Copiar estos archivos de BD a esa ubicación:
   - gestor_documental_COMPLETO.sql
   - gestor_documental_COMPLETO.backup

2. Crear un instalador INSTALAR.bat con este contenido:

@echo off
echo Instalando Gestor Documental...
echo.
echo [1/3] Creando entorno virtual...
python -m venv .venv
call .venv\\Scripts\\activate.bat
pip install -r requirements.txt
echo.
echo [2/3] Creando base de datos...
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;"
psql -U postgres -c "CREATE DATABASE gestor_documental;"
echo.
echo [3/3] Restaurando datos...
psql -U postgres -d gestor_documental -f gestor_documental_COMPLETO.sql
echo.
echo ✓ Instalación completa!
pause

═══════════════════════════════════════════════════════════════════════
   ✅ VERIFICACIÓN DESPUÉS DE RESTAURAR
═══════════════════════════════════════════════════════════════════════

Ejecutar estos comandos para verificar que todo está bien:

1. Contar usuarios:
   psql -U postgres -d gestor_documental -c "SELECT COUNT(*) FROM usuarios;"

2. Contar terceros:
   psql -U postgres -d gestor_documental -c "SELECT COUNT(*) FROM terceros;"

3. Contar facturas:
   psql -U postgres -d gestor_documental -c "SELECT COUNT(*) FROM facturas_recibidas;"

4. Listar tablas:
   psql -U postgres -d gestor_documental -c "\\dt"

═══════════════════════════════════════════════════════════════════════
   📍 UBICACIÓN DE LOS ARCHIVOS
═══════════════════════════════════════════════════════════════════════

Destino: {DESTINO}

Archivos:
├── gestor_documental_COMPLETO.sql        → Backup SQL
├── gestor_documental_COMPLETO.backup     → Backup CUSTOM
└── LEEME_BASE_DATOS.txt                  → Este archivo

═══════════════════════════════════════════════════════════════════════
   ⚠️  IMPORTANTE
═══════════════════════════════════════════════════════════════════════

• Estos backups contienen TODOS los datos del sistema en producción
• Incluyen contraseñas hasheadas (bcrypt) - seguras pero sensibles
• Mantener estos archivos en ubicación segura
• NO compartir públicamente
• Hacer backups regulares (diario/semanal)

═══════════════════════════════════════════════════════════════════════
   🔒 CREDENCIALES
═══════════════════════════════════════════════════════════════════════

Por defecto, la restauración usará:
- Usuario PostgreSQL: postgres
- Base de datos: gestor_documental

Si necesitas diferentes credenciales, edita los comandos de restauración.

═══════════════════════════════════════════════════════════════════════
   📞 SOPORTE
═══════════════════════════════════════════════════════════════════════

Documentación completa:
- .github/copilot-instructions.md (en el proyecto)

Scripts útiles:
- verificar_usuario.py
- check_user_status.py

Logs:
- logs/security.log
- logs/app.log

═══════════════════════════════════════════════════════════════════════

Base de datos: PostgreSQL 18
Framework: Flask 3.0
Python: 3.8+

Backup generado automáticamente
Sistema: Gestor Documental v4.3.2026
Empresa: Supertiendas Cañaveral

═══════════════════════════════════════════════════════════════════════
"""

archivo_doc = os.path.join(DESTINO, "LEEME_BASE_DATOS.txt")
with open(archivo_doc, 'w', encoding='utf-8') as f:
    f.write(documentacion)

print("[✓] LEEME_BASE_DATOS.txt creado\n")

# =============
# RESUMEN FINAL
# =============
print("\n" + "="*80)
print("   ✅✅✅ EXPORTACIÓN COMPLETADA EXITOSAMENTE ✅✅✅")
print("="*80 + "\n")

print(f"📁 Ubicación: {DESTINO}\n")
print("📦 Archivos creados:")

if os.path.exists(archivo_sql):
    tamanio = os.path.getsize(archivo_sql) / (1024 * 1024)
    print(f"   ✅ gestor_documental_COMPLETO.sql ({tamanio:.2f} MB)")
    
if os.path.exists(archivo_custom):
    tamanio = os.path.getsize(archivo_custom) / (1024 * 1024)
    print(f"   ✅ gestor_documental_COMPLETO.backup ({tamanio:.2f} MB)")
    
print(f"   ✅ LEEME_BASE_DATOS.txt")
print()
print("📊 Contenido:")
print("   ✅ TODAS las tablas del sistema")
print("   ✅ TODOS los datos (usuarios, terceros, facturas, etc.)")
print("   ✅ Schema completo")
print()
print("🔄 Para restaurar:")
print("   Ver instrucciones en: LEEME_BASE_DATOS.txt")
print()
print("📍 Código completo está en:")
print("   \\\\192.168.11.250\\tic\\Infraestructura\\Nueva carpeta\\")
print("   GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\\")
print()

input("\nPresione ENTER para salir...")
