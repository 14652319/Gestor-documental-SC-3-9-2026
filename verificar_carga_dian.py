#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar carga de archivos DIAN vs ERP
Consulta registros de enero 2025 y febrero 2026
"""

import os
from dotenv import load_dotenv
from extensions import db
from sqlalchemy import text

# Cargar variables de entorno
load_dotenv()

# Configurar Flask app mínima para usar db
from flask import Flask
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def verificar_carga():
    """Verifica registros cargados por periodo"""
    with app.app_context():
        try:
            # Consulta por periodo
            query = text("""
                SELECT 
                    TO_CHAR(fecha_documento, 'YYYY-MM') as periodo,
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT nit_tercero) as terceros_unicos,
                    MIN(fecha_documento) as fecha_minima,
                    MAX(fecha_documento) as fecha_maxima
                FROM maestro_dian_vs_erp
                WHERE fecha_documento >= '2025-01-01' 
                  AND fecha_documento <= '2026-02-28'
                GROUP BY TO_CHAR(fecha_documento, 'YYYY-MM')
                ORDER BY periodo;
            """)
            
            result = db.session.execute(query)
            registros = result.fetchall()
            
            print("=" * 80)
            print("📊 VERIFICACIÓN DE CARGA - MÓDULO DIAN VS ERP")
            print("=" * 80)
            print()
            
            if not registros:
                print("❌ NO se encontraron registros para enero 2025 o febrero 2026")
                print()
                
                # Verificar si hay datos en la tabla
                query_total = text("SELECT COUNT(*) as total FROM maestro_dian_vs_erp")
                total_result = db.session.execute(query_total)
                total = total_result.fetchone()[0]
                
                if total > 0:
                    print(f"ℹ️  La tabla tiene {total:,} registros en total")
                    
                    # Mostrar rango de fechas existente
                    query_rango = text("""
                        SELECT 
                            MIN(fecha_documento) as minima,
                            MAX(fecha_documento) as maxima
                        FROM maestro_dian_vs_erp
                    """)
                    rango = db.session.execute(query_rango).fetchone()
                    print(f"📅 Rango de fechas: {rango[0]} → {rango[1]}")
                else:
                    print("⚠️  La tabla maestro_dian_vs_erp está VACÍA")
                    print()
                    print("💡 Posibles causas:")
                    print("   • El proceso de carga no se completó por el error de pyarrow")
                    print("   • Los archivos no se procesaron correctamente")
                    print("   • Hay un problema con la base de datos")
            else:
                print("✅ REGISTROS ENCONTRADOS:")
                print()
                print(f"{'Periodo':<15} {'Registros':<15} {'Terceros':<15} {'Fecha Mín':<15} {'Fecha Máx'}")
                print("-" * 80)
                
                total_general = 0
                for row in registros:
                    periodo, total, terceros, fecha_min, fecha_max = row
                    total_general += total
                    print(f"{periodo:<15} {total:>12,}   {terceros:>12,}   {str(fecha_min):<15} {str(fecha_max)}")
                
                print("-" * 80)
                print(f"{'TOTAL':<15} {total_general:>12,}")
                print()
                
                # Verificar si enero 2025 y febrero 2026 están presentes
                periodos_encontrados = {row[0] for row in registros}
                
                if '2025-01' in periodos_encontrados:
                    print("✅ Enero 2025: CARGADO")
                else:
                    print("❌ Enero 2025: NO ENCONTRADO")
                
                if '2026-02' in periodos_encontrados:
                    print("✅ Febrero 2026: CARGADO")
                else:
                    print("❌ Febrero 2026: NO ENCONTRADO")
            
            print()
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ ERROR al consultar la base de datos: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verificar_carga()
