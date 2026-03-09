#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir las FK de empresa_id a empresas.sigla
"""
import sys
import psycopg2

try:
    # Conectar directamente con psycopg2
    conn = psycopg2.connect(
        host='localhost',
        database='gestor_documental',
        user='postgres',
        password='Inicio2024*'
    )
    
    cursor = conn.cursor()
    
    print("🔧 Corrigiendo FKs de empresa_id...")
    
    # Corregir FK en facturas_temporales
    cursor.execute("""
        ALTER TABLE facturas_temporales 
        DROP CONSTRAINT IF EXISTS fk_facturas_temporales_empresa;
    """)
    
    cursor.execute("""
        ALTER TABLE facturas_temporales
        ADD CONSTRAINT fk_facturas_temporales_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(sigla)
        ON DELETE RESTRICT;
    """)
    
    print("✅ FK corregida en facturas_temporales")
    
    # Corregir FK en facturas_recibidas
    cursor.execute("""
        ALTER TABLE facturas_recibidas
        DROP CONSTRAINT IF EXISTS fk_facturas_recibidas_empresa;
    """)
    
    cursor.execute("""
        ALTER TABLE facturas_recibidas
        ADD CONSTRAINT fk_facturas_recibidas_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(sigla)
        ON DELETE RESTRICT;
    """)
    
    print("✅ FK corregida en facturas_recibidas")
    
    # Commit
    conn.commit()
    
    print("\n✅ CORRECCIÓN COMPLETADA")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
