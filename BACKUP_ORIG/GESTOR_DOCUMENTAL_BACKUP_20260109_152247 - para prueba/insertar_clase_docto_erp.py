"""
Script: insertar_clase_docto_erp.py
Fecha: 30 de diciembre de 2025
Propósito: Insertar catálogo de clases de documento ERP
           para clasificación automática de terceros
"""

import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

# Configuración de conexión
DB_CONFIG = {
    'dbname': 'gestor_documental',
    'user': 'gestor_user',
    'password': 'Octubre2024**',
    'host': 'localhost',
    'port': '5432'
}

# ✅ CATÁLOGO DE CLASES - ERP FINANCIERO (ACREEDOR)
CLASES_ACREEDOR = [
    'Factura de servicio desde sol. anticipo',
    'Factura de servicio de reg.fijo compra',
    'Factura de servicio compra',
    'Legalización factura anticipos',
    'Legalización factura caja menor',
    'Nota débito de servicios - compra',
    'Factura de servicio, legalizacion gastos',
    'Legalización nota debito anticipos'
]

# ✅ CATÁLOGO DE CLASES - ERP COMERCIAL (PROVEEDOR)
CLASES_PROVEEDOR = [
    'Notas débito de proveedor',
    'Factura de proveedor',
    'Factura de consignación'
]

def crear_tabla():
    """Crea la tabla clase_docto_erp si no existe"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("📋 Creando tabla clase_docto_erp...")
        
        with open('sql/crear_tabla_clase_docto_erp.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            cursor.execute(sql)
        
        conn.commit()
        print("✅ Tabla creada correctamente")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tabla: {e}")
        return False

def insertar_clases():
    """Inserta el catálogo de clases de documento"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Limpiar tabla si existe (para evitar duplicados)
        print("🗑️ Limpiando tabla existente...")
        cursor.execute("TRUNCATE TABLE clase_docto_erp RESTART IDENTITY CASCADE")
        
        registros = []
        
        # Agregar clases ACREEDOR (ERP FINANCIERO)
        print(f"📝 Preparando {len(CLASES_ACREEDOR)} clases ACREEDOR...")
        for clase in CLASES_ACREEDOR:
            registros.append((clase, 'ACREEDOR', 'FINANCIERO'))
        
        # Agregar clases PROVEEDOR (ERP COMERCIAL)
        print(f"📝 Preparando {len(CLASES_PROVEEDOR)} clases PROVEEDOR...")
        for clase in CLASES_PROVEEDOR:
            registros.append((clase, 'PROVEEDOR', 'COMERCIAL'))
        
        # Insertar en lote
        print(f"💾 Insertando {len(registros)} registros...")
        sql = """
            INSERT INTO clase_docto_erp (clase_docto, tipo_tercero, modulo_origen)
            VALUES (%s, %s, %s)
        """
        
        execute_batch(cursor, sql, registros)
        conn.commit()
        
        # Mostrar resumen
        cursor.execute("SELECT tipo_tercero, modulo_origen, COUNT(*) FROM clase_docto_erp GROUP BY tipo_tercero, modulo_origen")
        resumen = cursor.fetchall()
        
        print("\n✅ REGISTROS INSERTADOS:")
        print("=" * 50)
        for tipo, modulo, cantidad in resumen:
            print(f"   {modulo:15} → {tipo:10} = {cantidad} clases")
        print("=" * 50)
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al insertar datos: {e}")
        if conn:
            conn.rollback()
        return False

def mostrar_catalogo():
    """Muestra el catálogo completo insertado"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, clase_docto, tipo_tercero, modulo_origen
            FROM clase_docto_erp
            ORDER BY modulo_origen, tipo_tercero, clase_docto
        """)
        
        registros = cursor.fetchall()
        
        print("\n📋 CATÁLOGO COMPLETO - clase_docto_erp")
        print("=" * 100)
        print(f"{'ID':<5} {'CLASE DOCTO':<50} {'TIPO':<15} {'MÓDULO':<15}")
        print("=" * 100)
        
        for id, clase, tipo, modulo in registros:
            print(f"{id:<5} {clase:<50} {tipo:<15} {modulo:<15}")
        
        print("=" * 100)
        print(f"TOTAL: {len(registros)} clases registradas\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al mostrar catálogo: {e}")

def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("🚀 INSERTAR CATÁLOGO DE CLASES DE DOCUMENTO ERP")
    print("=" * 60 + "\n")
    
    # Paso 1: Crear tabla
    if not crear_tabla():
        print("❌ No se pudo crear la tabla. Abortando...")
        return
    
    # Paso 2: Insertar datos
    if not insertar_clases():
        print("❌ No se pudieron insertar los datos. Abortando...")
        return
    
    # Paso 3: Mostrar catálogo
    mostrar_catalogo()
    
    print("\n✅ PROCESO COMPLETADO EXITOSAMENTE\n")
    print("💡 Ahora puedes usar esta tabla para clasificar terceros automáticamente")
    print("   basándote en el campo 'Clase docto.' de los archivos ERP.\n")

if __name__ == '__main__':
    main()
