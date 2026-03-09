"""
VALIDACIÓN COMPLETA DE TODAS LAS TABLAS
Verifica conteo y calidad de datos
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

print("\n" + "="*80)
print("VALIDACIÓN COMPLETA DE TODAS LAS TABLAS")
print("="*80)

with engine.connect() as conn:
    # Verificar tablas existentes
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('dian', 'erp_comercial', 'erp_financiero', 'acuses_recibidos', 'maestro_dian_vs_erp')
        ORDER BY table_name
    """))
    tablas_existentes = [row[0] for row in result]
    
    print(f"\n📋 Tablas disponibles: {', '.join(tablas_existentes)}")
    print("\n" + "-"*80)
    
    # TABLA 1: DIAN
    if 'dian' in tablas_existentes:
        print("\n📊 TABLA: DIAN")
        result = conn.execute(text("SELECT COUNT(*) FROM dian"))
        total = result.scalar()
        print(f"   Total registros: {total:,}")
        
        if total > 0:
            # Muestra de datos
            result = conn.execute(text("""
                SELECT nit_adquiriente, razon_social, numero, prefijo, folio, fecha_factura, valor
                FROM dian
                LIMIT 3
            """))
            print(f"\n   Muestra de datos:")
            for idx, row in enumerate(result, 1):
                print(f"   {idx}. NIT: {row[0]} | Razón: {row[1][:30]}... | Número: {row[2]} | Prefijo: '{row[3]}' | Folio: '{row[4]}'")
            
            # Validar campos poblados
            result = conn.execute(text("SELECT COUNT(*) FROM dian WHERE prefijo IS NULL OR prefijo = ''"))
            null_prefijo = result.scalar()
            print(f"\n   Prefijo NULL/Vacío: {null_prefijo:,} ({null_prefijo/total*100:.1f}%)")
            
            result = conn.execute(text("SELECT COUNT(*) FROM dian WHERE folio IS NULL OR folio = ''"))
            null_folio = result.scalar()
            print(f"   Folio NULL/Vacío: {null_folio:,} ({null_folio/total*100:.1f}%)")
    else:
        print("\n❌ TABLA DIAN no existe")
    
    # TABLA 2: ERP COMERCIAL
    print("\n" + "-"*80)
    if 'erp_comercial' in tablas_existentes:
        print("\n📊 TABLA: ERP_COMERCIAL")
        result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
        total = result.scalar()
        print(f"   Total registros: {total:,}")
        
        if total > 0:
            # Muestra de datos
            result = conn.execute(text("""
                SELECT proveedor, razon_social, docto_proveedor, clase_documento, fecha_recibido, valor
                FROM erp_comercial
                WHERE clase_documento IS NOT NULL
                LIMIT 3
            """))
            print(f"\n   Muestra de datos:")
            for idx, row in enumerate(result, 1):
                print(f"   {idx}. Proveedor: {row[0]} | Docto: {row[2]} | Clase: {row[3]} | Fecha: {row[4]} | Valor: ${row[5]:,.2f}")
            
            # Validar campos críticos
            result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE clase_documento IS NULL OR clase_documento = ''"))
            null_clase = result.scalar()
            print(f"\n   ⭐ clase_documento NULL/Vacío: {null_clase:,} ({null_clase/total*100:.1f}%)")
            
            result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE fecha_recibido IS NULL"))
            null_fecha = result.scalar()
            print(f"   ⭐ fecha_recibido NULL: {null_fecha:,} ({null_fecha/total*100:.1f}%)")
            
            result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE valor IS NULL OR valor = 0"))
            null_valor = result.scalar()
            print(f"   ⭐ valor NULL/Cero: {null_valor:,} ({null_valor/total*100:.1f}%)")
    else:
        print("\n❌ TABLA ERP_COMERCIAL no existe")
    
    # TABLA 3: ERP FINANCIERO
    print("\n" + "-"*80)
    if 'erp_financiero' in tablas_existentes:
        print("\n📊 TABLA: ERP_FINANCIERO")
        result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
        total = result.scalar()
        print(f"   Total registros: {total:,}")
        
        if total > 0:
            # Muestra de datos
            result = conn.execute(text("""
                SELECT proveedor, razon_social, docto_proveedor, clase_documento, fecha_recibido, valor
                FROM erp_financiero
                WHERE clase_documento IS NOT NULL
                LIMIT 3
            """))
            print(f"\n   Muestra de datos:")
            for idx, row in enumerate(result, 1):
                print(f"   {idx}. Proveedor: {row[0]} | Docto: {row[2]} | Clase: {row[3]} | Fecha: {row[4]} | Valor: ${row[5]:,.2f}")
            
            # Validar campos críticos
            result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero WHERE clase_documento IS NULL OR clase_documento = ''"))
            null_clase = result.scalar()
            print(f"\n   ⭐ clase_documento NULL/Vacío: {null_clase:,} ({null_clase/total*100:.1f}%)")
            
            result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero WHERE fecha_recibido IS NULL"))
            null_fecha = result.scalar()
            print(f"   ⭐ fecha_recibido NULL: {null_fecha:,} ({null_fecha/total*100:.1f}%)")
            
            result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero WHERE valor IS NULL OR valor = 0"))
            null_valor = result.scalar()
            print(f"   ⭐ valor NULL/Cero: {null_valor:,} ({null_valor/total*100:.1f}%)")
    else:
        print("\n❌ TABLA ERP_FINANCIERO no existe")
    
    # TABLA 4: ACUSES
    print("\n" + "-"*80)
    if 'acuses_recibidos' in tablas_existentes:
        print("\n📊 TABLA: ACUSES_RECIBIDOS")
        result = conn.execute(text("SELECT COUNT(*) FROM acuses_recibidos"))
        total = result.scalar()
        print(f"   Total registros: {total:,}")
    else:
        print("\n⚠️  TABLA ACUSES_RECIBIDOS no existe (opcional)")
    
    # RESUMEN FINAL
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    
    total_general = 0
    
    if 'dian' in tablas_existentes:
        result = conn.execute(text("SELECT COUNT(*) FROM dian"))
        total_dian = result.scalar()
        total_general += total_dian
        estado_dian = "✅" if total_dian > 0 else "❌"
        print(f"\n{estado_dian} DIAN: {total_dian:,} registros (Esperado: ~66,276)")
    
    if 'erp_comercial' in tablas_existentes:
        result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
        total_cm = result.scalar()
        total_general += total_cm
        estado_cm = "✅" if total_cm > 0 else "❌"
        print(f"{estado_cm} ERP Comercial: {total_cm:,} registros (Esperado: ~63,539)")
    
    if 'erp_financiero' in tablas_existentes:
        result = conn.execute(text("SELECT COUNT(*) FROM erp_financiero"))
        total_fn = result.scalar()
        total_general += total_fn
        estado_fn = "✅" if total_fn > 0 else "❌"
        print(f"{estado_fn} ERP Financiero: {total_fn:,} registros (Esperado: ~3,180)")
    
    print(f"\n{'✅' if total_general > 100000 else '⚠️ '} TOTAL GENERAL: {total_general:,} registros")
    print(f"   Esperado: ~133,000 registros")
    
    if total_general > 100000:
        print(f"\n🎉 CARGA COMPLETA EXITOSA")
    else:
        print(f"\n⚠️  Faltan datos por cargar")

print("\n" + "="*80 + "\n")
