"""
🔧 AGREGAR TIMEOUT A TODOS LOS TEMPLATES
==========================================
Agrega el código de timeout de 25 minutos automáticamente
a todos los templates HTML que lo necesitan.

Fecha: 30 de Noviembre 2025
"""

import os
import re

def agregar_timeout_a_template(archivo_path):
    """Agrega código de timeout a un template HTML específico"""
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar si ya tiene timeout
        if 'SESSION_TIMEOUT' in contenido or 'checkSessionTimeout' in contenido:
            return False, "Ya tiene timeout"
        
        # Buscar </body>
        if '</body>' not in contenido.lower():
            return False, "No tiene etiqueta </body>"
        
        # Código de timeout
        codigo_timeout = """
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
        
        # Insertar antes de </body> (case insensitive)
        contenido_nuevo = re.sub(
            r'</body>',
            codigo_timeout + '\n</body>',
            contenido,
            flags=re.IGNORECASE
        )
        
        # Guardar archivo
        with open(archivo_path, 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        return True, "Timeout agregado"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


def procesar_todos_los_templates():
    """Procesa todos los templates HTML del proyecto"""
    
    templates_dir = r"c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\templates"
    
    # Templates que deben excluirse (login.html y otros que NO requieren sesión)
    EXCLUIR = [
        'login.html',  # El login ya tiene su propio manejo
        'error.html',  # Página de error no requiere sesión
        'correo_token_firma_relacion.html',  # Template de correo
        'establecer_password.html',  # No requiere sesión activa
        '_inactivity_warning.html'  # Componente parcial
    ]
    
    # Buscar todos los HTML
    templates = []
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html') and file not in EXCLUIR:
                templates.append(os.path.join(root, file))
    
    print("\n" + "="*80)
    print("🔧 AGREGANDO TIMEOUT A TEMPLATES HTML")
    print("="*80 + "\n")
    print(f"📋 Encontrados {len(templates)} templates para procesar\n")
    
    # Contadores
    exitosos = 0
    ya_tenian = 0
    sin_body = 0
    errores = 0
    
    for template_path in templates:
        nombre_archivo = os.path.basename(template_path)
        carpeta = os.path.basename(os.path.dirname(template_path))
        ruta_corta = f"{carpeta}/{nombre_archivo}" if carpeta != 'templates' else nombre_archivo
        
        exito, mensaje = agregar_timeout_a_template(template_path)
        
        if exito:
            print(f"   ✅ {ruta_corta:60} → {mensaje}")
            exitosos += 1
        elif "Ya tiene timeout" in mensaje:
            print(f"   ⏭️  {ruta_corta:60} → {mensaje}")
            ya_tenian += 1
        elif "No tiene etiqueta" in mensaje:
            print(f"   ⚠️  {ruta_corta:60} → {mensaje}")
            sin_body += 1
        else:
            print(f"   ❌ {ruta_corta:60} → {mensaje}")
            errores += 1
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE PROCESAMIENTO")
    print("="*80 + "\n")
    print(f"   ✅ Templates actualizados:     {exitosos}")
    print(f"   ⏭️  Templates que ya tenían:    {ya_tenian}")
    print(f"   ⚠️  Templates sin </body>:      {sin_body}")
    print(f"   ❌ Errores:                    {errores}")
    print(f"   📋 Total procesados:           {len(templates)}")
    
    print("\n" + "="*80)
    print("✅ PROCESO COMPLETADO")
    print("="*80 + "\n")
    
    return exitosos


if __name__ == "__main__":
    procesar_todos_los_templates()
