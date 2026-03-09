# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import requests
import json

# Datos que envía el formulario
data_prueba = {
    "nit": "805013653",
    "razon_social": "LA GALERIA Y CIA SAS",
    "prefijo": "FE",
    "folio": "1",
    "empresa_id": "SC",  # Este es el valor que seleccionas en el dropdown
    "centro_operacion_id": "005 - SC SANTA ELENA",
    "fecha_expedicion": "26/11/2025",
    "fecha_radicacion": "26/11/2025",
    "valor_bruto": "15.000"
}

print("=== PRUEBA DE GUARDADO DE FACTURA ===")
print(f"\nDatos a enviar:")
for key, value in data_prueba.items():
    print(f"  {key}: {value}")

print(f"\n¿Campo empresa_id presente? {'✅ SÍ' if 'empresa_id' in data_prueba else '❌ NO'}")
print(f"¿Campo empresa_id tiene valor? {'✅ SÍ' if data_prueba.get('empresa_id') else '❌ NO'}")

# Verificar qué campos faltan según la validación del servidor
campos_requeridos = ['nit', 'razon_social', 'prefijo', 'folio', 'empresa_id', 'centro_operacion_id', 
                     'fecha_expedicion', 'valor_bruto']

print(f"\n=== VALIDACIÓN DE CAMPOS REQUERIDOS ===")
faltantes = []
for campo in campos_requeridos:
    presente = campo in data_prueba and data_prueba[campo]
    estado = "✅" if presente else "❌"
    print(f"{estado} {campo}: {data_prueba.get(campo, 'NO PRESENTE')}")
    if not presente:
        faltantes.append(campo)

if faltantes:
    print(f"\n❌ CAMPOS FALTANTES: {', '.join(faltantes)}")
else:
    print(f"\n✅ TODOS LOS CAMPOS REQUERIDOS PRESENTES")
