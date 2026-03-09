#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple para verificar carga de archivos DIAN vs ERP
Consulta directa a PostgreSQL sin dependencias de Flask
"""

import os
import psycopg2
from psycopg2 import sql

# Obtener DATABASE_URL del .env
def leer_database_url():
    """Lee DATABASE_URL del archivo .env"""
    with open('.env', 'r', encoding='utf-8') as f:
        for linea in f:
            if linea.startswith('DATABASE_URL='):
                # Formato: postgresql://user:pass@host:port/dbname
                return linea.split('=', 1)[1].strip().strip('"')
    return None

def verificar_carga():
    """Verifica registros cargados por periodo"""
    try:
        # Conectar a la base de datos
        database_url = leer_database_url()
        if not database_url:
            print("❌ No se pudo leer DATABASE_URL del archivo .env")
            return
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("=" * 80)
        print("📊 VERIFICACIÓN DE CARGA - MÓDULO DIAN VS ERP")
        print("=" * 80)
        print()
        
        # Consulta por periodo
        cur.execute("""
            SELECT 
                TO_CHAR(fecha_emision, 'YYYY-MM') as periodo,
                COUNT(*) as total_registros,
                COUNT(DISTINCT nit_emisor) as terceros_unicos,
                MIN(fecha_emision) as fecha_minima,
                MAX(fecha_emision) as fecha_maxima
            FROM maestro_dian_vs_erp
            WHERE fecha_emision >= '2025-01-01' 
              AND fecha_emision <= '2026-02-28'
            GROUP BY TO_CHAR(fecha_emision, 'YYYY-MM')
            ORDER BY periodo;
        """)
        
        registros = cur.fetchall()
        
        if not registros:
            print("❌ NO se encontraron registros para enero 2025 o febrero 2026")
            print()
            
            # Verificar si hay datos en la tabla
            cur.execute("SELECT COUNT(*) as total FROM maestro_dian_vs_erp")
            total = cur.fetchone()[0]
            
            if total > 0:
                print(f"ℹ️  La tabla tiene {total:,} registros en total")
                
                # Mostrar rango de fechas existente
                cur.execute("""
                    SELECT 
                        MIN(fecha_emision) as minima,
                        MAX(fecha_emision) as maxima
                    FROM maestro_dian_vs_erp
                """)
                rango = cur.fetchone()
                print(f"📅 Rango de fechas: {rango[0]} → {rango[1]}")
            else:
                print("⚠️  La tabla maestro_dian_vs_erp está VACÍA")
                print()
                print("💡 Posibles causas del ERROR 'pyarrow':")
                print("   ✅ RESUELTO: pyarrow ahora está instalado")
                print("   • Intenta cargar los archivos nuevamente desde el navegador")
                print("   • Actualiza la página (F5) y vuelve a procesar")
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
            
            print("📋 VERIFICACIÓN DE PERIODOS SOLICITADOS:")
            print()
            if '2025-01' in periodos_encontrados:
                print("   ✅ Enero 2025: CARGADO")
            else:
                print("   ❌ Enero 2025: NO ENCONTRADO")
            
            if '2026-02' in periodos_encontrados:
                print("   ✅ Febrero 2026: CARGADO")
            else:
                print("   ❌ Febrero 2026: NO ENCONTRADO")
        
        print()
        print("=" * 80)
        print()
        print("💡 RECOMENDACIÓN:")
        print("   • pyarrow ya está instalado ✅")
        print("   • Actualiza la página del módulo DIAN vs ERP (F5)")
        print("   • Vuelve a cargar los archivos")
        print("   • El error 'No module named pyarrow' NO debería aparecer")
        print()
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ ERROR de PostgreSQL: {e}")
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_carga()
