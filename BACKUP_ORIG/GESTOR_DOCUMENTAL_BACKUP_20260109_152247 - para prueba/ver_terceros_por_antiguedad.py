"""
Script para ver terceros clasificados por antigüedad de documentación
Muestra qué tercero usar para probar cada escenario
"""
import sys
from datetime import date, datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:GestorDoc2024!@localhost:5432/gestor_documental')

try:
    engine = create_engine(DATABASE_URL)
    
    # Query para obtener terceros con estado activo
    query = text("""
        SELECT 
            nit,
            razon_social,
            estado,
            fecha_actualizacion,
            fecha_registro
        FROM terceros
        WHERE estado = 'activo'
        ORDER BY fecha_actualizacion DESC NULLS LAST
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        terceros = result.fetchall()
    
    if not terceros:
        print("❌ No se encontraron terceros con estado 'activo'")
        sys.exit(1)
    
    print("=" * 100)
    print("📊 TERCEROS CLASIFICADOS POR ANTIGÜEDAD DE DOCUMENTACIÓN")
    print("=" * 100)
    print(f"Fecha actual: {date.today().strftime('%d/%m/%Y')}\n")
    
    # Clasificar terceros por escenario
    escenario1 = []  # < 330 días
    escenario2 = []  # 330-364 días
    escenario3 = []  # >= 365 días
    sin_fecha = []
    
    for tercero in terceros:
        nit, razon_social, estado, fecha_act, fecha_reg = tercero
        
        if not fecha_act:
            sin_fecha.append((nit, razon_social, "Sin fecha"))
            continue
        
        # Calcular días de antigüedad
        hoy = date.today()
        if isinstance(fecha_act, datetime):
            fecha_act = fecha_act.date()
        
        dias = (hoy - fecha_act).days
        
        if dias >= 365:
            escenario3.append((nit, razon_social, fecha_act, dias))
        elif dias >= 330:
            escenario2.append((nit, razon_social, fecha_act, dias))
        else:
            escenario1.append((nit, razon_social, fecha_act, dias))
    
    # Mostrar Escenario 1: ACTUALIZADO (Verde)
    print("✅ ESCENARIO 1: ACTUALIZADO (< 330 días) - Verde - Sin restricciones")
    print("-" * 100)
    if escenario1:
        for nit, razon, fecha, dias in escenario1:
            print(f"  NIT: {nit:15} | {razon:40} | {fecha.strftime('%d/%m/%Y')} | {dias:3} días")
        print(f"\n  💡 USA CUALQUIERA DE ESTOS {len(escenario1)} TERCEROS para probar registro NORMAL\n")
    else:
        print("  ⚠️  No hay terceros en este rango\n")
    
    # Mostrar Escenario 2: POR VENCER (Naranja)
    print("⚠️  ESCENARIO 2: PRÓXIMO A VENCER (330-364 días) - Naranja - Con advertencia")
    print("-" * 100)
    if escenario2:
        for nit, razon, fecha, dias in escenario2:
            dias_restantes = 365 - dias
            print(f"  NIT: {nit:15} | {razon:40} | {fecha.strftime('%d/%m/%Y')} | {dias:3} días | ⏰ Quedan {dias_restantes} días")
        print(f"\n  💡 USA CUALQUIERA DE ESTOS {len(escenario2)} TERCEROS para probar ADVERTENCIA de vencimiento\n")
    else:
        print("  ⚠️  No hay terceros en este rango")
        print("  📝 RECOMENDACIÓN: Modifica manualmente la fecha_actualizacion de un tercero:")
        print("     UPDATE terceros SET fecha_actualizacion = CURRENT_DATE - INTERVAL '340 days' WHERE nit = 'TU_NIT';\n")
    
    # Mostrar Escenario 3: VENCIDO (Rojo - BLOQUEADO)
    print("❌ ESCENARIO 3: DOCUMENTACIÓN VENCIDA (>= 365 días) - Rojo - BLOQUEADO")
    print("-" * 100)
    if escenario3:
        for nit, razon, fecha, dias in escenario3:
            print(f"  NIT: {nit:15} | {razon:40} | {fecha.strftime('%d/%m/%Y')} | {dias:3} días | 🚫 BLOQUEADO")
        print(f"\n  💡 USA CUALQUIERA DE ESTOS {len(escenario3)} TERCEROS para probar BLOQUEO de registro\n")
    else:
        print("  ⚠️  No hay terceros en este rango")
        print("  📝 RECOMENDACIÓN: Modifica manualmente la fecha_actualizacion de un tercero:")
        print("     UPDATE terceros SET fecha_actualizacion = CURRENT_DATE - INTERVAL '400 days' WHERE nit = 'TU_NIT';\n")
    
    # Terceros sin fecha
    if sin_fecha:
        print("⚠️  TERCEROS SIN FECHA DE ACTUALIZACIÓN")
        print("-" * 100)
        for nit, razon, estado in sin_fecha:
            print(f"  NIT: {nit:15} | {razon:40} | {estado}")
        print()
    
    # Resumen
    print("=" * 100)
    print(f"📊 RESUMEN:")
    print(f"  ✅ Escenario 1 (< 330 días):      {len(escenario1)} terceros")
    print(f"  ⚠️  Escenario 2 (330-364 días):   {len(escenario2)} terceros")
    print(f"  ❌ Escenario 3 (>= 365 días):     {len(escenario3)} terceros")
    print(f"  ⚠️  Sin fecha actualización:      {len(sin_fecha)} terceros")
    print("=" * 100)
    
    # Sugerencias
    print("\n💡 SUGERENCIAS DE PRUEBA:")
    print("-" * 100)
    
    if escenario1:
        print(f"1️⃣  Para probar REGISTRO NORMAL (verde):      USA NIT {escenario1[0][0]}")
    
    if escenario2:
        print(f"2️⃣  Para probar ADVERTENCIA (naranja):        USA NIT {escenario2[0][0]}")
    elif escenario1:
        # Sugerir modificar uno del escenario 1
        print(f"2️⃣  Para probar ADVERTENCIA (naranja):        MODIFICA {escenario1[-1][0]} con comando:")
        print(f"    UPDATE terceros SET fecha_actualizacion = CURRENT_DATE - INTERVAL '340 days' WHERE nit = '{escenario1[-1][0]}';")
    
    if escenario3:
        print(f"3️⃣  Para probar BLOQUEO (rojo):               USA NIT {escenario3[0][0]}")
    elif escenario1:
        # Sugerir modificar uno del escenario 1
        print(f"3️⃣  Para probar BLOQUEO (rojo):               MODIFICA {escenario1[-1][0] if len(escenario1) > 1 else escenario1[0][0]} con comando:")
        print(f"    UPDATE terceros SET fecha_actualizacion = CURRENT_DATE - INTERVAL '400 days' WHERE nit = '{escenario1[-1][0] if len(escenario1) > 1 else escenario1[0][0]}';")
    
    print("=" * 100)

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
