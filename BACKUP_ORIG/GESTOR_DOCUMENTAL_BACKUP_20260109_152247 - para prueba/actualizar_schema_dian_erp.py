"""
Script para actualizar solo las partes necesarias del esquema DIAN VS ERP
- Corrige función calcular_dias_desde_emision
- Amplía campos VARCHAR de tabla acuses
"""

import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'gestor_documental',
    'user': 'postgres',
    'password': 'G3st0radm$2025.'
}

def actualizar_esquema():
    print("="*80)
    print("ACTUALIZANDO ESQUEMA DIAN VS ERP")
    print("="*80)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Conexión exitosa\n")
        
        # 1. Corregir función calcular_dias_desde_emision
        print("🔧 Actualizando función calcular_dias_desde_emision...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION calcular_dias_desde_emision(fecha_emision DATE)
            RETURNS INTEGER AS $$
            BEGIN
                IF fecha_emision IS NULL THEN
                    RETURN NULL;
                END IF;
                
                RETURN (CURRENT_DATE - fecha_emision)::INTEGER;
            END;
            $$ LANGUAGE plpgsql STABLE;
        """)
        print("   ✅ Función actualizada\n")
        
        # 2. Eliminar vistas que dependen de acuses
        print("🔧 Eliminando vista v_dian_con_acuses...")
        cursor.execute("DROP VIEW IF EXISTS v_dian_con_acuses CASCADE;")
        print("   ✅ Vista eliminada\n")
        
        # 3. Ampliar campos de tabla acuses
        print("🔧 Ampliando campos VARCHAR de tabla acuses...")
        cursor.execute("""
            ALTER TABLE acuses 
                ALTER COLUMN acuse_recibido TYPE VARCHAR(50),
                ALTER COLUMN recibo_bien_servicio TYPE VARCHAR(50),
                ALTER COLUMN aceptacion_expresa TYPE VARCHAR(50),
                ALTER COLUMN reclamo TYPE VARCHAR(50),
                ALTER COLUMN aceptacion_tacita TYPE VARCHAR(50);
        """)
        print("   ✅ Campos ampliados\n")
        
        # 4. Recrear vista v_dian_con_acuses
        print("🔧 Recreando vista v_dian_con_acuses...")
        cursor.execute("""
            CREATE OR REPLACE VIEW v_dian_con_acuses AS
            SELECT 
                d.id AS dian_id,
                d.nit_emisor,
                d.nombre_emisor,
                d.prefijo,
                d.folio,
                d.clave AS clave_dian,
                d.cufe_cude,
                d.fecha_emision,
                d.total,
                d.estado AS estado_dian,
                a.id AS acuse_id,
                a.fecha AS fecha_acuse,
                a.estado_docto AS estado_acuse,
                a.acuse_recibido,
                a.recibo_bien_servicio,
                a.aceptacion_expresa,
                a.reclamo,
                a.aceptacion_tacita,
                CASE 
                    WHEN a.id IS NULL THEN 'Sin Acuse'
                    WHEN a.aceptacion_expresa = 'Sí' THEN 'Aceptado Expresamente'
                    WHEN a.reclamo = 'Sí' THEN 'Reclamado'
                    WHEN a.acuse_recibido = 'Sí' THEN 'Acuse Recibido'
                    ELSE 'Pendiente'
                END AS estado_acuse_completo
            FROM dian d
            LEFT JOIN acuses a ON d.clave_acuse = a.clave_acuse;
        """)
        print("   ✅ Vista recreada\n")
        
        print("="*80)
        print("✅ ESQUEMA ACTUALIZADO EXITOSAMENTE")
        print("="*80)
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    actualizar_esquema()
