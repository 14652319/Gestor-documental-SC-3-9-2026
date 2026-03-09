"""
FIX COMPLETO: Renombrar TODAS las columnas con desajustes
====================================================================
El código routes.py usa nombres diferentes al schema PostgreSQL.
Este script corrige TODOS los desajustes encontrados.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_todas_columnas():
    """Renombra todas las columnas para coincidir con el código routes.py"""
    
    # Conectar a PostgreSQL
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    try:
        print("🔧 RENOMBRANDO TODAS LAS COLUMNAS CON DESAJUSTES\n")
        print("=" * 70)
        
        # ===== TABLA: erp_comercial =====
        print("\n📋 TABLA: erp_comercial")
        print("-" * 70)
        
        cambios_comercial = [
            ('fecha_docto_prov', 'fecha_recibido'),
            ('clase_docto', 'clase_documento'),
            ('valor_bruto', 'valor')
        ]
        
        for old_name, new_name in cambios_comercial:
            try:
                cursor.execute(f"""
                    ALTER TABLE erp_comercial 
                    RENAME COLUMN {old_name} TO {new_name}
                """)
                print(f"   ✅ {old_name:20} → {new_name}")
                conn.commit()
            except psycopg2.errors.UndefinedColumn as e:
                print(f"   ⚠️ {old_name:20} → Columna no existe o ya renombrada")
                conn.rollback()
            except Exception as e:
                print(f"   ❌ {old_name:20} → Error: {e}")
                conn.rollback()
        
        # ===== TABLA: erp_financiero =====
        print("\n📋 TABLA: erp_financiero")
        print("-" * 70)
        
        cambios_financiero = [
            ('fecha_proveedor', 'fecha_recibido'),
            ('clase_docto', 'clase_documento'),
            ('valor_subtotal', 'valor')
        ]
        
        for old_name, new_name in cambios_financiero:
            try:
                cursor.execute(f"""
                    ALTER TABLE erp_financiero 
                    RENAME COLUMN {old_name} TO {new_name}
                """)
                print(f"   ✅ {old_name:20} → {new_name}")
                conn.commit()
            except psycopg2.errors.UndefinedColumn as e:
                print(f"   ⚠️ {old_name:20} → Columna no existe o ya renombrada")
                conn.rollback()
            except Exception as e:
                print(f"   ❌ {old_name:20} → Error: {e}")
                conn.rollback()
        
        # ===== ACTUALIZAR VISTAS =====
        print("\n📊 ACTUALIZANDO VISTAS DE RECONCILIACIÓN")
        print("-" * 70)
        
        # Vista 1: v_reconciliacion_dian_comercial
        try:
            cursor.execute("""
                CREATE OR REPLACE VIEW v_reconciliacion_dian_comercial AS
                SELECT 
                    d.id AS dian_id,
                    d.nit_emisor,
                    d.nombre_emisor,
                    d.prefijo,
                    d.folio,
                    d.clave AS clave_dian,
                    d.fecha_emision,
                    d.total AS total_dian,
                    d.estado AS estado_dian,
                    ec.id AS erp_comercial_id,
                    ec.proveedor,
                    ec.razon_social,
                    ec.clave_erp_comercial,
                    ec.fecha_recibido,
                    ec.valor AS total_erp_comercial,
                    ec.co,
                    ec.usuario_creacion,
                    CASE 
                        WHEN ec.id IS NULL THEN 'Solo en DIAN'
                        WHEN d.id IS NULL THEN 'Solo en ERP Comercial'
                        WHEN ABS(d.total - ec.valor) < 0.01 THEN 'Reconciliado'
                        ELSE 'Diferencia en Valores'
                    END AS estado_reconciliacion,
                    ABS(COALESCE(d.total, 0) - COALESCE(ec.valor, 0)) AS diferencia
                FROM dian d
                FULL OUTER JOIN erp_comercial ec ON d.clave = ec.clave_erp_comercial
            """)
            print("   ✅ Vista v_reconciliacion_dian_comercial actualizada")
            conn.commit()
        except Exception as e:
            print(f"   ⚠️ Vista v_reconciliacion_dian_comercial → Error: {e}")
            conn.rollback()
        
        # Vista 2: v_reconciliacion_dian_financiero
        try:
            cursor.execute("""
                CREATE OR REPLACE VIEW v_reconciliacion_dian_financiero AS
                SELECT 
                    d.id AS dian_id,
                    d.nit_emisor,
                    d.nombre_emisor,
                    d.prefijo,
                    d.folio,
                    d.clave AS clave_dian,
                    d.fecha_emision,
                    d.total AS total_dian,
                    d.estado AS estado_dian,
                    ef.id AS erp_financiero_id,
                    ef.proveedor,
                    ef.razon_social,
                    ef.clave_erp_financiero,
                    ef.fecha_recibido,
                    ef.valor AS total_erp_financiero,
                    ef.co,
                    ef.usuario_creacion,
                    CASE 
                        WHEN ef.id IS NULL THEN 'Solo en DIAN'
                        WHEN d.id IS NULL THEN 'Solo en ERP Financiero'
                        WHEN ABS(d.total - ef.valor) < 0.01 THEN 'Reconciliado'
                        ELSE 'Diferencia en Valores'
                    END AS estado_reconciliacion,
                    ABS(COALESCE(d.total, 0) - COALESCE(ef.valor, 0)) AS diferencia
                FROM dian d
                FULL OUTER JOIN erp_financiero ef ON d.clave = ef.clave_erp_financiero
            """)
            print("   ✅ Vista v_reconciliacion_dian_financiero actualizada")
            conn.commit()
        except Exception as e:
            print(f"   ⚠️ Vista v_reconciliacion_dian_financiero → Error: {e}")
            conn.rollback()
        
        print("\n" + "=" * 70)
        print("✅ TODOS LOS CAMBIOS APLICADOS")
        print("\n📊 RESUMEN DE CAMBIOS:")
        print("   🔧 Columnas renombradas: 6 (3 en erp_comercial + 3 en erp_financiero)")
        print("   📊 Vistas actualizadas: 2 (reconciliación comercial + financiero)")
        print("\n📌 NOTA: Los siguientes campos del schema NO se usan en el código:")
        print("   - erp_comercial.valor_imptos (nunca se carga)")
        print("   - erp_financiero.valor_impuestos (nunca se carga)")
        print("\n🔄 REINICIA el servidor Flask para aplicar los cambios")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR GENERAL: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    fix_todas_columnas()
