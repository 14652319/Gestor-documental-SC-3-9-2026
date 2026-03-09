#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUIR_MAESTRO_DESDE_BD.py
==============================
Construye maestro_dian_vs_erp directamente desde las tablas ya cargadas
en PostgreSQL (dian, erp_comercial, erp_financiero, acuses).

NO necesita Flask app context.
USA exactamente la misma lógica de normalización de routes.py.

Uso: python CONSTRUIR_MAESTRO_DESDE_BD.py
"""

import os
import re
import io
import sys
import time
from pathlib import Path
from datetime import date, datetime
from dotenv import load_dotenv

# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# ─────────────────────────────────────────────
# FUNCIONES DE NORMALIZACIÓN (idénticas a routes.py)
# ─────────────────────────────────────────────
def extraer_prefijo(docto: str) -> str:
    if not docto:
        return ""
    prefijo = re.sub(r'[\-\.\s]', '', str(docto)).strip().upper()
    if len(prefijo) > 20:
        if re.match(r'^[A-F0-9]+$', prefijo) and len(prefijo) > 20:
            return ""
        return prefijo[:20]
    return prefijo

def extraer_folio(docto: str) -> str:
    if not docto:
        return ""
    return re.sub(r'[^0-9]', '', str(docto))

def ultimos_8_sin_ceros(folio: str) -> str:
    if not folio:
        return "0"
    numeros = re.sub(r'[^0-9]', '', str(folio))
    if not numeros:
        return "0"
    ultimos = numeros[-8:] if len(numeros) >= 8 else numeros
    return ultimos.lstrip('0') or '0'

def crear_clave_factura(nit: str, prefijo: str, folio: str) -> str:
    nit_limpio = extraer_folio(str(nit))
    prefijo_limpio = extraer_prefijo(str(prefijo))
    folio_8 = ultimos_8_sin_ceros(extraer_folio(str(folio)))
    return f"{nit_limpio}{prefijo_limpio}{folio_8}"

def obtener_jerarquia_aceptacion(estado: str) -> int:
    jerarquias = {
        'Pendiente': 1,
        'Acuse Recibido': 2,
        'Acuse Bien/Servicio': 3,
        'Rechazada': 4,
        'Aceptación Expresa': 5,
        'Aceptación Tácita': 6,
    }
    return jerarquias.get(str(estado).strip() if estado else 'Pendiente', 1)

def calcular_acuses_recibidos(estado_aprobacion: str) -> int:
    jerarquias_contables = {
        'Acuse Bien/Servicio': 1,
        'Aceptación Expresa': 2,
        'Aceptación Tácita': 3,
        'Rechazada': 0,
    }
    return jerarquias_contables.get(str(estado_aprobacion).strip() if estado_aprobacion else '', 0)

def format_for_copy(v):
    if v is None or (isinstance(v, float) and v != v):
        return ''
    if isinstance(v, bool):
        return 't' if v else 'f'
    s = str(v).strip()
    s = s.replace('\\', '\\\\').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    return s

# Tipos de documento DIAN que NO se incluyen en el maestro
TIPOS_EXCLUIDOS_DIAN = {
    'tipo de documento',
    'application response',
    'documento soporte con no obligados',
    'nota de ajuste del documento soporte',
}

# Mapeo forma de pago: código → texto
FORMA_PAGO_MAP = {
    '1':   'Contado',
    '1.0': 'Contado',
    '2':   'Crédito',
    '2.0': 'Crédito',
}

def mapear_forma_pago(val: str) -> str:
    s = str(val).strip()
    return FORMA_PAGO_MAP.get(s, s)  # Si ya es 'Contado'/'Crédito', lo devuelve igual

SIGLAS = {
    "factura electrónica": "FE", "factura electronica": "FE",
    "factura electrónica de exportación": "FEE",
    "nota de débito electrónica": "NDE",
    "factura electrónica de contingencia": "FEC",
    "documento soporte con no obligados": "DSNO",
    "factura electrónica de contingencia dian": "FECD",
    "documento equivalente pos": "DEPOS",
    "nota de ajuste crédito del documento equivalente": "NCDE",
    "nota de crédito electrónica": "NCE",
}


# ─────────────────────────────────────────────
# PASO 1: LEER TABLAS FUENTE
# ─────────────────────────────────────────────
def leer_tabla(cursor, tabla, columnas="*", extra_where=""):
    """Lee una tabla completa y devuelve lista de dicts."""
    where = f"WHERE {extra_where}" if extra_where else ""
    cursor.execute(f"SELECT {columnas} FROM {tabla} {where}")
    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(cols, r)) for r in rows]


def construir_erp_por_clave(cursor):
    """
    Lee erp_comercial y erp_financiero y construye dict:
    clave → {razon_social, modulo, doc_causado_por}
    
    Clave = NIT + PREFIJO_NORM + FOLIO_8
    Prioridad: comercial > financiero
    """
    print("   📦 Leyendo erp_comercial...")
    t0 = time.time()
    cursor.execute("""
        SELECT proveedor, razon_social, prefijo, folio,
               modulo, nro_documento AS doc_causado_por
        FROM erp_comercial
        WHERE proveedor IS NOT NULL
    """)
    cols = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    print(f"      {len(rows):,} registros en {time.time()-t0:.1f}s")

    erp_por_clave = {}
    for row in rows:
        r = dict(zip(cols, row))
        nit = str(r['proveedor'] or '')
        prefijo = str(r['prefijo'] or '')
        folio = str(r['folio'] or '')
        clave = crear_clave_factura(nit, prefijo, folio)
        if clave and clave not in erp_por_clave:
            erp_por_clave[clave] = {
                'razon_social': r.get('razon_social', ''),
                'modulo': r.get('modulo', 'COMERCIAL') or 'COMERCIAL',
                'doc_causado_por': r.get('doc_causado_por', ''),
            }

    print("   📦 Leyendo erp_financiero...")
    t0 = time.time()
    cursor.execute("""
        SELECT proveedor, razon_social, prefijo, folio,
               modulo, nro_documento AS doc_causado_por
        FROM erp_financiero
        WHERE proveedor IS NOT NULL
    """)
    cols = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    print(f"      {len(rows):,} registros en {time.time()-t0:.1f}s")

    for row in rows:
        r = dict(zip(cols, row))
        nit = str(r['proveedor'] or '')
        prefijo = str(r['prefijo'] or '')
        folio = str(r['folio'] or '')
        clave = crear_clave_factura(nit, prefijo, folio)
        if clave and clave not in erp_por_clave:  # Comercial tiene prioridad
            erp_por_clave[clave] = {
                'razon_social': r.get('razon_social', ''),
                'modulo': r.get('modulo', 'FINANCIERO') or 'FINANCIERO',
                'doc_causado_por': r.get('doc_causado_por', ''),
            }

    print(f"   ✅ {len(erp_por_clave):,} claves ERP únicas construidas")
    return erp_por_clave


def construir_acuses_por_cufe(cursor):
    """
    Lee tabla acuses y construye dict cufe → estado_docto (jerarquía máxima).
    """
    print("   📦 Leyendo acuses...")
    t0 = time.time()
    cursor.execute("SELECT cufe, estado_docto FROM acuses WHERE cufe IS NOT NULL AND cufe != ''")
    rows = cursor.fetchall()
    print(f"      {len(rows):,} registros en {time.time()-t0:.1f}s")

    acuses_por_cufe = {}
    for cufe, estado in rows:
        cufe = str(cufe or '').strip()
        estado = str(estado or '').strip()
        if not cufe:
            continue
        existing = acuses_por_cufe.get(cufe, 'Pendiente')
        if obtener_jerarquia_aceptacion(estado) > obtener_jerarquia_aceptacion(existing):
            acuses_por_cufe[cufe] = estado

    print(f"   ✅ {len(acuses_por_cufe):,} CUFEs con acuse")
    return acuses_por_cufe


def construir_tipo_tercero(cursor):
    """
    Construye dict nit → tipo_tercero (Proveedor / Acreedor / etc.)
    """
    tipo_tercero_por_nit = {}

    cursor.execute("SELECT DISTINCT REGEXP_REPLACE(proveedor, '[^0-9]', '', 'g') AS nit FROM erp_comercial WHERE proveedor IS NOT NULL")
    nits_comercial = {r[0] for r in cursor.fetchall()}

    cursor.execute("SELECT DISTINCT REGEXP_REPLACE(proveedor, '[^0-9]', '', 'g') AS nit FROM erp_financiero WHERE proveedor IS NOT NULL")
    nits_financiero = {r[0] for r in cursor.fetchall()}

    all_nits = nits_comercial | nits_financiero
    for nit in all_nits:
        en_cm = nit in nits_comercial
        en_fn = nit in nits_financiero
        if en_cm and en_fn:
            tipo_tercero_por_nit[nit] = 'Proveedor y Acreedor'
        elif en_cm:
            tipo_tercero_por_nit[nit] = 'Proveedor'
        else:
            tipo_tercero_por_nit[nit] = 'Acreedor'

    return tipo_tercero_por_nit


# ─────────────────────────────────────────────
# PASO 2: CONSTRUIR REGISTROS MAESTRO
# ─────────────────────────────────────────────
def construir_registros_maestro(cursor, erp_por_clave, acuses_por_cufe, tipo_tercero_por_nit):
    """
    Lee tabla dian y construye registros para maestro_dian_vs_erp.
    Usa exactamente la misma lógica de actualizar_maestro() en routes.py.
    """
    print("   📦 Leyendo tabla dian...")
    t0 = time.time()
    # Construir lista de tipos excluidos para SQL
    excluidos_sql = ", ".join(f"'{t}'" for t in TIPOS_EXCLUIDOS_DIAN)
    cursor.execute(f"""
        SELECT nit_emisor, nombre_emisor, fecha_emision, prefijo, folio,
               total, tipo_documento, cufe_cude, forma_pago
        FROM dian
        WHERE nit_emisor IS NOT NULL
          AND tipo_documento IS NOT NULL
          AND LOWER(TRIM(tipo_documento)) NOT IN ({excluidos_sql})
    """)
    cols = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    print(f"      {len(rows):,} registros DIAN en {time.time()-t0:.1f}s")

    today = date.today()
    registros = []
    registros_con_modulo = 0
    errores_valor = 0

    print(f"   🔄 Procesando {len(rows):,} registros...")
    for row in rows:
        r = dict(zip(cols, row))

        # NIT
        nit_raw = str(r['nit_emisor'] or '')
        nit = extraer_folio(nit_raw)

        # Razón social (del ERP si disponible, sino del DIAN)
        razon_social_dian = str(r['nombre_emisor'] or '')

        # Fecha emisión
        fecha_emision = r['fecha_emision']
        if isinstance(fecha_emision, datetime):
            fecha_emision = fecha_emision.date()
        # Ya debería ser date desde la BD

        # Prefijo y folio (normalizados igual que en routes.py)
        prefijo_raw = str(r['prefijo'] or '')
        prefijo = extraer_prefijo(prefijo_raw)

        folio_raw = str(r['folio'] or '')
        folio = ultimos_8_sin_ceros(extraer_folio(folio_raw))

        # Valor
        try:
            valor = float(r['total'] or 0)
        except:
            valor = 0.0
            errores_valor += 1

        # Tipo documento (mapear a sigla si existe)
        tipo_doc_raw = str(r['tipo_documento'] or '')
        tipo_documento = SIGLAS.get(tipo_doc_raw.lower().strip(), tipo_doc_raw)

        # CUFE
        cufe = str(r['cufe_cude'] or '').strip()

        # Forma de pago: mapear código numérico a texto
        forma_pago = mapear_forma_pago(str(r['forma_pago'] or '').strip())

        # Buscar en ERP
        clave = crear_clave_factura(nit, prefijo_raw, folio_raw)
        erp_info = erp_por_clave.get(clave, {})
        modulo = erp_info.get('modulo', '') if erp_info else ''
        doc_causado_por = erp_info.get('doc_causado_por', '') if erp_info else ''
        razon_social_erp = erp_info.get('razon_social', '') if erp_info else ''
        razon_social = razon_social_erp or razon_social_dian

        if modulo:
            registros_con_modulo += 1

        # Estado aprobación desde acuses
        estado_aprobacion = acuses_por_cufe.get(cufe, 'No Registra')

        # Estado contable
        estado_contable = 'Causada' if modulo else 'No Registrada'

        # Acuses recibidos
        acuses_recibidos = calcular_acuses_recibidos(estado_aprobacion)

        # Días desde emisión
        dias_desde_emision = 0
        try:
            if fecha_emision and isinstance(fecha_emision, date):
                dias_desde_emision = (today - fecha_emision).days
        except:
            dias_desde_emision = 0

        # Tipo tercero
        tipo_tercero = tipo_tercero_por_nit.get(nit, 'No Registrado')

        registros.append({
            'nit_emisor': nit,
            'razon_social': razon_social,
            'fecha_emision': fecha_emision,
            'prefijo': prefijo,
            'folio': folio,
            'valor': valor,
            'tipo_documento': tipo_documento,
            'cufe': cufe,
            'forma_pago': forma_pago,
            'estado_aprobacion': estado_aprobacion,
            'modulo': modulo,
            'estado_contable': estado_contable,
            'acuses_recibidos': acuses_recibidos,
            'doc_causado_por': doc_causado_por,
            'dias_desde_emision': dias_desde_emision,
            'tipo_tercero': tipo_tercero,
        })

    print(f"   ✅ {len(registros):,} registros construidos")
    print(f"      Con módulo ERP: {registros_con_modulo:,} ({registros_con_modulo/len(registros)*100:.1f}%)")
    return registros


# ─────────────────────────────────────────────
# PASO 3: INSERTAR EN MAESTRO
# ─────────────────────────────────────────────
def insertar_en_maestro(cursor, registros):
    """
    Inserta registros en maestro_dian_vs_erp usando COPY FROM (ultra rápido).
    1. Respalda campos de causación
    2. Trunca maestro
    3. Inserta vía COPY FROM
    4. Restaura campos de causación
    """
    print(f"\n   📥 Insertando {len(registros):,} registros en maestro_dian_vs_erp...")

    # 1. Backup de campos de causación
    cursor.execute("""
        CREATE TEMP TABLE IF NOT EXISTS _backup_causacion AS
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
    cursor.execute("SELECT COUNT(*) FROM _backup_causacion")
    respaldados = cursor.fetchone()[0]
    print(f"      Respaldo causación: {respaldados:,} registros")

    # 2. Limpiar maestro
    cursor.execute("TRUNCATE TABLE maestro_dian_vs_erp")
    print("      Maestro truncado")

    # 3. Tabla temporal
    cursor.execute("""
        CREATE TEMP TABLE IF NOT EXISTS _temp_maestro (
            nit_emisor          VARCHAR(20),
            razon_social        VARCHAR(255),
            fecha_emision       DATE,
            prefijo             VARCHAR(10),
            folio               VARCHAR(20),
            valor               NUMERIC(15,2),
            tipo_documento      VARCHAR(100),
            cufe                VARCHAR(255),
            forma_pago          VARCHAR(100),
            estado_aprobacion   VARCHAR(100),
            modulo              VARCHAR(50),
            estado_contable     VARCHAR(100),
            acuses_recibidos    INTEGER,
            doc_causado_por     VARCHAR(255),
            dias_desde_emision  INTEGER,
            tipo_tercero        VARCHAR(50)
        )
    """)
    cursor.execute("TRUNCATE TABLE _temp_maestro")

    # 4. COPY FROM
    t_copy = time.time()
    buf = io.StringIO()
    for reg in registros:
        buf.write(f"{format_for_copy(reg['nit_emisor'])}\t")
        buf.write(f"{format_for_copy(reg['razon_social'])}\t")
        buf.write(f"{format_for_copy(reg['fecha_emision'])}\t")
        buf.write(f"{format_for_copy(reg['prefijo'])}\t")
        buf.write(f"{format_for_copy(reg['folio'])}\t")
        buf.write(f"{format_for_copy(reg['valor'])}\t")
        buf.write(f"{format_for_copy(reg['tipo_documento'])}\t")
        buf.write(f"{format_for_copy(reg['cufe'])}\t")
        buf.write(f"{format_for_copy(reg['forma_pago'])}\t")
        buf.write(f"{format_for_copy(reg['estado_aprobacion'])}\t")
        buf.write(f"{format_for_copy(reg['modulo'])}\t")
        buf.write(f"{format_for_copy(reg['estado_contable'])}\t")
        buf.write(f"{format_for_copy(reg['acuses_recibidos'])}\t")
        buf.write(f"{format_for_copy(reg['doc_causado_por'])}\t")
        buf.write(f"{format_for_copy(reg['dias_desde_emision'])}\t")
        buf.write(f"{format_for_copy(reg['tipo_tercero'])}\n")

    buf.seek(0)
    cursor.copy_from(
        buf,
        '_temp_maestro',
        sep='\t',
        null='',
        columns=(
            'nit_emisor', 'razon_social', 'fecha_emision', 'prefijo', 'folio',
            'valor', 'tipo_documento', 'cufe', 'forma_pago', 'estado_aprobacion',
            'modulo', 'estado_contable', 'acuses_recibidos', 'doc_causado_por',
            'dias_desde_emision', 'tipo_tercero'
        )
    )
    print(f"      COPY FROM: {time.time()-t_copy:.1f}s")

    # 5. INSERT desde temp
    cursor.execute("""
        INSERT INTO maestro_dian_vs_erp (
            nit_emisor, razon_social, fecha_emision, prefijo, folio,
            valor, tipo_documento, cufe, forma_pago, estado_aprobacion,
            modulo, estado_contable, acuses_recibidos, doc_causado_por,
            dias_desde_emision, tipo_tercero
        )
        SELECT 
            nit_emisor, razon_social, fecha_emision, prefijo, folio,
            valor::numeric, tipo_documento, cufe, forma_pago, estado_aprobacion,
            modulo, estado_contable, acuses_recibidos::integer, doc_causado_por,
            dias_desde_emision::integer, tipo_tercero
        FROM _temp_maestro
    """)
    insertados = cursor.rowcount
    print(f"      Insertados: {insertados:,}")

    # 6. Restaurar causación
    if respaldados > 0:
        cursor.execute("""
            UPDATE maestro_dian_vs_erp m
            SET causada              = b.causada,
                fecha_causacion      = b.fecha_causacion,
                usuario_causacion    = b.usuario_causacion,
                doc_causado_por      = b.doc_causado_por,
                recibida             = b.recibida,
                fecha_recibida       = b.fecha_recibida,
                usuario_recibio      = b.usuario_recibio,
                rechazada            = b.rechazada,
                fecha_rechazo        = b.fecha_rechazo,
                motivo_rechazo       = b.motivo_rechazo,
                estado_contable      = b.estado_contable,
                origen_sincronizacion= b.origen_sincronizacion
            FROM _backup_causacion b
            WHERE m.nit_emisor = b.nit_emisor
              AND m.prefijo    = b.prefijo
              AND m.folio      = b.folio
        """)
        restaurados = cursor.rowcount
        print(f"      Causación restaurada: {restaurados:,}")

    return insertados


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 70)
    print("  CONSTRUIR MAESTRO DIAN vs ERP DESDE TABLAS BD")
    print("  Sistema DIAN vs ERP - Supertiendas Cañaveral")
    print("=" * 70)

    if not DATABASE_URL:
        print("❌ DATABASE_URL no encontrada en .env")
        sys.exit(1)

    import psycopg2
    print(f"\n🔗 Conectando a PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # Verificar tablas fuente
        print("\n📊 Verificando tablas fuente:")
        for tabla in ['dian', 'erp_comercial', 'erp_financiero', 'acuses', 'maestro_dian_vs_erp']:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"   {tabla:30}: {count:,}")

        t0 = time.time()

        print("\n🔄 Paso 1: Construyendo estructuras de lookup...")
        erp_por_clave         = construir_erp_por_clave(cursor)
        acuses_por_cufe       = construir_acuses_por_cufe(cursor)
        tipo_tercero_por_nit  = construir_tipo_tercero(cursor)

        print("\n🔄 Paso 2: Construyendo registros maestro...")
        registros = construir_registros_maestro(
            cursor, erp_por_clave, acuses_por_cufe, tipo_tercero_por_nit
        )

        print("\n🔄 Paso 3: Insertando en maestro_dian_vs_erp...")
        total = insertar_en_maestro(cursor, registros)
        conn.commit()

        elapsed = time.time() - t0
        velocidad = total / elapsed if elapsed > 0 else 0

        # Conteo final
        cursor.execute("SELECT COUNT(*) FROM maestro_dian_vs_erp")
        final_count = cursor.fetchone()[0]

        print("\n" + "=" * 70)
        print("✅ MAESTRO CONSTRUIDO EXITOSAMENTE")
        print(f"   📊 Registros en maestro_dian_vs_erp: {final_count:,}")
        print(f"   ⏱️  Tiempo total: {elapsed:.1f}s")
        print(f"   ⚡ Velocidad: {velocidad:,.0f} registros/segundo")
        print(f"   🔗 Con módulo ERP: {sum(1 for r in registros if r['modulo']):,}")
        print(f"   ✉️  Con acuse: {sum(1 for r in registros if r['estado_aprobacion'] != 'No Registra'):,}")
        print("=" * 70)

    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
