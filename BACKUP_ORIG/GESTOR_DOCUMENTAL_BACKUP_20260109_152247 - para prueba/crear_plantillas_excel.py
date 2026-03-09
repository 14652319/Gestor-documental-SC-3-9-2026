"""
Script para crear plantillas Excel con encabezados exactos que el sistema espera
"""
import pandas as pd
import os

# Crear directorio
os.makedirs('plantillas', exist_ok=True)

# ==========================================
# PLANTILLA DIAN - Encabezados con espacios (formato original DIAN)
# ==========================================
dian_headers = [
    'Tipo Documento',
    'CUFE/CUDE', 
    'Numero',
    'Prefijo',
    'Fecha Emision',
    'NIT Emisor',
    'Nombre Emisor',
    'Valor',
    'Forma Pago'
]

# ==========================================
# PLANTILLA ERP - Encabezados exactos que busca el sistema
# ==========================================
erp_headers = [
    'Proveedor',
    'Docto. Proveedor',
    'Clase de Documento',
    'C.O.',
    'Usuario Creacion',
    'Nro. Documento'
]

# ==========================================
# PLANTILLA ACUSES - Encabezados exactos que busca el sistema
# ==========================================
acuses_headers = [
    'Fecha',
    'Adquiriente',
    'Factura',
    'Emisor',
    'CUFE',
    'Estado Docto.'
]

# Crear DataFrames vacíos con solo encabezados
df_dian = pd.DataFrame(columns=dian_headers)
df_erp = pd.DataFrame(columns=erp_headers)
df_acuses = pd.DataFrame(columns=acuses_headers)

# Guardar como Excel
df_dian.to_excel('plantillas/plantilla_dian.xlsx', index=False, engine='openpyxl')
df_erp.to_excel('plantillas/plantilla_erp.xlsx', index=False, engine='openpyxl')
df_acuses.to_excel('plantillas/plantilla_acuses.xlsx', index=False, engine='openpyxl')

print('✅ Plantillas Excel creadas exitosamente:')
print('   📄 plantillas/plantilla_dian.xlsx')
print('   📄 plantillas/plantilla_erp.xlsx')
print('   📄 plantillas/plantilla_acuses.xlsx')
print()
print('📋 Encabezados DIAN:', ', '.join(dian_headers))
print('📋 Encabezados ERP:', ', '.join(erp_headers))
print('📋 Encabezados Acuses:', ', '.join(acuses_headers))
