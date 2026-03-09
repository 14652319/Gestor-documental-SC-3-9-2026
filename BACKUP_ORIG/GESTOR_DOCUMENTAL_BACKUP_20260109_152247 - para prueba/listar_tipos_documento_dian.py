"""
Script para listar todos los tipos de documentos únicos en la tabla DIAN
"""
from extensions import db
from modules.dian_vs_erp.models import Dian
from sqlalchemy import func
from app import app

def listar_tipos_documento():
    with app.app_context():
        print("\n" + "="*80)
        print("📄 TIPOS DE DOCUMENTOS EN TABLA DIAN")
        print("="*80 + "\n")
        
        # Consultar tipos de documento únicos con conteo
        resultados = db.session.query(
            Dian.tipo_documento,
            func.count(Dian.id).label('cantidad')
        ).filter(
            Dian.tipo_documento != None,
            Dian.tipo_documento != ''
        ).group_by(
            Dian.tipo_documento
        ).order_by(
            func.count(Dian.id).desc()
        ).all()
        
        # Mostrar resultados
        print(f"{'TIPO DE DOCUMENTO':<60} {'CANTIDAD':>15}")
        print("-" * 80)
        
        total = 0
        for tipo, cantidad in resultados:
            print(f"{tipo:<60} {cantidad:>15,}")
            total += cantidad
        
        print("-" * 80)
        print(f"{'TOTAL DE DOCUMENTOS':<60} {total:>15,}")
        print("\n" + "="*80)
        print(f"✅ Se encontraron {len(resultados)} tipos de documentos diferentes")
        print("="*80 + "\n")

if __name__ == '__main__':
    listar_tipos_documento()
