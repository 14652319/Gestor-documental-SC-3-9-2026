# -*- coding: utf-8 -*-
"""
Script para verificar el texto EXACTO de tipo_documento en registros de 2025 vs 2026
"""
import requests

def verificar_texto_exacto():
    try:
        base_url = "http://127.0.0.1:8099"
        
        print("=" * 80)
        print("🔍 VERIFICANDO TEXTO EXACTO DE 'tipo_documento'")
        print("=" * 80)
        
        # 1. Registros de DICIEMBRE 2025 (que SÍ se ven)
        print("\n✅ DICIEMBRE 2025 (SÍ aparecen en visor):")
        response = requests.get(f"{base_url}/dian_vs_erp/api/dian", params={
            'fecha_inicial': '2025-12-01',
            'fecha_final': '2025-12-31',
            'size': 5
        }, timeout=30)
        
        if response.status_code == 200:
            data_dic = response.json()
            if len(data_dic) > 0:
                tipo_dic = data_dic[0].get('tipo_documento', '')
                print(f"   Primer registro - tipo_documento: '{tipo_dic}'")
                print(f"   Longitud: {len(tipo_dic)} caracteres")
                print(f"   ASCII: {[ord(c) for c in tipo_dic[:25]]}")
                
                # Mostrar todos los tipos únicos
                tipos_unicos_dic = set([r.get('tipo_documento', '') for r in data_dic])
                print(f"\n   Tipos únicos encontrados en muestra:")
                for t in tipos_unicos_dic:
                    print(f"      '{t}'")
        
        # 2. Registros de FEBRERO 2026 (que NO se ven)
        print("\n❌ FEBRERO 2026 (NO aparecen en visor):")
        response = requests.get(f"{base_url}/dian_vs_erp/api/dian", params={
            'fecha_inicial': '2026-02-01',
            'fecha_final': '2026-02-28',
            'size': 5
        }, timeout=30)
        
        if response.status_code == 200:
            data_feb = response.json()
            if len(data_feb) > 0:
                tipo_feb = data_feb[0].get('tipo_documento', '')
                print(f"   Primer registro - tipo_documento: '{tipo_feb}'")
                print(f"   Longitud: {len(tipo_feb)} caracteres")
                print(f"   ASCII: {[ord(c) for c in tipo_feb[:25]]}")
                
                # Mostrar todos los tipos únicos
                tipos_unicos_feb = set([r.get('tipo_documento', '') for r in data_feb])
                print(f"\n   Tipos únicos encontrados en muestra:")
                for t in tipos_unicos_feb:
                    print(f"      '{t}'")
        
        # 3. Comparación byte por byte
        if len(data_dic) > 0 and len(data_feb) > 0:
            tipo_2025 = data_dic[0].get('tipo_documento', '')
            tipo_2026 = data_feb[0].get('tipo_documento', '')
            
            print(f"\n🔬 COMPARACIÓN BYTE POR BYTE:")
            print(f"   2025: '{tipo_2025}'")
            print(f"   2026: '{tipo_2026}'")
            print(f"   ¿Son iguales? {tipo_2025 == tipo_2026}")
            
            if tipo_2025 != tipo_2026:
                print(f"\n⚠️  ¡ENCONTRADO EL PROBLEMA!")
                print(f"   El texto es DIFERENTE entre 2025 y 2026:")
                print(f"   - Diciembre 2025: '{tipo_2025}'")
                print(f"   - Febrero 2026: '{tipo_2026}'")
                
                # Comparar carácter por carácter
                max_len = max(len(tipo_2025), len(tipo_2026))
                print(f"\n   Comparación carácter por carácter:")
                for i in range(max_len):
                    c1 = tipo_2025[i] if i < len(tipo_2025) else '(fin)'
                    c2 = tipo_2026[i] if i < len(tipo_2026) else '(fin)'
                    igual = "✓" if c1 == c2 else "✗"
                    print(f"      Pos {i:2d}: '{c1}' vs '{c2}' {igual}")
        
        print("\n" + "=" * 80)
        print("✅ Verificación completada")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_texto_exacto()
