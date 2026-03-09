"""
Crear tabla catálogo de estados de aceptación con jerarquía
Fecha: 29 de diciembre de 2025

Esta tabla permite manejar la jerarquía de acuses de la DIAN
y determinar cuándo reemplazar un estado por otro más alto
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Configuración de conexión
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'gestor_documental'),
    'user': os.getenv('DB_USER', 'gestor_user'),
    'password': os.getenv('DB_PASSWORD', 'Supertiendas2024*')
}

def crear_tabla_estado_aceptacion():
    """
    Crea tabla de catálogo de estados de aceptación con jerarquía
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("📋 CREANDO TABLA CATÁLOGO DE ESTADOS DE ACEPTACIÓN")
        print("=" * 80)
        
        # 1. Verificar si la tabla ya existe
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
            respuesta = input("¿Desea eliminarla y recrearla? (s/n): ").strip().lower()
            if respuesta != 's':
                print("❌ Operación cancelada.")
                return
            
            print("\n🗑️  Eliminando tabla existente...")
            cursor.execute("DROP TABLE estado_aceptacion CASCADE;")
            print("✅ Tabla eliminada")
        
        # 2. Crear la tabla
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
                
                -- Índices para búsquedas rápidas
                CONSTRAINT unique_jerarquia UNIQUE (jerarquia),
                CONSTRAINT check_jerarquia CHECK (jerarquia >= 1 AND jerarquia <= 6),
                CONSTRAINT check_acuses CHECK (acuses_recibidos >= 0 AND acuses_recibidos <= 2)
            );
            
            -- Crear índice para búsquedas por nombre
            CREATE INDEX idx_estado_aceptacion_nombre ON estado_aceptacion(nombre);
            CREATE INDEX idx_estado_aceptacion_jerarquia ON estado_aceptacion(jerarquia);
            
            -- Comentarios
            COMMENT ON TABLE estado_aceptacion IS 'Catálogo de estados de aceptación/acuse de la DIAN con jerarquía';
            COMMENT ON COLUMN estado_aceptacion.jerarquia IS 'Nivel de jerarquía (1=más bajo, 6=más alto)';
            COMMENT ON COLUMN estado_aceptacion.acuses_recibidos IS 'Cantidad de acuses recibidos (0=pendiente, 1=acuse recibo, 2=aceptación)';
            COMMENT ON COLUMN estado_aceptacion.es_estado_final IS 'Indica si es un estado terminal que no debe cambiar';
        """)
        
        print("✅ Tabla creada exitosamente")
        
        # 3. Insertar estados con jerarquía
        print("\n📝 Insertando estados de aceptación con jerarquía...")
        
        estados = [
            # (nombre, jerarquia, acuses_recibidos, es_final, descripcion, color, icono)
            ('Pendiente', 1, 0, False, 
             'Sin respuesta de la DIAN - No hay acuse registrado',
             'gray', '⏳'),
            
            ('Acuse Recibido', 2, 1, False,
             'DIAN confirmó recepción del documento - Primer acuse',
             'blue', '📨'),
            
            ('Acuse Bien/Servicio', 3, 1, False,
             'DIAN confirmó bien o servicio recibido - Acuse intermedio',
             'cyan', '📦'),
            
            ('Rechazada', 4, 1, True,
             'Documento rechazado por el receptor - Estado final',
             'red', '❌'),
            
            ('Aceptación Expresa', 5, 2, True,
             'Aceptación explícita del documento - Segundo acuse - Estado final',
             'green', '✅'),
            
            ('Aceptación Tácita', 6, 2, True,
             'Aceptación por transcurso de tiempo - Segundo acuse - Estado final',
             'green', '✔️'),
        ]
        
        for estado in estados:
            cursor.execute("""
                INSERT INTO estado_aceptacion 
                (nombre, jerarquia, acuses_recibidos, es_estado_final, descripcion, color_ui, icono_ui)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, estado)
            print(f"   ✅ {estado[6]} [{estado[1]}] {estado[0]} (acuses: {estado[2]})")
        
        # 4. Commit
        conn.commit()
        print("\n" + "=" * 80)
        print("✅ TABLA 'estado_aceptacion' CREADA E INICIALIZADA EXITOSAMENTE")
        print("=" * 80)
        
        # 5. Mostrar resumen
        cursor.execute("""
            SELECT 
                nombre,
                jerarquia,
                acuses_recibidos,
                CASE WHEN es_estado_final THEN '✅ Final' ELSE '🔄 Puede cambiar' END as estado,
                icono_ui
            FROM estado_aceptacion
            ORDER BY jerarquia;
        """)
        
        print("\n📊 ESTADOS REGISTRADOS:")
        print("-" * 80)
        print(f"{'Icono':<6} {'Nombre':<25} {'Jerarquía':<12} {'Acuses':<10} {'Estado'}")
        print("-" * 80)
        
        for row in cursor.fetchall():
            print(f"{row[4]:<6} {row[0]:<25} {row[1]:<12} {row[2]:<10} {row[3]}")
        
        print("-" * 80)
        
        # 6. Consulta de utilidad
        print("\n💡 CONSULTAS ÚTILES:")
        print("\n-- Ver todos los estados ordenados por jerarquía:")
        print("SELECT * FROM estado_aceptacion ORDER BY jerarquia;")
        
        print("\n-- Obtener jerarquía de un estado:")
        print("SELECT jerarquia FROM estado_aceptacion WHERE nombre = 'Aceptación Expresa';")
        
        print("\n-- Contar acuses recibidos por estado:")
        print("SELECT nombre, acuses_recibidos FROM estado_aceptacion;")
        
        print("\n-- Comparar dos estados (para UPSERT):")
        print("""
SELECT 
    (SELECT jerarquia FROM estado_aceptacion WHERE nombre = 'Pendiente') as actual,
    (SELECT jerarquia FROM estado_aceptacion WHERE nombre = 'Acuse Recibido') as nuevo,
    CASE 
        WHEN (SELECT jerarquia FROM estado_aceptacion WHERE nombre = 'Acuse Recibido') > 
             (SELECT jerarquia FROM estado_aceptacion WHERE nombre = 'Pendiente')
        THEN 'ACTUALIZAR ✅'
        ELSE 'MANTENER ACTUAL ❌'
    END as decision;
        """)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_tabla_estado_aceptacion()
