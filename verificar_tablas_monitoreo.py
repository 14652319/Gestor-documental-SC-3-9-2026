#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificador de tablas del sistema de monitoreo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def verificar_y_crear_tablas():
    """Verifica y crea las tablas del sistema de monitoreo si no existen"""
    with app.app_context():
        print("=" * 80)
        print("🔍 VERIFICANDO SISTEMA DE MONITOREO")
        print("=" * 80)
        
        tablas_esperadas = [
            'sesiones_activas',
            'logs_sistema',
            'logs_auditoria',
            'alertas_sistema',
            'metricas_rendimiento',
            'ips_blancas'
        ]
        
        tablas_faltantes = []
        
        print("\n📊 ESTADO ACTUAL:")
        for tabla in tablas_esperadas:
            try:
                resultado = db.session.execute(db.text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = '{tabla}'
                """)).scalar()
                
                if resultado > 0:
                    count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                    print(f"   ✅ {tabla:30s} | {count:3d} registros")
                else:
                    print(f"   ❌ {tabla:30s} | NO EXISTE")
                    tablas_faltantes.append(tabla)
            except Exception as e:
                print(f"   ⚠️ {tabla:30s} | Error: {str(e)[:50]}")
                tablas_faltantes.append(tabla)
        
        if tablas_faltantes:
            print(f"\n⚠️ FALTAN {len(tablas_faltantes)} TABLAS")
            print("\n🔧 CREANDO TABLAS FALTANTES...")
            
            sql_file = 'sql/monitoreo_completo.sql'
            
            if not os.path.exists(sql_file):
                print(f"❌ Archivo no encontrado: {sql_file}")
                return
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Ejecutar cada comando SQL
            comandos = [c.strip() for c in sql_content.split(';') if c.strip() and not c.strip().startswith('--')]
            
            exitos = 0
            errores = 0
            
            for comando in comandos:
                try:
                    db.session.execute(db.text(comando))
                    db.session.commit()
                    exitos += 1
                    print(f"   ✅ Comando ejecutado ({exitos})")
                except Exception as e:
                    error_msg = str(e)
                    if 'already exists' in error_msg or 'ya existe' in error_msg:
                        print(f"   ⏭️ Objeto ya existe (omitiendo)")
                    else:
                        print(f"   ⚠️ Error: {error_msg[:80]}")
                        errores += 1
                    db.session.rollback()
            
            print(f"\n✅ Comandos ejecutados: {exitos}")
            print(f"⚠️ Errores: {errores}")
            
            # Verificar de nuevo
            print("\n📊 ESTADO FINAL:")
            for tabla in tablas_esperadas:
                try:
                    resultado = db.session.execute(db.text(f"""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_name = '{tabla}'
                    """)).scalar()
                    
                    if resultado > 0:
                        count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                        print(f"   ✅ {tabla:30s} | {count:3d} registros")
                    else:
                        print(f"   ❌ {tabla:30s} | NO EXISTE")
                except Exception as e:
                    print(f"   ⚠️ {tabla:30s} | Error: {str(e)[:50]}")
        else:
            print(f"\n✅ TODAS LAS TABLAS EXISTEN")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    verificar_y_crear_tablas()
