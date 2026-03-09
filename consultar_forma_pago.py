"""Script para consultar valores de forma_pago en AMBAS tablas"""
from extensions import db
from modules.dian_vs_erp.models import Dian, MaestroDianVsErp
from app import app

app_context = app.app_context()
app_context.push()

# Tabla dian
result_dian = db.session.query(Dian.forma_pago, db.func.count(Dian.id)).group_by(Dian.forma_pago).order_by(db.func.count(Dian.id).desc()).all()

# Tabla maestro
result_maestro = db.session.query(MaestroDianVsErp.forma_pago, db.func.count(MaestroDianVsErp.id)).group_by(MaestroDianVsErp.forma_pago).order_by(db.func.count(MaestroDianVsErp.id).desc()).all()

print('\n' + '='*70)
print('COMPARACIÓN: TABLA dian VS maestro_dian_vs_erp')
print('='*70)

print('\n📋 TABLA DIAN (origen):')
print('-'*70)
total_dian = sum(r[1] for r in result_dian)
for fp, count in result_dian:
    valor = fp if fp else '(null)'
    pct = (count / total_dian * 100) if total_dian > 0 else 0
    print(f'  {valor:20} | {count:>8,} registros ({pct:>5.2f}%)')
print(f'  {"TOTAL":20} | {total_dian:>8,} registros')

print('\n📊 TABLA MAESTRO_DIAN_VS_ERP (consolidado):')
print('-'*70)
total_maestro = sum(r[1] for r in result_maestro)
for fp, count in result_maestro:
    valor = fp if fp else '(null)'
    pct = (count / total_maestro * 100) if total_maestro > 0 else 0
    print(f'  {valor:20} | {count:>8,} registros ({pct:>5.2f}%)')
print(f'  {"TOTAL":20} | {total_maestro:>8,} registros')

print('\n🔍 DIAGNÓSTICO:')
if total_dian == total_maestro:
    print('  ✅ Cantidades coinciden entre tablas')
else:
    print(f'  ⚠️ Desincronización: dian={total_dian:,} vs maestro={total_maestro:,}')

# Verificar si maestro tiene los valores correctos
dian_valores = set(r[0] for r in result_dian)
maestro_valores = set(r[0] for r in result_maestro)

if dian_valores == maestro_valores:
    print('  ✅ Valores de forma_pago coinciden en ambas tablas')
else:
    print(f'  ⚠️ Valores diferentes:')
    print(f'     - Solo en dian: {dian_valores - maestro_valores}')
    print(f'     - Solo en maestro: {maestro_valores - dian_valores}')

print('='*70)
print()
