"""
Script para cargar TODOS los archivos CSV: 2025 + 2026
Con fix de formato de fecha día-mes-año aplicado
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
import glob

def read_csv_safe(path: str) -> pl.DataFrame:
    """Leer CSV y normalizar columnas a minúsculas"""
    try:
        df = pl.read_csv(path, infer_schema_length=0, truncate_ragged_lines=True, ignore_errors=True)
        # Normalizar columnas
        df = df.rename({c: c.strip().lower() for c in df.columns})
        return df
    except Exception as e:
        print(f"⚠️  Error leyendo {os.path.basename(path)}: {e}")
        return None

def extraer_nit(valor: str) -> str:
    """Extraer solo números del NIT"""
    return ''.join(c for c in str(valor) if c.isdigit())

def procesar_archivo(csv_path: str) -> list:
    """Procesar un archivo CSV y retornar lista de registros"""
    print(f"\n📂 Procesando: {os.path.basename(csv_path)}")
    
    df = read_csv_safe(csv_path)
    if df is None or df.height == 0:
        print(f"   ⚠️  Archivo vacío o con errores")
        return []
    
    print(f"   ✅ {df.height:,} filas leídas")
    
    # Convertir a Pandas
    df_pd = df.to_pandas()
    
    registros = []
    errores = 0
    fechas_2025 = 0
    fechas_2026 = 0
    
    for idx, row in df_pd.iterrows():
        try:
            # NIT Emisor
            nit = extraer_nit(row.get('nit emisor', row.get('nit_emisor', '')))
            if not nit:
                continue
            
            # Razón Social
            razon_social = str(row.get('nombre emisor', row.get('razon_social', ''))).strip()
            
            # ✅ FECHA con múltiples variantes
            fecha_raw = row.get('fecha emisión', row.get('fecha emisiã³n', row.get('fecha emision', row.get('fecha_emision', None))))
            
            if fecha_raw is None:
                errores += 1
                continue
            
            if isinstance(fecha_raw, str):
                try:
                    if '-' in fecha_raw:
                        partes = fecha_raw.split('-')
                        if len(partes) != 3:
                            fecha_emision = date.today()
                        elif len(partes[0]) == 4:  # año-mes-día (2026-02-14)
                            fecha_emision = datetime.strptime(fecha_raw, '%Y-%m-%d').date()
                        else:  # día-mes-año (14-02-2026)
                            fecha_emision = datetime.strptime(fecha_raw, '%d-%m-%Y').date()
                    else:
                        fecha_emision = date.today()
                except Exception as e:
                    fecha_emision = date.today()
            else:
                fecha_emision = fecha_raw if isinstance(fecha_raw, date) else date.today()
            
            # Contar por año
            if fecha_emision.year == 2025:
                fechas_2025 += 1
            elif fecha_emision.year == 2026:
                fechas_2026 += 1
            
            # Prefijo y Folio
            prefijo = str(row.get('prefijo', ''))[:10]
            folio = str(row.get('folio', row.get('numero', '')))[:20]
            
            # Valor (buscar 'total' primero, luego 'valor')
            valor_raw = row.get('total', row.get('valor', 0))
            try:
                valor = float(valor_raw) if valor_raw and str(valor_raw).strip() != '' else 0.0
            except:
                valor = 0.0
            
            # Tipo documento
            tipo_doc = str(row.get('tipo documento', row.get('tipo_documento', 'Factura Electrónica')))[:50]
            
            # CUFE
            cufe = str(row.get('cufe/cude', row.get('cufe', '')))[:255]
            
            # Forma de pago
            forma_pago = str(row.get('forma de pago', row.get('forma_pago', '2'))).strip()
            
            # Crear registro
            registro = MaestroDianVsErp(
                nit_emisor=nit,
                razon_social=razon_social[:255],
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
            
        except Exception as e:
            errores += 1
            if errores <= 3:
                print(f"      ⚠️  Error en fila {idx}: {e}")
    
    print(f"   ✅ {len(registros):,} registros válidos")
    print(f"      📅 2025: {fechas_2025:,} | 2026: {fechas_2026:,}")
    if errores > 0:
        print(f"      ⚠️  Errores: {errores}")
    
    return registros

def main():
    with app.app_context():
        print("=" * 80)
        print("🔄 CARGANDO ARCHIVOS CSV: 2025 + 2026")
        print("=" * 80)
        
        # 1. Limpiar tabla
        print("\n🗑️  Limpiando tabla maestro_dian_vs_erp...")
        MaestroDianVsErp.query.delete()
        db.session.commit()
        print("✅ Tabla limpia")
        
        # 2. Buscar todos los archivos CSV del 2025 y 2026
        archivos_2025 = [
            "uploads/dian/Desde_01-01-2025_Hasta_28-02-2025_ea77100881.csv",
            "uploads/dian/Desde_01-03-2025_Hasta_30-04-2025_53bf281ec5.csv",
            "uploads/dian/Desde_01-05-2025_Hasta_30-06-2025_ab312e9218.csv",
            "uploads/dian/Desde_01-07-2025_Hasta_31-08-2025_f06a5e7a3f.csv",
            "uploads/dian/Desde_01-09-2025_Hasta_31-10-2025_5f86a676d9.csv",
            "uploads/dian/Desde_01-11-2025_Hasta_29-12-2025_89e7a97a2d.csv",
            "uploads/dian/DIAN_Desde_01-12-2025_Hasta_18-12-2025_e13a2d984a.csv"
        ]
        
        archivo_2026 = "uploads/dian/Dian_bc63e290ca.csv"
        
        # Verificar archivos existentes
        archivos_validos = []
        print("\n📋 Verificando archivos...")
        for archivo in archivos_2025:
            if os.path.exists(archivo):
                archivos_validos.append(archivo)
                print(f"   ✅ {os.path.basename(archivo)}")
            else:
                print(f"   ⚠️  No existe: {os.path.basename(archivo)}")
        
        if os.path.exists(archivo_2026):
            archivos_validos.append(archivo_2026)
            print(f"   ✅ {os.path.basename(archivo_2026)}")
        else:
            print(f"   ⚠️  No existe: {os.path.basename(archivo_2026)}")
        
        if not archivos_validos:
            print("\n❌ No se encontraron archivos CSV para cargar")
            return
        
        print(f"\n📊 Total archivos a procesar: {len(archivos_validos)}")
        
        # 3. Procesar todos los archivos
        todos_registros = []
        
        for archivo in archivos_validos:
            registros = procesar_archivo(archivo)
            todos_registros.extend(registros)
        
        if not todos_registros:
            print("\n❌ No se generaron registros válidos")
            return
        
        print("\n" + "=" * 80)
        print(f"📊 TOTAL REGISTROS PREPARADOS: {len(todos_registros):,}")
        print("=" * 80)
        
        # Contar por año
        total_2025 = sum(1 for r in todos_registros if r.fecha_emision.year == 2025)
        total_2026 = sum(1 for r in todos_registros if r.fecha_emision.year == 2026)
        
        print(f"\n📅 Por año:")
        print(f"   • 2025: {total_2025:,} registros")
        print(f"   • 2026: {total_2026:,} registros")
        
        # 4. Guardar en bulk
        print(f"\n💾 Guardando en base de datos...")
        inicio = datetime.now()
        
        # Insertar en lotes de 10,000
        batch_size = 10000
        for i in range(0, len(todos_registros), batch_size):
            batch = todos_registros[i:i + batch_size]
            db.session.bulk_save_objects(batch)
            db.session.commit()
            print(f"   ... {min(i + batch_size, len(todos_registros)):,} / {len(todos_registros):,} guardados")
        
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        print(f"\n✅ Guardado en {duracion:.1f}s ({len(todos_registros)/duracion:.0f} registros/segundo)")
        
        # 5. Verificar
        total_bd = MaestroDianVsErp.query.count()
        print(f"\n📊 Total en BD: {total_bd:,}")
        
        # Verificar distribución de fechas
        from sqlalchemy import func, extract
        
        bd_2025 = MaestroDianVsErp.query.filter(
            extract('year', MaestroDianVsErp.fecha_emision) == 2025
        ).count()
        
        bd_2026 = MaestroDianVsErp.query.filter(
            extract('year', MaestroDianVsErp.fecha_emision) == 2026
        ).count()
        
        print(f"\n📅 Verificación por año en BD:")
        print(f"   • 2025: {bd_2025:,} registros")
        print(f"   • 2026: {bd_2026:,} registros")
        
        # Mostrar primeras fechas
        print(f"\n📅 PRIMERAS 10 FECHAS EN BD:")
        primeras = MaestroDianVsErp.query.order_by(MaestroDianVsErp.id).limit(10).all()
        for f in primeras:
            print(f"   {f.nit_emisor} | {f.prefijo}-{f.folio} | {f.fecha_emision} | ${f.valor:,.0f}")
        
        print("\n" + "=" * 80)
        print("✅✅✅ CARGA COMPLETADA ✅✅✅")
        print("=" * 80)
        print("\n🔍 AHORA VERIFICA EN EL VISOR:")
        print("   → http://127.0.0.1:8099/dian_vs_erp/visor_v2")
        print("\n⚠️  IMPORTANTE: Haz HARD REFRESH en el navegador:")
        print("   → Ctrl + Shift + R (Chrome/Edge)")
        print("   → Ctrl + F5 (Firefox)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPresiona ENTER para salir...")
