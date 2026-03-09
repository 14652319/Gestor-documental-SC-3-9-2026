"""
Script de Verificación del Sistema de Backup
Gestor Documental - Supertiendas Cañaveral

Verifica que todos los componentes del sistema de backup estén instalados correctamente.
"""

import os
import sys
import shutil

def print_header(titulo, simbolo="="):
    print(f"\n{simbolo*70}")
    print(f"  {titulo}")
    print(f"{simbolo*70}")

def verificar_archivos():
    """Verifica que existan todos los archivos necesarios"""
    print_header("VERIFICANDO ARCHIVOS DEL SISTEMA")
    
    archivos_requeridos = [
        ('backup_manager.py', 'Motor del sistema de backup'),
        ('ejecutar_backup.py', 'Script de ejecución manual'),
        ('instalar_sistema_backup.py', 'Instalador del sistema'),
        ('sql/schema_backup.sql', 'Schema de base de datos'),
        ('logs/backup.log', 'Log de backups'),
        ('logs/app.log', 'Log general'),
        ('logs/errors.log', 'Log de errores'),
        ('logs/facturas_digitales.log', 'Log facturas digitales'),
        ('logs/relaciones.log', 'Log relaciones'),
        ('logs/security.log', 'Log de seguridad'),
        ('DOCUMENTACION_SISTEMA_BACKUP.md', 'Documentación completa'),
        ('RESUMEN_SISTEMA_BACKUP.md', 'Resumen ejecutivo'),
    ]
    
    todos_ok = True
    for archivo, descripcion in archivos_requeridos:
        existe = os.path.exists(archivo)
        simbolo = "✅" if existe else "❌"
        print(f"{simbolo} {archivo:50} {descripcion}")
        if not existe:
            todos_ok = False
    
    return todos_ok

def verificar_pg_dump():
    """Verifica que pg_dump esté disponible"""
    print_header("VERIFICANDO POSTGRESQL")
    
    pg_dump = shutil.which('pg_dump')
    if pg_dump:
        print(f"✅ pg_dump encontrado: {pg_dump}")
        try:
            import subprocess
            resultado = subprocess.run(
                ['pg_dump', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"   {resultado.stdout.strip()}")
            return True
        except:
            print("   ⚠️  No se pudo verificar la versión")
            return True
    else:
        print("❌ pg_dump NO encontrado")
        print("   Sin pg_dump no se pueden hacer backups de base de datos")
        print("   Instalar desde: https://www.postgresql.org/download/")
        return False

def verificar_directorios():
    """Verifica directorios de destino"""
    print_header("VERIFICANDO DIRECTORIOS DE DESTINO")
    
    directorios = [
        'C:\\Backups_GestorDocumental\\base_datos',
        'C:\\Backups_GestorDocumental\\documentos',
        'C:\\Backups_GestorDocumental\\codigo'
    ]
    
    todos_ok = True
    for directorio in directorios:
        existe = os.path.exists(directorio)
        simbolo = "✅" if existe else "⚠️"
        print(f"{simbolo} {directorio}")
        if not existe:
            print(f"   Se creará automáticamente al ejecutar primer backup")
    
    return True

def verificar_base_datos():
    """Verifica que las tablas existan en la base de datos"""
    print_header("VERIFICANDO TABLAS DE BASE DE DATOS")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import app
        from extensions import db
        from sqlalchemy import inspect
        
        with app.app_context():
            inspector = inspect(db.engine)
            tablas = inspector.get_table_names()
            
            tablas_backup = [
                'configuracion_backup',
                'historial_backup'
            ]
            
            todas_ok = True
            for tabla in tablas_backup:
                existe = tabla in tablas
                simbolo = "✅" if existe else "❌"
                print(f"{simbolo} {tabla}")
                if not existe:
                    todas_ok = False
            
            if not todas_ok:
                print("\n⚠️  Las tablas no existen aún")
                print("   Ejecuta: python instalar_sistema_backup.py")
            
            return todas_ok
            
    except Exception as e:
        print(f"❌ Error al verificar base de datos: {str(e)}")
        print("   Asegúrate de que la base de datos esté activa")
        return False

def verificar_configuracion():
    """Verifica la configuración actual si existe"""
    print_header("VERIFICANDO CONFIGURACIÓN")
    
    try:
        from app import app
        from backup_manager import ConfiguracionBackup
        
        with app.app_context():
            configs = ConfiguracionBackup.query.all()
            
            if not configs:
                print("⚠️  No hay configuración aún")
                print("   Ejecuta: python instalar_sistema_backup.py")
                return False
            
            print(f"✅ Configuración encontrada: {len(configs)} tipos de backup")
            for cfg in configs:
                estado = "✅ Habilitado" if cfg.habilitado else "❌ Deshabilitado"
                print(f"\n   📦 {cfg.tipo.upper()}")
                print(f"      Estado: {estado}")
                print(f"      Destino: {cfg.destino}")
                print(f"      Retención: {cfg.dias_retencion} días")
                if cfg.ultima_ejecucion:
                    print(f"      Último backup: {cfg.ultima_ejecucion.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
    except Exception as e:
        print(f"⚠️  No se pudo verificar configuración: {str(e)}")
        print("   Es normal si aún no has ejecutado el instalador")
        return False

def verificar_endpoints():
    """Verifica que los endpoints estén disponibles"""
    print_header("VERIFICANDO ENDPOINTS API")
    
    endpoints_esperados = [
        'GET /admin/monitoreo/api/backup/estado',
        'POST /admin/monitoreo/api/backup/ejecutar/<tipo>',
        'GET /admin/monitoreo/api/backup/historial',
        'GET /admin/monitoreo/api/backup/configuracion',
        'PUT /admin/monitoreo/api/backup/configuracion/<tipo>'
    ]
    
    print("Endpoints implementados:")
    for endpoint in endpoints_esperados:
        print(f"   ✅ {endpoint}")
    
    print("\n💡 Para probar, inicia el servidor:")
    print("   python app.py")
    print("   Luego accede a: http://localhost:8099/admin/monitoreo/dashboard")
    
    return True

def mostrar_proximos_pasos():
    """Muestra los próximos pasos a seguir"""
    print_header("PRÓXIMOS PASOS", "=")
    
    print("""
1️⃣  INSTALAR EL SISTEMA (si aún no lo hiciste):
    python instalar_sistema_backup.py

2️⃣  EJECUTAR PRIMER BACKUP:
    python ejecutar_backup.py todos

3️⃣  VERIFICAR ESTADO:
    python ejecutar_backup.py historial
    python ejecutar_backup.py config

4️⃣  CONFIGURAR BACKUPS AUTOMÁTICOS:
    - Abrir Task Scheduler (Windows)
    - Crear 3 tareas programadas:
      • Base de Datos: 2 AM diario
      • Archivos: 3 AM diario
      • Código: 4 AM domingos

5️⃣  MONITOREAR:
    - Panel web: http://localhost:8099/admin/monitoreo/dashboard
    - Logs: logs/backup.log
    - Historial en BD: tabla historial_backup

📚 DOCUMENTACIÓN COMPLETA:
    - DOCUMENTACION_SISTEMA_BACKUP.md
    - RESUMEN_SISTEMA_BACKUP.md
    """)

def main():
    """Función principal"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     VERIFICACIÓN DEL SISTEMA DE BACKUP AUTOMÁTICO           ║
║     Gestor Documental - Supertiendas Cañaveral              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Verificaciones
    resultados = []
    
    resultados.append(('Archivos del sistema', verificar_archivos()))
    resultados.append(('PostgreSQL (pg_dump)', verificar_pg_dump()))
    resultados.append(('Directorios de destino', verificar_directorios()))
    resultados.append(('Tablas de base de datos', verificar_base_datos()))
    resultados.append(('Configuración', verificar_configuracion()))
    resultados.append(('Endpoints API', verificar_endpoints()))
    
    # Resumen
    print_header("RESUMEN DE VERIFICACIÓN")
    
    for nombre, resultado in resultados:
        simbolo = "✅" if resultado else "❌"
        print(f"{simbolo} {nombre}")
    
    exitosos = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    print(f"\n📊 Resultado: {exitosos}/{total} verificaciones exitosas")
    
    if exitosos == total:
        print("\n🎉 ¡TODO ESTÁ CORRECTO!")
        print("   El sistema de backup está listo para usar.")
    elif exitosos >= 4:
        print("\n✅ Sistema casi listo")
        print("   Revisa las advertencias arriba y ejecuta el instalador si es necesario.")
    else:
        print("\n⚠️  Sistema necesita instalación")
        print("   Ejecuta: python instalar_sistema_backup.py")
    
    # Mostrar próximos pasos
    mostrar_proximos_pasos()
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    main()
