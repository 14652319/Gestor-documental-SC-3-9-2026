"""
Script para cargar SOLO archivo DIAN (sin ERP, sin acuses) - TEST RÁPIDO
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Flask
os.environ['FLASK_ENV'] = 'development'

from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp
from datetime import datetime, date
import polars as pl

def read_csv(path: str) -> pl.DataFrame:
    """Leer CSV y normalizar columnas a minúsculas"""
    def norm_cols(df: pl.DataFrame) -> pl.DataFrame:
        return df.rename({c: c.strip().lower() for c in df.columns})
    return norm_cols(pl.read_csv(path, infer_schema_length=0, truncate_ragged_lines=True))

def extraer_nit(valor: str) -> str:
    """Extraer solo números del NIT"""
    return ''.join(c for c in str(valor) if c.isdigit())

def main():
    with app.app_context():
        print("=" * 80)
        print("🔄 CARGANDO ARCHIVO DIAN CON FIX DE FECHA (día-mes-año)")
        print("=" * 80)
        
        csv_path = "uploads/dian/Dian_bc63e290ca.csv"
        
        if not os.path.exists(csv_path):
            print(f"\n❌ Archivo no encontrado: {csv_path}")
            return
        
        print(f"\n📂 Archivo: {csv_path}")
        print("⚙️  Leyendo CSV con Polars...")
        
        try:
            # Leer con Polars (normaliza columnas a minúsculas)
            df = read_csv(csv_path)
            print(f"✅ {df.height:,} filas leídas")
            print(f"📋 Columnas: {', '.join(df.columns[:10])}...")
            
            # Convertir a Pandas para iterar
            df_pd = df.to_pandas()
            
            # Limpiar tabla primero
            print("\n🗑️  Limpiando tabla maestro_dian_vs_erp...")
            MaestroDianVsErp.query.delete()
            db.session.commit()
            print("✅ Tabla limpia")
            
            # Procesar registros
            print("\n📝 Procesando registros...")
            registros = []
            errores = 0
            fechas_2026 = 0
            
            for idx, row in df_pd.iterrows():
                try:
                    # NIT Emisor
                    nit = extraer_nit(row.get('nit emisor', row.get('nit_emisor', '')))
                    
                    # Razón Social
                    razon_social = str(row.get('nombre emisor', row.get('razon_social', ''))).strip()
                    
                    # ✅ FECHA con múltiples variantes
                    fecha_raw = row.get('fecha emisión', row.get('fecha emisiã³n', row.get('fecha emision', row.get('fecha_emision', date.today()))))
                    
                    if isinstance(fecha_raw, str):
                        try:
                            if '-' in fecha_raw:
                                partes = fecha_raw.split('-')
                                if len(partes[0]) == 4:  # año-mes-día (2026-02-14)
                                    fecha_emision = datetime.strptime(fecha_raw, '%Y-%m-%d').date()
                                else:  # día-mes-año (14-02-2026)
                                    fecha_emision = datetime.strptime(fecha_raw, '%d-%m-%Y').date()
                            else:
                                fecha_emision = date.today()
                        except:
                            fecha_emision = date.today()
                    else:
                        fecha_emision = fecha_raw if isinstance(fecha_raw, date) else date.today()
                    
                    # Contar fechas de 2026
                    if fecha_emision.year == 2026:
                        fechas_2026 += 1
                    
                    # Prefijo
                    prefijo = str(row.get('prefijo', ''))[:10]
                    
                    # Folio
                    folio = str(row.get('folio', row.get('numero', '')))[:20]
                    
                    # Valor (buscar 'total' primero, luego 'valor')
                    valor_raw = row.get('total', row.get('valor', 0))
                    try:
                        valor = float(valor_raw) if valor_raw and str(valor_raw).strip() != '' else 0.0
                    except:
                        valor = 0.0
                    
                    # Tipo documento
                    tipo_doc = str(row.get('tipo documento', row.get('tipo_documento', 'Factura Electrónica')))
                    
                    # CUFE
                    cufe = str(row.get('cufe/cude', row.get('cufe', '')))[:255]
                    
                    # Forma de pago
                    forma_pago = str(row.get('forma de pago', row.get('forma_pago', '2'))).strip()
                    
                    # Crear registro
                    registro = MaestroDianVsErp(
                        nit_emisor=nit,
                        razon_social=razon_social,
                        fecha_emision=fecha_emision,
                        prefijo=prefijo,
                        folio=folio,
                        valor=valor,
                        tipo_documento=tipo_doc,
                        cufe=cufe,
                        forma_pago=forma_pago,
                        modulo='',
                        doc_causado_por='',
                        estado_contable='No Registrada',
                        tipo_tercero=''
                    )
                    
                    registros.append(registro)
                    
                    # Mostrar progreso cada 10,000
                    if len(registros) % 10000 == 0:
                        print(f"  ... {len(registros):,} registros procesados")
                    
                except Exception as e:
                    errores += 1
                    if errores <= 5:
                        print(f"  ⚠️  Error en fila {idx}: {e}")
            
            print(f"\n✅ {len(registros):,} registros preparados ({errores} errores)")
            print(f"📅 Fechas de 2026: {fechas_2026:,} ({fechas_2026/len(registros)*100:.1f}%)")
            
            # Guardar en bulk
            print("\n💾 Guardando en base de datos...")
            inicio = datetime.now()
            
            db.session.bulk_save_objects(registros)
            db.session.commit()
            
            fin = datetime.now()
            duracion = (fin - inicio).total_seconds()
            
            print(f"✅ Guardado en {duracion:.1f}s ({len(registros)/duracion:.0f} registros/segundo)")
            
            # Verificar
            total_bd = MaestroDianVsErp.query.count()
            print(f"\n📊 Total en BD: {total_bd:,}")
            
            # Mostrar primeras fechas
            primeras = MaestroDianVsErp.query.order_by(MaestroDianVsErp.id).limit(10).all()
            print("\n📅 PRIMERAS 10 FECHAS EN BD:")
            for f in primeras:
                print(f"  {f.nit_emisor} | {f.prefijo}-{f.folio} | {f.fecha_emision} | ${f.valor:,.0f}")
            
            print("\n" + "=" * 80)
            print("✅✅✅ CARGA COMPLETADA ✅✅✅")
            print("=" * 80)
            print("\n🔍 AHORA VERIFICA EN EL VISOR:")
            print("   → http://127.0.0.1:8099/dian_vs_erp/visor_v2")
            print("\n⚠️  IMPORTANTE: Haz HARD REFRESH en el navegador:")
            print("   → Ctrl + Shift + R (Chrome/Edge)")
            print("   → Ctrl + F5 (Firefox)")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPresiona ENTER para salir...")
