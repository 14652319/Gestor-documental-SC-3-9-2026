"""
Validar permisos de módulos y limpiar duplicados
Fecha: 27 Noviembre 2025
"""
from app import app, db
from sqlalchemy import text
import os

# Módulos físicos existentes
MODULOS_FISICOS = {
    'admin',
    'causaciones',
    'configuracion',
    'dian_vs_erp',
    'facturas_digitales',
    'notas_contables',
    'recibir_facturas',
    'relaciones',
    'terceros'
}

def validar_permisos():
    with app.app_context():
        print("\n" + "="*100)
        print("🔍 VALIDACIÓN DE PERMISOS - GESTOR DOCUMENTAL")
        print("="*100 + "\n")
        
        # 1. Consultar módulos en catálogo
        print("📋 PASO 1: Módulos en catálogo de permisos\n")
        result = db.session.execute(text("""
            SELECT DISTINCT modulo, COUNT(*) as total_permisos
            FROM catalogo_permisos
            GROUP BY modulo
            ORDER BY modulo
        """))
        
        modulos_catalogo = {}
        for row in result:
            modulos_catalogo[row[0]] = row[1]
            print(f"   ✅ {row[0]:30} → {row[1]:3} permisos")
        
        print(f"\n   📊 Total: {len(modulos_catalogo)} módulos diferentes en catálogo")
        
        # 2. Comparar con módulos físicos
        print("\n📂 PASO 2: Comparación con módulos físicos\n")
        modulos_faltantes = MODULOS_FISICOS - set(modulos_catalogo.keys())
        modulos_extra = set(modulos_catalogo.keys()) - MODULOS_FISICOS
        
        if modulos_faltantes:
            print(f"   ⚠️  Módulos FÍSICOS sin permisos ({len(modulos_faltantes)}):")
            for mod in sorted(modulos_faltantes):
                print(f"      ❌ {mod}")
        else:
            print("   ✅ Todos los módulos físicos tienen permisos")
        
        if modulos_extra:
            print(f"\n   ℹ️  Módulos en catálogo sin carpeta física ({len(modulos_extra)}):")
            for mod in sorted(modulos_extra):
                print(f"      📝 {mod:30} → {modulos_catalogo[mod]:3} permisos (módulos virtuales/futuros)")
        
        # 3. Detectar duplicados (mismo módulo con diferentes nombres)
        print("\n🔍 PASO 3: Detectando duplicados por nombre\n")
        result = db.session.execute(text("""
            SELECT modulo, modulo_nombre, COUNT(*) as total
            FROM catalogo_permisos
            GROUP BY modulo, modulo_nombre
            HAVING COUNT(*) > 0
            ORDER BY modulo, modulo_nombre
        """))
        
        duplicados = {}
        for row in result:
            if row[0] not in duplicados:
                duplicados[row[0]] = []
            duplicados[row[0]].append((row[1], row[2]))
        
        tiene_duplicados = any(len(v) > 1 for v in duplicados.values())
        
        if tiene_duplicados:
            print("   ⚠️  Módulos con múltiples nombres (necesitan limpieza):\n")
            for modulo, nombres in duplicados.items():
                if len(nombres) > 1:
                    print(f"      📦 {modulo}:")
                    for nombre, total in nombres:
                        print(f"         • '{nombre}' → {total} permisos")
                    print()
        else:
            print("   ✅ No hay duplicados de nombre por módulo")
        
        # 4. Listar permisos por módulo FÍSICO
        print("\n📊 PASO 4: Detalle de permisos por módulo FÍSICO\n")
        
        for modulo in sorted(MODULOS_FISICOS):
            result = db.session.execute(text("""
                SELECT accion, accion_descripcion, tipo_accion, es_critico
                FROM catalogo_permisos
                WHERE modulo = :modulo
                ORDER BY accion
            """), {"modulo": modulo})
            
            permisos = result.fetchall()
            
            if permisos:
                print(f"   🔹 {modulo.upper()} ({len(permisos)} permisos):")
                for perm in permisos:
                    critico = "🔴" if perm[3] else "  "
                    tipo = f"[{perm[2]}]" if perm[2] else ""
                    print(f"      {critico} {perm[0]:30} → {perm[1][:50]} {tipo}")
                print()
            else:
                print(f"   ❌ {modulo.upper()} → SIN PERMISOS\n")
        
        # 5. Resumen final
        print("\n" + "="*100)
        print("📈 RESUMEN FINAL")
        print("="*100 + "\n")
        
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM catalogo_permisos
        """))
        total_registros = result.scalar()
        
        result = db.session.execute(text("""
            SELECT COUNT(DISTINCT modulo) FROM catalogo_permisos
        """))
        total_modulos = result.scalar()
        
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM catalogo_permisos WHERE es_critico = TRUE
        """))
        total_criticos = result.scalar()
        
        print(f"   📊 Total registros en catálogo: {total_registros}")
        print(f"   📦 Módulos diferentes: {total_modulos}")
        print(f"   🔴 Permisos críticos: {total_criticos}")
        print(f"   📂 Módulos físicos: {len(MODULOS_FISICOS)}")
        print(f"   ⚠️  Módulos físicos sin permisos: {len(modulos_faltantes)}")
        print(f"   ℹ️  Módulos virtuales (sin carpeta): {len(modulos_extra)}")
        
        cobertura = (len(MODULOS_FISICOS & set(modulos_catalogo.keys())) / len(MODULOS_FISICOS)) * 100
        print(f"\n   ✅ Cobertura de permisos: {cobertura:.1f}%")
        
        print("\n" + "="*100 + "\n")

if __name__ == '__main__':
    validar_permisos()
