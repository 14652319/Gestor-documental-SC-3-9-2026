#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico: Por qué no aparecen registros de 2026 en el visor
"""

import os
import psycopg2

def leer_database_url():
    """Lee DATABASE_URL del archivo .env"""
    with open('.env', 'r', encoding='utf-8') as f:
        for linea in f:
            if linea.startswith('DATABASE_URL='):
                return linea.split('=', 1)[1].strip().strip('"')
    return None

def diagnosticar():
    """Diagnostica por qué no aparecen los registros"""
    try:
        database_url = leer_database_url()
        if not database_url:
            print("❌ No se pudo leer DATABASE_URL")
            return
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("=" * 80)
        print("🔍 DIAGNÓSTICO: Por qué NO aparecen registros de 2026 en el visor")
        print("=" * 80)
        print()
        
        # 1. Verificar registros de enero 2026 en tabla dian
        print("1️⃣ VERIFICANDO REGISTROS EN TABLA 'dian'...")
        cur.execute("""
            SELECT COUNT(*) 
            FROM dian 
            WHERE fecha_emision >= '2026-01-01' 
              AND fecha_emision <= '2026-02-28'
        """)
        total_dian = cur.fetchone()[0]
        print(f"   📊 Total en tabla 'dian': {total_dian:,} registros")
        print()
        
        # 2. Verificar tipos de documento en esos registros
        print("2️⃣ TIPOS DE DOCUMENTO EN REGISTROS 2026:")
        cur.execute("""
            SELECT 
                tipo_documento, 
                COUNT(*) as cantidad
            FROM dian 
            WHERE fecha_emision >= '2026-01-01' 
              AND fecha_emision <= '2026-02-28'
            GROUP BY tipo_documento
            ORDER BY cantidad DESC
        """)
        tipos_dian = cur.fetchall()
        for tipo, cant in tipos_dian:
            print(f"   📋 {tipo}: {cant:,} registros")
        print()
        
        # 3. Verificar qué tipos ESTÁN configurados en TipoDocumentoDian
        print("3️⃣ TIPOS CONFIGURADOS EN 'tipo_documento_dian':")
        cur.execute("""
            SELECT 
                tipo_documento,
                procesar_frontend,
                activo
            FROM tipo_documento_dian
            ORDER BY tipo_documento
        """)
        tipos_config = cur.fetchall()
        
        if not tipos_config:
            print("   ❌ LA TABLA 'tipo_documento_dian' ESTÁ VACÍA")
            print("   💡 Esta es la razón de que no aparezcan registros")
        else:
            print("   ✅ Tipos configurados:")
            for tipo, frontend, activo in tipos_config:
                estado = "✅" if (frontend and activo) else "❌"
                print(f"   {estado} {tipo} (frontend={frontend}, activo={activo})")
        print()
        
        # 4. Verificar cuántos registros PASARÍAN el filtro del JOIN
        print("4️⃣ REGISTROS QUE PASARÍAN EL FILTRO DEL VISOR:")
        cur.execute("""
            SELECT COUNT(*)
            FROM dian d
            INNER JOIN tipo_documento_dian t ON d.tipo_documento = t.tipo_documento
            WHERE d.fecha_emision >= '2026-01-01' 
              AND d.fecha_emision <= '2026-02-28'
              AND t.procesar_frontend = TRUE
              AND t.activo = TRUE
        """)
        total_filtrado = cur.fetchone()[0]
        print(f"   📊 Registros visibles con filtro actual: {total_filtrado:,}")
        print()
        
        # 5. Diagnóstico y solución
        print("=" * 80)
        print("📋 DIAGNÓSTICO:")
        print("=" * 80)
        if total_dian == 0:
            print("❌ NO hay registros de 2026 en la tabla 'dian'")
            print("💡 Necesitas cargar los archivos desde el módulo 'Cargar y Procesar'")
        elif not tipos_config:
            print("❌ La tabla 'tipo_documento_dian' está VACÍA")
            print("💡 Necesitas ejecutar: python inicializar_tipo_documento_dian.py")
        elif total_filtrado == 0:
            print("❌ Hay registros pero NINGUNO pasa el filtro")
            print()
            print("💡 SOLUCIÓN: Actualizar tabla 'tipo_documento_dian'")
            print()
            print("   Los tipos de documento en 2026 son:")
            for tipo, cant in tipos_dian:
                en_config = any(t[0] == tipo for t in tipos_config)
                if not en_config:
                    print(f"   ⚠️  '{tipo}' NO está en tipo_documento_dian")
                else:
                    config = next(t for t in tipos_config if t[0] == tipo)
                    if not (config[1] and config[2]):
                        print(f"   ⚠️  '{tipo}' está desactivado (frontend={config[1]}, activo={config[2]})")
        else:
            print("✅ Todo está correcto")
            print(f"   Deberían aparecer {total_filtrado:,} registros en el visor")
        
        print()
        print("=" * 80)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnosticar()
