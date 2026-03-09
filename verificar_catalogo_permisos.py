"""
Script para verificar el catálogo de permisos actualizado
Muestra la estructura completa de módulos y acciones
"""

from modules.admin.usuarios_permisos.models import CatalogoPermisos

def verificar_catalogo():
    """Muestra información del catálogo de permisos"""
    
    print("=" * 100)
    print("VERIFICACIÓN DEL CATÁLOGO DE PERMISOS")
    print("=" * 100)
    print()
    
    catalogo = CatalogoPermisos.MODULOS
    
    # Estadísticas generales
    total_modulos = len(catalogo)
    total_acciones = sum(len(mod['acciones']) for mod in catalogo.values())
    total_criticas = sum(
        sum(1 for accion in mod['acciones'].values() if accion['critico'])
        for mod in catalogo.values()
    )
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Total de módulos: {total_modulos}")
    print(f"   • Total de acciones: {total_acciones}")
    print(f"   • Acciones críticas: {total_criticas}")
    print()
    
    # Listar cada módulo
    print("=" * 100)
    print("📦 MÓDULOS DISPONIBLES")
    print("=" * 100)
    print()
    
    for idx, (modulo_key, modulo_data) in enumerate(catalogo.items(), 1):
        num_acciones = len(modulo_data['acciones'])
        num_criticas = sum(1 for acc in modulo_data['acciones'].values() if acc['critico'])
        
        print(f"{idx}. {modulo_data['nombre']} ({modulo_key})")
        print(f"   └─ {modulo_data['descripcion']}")
        print(f"   └─ Acciones: {num_acciones} total, {num_criticas} críticas")
        print()
    
    # Detallar nuevos módulos
    print("=" * 100)
    print("🆕 MÓDULOS NUEVOS AGREGADOS")
    print("=" * 100)
    print()
    
    modulos_nuevos = ['facturas_digitales', 'monitoreo', 'gestion_usuarios']
    
    for modulo_key in modulos_nuevos:
        if modulo_key in catalogo:
            modulo_data = catalogo[modulo_key]
            print(f"📌 {modulo_data['nombre']} ({modulo_key})")
            print(f"   {modulo_data['descripcion']}")
            print()
            print(f"   Acciones ({len(modulo_data['acciones'])}):")
            
            for accion_key, accion_data in modulo_data['acciones'].items():
                critico = "⚠️ CRÍTICA" if accion_data['critico'] else ""
                tipo_emoji = {
                    'consulta': '🔍',
                    'creacion': '➕',
                    'modificacion': '✏️',
                    'eliminacion': '🗑️',
                    'configuracion': '⚙️'
                }.get(accion_data['tipo'], '❓')
                
                print(f"      {tipo_emoji} {accion_key:30} - {accion_data['descripcion']} {critico}")
            
            print()
    
    # Módulo actualizado
    print("=" * 100)
    print("🔄 MÓDULO ACTUALIZADO")
    print("=" * 100)
    print()
    
    if 'causaciones' in catalogo:
        modulo_data = catalogo['causaciones']
        print(f"📌 {modulo_data['nombre']} (causaciones)")
        print(f"   Acciones anteriores: 3")
        print(f"   Acciones actuales: {len(modulo_data['acciones'])}")
        print(f"   Acciones nuevas: {len(modulo_data['acciones']) - 3}")
        print()
        
        nuevas = ['ver_pdf', 'renombrar_archivo', 'exportar_excel']
        print("   Acciones nuevas agregadas:")
        for accion_key in nuevas:
            if accion_key in modulo_data['acciones']:
                accion_data = modulo_data['acciones'][accion_key]
                tipo_emoji = {
                    'consulta': '🔍',
                    'modificacion': '✏️'
                }.get(accion_data['tipo'], '❓')
                print(f"      {tipo_emoji} {accion_key:30} - {accion_data['descripcion']}")
        print()
    
    # Colores e iconos
    print("=" * 100)
    print("🎨 COLORES E ICONOS ACTUALIZADOS")
    print("=" * 100)
    print()
    
    print("Colores asignados:")
    colores = {
        'admin': '#DC143C',
        'recibir_facturas': '#228B22',
        'relaciones': '#FFD700',
        'configuracion': '#4169E1',
        'notas_contables': '#8B4513',
        'causaciones': '#FF8C00',
        'reportes': '#9370DB',
        'facturas_digitales': '#1E90FF',
        'monitoreo': '#FF6347'
    }
    
    for modulo, color in colores.items():
        print(f"   • {modulo:25} → {color}")
    
    print()
    print("Iconos asignados:")
    iconos = {
        'admin': 'fa-cog',
        'recibir_facturas': 'fa-file-invoice',
        'relaciones': 'fa-link',
        'configuracion': 'fa-sliders-h',
        'notas_contables': 'fa-file-invoice',
        'causaciones': 'fa-calculator',
        'reportes': 'fa-chart-bar',
        'facturas_digitales': 'fa-file-signature',
        'monitoreo': 'fa-chart-line'
    }
    
    for modulo, icono in iconos.items():
        print(f"   • {modulo:25} → {icono}")
    
    print()
    print("=" * 100)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 100)
    print()
    print(f"El catálogo tiene {total_modulos} módulos con {total_acciones} acciones totales.")
    print(f"Se identificaron {total_criticas} acciones críticas que requieren auditoría especial.")
    print()

if __name__ == "__main__":
    verificar_catalogo()
