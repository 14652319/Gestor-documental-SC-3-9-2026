#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configurar permisos solo Causaciones usando Flask context
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def configurar_permisos_minimos():
    with app.app_context():
        usuario_id = 22  # Usuario 14652319
        
        print("=" * 80)
        print("🔧 CONFIGURANDO PERMISOS MÍNIMOS PARA USUARIO 14652319")
        print("=" * 80)
        
        # 1. Desactivar TODO
        print("\n1️⃣ Desactivando TODOS los permisos...")
        result = db.session.execute(text("""
            UPDATE permisos_usuarios 
            SET permitido = FALSE 
            WHERE usuario_id = :usuario_id
        """), {"usuario_id": usuario_id})
        
        db.session.commit()
        print(f"   ✅ Todos los permisos desactivados")
        
        # 2. Activar SOLO Causaciones
        print("\n2️⃣ Activando SOLO permisos de Causaciones...")
        
        permisos = [
            'acceder_modulo',
            'consultar_causaciones',
            'nueva_causacion',
            'consultar_documentos',
            'ver_pdf',
            'agregar_observacion',
            'exportar_excel'
        ]
        
        for accion in permisos:
            db.session.execute(text("""
                UPDATE permisos_usuarios 
                SET permitido = TRUE 
                WHERE usuario_id = :usuario_id 
                  AND modulo = 'causaciones' 
                  AND accion = :accion
            """), {"usuario_id": usuario_id, "accion": accion})
            print(f"   ✅ causaciones.{accion}")
        
        db.session.commit()
        print(f"\n💾 {len(permisos)} permisos activados")
        
        # 3. Verificar
        print("\n3️⃣ Verificando resultado...")
        result = db.session.execute(text("""
            SELECT modulo, accion 
            FROM permisos_usuarios 
            WHERE usuario_id = :usuario_id AND permitido = TRUE
            ORDER BY modulo, accion
        """), {"usuario_id": usuario_id})
        
        activos = result.fetchall()
        print(f"\n✅ Permisos activos: {len(activos)}")
        for p in activos:
            print(f"   ✅ {p[0]}.{p[1]}")
        
        print("\n" + "=" * 80)
        print("✅ CONFIGURACIÓN COMPLETADA")
        print("=" * 80)
        print("\n📋 PRUEBA:")
        print("   1. Cerrar sesión")
        print("   2. Login: NIT=14652319, Usuario=14652319, Pass=R1c4rd0$")
        print("   3. /causaciones/ → ✅ DEBE FUNCIONAR")
        print("   4. /facturas_digitales/dashboard → ❌ DEBE BLOQUEAR")

if __name__ == "__main__":
    configurar_permisos_minimos()
