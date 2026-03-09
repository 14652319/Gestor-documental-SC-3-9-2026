# -*- coding: utf-8 -*-
"""
Script para verificar tipos de documentos en registros de febrero 2026
"""
import requests
from collections import Counter

def verificar_tipos_documentos():
    try:
        base_url = "http://127.0.0.1:8099"
        
        print("=" * 80)
        print("📊 ANALIZANDO TIPOS DE DOCUMENTOS - FEBRERO 2026")
        print("=" * 80)
        
        # 1. Consultar API ESTÁNDAR (sin filtro de TipoDocumentoDian)
        print("\n🔵 Consultando API ESTÁNDAR (/api/dian) - FEBRERO 2026...")
        response = requests.get(f"{base_url}/dian_vs_erp/api/dian", params={
            'fecha_inicial': '2026-02-01',
            'fecha_final': '2026-02-28',
            'size': 1000
        }, timeout=30)
        
        if response.status_code == 200:
            data_std = response.json()
            print(f"   Total registros: {len(data_std)}")
            
            # Agrupar por tipo_documento
            tipos = Counter([r.get('tipo_documento', 'Sin tipo') for r in data_std])
            print(f"\n   📋 TIPOS DE DOCUMENTOS ENCONTRADOS:")
            for tipo, cantidad in tipos.most_common():
                print(f"      {tipo}: {cantidad} registros")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
        
        # 2. Consultar API V2 (con filtro de TipoDocumentoDian)
        print("\n🔵 Consultando API V2 (/api/dian_v2) - FEBRERO 2026...")
        response = requests.get(f"{base_url}/dian_vs_erp/api/dian_v2", params={
            'fecha_inicial': '2026-02-01',
            'fecha_final': '2026-02-28',
            'size': 1000
        }, timeout=30)
        
        if response.status_code == 200:
            data_v2 = response.json()
            print(f"   Total registros: {len(data_v2)}")
            
            # Agrupar por tipo_documento
            tipos_v2 = Counter([r.get('tipo_documento', 'Sin tipo') for r in data_v2])
            print(f"\n   📋 TIPOS DE DOCUMENTOS VISIBLES EN VISOR V2:")
            for tipo, cantidad in tipos_v2.most_common():
                print(f"      {tipo}: {cantidad} registros")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return
        
        # 3. Comparación
        print(f"\n📊 COMPARACIÓN:")
        print(f"   API Estándar (sin filtro): {len(data_std)} registros")
        print(f"   API V2 (con filtro TipoDocumentoDian): {len(data_v2)} registros")
        print(f"   Diferencia: {len(data_std) - len(data_v2)} registros OCULTOS")
        
        # 4. Identificar tipos bloqueados
        tipos_bloqueados = set(tipos.keys()) - set(tipos_v2.keys())
        if tipos_bloqueados:
            print(f"\n⚠️  TIPOS DE DOCUMENTOS BLOQUEADOS (no aparecen en visor):")
            for tipo in tipos_bloqueados:
                print(f"      {tipo}: {tipos[tipo]} registros ocultos")
        
        print("\n" + "=" * 80)
        print("✅ Análisis completado")
        print("=" * 80)
        
        # Solución
        if len(data_std) > len(data_v2):
            print("\n💡 SOLUCIÓN: Debes agregar los tipos de documentos faltantes a la tabla")
            print("   'tipos_documentos_dian' con procesar_frontend=True y activo=True")
            print(f"\n   Tipos bloqueados: {', '.join(tipos_bloqueados)}")
        
    except requests.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al servidor en http://127.0.0.1:8099")
        print("   Asegúrate de que el servidor esté corriendo.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_tipos_documentos()
