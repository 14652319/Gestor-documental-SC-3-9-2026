from extensions import db
from modules.dian_vs_erp.models import MaestroDianVsErp
from sqlalchemy import func, extract
from app import app

app_context = app.app_context()
app_context.push()

# Consultar por año y forma_pago en maestro
result = db.session.query(
    extract('year', MaestroDianVsErp.fecha_emision).label('anio'),
    MaestroDianVsErp.forma_pago,
    func.count(MaestroDianVsErp.id).label('cantidad')
).filter(
    MaestroDianVsErp.fecha_emision.isnot(None)
).group_by(
    extract('year', MaestroDianVsErp.fecha_emision),
    MaestroDianVsErp.forma_pago
).order_by(
    extract('year', MaestroDianVsErp.fecha_emision).desc(),
    func.count(MaestroDianVsErp.id).desc()
).all()

# Escribir resultados
output = []
output.append('='*80)
output.append('TABLA maestro_dian_vs_erp - DISTRIBUCIÓN DE forma_pago POR AÑO')
output.append('='*80)

anio_actual = None
totales_anio = {}
for anio, fp, count in result:
    anio_int = int(anio) if anio else None
    
    if anio != anio_actual:
        anio_actual = anio
        output.append(f'\n📅 AÑO {anio_int if anio_int else "NULL"}:')
    
    valor = fp if fp else '(null)'
    # Agregar etiqueta según valor
    if fp == "1" or fp == "01":
        etiqueta = "→ Contado"
    elif fp == "2" or fp == "02":
        etiqueta = "→ Crédito"
    else:
        etiqueta = ""
    
    line = f'   {valor}: {count:,} registros {etiqueta}'
    output.append(line)
    print(line)
    
    # Sumar totales por año
    if anio_int not in totales_anio:
        totales_anio[anio_int] = 0
    totales_anio[anio_int] += count

output.append('\n' + '='*80)
output.append('📊 TOTALES POR AÑO:')
for anio in sorted(totales_anio.keys(), reverse=True):
    line = f'   {anio}: {totales_anio[anio]:,} facturas'
    output.append(line)
    print(line)

output.append('='*80)

# Guardar a archivo
with open('resultado_maestro_forma_pago_por_anio.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('\n✅ Resultados guardados en resultado_maestro_forma_pago_por_anio.txt')
