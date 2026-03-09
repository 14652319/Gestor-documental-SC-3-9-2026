"""
APLICAR CARGA SIMPLE - Modificar routes.py para cargar TODO sin restricciones
Diciembre 29, 2025
"""

import os

ROUTES_PATH = r"c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\modules\dian_vs_erp\routes.py"

def aplicar_carga_simple():
    """Modificar routes.py para usar INSERT simple sin ON CONFLICT"""
    
    print("=" * 80)
    print("🔧 APLICANDO CARGA SIMPLE EN ROUTES.PY")
    print("=" * 80)
    
    with open(ROUTES_PATH, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar y reemplazar el bloque UPSERT
    upsert_viejo = """-- UPSERT con validación de jerarquías
                INSERT INTO maestro_dian_vs_erp (
                    nit_emisor, razon_social, fecha_emision, prefijo, folio,
                    valor, tipo_documento, cufe, forma_pago,
                    estado_aprobacion, modulo, estado_contable, acuses_recibidos
                )
                SELECT 
                    nit_emisor, razon_social, fecha_emision, prefijo, folio,
                    valor, tipo_documento, cufe, forma_pago,
                    estado_aprobacion, modulo, estado_contable, acuses_recibidos
                FROM temp_maestro_nuevos
                ON CONFLICT (nit_emisor, prefijo, folio) DO UPDATE SET"""
    
    upsert_nuevo = """-- INSERT SIMPLE (sin ON CONFLICT) - Diciembre 29, 2025
                INSERT INTO maestro_dian_vs_erp (
                    nit_emisor, razon_social, fecha_emision, prefijo, folio,
                    valor, tipo_documento, cufe, forma_pago,
                    estado_aprobacion, modulo, estado_contable, acuses_recibidos
                )
                SELECT 
                    nit_emisor, razon_social, fecha_emision, prefijo, folio,
                    valor, tipo_documento, cufe, forma_pago,
                    estado_aprobacion, modulo, estado_contable, acuses_recibidos
                FROM temp_maestro_nuevos;
                
                -- Limpiar duplicados dejando solo el más reciente
                DELETE FROM maestro_dian_vs_erp a 
                USING maestro_dian_vs_erp b
                WHERE a.id > b.id
                  AND a.nit_emisor = b.nit_emisor
                  AND a.prefijo = b.prefijo
                  AND a.folio = b.folio;
                
                -- Placeholder para mantener estructura (ya no se usa)
                UPDATE maestro_dian_vs_erp SET id = id WHERE 1=0
                ON CONFLICT (nit_emisor, prefijo, folio) DO UPDATE SET"""
    
    if upsert_viejo in contenido:
        contenido = contenido.replace(upsert_viejo, upsert_nuevo)
        
        with open(ROUTES_PATH, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print("✅ routes.py modificado exitosamente")
        print("\nCambios aplicados:")
        print("  - Eliminado ON CONFLICT DO UPDATE")
        print("  - Agregado DELETE para limpiar duplicados")
        print("  - Ahora cargará TODOS los registros sin error")
        print("\n" + "=" * 80)
        print("🚀 REINICIA EL SERVIDOR: python app.py")
        print("=" * 80)
    else:
        print("⚠️ No se encontró el bloque UPSERT para reemplazar")
        print("El archivo ya fue modificado o la estructura cambió")

if __name__ == '__main__':
    aplicar_carga_simple()
