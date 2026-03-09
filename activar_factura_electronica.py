# -*- coding: utf-8 -*-
"""
Script para ver y activar tipos de documentos DIAN
"""
import sys
import os

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from extensions import db
from modules.dian_vs_erp.models import TipoDocumentoDian
from app import app

def verificar_y_activar_tipos():
    with app.app_context():
        try:
            print("=" * 80)
            print("📊 CONFIGURACIÓN ACTUAL DE TIPOS DE DOCUMENTOS DIAN")
            print("=" * 80)
            
            # Ver todos los tipos
            tipos = TipoDocumentoDian.query.all()
            
            if not tipos:
                print("\n⚠️  LA TABLA ESTÁ VACÍA")
                print("\n💡 Creando tipo 'Factura Electrónica'...")
                nuevo_tipo = TipoDocumentoDian(
                    tipo_documento="Factura Electrónica",
                    procesar_frontend=True,
                    activo=True
                )
                db.session.add(nuevo_tipo)
                db.session.commit()
                print("   ✅ 'Factura Electrónica' creada y activada")
            else:
                print(f"\n📋 TIPOS REGISTRADOS ({len(tipos)}):\n")
                print(f"{'ID':<5} {'Tipo Documento':<40} {'Frontend':<12} {'Activo':<8}")
                print("-" * 70)
                
                for t in tipos:
                    procesar_str = "✅ SÍ" if t.procesar_frontend else "❌ NO"
                    activo_str = "✅ SÍ" if t.activo else "❌ NO"
                    print(f"{t.id:<5} {t.tipo_documento:<40} {procesar_str:<12} {activo_str:<8}")
                
                # Buscar "Factura Electrónica"
                factura_elec = TipoDocumentoDian.query.filter_by(tipo_documento="Factura Electrónica").first()
                
                if not factura_elec:
                    print("\n⚠️  'Factura Electrónica' NO ESTÁ REGISTRADA")
                    print("\n💡 Creando tipo 'Factura Electrónica'...")
                    nuevo_tipo = TipoDocumentoDian(
                        tipo_documento="Factura Electrónica",
                        procesar_frontend=True,
                        activo=True
                    )
                    db.session.add(nuevo_tipo)
                    db.session.commit()
                    print("   ✅ 'Factura Electrónica' creada y activada")
                elif not factura_elec.procesar_frontend or not factura_elec.activo:
                    print(f"\n⚠️  'Factura Electrónica' ESTÁ DESACTIVADA:")
                    print(f"    procesar_frontend: {factura_elec.procesar_frontend}")
                    print(f"    activo: {factura_elec.activo}")
                    print("\n💡 Activando 'Factura Electrónica'...")
                    factura_elec.procesar_frontend = True
                    factura_elec.activo = True
                    db.session.commit()
                    print("   ✅ 'Factura Electrónica' activada correctamente")
                else:
                    print("\n✅ 'Factura Electrónica' YA ESTÁ ACTIVADA")
                    print("    Esto es raro... el problema debe ser otro")
            
            print("\n" + "=" * 80)
            print("✅ Verificación completada")
            print("=" * 80)
            
            print("\n💡 AHORA RECARGA EL VISOR EN TU NAVEGADOR:")
            print("   1. Abre http://localhost:8099/dian_vs_erp/visor_v2")
            print("   2. Presiona Ctrl+F5 para forzar recarga")
            print("   3. Los 104 registros de febrero deberían aparecer")
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    verificar_y_activar_tipos()
