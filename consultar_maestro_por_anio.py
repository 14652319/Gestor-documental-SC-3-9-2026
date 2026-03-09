from extensions import db
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import func, extract
from app import app

app_context = app.app_context()
app_context.push()

# Consultar distribución por año en maestro_dian_vs_erp
result = db.session.query(
    extract('year', MaestroDianVsErp.fecha_emision).label('anio'),
    func.count(MaestroDianVsErp.id).label('cantidad')
).group_by(
    extract('year', MaestroDianVsErp.fecha_emision)
).order_by(
    extract('year', MaestroDianVsErp.fecha_emision).desc()
).all()

print('='*60)
print('TABLA maestro_dian_vs_erp - DISTRIBUCIÓN POR AÑO')
print('='*60)
total = 0
for anio, count in result:
    anio_str = int(anio) if anio else 'NULL'
    print(f'{anio_str}: {count:,} registros')
    total += count
print('-'*60)
print(f'TOTAL: {total:,} registros')
print('='*60)
