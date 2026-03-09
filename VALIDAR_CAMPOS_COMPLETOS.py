"""
VALIDACIÓN DE CAMPOS COMPLETOS EN ERP_COMERCIAL
Verifica que clase_documento, fecha_recibido, valor, etc. estén poblados
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)

print("\n" + "="*80)
print("VALIDACIÓN DE CAMPOS EN ERP_COMERCIAL")
print("="*80)

with engine.connect() as conn:
    # Total registros
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial"))
    total = result.scalar()
    print(f"\nTotal registros: {total:,}")
    
    # Validar proveedor
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE proveedor IS NULL OR proveedor = ''"))
    null_proveedor = result.scalar()
    print(f"\nProveedor:")
    print(f"  NULL/Vacío: {null_proveedor:,} ({null_proveedor/total*100:.1f}%)")
    print(f"  Poblado: {total-null_proveedor:,} ({(total-null_proveedor)/total*100:.1f}%)")
    
    # Validar razon_social
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE razon_social IS NULL OR razon_social = ''"))
    null_razon = result.scalar()
    print(f"\nRazón Social:")
    print(f"  NULL/Vacío: {null_razon:,} ({null_razon/total*100:.1f}%)")
    print(f"  Poblado: {total-null_razon:,} ({(total-null_razon)/total*100:.1f}%)")
    
    # Validar clase_documento ⭐ CRÍTICO
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE clase_documento IS NULL OR clase_documento = ''"))
    null_clase = result.scalar()
    print(f"\nClase Documento: ⭐ CRÍTICO")
    print(f"  NULL/Vacío: {null_clase:,} ({null_clase/total*100:.1f}%)")
    print(f"  Poblado: {total-null_clase:,} ({(total-null_clase)/total*100:.1f}%)")
    
    # Validar fecha_recibido ⭐ CRÍTICO
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE fecha_recibido IS NULL"))
    null_fecha = result.scalar()
    print(f"\nFecha Recibido: ⭐ CRÍTICO")
    print(f"  NULL: {null_fecha:,} ({null_fecha/total*100:.1f}%)")
    print(f"  Poblado: {total-null_fecha:,} ({(total-null_fecha)/total*100:.1f}%)")
    
    # Validar valor ⭐ CRÍTICO
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE valor IS NULL OR valor = 0"))
    null_valor = result.scalar()
    print(f"\nValor: ⭐ CRÍTICO")
    print(f"  NULL/Cero: {null_valor:,} ({null_valor/total*100:.1f}%)")
    print(f"  Poblado: {total-null_valor:,} ({(total-null_valor)/total*100:.1f}%)")
    
    # Validar prefijo
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE prefijo IS NULL OR prefijo = ''"))
    null_prefijo = result.scalar()
    print(f"\nPrefijo:")
    print(f"  NULL/Vacío: {null_prefijo:,} ({null_prefijo/total*100:.1f}%)")
    print(f"  Poblado: {total-null_prefijo:,} ({(total-null_prefijo)/total*100:.1f}%)")
    
    # Validar folio
    result = conn.execute(text("SELECT COUNT(*) FROM erp_comercial WHERE folio IS NULL OR folio = '' OR folio = '0'"))
    null_folio = result.scalar()
    print(f"\nFolio:")
    print(f"  NULL/Vacío/Cero: {null_folio:,} ({null_folio/total*100:.1f}%)")
    print(f"  Poblado: {total-null_folio:,} ({(total-null_folio)/total*100:.1f}%)")
    
    # Muestra de datos
    print(f"\n" + "="*80)
    print("MUESTRA DE 5 REGISTROS")
    print("="*80)
    result = conn.execute(text("""
        SELECT 
            proveedor,
            razon_social,
            clase_documento,
            fecha_recibido,
            valor,
            prefijo,
            folio,
            docto_proveedor
        FROM erp_comercial
        WHERE clase_documento IS NOT NULL
        LIMIT 5
    """))
    
    for idx, row in enumerate(result, 1):
        print(f"\nRegistro {idx}:")
        print(f"  Proveedor: {row[0]}")
        print(f"  Razón Social: {row[1][:50] if row[1] else 'NULL'}...")
        print(f"  Clase Documento: {row[2]}")
        print(f"  Fecha Recibido: {row[3]}")
        print(f"  Valor: ${row[4]:,.2f}")
        print(f"  Prefijo: '{row[5]}'")
        print(f"  Folio: '{row[6]}'")
        print(f"  Docto Proveedor: {row[7]}")

print("\n" + "="*80)
print()
