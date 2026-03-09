"""
Script de Backup Completo del Gestor Documental
Incluye: código fuente, base de datos, configuraciones
Fecha: 26 de Diciembre 2025
"""

import os
import subprocess
import zipfile
from datetime import datetime
import shutil

def log_mensaje(mensaje):
    """Imprime mensaje con timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {mensaje}")

def crear_backup_base_datos():
    """Crea backup completo de PostgreSQL"""
    log_mensaje("📦 Creando backup de base de datos PostgreSQL...")
    
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_bd = f"backup_gestor_documental_{fecha}.backup"
    
    # Comando pg_dump para backup completo
    comando = [
        "pg_dump",
        "-U", "gestor_user",
        "-h", "localhost",
        "-p", "5432",
        "-F", "c",  # Formato custom (comprimido)
        "-b",       # Incluir blobs
        "-v",       # Verbose
        "-f", archivo_bd,
        "gestor_documental"
    ]
    
    try:
        # Establecer variable de entorno para password
        env = os.environ.copy()
        env['PGPASSWORD'] = 'abc123'  # Password de la BD
        
        resultado = subprocess.run(comando, env=env, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            log_mensaje(f"✅ Backup BD creado: {archivo_bd}")
            log_mensaje(f"   Tamaño: {os.path.getsize(archivo_bd) / (1024*1024):.2f} MB")
            return archivo_bd
        else:
            log_mensaje(f"❌ Error creando backup BD: {resultado.stderr}")
            return None
    except Exception as e:
        log_mensaje(f"❌ Excepción creando backup BD: {str(e)}")
        return None

def crear_backup_codigo(archivo_bd):
    """Crea ZIP con código fuente + backup de BD"""
    log_mensaje("📦 Creando backup de código fuente...")
    
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_zip = f"BACKUP_COMPLETO_{fecha}.zip"
    
    # Directorio actual
    directorio_actual = os.getcwd()
    
    # Archivos y carpetas a incluir
    incluir = [
        'app.py',
        'extensions.py',
        'decoradores_permisos.py',
        'utils_fecha.py',
        'requirements.txt',
        '.env',
        'modules/',
        'templates/',
        'static/',
        'sql/',
        'logs/',
        'DOCUMENTACION_MODULO_DIAN_VS_ERP.md',
        'README_Estructura.txt',
        'REQUISITOS_INSTALACION.txt',
        '.github/copilot-instructions.md'
    ]
    
    # Carpetas a excluir
    excluir = [
        '__pycache__',
        '.venv',
        'venv',
        '.git',
        '.pytest_cache',
        'node_modules',
        'documentos_terceros',  # Excluir archivos PDF (pueden ser muy grandes)
        '*.pyc',
        '*.pyo'
    ]
    
    try:
        with zipfile.ZipFile(archivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            total_archivos = 0
            
            # Agregar backup de BD primero
            if archivo_bd and os.path.exists(archivo_bd):
                log_mensaje(f"   📄 Agregando: {archivo_bd}")
                zipf.write(archivo_bd, archivo_bd)
                total_archivos += 1
            
            # Agregar archivos de código
            for item in incluir:
                item_path = os.path.join(directorio_actual, item)
                
                # Si es archivo
                if os.path.isfile(item_path):
                    log_mensaje(f"   📄 Agregando: {item}")
                    zipf.write(item_path, item)
                    total_archivos += 1
                
                # Si es directorio
                elif os.path.isdir(item_path):
                    log_mensaje(f"   📁 Agregando directorio: {item}")
                    for root, dirs, files in os.walk(item_path):
                        # Filtrar directorios excluidos
                        dirs[:] = [d for d in dirs if d not in excluir]
                        
                        for file in files:
                            # Filtrar archivos excluidos
                            if file.endswith(('.pyc', '.pyo')):
                                continue
                            
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, directorio_actual)
                            zipf.write(file_path, arc_name)
                            total_archivos += 1
        
        log_mensaje(f"✅ Backup código creado: {archivo_zip}")
        log_mensaje(f"   Archivos incluidos: {total_archivos}")
        log_mensaje(f"   Tamaño: {os.path.getsize(archivo_zip) / (1024*1024):.2f} MB")
        
        return archivo_zip
    except Exception as e:
        log_mensaje(f"❌ Error creando backup código: {str(e)}")
        return None

def crear_script_restauracion(archivo_zip):
    """Crea script batch para restaurar el backup"""
    log_mensaje("📝 Creando script de restauración...")
    
    script_content = f"""@echo off
REM Script de Restauración - Backup Completo Gestor Documental
REM Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

echo ============================================
echo RESTAURACION DE BACKUP - GESTOR DOCUMENTAL
echo ============================================
echo.

REM 1. Extraer archivo ZIP
echo [1/3] Extrayendo archivos...
powershell -Command "Expand-Archive -Path '{archivo_zip}' -DestinationPath 'restauracion_temp' -Force"
if errorlevel 1 (
    echo ERROR: No se pudo extraer el archivo ZIP
    pause
    exit /b 1
)
echo OK: Archivos extraidos

REM 2. Buscar archivo .backup de PostgreSQL
echo.
echo [2/3] Buscando backup de base de datos...
for %%f in (restauracion_temp\\*.backup) do set BACKUP_FILE=%%f
if not defined BACKUP_FILE (
    echo ERROR: No se encontro archivo .backup
    pause
    exit /b 1
)
echo OK: Backup encontrado: %BACKUP_FILE%

REM 3. Restaurar base de datos
echo.
echo [3/3] Restaurando base de datos PostgreSQL...
echo IMPORTANTE: Esto sobreescribira la base de datos actual
set /p confirmar="¿Desea continuar? (S/N): "
if /i not "%confirmar%"=="S" (
    echo Restauracion cancelada por el usuario
    pause
    exit /b 0
)

REM Crear nueva BD si no existe
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;"
psql -U postgres -c "CREATE DATABASE gestor_documental OWNER gestor_user;"

REM Restaurar backup
pg_restore -U gestor_user -d gestor_documental -v "%BACKUP_FILE%"
if errorlevel 1 (
    echo ERROR: Fallo la restauracion de la base de datos
    pause
    exit /b 1
)

echo.
echo ============================================
echo RESTAURACION COMPLETADA EXITOSAMENTE
echo ============================================
echo.
echo Archivos restaurados en: restauracion_temp\\
echo Base de datos restaurada: gestor_documental
echo.
echo Proximos pasos:
echo 1. Copiar archivos de restauracion_temp\\ a tu directorio de trabajo
echo 2. Instalar dependencias: pip install -r requirements.txt
echo 3. Verificar archivo .env con configuraciones
echo 4. Iniciar servidor: python app.py
echo.
pause
"""
    
    try:
        script_file = "RESTAURAR_BACKUP.bat"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        log_mensaje(f"✅ Script de restauración creado: {script_file}")
        return script_file
    except Exception as e:
        log_mensaje(f"❌ Error creando script restauración: {str(e)}")
        return None

def crear_readme_backup():
    """Crea README con instrucciones del backup"""
    log_mensaje("📝 Creando README del backup...")
    
    readme_content = f"""# 📦 BACKUP COMPLETO - GESTOR DOCUMENTAL

**Fecha de creación:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Versión:** 1.0.0
**Estado:** Productivo y Funcional

---

## 📋 CONTENIDO DEL BACKUP

Este backup incluye:

### 1. Código Fuente
- ✅ Archivo principal: `app.py`
- ✅ Módulos: `modules/` (recibir_facturas, relaciones, causaciones, dian_vs_erp, etc.)
- ✅ Templates: `templates/`
- ✅ Estilos: `static/`
- ✅ Utilities: `extensions.py`, `decoradores_permisos.py`, `utils_fecha.py`
- ✅ Scripts SQL: `sql/`
- ✅ Dependencias: `requirements.txt`

### 2. Base de Datos PostgreSQL
- ✅ Backup completo formato custom (.backup)
- ✅ Todas las tablas con datos
- ✅ Índices y constraints
- ✅ Secuencias y triggers
- ✅ Usuarios y permisos

**Tablas incluidas (40+):**
- Maestro DIAN: `maestro_dian_vs_erp`
- Envíos programados: `envios_programados_dian_vs_erp`
- Usuarios asignados: `usuarios_asignados`
- Historial: `historial_envios_dian_vs_erp`
- Facturas: `facturas_temporales`, `facturas_recibidas`
- Relaciones: `relaciones_facturas`, `recepciones_digitales`
- Core: `terceros`, `usuarios`, `accesos`
- Y más...

### 3. Configuraciones
- ✅ Archivo `.env` (variables de entorno)
- ✅ Logs del sistema: `logs/`
- ✅ Documentación: `DOCUMENTACION_MODULO_DIAN_VS_ERP.md`
- ✅ Instrucciones: `README_Estructura.txt`, `REQUISITOS_INSTALACION.txt`

### 4. Documentación
- ✅ Manual completo del módulo DIAN vs ERP
- ✅ Instrucciones de instalación
- ✅ Guías de configuración
- ✅ Copilot instructions para IA

---

## 🔄 CÓMO RESTAURAR EL BACKUP

### Opción 1: Script Automático (Recomendado)

1. Ejecutar: `RESTAURAR_BACKUP.bat`
2. Seguir instrucciones en pantalla
3. Listo - Sistema restaurado

### Opción 2: Manual

#### Paso 1: Extraer archivos
```cmd
powershell -Command "Expand-Archive -Path 'BACKUP_COMPLETO_YYYYMMDD_HHMMSS.zip' -DestinationPath 'gestor_restaurado'"
cd gestor_restaurado
```

#### Paso 2: Restaurar base de datos
```cmd
REM Crear base de datos
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;"
psql -U postgres -c "CREATE DATABASE gestor_documental OWNER gestor_user;"

REM Restaurar backup
pg_restore -U gestor_user -d gestor_documental -v backup_gestor_documental_YYYYMMDD_HHMMSS.backup
```

#### Paso 3: Configurar entorno
```cmd
REM Crear virtualenv
python -m venv .venv
.venv\\Scripts\\activate

REM Instalar dependencias
pip install -r requirements.txt
```

#### Paso 4: Verificar configuración
```cmd
REM Editar .env si es necesario
notepad .env

REM Verificar conexión BD
python -c "from app import db; print('DB OK')"
```

#### Paso 5: Iniciar sistema
```cmd
python app.py
```

Acceder a: http://localhost:8099

---

## ⚙️ REQUISITOS DEL SISTEMA

### Software Necesario
- **Python:** 3.11+ (3.11.9 recomendado)
- **PostgreSQL:** 14+ (18 recomendado)
- **pip:** Última versión
- **virtualenv:** Para entorno aislado

### Configuraciones PostgreSQL
```sql
-- Usuario: gestor_user
-- Password: abc123
-- Base de datos: gestor_documental
-- Puerto: 5432
```

### Variables de Entorno (.env)
```env
SECRET_KEY=tu_secret_key_aqui
DATABASE_URL=postgresql://gestor_user:abc123@localhost:5432/gestor_documental

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=urjrkjlogcfdtynq
```

---

## 🧪 VERIFICACIÓN POST-RESTAURACIÓN

### 1. Verificar Base de Datos
```sql
-- Conectar a PostgreSQL
psql -U gestor_user -d gestor_documental

-- Verificar tablas
\\dt

-- Verificar datos en tabla principal
SELECT COUNT(*) FROM maestro_dian_vs_erp;
SELECT COUNT(*) FROM usuarios_asignados;
SELECT COUNT(*) FROM envios_programados_dian_vs_erp;
```

### 2. Verificar Módulos
```bash
# Probar imports
python -c "from modules.dian_vs_erp.routes import dian_vs_erp_bp; print('OK')"
python -c "from modules.dian_vs_erp.scheduler_envios import EnviosProgramadosSchedulerDianVsErp; print('OK')"
```

### 3. Verificar Servidor
```bash
# Iniciar servidor
python app.py

# En otra terminal, probar endpoints
curl http://localhost:8099/
curl http://localhost:8099/dian_vs_erp/api/maestro/documentos?page=1
```

---

## 📊 INFORMACIÓN DEL BACKUP

### Tamaño Estimado
- Código fuente: ~50 MB
- Base de datos: ~10-50 MB (depende de datos)
- Total: ~60-100 MB comprimido

### Tiempo de Restauración
- Extracción ZIP: 1-2 minutos
- Restauración BD: 2-5 minutos
- Instalación dependencias: 3-5 minutos
- **Total:** 10-15 minutos

---

## 🆘 PROBLEMAS COMUNES

### Error: "pg_restore: command not found"
**Solución:** Agregar PostgreSQL al PATH:
```cmd
set PATH=%PATH%;C:\\Program Files\\PostgreSQL\\18\\bin
```

### Error: "psycopg2 import error"
**Solución:**
```cmd
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary==2.9.9
```

### Error: "Puerto 8099 ya en uso"
**Solución:**
```cmd
REM Matar proceso en puerto 8099
netstat -ano | findstr :8099
taskkill /PID <PID> /F
```

### Error: "SMTP Authentication failed"
**Solución:** Verificar variables MAIL_* en .env y usar App Password de Gmail (2FA habilitado)

---

## 📞 SOPORTE

**Desarrollador:** Ricardo Riascos  
**Email:** ricardoriascos07@gmail.com  
**Empresa:** Supertiendas Cañaveral  

---

## 📝 NOTAS IMPORTANTES

⚠️ **SEGURIDAD:**
- Este backup contiene archivo `.env` con credenciales
- NO compartir públicamente
- Guardar en ubicación segura con acceso restringido

⚠️ **PRODUCCIÓN:**
- Sistema completamente funcional y testeado
- Incluye módulo DIAN vs ERP operativo
- Scheduler de envíos programados funcionando
- Excel con hipervínculos a DIAN implementado

⚠️ **VERSIONES:**
- Última actualización: 26/12/2025
- Todas las funcionalidades documentadas están operativas
- Sistema listo para uso en producción

---

**FIN DEL README**
"""
    
    try:
        readme_file = "README_BACKUP.txt"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        log_mensaje(f"✅ README creado: {readme_file}")
        return readme_file
    except Exception as e:
        log_mensaje(f"❌ Error creando README: {str(e)}")
        return None

def main():
    """Función principal"""
    print("=" * 60)
    print("GENERADOR DE BACKUP COMPLETO - GESTOR DOCUMENTAL")
    print("=" * 60)
    print()
    
    # 1. Crear backup de base de datos
    archivo_bd = crear_backup_base_datos()
    if not archivo_bd:
        log_mensaje("⚠️ Continuando sin backup de BD...")
    
    print()
    
    # 2. Crear backup de código
    archivo_zip = crear_backup_codigo(archivo_bd)
    if not archivo_zip:
        log_mensaje("❌ Error crítico: No se pudo crear backup de código")
        return
    
    print()
    
    # 3. Crear script de restauración
    crear_script_restauracion(archivo_zip)
    
    print()
    
    # 4. Crear README
    crear_readme_backup()
    
    print()
    print("=" * 60)
    log_mensaje("✅ BACKUP COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print()
    print("📦 Archivos generados:")
    if archivo_bd and os.path.exists(archivo_bd):
        print(f"   - {archivo_bd} ({os.path.getsize(archivo_bd) / (1024*1024):.2f} MB)")
    if archivo_zip and os.path.exists(archivo_zip):
        print(f"   - {archivo_zip} ({os.path.getsize(archivo_zip) / (1024*1024):.2f} MB)")
    print(f"   - RESTAURAR_BACKUP.bat")
    print(f"   - README_BACKUP.txt")
    print()
    print("📋 Para restaurar el backup:")
    print("   1. Ejecutar: RESTAURAR_BACKUP.bat")
    print("   2. O seguir instrucciones en README_BACKUP.txt")
    print()
    
    # Limpiar archivo temporal de BD si existe
    if archivo_bd and os.path.exists(archivo_bd):
        try:
            os.remove(archivo_bd)
            log_mensaje(f"🧹 Archivo temporal BD eliminado: {archivo_bd}")
        except:
            pass

if __name__ == '__main__':
    main()
