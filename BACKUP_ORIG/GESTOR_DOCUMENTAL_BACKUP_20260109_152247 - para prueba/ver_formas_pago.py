from app import app, db
from modules.dian_vs_erp.models import MaestroDianVsErp

with app.app_context():
    print("\n" + "="*60)
    print("FORMAS DE PAGO EN LA BASE DE DATOS")
    print("="*60 + "\n")
    
    # Obtener todas las formas de pago distintas
    query = """
        SELECT DISTINCT forma_pago, COUNT(*) as cantidad
        FROM maestro_dian_vs_erp 
        WHERE forma_pago IS NOT NULL 
        GROUP BY forma_pago
        ORDER BY cantidad DESC
        LIMIT 30
    """
    result = db.session.execute(db.text(query))
    formas_pago = result.fetchall()
    
    if formas_pago:
        print(f"Total de formas de pago distintas: {len(formas_pago)}\n")
        for i, (forma, cantidad) in enumerate(formas_pago, 1):
            print(f"{i}. '{forma}' - {cantidad} documentos")
    else:
        print("⚠️ No se encontraron formas de pago en la tabla")
    
    print("\n" + "="*60 + "\n")
