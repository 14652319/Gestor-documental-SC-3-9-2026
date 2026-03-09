#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar permisos ACTUALES del usuario 14652319
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def verificar_permisos():
    with app.app_context():
        usuario_id = 22
        
        print("=" * 80)
        print("🔍 VERIFICANDO PERMISOS ACTUALES DEL USUARIO 14652319")
        print("=" * 80)
        
        # 1. Permisos activos
        print("\n1️⃣ PERMISOS ACTIVOS (permitido=TRUE):")
        result = db.session.execute(text("""
            SELECT modulo, accion, permitido, fecha_asignacion
            FROM permisos_usuarios
            WHERE usuario_id = :usuario_id AND permitido = TRUE
            ORDER BY modulo, accion
        """), {"usuario_id": usuario_id})
        
        activos = result.fetchall()
        print(f"   Total: {len(activos)}")
        
        if activos:
            modulo_actual = None
            for p in activos:
                if p[0] != modulo_actual:
                    print(f"\n   📁 {p[0].upper()}")
                    modulo_actual = p[0]
                print(f"      ✅ {p[1]}")
        
        # 2. Verificar archivo_digital específicamente
        print("\n2️⃣ PERMISOS DE ARCHIVO_DIGITAL:")
        result = db.session.execute(text("""
            SELECT accion, permitido
            FROM permisos_usuarios
            WHERE usuario_id = :usuario_id 
              AND modulo = 'archivo_digital'
            ORDER BY accion
        """), {"usuario_id": usuario_id})
        
        archivo_permisos = result.fetchall()
        for p in archivo_permisos:
            estado = "✅ TRUE" if p[1] else "❌ FALSE"
            print(f"   {p[0]}: {estado}")
        
        # 3. Verificar otras rutas sin decorador
        print("\n3️⃣ VERIFICAR MÓDULOS SIN DECORADOR:")
        print("   ⚠️ archivo_digital: NO tiene decoradores @requiere_permiso")
        print("   ⚠️ configuracion: NO tiene decoradores")
        print("   ⚠️ notas_contables: NO tiene decoradores")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    verificar_permisos()
