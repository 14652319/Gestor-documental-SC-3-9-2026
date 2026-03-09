"""
Script de prueba para verificar los endpoints de configuración de catálogos
"""
import requests

BASE_URL = "http://127.0.0.1:8099/facturas-digitales/configuracion"

def test_endpoints():
    """Probar todos los endpoints de configuración"""
    
    print("=" * 60)
    print("🧪 PRUEBA DE ENDPOINTS DE CONFIGURACIÓN")
    print("=" * 60)
    
    tablas = ['tipo-documento', 'forma-pago', 'tipo-servicio', 'departamento']
    
    for tabla in tablas:
        print(f"\n📋 Probando: {tabla}")
        print("-" * 60)
        
        try:
            # GET - Listar registros
            response = requests.get(f"{BASE_URL}/api/{tabla}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    registros = data.get('data', [])
                    print(f"✅ GET exitoso - {len(registros)} registros encontrados")
                    
                    # Mostrar primeros 3 registros
                    for reg in registros[:3]:
                        nombre = reg.get('nombre') or reg.get('descripcion')
                        estado = "✓ Activo" if reg.get('activo') else "✗ Inactivo"
                        print(f"   • {reg.get('sigla'):10s} - {nombre:30s} [{estado}]")
                else:
                    print(f"⚠️  GET devolvió success=False: {data.get('error', 'Sin error')}")
            else:
                print(f"❌ GET falló con código: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ ERROR: No se pudo conectar al servidor en {BASE_URL}")
            print("   Verifica que el servidor esté corriendo en http://127.0.0.1:8099")
            break
        except Exception as e:
            print(f"❌ ERROR inesperado: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 60)
    print(f"\n💡 Puedes acceder al módulo en: {BASE_URL}")
    print("   Usuario: admin (o tu usuario actual)")

if __name__ == "__main__":
    test_endpoints()
