#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialización del módulo DIAN vs ERP
Configura base de datos SQLite y tablas PostgreSQL
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.dian_vs_erp.models import (
    DianSqliteManager, 
    ReporteDian, 
    LogProcesamiento, 
    ConfiguracionDian,
    obtener_estadisticas_sqlite
)
from datetime import datetime

def inicializar_sqlite():
    """Inicializa la base de datos SQLite del módulo DIAN vs ERP"""
    print("🔧 Inicializando base de datos SQLite...")
    
    try:
        manager = DianSqliteManager()
        print("✅ Base de datos SQLite inicializada correctamente")
        
        # Obtener estadísticas para verificar
        stats = obtener_estadisticas_sqlite()
        print(f"📊 Estadísticas SQLite: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando SQLite: {str(e)}")
        return False

def crear_tablas_postgresql():
    """Crea las tablas PostgreSQL para reportes y auditoría"""
    print("🔧 Creando tablas PostgreSQL...")
    
    try:
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            
            # Verificar que las tablas se crearon
            inspector = db.inspect(db.engine)
            tablas_creadas = inspector.get_table_names()
            
            tablas_dian = [
                'reportes_dian',
                'logs_procesamiento_dian', 
                'configuracion_dian'
            ]
            
            tablas_encontradas = []
            for tabla in tablas_dian:
                if tabla in tablas_creadas:
                    tablas_encontradas.append(tabla)
                    print(f"  ✅ Tabla {tabla} creada")
                else:
                    print(f"  ⚠️ Tabla {tabla} no encontrada")
            
            print(f"✅ PostgreSQL: {len(tablas_encontradas)}/{len(tablas_dian)} tablas creadas")
            return len(tablas_encontradas) == len(tablas_dian)
            
    except Exception as e:
        print(f"❌ Error creando tablas PostgreSQL: {str(e)}")
        return False

def configurar_modulo():
    """Configura parámetros iniciales del módulo"""
    print("🔧 Configurando módulo DIAN vs ERP...")
    
    try:
        with app.app_context():
            configuraciones = [
                {
                    'empresa_id': '805028041',  # Supertiendas Cañaveral
                    'clave': 'directorio_csv',
                    'valor': 'modules/dian_vs_erp/data/csv/',
                    'descripcion': 'Directorio donde se almacenan los archivos CSV'
                },
                {
                    'empresa_id': '805028041',
                    'clave': 'backup_automatico',
                    'valor': 'true',
                    'descripcion': 'Activar backup automático de la base SQLite'
                },
                {
                    'empresa_id': '805028041',
                    'clave': 'max_registros_por_pagina',
                    'valor': '1000',
                    'descripcion': 'Máximo de registros por página en el dashboard'
                }
            ]
            
            for config in configuraciones:
                # Verificar si ya existe
                existente = ConfiguracionDian.query.filter_by(
                    empresa_id=config['empresa_id'],
                    clave=config['clave']
                ).first()
                
                if not existente:
                    nueva_config = ConfiguracionDian(
                        empresa_id=config['empresa_id'],
                        clave=config['clave'],
                        valor=config['valor'],
                        descripcion=config['descripcion'],
                        usuario_actualizacion='sistema'
                    )
                    db.session.add(nueva_config)
                    print(f"  ✅ Configuración '{config['clave']}' agregada")
                else:
                    print(f"  ⚠️ Configuración '{config['clave']}' ya existe")
            
            db.session.commit()
            print("✅ Configuración inicial completada")
            return True
            
    except Exception as e:
        print(f"❌ Error configurando módulo: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass  # Ya estamos fuera del contexto
        return False

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    print("🔧 Verificando dependencias...")
    
    dependencias = [
        ('polars', 'polars'),
        ('pandas', 'pandas'),
        ('sqlite3', 'sqlite3'),
        ('pathlib', 'pathlib')
    ]
    
    dependencias_ok = True
    
    for nombre, import_name in dependencias:
        try:
            if import_name == 'pathlib':
                from pathlib import Path
            else:
                __import__(import_name)
            print(f"  ✅ {nombre}")
        except ImportError:
            print(f"  ❌ {nombre} - FALTANTE")
            dependencias_ok = False
    
    return dependencias_ok

def mostrar_resumen():
    """Muestra resumen del estado del módulo"""
    print("\n" + "="*50)
    print("📊 RESUMEN DEL MÓDULO DIAN VS ERP")
    print("="*50)
    
    # SQLite
    try:
        stats = obtener_estadisticas_sqlite()
        print(f"🗃️  SQLite:")
        print(f"   • Total DIAN: {stats['total_dian']:,}")
        print(f"   • Total ERP: {stats['total_erp']:,}")
        print(f"   • Matches: {stats['matches_dian_erp']:,}")
        print(f"   • Con módulo: {stats['dian_con_modulo']:,}")
        
    except Exception as e:
        print(f"🗃️  SQLite: Error obteniendo estadísticas")
    
    # PostgreSQL
    try:
        with app.app_context():
            total_reportes = ReporteDian.query.count()
            total_logs = LogProcesamiento.query.count()
            total_configs = ConfiguracionDian.query.count()
            
            print(f"🐘 PostgreSQL:")
            print(f"   • Reportes: {total_reportes}")
            print(f"   • Logs: {total_logs}")
            print(f"   • Configuraciones: {total_configs}")
            
    except Exception as e:
        print(f"🐘 PostgreSQL: Error conectando")
    
    print("\n🌟 URLs del módulo:")
    print(f"   • Dashboard: http://localhost:8099/dian_vs_erp/")
    print(f"   • Cargar archivos: http://localhost:8099/dian_vs_erp/cargar")
    print(f"   • API: http://localhost:8099/dian_vs_erp/api/dian")

def main():
    """Función principal de inicialización"""
    print("🚀 INICIALIZANDO MÓDULO DIAN VS ERP")
    print("="*50)
    
    # 1. Verificar dependencias
    if not verificar_dependencias():
        print("❌ Faltan dependencias. Ejecuta: pip install -r requirements.txt")
        return False
    
    # 2. Inicializar SQLite
    if not inicializar_sqlite():
        print("❌ Error en SQLite")
        return False
    
    # 3. Crear tablas PostgreSQL  
    if not crear_tablas_postgresql():
        print("❌ Error en PostgreSQL")
        return False
    
    # 4. Configurar módulo
    if not configurar_modulo():
        print("❌ Error en configuración")
        return False
    
    # 5. Mostrar resumen
    mostrar_resumen()
    
    print("\n✅ MÓDULO DIAN VS ERP INICIALIZADO CORRECTAMENTE")
    print("🎯 Listo para usar en: http://localhost:8099/dian_vs_erp/")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)