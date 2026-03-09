"""
cargador_bd.py
==============
Funciones para cargar archivos Excel/CSV a sus tablas PostgreSQL
correspondientes y reconstruir maestro_dian_vs_erp.

Uso desde subir_archivos() en routes.py:
    from .cargador_bd import cargar_dian, cargar_erp, cargar_acuses, reconstruir_maestro
"""

import os
import io
import re
import sys
import time
from pathlib import Path

# Asegurar stdout/stderr en UTF-8 (evita UnicodeEncodeError en Windows con cp1252)
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass
from datetime import date, datetime
from unicodedata import normalize

import pandas as pd
import psycopg2

# ─────────────────────────────────────────────────────────────────
# Constantes
# ─────────────────────────────────────────────────────────────────

TIPOS_EXCLUIDOS_DIAN = {
    'tipo de documento',
    'application response',
    'documento soporte con no obligados',
    'nota de ajuste del documento soporte',
}

FORMA_PAGO_MAP = {
    '1': 'Contado', '1.0': 'Contado',
    '2': 'Crédito', '2.0': 'Crédito',
}

SIGLAS = {
    "factura electrónica": "FE",
    "factura electronica": "FE",
    "factura electrónica de exportación": "FEE",
    "nota de débito electrónica": "NDE",
    "nota de debito electronica": "NDE",
    "factura electrónica de contingencia": "FEC",
    "documento soporte con no obligados": "DSNO",
    "factura electrónica de contingencia dian": "FECD",
    "documento equivalente pos": "DEPOS",
    "nota de ajuste crédito del documento equivalente": "NCDE",
    "nota de crédito electrónica": "NCE",
    "nota de credito electronica": "NCE",
    "documento equivalente - cobro de peajes": "DECPE",
    "documento equivalente - servicios públicos domiciliarios": "DESPD",
}

JERARQUIA_ACUSES = {
    'Pendiente': 1, 'Acuse Recibido': 2, 'Acuse Bien/Servicio': 3,
    'Rechazada': 4, 'Aceptación Expresa': 5, 'Aceptación Tácita': 6,
}


# ─────────────────────────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────────────────────────

def _normalizar_col(nombre):
    nombre = str(nombre).strip()
    nombre = normalize('NFD', nombre)
    nombre = ''.join(c for c in nombre if c.isalnum() or c in ' _-')
    nombre = nombre.lower().replace(' ', '_').replace('-', '_')
    nombre = re.sub(r'_+', '_', nombre)
    return nombre.rstrip('_').rstrip('.')


def _safe_str(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ''
    return str(val).strip()


def _safe_date(val):
    if val is None:
        return None
    try:
        if isinstance(val, float) and pd.isna(val):
            return None
    except Exception:
        pass
    try:
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val
        return pd.to_datetime(val, errors='coerce').date()
    except Exception:
        return None


def _safe_float(val):
    if val is None:
        return 0.0
    try:
        if isinstance(val, float) and pd.isna(val):
            return 0.0
    except Exception:
        pass
    try:
        return float(str(val).replace(',', '.'))
    except Exception:
        return 0.0


def _fmt(val):
    """Convierte valor a string TSV-safe para COPY FROM."""
    if val is None:
        return ''
    try:
        if isinstance(val, float) and val != val:   # NaN
            return ''
    except Exception:
        pass
    if isinstance(val, bool):
        return 't' if val else 'f'
    s = str(val).strip()
    return s.replace('\\', '\\\\').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')


def _mapear_forma_pago(val):
    s = _safe_str(val)
    # Quitar sufijo .0 si es decimal
    s_clean = s.rstrip('0').rstrip('.') if '.' in s else s
    return FORMA_PAGO_MAP.get(s, FORMA_PAGO_MAP.get(s_clean, s))


def _extraer_prefijo(docto):
    if not docto:
        return ''
    p = re.sub(r'[\-\.\s]', '', str(docto)).strip().upper()
    if len(p) > 20:
        if re.match(r'^[A-F0-9]{20,}$', p):   # probablemente CUFE
            return ''
        return p[:20]
    return p


def _extraer_folio(docto):
    if not docto:
        return ''
    return re.sub(r'[^0-9]', '', str(docto))


def _ultimos_8_sin_ceros(folio):
    nums = re.sub(r'[^0-9]', '', str(folio))
    if not nums:
        return '0'
    part = nums[-8:] if len(nums) >= 8 else nums
    return part.lstrip('0') or '0'


def _crear_clave(nit, prefijo, folio):
    return f"{_extraer_folio(str(nit))}{_extraer_prefijo(str(prefijo))}{_ultimos_8_sin_ceros(_extraer_folio(str(folio)))}"


def _jerarquia_aprobacion(estado):
    return JERARQUIA_ACUSES.get(str(estado).strip() if estado else 'Pendiente', 1)


def _acuses_recibidos(estado):
    contables = {
        'Acuse Bien/Servicio': 1,
        'Aceptación Expresa': 2,
        'Aceptación Tácita': 3,
    }
    return contables.get(str(estado).strip() if estado else '', 0)


# ═════════════════════════════════════════════════════════════════
# 1. CARGAR DIAN
# ═════════════════════════════════════════════════════════════════

def cargar_dian(ruta_excel: str, db_url: str, truncar: bool = True) -> dict:
    """
    Carga archivo Excel/CSV DIAN en tabla `dian`.
    - Filtra tipos de documento excluidos
    - Mapea forma_pago (1/2 → Contado/Crédito)
    - Si truncar=True: TRUNCATE + INSERT (reemplazo completo)
    - Si truncar=False: INSERT ON CONFLICT DO NOTHING (incremental)
    """
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"📥 CARGAR DIAN: {Path(ruta_excel).name}")
    print(f"{'='*60}")

    # Leer Excel
    df = pd.read_excel(ruta_excel, engine='openpyxl', dtype=str)
    total_leidos = len(df)
    print(f"   Leídas: {total_leidos:,} filas")

    df.columns = [_normalizar_col(c) for c in df.columns]
    cols = df.columns.tolist()

    # Detectar columnas clave por nombre normalizado
    def find(* kws, exclude=None):
        for c in cols:
            if all(k in c for k in kws):
                if exclude and any(x in c for x in exclude):
                    continue
                return c
        return None

    tipo_doc_col        = find('tipo', 'documento')
    cufe_col            = find('cufe') or find('cude')
    folio_col           = find('folio')
    prefijo_col         = find('prefijo')
    divisa_col          = find('divisa')
    forma_pago_col      = find('forma', 'pago')
    medio_pago_col      = find('medio', 'pago')
    fecha_emision_col   = find('fecha', 'emision') or find('fecha', 'generac') or find('fecha', 'factur')
    fecha_recepcion_col = find('fecha', 'recepcion')
    nit_emisor_col      = find('nit', 'emisor') or find('nit', 'proveedor') or find('nit', 'vendedor')
    nombre_emisor_col   = (find('nombre', 'emisor') or find('razon', 'emisor') or
                           find('nombre', 'proveedor') or find('razon', 'proveedor'))
    nit_receptor_col    = find('nit', 'receptor') or find('nit', 'adquir') or find('nit', 'comprador')
    nombre_receptor_col = (find('nombre', 'receptor') or find('razon', 'receptor') or
                           find('nombre', 'adquir') or find('razon', 'adquir'))
    iva_col       = 'iva'       if 'iva'  in cols else None
    ica_col       = 'ica'       if 'ica'  in cols else None
    ic_col        = 'ic'        if 'ic'   in cols else None
    inc_col       = 'inc'       if 'inc'  in cols else None
    timbre_col    = find('timbre')
    inc_bolsas_col= find('bolsa')
    in_carbono_col= find('carbono')
    in_combustibles_col = find('combustible')
    ic_datos_col  = find('datos')
    icl_col       = 'icl'   if 'icl'   in cols else None
    inpp_col      = 'inpp'  if 'inpp'  in cols else None
    ibua_col      = 'ibua'  if 'ibua'  in cols else None
    icui_col      = 'icui'  if 'icui'  in cols else None
    rete_iva_col  = find('rete', 'iva')
    rete_renta_col= find('rete', 'renta')
    rete_ica_col  = find('rete', 'ica')
    total_col     = 'total' if 'total' in cols else find('total', 'documento')
    estado_col    = 'estado' if 'estado' in cols else None
    grupo_col     = 'grupo'  if 'grupo'  in cols else None

    print(f"   tipo_doc={tipo_doc_col}, nit_emisor={nit_emisor_col}, total={total_col}")

    # Procesar registros
    registros = []
    omitidos = 0

    for _, row in df.iterrows():
        tipo_documento = _safe_str(row.get(tipo_doc_col, ''))
        if tipo_documento.lower() in TIPOS_EXCLUIDOS_DIAN or not tipo_documento:
            omitidos += 1
            continue

        nit_emisor = _safe_str(row.get(nit_emisor_col, ''))
        prefijo    = _safe_str(row.get(prefijo_col, ''))
        folio      = _safe_str(row.get(folio_col, ''))
        clave      = f"{nit_emisor}-{prefijo}-{folio}"

        registros.append((
            tipo_documento,
            _safe_str(row.get(cufe_col, '')),
            folio,
            prefijo,
            _safe_str(row.get(divisa_col, '')),
            _mapear_forma_pago(row.get(forma_pago_col, '')),
            _safe_str(row.get(medio_pago_col, '')),
            _safe_date(row.get(fecha_emision_col)),
            _safe_date(row.get(fecha_recepcion_col)),
            nit_emisor,
            _safe_str(row.get(nombre_emisor_col, ''))[:255],
            _safe_str(row.get(nit_receptor_col, '')),
            _safe_str(row.get(nombre_receptor_col, ''))[:255],
            _safe_float(row.get(iva_col, 0)),
            _safe_float(row.get(ica_col, 0)),
            _safe_float(row.get(ic_col, 0)),
            _safe_float(row.get(inc_col, 0)),
            _safe_float(row.get(timbre_col, 0)),
            _safe_float(row.get(inc_bolsas_col, 0)),
            _safe_float(row.get(in_carbono_col, 0)),
            _safe_float(row.get(in_combustibles_col, 0)),
            _safe_float(row.get(ic_datos_col, 0)),
            _safe_float(row.get(icl_col, 0)),
            _safe_float(row.get(inpp_col, 0)),
            _safe_float(row.get(ibua_col, 0)),
            _safe_float(row.get(icui_col, 0)),
            _safe_float(row.get(rete_iva_col, 0)),
            _safe_float(row.get(rete_renta_col, 0)),
            _safe_float(row.get(rete_ica_col, 0)),
            _safe_float(row.get(total_col, 0)),
            _safe_str(row.get(estado_col, '')),
            _safe_str(row.get(grupo_col, '')),
            clave,
        ))

    print(f"   Procesados: {len(registros):,}  |  Omitidos (excluidos): {omitidos:,}")

    # Insertar en PostgreSQL
    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        if truncar:
            cur.execute("TRUNCATE TABLE dian")
            print("   TRUNCATE dian (pendiente...)")

        cur.execute("CREATE TEMP TABLE _t_dian (LIKE dian INCLUDING DEFAULTS) ON COMMIT DROP")

        buf = io.StringIO()
        for r in registros:
            buf.write('\t'.join(_fmt(v) for v in r) + '\n')
        buf.seek(0)

        cols_db = (
            'tipo_documento', 'cufe_cude', 'folio', 'prefijo', 'divisa',
            'forma_pago', 'medio_pago', 'fecha_emision', 'fecha_recepcion',
            'nit_emisor', 'nombre_emisor', 'nit_receptor', 'nombre_receptor',
            'iva', 'ica', 'ic', 'inc', 'timbre', 'inc_bolsas', 'in_carbono',
            'in_combustibles', 'ic_datos', 'icl', 'inpp', 'ibua', 'icui',
            'rete_iva', 'rete_renta', 'rete_ica', 'total', 'estado', 'grupo', 'clave'
        )
        cur.copy_from(buf, '_t_dian', sep='\t', null='', columns=cols_db)

        if truncar:
            cur.execute("INSERT INTO dian SELECT * FROM _t_dian")
        else:
            cur.execute("INSERT INTO dian SELECT * FROM _t_dian ON CONFLICT (clave) DO NOTHING")

        insertados = cur.rowcount
        conn.commit()

        t = time.time() - t0
        msg = f"✅ DIAN: {insertados:,} insertados ({omitidos:,} tipos excluidos) en {t:.1f}s"
        print(f"   {msg}")
        return {"tabla": "dian", "insertados": insertados, "omitidos": omitidos,
                "total_leidos": total_leidos, "tiempo": t, "mensaje": msg}

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ═════════════════════════════════════════════════════════════════
# 2. CARGAR ERP (COMERCIAL o FINANCIERO)
# ═════════════════════════════════════════════════════════════════

def cargar_erp(ruta_excel: str, tabla: str, db_url: str, truncar: bool = True) -> dict:
    """
    Carga archivo Excel ERP en tabla `erp_comercial` o `erp_financiero`.
    Detecta columnas flexiblemente (Comercial y Financiero tienen nombres distintos).
    """
    assert tabla in ('erp_comercial', 'erp_financiero'), f"Tabla inválida: {tabla}"

    t0 = time.time()
    es_comercial = (tabla == 'erp_comercial')
    modulo_nombre = 'Comercial' if es_comercial else 'Financiero'
    clave_col_db  = 'clave_erp_comercial' if es_comercial else 'clave_erp_financiero'
    imptos_col_db = 'valor_imptos' if es_comercial else 'valor_impuestos'

    print(f"\n{'='*60}")
    print(f"📥 CARGAR ERP {modulo_nombre}: {Path(ruta_excel).name}")
    print(f"{'='*60}")

    df = pd.read_excel(ruta_excel, engine='openpyxl', dtype=str)
    total_leidos = len(df)
    print(f"   Leídas: {total_leidos:,} filas | Columnas: {df.columns.tolist()}")

    # Detección flexible de columnas (comparar en minúsculas)
    def find_col(*kws, exclude=None):
        for col in df.columns:
            cl = col.lower().strip()
            if all(k.lower() in cl for k in kws):
                if exclude and any(x.lower() in cl for x in exclude):
                    continue
                return col
        return None

    proveedor_col = find_col('proveedor', exclude=['razon', 'razón', 'social'])
    razon_col     = (find_col('razón', 'social') or find_col('razon', 'social') or
                     find_col('razon', 'proveedor') or find_col('razón', 'proveedor'))
    fecha_col     = (find_col('fecha', 'docto') or find_col('fecha', 'prov') or
                     find_col('fecha'))
    docto_col     = find_col('docto', 'prov', exclude=['fecha']) or find_col('docto.')
    valor_col     = (find_col('valor', 'bruto') or find_col('valor', 'subtotal') or
                     find_col('importe'))
    imptos_x_col  = find_col('valor', 'imptos') or find_col('valor', 'impuesto')
    co_col        = next((c for c in df.columns if c.strip().upper() == 'C.O.'), None)
    usuario_col   = find_col('usuario', 'cre')
    clase_col     = find_col('clase', 'docto') or find_col('clase', 'doc')
    nro_doc_col   = (find_col('nro', 'documento') or find_col('nro', 'doc') or
                     find_col('número', 'documento'))

    if not proveedor_col:
        raise ValueError(f"No se encontró columna 'Proveedor'. Columnas disponibles: {df.columns.tolist()}")
    if not docto_col:
        raise ValueError(f"No se encontró columna 'Docto. proveedor'. Columnas disponibles: {df.columns.tolist()}")

    print(f"   proveedor={proveedor_col}, docto={docto_col}, valor={valor_col}, co={co_col}")

    # Procesar registros
    registros = []
    omitidos = 0

    for _, row in df.iterrows():
        nit = _safe_str(row.get(proveedor_col, ''))
        if not nit:
            omitidos += 1
            continue

        razon_social    = _safe_str(row.get(razon_col, ''))[:255] if razon_col else ''
        fecha_recibido  = _safe_date(row.get(fecha_col)) if fecha_col else None
        docto_proveedor = _safe_str(row.get(docto_col, ''))
        valor           = _safe_float(row.get(valor_col, 0))
        valor_imptos    = _safe_float(row.get(imptos_x_col, 0)) if imptos_x_col else 0.0
        co              = _safe_str(row.get(co_col, '')) if co_col else ''
        usuario_creacion= _safe_str(row.get(usuario_col, '')) if usuario_col else ''
        clase_documento = _safe_str(row.get(clase_col, '')) if clase_col else ''
        nro_documento   = _safe_str(row.get(nro_doc_col, '')) if nro_doc_col else ''

        # Calcular prefijo + folio desde "Docto. proveedor" (formato PREFIX-FOLIO)
        if '-' in docto_proveedor:
            partes = docto_proveedor.split('-', 1)
            prefijo   = partes[0].strip()
            folio_raw = partes[1].strip()
        else:
            prefijo   = ''
            folio_raw = docto_proveedor

        folio           = _ultimos_8_sin_ceros(_extraer_folio(folio_raw))
        nit_solo        = _extraer_folio(nit)
        clave_erp       = f"{nit_solo}{prefijo}{folio}"
        doc_causado_por = f"{co} | {usuario_creacion} | {nro_documento}".strip(' |')

        registros.append((
            nit, razon_social, fecha_recibido, docto_proveedor,
            valor, valor_imptos, co, usuario_creacion, clase_documento,
            nro_documento, prefijo, folio, clave_erp, modulo_nombre, doc_causado_por,
        ))

    # Deduplicar por clave_erp (índice 12) — el último prevalece
    _dedup: dict = {}
    for r in registros:
        _dedup[r[12]] = r
    duplicados = len(registros) - len(_dedup)
    registros = list(_dedup.values())

    print(f"   Procesados: {len(registros):,}  |  Omitidos (sin NIT): {omitidos:,}  |  Duplicados removidos: {duplicados:,}")

    # Insertar via tabla temporal (evita UniqueViolation con datos duplicados)
    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    cur = conn.cursor()

    cols_db = (
        'proveedor', 'razon_social', 'fecha_recibido', 'docto_proveedor',
        'valor', imptos_col_db, 'co', 'usuario_creacion', 'clase_documento',
        'nro_documento', 'prefijo', 'folio', clave_col_db, 'modulo', 'doc_causado_por',
    )
    cols_list = ', '.join(cols_db)

    try:
        # 1. Crear tabla temporal sin constraints
        cur.execute(f"CREATE TEMP TABLE _t_{tabla} (LIKE {tabla} INCLUDING DEFAULTS) ON COMMIT DROP")
        cur.execute(f"ALTER TABLE _t_{tabla} DROP CONSTRAINT IF EXISTS uk_{tabla}_clave")
        # Eliminar cualquier constraint heredada
        cur.execute(f"""
            DO $$
            DECLARE r RECORD;
            BEGIN
                FOR r IN SELECT conname FROM pg_constraint WHERE conrelid = '_t_{tabla}'::regclass
                LOOP
                    EXECUTE 'ALTER TABLE _t_{tabla} DROP CONSTRAINT ' || quote_ident(r.conname);
                END LOOP;
            END $$
        """)

        # 2. COPY a tabla temporal
        buf = io.StringIO()
        for r in registros:
            buf.write('\t'.join(_fmt(v) for v in r) + '\n')
        buf.seek(0)
        cur.copy_from(buf, f'_t_{tabla}', sep='\t', null='', columns=cols_db)
        print(f"   Copiados a tabla temporal: {cur.rowcount:,}")

        # 3. Truncar y cargar, o upsert
        if truncar:
            cur.execute(f"TRUNCATE TABLE {tabla}")
            cur.execute(f"""
                INSERT INTO {tabla} ({cols_list})
                SELECT {cols_list} FROM _t_{tabla}
                ON CONFLICT ({clave_col_db}) DO NOTHING
            """)
        else:
            cur.execute(f"""
                INSERT INTO {tabla} ({cols_list})
                SELECT {cols_list} FROM _t_{tabla}
                ON CONFLICT ({clave_col_db}) DO NOTHING
            """)

        insertados = cur.rowcount
        conn.commit()

        t = time.time() - t0
        msg = f"OK {tabla}: {insertados:,} registros en {t:.1f}s"
        print(f"   {msg}")
        return {"tabla": tabla, "insertados": insertados, "omitidos": omitidos,
                "total_leidos": total_leidos, "tiempo": t, "mensaje": msg}

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ═════════════════════════════════════════════════════════════════
# 3. CARGAR ACUSES
# ═════════════════════════════════════════════════════════════════

def cargar_acuses(ruta_excel: str, db_url: str, truncar: bool = True) -> dict:
    """
    Carga archivo Excel de acuses en tabla `acuses`.
    Deduplica por CUFE manteniendo jerarquía máxima de estado.
    """
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"📥 CARGAR ACUSES: {Path(ruta_excel).name}")
    print(f"{'='*60}")

    df = pd.read_excel(ruta_excel, engine='openpyxl', dtype=str)
    total_leidos = len(df)
    print(f"   Leídas: {total_leidos:,} filas")

    # Normalizar nombres a minúsculas con strip
    df.columns = [c.strip().lower() for c in df.columns]

    # Mapeo flexible de columnas Excel → DB
    col_map = {
        'fecha':                    'fecha',
        'adquiriente':              'adquiriente',
        'factura':                  'factura',
        'emisor':                   'emisor',
        'nit emisor':               'nit_emisor',
        'nit. pt':                  'nit_pt',
        'nit pt':                   'nit_pt',
        'estado docto.':            'estado_docto',
        'estado docto':             'estado_docto',
        'descripción reclamo':      'descripcion_reclamo',
        'descripcion reclamo':      'descripcion_reclamo',
        'descripcion del reclamo':  'descripcion_reclamo',
        'tipo documento':           'tipo_documento',
        'cufe':                     'cufe',
        'valor':                    'valor',
        'acuse recibido':           'acuse_recibido',
        'recibo bien servicio':     'recibo_bien_servicio',
        'recibo de bien/servicio':  'recibo_bien_servicio',
        'aceptación expresa':       'aceptacion_expresa',
        'aceptacion expresa':       'aceptacion_expresa',
        'reclamo':                  'reclamo',
        'aceptación tacita':        'aceptacion_tacita',
        'aceptacion tacita':        'aceptacion_tacita',
        'aceptación tácita':        'aceptacion_tacita',
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    print(f"   Columnas en BD: {df.columns.tolist()}")

    if 'cufe' not in df.columns:
        raise ValueError(f"Columna 'cufe' no encontrada. Columnas: {df.columns.tolist()}")
    if 'estado_docto' not in df.columns:
        raise ValueError(f"Columna 'estado_docto' no encontrada. Columnas: {df.columns.tolist()}")

    # Limpiar y deduplicar por cufe (jerarquía máxima)
    df['cufe'] = df['cufe'].fillna('').astype(str).str.strip()
    df = df[df['cufe'] != '']
    df['clave_acuse'] = df['cufe']

    df['_jer'] = df['estado_docto'].map(
        lambda x: JERARQUIA_ACUSES.get(_safe_str(x), 1)
    )
    df = (df.sort_values('_jer', ascending=False)
            .drop_duplicates(subset=['cufe'], keep='first')
            .drop(columns=['_jer']))

    n_unicos = len(df)
    print(f"   Únicos por CUFE: {n_unicos:,}")

    # Columnas a insertar (en orden)
    cols_a_insertar = [
        'fecha', 'adquiriente', 'factura', 'emisor', 'nit_emisor', 'nit_pt',
        'estado_docto', 'descripcion_reclamo', 'tipo_documento', 'cufe', 'valor',
        'acuse_recibido', 'recibo_bien_servicio', 'aceptacion_expresa', 'reclamo',
        'aceptacion_tacita', 'clave_acuse',
    ]
    # Asegurar todas las columnas existen
    for c in cols_a_insertar:
        if c not in df.columns:
            df[c] = ''

    df_final = df[cols_a_insertar].copy()
    df_final = df_final.fillna('').astype(str).replace({'nan': '', 'None': '', 'NaT': ''})

    # Insertar
    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        if truncar:
            cur.execute("TRUNCATE TABLE acuses")
            print("   TRUNCATE acuses (pendiente...)")

        buf = io.StringIO()
        for _, row in df_final.iterrows():
            buf.write('\t'.join(_fmt(v) for v in row) + '\n')
        buf.seek(0)

        if truncar:
            cur.copy_from(buf, 'acuses', sep='\t', null='', columns=cols_a_insertar)
            insertados = cur.rowcount
            # rowcount after copy_from might be -1; verify
            if insertados < 0:
                cur.execute("SELECT COUNT(*) FROM acuses")
                insertados = cur.fetchone()[0]
        else:
            # Upsert via temp table
            cur.execute("""
                CREATE TEMP TABLE _t_acuses (
                    fecha TEXT, adquiriente TEXT, factura TEXT, emisor TEXT,
                    nit_emisor TEXT, nit_pt TEXT, estado_docto TEXT,
                    descripcion_reclamo TEXT, tipo_documento TEXT, cufe TEXT,
                    valor TEXT, acuse_recibido TEXT, recibo_bien_servicio TEXT,
                    aceptacion_expresa TEXT, reclamo TEXT, aceptacion_tacita TEXT,
                    clave_acuse TEXT
                ) ON COMMIT DROP
            """)
            buf.seek(0)
            cur.copy_from(buf, '_t_acuses', sep='\t', null='', columns=cols_a_insertar)
            cur.execute("""
                INSERT INTO acuses (
                    fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,
                    estado_docto, descripcion_reclamo, tipo_documento, cufe, valor,
                    acuse_recibido, recibo_bien_servicio, aceptacion_expresa, reclamo,
                    aceptacion_tacita, clave_acuse
                )
                SELECT
                    fecha::date, adquiriente, factura, emisor, nit_emisor, nit_pt,
                    estado_docto, descripcion_reclamo, tipo_documento, cufe,
                    CASE WHEN valor ~ '^[0-9.]+$' THEN valor::numeric ELSE 0 END,
                    acuse_recibido, recibo_bien_servicio, aceptacion_expresa, reclamo,
                    aceptacion_tacita, clave_acuse
                FROM _t_acuses
                ON CONFLICT (clave_acuse) DO UPDATE
                    SET estado_docto = EXCLUDED.estado_docto
                    WHERE calcular_jerarquia_acuse(EXCLUDED.estado_docto)
                        > calcular_jerarquia_acuse(acuses.estado_docto)
            """)
            insertados = cur.rowcount

        conn.commit()
        t = time.time() - t0
        msg = f"✅ acuses: {n_unicos:,} registros en {t:.1f}s"
        print(f"   {msg}")
        return {"tabla": "acuses", "insertados": n_unicos, "omitidos": total_leidos - n_unicos,
                "total_leidos": total_leidos, "tiempo": t, "mensaje": msg}

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ═════════════════════════════════════════════════════════════════
# 4. RECONSTRUIR MAESTRO
# ═════════════════════════════════════════════════════════════════

def reconstruir_maestro(db_url: str) -> dict:
    """
    Reconstruye maestro_dian_vs_erp desde las tablas dian, erp_comercial,
    erp_financiero y acuses. Lógica idéntica a CONSTRUIR_MAESTRO_DESDE_BD.py.
    """
    t0 = time.time()
    print(f"\n{'='*60}")
    print("🔄 RECONSTRUIR MAESTRO DIAN vs ERP")
    print(f"{'='*60}")

    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # ── Paso 1: Lookups ERP ──────────────────────────────────
        print("   [1/4] Construyendo lookup ERP...")
        erp_por_clave = {}

        for tabla_erp, label_modulo in [('erp_comercial', 'Comercial'), ('erp_financiero', 'Financiero')]:
            cur.execute(f"""
                SELECT proveedor, razon_social, prefijo, folio,
                       modulo, doc_causado_por
                FROM {tabla_erp}
                WHERE proveedor IS NOT NULL
            """)
            cols_erp = [d[0] for d in cur.description]
            for row in cur.fetchall():
                r = dict(zip(cols_erp, row))
                clave = _crear_clave(r['proveedor'], r['prefijo'] or '', r['folio'] or '')
                if clave and clave not in erp_por_clave:
                    erp_por_clave[clave] = {
                        'razon_social':   r.get('razon_social', '') or '',
                        'modulo':         r.get('modulo', '') or label_modulo,
                        'doc_causado_por': r.get('doc_causado_por', '') or '',
                    }
            print(f"      {tabla_erp}: {len(erp_por_clave):,} claves acumuladas")

        # ── Paso 2: Lookup acuses ────────────────────────────────
        print("   [2/4] Construyendo lookup acuses...")
        cur.execute("SELECT cufe, estado_docto FROM acuses WHERE cufe IS NOT NULL AND cufe != ''")
        acuses_por_cufe = {}
        for cufe, estado in cur.fetchall():
            cufe = str(cufe or '').strip()
            estado = str(estado or '').strip()
            if cufe:
                prev = acuses_por_cufe.get(cufe, 'Pendiente')
                if _jerarquia_aprobacion(estado) > _jerarquia_aprobacion(prev):
                    acuses_por_cufe[cufe] = estado
        print(f"      {len(acuses_por_cufe):,} CUFEs con acuse")

        # ── Paso 3: Tipo tercero ─────────────────────────────────
        print("   [3/4] Construyendo tipo tercero...")
        cur.execute("SELECT DISTINCT REGEXP_REPLACE(proveedor,'[^0-9]','','g') FROM erp_comercial WHERE proveedor IS NOT NULL")
        nits_cm = {r[0] for r in cur.fetchall() if r[0]}
        cur.execute("SELECT DISTINCT REGEXP_REPLACE(proveedor,'[^0-9]','','g') FROM erp_financiero WHERE proveedor IS NOT NULL")
        nits_fn = {r[0] for r in cur.fetchall() if r[0]}
        tipo_tercero_por_nit = {}
        for nit in nits_cm | nits_fn:
            if nit in nits_cm and nit in nits_fn:
                tipo_tercero_por_nit[nit] = 'Proveedor y Acreedor'
            elif nit in nits_cm:
                tipo_tercero_por_nit[nit] = 'Proveedor'
            else:
                tipo_tercero_por_nit[nit] = 'Acreedor'

        # ── Paso 4: Leer DIAN y construir maestro ───────────────
        print("   [4/4] Leyendo DIAN y construyendo registros...")
        excluidos_sql = ', '.join(f"'{t}'" for t in TIPOS_EXCLUIDOS_DIAN)
        cur.execute(f"""
            SELECT nit_emisor, nombre_emisor, fecha_emision, prefijo, folio,
                   total, tipo_documento, cufe_cude, forma_pago
            FROM dian
            WHERE nit_emisor IS NOT NULL
              AND tipo_documento IS NOT NULL
              AND LOWER(TRIM(tipo_documento)) NOT IN ({excluidos_sql})
        """)
        cols_dian = [d[0] for d in cur.description]
        rows_dian = cur.fetchall()
        print(f"      {len(rows_dian):,} registros DIAN")

        today = date.today()
        registros = []
        con_modulo = 0

        for row in rows_dian:
            r = dict(zip(cols_dian, row))

            nit         = _extraer_folio(str(r['nit_emisor'] or ''))
            razon_dian  = str(r['nombre_emisor'] or '')
            prefijo_raw = str(r['prefijo'] or '')
            folio_raw   = str(r['folio'] or '')
            prefijo     = _extraer_prefijo(prefijo_raw)
            folio       = _ultimos_8_sin_ceros(_extraer_folio(folio_raw))

            fecha_em = r['fecha_emision']
            if isinstance(fecha_em, datetime):
                fecha_em = fecha_em.date()

            try:
                valor = float(r['total'] or 0)
            except Exception:
                valor = 0.0

            tipo_doc_raw = str(r['tipo_documento'] or '')
            tipo_doc     = SIGLAS.get(tipo_doc_raw.lower().strip(), tipo_doc_raw)
            cufe         = str(r['cufe_cude'] or '').strip()
            forma_pago   = _mapear_forma_pago(str(r['forma_pago'] or '').strip())

            clave = _crear_clave(nit, prefijo_raw, folio_raw)
            erp_info          = erp_por_clave.get(clave, {})
            modulo            = erp_info.get('modulo', '')
            doc_causado_por   = erp_info.get('doc_causado_por', '')
            razon_erp         = erp_info.get('razon_social', '')
            razon_social      = razon_erp or razon_dian

            if modulo:
                con_modulo += 1

            estado_aprobacion = acuses_por_cufe.get(cufe, 'No Registra')
            estado_contable   = 'Causada' if modulo else 'No Registrada'
            acuses_rec        = _acuses_recibidos(estado_aprobacion)

            try:
                dias = (today - fecha_em).days if fecha_em and isinstance(fecha_em, date) else 0
            except Exception:
                dias = 0

            tipo_tercero = tipo_tercero_por_nit.get(nit, 'No Registrado')

            registros.append({
                'nit_emisor':          nit,
                'razon_social':        razon_social,
                'fecha_emision':       fecha_em,
                'prefijo':             prefijo,
                'folio':               folio,
                'valor':               valor,
                'tipo_documento':      tipo_doc,
                'cufe':                cufe,
                'forma_pago':          forma_pago,
                'estado_aprobacion':   estado_aprobacion,
                'modulo':              modulo,
                'estado_contable':     estado_contable,
                'acuses_recibidos':    acuses_rec,
                'doc_causado_por':     doc_causado_por,
                'dias_desde_emision':  dias,
                'tipo_tercero':        tipo_tercero,
            })

        print(f"      Construidos: {len(registros):,}  |  Con módulo ERP: {con_modulo:,}")

        # ── Insertar en maestro (COPY FROM) ─────────────────────
        print("   Insertando en maestro_dian_vs_erp...")

        # Respaldar causación
        cur.execute("""
            CREATE TEMP TABLE IF NOT EXISTS _bk_causacion AS
            SELECT nit_emisor, prefijo, folio,
                   causada, fecha_causacion, usuario_causacion, doc_causado_por,
                   recibida, fecha_recibida, usuario_recibio,
                   rechazada, fecha_rechazo, motivo_rechazo,
                   estado_contable, origen_sincronizacion
            FROM maestro_dian_vs_erp
            WHERE doc_causado_por IS NOT NULL
               OR causada = TRUE
               OR rechazada = TRUE
               OR estado_contable IN ('Causada', 'Rechazada', 'En Trámite')
        """)
        cur.execute("SELECT COUNT(*) FROM _bk_causacion")
        n_backup = cur.fetchone()[0]
        print(f"      Backup causación: {n_backup:,}")

        cur.execute("TRUNCATE TABLE maestro_dian_vs_erp")

        # Tabla temporal con columnas explícitas
        cur.execute("""
            CREATE TEMP TABLE _t_maestro (
                nit_emisor        VARCHAR(20),
                razon_social      VARCHAR(255),
                fecha_emision     DATE,
                prefijo           VARCHAR(10),
                folio             VARCHAR(20),
                valor             NUMERIC(15,2),
                tipo_documento    VARCHAR(100),
                cufe              VARCHAR(255),
                forma_pago        VARCHAR(100),
                estado_aprobacion VARCHAR(100),
                modulo            VARCHAR(50),
                estado_contable   VARCHAR(100),
                acuses_recibidos  INTEGER,
                doc_causado_por   VARCHAR(255),
                dias_desde_emision INTEGER,
                tipo_tercero      VARCHAR(50)
            ) ON COMMIT DROP
        """)

        buf = io.StringIO()
        for reg in registros:
            line = '\t'.join([
                _fmt(reg['nit_emisor']),
                _fmt(reg['razon_social'][:255] if reg['razon_social'] else ''),
                _fmt(reg['fecha_emision']),
                _fmt(reg['prefijo']),
                _fmt(reg['folio']),
                _fmt(reg['valor']),
                _fmt(reg['tipo_documento']),
                _fmt(reg['cufe']),
                _fmt(reg['forma_pago']),
                _fmt(reg['estado_aprobacion']),
                _fmt(reg['modulo']),
                _fmt(reg['estado_contable']),
                _fmt(reg['acuses_recibidos']),
                _fmt(reg['doc_causado_por']),
                _fmt(reg['dias_desde_emision']),
                _fmt(reg['tipo_tercero']),
            ])
            buf.write(line + '\n')
        buf.seek(0)

        cols_maestro = (
            'nit_emisor', 'razon_social', 'fecha_emision', 'prefijo', 'folio',
            'valor', 'tipo_documento', 'cufe', 'forma_pago', 'estado_aprobacion',
            'modulo', 'estado_contable', 'acuses_recibidos', 'doc_causado_por',
            'dias_desde_emision', 'tipo_tercero',
        )
        cur.copy_from(buf, '_t_maestro', sep='\t', null='', columns=cols_maestro)

        cur.execute(f"""
            INSERT INTO maestro_dian_vs_erp ({', '.join(cols_maestro)})
            SELECT
                nit_emisor, razon_social, fecha_emision::date, prefijo, folio,
                COALESCE(valor, 0),
                tipo_documento, cufe, forma_pago, estado_aprobacion,
                modulo, estado_contable,
                COALESCE(acuses_recibidos, 0),
                doc_causado_por,
                COALESCE(dias_desde_emision, 0),
                tipo_tercero
            FROM _t_maestro
        """)
        insertados = cur.rowcount

        # Restaurar causación
        if n_backup > 0:
            cur.execute("""
                UPDATE maestro_dian_vs_erp m
                SET causada               = b.causada,
                    fecha_causacion       = b.fecha_causacion,
                    usuario_causacion     = b.usuario_causacion,
                    doc_causado_por       = b.doc_causado_por,
                    recibida              = b.recibida,
                    fecha_recibida        = b.fecha_recibida,
                    usuario_recibio       = b.usuario_recibio,
                    rechazada             = b.rechazada,
                    fecha_rechazo         = b.fecha_rechazo,
                    motivo_rechazo        = b.motivo_rechazo,
                    estado_contable       = b.estado_contable,
                    origen_sincronizacion = b.origen_sincronizacion
                FROM _bk_causacion b
                WHERE m.nit_emisor = b.nit_emisor
                  AND m.prefijo    = b.prefijo
                  AND m.folio      = b.folio
            """)
            print(f"      Causación restaurada: {cur.rowcount:,}")

        conn.commit()

        t = time.time() - t0
        msg = f"✅ Maestro reconstruido: {insertados:,} registros en {t:.1f}s"
        print(f"\n   {msg}")
        return {"registros": insertados, "con_modulo": con_modulo, "tiempo": t, "mensaje": msg}

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ═════════════════════════════════════════════════════════════════
# Función de alto nivel: procesar_archivo_subido
# ═════════════════════════════════════════════════════════════════

def procesar_archivo_subido(tipo: str, ruta_excel: str, db_url: str) -> dict:
    """
    Despacha al loader correcto según el tipo de archivo.

    tipo: 'dian' | 'erp_fn' | 'erp_cm' | 'acuses' | 'errores'
    """
    tipo_a_tabla = {
        'dian':    ('dian',          cargar_dian),
        'erp_fn':  ('erp_financiero', None),     # especial
        'erp_cm':  ('erp_comercial',  None),     # especial
        'acuses':  ('acuses',        cargar_acuses),
        'errores': (None, None),                  # por implementar
    }

    if tipo not in tipo_a_tabla:
        raise ValueError(f"Tipo de archivo desconocido: {tipo}")

    tabla, fn = tipo_a_tabla[tipo]

    if tipo == 'dian':
        return fn(ruta_excel, db_url, truncar=True)
    elif tipo == 'acuses':
        return fn(ruta_excel, db_url, truncar=True)
    elif tipo == 'erp_fn':
        return cargar_erp(ruta_excel, 'erp_financiero', db_url, truncar=True)
    elif tipo == 'erp_cm':
        return cargar_erp(ruta_excel, 'erp_comercial', db_url, truncar=True)
    elif tipo == 'errores':
        return {"tabla": "errores", "insertados": 0, "mensaje": "⚠️ Módulo errores no implementado aún"}

    return {"tabla": tipo, "insertados": 0, "mensaje": "⚠️ Tipo no procesado"}
