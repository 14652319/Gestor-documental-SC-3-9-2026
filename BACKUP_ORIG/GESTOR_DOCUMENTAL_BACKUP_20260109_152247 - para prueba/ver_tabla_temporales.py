"""
Script para ver contenido de facturas_temporales
"""
from extensions import db
from flask import Flask
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Inicio2024*@localhost/gestor_documental'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("\n" + "=" * 180)
    print("CONTENIDO DE TABLA facturas_temporales (ULTIMAS 15 FACTURAS)")
    print("=" * 180)
    
    query = """
        SELECT 
            id,
            nit,
            razon_social,
            prefijo,
            folio,
            empresa_id,
            centro_operacion_id,
            valor_neto,
            fecha_radicacion::TEXT,
            usuario_nombre
        FROM facturas_temporales 
        ORDER BY id DESC 
        LIMIT 15
    """
    
    result = db.session.execute(text(query)).fetchall()
    
    # Header
    print(f"{'ID':<5} | {'NIT':<12} | {'Razón Social':<25} | {'Pref':<5} | {'Folio':<8} | {'Empresa':<8} | {'CO_ID':<6} | {'Valor Neto':<12} | {'Fecha Rad':<12} | {'Usuario':<15}")
    print("=" * 180)
    
    if not result:
        print("NO HAY FACTURAS EN LA TABLA")
    else:
        for row in result:
            empresa_val = row[5] if row[5] else 'NULL'
            print(f"{row[0]:<5} | {row[1]:<12} | {row[2]:<25} | {row[3]:<5} | {row[4]:<8} | {empresa_val:<8} | {row[6]:<6} | {row[7]:<12} | {row[8]:<12} | {row[9]:<15}")
    
    print("=" * 180)
    
    # Estadisticas
    stats = db.session.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(empresa_id) as con_empresa,
            COUNT(*) - COUNT(empresa_id) as sin_empresa,
            COUNT(DISTINCT empresa_id) as empresas_distintas
        FROM facturas_temporales
    """)).fetchone()
    
    print(f"\nESTADISTICAS:")
    print(f"   Total facturas: {stats[0]}")
    print(f"   Con empresa_id: {stats[1]}")
    print(f"   Sin empresa_id (NULL): {stats[2]}")
    print(f"   Empresas distintas: {stats[3]}")
    
    # Ver que empresas hay
    if stats[1] > 0:
        empresas = db.session.execute(text("""
            SELECT empresa_id, COUNT(*) as cantidad
            FROM facturas_temporales
            WHERE empresa_id IS NOT NULL
            GROUP BY empresa_id
            ORDER BY cantidad DESC
        """)).fetchall()
        
        print(f"\nDISTRIBUCION POR EMPRESA:")
        for emp in empresas:
            print(f"   {emp[0]}: {emp[1]} facturas")
    
    print("\n")
