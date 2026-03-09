#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificación simple de permisos del usuario 14652319
"""
import os
import sys
from sqlalchemy import create_engine, text

# Configuración de base de datos
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/gestor_documental"

def main():
    engine = create_engine(DATABASE_URL)
    
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE PERMISOS - USUARIO 14652319")
    print("=" * 80)
    
    with engine.connect() as conn:
        # 1. Información del usuario
        print("\n1️⃣ INFORMACIÓN DEL USUARIO:")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT id, usuario, nit, activo, rol, fecha_creacion
            FROM usuarios 
            WHERE usuario = '14652319'
        """))
        user = result.fetchone()
        
        if user:
            print(f"   ID: {user[0]}")
            print(f"   Usuario: {user[1]}")
            print(f"   NIT: {user[2]}")
            print(f"   Activo: {'✅ SÍ' if user[3] else '❌ NO'}")
            print(f"   Rol: {user[4] or 'Sin rol'}")
            print(f"   Fecha creación: {user[5]}")
            usuario_id = user[0]
        else:
            print("   ❌ Usuario NO encontrado")
            return
        
        # 2. Contar permisos
        print("\n2️⃣ RESUMEN DE PERMISOS:")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE permitido = true) as activos,
                COUNT(*) FILTER (WHERE permitido = false) as inactivos
            FROM permisos_usuarios
            WHERE usuario_id = :usuario_id
        """), {"usuario_id": usuario_id})
        
        stats = result.fetchone()
        print(f"   Total de registros: {stats[0]}")
        print(f"   ✅ Permisos ACTIVOS (permitido=TRUE): {stats[1]}")
        print(f"   ❌ Permisos INACTIVOS (permitido=FALSE): {stats[2]}")
        
        # 3. Permisos activos por módulo
        print("\n3️⃣ PERMISOS ACTIVOS (permitido=TRUE):")
        print("-" * 80)
        result = conn.execute(text("""
            SELECT modulo, accion, permitido
            FROM permisos_usuarios
            WHERE usuario_id = :usuario_id AND permitido = true
            ORDER BY modulo, accion
        """), {"usuario_id": usuario_id})
        
        permisos_activos = result.fetchall()
        
        if permisos_activos:
            modulo_actual = None
            for modulo, accion, permitido in permisos_activos:
                if modulo != modulo_actual:
                    print(f"\n   📁 Módulo: {modulo.upper()}")
                    modulo_actual = modulo
                print(f"      ✅ {accion}")
        else:
            print("   ⚠️ NO hay permisos activos")
        
        # 4. Verificar tabla antigua (backup)
        print("\n4️⃣ VERIFICAR TABLA ANTIGUA (permisos_usuario):")
        print("-" * 80)
        try:
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = 'permisos_usuario'
            """))
            existe = result.scalar()
            
            if existe:
                print("   ❌ PROBLEMA: La tabla 'permisos_usuario' AÚN EXISTE")
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM permisos_usuario
                """))
                count = result.scalar()
                print(f"   ⚠️ Tiene {count} registros (debería estar renombrada a backup)")
            else:
                print("   ✅ Tabla 'permisos_usuario' NO existe (correcto, fue renombrada)")
        except Exception as e:
            print(f"   ✅ Tabla 'permisos_usuario' NO existe (correcto): {e}")
        
        # 5. Verificar tabla backup
        print("\n5️⃣ VERIFICAR TABLA BACKUP (permisos_usuario_backup_20251127):")
        print("-" * 80)
        try:
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM permisos_usuario_backup_20251127
            """))
            count = result.scalar()
            print(f"   ✅ Tabla backup existe con {count} registros")
        except Exception as e:
            print(f"   ❌ Error accediendo tabla backup: {e}")
        
        # 6. Simulación de queries de decoradores
        print("\n6️⃣ SIMULACIÓN DE QUERIES DE DECORADORES:")
        print("-" * 80)
        
        modulos_prueba = [
            ('facturas_digitales', 'acceder_modulo'),
            ('facturas_digitales', 'cargar_factura'),
            ('causaciones', 'acceder_modulo'),
            ('relaciones', 'acceder_modulo'),
            ('archivo_digital', 'acceder_modulo')
        ]
        
        for modulo, accion in modulos_prueba:
            result = conn.execute(text("""
                SELECT permitido 
                FROM permisos_usuarios 
                WHERE usuario_id = :usuario_id 
                  AND modulo = :modulo 
                  AND accion = :accion
            """), {"usuario_id": usuario_id, "modulo": modulo, "accion": accion})
            
            row = result.fetchone()
            if row:
                permitido = row[0]
                icono = "✅ PERMITIDO" if permitido else "❌ DENEGADO"
                print(f"   {modulo}.{accion}: {icono}")
            else:
                print(f"   {modulo}.{accion}: ⚠️ NO REGISTRADO")
    
    print("\n" + "=" * 80)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    main()
