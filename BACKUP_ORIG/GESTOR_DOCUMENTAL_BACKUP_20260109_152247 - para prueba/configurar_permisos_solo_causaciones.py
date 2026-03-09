#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configurar permisos MÍNIMOS para usuario 14652319
Solo acceso a módulo Causaciones
"""
import psycopg2

def main():
    conn = psycopg2.connect(
        dbname='gestor_documental',
        user='postgres',
        password='123456',
        host='localhost'
    )
    cur = conn.cursor()
    
    usuario_id = 22  # ID del usuario 14652319
    
    print("=" * 80)
    print("🔧 CONFIGURANDO PERMISOS MÍNIMOS PARA USUARIO 14652319")
    print("=" * 80)
    
    # 1. Desactivar TODOS los permisos
    print("\n1️⃣ Desactivando TODOS los permisos...")
    cur.execute("""
        UPDATE permisos_usuarios 
        SET permitido = FALSE 
        WHERE usuario_id = %s
    """, (usuario_id,))
    
    total_desactivados = cur.rowcount
    print(f"   ✅ {total_desactivados} permisos desactivados")
    
    # 2. Activar SOLO permisos de Causaciones
    print("\n2️⃣ Activando SOLO permisos del módulo Causaciones...")
    
    permisos_causaciones = [
        'acceder_modulo',        # CRÍTICO: Permite entrar al módulo
        'consultar_causaciones', # Ver listado de causaciones
        'nueva_causacion',       # Crear nueva causación
        'consultar_documentos',  # Ver documentos
        'ver_pdf',              # Visualizar PDFs
        'agregar_observacion',  # Agregar comentarios
        'exportar_excel'        # Exportar a Excel
    ]
    
    activados = 0
    for accion in permisos_causaciones:
        cur.execute("""
            UPDATE permisos_usuarios 
            SET permitido = TRUE 
            WHERE usuario_id = %s 
              AND modulo = 'causaciones' 
              AND accion = %s
        """, (usuario_id, accion))
        
        if cur.rowcount > 0:
            print(f"   ✅ causaciones.{accion}")
            activados += 1
        else:
            print(f"   ⚠️ causaciones.{accion} - NO EXISTE EN BD")
    
    # 3. Commit
    conn.commit()
    print(f"\n💾 Cambios guardados: {activados} permisos activados")
    
    # 4. Verificar resultado
    print("\n3️⃣ Verificando resultado...")
    cur.execute("""
        SELECT modulo, accion, permitido
        FROM permisos_usuarios
        WHERE usuario_id = %s AND permitido = TRUE
        ORDER BY modulo, accion
    """, (usuario_id,))
    
    permisos_activos = cur.fetchall()
    
    if permisos_activos:
        print(f"\n✅ Permisos activos: {len(permisos_activos)}")
        for p in permisos_activos:
            print(f"   ✅ {p[0]}.{p[1]}")
    else:
        print("\n❌ NO hay permisos activos")
    
    # 5. Verificar otros módulos
    print("\n4️⃣ Verificando que otros módulos estén bloqueados...")
    
    modulos_test = ['facturas_digitales', 'relaciones', 'gestion_usuarios', 'archivo_digital']
    
    for modulo in modulos_test:
        cur.execute("""
            SELECT COUNT(*) 
            FROM permisos_usuarios 
            WHERE usuario_id = %s 
              AND modulo = %s 
              AND permitido = TRUE
        """, (usuario_id, modulo))
        
        count = cur.fetchone()[0]
        if count == 0:
            print(f"   ✅ {modulo}: BLOQUEADO (0 permisos activos)")
        else:
            print(f"   ⚠️ {modulo}: {count} permisos activos")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 80)
    print("\n📋 INSTRUCCIONES:")
    print("   1. Cerrar sesión en el navegador")
    print("   2. Login con NIT: 14652319, Usuario: 14652319, Password: R1c4rd0$")
    print("   3. Intentar acceder a /causaciones/ → ✅ DEBERÍA FUNCIONAR")
    print("   4. Intentar acceder a /facturas_digitales/dashboard → ❌ DEBERÍA BLOQUEAR")
    print("   5. Intentar acceder a /admin/usuarios-permisos → ❌ DEBERÍA BLOQUEAR")

if __name__ == "__main__":
    main()
