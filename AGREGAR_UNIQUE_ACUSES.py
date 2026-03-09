"""
AGREGAR_UNIQUE_ACUSES.py
========================
Agrega restricción UNIQUE a la tabla acuses para soportar carga incremental

Esta restricción permite usar ON CONFLICT DO UPDATE para actualizar acuses
cuando la jerarquía de aceptación es mayor.
"""

import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="gestor_documental",
        user="postgres",
        password="G3st0radm$2025."
    )
    cursor = conn.cursor()
    
    print("="*80)
    print("🔧 AGREGANDO RESTRICCIÓN UNIQUE A TABLA acuses")
    print("="*80)
    print()
    
    # Verificar si ya existe la restricción
    cursor.execute("""
        SELECT constraint_name 
        FROM information_schema.table_constraints 
        WHERE table_name = 'acuses' 
        AND constraint_type = 'UNIQUE'
        AND constraint_name = 'uk_acuses_clave'
    """)
    
    if cursor.fetchone():
        print("✅ La restricción uk_acuses_clave ya existe")
    else:
        print("📝 Agregando restricción UNIQUE en clave_acuse...")
        
        # Primero eliminar duplicados existentes (mantener el de mayor jerarquía)
        cursor.execute("""
            -- Función para calcular jerarquía de estado
            CREATE OR REPLACE FUNCTION calcular_jerarquia_acuse(estado TEXT) RETURNS INT AS $$
            BEGIN
                RETURN CASE 
                    WHEN estado IS NULL OR estado = '' OR estado = 'Pendiente' THEN 1
                    WHEN estado = 'Acuse Recibido' THEN 2
                    WHEN estado = 'Acuse Bien/Servicio' THEN 3
                    WHEN estado = 'Rechazada' THEN 4
                    WHEN estado = 'Aceptación Expresa' THEN 5
                    WHEN estado = 'Aceptación Tácita' THEN 6
                    ELSE 1
                END;
            END;
            $$ LANGUAGE plpgsql IMMUTABLE;
        """)
        
        cursor.execute("""
            -- Eliminar duplicados manteniendo el de mayor jerarquía
            DELETE FROM acuses a
            USING acuses b
            WHERE a.id < b.id 
            AND a.clave_acuse = b.clave_acuse
            AND a.clave_acuse IS NOT NULL
            AND calcular_jerarquia_acuse(a.estado_docto) <= calcular_jerarquia_acuse(b.estado_docto)
        """)
        
        eliminados = cursor.rowcount
        if eliminados > 0:
            print(f"   🗑️  Eliminados {eliminados} duplicados (manteniendo el de mayor jerarquía)")
        
        # Agregar restricción UNIQUE
        cursor.execute("""
            ALTER TABLE acuses 
            ADD CONSTRAINT uk_acuses_clave UNIQUE (clave_acuse)
        """)
        
        conn.commit()
        print("   ✅ Restricción agregada exitosamente")
    
    print()
    print("="*80)
    print("✅ COMPLETADO")
    print("="*80)
    print()
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print()
    print("="*80)
    print("❌ ERROR")
    print("="*80)
    print()
    print(str(e))
    print()
    import traceback
    print(traceback.format_exc())
    print()

input("Presiona ENTER para salir...")
