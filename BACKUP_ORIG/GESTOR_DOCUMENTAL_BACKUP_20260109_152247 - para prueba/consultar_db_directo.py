"""
Consultar directamente la base de datos SIN importar app.py
"""
import psycopg2

# Datos de búsqueda
NIT = "805003786"
PREFIJO = "LF"
FOLIO = "29065"

print("\n" + "="*80)
print(f"🔍 CONSULTANDO BASE DE DATOS: NIT={NIT} | PREFIJO={PREFIJO} | FOLIO={FOLIO}")
print("="*80)

try:
    # Conectar a PostgreSQL
    conn = psycopg2.connect(
        dbname="gestor_documental",
        user="gestor_user",
        password="CanaveralGestor2024!",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    
    # Consultar maestro_dian_vs_erp
    print("\n📊 CONSULTANDO maestro_dian_vs_erp")
    print("-" * 80)
    
    query = """
        SELECT 
            id,
            nit_emisor,
            prefijo,
            folio,
            razon_social,
            fecha_emision,
            valor,
            estado_contable,
            estado_aprobacion,
            tipo_documento,
            forma_pago,
            recibida,
            causada,
            rechazada,
            usuario_recibio,
            fecha_recibida,
            origen_sincronizacion
        FROM maestro_dian_vs_erp
        WHERE nit_emisor = %s 
          AND prefijo = %s 
          AND folio = %s
    """
    
    cur.execute(query, (NIT, PREFIJO, FOLIO))
    result = cur.fetchone()
    
    if result:
        print("\n✅ FACTURA ENCONTRADA:")
        print(f"   ID: {result[0]}")
        print(f"   NIT-Prefijo-Folio: {result[1]}-{result[2]}-{result[3]}")
        print(f"   Razón Social: {result[4]}")
        print(f"   Fecha Emisión: {result[5]}")
        print(f"   Valor: ${result[6]:,.2f}" if result[6] else "   Valor: N/A")
        print(f"\n📊 ESTADO CONTABLE: '{result[7]}'")
        print(f"   ⚠️ Estado Aprobación: '{result[8]}'")
        print(f"   📝 Tipo Documento: '{result[9]}'")
        print(f"   💳 Forma Pago: '{result[10]}'")
        print(f"\n🔄 FLAGS:")
        print(f"   Recibida: {result[11]}")
        print(f"   Causada: {result[12]}")
        print(f"   Rechazada: {result[13]}")
        print(f"\n👤 AUDITORÍA:")
        print(f"   Usuario Recibió: '{result[14]}'")
        print(f"   Fecha Recibida: {result[15]}")
        print(f"   Origen Sync: '{result[16]}'")
        
        # Análisis del estado_contable
        estado = result[7]
        print(f"\n🔍 ANÁLISIS DEL ESTADO CONTABLE:")
        print(f"   Valor: '{estado}'")
        print(f"   Tipo: {type(estado)}")
        print(f"   ¿Es None?: {estado is None}")
        print(f"   ¿Es vacío?: {estado == '' if estado else 'N/A'}")
        print(f"   Longitud: {len(estado) if estado else 0}")
        print(f"   Repr: {repr(estado)}")
        print(f"   Bytes: {estado.encode() if estado else b''}")
        
    else:
        print("\n❌ FACTURA NO ENCONTRADA")
    
    # Consultar facturas_recibidas
    print("\n" + "="*80)
    print("📊 CONSULTANDO facturas_recibidas")
    print("-" * 80)
    
    query2 = """
        SELECT 
            id,
            nit,
            prefijo,
            folio,
            razon_social,
            fecha_expedicion,
            fecha_radicacion,
            valor_bruto,
            valor_neto,
            forma_pago,
            plazo,
            usuario_solicita,
            comprador,
            quien_recibe,
            fecha_creacion
        FROM facturas_recibidas
        WHERE nit = %s 
          AND prefijo = %s 
          AND folio = %s
    """
    
    cur.execute(query2, (NIT, PREFIJO, FOLIO))
    result2 = cur.fetchone()
    
    if result2:
        print("\n✅ FACTURA ENCONTRADA:")
        print(f"   ID: {result2[0]}")
        print(f"   NIT-Prefijo-Folio: {result2[1]}-{result2[2]}-{result2[3]}")
        print(f"   Razón Social: {result2[4]}")
        print(f"   Fecha Expedición: {result2[5]}")
        print(f"   Fecha Radicación: {result2[6]}")
        print(f"   Valor Bruto: ${result2[7]:,.2f}" if result2[7] else "   Valor Bruto: N/A")
        print(f"   Valor Neto: ${result2[8]:,.2f}" if result2[8] else "   Valor Neto: N/A")
        print(f"   Forma Pago: {result2[9]}")
        print(f"   Plazo: {result2[10]} días")
        print(f"   Usuario Solicita: {result2[11]}")
        print(f"   Comprador: {result2[12]}")
        print(f"   Quien Recibe: {result2[13]}")
        print(f"   Fecha Creación: {result2[14]}")
    else:
        print("\n❌ FACTURA NO ENCONTRADA")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ CONSULTA COMPLETADA")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
