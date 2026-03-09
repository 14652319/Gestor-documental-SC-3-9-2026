"""
🔧 ACTUALIZACIÓN COMPLETA DEL SISTEMA
====================================
1. Agregar módulos faltantes al sistema de permisos
2. Implementar timeout de 25 minutos en todos los frontends
3. Validar estructura completa del sistema

Fecha: 30 de Noviembre 2025
"""

from app import app, db
from sqlalchemy import text
import os
import glob

def agregar_modulos_faltantes():
    """Agrega módulos DIAN vs ERP y Terceros al catálogo de permisos"""
    
    print("\n" + "="*80)
    print("🔧 PASO 1: AGREGAR MÓDULOS FALTANTES AL SISTEMA DE PERMISOS")
    print("="*80 + "\n")
    
    with app.app_context():
        try:
            # Verificar módulos actuales
            result = db.session.execute(text("""
                SELECT DISTINCT modulo, modulo_nombre 
                FROM catalogo_permisos 
                ORDER BY modulo
            """))
            modulos_actuales = [row[0] for row in result.fetchall()]
            
            print("📋 Módulos actuales en el sistema:")
            for mod in modulos_actuales:
                print(f"   ✅ {mod}")
            
            # Definir módulos faltantes
            modulos_nuevos = {
                'dian_vs_erp': {
                    'nombre': 'DIAN vs ERP',
                    'descripcion': 'Validación y comparación de facturas DIAN contra ERP',
                    'acciones': [
                        ('acceder_modulo', 'Acceder al Módulo', 'Acceso general al módulo DIAN vs ERP', 'acceso', False),
                        ('ver_dashboard', 'Ver Dashboard', 'Acceder al visor de validación', 'vista', False),
                        ('cargar_archivo_dian', 'Cargar Archivo DIAN', 'Subir archivo de facturas DIAN', 'carga', False),
                        ('cargar_archivo_erp_fn', 'Cargar Archivo ERP FN', 'Subir archivo ERP Fenalco', 'carga', False),
                        ('cargar_archivo_erp_cm', 'Cargar Archivo ERP CM', 'Subir archivo ERP Coomultrasán', 'carga', False),
                        ('cargar_acuses', 'Cargar Acuses', 'Subir archivo de acuses recibos', 'carga', False),
                        ('procesar_archivos', 'Procesar Archivos', 'Ejecutar validación y comparación', 'accion', False),
                        ('ver_diferencias', 'Ver Diferencias', 'Ver discrepancias detectadas', 'consulta', False),
                        ('exportar_reporte', 'Exportar Reporte', 'Descargar reporte de validación', 'exportacion', False),
                        ('enviar_correo', 'Enviar Correo', 'Enviar reporte por correo electrónico', 'accion', False),
                        ('asignar_usuario_factura', 'Asignar Usuario', 'Asignar responsable a factura', 'edicion', True),
                        ('cambiar_estado_factura', 'Cambiar Estado', 'Actualizar estado de validación', 'edicion', True),
                        ('configurar_smtp', 'Configurar SMTP', 'Administrar configuración de correo', 'configuracion', True)
                    ]
                },
                'terceros': {
                    'nombre': 'Gestión de Terceros',
                    'descripcion': 'Administración completa de proveedores, clientes y empleados',
                    'acciones': [
                        ('acceder_modulo', 'Acceder al Módulo', 'Acceso general al módulo de terceros', 'acceso', False),
                        ('ver_dashboard', 'Ver Dashboard', 'Acceder al dashboard de terceros', 'vista', False),
                        ('consultar_terceros', 'Consultar Terceros', 'Listar y buscar terceros', 'consulta', False),
                        ('ver_tercero', 'Ver Detalle Tercero', 'Ver información completa de un tercero', 'vista', False),
                        ('crear_tercero', 'Crear Tercero', 'Dar de alta nuevos terceros', 'creacion', True),
                        ('editar_tercero', 'Editar Tercero', 'Modificar datos de terceros existentes', 'edicion', True),
                        ('activar_tercero', 'Activar/Desactivar Tercero', 'Cambiar estado activo de terceros', 'edicion', True),
                        ('eliminar_tercero', 'Eliminar Tercero', 'Borrar terceros del sistema', 'eliminacion', True),
                        ('subir_documentos', 'Subir Documentos', 'Cargar documentos del tercero (RUT, cámara)', 'carga', False),
                        ('ver_documentos', 'Ver Documentos', 'Ver documentos del tercero', 'vista', False),
                        ('descargar_documentos', 'Descargar Documentos', 'Descargar documentos del tercero', 'descarga', False),
                        ('aprobar_registro', 'Aprobar Registro', 'Aprobar solicitudes de registro de terceros', 'aprobacion', True),
                        ('rechazar_registro', 'Rechazar Registro', 'Rechazar solicitudes de registro', 'aprobacion', True),
                        ('ver_estadisticas', 'Ver Estadísticas', 'Dashboard de estadísticas de terceros', 'vista', False),
                        ('exportar_terceros', 'Exportar Terceros', 'Exportar listado de terceros a Excel', 'exportacion', False),
                        ('importar_terceros', 'Importar Terceros', 'Importar terceros masivamente desde Excel', 'importacion', True)
                    ]
                }
            }
            
            # Verificar qué módulos faltan
            modulos_a_agregar = []
            for modulo_key in modulos_nuevos.keys():
                if modulo_key not in modulos_actuales:
                    modulos_a_agregar.append(modulo_key)
            
            if not modulos_a_agregar:
                print("\n✅ Todos los módulos ya están en el sistema. No hay nada que agregar.")
                return True
            
            print(f"\n📝 Módulos a agregar ({len(modulos_a_agregar)}):")
            for mod in modulos_a_agregar:
                print(f"   🆕 {mod} - {modulos_nuevos[mod]['nombre']}")
            
            # Insertar módulos faltantes
            contador_insertados = 0
            for modulo_key in modulos_a_agregar:
                modulo_data = modulos_nuevos[modulo_key]
                print(f"\n⚙️  Insertando módulo: {modulo_key}")
                
                for accion_key, accion_nombre, accion_desc, tipo, critico in modulo_data['acciones']:
                    try:
                        # Verificar si ya existe
                        existe = db.session.execute(text("""
                            SELECT id FROM catalogo_permisos 
                            WHERE modulo = :modulo AND accion = :accion
                        """), {'modulo': modulo_key, 'accion': accion_key}).fetchone()
                        
                        if not existe:
                            db.session.execute(text("""
                                INSERT INTO catalogo_permisos 
                                (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo)
                                VALUES (:modulo, :modulo_nombre, :modulo_desc, :accion, :accion_desc, :tipo, :critico, true)
                            """), {
                                'modulo': modulo_key,
                                'modulo_nombre': modulo_data['nombre'],
                                'modulo_desc': modulo_data['descripcion'],
                                'accion': accion_key,
                                'accion_desc': accion_desc,
                                'tipo': tipo,
                                'critico': critico
                            })
                            contador_insertados += 1
                            print(f"   ✅ {accion_key}")
                    
                    except Exception as e:
                        print(f"   ❌ Error insertando {accion_key}: {str(e)}")
            
            db.session.commit()
            print(f"\n✅ Se insertaron {contador_insertados} nuevos permisos en el catálogo")
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            db.session.rollback()
            return False


def verificar_templates_con_timeout():
    """Identifica templates que necesitan timeout de 25 minutos"""
    
    print("\n" + "="*80)
    print("🔧 PASO 2: VERIFICAR TIMEOUT EN TEMPLATES HTML")
    print("="*80 + "\n")
    
    templates_dir = r"c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\templates"
    
    # Buscar todos los HTML
    templates = []
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                templates.append(os.path.join(root, file))
    
    print(f"📋 Encontrados {len(templates)} templates HTML\n")
    
    # Templates que YA tienen timeout (login.html ya lo tiene)
    templates_con_timeout = []
    templates_sin_timeout = []
    
    codigo_timeout = "1500000"  # 25 minutos en milisegundos
    
    for template_path in templates:
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            # Buscar si tiene setTimeout con 1500000 (25 min)
            if codigo_timeout in contenido or 'checkSessionTimeout' in contenido:
                templates_con_timeout.append(template_path)
            else:
                # Ver si tiene alguna sesión o requiere login
                if 'session' in contenido.lower() or 'usuario' in contenido.lower() or 'dashboard' in contenido.lower():
                    templates_sin_timeout.append(template_path)
        
        except Exception as e:
            print(f"⚠️  Error leyendo {os.path.basename(template_path)}: {str(e)}")
    
    print("✅ TEMPLATES CON TIMEOUT (No requieren cambios):")
    for t in templates_con_timeout:
        print(f"   ✓ {os.path.relpath(t, templates_dir)}")
    
    print(f"\n⚠️  TEMPLATES SIN TIMEOUT ({len(templates_sin_timeout)}):")
    for t in templates_sin_timeout:
        print(f"   ❌ {os.path.relpath(t, templates_dir)}")
    
    return templates_sin_timeout


def generar_codigo_timeout_javascript():
    """Genera el código JavaScript para timeout de sesión"""
    
    return """
<!-- ============================================ -->
<!-- ⏰ TIMEOUT DE SESIÓN - 25 MINUTOS -->
<!-- ============================================ -->
<script>
// Configuración de timeout
const SESSION_TIMEOUT = 25 * 60 * 1000; // 25 minutos en milisegundos
let timeoutTimer;

function iniciarContadorSesion() {
    // Limpiar cualquier timer existente
    if (timeoutTimer) {
        clearTimeout(timeoutTimer);
    }
    
    // Iniciar nuevo timer
    timeoutTimer = setTimeout(() => {
        cerrarSesionPorInactividad();
    }, SESSION_TIMEOUT);
}

function reiniciarContadorSesion() {
    // Reiniciar el contador con cada actividad del usuario
    iniciarContadorSesion();
}

function cerrarSesionPorInactividad() {
    // Mostrar mensaje
    alert('⏰ Tu sesión ha expirado por inactividad (25 minutos).\\n\\n' +
          'Serás redirigido al inicio de sesión.');
    
    // Cerrar sesión en el servidor
    fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'same-origin'
    }).finally(() => {
        // Redirigir al login
        window.location.href = '/';
    });
}

// Eventos que reinician el contador
document.addEventListener('mousemove', reiniciarContadorSesion, { passive: true });
document.addEventListener('keypress', reiniciarContadorSesion, { passive: true });
document.addEventListener('click', reiniciarContadorSesion, { passive: true });
document.addEventListener('scroll', reiniciarContadorSesion, { passive: true });
document.addEventListener('touchstart', reiniciarContadorSesion, { passive: true });

// Iniciar contador al cargar la página
window.addEventListener('DOMContentLoaded', () => {
    console.log('✅ Timeout de sesión activado (25 minutos)');
    iniciarContadorSesion();
});

// Advertencia si el usuario intenta cerrar la página con cambios sin guardar
window.addEventListener('beforeunload', (e) => {
    // Solo mostrar si hay cambios pendientes (puedes personalizar esta lógica)
    const formularioModificado = document.querySelector('form.modificado');
    if (formularioModificado) {
        e.preventDefault();
        e.returnValue = '';
    }
});
</script>
"""


def crear_endpoint_logout():
    """Verifica si existe el endpoint /api/auth/logout"""
    
    print("\n" + "="*80)
    print("🔧 PASO 3: VERIFICAR ENDPOINT DE LOGOUT")
    print("="*80 + "\n")
    
    app_py_path = r"c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\app.py"
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    if '/api/auth/logout' in contenido:
        print("✅ El endpoint /api/auth/logout YA EXISTE")
        return True
    else:
        print("⚠️  El endpoint /api/auth/logout NO EXISTE")
        print("\n📝 Código a agregar en app.py:")
        print("""
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    '''Cierra la sesión del usuario actual'''
    try:
        usuario = session.get('usuario', 'Desconocido')
        ip = request.remote_addr
        
        # Limpiar sesión
        session.clear()
        
        log_security(f"LOGOUT | usuario={usuario} | IP={ip} | motivo=inactividad")
        
        return jsonify({
            'success': True,
            'message': 'Sesión cerrada correctamente'
        })
    except Exception as e:
        log_security(f"ERROR LOGOUT | error={str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error al cerrar sesión'
        }), 500
""")
        return False


def generar_informe_final():
    """Genera informe completo del estado del sistema"""
    
    print("\n" + "="*80)
    print("📊 INFORME FINAL DEL SISTEMA")
    print("="*80 + "\n")
    
    with app.app_context():
        try:
            # 1. Módulos en sistema de permisos
            result = db.session.execute(text("""
                SELECT modulo, modulo_nombre, COUNT(*) as acciones
                FROM catalogo_permisos
                WHERE activo = true
                GROUP BY modulo, modulo_nombre
                ORDER BY modulo
            """))
            modulos = result.fetchall()
            
            print("1️⃣ MÓDULOS EN SISTEMA DE PERMISOS:")
            print("-" * 80)
            for modulo, nombre, acciones in modulos:
                print(f"   ✅ {nombre:40} ({modulo:20}) → {acciones} permisos")
            
            # 2. Blueprints registrados
            print(f"\n2️⃣ BLUEPRINTS REGISTRADOS EN FLASK:")
            print("-" * 80)
            for blueprint_name in app.blueprints.keys():
                print(f"   ✅ {blueprint_name}")
            
            # 3. Timeout configurado
            print(f"\n3️⃣ CONFIGURACIÓN DE SESIÓN:")
            print("-" * 80)
            print(f"   ⏰ Timeout: {app.config.get('PERMANENT_SESSION_LIFETIME')}")
            print(f"   🔄 Refresh cada request: {app.config.get('SESSION_REFRESH_EACH_REQUEST')}")
            
            # 4. Total de permisos
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM catalogo_permisos WHERE activo = true
            """))
            total_permisos = result.fetchone()[0]
            
            print(f"\n4️⃣ ESTADÍSTICAS:")
            print("-" * 80)
            print(f"   📋 Total de módulos: {len(modulos)}")
            print(f"   🔐 Total de permisos: {total_permisos}")
            print(f"   🌐 Blueprints activos: {len(app.blueprints)}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR generando informe: {str(e)}")
            return False


def main():
    """Función principal que ejecuta todos los pasos"""
    
    print("\n" + "="*80)
    print("🚀 ACTUALIZACIÓN COMPLETA DEL SISTEMA - INICIO")
    print("="*80)
    print("Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Paso 1: Agregar módulos faltantes
    exito_modulos = agregar_modulos_faltantes()
    
    # Paso 2: Verificar templates
    templates_sin_timeout = verificar_templates_con_timeout()
    
    # Paso 3: Verificar endpoint logout
    tiene_logout = crear_endpoint_logout()
    
    # Paso 4: Generar informe
    generar_informe_final()
    
    # Resumen final
    print("\n" + "="*80)
    print("📋 RESUMEN DE ACCIONES NECESARIAS")
    print("="*80 + "\n")
    
    if exito_modulos:
        print("✅ PASO 1: Módulos actualizados en sistema de permisos")
    else:
        print("❌ PASO 1: Error actualizando módulos")
    
    if len(templates_sin_timeout) > 0:
        print(f"\n⚠️  PASO 2: Se encontraron {len(templates_sin_timeout)} templates SIN timeout")
        print("   📝 ACCIÓN REQUERIDA: Agregar código de timeout a estos templates")
        print("\n   Código a agregar (antes de </body>):")
        print(generar_codigo_timeout_javascript())
    else:
        print("\n✅ PASO 2: Todos los templates tienen timeout configurado")
    
    if not tiene_logout:
        print("\n⚠️  PASO 3: Falta endpoint /api/auth/logout")
        print("   📝 ACCIÓN REQUERIDA: Agregar endpoint en app.py")
    else:
        print("\n✅ PASO 3: Endpoint /api/auth/logout existe")
    
    print("\n" + "="*80)
    print("✅ ACTUALIZACIÓN COMPLETA FINALIZADA")
    print("="*80 + "\n")


if __name__ == "__main__":
    from datetime import datetime
    main()
