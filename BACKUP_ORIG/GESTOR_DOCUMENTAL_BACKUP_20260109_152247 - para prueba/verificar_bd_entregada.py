#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import os

def verificar_base_datos():
    print("🔍 VERIFICANDO BASE DE DATOS EN PROYECTO ENTREGADO...")
    
    # Verificar proyecto entregado
    db_path_entregado = "Proyecto Dian Vs ERP v5.20251130/maestro/maestro.db"
    print(f"\n📁 Ruta proyecto entregado: {os.path.abspath(db_path_entregado)}")
    print(f"📂 Existe: {os.path.exists(db_path_entregado)}")
    
    if os.path.exists(db_path_entregado):
        size_mb = os.path.getsize(db_path_entregado) / 1024 / 1024
        print(f"📊 Tamaño: {size_mb:.1f} MB")
        
        # Conectar y verificar
        conn = sqlite3.connect(db_path_entregado)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n=== {len(tables)} TABLAS ENCONTRADAS ===")
        for t in tables:
            print(f"✅ {t[0]}")
        
        print(f"\n=== CONTEO DE REGISTROS POR TABLA ===")
        for table_tuple in tables:
            table = table_tuple[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                count = cursor.fetchone()[0]
                emoji = "📊" if count > 0 else "⚪"
                print(f"{emoji} {table}: {count:,} registros")
            except Exception as e:
                print(f"❌ {table}: Error al contar - {str(e)}")
        
        # Verificar algunas tablas específicas con más detalle
        print(f"\n=== VERIFICACIÓN DETALLADA ===")
        tables_importantes = ['dian', 'erp', 'maestro_consolidado', 'usuarios_asignados', 'historial_envios_email']
        
        for table in tables_importantes:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                count = cursor.fetchone()[0]
                print(f"🎯 {table}: {count:,} registros")
                
                if count > 0 and table == 'dian':
                    # Ver una muestra de datos DIAN
                    cursor.execute(f"SELECT * FROM [{table}] LIMIT 3")
                    rows = cursor.fetchall()
                    cursor.execute(f"PRAGMA table_info([{table}])")
                    columns = [col[1] for col in cursor.fetchall()]
                    print(f"   Columnas: {', '.join(columns[:5])}...")
                    print(f"   Muestra: {len(rows)} registros encontrados")
                    
            except Exception as e:
                print(f"⚠️ {table}: Tabla no existe o error - {str(e)}")
        
        conn.close()
        return True
    else:
        print("❌ NO SE ENCUENTRA LA BASE DE DATOS EN PROYECTO ENTREGADO")
        return False

if __name__ == "__main__":
    verificar_base_datos()