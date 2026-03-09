"""
Script para verificar campos de trazabilidad en facturas_digitales
"""
from extensions import db
from app import app
from sqlalchemy import text

with app.app_context():
    print("\n🔍 VERIFICANDO TRAZABILIDAD DE FACTURAS\n")
    print("=" * 80)
    
    query = text("""
        SELECT 
            id,
            numero_factura,
            estado,
            fecha_envio_firma,
            usuario_envio_firma,
            fecha_firmado,
            usuario_firmador
        FROM facturas_digitales
        WHERE estado IN ('enviado_a_firmar', 'firmada')
        ORDER BY id DESC
        LIMIT 10
    """)
    
    result = db.session.execute(query)
    facturas = result.fetchall()
    
    if not facturas:
        print("❌ No hay facturas con estado 'enviado_a_firmar' o 'firmada'")
    else:
        print(f"✅ Encontradas {len(facturas)} facturas\n")
        
        for f in facturas:
            print(f"📄 ID: {f[0]} | Número: {f[1]}")
            print(f"   Estado: {f[2]}")
            print(f"   📤 Fecha envío: {f[3] if f[3] else 'NO GUARDADA ❌'}")
            print(f"   👤 Usuario envío: {f[4] if f[4] else 'NO GUARDADO ❌'}")
            print(f"   ✅ Fecha firmado: {f[5] if f[5] else 'Pendiente'}")
            print(f"   👤 Usuario firmador: {f[6] if f[6] else 'Pendiente'}")
            print("-" * 80)
    
    print("\n✅ Verificación completa\n")
