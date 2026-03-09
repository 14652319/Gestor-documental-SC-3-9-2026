# -*- coding: utf-8 -*-
"""
Verificar registros en tipos_documentos_dian después de la inserción
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from modules.dian_vs_erp.models import TipoDocumentoDian, Dian
from app import app

def verificar_y_corregir():
    with app.app_context():
        try:
            print("=" * 80)
            print("🔍 VERIFICANDO REGISTROS EN tipos_documentos_dian")
            print("=" * 80)
            
            # Ver todos los "Factura" algo
            tipos_factura = TipoDocumentoDian.query.filter(
                TipoDocumentoDian.tipo_documento.like('%actura%')
            ).all()
            
            print(f"\nTipos que contienen 'actura':")
            for t in tipos_factura:
                print(f"  ID {t.id}: '{t.tipo_documento}' | procesar_frontend={t.procesar_frontend} | activo={t.activo}")
            
            # Ver qué tipos de documento existen en la tabla dian de 2026
            print(f"\n" + "=" * 80)
            print("🔍 TIPOS DE DOCUMENTOS EN TABLA DIAN (FEBRERO 2026)")
            print("=" * 80)
            
            tipos_dian = db.session.execute(
                db.text("""
                    SELECT DISTINCT tipo_documento, COUNT(*) as cantidad
                    FROM dian 
                    WHERE fecha_emision >= '2026-02-01' AND fecha_emision <= '2026-02-28'
                    GROUP BY tipo_documento
                    ORDER BY cantidad DESC
                """)
            ).fetchall()
            
            print(f"\nTipos encontrados en febrero 2026:")
            for tipo, cantidad in tipos_dian:
                print(f"  '{tipo}' ({cantidad} registros)")
                # Buscar coincidencia en tipos_documentos_dian
                coincidencia = TipoDocumentoDian.query.filter_by(tipo_documento=tipo).first()
                if coincidencia:
                    print(f"    ✅ EXISTE en tipos_documentos_dian (ID {coincidencia.id})")
                else:
                    print(f"    ❌ NO EXISTE en tipos_documentos_dian")
                    print(f"    💡 Insertando...")
                    nuevo = TipoDocumentoDian(
                        tipo_documento=tipo,
                        procesar_frontend=True,
                        activo=True
                    )
                    db.session.add(nuevo)
            
            db.session.commit()
            print(f"\n✅ Todos los tipos de 2026 ahora están configurados")
            
            # Verificar nuevamente
            print(f"\n" + "=" * 80)
            print("✅ VERIFICACIÓN FINAL")
            print("=" * 80)
            
            tipos_factura = TipoDocumentoDian.query.filter(
                TipoDocumentoDian.tipo_documento.like('%actura%')
            ).all()
            
            print(f"\nTipos configurados que contienen 'actura':")
            for t in tipos_factura:
                activo_str = "✅" if (t.procesar_frontend and t.activo) else "❌"
                print(f"  {activo_str} ID {t.id}: '{t.tipo_documento}'")
            
            print("\n" + "=" * 80)
            print("💡 AHORA RECARGA EL VISOR:")
            print("   1. Ctrl+F5 en el navegador")
            print("   2. Fechas: 01/02/2026 - 28/02/2026")
            print("   3. Click 'Buscar'")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    verificar_y_corregir()
