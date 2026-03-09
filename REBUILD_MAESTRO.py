"""Reconstruye el maestro_dian_vs_erp desde las tablas existentes."""
import sys, os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, '.')

from modules.dian_vs_erp.cargador_bd import reconstruir_maestro

print("=" * 60)
print("RECONSTRUYENDO maestro_dian_vs_erp")
print("=" * 60)
r = reconstruir_maestro(os.environ['DATABASE_URL'])
print("RESULTADO:", r)
