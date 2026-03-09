"""
🔄 Script para LIMPIAR radicados RFD de facturas (para poder probar de nuevo)

Este script:
1. Busca facturas con radicado RFD-000002 (el que se generó para las 2 facturas)
2. Limpia el campo radicado_rfd (lo pone en NULL)
3. Permite volver a probar el endpoint de finalizar lote

USO:
    python limpiar_radicados_para_prueba.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from modules.facturas_digitales.models import FacturaDigital

def main():
    with app.app_context():
        print("\n" + "="*70)
        print("🔄 LIMPIEZA DE RADICADOS RFD PARA PRUEBAS")
        print("="*70)
        
        # Aceptar argumentos de línea de comandos
        if len(sys.argv) > 1:
            opcion = sys.argv[1]
            print(f"\n[MODO AUTOMÁTICO] Opción seleccionada: {opcion}")
        else:
            # Modo interactivo
            print("\nOpciones:")
            print("  1. Limpiar RFD-000002 (las 2 facturas del usuario externo)")
            print("  2. Limpiar TODOS los radicados de un usuario específico")
            print("  3. Limpiar radicado específico")
            
            opcion = input("\nElige opción (1/2/3): ").strip()
        
        if opcion == '1':
            radicado_target = 'RFD-000002'
            facturas = FacturaDigital.query.filter_by(radicado_rfd=radicado_target).all()
            
            if not facturas:
                print(f"\n❌ No hay facturas con radicado {radicado_target}")
                return
            
            print(f"\n📋 Encontradas {len(facturas)} factura(s) con {radicado_target}:")
            for idx, factura in enumerate(facturas, start=1):
                print(f"  {idx}. ID:{factura.id} | {factura.numero_factura} | {factura.razon_social_proveedor} | ${factura.valor_total:,.2f}")
            
            respuesta = input(f"\n¿Limpiar radicado de estas {len(facturas)} factura(s)? (S/N): ").strip().upper()
            if respuesta == 'S':
                for factura in facturas:
                    print(f"  🔄 Limpiando {factura.numero_factura}...")
                    factura.radicado_rfd = None
                
                db.session.commit()
                print(f"\n✅ Se limpiaron {len(facturas)} factura(s)")
                print("✅ Ahora puedes ejecutar: python probar_finalizar_lote.py")
            else:
                print("❌ Operación cancelada")
        
        elif opcion == '2':
            # Aceptar usuario de línea de comandos
            if len(sys.argv) > 2:
                usuario = sys.argv[2]
                print(f"\n[MODO AUTOMÁTICO] Usuario: {usuario}")
                auto_confirmar = True
            else:
                usuario = input("\nIngresa el usuario (ej: 14652319): ").strip()
                auto_confirmar = False
            
            facturas = FacturaDigital.query.filter(
                FacturaDigital.usuario_carga == usuario,
                FacturaDigital.radicado_rfd.isnot(None)
            ).all()
            
            if not facturas:
                print(f"\n❌ No hay facturas con radicado del usuario {usuario}")
                return
            
            print(f"\n📋 Encontradas {len(facturas)} factura(s) con radicado del usuario {usuario}:")
            for idx, factura in enumerate(facturas, start=1):
                print(f"  {idx}. {factura.radicado_rfd} | {factura.numero_factura} | ${factura.valor_total:,.2f}")
            
            if auto_confirmar:
                respuesta = 'S'
                print(f"\n[MODO AUTOMÁTICO] Limpiando automáticamente...")
            else:
                respuesta = input(f"\n¿Limpiar radicado de estas {len(facturas)} factura(s)? (S/N): ").strip().upper()
            
            if respuesta == 'S':
                for factura in facturas:
                    print(f"  🔄 Limpiando {factura.numero_factura} (era {factura.radicado_rfd})...")
                    factura.radicado_rfd = None
                
                db.session.commit()
                print(f"\n✅ Se limpiaron {len(facturas)} factura(s)")
            else:
                print("❌ Operación cancelada")
        
        elif opcion == '3':
            radicado = input("\nIngresa el radicado (ej: RFD-000003): ").strip().upper()
            
            facturas = FacturaDigital.query.filter_by(radicado_rfd=radicado).all()
            
            if not facturas:
                print(f"\n❌ No hay facturas con radicado {radicado}")
                return
            
            print(f"\n📋 Encontradas {len(facturas)} factura(s) con {radicado}:")
            for idx, factura in enumerate(facturas, start=1):
                print(f"  {idx}. ID:{factura.id} | {factura.numero_factura} | {factura.razon_social_proveedor}")
            
            respuesta = input(f"\n¿Limpiar radicado de estas {len(facturas)} factura(s)? (S/N): ").strip().upper()
            if respuesta == 'S':
                for factura in facturas:
                    factura.radicado_rfd = None
                
                db.session.commit()
                print(f"\n✅ Se limpiaron {len(facturas)} factura(s)")
            else:
                print("❌ Operación cancelada")
        
        else:
            print("❌ Opción inválida")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
