#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Análisis completo de decoradores vs permisos en BD
"""
import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def analizar_decoradores_y_permisos():
    with app.app_context():
        print("=" * 100)
        print("🔍 ANÁLISIS COMPLETO: DECORADORES vs PERMISOS EN BD")
        print("=" * 100)
        
        # 1. Analizar módulo Causaciones
        print("\n1️⃣ MÓDULO: CAUSACIONES")
        print("-" * 100)
        
        # Decoradores en código
        print("\n   📝 Analizando archivo: modules/causaciones/routes.py")
        try:
            with open('modules/causaciones/routes.py', 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            # Buscar decoradores
            decoradores_encontrados = re.findall(r"@requiere_permiso(?:_html)?\(['\"]causaciones['\"],\s*['\"]([^'\"]+)['\"]", contenido)
            
            print(f"   Decoradores encontrados: {len(decoradores_encontrados)}")
            if decoradores_encontrados:
                decoradores_unicos = set(decoradores_encontrados)
                for dec in sorted(decoradores_unicos):
                    print(f"      - causaciones.{dec}")
        except Exception as e:
            print(f"   ⚠️ Error leyendo archivo: {e}")
        
        # Permisos en BD
        print("\n   💾 Permisos en BD para módulo 'causaciones':")
        result = db.session.execute(text("""
            SELECT DISTINCT accion 
            FROM permisos_usuarios 
            WHERE modulo = 'causaciones'
            ORDER BY accion
        """))
        
        permisos_bd = result.fetchall()
        print(f"   Total en BD: {len(permisos_bd)}")
        for p in permisos_bd:
            print(f"      - causaciones.{p[0]}")
        
        # 2. Módulo Facturas Digitales
        print("\n2️⃣ MÓDULO: FACTURAS_DIGITALES")
        print("-" * 100)
        
        print("\n   📝 Analizando archivo: modules/facturas_digitales/routes.py")
        try:
            with open('modules/facturas_digitales/routes.py', 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            decoradores_encontrados = re.findall(r"@requiere_permiso(?:_html)?\(['\"]facturas_digitales['\"],\s*['\"]([^'\"]+)['\"]", contenido)
            
            print(f"   Decoradores encontrados: {len(decoradores_encontrados)}")
            if decoradores_encontrados:
                decoradores_unicos = set(decoradores_encontrados)
                for dec in sorted(decoradores_unicos):
                    print(f"      - facturas_digitales.{dec}")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        
        print("\n   💾 Permisos en BD:")
        result = db.session.execute(text("""
            SELECT DISTINCT accion 
            FROM permisos_usuarios 
            WHERE modulo = 'facturas_digitales'
            ORDER BY accion
        """))
        
        permisos_bd = result.fetchall()
        print(f"   Total en BD: {len(permisos_bd)}")
        for p in permisos_bd:
            print(f"      - facturas_digitales.{p[0]}")
        
        # 3. Módulo Archivo Digital
        print("\n3️⃣ MÓDULO: ARCHIVO_DIGITAL")
        print("-" * 100)
        
        print("\n   📝 Analizando archivo: modules/notas_contables/pages.py")
        try:
            with open('modules/notas_contables/pages.py', 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            decoradores_encontrados = re.findall(r"@requiere_permiso(?:_html)?\(['\"]archivo_digital['\"],\s*['\"]([^'\"]+)['\"]", contenido)
            
            print(f"   Decoradores encontrados: {len(decoradores_encontrados)}")
            if decoradores_encontrados:
                decoradores_unicos = set(decoradores_encontrados)
                for dec in sorted(decoradores_unicos):
                    print(f"      - archivo_digital.{dec}")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        
        print("\n   💾 Permisos en BD:")
        result = db.session.execute(text("""
            SELECT DISTINCT accion 
            FROM permisos_usuarios 
            WHERE modulo = 'archivo_digital'
            ORDER BY accion
        """))
        
        permisos_bd = result.fetchall()
        print(f"   Total en BD: {len(permisos_bd)}")
        for p in permisos_bd:
            print(f"      - archivo_digital.{p[0]}")
        
        # 4. PROBLEMA: Rutas sin decorador específico
        print("\n4️⃣ PROBLEMA DETECTADO:")
        print("-" * 100)
        print("\n   ⚠️ Si TODAS las rutas usan el mismo decorador 'acceder_modulo',")
        print("   entonces con UN solo permiso activo, puede acceder a TODO el módulo.")
        print("\n   ✅ SOLUCIÓN: Cada ruta debe tener su propio decorador específico:")
        print("      - /causaciones/nueva → @requiere_permiso('causaciones', 'nueva_causacion')")
        print("      - /causaciones/editar → @requiere_permiso('causaciones', 'editar_causacion')")
        print("      - /causaciones/exportar → @requiere_permiso('causaciones', 'exportar_excel')")
        
        print("\n" + "=" * 100)

if __name__ == "__main__":
    analizar_decoradores_y_permisos()
