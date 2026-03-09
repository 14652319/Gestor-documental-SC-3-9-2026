#!/usr/bin/env python3
"""
Test de importación de app.py para identificar errores
"""

import sys
import traceback

def test_app_import():
    """Probar importación de app.py"""
    try:
        print("📦 Probando importación de app.py...")
        import app
        print("✅ app.py importado correctamente")
        
        print("🌐 Probando inicio del servidor...")
        # El servidor debería iniciar automáticamente
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Error general: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_app_import()