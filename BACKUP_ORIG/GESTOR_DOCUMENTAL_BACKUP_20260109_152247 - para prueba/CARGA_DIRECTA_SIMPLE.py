"""
CARGA DIRECTA SIMPLE - Sin validaciones, sin UPSERT, solo INSERT
Diciembre 29, 2025

USO:
    python CARGA_DIRECTA_SIMPLE.py ruta_archivo_dian.xlsx

CARACTERÍSTICAS:
- Lee archivo Excel/CSV directo con Polars
- Inserta TODO en maestro_dian_vs_erp
- Sin duplicados, sin validaciones
- VELOCIDAD MÁXIMA
"""

import sys
import os
import polars as pl
import psycopg2
import io
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')

def limpiar_nit(nit_str):
    """Extrae solo números del NIT"""
    if not nit_str:
        return ""
    import re
    return re.sub(r'[^0-9]', '', str(nit_str))

def extraer_prefijo(docto):
    """Extrae solo LETRAS"""
    if not docto:
        return ""
    import re
    return re.sub(r'[0-9\-\.]', '', str(docto)).strip().upper()

def extraer_folio(docto):
    """Extrae últimos 8 dígitos sin ceros"""
    if not docto:
        return "0"
    import re
    numeros = re.sub(r'[^0-9]', '', str(docto))
    if not numeros:
        return "0"
    ultimos = numeros[-8:] if len(numeros) >= 8 else numeros
    return ultimos.lstrip('0') or '0'

def procesar_archivo_dian(archivo_path):
    """Procesa archivo DIAN e inserta directo en PostgreSQL"""
    
    print("=" * 80)
    print(f"📂 PROCESANDO: {archivo_path}")
    print("=" * 80)
    
    # 1. LEER ARCHIVO CON PANDAS (más compatible que Polars para Excel)
    print("\n1️⃣ Leyendo archivo...")
    ext = os.path.splitext(archivo_path)[1].lower()
    
    if ext in ['.xlsx', '.xls', '.xlsm']:
        import pandas as pd
        df_pd = pd.read_excel(archivo_path, dtype=str)
    elif ext == '.csv':
        df_pd = pl.read_csv(archivo_path, infer_schema_length=0).to_pandas()
    else:
        print(f"❌ Extensión no soportada: {ext}")
        return
    
    print(f"   ✅ {len(df_pd):,} registros leídos")
    
    # 2. NORMALIZAR COLUMNAS
    df_pd.columns = [c.strip().lower() for c in df_pd.columns]
    
    # 3. PREPARAR REGISTROS PARA POSTGRESQL
    print("\n2️⃣ Preparando registros...")
    registros = []
    
    for idx, row in df_pd.iterrows():
        # Extraer campos
        nit = limpiar_nit(row.get('nit emisor', row.get('nit_emisor', '')))
        razon_social = str(row.get('nombre emisor', row.get('razon_social', ''))).strip()
        
        fecha_raw = row.get('fecha emision', row.get('fecha_emision', date.today()))
        if isinstance(fecha_raw, str):
            try:
                fecha = datetime.strptime(fecha_raw, '%Y-%m-%d').date()
            except:
                fecha = date.today()
        else:
            fecha = fecha_raw
        
        prefijo_raw = str(row.get('prefijo', ''))
        prefijo = extraer_prefijo(prefijo_raw)
        
        folio_raw = str(row.get('numero', row.get('folio', '')))
        folio = extraer_folio(folio_raw)
        
        valor = float(row.get('valor', 0))
        tipo_doc = str(row.get('tipo documento', row.get('tipo_documento', 'Factura Electrónica')))
        cufe = str(row.get('cufe/cude', row.get('CUFE', row.get('cufe', ''))))
        forma_pago = str(row.get('forma pago', row.get('forma_pago', 'Crédito')))
        
        registros.append({
            'nit_emisor': nit,
            'razon_social': razon_social,
            'fecha_emision': fecha,
            'prefijo': prefijo,
            'folio': folio,
            'valor': valor,
            'tipo_documento': tipo_doc,
            'cufe': cufe,
            'forma_pago': forma_pago,
            'estado_aprobacion': 'Pendiente',
            'modulo': '',
            'estado_contable': 'No Registrada',
            'acuses_recibidos': 0
        })
    
    print(f"   ✅ {len(registros):,} registros preparados")
    
    # 4. INSERTAR EN POSTGRESQL CON COPY FROM
    print("\n3️⃣ Insertando en PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # Crear tabla temporal
    cursor.execute("""
        CREATE TEMP TABLE temp_carga (
            nit_emisor VARCHAR(20),
            razon_social VARCHAR(255),
            fecha_emision DATE,
            prefijo VARCHAR(10),
            folio VARCHAR(20),
            valor NUMERIC(15,2),
            tipo_documento VARCHAR(50),
            cufe VARCHAR(255),
            forma_pago VARCHAR(20),
            estado_aprobacion VARCHAR(50),
            modulo VARCHAR(50),
            estado_contable VARCHAR(50),
            acuses_recibidos INTEGER
        );
    """)
    
    # Preparar buffer para COPY FROM
    buffer = io.StringIO()
    for reg in registros:
        buffer.write(f"{reg['nit_emisor']}\t{reg['razon_social']}\t{reg['fecha_emision']}\t")
        buffer.write(f"{reg['prefijo']}\t{reg['folio']}\t{reg['valor']}\t{reg['tipo_documento']}\t")
        buffer.write(f"{reg['cufe']}\t{reg['forma_pago']}\t{reg['estado_aprobacion']}\t")
        buffer.write(f"{reg['modulo']}\t{reg['estado_contable']}\t{reg['acuses_recibidos']}\n")
    
    buffer.seek(0)
    
    # COPY FROM ultra rápido
    cursor.copy_from(
        buffer,
        'temp_carga',
        sep='\t',
        null='',
        columns=(
            'nit_emisor', 'razon_social', 'fecha_emision', 'prefijo', 'folio',
            'valor', 'tipo_documento', 'cufe', 'forma_pago', 'estado_aprobacion',
            'modulo', 'estado_contable', 'acuses_recibidos'
        )
    )
    
    print(f"   ✅ {len(registros):,} registros cargados en tabla temporal")
    
    # 5. INSERTAR EN MAESTRO (sin ON CONFLICT)
    print("\n4️⃣ Insertando en maestro_dian_vs_erp...")
    cursor.execute("""
        INSERT INTO maestro_dian_vs_erp (
            nit_emisor, razon_social, fecha_emision, prefijo, folio,
            valor, tipo_documento, cufe, forma_pago, estado_aprobacion,
            modulo, estado_contable, acuses_recibidos
        )
        SELECT 
            nit_emisor, razon_social, fecha_emision, prefijo, folio,
            valor, tipo_documento, cufe, forma_pago, estado_aprobacion,
            modulo, estado_contable, acuses_recibidos
        FROM temp_carga;
    """)
    
    total = cursor.rowcount
    conn.commit()
    
    print(f"   ✅ {total:,} registros insertados en maestro")
    
    # 6. LIMPIAR DUPLICADOS
    print("\n5️⃣ Limpiando duplicados...")
    cursor.execute("""
        DELETE FROM maestro_dian_vs_erp a 
        USING maestro_dian_vs_erp b
        WHERE a.id < b.id
          AND a.nit_emisor = b.nit_emisor
          AND a.prefijo = b.prefijo
          AND a.folio = b.folio;
    """)
    
    duplicados = cursor.rowcount
    conn.commit()
    print(f"   ✅ {duplicados:,} duplicados eliminados")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ CARGA COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    print(f"\nRegistros procesados: {total:,}")
    print(f"Duplicados eliminados: {duplicados:,}")
    print(f"Registros netos: {total - duplicados:,}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("USO: python CARGA_DIRECTA_SIMPLE.py ruta_archivo.xlsx")
        sys.exit(1)
    
    archivo = sys.argv[1]
    if not os.path.exists(archivo):
        print(f"❌ Archivo no existe: {archivo}")
        sys.exit(1)
    
    procesar_archivo_dian(archivo)
