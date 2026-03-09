"""Test rápido de cargador_bd.py con archivos existentes."""
from dotenv import load_dotenv; load_dotenv()
import os, sys, time
sys.path.insert(0, '.')

from modules.dian_vs_erp.cargador_bd import (
    cargar_dian, cargar_erp, cargar_acuses, reconstruir_maestro
)

db_url = os.environ['DATABASE_URL']
print("=" * 60)
print("TEST CARGADOR_BD.PY")
print("=" * 60)

t_total = time.time()

# ── Test 1: Cargar DIAN ─────────────────────────────────────
print("\n[1/4] Cargar DIAN...")
r1 = cargar_dian('uploads/dian/Dian_23022026.xlsx', db_url, truncar=True)
print(f"   Resultado: {r1}")

# ── Test 2: Cargar ERP Comercial ────────────────────────────
print("\n[2/4] Cargar ERP Comercial...")
r2 = cargar_erp('uploads/erp_cm/ERP_comercial_23022026.xlsx', 'erp_comercial', db_url, truncar=True)
print(f"   Resultado: {r2}")

# ── Test 3: Cargar ERP Financiero ───────────────────────────
print("\n[3/4] Cargar ERP Financiero...")
r3 = cargar_erp('uploads/erp_fn/erp_financiero_23022026.xlsx', 'erp_financiero', db_url, truncar=True)
print(f"   Resultado: {r3}")

# ── Test 4: Reconstruir Maestro ─────────────────────────────
print("\n[4/4] Reconstruir maestro...")
r4 = reconstruir_maestro(db_url)
print(f"   Resultado: registros={r4['registros']:,}, tiempo={r4['tiempo']:.1f}s")

print(f"\n{'='*60}")
print(f"✅ TODAS LAS PRUEBAS COMPLETADAS EN {time.time()-t_total:.1f}s")
print(f"{'='*60}")
