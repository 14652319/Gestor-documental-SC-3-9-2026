"""Script para limpiar TODAS las tablas intermedias de DIAN vs ERP"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Conectar a la base de datos
engine = create_engine(DATABASE_URL)

print("="*80)
print("🗑️  LIMPIANDO TODAS LAS TABLAS INTERMEDIAS")
print("="*80)

tablas_a_limpiar = [
    'dian',
    'erp_comercial', 
    'erp_financiero',
    'acuses',
    'maestro_dian_vs_erp'
]

total_eliminados = 0

with engine.connect() as conn:
    for tabla in tablas_a_limpiar:
        try:
            # Contar registros antes
            result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
            count_antes = result.scalar()
            
            print(f"\n📊 {tabla}: {count_antes:,} registros")
            
            if count_antes > 0:
                # Eliminar todos los registros
                conn.execute(text(f"DELETE FROM {tabla}"))
                conn.commit()
                
                # Verificar después
                result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                count_despues = result.scalar()
                
                eliminados = count_antes - count_despues
                total_eliminados += eliminados
                
                print(f"   ✅ Eliminados: {eliminados:,} registros")
                print(f"   📊 Quedan: {count_despues:,} registros")
            else:
                print(f"   ⚪ Ya está vacía")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)[:60]}...")

print("\n" + "="*80)
print(f"🎯 TOTAL ELIMINADOS: {total_eliminados:,} registros")
print("="*80)
print("\n✅ Ahora puedes cargar los archivos nuevos con prefijos correctos")
print("   - Dian.xlsx")
print("   - ERP_comercial_23022026.xlsx")
print("   - erp_financiero_23022026.xlsx")
print("   - acuses_23022026.xlsx")
print("\n🚀 Ve a: http://127.0.0.1:8099/dian_vs_erp/sincronizar")
print("="*80)
