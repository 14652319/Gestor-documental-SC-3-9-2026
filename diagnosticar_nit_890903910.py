"""
Script para diagnosticar por qué el NIT 890903910 aparece como NO REGISTRADO
"""
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gestor_user:GestorDoc2024!@localhost:5432/gestor_documental')

try:
    engine = create_engine(DATABASE_URL)
    nit = '890903910'
    
    print("=" * 100)
    print(f"🔍 DIAGNÓSTICO COMPLETO DEL NIT: {nit}")
    print("=" * 100)
    print()
    
    # 1. Verificar si existe en tabla terceros
    query1 = text("SELECT nit, razon_social, estado, fecha_actualizacion FROM terceros WHERE nit = :nit")
    
    with engine.connect() as conn:
        result = conn.execute(query1, {"nit": nit})
        tercero = result.fetchone()
    
    if tercero:
        print("✅ TERCERO ENCONTRADO EN TABLA 'terceros':")
        print(f"  NIT:                  {tercero[0]}")
        print(f"  Razón Social:         {tercero[1]}")
        print(f"  Estado:               {tercero[2]}")
        print(f"  Fecha Actualización:  {tercero[3]}")
        print()
        
        if tercero[2] != 'activo':
            print("⚠️  PROBLEMA DETECTADO:")
            print(f"  El estado es '{tercero[2]}' pero debería ser 'activo'")
            print()
            print("💡 SOLUCIÓN:")
            print(f"  UPDATE terceros SET estado = 'activo' WHERE nit = '{nit}';")
            print()
    else:
        print("❌ TERCERO NO ENCONTRADO EN TABLA 'terceros'")
        print()
        print("💡 POSIBLES CAUSAS:")
        print("  1. El NIT no existe en la base de datos")
        print("  2. El NIT está escrito con espacios o caracteres especiales")
        print()
        
        # Buscar NITs similares
        query2 = text("SELECT nit, razon_social FROM terceros WHERE nit LIKE :nit_pattern LIMIT 5")
        with engine.connect() as conn:
            result = conn.execute(query2, {"nit_pattern": f"%{nit[-6:]}%"})
            similares = result.fetchall()
        
        if similares:
            print("🔎 NITs SIMILARES ENCONTRADOS:")
            for nit_sim, razon in similares:
                print(f"  {nit_sim:15} | {razon}")
            print()
    
    # 2. Verificar qué hace el endpoint /api/registro/check_nit
    print("-" * 100)
    print("📍 ENDPOINT QUE USA EL FRONTEND:")
    print("  Ruta:    /api/registro/check_nit")
    print("  Método:  POST")
    print("  Busca:   Tercero.query.filter_by(nit=nit).first()")
    print("  Retorna: {'exists': True/False, 'tercero': {...}}")
    print("-" * 100)
    print()
    
    # 3. Simular lo que hace el endpoint
    print("🧪 SIMULACIÓN DEL ENDPOINT:")
    query3 = text("SELECT COUNT(*) FROM terceros WHERE nit = :nit")
    with engine.connect() as conn:
        result = conn.execute(query3, {"nit": nit})
        count = result.scalar()
    
    if count > 0:
        print(f"  ✅ El endpoint DEBERÍA retornar: {{'exists': True}}")
    else:
        print(f"  ❌ El endpoint retorna: {{'exists': False}}")
        print("     Por eso aparece: '❌ NIT NO REGISTRADO'")
    
    print()
    print("=" * 100)

except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
