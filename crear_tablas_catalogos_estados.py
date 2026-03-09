"""
Crear tablas catálogo de estados con jerarquía
Fecha: 29 de diciembre de 2025

Tablas:
1. estado_aceptacion: Estados de acuses de la DIAN
2. estado_contable: Estados contables del documento en el sistema
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import psycopg2
from sqlalchemy import create_engine
from app import app

# Obtener URL de conexión desde Flask (que ya lee .env correctamente)
with app.app_context():
    database_url = app.config['SQLALCHEMY_DATABASE_URI']
    
# Extraer componentes de la URL para psycopg2
engine = create_engine(database_url)
raw_conn = engine.raw_connection()

def crear_tabla_estado_aceptacion(cursor):
    """
    Crea tabla de catálogo de estados de aceptación (acuses DIAN)
    """
    print("\n" + "=" * 80)
    print("📋 TABLA 1: ESTADO_ACEPTACION (Acuses de la DIAN)")
    print("=" * 80)
    
    # Verificar si existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'estado_aceptacion'
        );
    """)
    
    existe = cursor.fetchone()[0]
    
    if existe:
        print("\n⚠️  La tabla 'estado_aceptacion' ya existe.")
        print("🗑️  Eliminando tabla existente...")
        cursor.execute("DROP TABLE estado_aceptacion CASCADE;")
        print("✅ Tabla eliminada")
    
    # Crear la tabla
    print("\n🔨 Creando tabla 'estado_aceptacion'...")
    cursor.execute("""
        CREATE TABLE estado_aceptacion (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE NOT NULL,
            jerarquia INTEGER NOT NULL,
            acuses_recibidos INTEGER NOT NULL DEFAULT 0,
            es_estado_final BOOLEAN DEFAULT FALSE,
            descripcion TEXT,
            color_ui VARCHAR(20),
            icono_ui VARCHAR(20),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            CONSTRAINT unique_jerarquia_aceptacion UNIQUE (jerarquia),
            CONSTRAINT check_jerarquia_aceptacion CHECK (jerarquia >= 1 AND jerarquia <= 6),
            CONSTRAINT check_acuses CHECK (acuses_recibidos >= 0 AND acuses_recibidos <= 2)
        );
        
        CREATE INDEX idx_estado_aceptacion_nombre ON estado_aceptacion(nombre);
        CREATE INDEX idx_estado_aceptacion_jerarquia ON estado_aceptacion(jerarquia);
        
        COMMENT ON TABLE estado_aceptacion IS 'Catálogo de estados de aceptación/acuse de la DIAN con jerarquía';
        COMMENT ON COLUMN estado_aceptacion.jerarquia IS 'Nivel de jerarquía (1=más bajo, 6=más alto)';
        COMMENT ON COLUMN estado_aceptacion.acuses_recibidos IS 'Cantidad de acuses recibidos (0=pendiente, 1=acuse recibo, 2=aceptación)';
    """)
    
    print("✅ Tabla creada")
    
    # Insertar estados
    print("\n📝 Insertando estados de aceptación...")
    
    estados = [
        # (nombre, jerarquia, acuses, es_final, descripcion, color, icono)
        ('Pendiente', 1, 0, False, 
         'Sin respuesta de la DIAN - No hay acuse', 'gray', '⏳'),
        
        ('Acuse Recibido', 2, 1, False,
         'DIAN confirmó recepción - Primer acuse', 'blue', '📨'),
        
        ('Acuse Bien/Servicio', 3, 1, False,
         'DIAN confirmó bien/servicio - Acuse intermedio', 'cyan', '📦'),
        
        ('Rechazada', 4, 1, True,
         'Documento rechazado - Estado final', 'red', '❌'),
        
        ('Aceptación Expresa', 5, 2, True,
         'Aceptación explícita - Segundo acuse - Final', 'green', '✅'),
        
        ('Aceptación Tácita', 6, 2, True,
         'Aceptación por tiempo - Segundo acuse - Final', 'green', '✔️'),
    ]
    
    for estado in estados:
        cursor.execute("""
            INSERT INTO estado_aceptacion 
            (nombre, jerarquia, acuses_recibidos, es_estado_final, descripcion, color_ui, icono_ui)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, estado)
        print(f"   {estado[6]} [{estado[1]}] {estado[0]} (acuses: {estado[2]})")
    
    print("✅ Estados de aceptación insertados")


def crear_tabla_estado_contable(cursor):
    """
    Crea tabla de catálogo de estados contables del sistema
    """
    print("\n" + "=" * 80)
    print("📋 TABLA 2: ESTADO_CONTABLE (Estados en el sistema)")
    print("=" * 80)
    
    # Verificar si existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'estado_contable'
        );
    """)
    
    existe = cursor.fetchone()[0]
    
    if existe:
        print("\n⚠️  La tabla 'estado_contable' ya existe.")
        print("🗑️  Eliminando tabla existente...")
        cursor.execute("DROP TABLE estado_contable CASCADE;")
        print("✅ Tabla eliminada")
    
    # Crear la tabla
    print("\n🔨 Creando tabla 'estado_contable'...")
    cursor.execute("""
        CREATE TABLE estado_contable (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE NOT NULL,
            jerarquia INTEGER NOT NULL,
            es_estado_final BOOLEAN DEFAULT FALSE,
            permite_edicion BOOLEAN DEFAULT TRUE,
            descripcion TEXT,
            color_ui VARCHAR(20),
            icono_ui VARCHAR(20),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            CONSTRAINT unique_jerarquia_contable UNIQUE (jerarquia),
            CONSTRAINT check_jerarquia_contable CHECK (jerarquia >= 1 AND jerarquia <= 6)
        );
        
        CREATE INDEX idx_estado_contable_nombre ON estado_contable(nombre);
        CREATE INDEX idx_estado_contable_jerarquia ON estado_contable(jerarquia);
        
        COMMENT ON TABLE estado_contable IS 'Catálogo de estados contables del documento en el sistema';
        COMMENT ON COLUMN estado_contable.jerarquia IS 'Nivel de jerarquía (1=más bajo, 6=más alto)';
        COMMENT ON COLUMN estado_contable.permite_edicion IS 'Si se puede editar/mover el documento en este estado';
        COMMENT ON COLUMN estado_contable.es_estado_final IS 'Estado terminal que no debe cambiar automáticamente';
    """)
    
    print("✅ Tabla creada")
    
    # Insertar estados
    print("\n📝 Insertando estados contables...")
    
    estados = [
        # (nombre, jerarquia, es_final, permite_edit, descripcion, color, icono)
        ('No Registrada', 1, False, True,
         'Factura DIAN sin registro en sistema - No recibida', 'red', '❓'),
        
        ('Recibida', 2, False, True,
         'Factura recibida físicamente - En facturas_recibidas', 'blue', '📥'),
        
        ('Novedad', 3, False, True,
         'Factura con observaciones/novedad - Requiere atención', 'orange', '⚠️'),
        
        ('En Trámite', 4, False, True,
         'Factura en proceso de validación - En relaciones', 'yellow', '🔄'),
        
        ('Rechazada', 5, True, False,
         'Factura rechazada - Estado final - No editable', 'red', '❌'),
        
        ('Causada', 6, True, False,
         'Factura causada en ERP - Estado final - No editable', 'green', '✅'),
    ]
    
    for estado in estados:
        cursor.execute("""
            INSERT INTO estado_contable 
            (nombre, jerarquia, es_estado_final, permite_edicion, descripcion, color_ui, icono_ui)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, estado)
        print(f"   {estado[6]} [{estado[1]}] {estado[0]} ({'Final' if estado[2] else 'Puede cambiar'})")
    
    print("✅ Estados contables insertados")


def mostrar_resumen(cursor):
    """
    Muestra resumen de ambas tablas
    """
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE TABLAS CREADAS")
    print("=" * 80)
    
    # Tabla estado_aceptacion
    print("\n🔵 ESTADO_ACEPTACION (Acuses DIAN):")
    print("-" * 80)
    cursor.execute("""
        SELECT nombre, jerarquia, acuses_recibidos, 
               CASE WHEN es_estado_final THEN 'Final' ELSE 'Transitorio' END,
               icono_ui
        FROM estado_aceptacion
        ORDER BY jerarquia;
    """)
    
    print(f"{'Icono':<6} {'Nombre':<25} {'Jerarquía':<12} {'Acuses':<10} {'Tipo'}")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[4]:<6} {row[0]:<25} {row[1]:<12} {row[2]:<10} {row[3]}")
    
    # Tabla estado_contable
    print("\n🟢 ESTADO_CONTABLE (Estados del sistema):")
    print("-" * 80)
    cursor.execute("""
        SELECT nombre, jerarquia, 
               CASE WHEN permite_edicion THEN 'Sí' ELSE 'No' END,
               CASE WHEN es_estado_final THEN 'Final' ELSE 'Transitorio' END,
               icono_ui
        FROM estado_contable
        ORDER BY jerarquia;
    """)
    
    print(f"{'Icono':<6} {'Nombre':<25} {'Jerarquía':<12} {'Editable':<10} {'Tipo'}")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row[4]:<6} {row[0]:<25} {row[1]:<12} {row[2]:<10} {row[3]}")
    
    print("\n" + "=" * 80)
    print("💡 CONSULTAS ÚTILES PARA UPSERT:")
    print("=" * 80)
    
    print("""
-- 1️⃣ Obtener jerarquía de un estado de aceptación:
SELECT jerarquia, acuses_recibidos 
FROM estado_aceptacion 
WHERE nombre = 'Acuse Recibido';

-- 2️⃣ Comparar jerarquías para decidir si actualizar (ACUSES):
SELECT 
    e1.nombre as estado_actual,
    e1.jerarquia as jerarquia_actual,
    e2.nombre as estado_nuevo,
    e2.jerarquia as jerarquia_nueva,
    CASE 
        WHEN e2.jerarquia > e1.jerarquia THEN 'ACTUALIZAR ✅'
        ELSE 'MANTENER ACTUAL ❌'
    END as decision
FROM estado_aceptacion e1, estado_aceptacion e2
WHERE e1.nombre = 'Pendiente' 
  AND e2.nombre = 'Acuse Recibido';

-- 3️⃣ Obtener jerarquía de un estado contable:
SELECT jerarquia, es_estado_final, permite_edicion
FROM estado_contable
WHERE nombre = 'Causada';

-- 4️⃣ Comparar estados contables (para sincronización):
SELECT 
    e1.nombre as actual,
    e2.nombre as nuevo,
    CASE 
        WHEN e2.jerarquia > e1.jerarquia THEN 'ACTUALIZAR'
        WHEN e1.es_estado_final THEN 'NO ACTUALIZAR (FINAL)'
        ELSE 'MANTENER'
    END as accion
FROM estado_contable e1, estado_contable e2
WHERE e1.nombre = 'Recibida' 
  AND e2.nombre = 'Causada';

-- 5️⃣ QUERY PARA UPSERT con validación de jerarquía:
INSERT INTO maestro_dian_vs_erp (nit_emisor, prefijo, folio, estado_aprobacion, estado_contable)
VALUES ('123456789', 'FV', '12345678', 'Acuse Recibido', 'Recibida')
ON CONFLICT (nit_emisor, prefijo, folio) DO UPDATE SET
    estado_aprobacion = CASE
        WHEN (SELECT jerarquia FROM estado_aceptacion WHERE nombre = EXCLUDED.estado_aprobacion) >
             (SELECT jerarquia FROM estado_aceptacion WHERE nombre = maestro_dian_vs_erp.estado_aprobacion)
        THEN EXCLUDED.estado_aprobacion
        ELSE maestro_dian_vs_erp.estado_aprobacion
    END,
    estado_contable = CASE
        WHEN (SELECT jerarquia FROM estado_contable WHERE nombre = EXCLUDED.estado_contable) >
             (SELECT jerarquia FROM estado_contable WHERE nombre = maestro_dian_vs_erp.estado_contable)
        THEN EXCLUDED.estado_contable
        ELSE maestro_dian_vs_erp.estado_contable
    END;
    """)


def main():
    """
    Proceso principal
    """
    try:
        # Usar la conexión que ya se creó globalmente
        cursor = raw_conn.cursor()
        
        print("\n" + "=" * 80)
        print("🚀 CREACIÓN DE TABLAS CATÁLOGO DE ESTADOS")
        print("=" * 80)
        
        # Crear tablas
        crear_tabla_estado_aceptacion(cursor)
        crear_tabla_estado_contable(cursor)
        
        # Commit
        raw_conn.commit()
        print("\n✅ TODAS LAS TABLAS CREADAS E INICIALIZADAS")
        
        # Mostrar resumen
        mostrar_resumen(cursor)
        
        print("\n" + "=" * 80)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print("\n💡 Ahora puedes usar estas tablas en tus UPSERT para validar jerarquías")
        print("💡 Ejecuta las consultas de ejemplo para ver cómo funcionan\n")
        
        cursor.close()
        raw_conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
