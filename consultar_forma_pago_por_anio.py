from extensions import db
from modules.dian_vs_erp.models import Dian
from sqlalchemy import func, extract
from app import app

app_context = app.app_context()
app_context.push()

# Consultar por año y forma_pago
result = db.session.query(
    extract('year', Dian.fecha_emision).label('anio'),
    Dian.forma_pago,
    func.count(Dian.id).label('cantidad')
).filter(
    Dian.fecha_emision.isnot(None)
).group_by(
    extract('year', Dian.fecha_emision),
    Dian.forma_pago
).order_by(
    extract('year', Dian.fecha_emision).desc(),
    func.count(Dian.id).desc()
).all()

# Escribir a archivo y consola
output = []
output.append('='*80)
output.append('DISTRIBUCIÓN DE forma_pago POR AÑO')
output.append('='*80)

anio_actual = None
for anio, fp, count in result:
    if anio != anio_actual:
        if anio_actual is not None:
            output.append('-'*80)
        anio_actual = anio
        output.append(f'\n📅 AÑO {int(anio) if anio else "NULL"}:')
    
    valor = fp if fp else '(null)'
    line = f'   {valor}: {count:,} registros'
    output.append(line)
    print(line)

output.append('='*80)

# Totales por año
output.append('\n📊 TOTALES POR AÑO:')
totales = db.session.query(
    extract('year', Dian.fecha_emision).label('anio'),
    func.count(Dian.id).label('total')
).filter(
    Dian.fecha_emision.isnot(None)
).group_by(
    extract('year', Dian.fecha_emision)
).order_by(
    extract('year', Dian.fecha_emision).desc()
).all()

for anio, total in totales:
    line = f'   {int(anio) if anio else "NULL"}: {total:,} facturas'
    output.append(line)
    print(line)

output.append('='*80)

# Guardar a archivo
with open('resultado_forma_pago_por_anio.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('\n✅ Resultados guardados en resultado_forma_pago_por_anio.txt')
