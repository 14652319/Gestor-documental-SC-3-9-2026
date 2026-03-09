# -*- coding: utf-8 -*-
"""
Script para consultar fechas de registros DIAN usando la API del servidor
"""
import requests
from datetime import datetime

def consultar_api_dian():
    try:
        base_url = "http://127.0.0.1:8099"
        
        print("=" * 80)
        print("📊 CONSULTANDO FECHAS EN LA BASE DE DATOS DIAN")
        print("=" * 80)
        
        # 1. Consultar enero 2026
        print("\n🔵 CONSULTANDO ENERO 2026...")
        response = requests.get(f"{base_url}/dian_vs_erp/api/dian", params={
            'fecha_inicial': '2026-01-01',
            'fecha_final': '2026-01-31',
            'size': 1000
        }, timeout=30)
        
        if response.status_code == 200:
            data_enero = response.json()
            print(f"   Total registros en enero 2026: {len(data_enero)}")
            if len(data_enero) > 0:
                print(f"\n   📋 Primeros 5 registros de enero 2026:")
                for i, reg in enumerate(data_enero[:5]):
                    print(f"      {i+1}. {reg.get('nombre_emisor', 'N/A')[:40]} | {reg.get('prefijo', '')}-{reg.get('folio', '')} | Fecha: {reg.get('fecha_emision', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        # 2. Consultar febrero 2026
        print("\n🔵 CONSULTANDO FEBRERO 2026...")
        response = requests.get(f"{base_url}/dian_vs_erp/api/dian", params={
            'fecha_inicial': '2026-02-01',
            'fecha_final': '2026-02-28',
            'size': 1000
        }, timeout=30)
        
        if response.status_code == 200:
            data_febrero = response.json()
            print(f"   Total registros en febrero 2026: {len(data_febrero)}")
            if len(data_febrero) > 0:
                print(f"\n   📋 Primeros 5 registros de febrero 2026:")
                for i, reg in enumerate(data_febrero[:5]):
                    print(f"      {i+1}. {reg.get('nombre_emisor', 'N/A')[:40]} | {reg.get('prefijo', '')}-{reg.get('folio', '')} | Fecha: {reg.get('fecha_emision', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        # 3. Consultar diciembre 2025
        print("\n🟡 CONSULTANDO DICIEMBRE 2025...")
        response = requests.get(f"{base_url}/dian_vs_erp/api/dian", params={
            'fecha_inicial': '2025-12-01',
            'fecha_final': '2025-12-31',
            'size': 1000
        }, timeout=30)
        
        if response.status_code == 200:
            data_dic = response.json()
            print(f"   Total registros en diciembre 2025: {len(data_dic)}")
            if len(data_dic) > 0:
                print(f"\n   📋 Primeros 5 registros de diciembre 2025:")
                for i, reg in enumerate(data_dic[:5]):
                    print(f"      {i+1}. {reg.get('nombre_emisor', 'N/A')[:40]} | {reg.get('prefijo', '')}-{reg.get('folio', '')} | Fecha: {reg.get('fecha_emision', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        # 4. Consultar todo 2026
        print("\n🔵 CONSULTANDO TODO EL AÑO 2026...")
        response = requests.get(f"{base_url}/dian_vs_erp/api/dian", params={
            'fecha_inicial': '2026-01-01',
            'fecha_final': '2026-12-31',
            'size': 5000
        }, timeout=30)
        
        if response.status_code == 200:
            data_2026 = response.json()
            print(f"   Total registros en 2026: {len(data_2026)}")
            
            # Agrupar por mes
            meses = {}
            for reg in data_2026:
                fecha = reg.get('fecha_emision', '')
                if fecha:
                    mes = fecha[:7]  # YYYY-MM
                    meses[mes] = meses.get(mes, 0) + 1
            
            if meses:
                print(f"\n   📅 Distribución por mes en 2026:")
                for mes in sorted(meses.keys()):
                    print(f"      {mes}: {meses[mes]} registros")
        else:
            print(f"   ❌ Error: {response.status_code}")
        
        print("\n" + "=" * 80)
        print("✅ Consulta completada")
        print("=" * 80)
        
    except requests.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al servidor en http://127.0.0.1:8099")
        print("   Asegúrate de que el servidor esté corriendo.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    consultar_api_dian()
