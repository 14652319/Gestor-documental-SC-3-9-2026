"""Restaura erp_comercial y reconstruye maestro."""
import sys, os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, '.')

from modules.dian_vs_erp.cargador_bd import cargar_erp, reconstruir_maestro

print("=" * 60)
print("PASO 1: RESTAURAR erp_comercial")
print("=" * 60)
r1 = cargar_erp(
    'uploads/erp_cm/ERP_comercial_23022026.xlsx',
    'erp_comercial',
    os.environ['DATABASE_URL']
)
print("RESULTADO ERP_CM:", r1)

print()
print("=" * 60)
print("PASO 2: RECONSTRUIR MAESTRO")
print("=" * 60)
r2 = reconstruir_maestro(os.environ['DATABASE_URL'])
print("RESULTADO MAESTRO:", r2)
