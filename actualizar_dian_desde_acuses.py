"""
ACTUALIZAR DIAN CON DATOS DE ACUSES
Usar CUFE para vincular y extraer PREFIJO + FOLIO
"""

import psycopg2
import re

conn = psycopg2.connect(
    dbname='gestor_documental',
    user='postgres',
    password='G3st0radm$2025.',
    host='localhost',
    port='5432'
)
conn.autocommit = False
cursor = conn.cursor()

try:
    print("\n" + "="*80)
    print("🔄 ACTUALIZANDO DIAN CON DATOS DE ACUSES")
    print("="*80)
    
    # 1. Ver situación actual
    print("\n1️⃣ SITUACIÓN ACTUAL:")
    cursor.execute("SELECT COUNT(*) FROM dian WHERE prefijo IS NULL OR prefijo = ''")
    sin_prefijo = cursor.fetchone()[0]
    print(f"   DIAN sin prefijo: {sin_prefijo:,} registros")
    
    cursor.execute("SELECT COUNT(*) FROM acuses")
    total_acuses = cursor.fetchone()[0]
    print(f"   ACUSES total: {total_acuses:,} registros")
    
    # 2. Ver cuántos matches podemos hacer por CUFE
    cursor.execute("""
        SELECT COUNT(*)
        FROM dian d
        INNER JOIN acuses a ON d.cufe_cude = a.cufe
    """)
    matches_posibles = cursor.fetchone()[0]
    print(f"   Matches posibles (DIAN ↔ ACUSES por CUFE): {matches_posibles:,}")
    
    # 3. Actualizar DIAN con prefijo y folio de ACUSES
    print("\n2️⃣ ACTUALIZANDO PREFIJO Y FOLIO EN DIAN...")
    
    # Usamos una función SQL inline para extraer prefijo y folio
    cursor.execute("""
        -- Función temporal para extraer prefijo (letras + números al inicio)
        CREATE OR REPLACE FUNCTION extraer_prefijo_temp(texto TEXT) 
        RETURNS TEXT AS $$
        BEGIN
            -- Extrae todo lo que NO sea dígito puro al final
            -- Ejemplo: "1FEA168" → busca hasta donde empieza la secuencia numérica final
            RETURN substring(texto from '^([A-Z0-9]*?)[0-9]+$');
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
        
        -- Función temporal para extraer folio (números al final)
        CREATE OR REPLACE FUNCTION extraer_folio_temp(texto TEXT) 
        RETURNS TEXT AS $$
        BEGIN
            -- Extrae solo los números al final
            RETURN substring(texto from '([0-9]+)$');
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)
    
    # UPDATE masivo usando el CUFE como vínculo
    cursor.execute("""
        UPDATE dian d
        SET 
            prefijo = extraer_prefijo_temp(a.factura),
            folio = extraer_folio_temp(a.factura),
            fecha_actualizacion = CURRENT_TIMESTAMP
        FROM acuses a
        WHERE d.cufe_cude = a.cufe
          AND a.factura IS NOT NULL
          AND a.factura != ''
    """)
    actualizados = cursor.rowcount
    print(f"   ✅ {actualizados:,} registros actualizados con prefijo/folio de ACUSES")
    
   # 4. Regenerar CLAVES en DIAN (DIRECTO EN SQL)
    print("\n3️⃣ REGENERANDO CLAVES EN DIAN...")
    
    # Función SQL para limpiar folio (eliminar ceros a la izquierda)
    cursor.execute("""
        CREATE OR REPLACE FUNCTION limpiar_folio_temp(folio TEXT) 
        RETURNS TEXT AS $$
        BEGIN
            -- Elimina ceros a la izquierda: "00168" → "168"
            RETURN LTRIM(folio, '0');
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)
    
    # UPDATE masivo: concatenar NIT + PREFIJO + FOLIO limpio
    cursor.execute("""
        UPDATE dian
        SET clave = nit_emisor || COALESCE(prefijo, '') || limpiar_folio_temp(COALESCE(folio, '0'))
        WHERE prefijo IS NOT NULL AND prefijo != ''
    """)
    claves_regeneradas = cursor.rowcount
    print(f"   ✅ {claves_regeneradas:,} claves regeneradas")
    
    # 5. Agregar UNIQUE constraint en CUFE
    print("\n4️⃣ AGREGANDO UNIQUE CONSTRAINT EN CUFE...")
    try:
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_dian_cufe_unique 
            ON dian(cufe_cude) 
            WHERE cufe_cude IS NOT NULL AND cufe_cude != ''
        """)
        print("   ✅ UNIQUE constraint en CUFE agregado")
    except Exception as e:
        print(f"   ⚠️ Constraint ya existe o error: {str(e)[:100]}")
    
    # 6. Ver resultados finales
    print("\n5️⃣ RESULTADOS FINALES:")
    cursor.execute("""
        SELECT COUNT(*) FROM dian WHERE prefijo IS NOT NULL AND prefijo != ''
    """)
    con_prefijo = cursor.fetchone()[0]
    print(f"   DIAN con prefijo OK: {con_prefijo:,} registros")
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM dian d
        INNER JOIN erp_financiero ef 
            ON d.clave = ef.clave_erp_financiero
    """)
    matches_fn = cursor.fetchone()[0]
    print(f"   Matches DIAN ↔ ERP_FINANCIERO (por clave): {matches_fn:,}")
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM dian d
        INNER JOIN erp_comercial ec 
            ON d.clave = ec.clave_erp_comercial
    """)
    matches_cm = cursor.fetchone()[0]
    print(f"   Matches DIAN ↔ ERP_COMERCIAL (por clave): {matches_cm:,}")
    
    # 7. Ver ejemplos actualizados
    print("\n6️⃣ EJEMPLOS DE REGISTROS ACTUALIZADOS (NIT 805013653):")
    cursor.execute("""
        SELECT nit_emisor, prefijo, folio, clave, LEFT(cufe_cude, 20) as cufe_inicio
        FROM dian
        WHERE nit_emisor = '805013653'
          AND prefijo IS NOT NULL
        LIMIT 5
    """)
    ejemplos = cursor.fetchall()
    for ej in ejemplos:
        print(f"   NIT: {ej[0]} | Prefijo: {ej[1]:5} | Folio: {ej[2]:5} | Clave: {ej[3]:20} | CUFE: {ej[4]}...")
    
    # COMMIT final
    conn.commit()
    print("\n" + "="*80)
    print("✅ ACTUALIZACIÓN COMPLETADA Y GUARDADA")
    print("="*80)
    print("""
    PRÓXIMOS PASOS:
    1. Reconstruir la tabla maestro_dian_vs_erp
    2. Verificar que ahora aparezcan estados contables correctos
    3. El servidor necesita restart para aplicar cambios
    """)
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ ERROR: {str(e)}")
    print("   Se hizo ROLLBACK, no se aplicaron cambios")
    raise

finally:
    cursor.close()
    conn.close()
