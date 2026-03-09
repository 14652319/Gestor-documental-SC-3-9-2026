"""Debug: ver primeras claves calculadas del ERP Comercial."""
import sys, os
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from dotenv import load_dotenv; load_dotenv()
sys.path.insert(0, '.')

import pandas as pd
import re
from pathlib import Path

# ---------- Funciones helper (copiadas de cargador_bd) ----------
def _extraer_folio(s: str) -> str:
    s = str(s).strip()
    nums = re.sub(r'[^0-9]', '', s)
    return nums

def _ultimos_8_sin_ceros(s: str) -> str:
    return s[-8:].lstrip('0') or s[-1:] or ''

def _safe_str(v) -> str:
    if v is None or (isinstance(v, float) and str(v) == 'nan'):
        return ''
    return str(v).strip()

# ---------- Leer Excel ----------
ruta = 'uploads/erp_cm/ERP_comercial_23022026.xlsx'
df = pd.read_excel(ruta, engine='openpyxl', dtype=str)
print(f"Total filas: {len(df):,}")
print(f"Columnas: {df.columns.tolist()}")

proveedor_col = 'Proveedor'
docto_col     = 'Docto. proveedor'

registros = []
claves = []
for _, row in df.iterrows():
    nit = _safe_str(row.get(proveedor_col, ''))
    if not nit:
        continue
    docto_proveedor = _safe_str(row.get(docto_col, ''))
    if '-' in docto_proveedor:
        partes = docto_proveedor.split('-', 1)
        prefijo   = partes[0].strip()
        folio_raw = partes[1].strip()
    else:
        prefijo   = ''
        folio_raw = docto_proveedor
    folio   = _ultimos_8_sin_ceros(_extraer_folio(folio_raw))
    nit_solo = _extraer_folio(nit)
    clave_erp = f"{nit_solo}{prefijo}{folio}"
    claves.append(clave_erp)
    registros.append((nit, docto_proveedor, clave_erp))

print(f"\nTotal procesados: {len(claves):,}")

# Encontrar duplicados REALES en las claves calculadas
from collections import Counter
cnt = Counter(claves)
dups = {k: v for k, v in cnt.items() if v > 1}
print(f"Claves duplicadas: {len(dups):,}")
if dups:
    print("Primeras 5 duplicadas:")
    for k, v in list(dups.items())[:5]:
        print(f"  clave={k!r} aparece {v} veces")
        # Mostrar las filas
        idxs = [i for i, c in enumerate(claves) if c == k]
        for i in idxs[:3]:
            print(f"    {registros[i]}")

# Deduplicar
_dedup = {}
for r in registros:
    _dedup[r[2]] = r
print(f"\nDespués de dedup: {len(_dedup):,}")

# Verificar: ¿hay claves vacías?
empty = sum(1 for k in _dedup if not k)
print(f"Claves vacías/None: {empty}")
