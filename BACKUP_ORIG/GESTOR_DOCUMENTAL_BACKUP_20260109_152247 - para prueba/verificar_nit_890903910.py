"""
Script para verificar si el NIT 890903910 está en la base de datos
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:GestorDoc2024!@localhost:5432/gestor_documental')

try:
    engine = create_engine(DATABASE_URL)
    
    nit_buscar = '890903910'
    
    print("=" * 100)
    print(f"🔍 BUSCANDO NIT: {nit_buscar}")
    print("=" * 100)
    print()
    
    # Buscar en tabla terceros
    query = text("""
        SELECT 
            id,
            nit,
            razon_social,
            tipo_persona,
            estado,
            fecha_registro,
            fecha_actualizacion
        FROM terceros
        WHERE nit = :nit
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"nit": nit_buscar})
        tercero = result.fetchone()
    
    if tercero:
        print("✅ TERCERO ENCONTRADO EN TABLA 'terceros':")
        print("-" * 100)
        print(f"  ID:                   {tercero[0]}")
        print(f"  NIT:                  {tercero[1]}")
        print(f"  Razón Social:         {tercero[2]}")
        print(f"  Tipo Persona:         {tercero[3]}")
        print(f"  Estado:               {tercero[4]}")
        print(f"  Fecha Registro:       {tercero[5]}")
        print(f"  Fecha Actualización:  {tercero[6]}")
        print("-" * 100)
        print()
        print("🔍 VERIFICACIÓN DEL ENDPOINT:")
        print("-" * 100)
        print(f"  El endpoint /api/registro/check_nit busca en: Tercero.query.filter_by(nit='{nit_buscar}').first()")
        print(f"  Tabla: terceros")
        print(f"  Condición: nit = '{nit_buscar}'")
        print()
        
        if tercero[4] == 'activo':
            print("  ✅ Estado es 'activo' - DEBERÍA aparecer como ENCONTRADO")
        else:
            print(f"  ⚠️  Estado es '{tercero[4]}' - Puede afectar validación")
        print()
        
        if tercero[6]:
            from datetime import date, datetime
            fecha_act = tercero[6].date() if isinstance(tercero[6], datetime) else tercero[6]
            dias = (date.today() - fecha_act).days
            print(f"  📅 Antigüedad: {dias} días")
            
            if dias >= 365:
                print(f"  ❌ VENCIDO (>= 365 días) - Debería aparecer en ROJO y BLOQUEADO")
            elif dias >= 330:
                print(f"  ⚠️  POR VENCER (330-364 días) - Debería aparecer en NARANJA")
            else:
                print(f"  ✅ ACTUALIZADO (< 330 días) - Debería aparecer en VERDE")
        else:
            print("  ⚠️  Sin fecha_actualizacion - No se calcula antigüedad")
        
        print("=" * 100)
    else:
        print("❌ TERCERO NO ENCONTRADO EN TABLA 'terceros'")
        print("-" * 100)
        print(f"  El NIT {nit_buscar} NO existe en la base de datos")
        print()
        print("🔍 POSIBLES CAUSAS:")
        print("-" * 100)
        print("  1. El NIT fue escrito incorrectamente")
        print("  2. El tercero no ha sido registrado aún")
        print("  3. El tercero fue eliminado de la BD")
        print()
        print("💡 SOLUCIÓN:")
        print("-" * 100)
        print(f"  Buscar NITs disponibles: python ver_terceros_por_antiguedad.py")
        print(f"  O verificar con:")
        print(f"  SELECT nit, razon_social FROM terceros WHERE nit LIKE '%890903910%';")
        print("=" * 100)

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
