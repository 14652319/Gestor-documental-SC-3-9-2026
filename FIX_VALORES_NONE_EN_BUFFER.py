"""
🔧 FIX: Manejo correcto de valores None al escribir a buffer para COPY FROM

PROBLEMA:
- Cuando una fecha/valor es None, f-string lo convierte a 'None' (string)
- PostgreSQL no puede convertir 'None' a DATE/NUMERIC
- Error: "la sintaxis de entrada no es válida para el tipo date: «None»"

SOLUCIÓN:
- Convertir None a cadena vacía antes de escribir al buffer
- PostgreSQL interpreta cadena vacía como NULL cuando se usa null=''

ARCHIVOS AFECTADOS:
- modules/dian_vs_erp/routes.py
"""

import re
import os

def fix_buffer_writes():
    """Corrige escrituras a buffer para manejar valores None correctamente"""
    
    routes_file = "modules/dian_vs_erp/routes.py"
    
    if not os.path.exists(routes_file):
        print(f"❌ Archivo no encontrado: {routes_file}")
        return False
    
    print("🔧 CORRIGIENDO MANEJO DE VALORES None EN BUFFER")
    print("=" * 70)
    
    with open(routes_file, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    cambios_realizados = 0
    
    # ========== FUNCIÓN HELPER ==========
    # Buscar si ya existe la función helper
    if "def format_value_for_copy" not in contenido:
        print("\n📝 Agregando función helper format_value_for_copy()...")
        
        # Buscar un buen lugar para insertarla (antes de insertar_dian_bulk)
        insertar_antes = "def insertar_dian_bulk"
        
        helper_function = '''
def format_value_for_copy(value):
    """
    Formatea un valor para COPY FROM, convirtiendo None a cadena vacía.
    PostgreSQL interpreta cadena vacía como NULL cuando se usa null=''
    """
    if value is None:
        return ''
    if isinstance(value, bool):
        return 't' if value else 'f'
    return str(value)

'''
        
        if insertar_antes in contenido:
            contenido = contenido.replace(insertar_antes, helper_function + insertar_antes)
            cambios_realizados += 1
            print("   ✅ Función helper agregada")
        else:
            print("   ⚠️ No se encontró punto de inserción")
    else:
        print("\n✓ Función helper ya existe")
    
    # ========== FIX 1: TABLA DIAN ==========
    print("\n📋 Corrigiendo buffer writes en TABLA DIAN...")
    
    # Buscar el bloque de escritura de DIAN
    patron_dian = r"(buffer = io\.StringIO\(\)\s+for reg in registros:\s+)buffer\.write\(f\"\{reg\['nit_emisor'\]\}\\t\"\)"
    
    if re.search(patron_dian, contenido):
        # Reemplazar todas las líneas buffer.write en el bloque DIAN
        bloque_dian_viejo = r'''buffer\.write\(f"{reg\['nit_emisor'\]}\\t"\)
        buffer\.write\(f"{reg\['nombre_emisor'\]}\\t"\)
        buffer\.write\(f"{reg\['prefijo'\]}\\t"\)
        buffer\.write\(f"{reg\['folio'\]}\\t"\)
        buffer\.write\(f"{reg\['fecha_emision'\]}\\t"\)
        buffer\.write\(f"{reg\['fecha_vencimiento'\]}\\t"\)
        buffer\.write\(f"{reg\['base'\]}\\t"\)
        buffer\.write\(f"{reg\['iva'\]}\\t"\)
        buffer\.write\(f"{reg\['total'\]}\\t"\)
        buffer\.write\(f"{reg\['clave'\]}\\t"\)
        buffer\.write\(f"{reg\['clave_acuse'\]}\\n"\)'''
        
        bloque_dian_nuevo = r'''buffer.write(f"{format_value_for_copy(reg['nit_emisor'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['nombre_emisor'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['prefijo'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['folio'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['fecha_emision'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['fecha_vencimiento'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['base'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['iva'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['total'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['clave'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['clave_acuse'])}\\n")'''
        
        contenido_nuevo = re.sub(bloque_dian_viejo, bloque_dian_nuevo, contenido)
        if contenido_nuevo != contenido:
            contenido = contenido_nuevo
            cambios_realizados += 1
            print("   ✅ Buffer writes de DIAN corregidos")
    
    # ========== FIX 2: TABLA ERP_COMERCIAL ==========
    print("\n📋 Corrigiendo buffer writes en TABLA ERP_COMERCIAL...")
    
    bloque_comercial_viejo = r'''buffer\.write\(f"{reg\['proveedor'\]}\\t"\)
        buffer\.write\(f"{reg\['razon_social'\]}\\t"\)
        buffer\.write\(f"{reg\['docto_proveedor'\]}\\t"\)
        buffer\.write\(f"{reg\['prefijo'\]}\\t"\)
        buffer\.write\(f"{reg\['folio'\]}\\t"\)
        buffer\.write\(f"{reg\['co'\]}\\t"\)
        buffer\.write\(f"{reg\['nro_documento'\]}\\t"\)
        buffer\.write\(f"{reg\['fecha_recibido'\]}\\t"\)
        buffer\.write\(f"{reg\['usuario_creacion'\]}\\t"\)
        buffer\.write\(f"{reg\['clase_documento'\]}\\t"\)
        buffer\.write\(f"{reg\['valor'\]}\\t"\)
        buffer\.write\(f"{reg\['clave_erp_comercial'\]}\\t"\)
        buffer\.write\(f"{reg\['doc_causado_por'\]}\\t"\)
        buffer\.write\(f"{reg\['modulo'\]}\\n"\)'''
    
    bloque_comercial_nuevo = r'''buffer.write(f"{format_value_for_copy(reg['proveedor'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['razon_social'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['docto_proveedor'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['prefijo'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['folio'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['co'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['nro_documento'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['fecha_recibido'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['usuario_creacion'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['clase_documento'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['valor'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['clave_erp_comercial'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['doc_causado_por'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['modulo'])}\\n")'''
    
    contenido_nuevo = re.sub(bloque_comercial_viejo, bloque_comercial_nuevo, contenido)
    if contenido_nuevo != contenido:
        contenido = contenido_nuevo
        cambios_realizados += 1
        print("   ✅ Buffer writes de ERP_COMERCIAL corregidos")
    
    # ========== FIX 3: TABLA ERP_FINANCIERO ==========
    print("\n📋 Corrigiendo buffer writes en TABLA ERP_FINANCIERO...")
    
    bloque_financiero_viejo = r'''buffer\.write\(f"{reg\['proveedor'\]}\\t"\)
        buffer\.write\(f"{reg\['razon_social'\]}\\t"\)
        buffer\.write\(f"{reg\['docto_proveedor'\]}\\t"\)
        buffer\.write\(f"{reg\['prefijo'\]}\\t"\)
        buffer\.write\(f"{reg\['folio'\]}\\t"\)
        buffer\.write\(f"{reg\['co'\]}\\t"\)
        buffer\.write\(f"{reg\['nro_documento'\]}\\t"\)
        buffer\.write\(f"{reg\['fecha_recibido'\]}\\t"\)
        buffer\.write\(f"{reg\['usuario_creacion'\]}\\t"\)
        buffer\.write\(f"{reg\['clase_documento'\]}\\t"\)
        buffer\.write\(f"{reg\['valor'\]}\\t"\)
        buffer\.write\(f"{reg\['clave_erp_financiero'\]}\\t"\)
        buffer\.write\(f"{reg\['doc_causado_por'\]}\\t"\)
        buffer\.write\(f"{reg\['modulo'\]}\\n"\)'''
    
    bloque_financiero_nuevo = r'''buffer.write(f"{format_value_for_copy(reg['proveedor'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['razon_social'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['docto_proveedor'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['prefijo'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['folio'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['co'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['nro_documento'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['fecha_recibido'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['usuario_creacion'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['clase_documento'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['valor'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['clave_erp_financiero'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['doc_causado_por'])}\\t")
        buffer.write(f"{format_value_for_copy(reg['modulo'])}\\n")'''
    
    contenido_nuevo = re.sub(bloque_financiero_viejo, bloque_financiero_nuevo, contenido)
    if contenido_nuevo != contenido:
        contenido = contenido_nuevo
        cambios_realizados += 1
        print("   ✅ Buffer writes de ERP_FINANCIERO corregidos")
    
    # ========== FIX 4: TABLA ACUSES ==========
    print("\n📋 Corrigiendo buffer writes en TABLA ACUSES...")
    
    # Buscar patrón de acuses (más campos)
    patron_acuses = r"buffer\.write\(f\"\{reg\['nit_proveedor'\]\}\\t\"\)"
    if re.search(patron_acuses, contenido):
        # Reemplazar manualmente con búsqueda más flexible
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'nit_proveedor\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'nit_proveedor\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'razon_social\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'razon_social\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'estado_docto\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'estado_docto\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'cufe\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'cufe\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'numero_documento\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'numero_documento\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'prefijo\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'prefijo\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'folio\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'folio\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'fecha_documento\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'fecha_documento\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'fecha_recepcion\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'fecha_recepcion\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'tipo_documento\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'tipo_documento\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'tipo_operacion\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'tipo_operacion\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'descripcion_evento\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'descripcion_evento\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'codigo_rechazo\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'codigo_rechazo\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'total_factura\']}\\t")',
            'buffer.write(f"{format_value_for_copy(reg[\'total_factura\'])}\\t")'
        )
        contenido = contenido.replace(
            'buffer.write(f"{reg[\'clave_acuse\']}\\n")',
            'buffer.write(f"{format_value_for_copy(reg[\'clave_acuse\'])}\\n")'
        )
        
        cambios_realizados += 1
        print("   ✅ Buffer writes de ACUSES corregidos")
    
    # Guardar cambios
    if contenido != contenido_original:
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print("\n" + "=" * 70)
        print(f"✅ CORRECCIONES APLICADAS: {cambios_realizados}")
        print("\n📊 RESUMEN:")
        print("   ✅ Función helper format_value_for_copy() agregada/verificada")
        print("   ✅ Buffer writes de DIAN corregidos")
        print("   ✅ Buffer writes de ERP_COMERCIAL corregidos")
        print("   ✅ Buffer writes de ERP_FINANCIERO corregidos")
        print("   ✅ Buffer writes de ACUSES corregidos")
        print("\n🔄 SIGUIENTE PASO:")
        print("   1. REINICIA el servidor Flask")
        print("   2. Reintenta cargar los archivos")
        print("   3. Valores None ahora se manejan como NULL ✅")
        return True
    else:
        print("\n⚠️ No se detectaron cambios necesarios")
        return False


if __name__ == "__main__":
    fix_buffer_writes()
