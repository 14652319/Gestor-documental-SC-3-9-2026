"""
CARGA MANUAL DIRECTA - Forzar inserción en tablas individuales
Fecha: 19 de Febrero de 2026

Este script ejecuta SOLO la inserción en tablas individuales,
omitiendo el maestro consolidado.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Agregar rutas al path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Flask app context
os.environ['FLASK_ENV'] = 'development'

print("="*80)
print("🔥 CARGA MANUAL: Inserción Directa en Tablas Individuales")
print("="*80)

from app import app, db
from modules.dian_vs_erp.routes import (
    insertar_dian_bulk,
    insertar_erp_comercial_bulk,
    insertar_erp_financiero_bulk,
    insertar_acuses_bulk,
    read_csv
)
from sqlalchemy import create_engine

print("\n1️⃣ Buscando archivos en uploads/...")
uploads = {
    "dian": BASE_DIR / "uploads" / "dian",
    "erp_fn": BASE_DIR / "uploads" / "erp_fn",
    "erp_cm": BASE_DIR / "uploads" / "erp_cm", 
    "acuses": BASE_DIR / "uploads" / "acuses",
}

archivos = {}
for key, carpeta in uploads.items():
    excel_files = list(carpeta.glob("*.xlsx"))
    if excel_files:
        archivos[key] = excel_files[0]
        print(f"   ✅ {key.upper():15s}: {excel_files[0].name}")

if len(archivos) < 4:
    print("\n❌ ERROR: No se encontraron todos los archivos necesarios")
    sys.exit(1)

print("\n2️⃣ Leyendo archivos con Polars...")
dfs = {}

with app.app_context():
    for key, archivo in archivos.items():
        print(f"\n   📂 Leyendo {key.upper()}...")
        try:
            df = read_csv(str(archivo))
            if df is not None and len(df) > 0:
                print(f"      ✅ {len(df):,} registros, {len(df.columns)} columnas")
                dfs[key] = df
            else:
                print(f"      ⚠️ DataFrame vacío")
        except Exception as e:
            print(f"      ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

print(f"\n3️⃣ Conectando a PostgreSQL...")
with app.app_context():
    try:
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        raw_conn = engine.raw_connection()
        cursor = raw_conn.cursor()
        print(f"   ✅ Conexión exitosa")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        sys.exit(1)

    print("\n4️⃣ Preparando diccionario de tipos de tercero...")
    # Crear diccionario vacío (se podría mejorar leyendo de BD)
    tipo_tercero_dict = {}
    
    # Si hay ERP, construir tipo_tercero desde ahí
    if 'erp_cm' in dfs or 'erp_fn' in dfs:
        print("   ℹ️ Analizando terceros desde ERPs...")
        tipo_tercero_por_nit = {}
        
        for key in ['erp_cm', 'erp_fn']:
            if key in dfs:
                df_temp = dfs[key].to_pandas()
                for _, row in df_temp.iterrows():
                    # Buscar columna de proveedor
                    nit = None
                    for col in df_temp.columns:
                        if 'proveedor' in col.lower() and 'razon' not in col.lower():
                            nit = str(row.get(col, '')).strip()
                            break
                    
                    if nit:
                        if nit not in tipo_tercero_por_nit:
                            tipo_tercero_por_nit[nit] = set()
                        tipo_tercero_por_nit[nit].add('PROVEEDOR')
        
        # Consolidar
        for nit, tipos in tipo_tercero_por_nit.items():
            if 'PROVEEDOR' in tipos:
                tipo_tercero_dict[nit] = 'PROVEEDOR'
        
        print(f"   ✅ {len(tipo_tercero_dict):,} terceros clasificados")
    
    print("\n5️⃣ Insertando en tabla DIAN...")
    try:
        if 'dian' in dfs:
            count = insertar_dian_bulk(dfs['dian'], cursor, tipo_tercero_dict)
            print(f"   ✅ {count:,} registros insertados")
        else:
            print("   ⚠️ No hay archivo DIAN")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raw_conn.rollback()
    
    print("\n6️⃣ Insertando en tabla ERP_COMERCIAL...")
    try:
        if 'erp_cm' in dfs:
            count = insertar_erp_comercial_bulk(dfs['erp_cm'], cursor)
            print(f"   ✅ {count:,} registros insertados")
        else:
            print("   ⚠️ No hay archivo ERP Comercial")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raw_conn.rollback()
    
    print("\n7️⃣ Insertando en tabla ERP_FINANCIERO...")
    try:
        if 'erp_fn' in dfs:
            count = insertar_erp_financiero_bulk(dfs['erp_fn'], cursor)
            print(f"   ✅ {count:,} registros insertados")
        else:
            print("   ⚠️ No hay archivo ERP Financiero")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raw_conn.rollback()
    
    print("\n8️⃣ Insertando en tabla ACUSES...")
    try:
        if 'acuses' in dfs:
            count = insertar_acuses_bulk(dfs['acuses'], cursor)
            print(f"   ✅ {count:,} registros insertados")
        else:
            print("   ⚠️ No hay archivo ACUSES")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raw_conn.rollback()
    
    print("\n9️⃣ Haciendo COMMIT...")
    try:
        raw_conn.commit()
        print("   ✅ COMMIT exitoso")
    except Exception as e:
        print(f"   ❌ ERROR en COMMIT: {e}")
        raw_conn.rollback()
    
    # Cerrar conexión
    cursor.close()
    raw_conn.close()

print("\n" + "="*80)
print("✅ CARGA MANUAL COMPLETADA")
print("="*80)

# Verificar resultados
print("\n10️⃣ Verificando resultados...")
with app.app_context():
    try:
        result_dian = db.session.execute(db.text("SELECT COUNT(*) FROM dian")).scalar()
        result_erp_cm = db.session.execute(db.text("SELECT COUNT(*) FROM erp_comercial")).scalar()
        result_erp_fn = db.session.execute(db.text("SELECT COUNT(*) FROM erp_financiero")).scalar()
        result_acuses = db.session.execute(db.text("SELECT COUNT(*) FROM acuses")).scalar()
        
        print(f"\n   📊 RESULTADOS FINALES:")
        print(f"      • DIAN:          {result_dian:>10,} registros")
        print(f"      • ERP Comercial: {result_erp_cm:>10,} registros")
        print(f"      • ERP Financiero:{result_erp_fn:>10,} registros")
        print(f"      • Acuses:        {result_acuses:>10,} registros")
        
        if result_dian > 0 and result_acuses > 0:
            print(f"\n   ✅ ¡ÉXITO! Todas las tablas tienen datos")
            print(f"   🎯 Ahora puedes verificar el Visor V2")
        else:
            print(f"\n   ⚠️ Algunas tablas están vacías, revisar errores arriba")
    except Exception as e:
        print(f"   ❌ ERROR verificando: {e}")
