"""
VERIFICAR ESTADO REAL DE LAS TABLAS
Muestra el conteo exacto de registros en cada tabla
"""
import psycopg2

# Conexión
conn = psycopg2.connect(
    dbname="gestor_documental",
    user="postgres",
    password="654321",
    host="localhost",
    port=5432
)

cursor = conn.cursor()

print("\n" + "="*80)
print("VERIFICACIÓN DE ESTADO DE TABLAS")
print("="*80)

# Tablas a verificar
tablas = [
    'dian',
    'erp_financiero', 
    'erp_comercial',
    'acuses_recibidos',
    'maestro_dian_vs_erp'
]

for tabla in tablas:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"\n❌ {tabla}: {count:,} registros (NO ESTÁ VACÍA)")
            
            # Mostrar un ejemplo del primer registro
            cursor.execute(f"SELECT * FROM {tabla} LIMIT 1")
            ejemplo = cursor.fetchone()
            if ejemplo:
                print(f"   Ejemplo primer registro: {ejemplo[:3]}...")
        else:
            print(f"\n✅ {tabla}: 0 registros (VACÍA)")
            
    except Exception as e:
        print(f"\n⚠️  {tabla}: Error al consultar - {e}")

print("\n" + "="*80)
print("DIAGNÓSTICO:")
print("="*80)

# Verificar específicamente el CUFE problemático
cufe_problema = "929f7761de9ff5fd92865b32d3aabbd4e056589f9cb854c0cfc15a570564f657aba35f6131872b4523c43152f393c793"

cursor.execute("""
    SELECT cufe_cude, nit_proveedor, prefijo, folio, valor_total, fecha_emision
    FROM dian 
    WHERE cufe_cude = %s
""", (cufe_problema,))

registro = cursor.fetchone()
if registro:
    print(f"\n🔍 El CUFE problemático SÍ EXISTE en la tabla dian:")
    print(f"   CUFE: {registro[0][:50]}...")
    print(f"   NIT: {registro[1]}")
    print(f"   Prefijo: {registro[2]}")
    print(f"   Folio: {registro[3]}")
    print(f"   Valor: ${registro[4]:,.2f}")
    print(f"   Fecha: {registro[5]}")
else:
    print(f"\n✅ El CUFE problemático NO existe en dian")

conn.close()

print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
print("Si alguna tabla muestra registros (NO ESTÁ VACÍA),")
print("necesitas ejecutar el script de limpieza COMPLETA.")
print("\nComando: python limpiar_tabla_COMPLETO.py")
print("="*80 + "\n")
