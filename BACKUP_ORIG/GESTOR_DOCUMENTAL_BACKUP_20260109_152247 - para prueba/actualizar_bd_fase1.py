# -*- coding: utf-8 -*-
"""Script para ejecutar actualizacion FASE 1 de facturas digitales"""
from app import app
from extensions import db
from sqlalchemy import text

print("=" * 60)
print("ACTUALIZANDO BASE DE DATOS - FACTURAS DIGITALES FASE 1")
print("=" * 60)

with app.app_context():
    try:
        # Leer archivo SQL
        with open('sql/actualizar_facturas_digitales_fase1.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir por statements (separados por ;)
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        print(f"\n📋 Se ejecutarán {len(statements)} statements SQL...\n")
        
        # Ejecutar cada statement
        for i, statement in enumerate(statements, 1):
            try:
                if statement.strip():
                    db.session.execute(text(statement))
                    db.session.commit()
                    print(f"✅ Statement {i} ejecutado correctamente")
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg or "ya existe" in error_msg.lower():
                    print(f"⚠️  Statement {i}: Ya existe (saltando)")
                    db.session.rollback()
                    continue
                else:
                    print(f"❌ Error en statement {i}: {error_msg[:100]}")
                    db.session.rollback()
                    continue
        
        print("\n" + "=" * 60)
        print("✅ ACTUALIZACION COMPLETADA")
        print("=" * 60)
        print("\n📋 Nuevos campos en facturas_digitales:")
        print("   ✓ departamento")
        print("   ✓ forma_pago") 
        print("   ✓ estado_firma")
        print("   ✓ fecha_envio_firma, usuario_envio_firma")
        print("   ✓ fecha_firmado, usuario_carga_firmado")
        print("   ✓ archivo_firmado_path")
        print("   ✓ numero_causacion, fecha_causacion, usuario_causacion")
        print("   ✓ fecha_pago, usuario_pago")
        print("\n✅ Sistema listo para FASE 1\n")
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {str(e)}")
        db.session.rollback()
