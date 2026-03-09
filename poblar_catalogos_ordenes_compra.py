"""
Script para poblar datos iniciales en catálogos de Órdenes de Compra
Unidades de Negocio y Centros de Costo
"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def poblar_catalogos():
    """Insertar datos iniciales en catálogos"""
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: No se encontró DATABASE_URL en .env")
        return False
    
    try:
        print("📊 Conectando a la base de datos...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 1. UNIDADES DE NEGOCIO (según imagen)
        print("\n📦 Insertando Unidades de Negocio...")
        unidades_negocio = [
            ('06 PGC', 'Productos de Gran Consumo', 'Productos de gran consumo y distribución masiva'),
            ('01 ALI', 'Alimentos', 'Productos alimenticios'),
            ('02 BEB', 'Bebidas', 'Bebidas y licores'),
            ('03 ABA', 'Abarrotes', 'Productos de abarrotes'),
            ('04 CAR', 'Cárnicos', 'Productos cárnicos y embutidos'),
            ('05 FRV', 'Frutas y Verduras', 'Frutas y verduras frescas'),
            ('07 PAN', 'Panadería', 'Productos de panadería'),
            ('08 LAC', 'Lácteos', 'Productos lácteos'),
            ('09 ASE', 'Aseo', 'Productos de aseo y limpieza'),
            ('10 PER', 'Perfumería', 'Productos de perfumería y cuidado personal')
        ]
        
        for codigo, nombre, descripcion in unidades_negocio:
            cursor.execute("""
                INSERT INTO unidades_negocio (codigo, nombre, descripcion, activo)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (codigo) DO UPDATE
                SET nombre = EXCLUDED.nombre,
                    descripcion = EXCLUDED.descripcion,
                    fecha_actualizacion = CURRENT_TIMESTAMP
            """, (codigo, nombre, descripcion))
            print(f"   ✓ {codigo} - {nombre}")
        
        # 2. CENTROS DE COSTO (ejemplos)
        print("\n💰 Insertando Centros de Costo...")
        centros_costo = [
            ('001', 'Administración General', 'Costos administrativos generales'),
            ('002', 'Compras', 'Departamento de compras'),
            ('003', 'Ventas', 'Departamento de ventas'),
            ('004', 'Logística', 'Logística y distribución'),
            ('005', 'Marketing', 'Marketing y publicidad'),
            ('006', 'Recursos Humanos', 'Gestión de recursos humanos'),
            ('007', 'Sistemas', 'Tecnología e informática'),
            ('008', 'Contabilidad', 'Departamento contable'),
            ('009', 'Mantenimiento', 'Mantenimiento de instalaciones'),
            ('010', 'Producción', 'Área de producción')
        ]
        
        for codigo, nombre, descripcion in centros_costo:
            cursor.execute("""
                INSERT INTO centros_costo (codigo, nombre, descripcion, activo)
                VALUES (%s, %s, %s, TRUE)
                ON CONFLICT (codigo) DO UPDATE
                SET nombre = EXCLUDED.nombre,
                    descripcion = EXCLUDED.descripcion,
                    fecha_actualizacion = CURRENT_TIMESTAMP
            """, (codigo, nombre, descripcion))
            print(f"   ✓ {codigo} - {nombre}")
        
        conn.commit()
        
        # Verificar totales
        cursor.execute("SELECT COUNT(*) FROM unidades_negocio WHERE activo = TRUE")
        total_un = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM centros_costo WHERE activo = TRUE")
        total_cc = cursor.fetchone()[0]
        
        print(f"\n✅ Datos insertados exitosamente!")
        print(f"   📦 Unidades de Negocio: {total_un}")
        print(f"   💰 Centros de Costo: {total_cc}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("POBLADO DE CATÁLOGOS - ÓRDENES DE COMPRA")
    print("=" * 60)
    print()
    
    exitoso = poblar_catalogos()
    
    if exitoso:
        print("\n✅ Proceso completado exitosamente!")
        print("🚀 Los catálogos están listos para usar")
    else:
        print("\n❌ Hubo errores durante la ejecución")
    
    input("\nPresiona Enter para salir...")
