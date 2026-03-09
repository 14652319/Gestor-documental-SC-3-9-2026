"""
TEST: Verificar estados contables en base de datos
Objetivo: Ver cuántos registros tienen cada estado según la lógica de cálculo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from modules.dian_vs_erp.models import (
    Dian, Acuses, ErpFinanciero, ErpComercial,
    FacturaTemporal, FacturaRecibida, FacturaDigital,
    TipoTerceroDianErp
)

def test_estados_contables():
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 TEST: ANÁLISIS DE ESTADOS CONTABLES")
        print("="*80)
        
        # Query igual que en /api/generar_reporte_dinamico
        query = db.session.query(
            Dian,
            Acuses.estado_docto.label('estado_acuse'),
            ErpFinanciero.id.label('existe_financiero'),
            ErpComercial.id.label('existe_comercial'),
            FacturaTemporal.id.label('existe_temporal'),
            FacturaRecibida.id.label('existe_recibida'),
            FacturaDigital.id.label('existe_digital')
        ).outerjoin(
            Acuses,
            (Dian.nit_emisor == Acuses.nit_emisor) &
            (Dian.prefijo == Acuses.prefijo) &
            (Dian.folio == Acuses.folio)
        ).outerjoin(
            ErpFinanciero,
            (Dian.nit_emisor == ErpFinanciero.nit_emisor) &
            (Dian.prefijo == ErpFinanciero.prefijo) &
            (Dian.folio == ErpFinanciero.folio)
        ).outerjoin(
            ErpComercial,
            (Dian.nit_emisor == ErpComercial.nit_emisor) &
            (Dian.prefijo == ErpComercial.prefijo) &
            (Dian.folio == ErpComercial.folio)
        ).outerjoin(
            FacturaTemporal,
            (Dian.nit_emisor == FacturaTemporal.nit_emisor) &
            (Dian.prefijo == FacturaTemporal.prefijo) &
            (Dian.folio == FacturaTemporal.folio)
        ).outerjoin(
            FacturaRecibida,
            (Dian.nit_emisor == FacturaRecibida.nit_emisor) &
            (Dian.prefijo == FacturaRecibida.prefijo) &
            (Dian.folio == FacturaRecibida.folio)
        ).outerjoin(
            FacturaDigital,
            (Dian.nit_emisor == FacturaDigital.nit_emisor) &
            (Dian.prefijo == FacturaDigital.prefijo) &
            (Dian.folio == FacturaDigital.folio)
        )
        
        # Aplicar filtro de fechas (igual que el reporte)
        from datetime import datetime
        fecha_inicio = datetime.strptime('2026-01-01', '%Y-%m-%d').date()
        fecha_fin = datetime.strptime('2026-03-02', '%Y-%m-%d').date()
        
        query = query.filter(Dian.fecha_emision >= fecha_inicio)
        query = query.filter(Dian.fecha_emision <= fecha_fin)
        
        print(f"\n📅 Filtro aplicado: {fecha_inicio} a {fecha_fin}")
        print(f"⏳ Ejecutando query...")
        
        resultados = query.all()
        print(f"✅ {len(resultados):,} registros recuperados de la BD")
        
        # Calcular estados según la lógica del backend
        estados = {
            'Causada': 0,
            'Recibida': 0,
            'No Registrada': 0
        }
        
        muestras_no_registrada = []
        
        for i, row in enumerate(resultados):
            registro = row[0]
            existe_financiero = row[2]
            existe_comercial = row[3]
            existe_temporal = row[4]
            existe_recibida = row[5]
            existe_digital = row[6]
            
            if existe_financiero or existe_comercial:
                estado = "Causada"
            elif existe_recibida or existe_temporal or existe_digital:
                estado = "Recibida"
            else:
                estado = "No Registrada"
                if len(muestras_no_registrada) < 5:
                    muestras_no_registrada.append({
                        'nit': registro.nit_emisor,
                        'prefijo': registro.prefijo,
                        'folio': registro.folio,
                        'fecha': registro.fecha_emision
                    })
            
            estados[estado] += 1
        
        print(f"\n📊 DISTRIBUCIÓN DE ESTADOS CONTABLES:")
        for estado, cantidad in estados.items():
            porcentaje = (cantidad / len(resultados) * 100) if len(resultados) > 0 else 0
            print(f"   • {estado}: {cantidad:,} ({porcentaje:.1f}%)")
        
        if muestras_no_registrada:
            print(f"\n📋 MUESTRA DE REGISTROS 'No Registrada' (primeros 5):")
            for i, muestra in enumerate(muestras_no_registrada, 1):
                print(f"   {i}. NIT={muestra['nit']}, Prefijo={muestra['prefijo']}, Folio={muestra['folio']}, Fecha={muestra['fecha']}")
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETADO")
        print("="*80)

if __name__ == '__main__':
    test_estados_contables()
