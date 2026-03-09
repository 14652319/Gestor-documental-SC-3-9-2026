"""
CARGAR_CSV_SQLALCHEMY.py
========================
Usa SQLAlchemy en lugar de psycopg2 para evitar errores de encoding
"""

import polars as pl
from pathlib import Path
from datetime import datetime
import sys

# Agregar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar sin cargar .env
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:Vimer2024*@localhost:5432/gestor_documental'

print("="*80)
print("🚀 CARGAR CSV CON SQLAlchemy")
print("="*80)
print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

try:
    from app import app, db
    from modules.dian_vs_erp.models import MaestroDianVsErp  # ✅ FIX: Nombre correcto
    
    with app.app_context():
        # PASO 1: Limpiar tabla
        print("\n🗑️  PASO 1: LIMPIAR TABLA")
        count_antes = db.session.query(MaestroDianVsErp).count()
        print(f"Registros antes: {count_antes:,}")
        
        db.session.query(MaestroDianVsErp).delete()
        db.session.commit()
        print("✅ Tabla limpiada")
        
        # PASO 2: Cargar CSV
        print("\n📂 PASO 2: CARGAR CSV")
        csv_path = Path("uploads/dian/Desde_01-01-2025_Hasta_28-02-2025_ea77100881.csv")
        
        if not csv_path.exists():
            print(f"❌ No se encontró: {csv_path}")
            exit(1)
        
        print(f"✅ Archivo: {csv_path.name}")
        
        # Leer con Polars
        print("\n🔄 Leyendo CSV...")
        df = pl.read_csv(
            str(csv_path),
            infer_schema_length=0,
            ignore_errors=True,
            null_values=["", " "]
        )
        
        # Normalizar columnas
        df = df.rename({c: c.strip().lower() for c in df.columns})
        print(f"✅ {df.height:,} registros leídos")
        
        # Convertir a Pandas
        df_pd = df.to_pandas()
        
        # PASO 3: Procesar e insertar
        print("\n⚙️  PASO 3: PROCESAR E INSERTAR")
        
        batch_size = 5000
        total = len(df_pd)
        
        for i in range(0, total, batch_size):
            batch = df_pd.iloc[i:i+batch_size]
            registros = []
            
            for _, row in batch.iterrows():
                # Extraer fecha
                fecha_raw = None
                for col in ['fecha emisión', 'fecha emision', 'fecha_emision']:
                    if col in row.index:
                        val = row[col]
                        if val and str(val).strip() and str(val) != 'nan':
                            fecha_raw = str(val).strip()
                            break
                
                # Parsear fecha
                fecha_emision = None
                if fecha_raw:
                    try:
                        fecha_emision = datetime.strptime(fecha_raw, '%d-%m-%Y').date()
                    except:
                        try:
                            fecha_emision = datetime.strptime(fecha_raw, '%Y-%m-%d').date()
                        except:
                            pass
                
                # Crear registro
                registro = MaestroDianVsErp(
                    nit_emisor=str(row.get('nit emisor', '')).strip(),
                    razon_social=str(row.get('nombre emisor', '')).strip(),
                    fecha_emision=fecha_emision,
                    prefijo=str(row.get('prefijo', '')).strip(),
                    folio=str(row.get('folio', '')).strip(),
                    valor=0.0,
                    forma_pago='',
                    estado_contable='No Registrada',
                    fecha_registro=datetime.now()
                )
                
                registros.append(registro)
            
            # Insertar batch
            db.session.bulk_save_objects(registros)
            db.session.commit()
            
            print(f"   Insertados: {i + len(batch):,}/{total:,}")
        
        # VERIFICAR
        print("\n📊 VERIFICACIÓN")
        count_final = db.session.query(MaestroDianVsErp).count()
        print(f"Total registros: {count_final:,}")
        
        # Mostrar fechas
        result = db.session.execute("""
            SELECT fecha_emision, COUNT(*) as cantidad
            FROM maestro_dian_vs_erp
            WHERE fecha_emision IS NOT NULL
            GROUP BY fecha_emision
            ORDER BY cantidad DESC
            LIMIT 5
        """)
        
        print(f"\n📅 Fechas más comunes:")
        for row in result:
            print(f"   {row[0]}: {row[1]:,} registros")
        
        print("\n" + "="*80)
        print("✅ ¡COMPLETADO!")
        print("="*80)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
