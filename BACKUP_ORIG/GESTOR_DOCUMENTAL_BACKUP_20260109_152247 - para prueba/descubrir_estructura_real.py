#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para descubrir la estructura REAL de la tabla facturas_digitales
"""

import sys
import os

# Configurar ruta para importar módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def descubrir_estructura():
    """Descubre la estructura real de facturas_digitales"""
    
    with app.app_context():
        try:
            # Consultar estructura de la tabla
            query = text("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'facturas_digitales'
                ORDER BY ordinal_position;
            """)
            
            result = db.session.execute(query)
            columnas = result.fetchall()
            
            print("=" * 100)
            print("ESTRUCTURA REAL DE LA TABLA facturas_digitales")
            print("=" * 100)
            print(f"\nTotal de columnas: {len(columnas)}\n")
            
            print(f"{'#':<4} {'COLUMNA':<40} {'TIPO':<25} {'LONGITUD':<10} {'NULLABLE':<10}")
            print("-" * 100)
            
            for idx, col in enumerate(columnas, 1):
                nombre = col[0]
                tipo = col[1]
                longitud = col[2] if col[2] else 'N/A'
                nullable = 'SÍ' if col[3] == 'YES' else 'NO'
                
                print(f"{idx:<4} {nombre:<40} {tipo:<25} {str(longitud):<10} {nullable:<10}")
            
            print("\n" + "=" * 100)
            print("CAMPOS QUE EL MODELO ESPERA (y están causando error):")
            print("=" * 100)
            
            campos_modelo = [
                'id', 'prefijo', 'folio', 'nit_proveedor', 'razon_social_proveedor',
                'fecha_radicacion', 'fecha_emision', 'fecha_vencimiento', 'tipo_documento',
                'tipo_servicio', 'valor_total', 'valor_iva', 'valor_base',
                'nombre_archivo_original', 'nombre_archivo_sistema', 'ruta_archivo',
                'tipo_archivo', 'tamanio_kb', 'hash_archivo', 'archivo_zip_path',
                'archivo_seguridad_social_path', 'archivos_soportes_paths',
                'historial_observaciones', 'estado', 'motivo_rechazo', 'observaciones',
                'usuario_carga', 'tipo_usuario', 'fecha_ultima_modificacion',
                'usuario_ultima_modificacion', 'fecha_carga', 'ip_carga',
                'usuario_revision', 'fecha_revision',
                # Campos FASE 1 que SÍ agregamos
                'departamento', 'forma_pago', 'estado_firma', 'archivo_firmado_path',
                'numero_causacion', 'fecha_pago', 'activo'
            ]
            
            columnas_reales = [col[0] for col in columnas]
            
            print("\nCAMPOS QUE NO EXISTEN EN LA TABLA:")
            faltantes = [c for c in campos_modelo if c not in columnas_reales]
            for campo in faltantes:
                print(f"  ❌ {campo}")
            
            print("\nCAMPOS QUE SÍ EXISTEN:")
            existentes = [c for c in campos_modelo if c in columnas_reales]
            for campo in existentes:
                print(f"  ✅ {campo}")
            
            print("\nCAMPOS EN LA TABLA QUE NO ESTÁN EN EL MODELO:")
            extras = [c for c in columnas_reales if c not in campos_modelo]
            for campo in extras:
                print(f"  ⚠️ {campo}")
            
            print("\n" + "=" * 100)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    descubrir_estructura()
