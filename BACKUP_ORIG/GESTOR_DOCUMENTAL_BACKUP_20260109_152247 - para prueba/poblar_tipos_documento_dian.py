"""
Script para crear y poblar la tabla tipos_documento_dian
Define qué tipos de documentos se procesan y muestran en el frontend
"""
from extensions import db
from modules.dian_vs_erp.models import TipoDocumentoDian
from app import app

def crear_y_poblar_tipos_documento():
    with app.app_context():
        print("\n" + "="*80)
        print("📋 CREANDO Y POBLANDO TABLA tipos_documento_dian")
        print("="*80 + "\n")
        
        # Crear la tabla si no existe
        try:
            db.create_all()
            print("✅ Tabla tipos_documento_dian creada/verificada")
        except Exception as e:
            print(f"⚠️ Error creando tabla: {e}")
        
        # Datos según especificación del usuario
        tipos_documento = [
            {"id": 1, "tipo": "Factura electrónica", "procesar": True},
            {"id": 2, "tipo": "Nota de crédito electrónica", "procesar": True},
            {"id": 3, "tipo": "Application response", "procesar": False},
            {"id": 4, "tipo": "Documento equivalente - Cobro de peajes", "procesar": True},
            {"id": 5, "tipo": "Nota de débito electrónica", "procesar": True},
            {"id": 6, "tipo": "Documento equivalente - Servicios públicos domiciliarios", "procesar": True},
            {"id": 7, "tipo": "Nota de ajuste crédito del documento equivalente", "procesar": False},
            {"id": 8, "tipo": "Factura electrónica de contingencia", "procesar": True},
            {"id": 9, "tipo": "Documento soporte con no obligados", "procesar": False},
            {"id": 10, "tipo": "Factura electrónica de contingencia DIAN", "procesar": True},
            {"id": 11, "tipo": "Documento equivalente POS", "procesar": True},
            {"id": 12, "tipo": "Documento equivalente - Transporte pasajeros terrestre", "procesar": True},
            {"id": 13, "tipo": "Nota de ajuste del documento soporte", "procesar": False},
            {"id": 14, "tipo": "Nota de ajuste débito del documento equivalente", "procesar": False},
            {"id": 15, "tipo": "Factura electrónica AIU", "procesar": True},
            {"id": 16, "tipo": "Factura electrónica de exportación", "procesar": True},
        ]
        
        print("\n📝 Insertando tipos de documentos...\n")
        
        insertados = 0
        actualizados = 0
        
        for item in tipos_documento:
            # Verificar si ya existe
            tipo_existente = TipoDocumentoDian.query.filter_by(tipo_documento=item["tipo"]).first()
            
            if tipo_existente:
                # Actualizar
                tipo_existente.procesar_frontend = item["procesar"]
                tipo_existente.activo = True
                actualizados += 1
                simbolo = "✅" if item["procesar"] else "❌"
                print(f"{simbolo} {item['id']:2d}. {item['tipo']:<70} (ACTUALIZADO)")
            else:
                # Insertar nuevo
                nuevo_tipo = TipoDocumentoDian(
                    tipo_documento=item["tipo"],
                    procesar_frontend=item["procesar"],
                    activo=True
                )
                db.session.add(nuevo_tipo)
                insertados += 1
                simbolo = "✅" if item["procesar"] else "❌"
                print(f"{simbolo} {item['id']:2d}. {item['tipo']:<70} (NUEVO)")
        
        # Guardar cambios
        try:
            db.session.commit()
            print("\n" + "="*80)
            print(f"✅ Proceso completado:")
            print(f"   - Registros insertados: {insertados}")
            print(f"   - Registros actualizados: {actualizados}")
            print(f"   - Total de tipos: {len(tipos_documento)}")
            print(f"   - Tipos a procesar (SI): {sum(1 for t in tipos_documento if t['procesar'])}")
            print(f"   - Tipos a omitir (NO): {sum(1 for t in tipos_documento if not t['procesar'])}")
            print("="*80 + "\n")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error guardando datos: {e}\n")

if __name__ == '__main__':
    crear_y_poblar_tipos_documento()
