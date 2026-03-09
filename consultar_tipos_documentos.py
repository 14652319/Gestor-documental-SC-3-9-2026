# -*- coding: utf-8 -*-
"""
Script para consultar la tabla tipos_documentos_dian directamente
"""
import sys
import os

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from modules.dian_vs_erp.models import TipoDocumentoDian
from app import app

def consultar_tipos():
    with app.app_context():
        try:
            print("=" * 80)
            print("📊 TABLA tipos_documentos_dian - ESTADO ACTUAL")
            print("=" * 80)
            
            # Contar registros
            total = TipoDocumentoDian.query.count()
            print(f"\nTotal de registros: {total}")
            
            if total == 0:
                print("\n⚠️  ¡LA TABLA ESTÁ VACÍA!")
                print("\nEsto explica por qué el visor V2 no muestra NADA.")
                print("El JOIN con esta tabla falla porque no hay registros.")
                
                print("\n💡 INSERTANDO 'Factura Electrónica'...")
                nuevo = TipoDocumentoDian(
                    tipo_documento="Factura Electrónica",
                    procesar_frontend=True,
                    activo=True
                )
                db.session.add(nuevo)
                db.session.commit()
                print("   ✅ Insertado correctamente")
            else:
                print(f"\n📋 REGISTROS:\n")
                print(f"{'ID':<5} {'Tipo Documento':<50} {'Frontend':<12} {'Activo':<8}")
                print("-" * 80)
                
                tipos = TipoDocumentoDian.query.all()
                for t in tipos:
                    procesar = "✅ SÍ" if t.procesar_frontend else "❌ NO"
                    activo = "✅ SÍ" if t.activo else "❌ NO"
                    print(f"{t.id:<5} {t.tipo_documento:<50} {procesar:<12} {activo:<8}")
                
                # Buscar específicamente "Factura Electrónica"
                factura = TipoDocumentoDian.query.filter_by(tipo_documento="Factura Electrónica").first()
                
                print(f"\n🔍 Búsqueda de 'Factura Electrónica':")
                if factura:
                    print(f"   ✅ ENCONTRADA:")
                    print(f"      ID: {factura.id}")
                    print(f"      procesar_frontend: {factura.procesar_frontend}")
                    print(f"      activo: {factura.activo}")
                    
                    if not factura.procesar_frontend or not factura.activo:
                        print(f"\n   ⚠️  ESTÁ DESACTIVADA - Activando...")
                        factura.procesar_frontend = True
                        factura.activo = True
                        db.session.commit()
                        print(f"   ✅ Activada")
                else:
                    print(f"   ❌ NO ENCONTRADA")
                    print(f"\n   💡 Insertando...")
                    nuevo = TipoDocumentoDian(
                        tipo_documento="Factura Electrónica",
                        procesar_frontend=True,
                        activo=True
                    )
                    db.session.add(nuevo)
                    db.session.commit()
                    print(f"   ✅ Insertada correctamente")
            
            print("\n" + "=" * 80)
            print("✅ Verificación completada")
            print("=" * 80)
            
            print("\n💡 AHORA PRUEBA:")
            print("   1. Abre el visor: http://localhost:8099/dian_vs_erp/visor_v2")
            print("   2. Presiona Ctrl+F5 para forzar recarga")
            print("   3. Cambia las fechas a: 01/02/2026 - 28/02/2026")
            print("   4. Click en 'Buscar'")
            print("   5. Deberían aparecer los 104 registros de febrero")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    consultar_tipos()
