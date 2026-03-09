"""
Script para VERIFICAR y CREAR la tabla observaciones_radicado
Esta tabla almacena las observaciones reales que los usuarios escriben al cambiar el estado de un RAD.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: No se encontró DATABASE_URL en el archivo .env")
    exit(1)

# Extraer los componentes de la URL
# Formato: postgresql://usuario:password@host:puerto/database
try:
    url_parts = DATABASE_URL.replace('postgresql://', '').replace('postgres://', '')
    credentials, location = url_parts.split('@')
    user, password = credentials.split(':')
    host_port, database = location.split('/')
    host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
    
    print(f"\n📊 CONECTANDO A POSTGRESQL...")
    print(f"   Host: {host}")
    print(f"   Puerto: {port}")
    print(f"   Base de datos: {database}")
    print(f"   Usuario: {user}")
    print()
    
except Exception as e:
    print(f"❌ ERROR parseando DATABASE_URL: {e}")
    exit(1)

# Conectar a PostgreSQL
try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    cursor = conn.cursor()
    print("✅ Conexión exitosa a PostgreSQL\n")
    
    # PASO 1: Verificar si la tabla existe
    print("🔍 VERIFICANDO SI EXISTE LA TABLA 'observaciones_radicado'...")
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'observaciones_radicado'
        );
    """)
    existe = cursor.fetchone()[0]
    
    if existe:
        print("✅ La tabla 'observaciones_radicado' YA EXISTE en la base de datos")
        
        # Verificar cuántos registros tiene
        cursor.execute("SELECT COUNT(*) FROM observaciones_radicado;")
        count = cursor.fetchone()[0]
        print(f"   📊 Registros actuales: {count}")
        
        if count > 0:
            # Mostrar algunos ejemplos
            cursor.execute("""
                SELECT radicado, estado, LEFT(observacion, 50) as obs_preview, usuario, fecha_registro
                FROM observaciones_radicado
                ORDER BY fecha_registro DESC
                LIMIT 5;
            """)
            registros = cursor.fetchall()
            print("\n   📋 ÚLTIMOS 5 REGISTROS:")
            for reg in registros:
                print(f"      {reg[0]} | {reg[1]} | {reg[2]}... | {reg[3]} | {reg[4]}")
        
        print("\n✅ NO ES NECESARIO CREAR LA TABLA")
        
    else:
        print("⚠️  La tabla 'observaciones_radicado' NO EXISTE")
        print("\n📝 CREANDO TABLA...\n")
        
        # PASO 2: Crear la tabla
        sql_crear_tabla = """
        CREATE TABLE IF NOT EXISTS observaciones_radicado (
            id SERIAL PRIMARY KEY,
            radicado VARCHAR(20) NOT NULL,
            estado VARCHAR(30) NOT NULL,
            observacion TEXT,
            usuario VARCHAR(100),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_radicado FOREIGN KEY (radicado) 
                REFERENCES solicitudes_registro(radicado) ON DELETE CASCADE
        );
        """
        
        cursor.execute(sql_crear_tabla)
        print("✅ Tabla 'observaciones_radicado' creada exitosamente")
        
        # PASO 3: Crear índices para optimizar consultas
        print("\n📝 Creando índices...")
        
        sql_index_radicado = """
        CREATE INDEX IF NOT EXISTS idx_observaciones_radicado 
        ON observaciones_radicado(radicado);
        """
        cursor.execute(sql_index_radicado)
        print("✅ Índice en columna 'radicado' creado")
        
        sql_index_fecha = """
        CREATE INDEX IF NOT EXISTS idx_observaciones_fecha 
        ON observaciones_radicado(fecha_registro DESC);
        """
        cursor.execute(sql_index_fecha)
        print("✅ Índice en columna 'fecha_registro' creado")
        
        # Confirmar los cambios
        conn.commit()
        print("\n✅ TODOS LOS CAMBIOS CONFIRMADOS EN LA BASE DE DATOS")
        
        # PASO 4: Verificar que se creó correctamente
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'observaciones_radicado'
            ORDER BY ordinal_position;
        """)
        columnas = cursor.fetchall()
        
        print("\n📋 ESTRUCTURA DE LA TABLA CREADA:")
        for col in columnas:
            print(f"   {col[0]:20} | {col[1]:15} | Null: {col[2]}")
    
    # Cerrar conexión
    cursor.close()
    conn.close()
    print("\n✅ VERIFICACIÓN COMPLETADA")
    print("\n" + "="*60)
    print("📌 PRÓXIMOS PASOS:")
    print("="*60)
    if not existe:
        print("1. La tabla ha sido creada exitosamente")
        print("2. Ahora necesitas MODIFICAR los endpoints en routes.py:")
        print("   a) Endpoint cambiar estado: INSERT observación en la tabla")
        print("   b) Endpoint listar RADs: SELECT observación de la tabla")
        print("3. Reinicia el servidor: python app.py")
        print("4. Prueba cambiar el estado de un RAD con observación")
        print("5. Verifica que el tooltip muestre la observación real")
    else:
        print("1. La tabla ya existía en la base de datos")
        print("2. Verifica que los endpoints estén usando esta tabla:")
        print("   a) Al cambiar estado → INSERT INTO observaciones_radicado")
        print("   b) Al listar RADs → SELECT FROM observaciones_radicado")
    print("="*60)
    
except psycopg2.Error as e:
    print(f"\n❌ ERROR DE POSTGRESQL: {e}")
    print(f"   Código: {e.pgcode}")
    print(f"   Mensaje: {e.pgerror}")
    
except Exception as e:
    print(f"\n❌ ERROR GENERAL: {e}")
    import traceback
    traceback.print_exc()

finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("\n🔌 Conexión cerrada")
