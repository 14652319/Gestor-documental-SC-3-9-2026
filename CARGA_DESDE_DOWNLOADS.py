"""
CARGA DESDE DOWNLOADS - Procesamiento directo
Fecha: 19 de Febrero de 2026

Carga los archivos directamente desde Downloads/Ricardo
"""

import os
import sys
from pathlib import Path
from datetime import datetime, date

# Agregar rutas al path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Flask app context
os.environ['FLASK_ENV'] = 'development'

print("="*80)
print("🔥 CARGA DESDE DOWNLOADS")
print("="*80)

from app import app, db
from modules.dian_vs_erp.routes import read_csv
from sqlalchemy import create_engine
import polars as pl
import io

# Rutas de archivos en Downloads (usar raw string para evitar escape)
DOWNLOADS_DIR = Path(r"C:/Users/Usuario/Downloads/Ricardo")
archivos = {
    "dian": DOWNLOADS_DIR / "Dian.xlsx",
    "erp_fn": DOWNLOADS_DIR / "ERP Financiero 18 02 2026.xlsx",
    "erp_cm": DOWNLOADS_DIR / "ERP comercial 18 02 2026.xlsx",
    "acuses": DOWNLOADS_DIR / "acuses 2.xlsx",
}

print("\n1️⃣ Verificando archivos en Downloads...")
for key, archivo in archivos.items():
    if archivo.exists():
        size_mb = archivo.stat().st_size / (1024*1024)
        print(f"   ✅ {key.upper():10s}: {archivo.name} ({size_mb:.1f} MB)")
    else:
        print(f"   ❌ {key.upper():10s}: NO ENCONTRADO - {archivo}")

print("\n2️⃣ Leyendo archivos...")
dfs = {}

with app.app_context():
    for key, archivo in archivos.items():
        if not archivo.exists():
            continue
            
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

    if len(dfs) == 0:
        print("\n❌ No se pudo leer ningún archivo")
        sys.exit(1)

    print(f"\n3️⃣ Conectando a PostgreSQL...")
    try:
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        raw_conn = engine.raw_connection()
        cursor = raw_conn.cursor()
        print(f"   ✅ Conexión exitosa")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        sys.exit(1)

    print("\n4️⃣ Construyendo diccionario de tipos de tercero...")
    tipo_tercero_dict = {}
    
    for key in ['erp_cm', 'erp_fn']:
        if key not in dfs:
            continue
        
        df_pd = dfs[key].to_pandas()
        proveedor_col = None
        
        # Detectar columna de proveedor
        for col in df_pd.columns:
            if 'proveedor' in col.lower() and 'razon' not in col.lower():
                proveedor_col = col
                break
        
        if proveedor_col:
            for _, row in df_pd.iterrows():
                nit = str(row.get(proveedor_col, '')).strip()
                if nit:
                    tipo_tercero_dict[nit] = 'PROVEEDOR'
    
    print(f"   ✅ {len(tipo_tercero_dict):,} terceros clasificados")

    # ============== INSERCIÓN EN DIAN ==============
    if 'dian' in dfs:
        print("\n5️⃣ Insertando en tabla DIAN...")
        try:
            dian_df = dfs['dian']
            dian_pd = dian_df.to_pandas()
            
            # Normalizar columnas
            dian_pd.columns = [col.lower().strip() for col in dian_pd.columns]
            
            # Detectar columna CUFE
            cufe_col = None
            for col in dian_pd.columns:
                if 'cufe' in col or 'cude' in col:
                    cufe_col = col
                    print(f"      ✅ Columna CUFE detectada: '{cufe_col}'")
                    break
            
            # Limpiar tabla
            cursor.execute("DELETE FROM dian")
            print(f"      ✅ Tabla limpiada")
            
            # Preparar registros
            registros = []
            fecha_hoy = date.today()
            
            for idx, row in dian_pd.iterrows():
                nit = str(row.get('nit emisor', '')).strip()
                razon = str(row.get('nombre  emisor', row.get('nombre emisor', ''))).strip()[:255]
                fecha_str = str(row.get('fecha emisión', row.get('fecha emision', '')))
                
                # Parsear fecha
                try:
                    if isinstance(fecha_str, str) and fecha_str.strip():
                        fecha = datetime.strptime(fecha_str[:10], '%Y-%m-%d').date()
                    else:
                        fecha = fecha_hoy
                except:
                    fecha = fecha_hoy
                
                prefijo = str(row.get('prefijo', '')).strip()
                folio = str(row.get('folio', '')).strip()
                valor = float(row.get('valor total', row.get('total', 0)))
                tipo_doc = str(row.get('tipo de documento', 'Factura Electrónica')).strip()
                cufe = str(row.get(cufe_col, '')) if cufe_col else ''
                forma_pago = str(row.get('forma de pago', '2')).strip()
                
                # Calcular campos
                clave = f"{nit}{prefijo}{folio}"
                tipo_tercero = tipo_tercero_dict.get(nit, 'Externo')
                n_dias = (fecha_hoy - fecha).days if fecha else 0
                
                registros.append({
                    'nit_emisor': nit,
                    'nombre_emisor': razon,
                    'fecha_emision': fecha,
                    'prefijo': prefijo,
                    'folio': folio,
                    'total': valor,
                    'tipo_documento': tipo_doc,
                    'cufe_cude': cufe,
                    'forma_pago': forma_pago,
                    'clave': clave,
                    'clave_acuse': cufe,
                    'tipo_tercero': tipo_tercero,
                    'n_dias': n_dias,
                    'modulo': 'DIAN'
                })
                
                if idx >= 4:  # Mostrar primeros 5
                    break
            
            # COPY FROM
            buffer = io.StringIO()
            for reg in registros[:5]:  # Solo primeros 5 para prueba
                buffer.write(f"{reg['nit_emisor']}\t")
                buffer.write(f"{reg['nombre_emisor']}\t")
                buffer.write(f"{reg['fecha_emision']}\t")
                buffer.write(f"{reg['prefijo']}\t")
                buffer.write(f"{reg['folio']}\t")
                buffer.write(f"{reg['total']}\t")
                buffer.write(f"{reg['tipo_documento']}\t")
                buffer.write(f"{reg['cufe_cude']}\t")
                buffer.write(f"{reg['forma_pago']}\t")
                buffer.write(f"{reg['clave']}\t")
                buffer.write(f"{reg['clave_acuse']}\t")
                buffer.write(f"{reg['tipo_tercero']}\t")
                buffer.write(f"{reg['n_dias']}\t")
                buffer.write(f"{reg['modulo']}\n")
            
            buffer.seek(0)
            cursor.copy_from(
                buffer,
                'dian',
                sep='\t',
                null='',
                columns=(
                    'nit_emisor', 'nombre_emisor', 'fecha_emision',
                    'prefijo', 'folio', 'total', 'tipo_documento', 'cufe_cude',
                    'forma_pago', 'clave', 'clave_acuse', 'tipo_tercero', 'n_dias', 'modulo'
                )
            )
            
            print(f"      ✅ {len(registros[:5])} registros insertados (PRUEBA)")
            
        except Exception as e:
            print(f"      ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            raw_conn.rollback()
    
    # COMMIT
    print("\n6️⃣ Haciendo COMMIT...")
    try:
        raw_conn.commit()
        print("   ✅ COMMIT exitoso")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        raw_conn.rollback()
    
    cursor.close()
    raw_conn.close()

print("\n7️⃣ Verificando resultados...")
with app.app_context():
    try:
        count = db.session.execute(db.text("SELECT COUNT(*) FROM dian")).scalar()
        print(f"\n   📊 DIAN: {count:,} registros")
        
        if count > 0:
            # Mostrar muestra
            resultado = db.session.execute(db.text("""
                SELECT nit_emisor, prefijo, folio, LENGTH(cufe_cude), tipo_tercero
                FROM dian LIMIT 3
            """)).fetchall()
            
            print(f"\n   📋 Muestra:")
            for row in resultado:
                print(f"      • NIT={row[0]}, {row[1]}-{row[2]}, CUFE len={row[3]}, Tipo={row[4]}")
            
            print(f"\n   ✅ ¡INSERCIÓN EXITOSA!")
        else:
            print(f"\n   ⚠️ Tabla sigue vacía")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

print("\n" + "="*80)
print("✅ PROCESO COMPLETADO")
print("="*80)
