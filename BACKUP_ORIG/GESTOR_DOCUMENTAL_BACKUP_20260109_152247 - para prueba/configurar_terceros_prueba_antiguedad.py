"""
Script para configurar terceros de PRUEBA con diferentes antigüedades
Esto te permitirá probar los 3 escenarios de validación
"""
from datetime import date, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:GestorDoc2024!@localhost:5432/gestor_documental')

try:
    engine = create_engine(DATABASE_URL)
    
    print("=" * 100)
    print("🔧 CONFIGURANDO TERCEROS DE PRUEBA PARA VALIDACIÓN DE ANTIGÜEDAD")
    print("=" * 100)
    print()
    
    # Obtener 3 terceros para usar como prueba (los primeros con estado activo)
    query_terceros = text("""
        SELECT nit, razon_social 
        FROM terceros 
        WHERE estado = 'activo' 
        LIMIT 3
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query_terceros)
        terceros = result.fetchall()
    
    if len(terceros) < 3:
        print("❌ ERROR: Se necesitan al menos 3 terceros con estado 'activo'")
        print("   Ejecuta primero: activar_admin.py para activar terceros")
        exit(1)
    
    # Calcular fechas para cada escenario
    hoy = date.today()
    
    # Escenario 1: ACTUALIZADO (< 330 días) - 120 días atrás
    fecha_escenario1 = hoy - timedelta(days=120)
    
    # Escenario 2: POR VENCER (330-364 días) - 340 días atrás
    fecha_escenario2 = hoy - timedelta(days=340)
    
    # Escenario 3: VENCIDO (>= 365 días) - 400 días atrás
    fecha_escenario3 = hoy - timedelta(days=400)
    
    print("📅 FECHAS CALCULADAS:")
    print(f"  Hoy:              {hoy.strftime('%d/%m/%Y')}")
    print(f"  Escenario 1:      {fecha_escenario1.strftime('%d/%m/%Y')} ({120} días atrás)")
    print(f"  Escenario 2:      {fecha_escenario2.strftime('%d/%m/%Y')} ({340} días atrás)")
    print(f"  Escenario 3:      {fecha_escenario3.strftime('%d/%m/%Y')} ({400} días atrás)")
    print()
    
    # Actualizar los 3 terceros
    with engine.begin() as conn:
        # Escenario 1: Verde ✅
        nit1, razon1 = terceros[0]
        conn.execute(
            text("UPDATE terceros SET fecha_actualizacion = :fecha WHERE nit = :nit"),
            {"fecha": fecha_escenario1, "nit": nit1}
        )
        print(f"✅ ESCENARIO 1 (VERDE - ACTUALIZADO):")
        print(f"   NIT: {nit1}")
        print(f"   Razón Social: {razon1}")
        print(f"   Fecha actualización: {fecha_escenario1.strftime('%d/%m/%Y')} (120 días)")
        print(f"   💡 USA ESTE NIT para probar registro NORMAL sin restricciones")
        print()
        
        # Escenario 2: Naranja ⚠️
        nit2, razon2 = terceros[1]
        conn.execute(
            text("UPDATE terceros SET fecha_actualizacion = :fecha WHERE nit = :nit"),
            {"fecha": fecha_escenario2, "nit": nit2}
        )
        print(f"⚠️  ESCENARIO 2 (NARANJA - POR VENCER):")
        print(f"   NIT: {nit2}")
        print(f"   Razón Social: {razon2}")
        print(f"   Fecha actualización: {fecha_escenario2.strftime('%d/%m/%Y')} (340 días)")
        print(f"   💡 USA ESTE NIT para probar ADVERTENCIA (quedan 25 días)")
        print()
        
        # Escenario 3: Rojo ❌
        nit3, razon3 = terceros[2]
        conn.execute(
            text("UPDATE terceros SET fecha_actualizacion = :fecha WHERE nit = :nit"),
            {"fecha": fecha_escenario3, "nit": nit3}
        )
        print(f"❌ ESCENARIO 3 (ROJO - VENCIDO):")
        print(f"   NIT: {nit3}")
        print(f"   Razón Social: {razon3}")
        print(f"   Fecha actualización: {fecha_escenario3.strftime('%d/%m/%Y')} (400 días)")
        print(f"   💡 USA ESTE NIT para probar BLOQUEO (botón Adicionar deshabilitado)")
        print()
    
    print("=" * 100)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 100)
    print()
    print("🧪 AHORA PUEDES PROBAR:")
    print("-" * 100)
    print(f"1️⃣  Ve a /recibir_facturas/nueva_factura")
    print(f"2️⃣  Ingresa NIT {nit1} → Verás mensaje VERDE con fecha y días")
    print(f"3️⃣  Ingresa NIT {nit2} → Verás mensaje NARANJA con advertencia")
    print(f"4️⃣  Ingresa NIT {nit3} → Verás mensaje ROJO y botón BLOQUEADO")
    print("=" * 100)
    print()
    print("💾 COMANDOS SQL EJECUTADOS:")
    print("-" * 100)
    print(f"UPDATE terceros SET fecha_actualizacion = '{fecha_escenario1}' WHERE nit = '{nit1}';")
    print(f"UPDATE terceros SET fecha_actualizacion = '{fecha_escenario2}' WHERE nit = '{nit2}';")
    print(f"UPDATE terceros SET fecha_actualizacion = '{fecha_escenario3}' WHERE nit = '{nit3}';")
    print("=" * 100)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
