"""
Validar permisos de todos los módulos y crear faltantes
"""
from app import app, db
from sqlalchemy import text
import os

# Módulos que existen físicamente en la carpeta modules/
MODULOS_FISICOS = [
    'admin',
    'causaciones', 
    'configuracion',
    'dian_vs_erp',
    'facturas_digitales',
    'notas_contables',
    'recibir_facturas',
    'relaciones',
    'terceros'
]

# Permisos estándar que debe tener cada módulo
PERMISOS_ESTANDAR = [
    'acceder_modulo',
    'crear',
    'editar',
    'eliminar',
    'consultar',
    'listar',
    'exportar'
]

# Permisos especiales por módulo
PERMISOS_ESPECIALES = {
    'admin': ['activar_usuario', 'desactivar_usuario', 'gestionar_permisos', 'ver_logs'],
    'configuracion': ['modificar_catalogos', 'gestionar_empresas', 'configurar_backup'],
    'facturas_digitales': ['radicar_factura', 'anular_factura', 'validar_duplicada'],
    'recibir_facturas': ['adicionar_factura', 'guardar_facturas', 'exportar_temporales'],
    'relaciones': ['generar_relacion', 'confirmar_recepcion', 'exportar_relacion'],
    'causaciones': ['crear_causacion', 'aprobar_causacion', 'contabilizar'],
    'dian_vs_erp': ['comparar_datos', 'generar_reporte'],
    'notas_contables': ['crear_nota', 'aprobar_nota'],
    'terceros': ['crear_tercero', 'actualizar_tercero', 'validar_tercero']
}

def validar_y_crear_permisos():
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 VALIDACIÓN DE PERMISOS DE MÓDULOS")
        print("="*80 + "\n")
        
        # 1. Consultar módulos actuales en BD
        print("📋 PASO 1: Consultando módulos en base de datos...")
        result = db.session.execute(text("""
            SELECT DISTINCT modulo 
            FROM permisos_modulos 
            ORDER BY modulo
        """))
        modulos_bd = [row[0] for row in result]
        print(f"   Módulos con permisos en BD: {len(modulos_bd)}")
        for mod in modulos_bd:
            print(f"   ✅ {mod}")
        
        # 2. Comparar con módulos físicos
        print("\n📂 PASO 2: Comparando con módulos físicos...")
        modulos_faltantes = set(MODULOS_FISICOS) - set(modulos_bd)
        if modulos_faltantes:
            print(f"   ⚠️  Módulos SIN permisos: {len(modulos_faltantes)}")
            for mod in modulos_faltantes:
                print(f"   ❌ {mod}")
        else:
            print("   ✅ Todos los módulos físicos tienen permisos")
        
        # 3. Consultar permisos existentes por módulo
        print("\n📝 PASO 3: Verificando permisos por módulo...")
        permisos_a_crear = []
        
        for modulo in MODULOS_FISICOS:
            print(f"\n   🔍 Módulo: {modulo}")
            
            # Consultar permisos actuales
            result = db.session.execute(text("""
                SELECT permiso, descripcion 
                FROM permisos_modulos 
                WHERE modulo = :modulo
                ORDER BY permiso
            """), {"modulo": modulo})
            permisos_actuales = {row[0]: row[1] for row in result}
            
            print(f"      Permisos actuales: {len(permisos_actuales)}")
            
            # Verificar permisos estándar
            for permiso in PERMISOS_ESTANDAR:
                if permiso not in permisos_actuales:
                    descripcion = f"{permiso.replace('_', ' ').title()} en {modulo}"
                    permisos_a_crear.append({
                        'modulo': modulo,
                        'permiso': permiso,
                        'descripcion': descripcion
                    })
                    print(f"      ➕ Faltante: {permiso}")
            
            # Verificar permisos especiales
            if modulo in PERMISOS_ESPECIALES:
                for permiso in PERMISOS_ESPECIALES[modulo]:
                    if permiso not in permisos_actuales:
                        descripcion = f"{permiso.replace('_', ' ').title()} en {modulo}"
                        permisos_a_crear.append({
                            'modulo': modulo,
                            'permiso': permiso,
                            'descripcion': descripcion
                        })
                        print(f"      ➕ Faltante especial: {permiso}")
        
        # 4. Crear permisos faltantes
        if permisos_a_crear:
            print(f"\n💾 PASO 4: Creando {len(permisos_a_crear)} permisos faltantes...")
            
            for perm in permisos_a_crear:
                try:
                    db.session.execute(text("""
                        INSERT INTO permisos_modulos (modulo, permiso, descripcion)
                        VALUES (:modulo, :permiso, :descripcion)
                    """), perm)
                    print(f"   ✅ {perm['modulo']}.{perm['permiso']}")
                except Exception as e:
                    print(f"   ❌ Error creando {perm['modulo']}.{perm['permiso']}: {e}")
            
            db.session.commit()
            print("\n   ✅ Permisos creados exitosamente")
        else:
            print("\n✅ PASO 4: No hay permisos faltantes por crear")
        
        # 5. Resumen final
        print("\n" + "="*80)
        print("📊 RESUMEN FINAL")
        print("="*80)
        
        result = db.session.execute(text("""
            SELECT modulo, COUNT(*) as total_permisos
            FROM permisos_modulos
            GROUP BY modulo
            ORDER BY modulo
        """))
        
        print("\n   Permisos por módulo:")
        total_permisos = 0
        for row in result:
            print(f"   📌 {row[0]}: {row[1]} permisos")
            total_permisos += row[1]
        
        print(f"\n   ✅ TOTAL: {total_permisos} permisos en {len(MODULOS_FISICOS)} módulos")
        print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    validar_y_crear_permisos()
