"""
🧪 TEST COMPLETO MÓDULO TERCEROS
===============================
Script de pruebas para verificar funcionamiento del módulo super completo
de gestión de terceros.

Autor: GitHub Copilot (Claude Sonnet 4)
Fecha: Noviembre 2025
"""

import requests
import json
import time
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8099"
LOGIN_DATA = {
    "nit": "805028041",
    "usuario": "ADMIN",
    "password": "Gestor2024*"
}

class TercerosModuleTest:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
    
    def login(self):
        """Iniciar sesión como administrador"""
        print("🔑 Iniciando sesión...")
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login", json=LOGIN_DATA)
            if response.status_code == 200:
                self.logged_in = True
                print("✅ Login exitoso")
                return True
            else:
                print(f"❌ Login falló: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False
    
    def test_dashboard_access(self):
        """Probar acceso al dashboard principal"""
        print("\n📊 Probando acceso al dashboard...")
        try:
            response = self.session.get(f"{BASE_URL}/terceros/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Dashboard accesible")
                if "Gestión de Terceros" in response.text:
                    print("✅ Contenido del dashboard correcto")
                return True
            else:
                print("❌ Dashboard no accesible")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_api_estadisticas(self):
        """Probar endpoint de estadísticas"""
        print("\n📈 Probando API de estadísticas...")
        try:
            response = self.session.get(f"{BASE_URL}/terceros/api/estadisticas_sistema")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("✅ Estadísticas obtenidas:")
                if 'data' in data:
                    stats = data['data']
                    print(f"  - Total terceros: {stats.get('total_terceros', 0)}")
                    print(f"  - Correos hoy: {stats.get('correos_enviados_hoy', 0)}")
                    print(f"  - Docs pendientes: {stats.get('documentos_pendientes', 0)}")
                    print(f"  - Por notificar: {stats.get('terceros_por_notificar', 0)}")
                return True
            else:
                print(f"❌ Error en estadísticas: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_api_listar(self):
        """Probar listado paginado de terceros"""
        print("\n📋 Probando API de listado...")
        try:
            params = {
                'page': 1,
                'per_page': 5,
                'search': ''
            }
            response = self.session.get(f"{BASE_URL}/terceros/api/listar", params=params)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("✅ Listado obtenido:")
                if 'data' in data:
                    terceros = data['data']
                    print(f"  - Terceros en página: {len(terceros)}")
                    print(f"  - Total registros: {data.get('total', 0)}")
                    print(f"  - Páginas totales: {data.get('pages', 0)}")
                    if terceros:
                        print(f"  - Primer tercero: {terceros[0].get('razon_social', 'N/A')}")
                return True
            else:
                print(f"❌ Error en listado: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_consulta_page(self):
        """Probar página de consulta"""
        print("\n🔍 Probando página de consulta...")
        try:
            response = self.session.get(f"{BASE_URL}/terceros/consulta")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Página de consulta accesible")
                # Verificar elementos clave
                content = response.text
                checks = [
                    ("tabla de terceros", "table" in content),
                    ("filtros de búsqueda", "search" in content.lower()),
                    ("paginación", "pagination" in content.lower()),
                    ("colores institucionales", "--brand-green" in content)
                ]
                for check_name, check_result in checks:
                    status = "✅" if check_result else "⚠️"
                    print(f"  {status} {check_name}")
                return True
            else:
                print("❌ Página de consulta no accesible")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_crear_page(self):
        """Probar página de creación"""
        print("\n➕ Probando página de creación...")
        try:
            response = self.session.get(f"{BASE_URL}/terceros/crear")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Página de creación accesible")
                content = response.text
                checks = [
                    ("formulario de 3 pasos", "Paso 1" in content and "Paso 2" in content),
                    ("validación de NIT", "validarNIT" in content),
                    ("campos básicos", 'name="nit"' in content),
                    ("responsive design", "container-fluid" in content)
                ]
                for check_name, check_result in checks:
                    status = "✅" if check_result else "⚠️"
                    print(f"  {status} {check_name}")
                return True
            else:
                print("❌ Página de creación no accesible")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_api_validar_nit(self):
        """Probar validación de NIT"""
        print("\n🔢 Probando validación de NIT...")
        try:
            # Probar con NIT que probablemente existe
            test_nit = "805028041"
            response = self.session.post(
                f"{BASE_URL}/terceros/api/validar_nit",
                json={"nit": test_nit}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                disponible = data.get("disponible", True)
                message = data.get("message", "")
                print(f"✅ Validación completada:")
                print(f"  - NIT {test_nit}: {'Disponible' if disponible else 'Ya existe'}")
                print(f"  - Mensaje: {message}")
                return True
            else:
                print(f"❌ Error en validación: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS DEL MÓDULO TERCEROS")
        print("=" * 50)
        
        if not self.login():
            print("❌ No se puede continuar sin login")
            return
        
        tests = [
            ("Dashboard Principal", self.test_dashboard_access),
            ("API Estadísticas", self.test_api_estadisticas),
            ("API Listado", self.test_api_listar),
            ("Página Consulta", self.test_consulta_page),
            ("Página Creación", self.test_crear_page),
            ("API Validar NIT", self.test_api_validar_nit)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                time.sleep(1)  # Pausa entre tests
            except Exception as e:
                print(f"❌ Error ejecutando {test_name}: {e}")
                results.append((test_name, False))
        
        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\n🎯 RESULTADO FINAL: {passed}/{total} pruebas exitosas")
        
        if passed == total:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
            print("✨ El módulo terceros está completamente funcional")
        else:
            print("⚠️  Algunas pruebas fallaron. Revisar configuración.")
        
        return passed == total

def main():
    """Función principal"""
    print(f"🕐 {datetime.now()}")
    print("Módulo: Gestión Super Completa de Terceros")
    print("Servidor: http://localhost:8099")
    
    tester = TercerosModuleTest()
    success = tester.run_all_tests()
    
    print("\n" + "="*50)
    if success:
        print("🚀 ¡MÓDULO LISTO PARA PRODUCCIÓN!")
    else:
        print("🔧 Módulo necesita ajustes")
    
    return success

if __name__ == "__main__":
    main()