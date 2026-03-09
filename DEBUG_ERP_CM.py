"""Debug rápido solo ERP Comercial"""
from dotenv import load_dotenv; load_dotenv()
import os, sys
sys.path.insert(0, '.')

from modules.dian_vs_erp.cargador_bd import cargar_erp

db_url = os.environ['DATABASE_URL']

try:
    r = cargar_erp(
        'uploads/erp_cm/ERP_comercial_23022026.xlsx',
        'erp_comercial',
        db_url,
        truncar=True
    )
    print(f"\nRESULTADO: {r}")
except Exception as e:
    import traceback
    print(f"\nERROR: {e}")
    traceback.print_exc()
