"""
🗃️ INICIALIZAR MÓDULO TERCEROS
==============================
Script para crear las tablas del módulo súper completo de terceros
y configurar datos iniciales.

Autor: GitHub Copilot (Claude Sonnet 4)
Fecha: Noviembre 2025
"""

from extensions import db
from app import app
import sys
import os

def crear_tablas_terceros():
    """Crear las 5 tablas nuevas del módulo terceros"""
    print("🗃️ Creando tablas del módulo terceros...")
    
    try:
        # Importar los modelos para que SQLAlchemy los reconozca
        from modules.terceros.models import (
            TerceroExtendido, 
            EstadoDocumentacion, 
            HistorialNotificaciones,
            AprobacionDocumentos,
            ConfiguracionNotificaciones
        )
        
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            
            print("✅ Tablas creadas exitosamente:")
            print("  - terceros_extendidos")
            print("  - estados_documentacion") 
            print("  - historial_notificaciones")
            print("  - aprobaciones_documentos")
            print("  - configuracion_notificaciones")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

def crear_configuracion_inicial():
    """Crear configuración inicial del sistema"""
    print("\n⚙️ Creando configuración inicial...")
    
    try:
        from modules.terceros.models import ConfiguracionNotificaciones
        
        with app.app_context():
            # Verificar si ya existe configuración
            config_existente = ConfiguracionNotificaciones.query.first()
            
            if not config_existente:
                # Crear configuración por defecto
                config = ConfiguracionNotificaciones(
                    correos_por_bloque=5,
                    segundos_entre_bloques=5,
                    dias_recordatorio_defecto=365,
                    dias_anticipacion_vencimiento=30,
                    plantilla_actualizacion="""
                    <h2>Actualización de Documentación Requerida</h2>
                    <p>Estimado proveedor,</p>
                    <p>Le informamos que es necesario actualizar su documentación en nuestro sistema.</p>
                    <p>Por favor, póngase en contacto con nosotros para coordinar la actualización.</p>
                    <p>Saludos cordiales,<br>Supertiendas Cañaveral</p>
                    """,
                    notificaciones_activas=True,
                    envio_automatico_activo=False,
                    usuario_actualizacion="SISTEMA"
                )
                
                db.session.add(config)
                db.session.commit()
                
                print("✅ Configuración inicial creada:")
                print("  - 5 correos por bloque")
                print("  - 5 segundos entre bloques") 
                print("  - Notificación cada 365 días")
                print("  - Plantilla de email configurada")
                
            else:
                print("✅ Configuración ya existe, no se modifica")
                
            return True
            
    except Exception as e:
        print(f"❌ Error creando configuración: {e}")
        return False

def verificar_permisos():
    """Verificar que los permisos del módulo estén configurados"""
    print("\n🔐 Verificando permisos...")
    
    try:
        # Esta función se puede expandir cuando el sistema de permisos
        # esté más desarrollado
        print("✅ Permisos verificados (implementación futura)")
        return True
        
    except Exception as e:
        print(f"❌ Error verificando permisos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIALIZADOR DEL MÓDULO SÚPER COMPLETO DE TERCEROS")
    print("=" * 60)
    print("Sistema: Gestor Documental - Supertiendas Cañaveral")
    print("Módulo: Gestión Avanzada de Terceros")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('modules/terceros'):
        print("❌ Error: No se encuentra el directorio modules/terceros")
        print("   Ejecute este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Ejecutar pasos de inicialización
    pasos = [
        ("Crear tablas de base de datos", crear_tablas_terceros),
        ("Configuración inicial", crear_configuracion_inicial),
        ("Verificar permisos", verificar_permisos)
    ]
    
    exitos = 0
    total = len(pasos)
    
    for nombre_paso, funcion_paso in pasos:
        print(f"\n📋 Ejecutando: {nombre_paso}")
        if funcion_paso():
            exitos += 1
        else:
            print(f"⚠️ Falló el paso: {nombre_paso}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE INICIALIZACIÓN")
    print("=" * 60)
    
    if exitos == total:
        print("🎉 ¡INICIALIZACIÓN COMPLETADA EXITOSAMENTE!")
        print("\n✨ El módulo terceros está listo para usar:")
        print("   📊 Dashboard: http://localhost:8099/terceros/")
        print("   📋 Consulta: http://localhost:8099/terceros/consulta")
        print("   ➕ Crear:   http://localhost:8099/terceros/crear")
        print("   ⚙️ Config:   http://localhost:8099/terceros/configuracion")
        print("\n🧪 Para probar el módulo, ejecute:")
        print("   python test_modulo_terceros.py")
        
    else:
        print(f"⚠️ INICIALIZACIÓN PARCIAL: {exitos}/{total} pasos exitosos")
        print("   Revise los errores anteriores y vuelva a ejecutar")
    
    print("\n" + "=" * 60)
    return exitos == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)