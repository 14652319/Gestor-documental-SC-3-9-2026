"""
Consultar directamente la tabla maestro_dian_vs_erp
"""
import os
from sqlalchemy import create_engine, text

# Leer configuración de .env
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:CerdosDelValle2025*@localhost:5432/gestor_documental')

# Crear conexión
engine = create_engine(DATABASE_URL)

print("🔍 Consultando tabla maestro_dian_vs_erp...")

with engine.connect() as conn:
   # Contar registros
    result = conn.execute(text("SELECT COUNT(*) FROM maestro_dian_vs_erp"))
    total = result.scalar()
    
    print(f"   Total registros: {total:,}")
    
    if total > 0:
        # Obtener últimos 2 registros
        result = conn.execute(text("""
            SELECT nit_emisor, razon_social, fecha_emision, prefijo, folio, valor, tipo_documento
            FROM maestro_dian_vs_erp
            ORDER BY id DESC
            LIMIT 2
        """))
        
        registros = result.fetchall()
        
        print("\n📊 ÚLTIMOS 2 REGISTROS CARGADOS:")
        for i, reg in enumerate(registros, 1):
            print(f"\n   Registro {i}:")
            print(f"      NIT: {reg[0]}")
            print(f"      Razón Social: {reg[1]}")
            print(f"      Fecha Emisión: {reg[2]}")
            print(f"      Prefijo: {reg[3]}")
            print(f"      Folio: {reg[4]}")
            print(f"      ⚠️ VALOR: {reg[5]}  ← ¡ESTE ES EL CAMPO QUE DEBE ESTAR CORRECTO!")
            print(f"      Tipo: {reg[6]}")
            
            # Verificar valores esperados
            if i == 1:  # Último registro cargado
                if reg[5] is None or reg[5] == 0:
                    print("\n      ❌ ERROR: Valor es NULL o 0")
                    print("      Esperado: 1555408.0 o 1036644.7")
                elif reg[5] in [1555408.0, 1036644.7]:
                    print("\n      ✅ CORRECTO: Valor detectado correctamente")
                else:
                    print(f"\n      ⚠️ Valor detectado: {reg[5]} (verificar si es correcto)")
                
                if reg[2]:
                    fecha_str = str(reg[2])
                    if '2026-02-17' in fecha_str:
                        print("      ❌ ERROR: Fecha es hoy, no la del CSV")
                    elif '2025-01' in fecha_str:
                        print("      ✅ CORRECTO: Fecha de enero 2025")
                    else:
                        print(f"      ⚠️  Verificar fecha: {fecha_str}")
    else:
        print("\n❌ La tabla está vacía")
        print("   Debes cargar el archivo desde el navegador en:")
        print("   http://127.0.0.1:8099/dian_vs_erp/cargar_archivos")

print("\n✅ Consulta completa")
