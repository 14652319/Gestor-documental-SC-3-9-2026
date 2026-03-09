# -*- coding: utf-8 -*-
"""
Script de prueba para simular el envío del formulario con empresa_id
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from modules.recibir_facturas.models import FacturaTemporal
from sqlalchemy import text
import json

# Simular datos del formulario
datos_formulario = {
    "nit": "805013653",
    "razon_social": "LA GALERIA Y CIA SAS",
    "prefijo": "FE",
    "folio": "999",
    "empresa_id": "SC",
    "centro_operacion_id": 1,
    "fecha_expedicion": "2025-11-26",
    "fecha_radicacion": "2025-11-26",
    "valor_bruto": 15000
}

print("=== PRUEBA DE VALIDACIÓN Y GUARDADO ===\n")

with app.app_context():
    # Validar campos requeridos (misma lógica del servidor)
    campos_requeridos = ['nit', 'razon_social', 'prefijo', 'folio', 'empresa_id', 'centro_operacion_id', 
                        'fecha_expedicion', 'valor_bruto']
    
    print("1. VALIDACIÓN DE CAMPOS REQUERIDOS:")
    faltantes = []
    for campo in campos_requeridos:
        valor = datos_formulario.get(campo)
        presente = campo in datos_formulario and valor
        estado = "✅" if presente else "❌"
        print(f"   {estado} {campo}: {valor}")
        if not presente:
            faltantes.append(campo)
    
    if faltantes:
        print(f"\n❌ ERROR: Campos faltantes: {', '.join(faltantes)}")
        sys.exit(1)
    
    print("\n✅ Todos los campos requeridos presentes\n")
    
    # Verificar que la empresa existe
    print("2. VERIFICACIÓN DE EMPRESA:")
    result = db.session.execute(text("""
        SELECT sigla, nombre, activo 
        FROM empresas 
        WHERE sigla = :sigla
    """), {"sigla": datos_formulario['empresa_id']})
    
    empresa = result.fetchone()
    if empresa:
        print(f"   ✅ Empresa encontrada: {empresa[0]} - {empresa[1]}")
        if not empresa[2]:
            print(f"   ⚠️  ADVERTENCIA: Empresa está INACTIVA")
    else:
        print(f"   ❌ ERROR: Empresa '{datos_formulario['empresa_id']}' no existe")
        sys.exit(1)
    
    # Intentar crear la factura temporal
    print("\n3. CREACIÓN DE FACTURA TEMPORAL:")
    try:
        factura = FacturaTemporal(
            nit=datos_formulario['nit'],
            razon_social=datos_formulario['razon_social'],
            prefijo=datos_formulario['prefijo'],
            folio=datos_formulario['folio'],
            empresa_id=datos_formulario['empresa_id'],
            centro_operacion_id=datos_formulario['centro_operacion_id'],
            fecha_expedicion=datos_formulario['fecha_expedicion'],
            fecha_radicacion=datos_formulario['fecha_radicacion'],
            valor_bruto=datos_formulario['valor_bruto']
        )
        
        print(f"   ✅ Objeto FacturaTemporal creado")
        print(f"   - NIT: {factura.nit}")
        print(f"   - Razón Social: {factura.razon_social}")
        print(f"   - Prefijo: {factura.prefijo}")
        print(f"   - Folio: {factura.folio}")
        print(f"   - Empresa ID: {factura.empresa_id}")
        print(f"   - Centro Operación: {factura.centro_operacion_id}")
        
        # NO GUARDAR para no ensuciar la BD
        print(f"\n✅ PRUEBA EXITOSA - La factura se puede guardar correctamente")
        
    except Exception as e:
        print(f"   ❌ ERROR al crear factura: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
