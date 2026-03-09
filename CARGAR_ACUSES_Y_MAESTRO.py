#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CARGAR_ACUSES_Y_MAESTRO.py
==========================
Script para:
  1. Crear tabla 'acuses' en PostgreSQL (si no existe)
  2. Cargar datos desde uploads/acuses/*.xlsx
  3. Reconstruir tabla maestro_dian_vs_erp via actualizar_maestro()

Uso: python CARGAR_ACUSES_Y_MAESTRO.py
"""

import os
import sys
import time
import io
from pathlib import Path
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# 0. CONFIGURACIÓN
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_conn_str():
    """Obtiene cadena de conexión psycopg2 desde DATABASE_URL."""
    url = DATABASE_URL
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        # psycopg2 acepta la URL directamente
        return url
    raise ValueError(f"DATABASE_URL inválida: {url!r}")


# ─────────────────────────────────────────────
# 1. CREAR TABLA ACUSES (si no existe)
# ─────────────────────────────────────────────
def crear_tabla_acuses(cursor):
    """Crea la tabla acuses con todos los campos y constraint UNIQUE."""
    print("\n📋 Paso 1: Verificando tabla 'acuses'...")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS acuses (
            id                  SERIAL PRIMARY KEY,
            fecha               DATE,
            adquiriente         VARCHAR(255),
            factura             VARCHAR(100),
            emisor              VARCHAR(255),
            nit_emisor          VARCHAR(20),
            nit_pt              VARCHAR(20),
            estado_docto        VARCHAR(100),
            descripcion_reclamo TEXT,
            tipo_documento      VARCHAR(50),
            cufe                VARCHAR(255),
            valor               NUMERIC(15,2) DEFAULT 0,
            acuse_recibido      VARCHAR(50),
            recibo_bien_servicio VARCHAR(50),
            aceptacion_expresa  VARCHAR(50),
            reclamo             VARCHAR(50),
            aceptacion_tacita   VARCHAR(50),
            clave_acuse         VARCHAR(255),
            fecha_carga         TIMESTAMP DEFAULT NOW(),
            fecha_actualizacion TIMESTAMP DEFAULT NOW()
        )
    """)
    print("   ✅ Tabla 'acuses' existe o fue creada")

    # Índices
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE tablename='acuses' AND indexname='ix_acuses_clave_acuse'
            ) THEN
                CREATE UNIQUE INDEX ix_acuses_clave_acuse ON acuses(clave_acuse);
                RAISE NOTICE 'Índice UNIQUE clave_acuse creado';
            END IF;
        END$$;
    """)
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE tablename='acuses' AND indexname='ix_acuses_cufe'
            ) THEN
                CREATE INDEX ix_acuses_cufe ON acuses(cufe);
            END IF;
        END$$;
    """)
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE tablename='acuses' AND indexname='ix_acuses_nit_emisor'
            ) THEN
                CREATE INDEX ix_acuses_nit_emisor ON acuses(nit_emisor);
            END IF;
        END$$;
    """)
    print("   ✅ Índices verificados")

    # También crear función de jerarquía de acuse si no existe (necesaria para el ON CONFLICT)
    cursor.execute("""
        CREATE OR REPLACE FUNCTION calcular_jerarquia_acuse(estado TEXT) RETURNS INTEGER AS $$
        BEGIN
            RETURN CASE COALESCE(estado, 'Pendiente')
                WHEN 'Pendiente'           THEN 1
                WHEN 'Acuse Recibido'      THEN 2
                WHEN 'Acuse Bien/Servicio' THEN 3
                WHEN 'Rechazada'           THEN 4
                WHEN 'Aceptación Expresa'  THEN 5
                WHEN 'Aceptación Tácita'   THEN 6
                ELSE 1
            END;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)
    print("   ✅ Función calcular_jerarquia_acuse lista")


# ─────────────────────────────────────────────
# 2. CARGAR EXCEL ACUSES
# ─────────────────────────────────────────────
def format_value_for_copy(value):
    """Convierte valor a string TSV-safe para COPY FROM."""
    if value is None or (isinstance(value, float) and value != value):
        return ''
    s = str(value).strip()
    # Escapar tabulaciones y saltos de línea
    s = s.replace('\\', '\\\\').replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
    return s


def cargar_excel_acuses(cursor):
    """Lee el archivo Excel de acuses y lo inserta en la tabla."""
    import pandas as pd

    acuses_dir = BASE_DIR / "uploads" / "acuses"
    archivos = sorted(acuses_dir.glob("*.xlsx"))
    if not archivos:
        archivos = sorted(acuses_dir.glob("*.csv"))

    if not archivos:
        print("   ⚠️ No se encontraron archivos en uploads/acuses/")
        return 0

    archivo = archivos[-1]  # El más reciente (ordenados por nombre)
    print(f"\n📊 Paso 2: Cargando acuses desde: {archivo.name}")
    t0 = time.time()

    # Leer Excel
    df = pd.read_excel(archivo, dtype=str)
    print(f"   📦 {len(df):,} filas leídas en {time.time()-t0:.1f}s")
    print(f"   Columnas Excel: {df.columns.tolist()}")

    # Normalizar nombres de columnas (minúsculas, sin espacios extra)
    df.columns = [c.strip().lower() for c in df.columns]
    print(f"   Columnas normalizadas: {df.columns.tolist()}")

    # Mapeo Excel → DB (basado en routes.py insertar_acuses_bulk)
    column_mapping = {
        'fecha':                  'fecha',
        'adquiriente':            'adquiriente',
        'factura':                'factura',
        'emisor':                 'emisor',
        'nit emisor':             'nit_emisor',
        'nit. pt':                'nit_pt',
        'estado docto.':          'estado_docto',
        'descripción reclamo':    'descripcion_reclamo',
        'descripcion reclamo':    'descripcion_reclamo',
        'tipo documento':         'tipo_documento',
        'cufe':                   'cufe',
        'valor':                  'valor',
        'acuse recibido':         'acuse_recibido',
        'recibo bien servicio':   'recibo_bien_servicio',
        'aceptación expresa':     'aceptacion_expresa',
        'aceptacion expresa':     'aceptacion_expresa',
        'reclamo':                'reclamo',
        'aceptación tacita':      'aceptacion_tacita',
        'aceptacion tacita':      'aceptacion_tacita',
    }

    cols_a_renombrar = {k: v for k, v in column_mapping.items() if k in df.columns}
    df = df.rename(columns=cols_a_renombrar)
    print(f"   Columnas renombradas: {cols_a_renombrar}")

    # Verificar columnas clave
    if 'cufe' not in df.columns:
        print(f"   ❌ ERROR: columna 'cufe' no encontrada. Columnas: {df.columns.tolist()}")
        return 0
    if 'estado_docto' not in df.columns:
        print(f"   ❌ ERROR: columna 'estado_docto' no encontrada. Columnas: {df.columns.tolist()}")
        return 0

    # Generar clave_acuse
    df['clave_acuse'] = (
        df['cufe'].fillna('').astype(str) + '|' +
        df['estado_docto'].fillna('Pendiente').astype(str)
    )

    # Limpiar duplicados internos (quedar con primera ocurrencia por clave_acuse)
    antes = len(df)
    df = df.drop_duplicates(subset=['clave_acuse'], keep='first')
    print(f"   🔍 Duplicados internos eliminados: {antes - len(df):,}")

    # Asegurar columnas necesarias con defaults
    columnas_db = [
        'fecha', 'adquiriente', 'factura', 'emisor', 'nit_emisor', 'nit_pt',
        'estado_docto', 'descripcion_reclamo', 'tipo_documento', 'cufe', 'valor',
        'acuse_recibido', 'recibo_bien_servicio', 'aceptacion_expresa',
        'reclamo', 'aceptacion_tacita', 'clave_acuse'
    ]
    for col in columnas_db:
        if col not in df.columns:
            df[col] = None
            print(f"   ⚠️ Columna '{col}' no en Excel → se usará NULL")

    registros = df[columnas_db].to_dict('records')
    print(f"   📋 {len(registros):,} registros a insertar/actualizar")

    # Tabla temporal (sin restricciones para los duplicados de la temp)
    cursor.execute("""
        CREATE TEMP TABLE IF NOT EXISTS _temp_acuses_load (
            fecha               DATE,
            adquiriente         VARCHAR(255),
            factura             VARCHAR(100),
            emisor              VARCHAR(255),
            nit_emisor          VARCHAR(20),
            nit_pt              VARCHAR(20),
            estado_docto        VARCHAR(100),
            descripcion_reclamo TEXT,
            tipo_documento      VARCHAR(50),
            cufe                VARCHAR(255),
            valor               NUMERIC(15,2),
            acuse_recibido      VARCHAR(50),
            recibo_bien_servicio VARCHAR(50),
            aceptacion_expresa  VARCHAR(50),
            reclamo             VARCHAR(50),
            aceptacion_tacita   VARCHAR(50),
            clave_acuse         VARCHAR(255)
        )
    """)
    cursor.execute("TRUNCATE TABLE _temp_acuses_load")

    # COPY FROM
    t_copy = time.time()
    buf = io.StringIO()
    for reg in registros:
        buf.write(f"{format_value_for_copy(reg.get('fecha'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('adquiriente'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('factura'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('emisor'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('nit_emisor'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('nit_pt'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('estado_docto'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('descripcion_reclamo'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('tipo_documento'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('cufe'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('valor'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('acuse_recibido'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('recibo_bien_servicio'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('aceptacion_expresa'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('reclamo'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('aceptacion_tacita'))}\t")
        buf.write(f"{format_value_for_copy(reg.get('clave_acuse'))}\n")

    buf.seek(0)
    cursor.copy_from(
        buf,
        '_temp_acuses_load',
        sep='\t',
        null='',
        columns=tuple(columnas_db)
    )
    print(f"   ⚡ COPY FROM completado en {time.time()-t_copy:.1f}s")

    # UPSERT a tabla final
    cursor.execute("""
        INSERT INTO acuses (
            fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,
            estado_docto, descripcion_reclamo, tipo_documento, cufe, valor,
            acuse_recibido, recibo_bien_servicio, aceptacion_expresa,
            reclamo, aceptacion_tacita, clave_acuse, fecha_carga
        )
        SELECT
            fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,
            estado_docto, descripcion_reclamo, tipo_documento, cufe, valor,
            acuse_recibido, recibo_bien_servicio, aceptacion_expresa,
            reclamo, aceptacion_tacita, clave_acuse, NOW()
        FROM _temp_acuses_load
        ON CONFLICT (clave_acuse) DO UPDATE SET
            fecha               = EXCLUDED.fecha,
            adquiriente         = EXCLUDED.adquiriente,
            factura             = EXCLUDED.factura,
            emisor              = EXCLUDED.emisor,
            nit_emisor          = EXCLUDED.nit_emisor,
            nit_pt              = EXCLUDED.nit_pt,
            estado_docto        = EXCLUDED.estado_docto,
            descripcion_reclamo = EXCLUDED.descripcion_reclamo,
            tipo_documento      = EXCLUDED.tipo_documento,
            cufe                = EXCLUDED.cufe,
            valor               = EXCLUDED.valor,
            acuse_recibido      = EXCLUDED.acuse_recibido,
            recibo_bien_servicio= EXCLUDED.recibo_bien_servicio,
            aceptacion_expresa  = EXCLUDED.aceptacion_expresa,
            reclamo             = EXCLUDED.reclamo,
            aceptacion_tacita   = EXCLUDED.aceptacion_tacita,
            fecha_actualizacion = NOW()
        WHERE calcular_jerarquia_acuse(EXCLUDED.estado_docto) 
              >= calcular_jerarquia_acuse(acuses.estado_docto)
    """)

    insertados = cursor.rowcount
    print(f"   ✅ {insertados:,} registros insertados/actualizados en acuses")
    return len(registros)


# ─────────────────────────────────────────────
# 3. RECONSTRUIR MAESTRO (Flask app context)
# ─────────────────────────────────────────────
def reconstruir_maestro():
    """
    Llama actualizar_maestro() dentro del contexto de la Flask app.
    Esta función lee los Excel del disco y reconstruye maestro_dian_vs_erp.
    """
    print("\n🏗️  Paso 3: Reconstruyendo maestro_dian_vs_erp...")
    print("   (Lee todos los Excel de uploads/ y hace el JOIN completo)")

    try:
        from app import app
        from modules.dian_vs_erp.routes import actualizar_maestro

        with app.app_context():
            t0 = time.time()
            msg = actualizar_maestro()
            elapsed = time.time() - t0
            print(f"\n   ✅ Maestro reconstruido en {elapsed:.1f}s")
            print("=" * 60)
            print(msg)
            print("=" * 60)

    except Exception as e:
        import traceback
        print(f"\n   ❌ Error reconstruyendo maestro: {e}")
        traceback.print_exc()
        print("\n   💡 Si el servidor está corriendo, reinícialo después de cargar acuses")
        print("      y luego usa el botón 'Forzar Procesamiento' en la interfaz web")
        sys.exit(1)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 70)
    print("  CARGAR ACUSES Y RECONSTRUIR MAESTRO")
    print("  Sistema DIAN vs ERP - Supertiendas Cañaveral")
    print("=" * 70)

    if not DATABASE_URL:
        print("❌ DATABASE_URL no encontrada en .env")
        sys.exit(1)

    print(f"🔗 Conectando a PostgreSQL...")

    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # Paso 1: Crear tabla acuses
        crear_tabla_acuses(cursor)
        conn.commit()

        # Paso 2: Cargar Excel
        total = cargar_excel_acuses(cursor)
        conn.commit()
        print(f"\n   📊 Total acuses en BD:")
        cursor.execute("SELECT COUNT(*) FROM acuses")
        count = cursor.fetchone()[0]
        print(f"      acuses: {count:,} registros")

    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        print(f"\n❌ Error en pasos 1-2: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

    if total == 0:
        print("\n⚠️ No se cargaron acuses. Verifica el archivo Excel.")
        print("   Continuando con reconstrucción del maestro de todas formas...")

    # Paso 3: Reconstruir maestro (Flask context)
    reconstruir_maestro()

    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("   - acuses: cargados ✅")
    print("   - maestro_dian_vs_erp: reconstruido ✅")
    print("=" * 70)


if __name__ == "__main__":
    main()
