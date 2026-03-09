#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creador de tablas del sistema de monitoreo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def crear_tablas_monitoreo():
    """Crea todas las tablas del sistema de monitoreo"""
    with app.app_context():
        print("=" * 80)
        print("🔧 CREANDO TABLAS DEL SISTEMA DE MONITOREO")
        print("=" * 80)
        
        # Leer y ejecutar el SQL
        sql_file = 'sql/monitoreo_completo.sql'
        
        if not os.path.exists(sql_file):
            print(f"❌ Archivo no encontrado: {sql_file}")
            return
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Ejecutar cada comando SQL
        comandos = sql_content.split(';')
        
        exitos = 0
        errores = 0
        
        for i, comando in enumerate(comandos, 1):
            comando = comando.strip()
            if not comando or comando.startswith('--') or comando.startswith('/*'):
                continue
            
            try:
                db.session.execute(db.text(comando))
                db.session.commit()
                exitos += 1
            except Exception as e:
                print(f"⚠️ Error en comando {i}: {str(e)[:100]}")
                errores += 1
                db.session.rollback()
        
        print(f"\n✅ Comandos ejecutados: {exitos}")
        print(f"⚠️ Errores: {errores}")
        
        # Verificar tablas creadas
        print("\n📊 VERIFICANDO TABLAS CREADAS:")
        tablas_esperadas = [
            'sesiones_activas',
            'logs_sistema',
            'logs_auditoria',
            'alertas_sistema',
            'metricas_rendimiento',
            'ips_blancas'
        ]
        
        for tabla in tablas_esperadas:
            try:
                resultado = db.session.execute(db.text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = '{tabla}'
                """)).scalar()
                
                if resultado > 0:
                    # Contar registros
                    count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
                    print(f"   ✅ {tabla:30s} | {count} registros")
                else:
                    print(f"   ❌ {tabla:30s} | NO EXISTE")
            except Exception as e:
                print(f"   ❌ {tabla:30s} | Error: {str(e)[:50]}")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    crear_tablas_monitoreo()
