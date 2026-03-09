"""
Script de diagnóstico completo del sistema de permisos
Verifica: Frontend → Backend → Base de datos → Decoradores
"""
from app import app, db
from sqlalchemy import text

print('=' * 80)
print('🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE PERMISOS')
print('=' * 80)
print()

with app.app_context():
    # PASO 1: Verificar usuario 14652319
    print('👤 PASO 1: INFORMACIÓN DEL USUARIO 14652319')
    print('-' * 80)
    
    result = db.session.execute(text("""
        SELECT u.id, u.usuario, u.activo, u.correo, t.nit, t.razon_social, t.tipo_persona
        FROM usuarios u
        JOIN terceros t ON u.tercero_id = t.id
        WHERE t.nit = '14652319' OR u.usuario = '14652319'
    """))
    
    usuario_info = result.fetchone()
    
    if not usuario_info:
        print('❌ Usuario NO encontrado')
        exit(1)
    
    usuario_id, usuario, activo, correo, nit, razon_social, tipo_persona = usuario_info
    
    print(f'✅ Usuario encontrado:')
    print(f'   • ID: {usuario_id}')
    print(f'   • Usuario: {usuario}')
    print(f'   • NIT: {nit}')
    print(f'   • Razón Social: {razon_social}')
    print(f'   • Activo: {activo}')
    print(f'   • Correo: {correo}')
    print()
    
    # PASO 2: Ver TODOS los permisos del usuario (activos E inactivos)
    print('📋 PASO 2: PERMISOS EN BASE DE DATOS')
    print('-' * 80)
    
    result = db.session.execute(text("""
        SELECT modulo, accion, permitido, fecha_asignacion
        FROM permisos_usuarios
        WHERE usuario_id = :uid
        ORDER BY modulo, accion
    """), {'uid': usuario_id})
    
    permisos_todos = result.fetchall()
    
    print(f'Total de registros de permisos: {len(permisos_todos)}')
    print()
    
    permisos_activos = [p for p in permisos_todos if p[2]]
    permisos_inactivos = [p for p in permisos_todos if not p[2]]
    
    print(f'✅ PERMISOS ACTIVOS (permitido=TRUE): {len(permisos_activos)}')
    if permisos_activos:
        for p in permisos_activos:
            print(f'   • {p[0]}.{p[1]} (desde {p[3]})')
    else:
        print('   ⚠️ NO TIENE NINGÚN PERMISO ACTIVO')
    
    print()
    print(f'❌ PERMISOS INACTIVOS (permitido=FALSE): {len(permisos_inactivos)}')
    if len(permisos_inactivos) > 0:
        print(f'   (Mostrando primeros 10 de {len(permisos_inactivos)})')
        for p in permisos_inactivos[:10]:
            print(f'   • {p[0]}.{p[1]}')
    
    print()
    
    # PASO 3: Verificar tabla que usan los decoradores
    print('🔍 PASO 3: VERIFICAR TABLA QUE USAN LOS DECORADORES')
    print('-' * 80)
    
    # Leer decoradores_permisos.py
    with open('decoradores_permisos.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
        
        if 'FROM permisos_usuarios' in contenido:
            print('✅ Decoradores usan tabla: permisos_usuarios (CORRECTO)')
        elif 'FROM permisos_usuario' in contenido and 'FROM permisos_usuarios' not in contenido:
            print('❌ Decoradores usan tabla: permisos_usuario (INCORRECTO - tabla vieja)')
        else:
            print('⚠️ No se pudo determinar qué tabla usan')
    
    print()
    
    # PASO 4: Simular consulta del decorador
    print('🔧 PASO 4: SIMULAR CONSULTA DEL DECORADOR')
    print('-' * 80)
    
    # Probar con algunos módulos clave
    modulos_prueba = [
        ('causaciones', 'acceder_modulo'),
        ('facturas_digitales', 'acceder_modulo'),
        ('recibir_facturas', 'nueva_factura'),
        ('relaciones', 'generar_relacion'),
        ('archivo_digital', 'acceder_modulo'),
        ('configuracion', 'acceder_modulo'),
    ]
    
    print('Consultando permisos como lo haría el decorador:')
    print()
    
    for modulo, accion in modulos_prueba:
        result = db.session.execute(text("""
            SELECT permitido 
            FROM permisos_usuarios 
            WHERE usuario_id = :uid 
              AND modulo = :mod 
              AND accion = :acc
        """), {'uid': usuario_id, 'mod': modulo, 'acc': accion})
        
        permiso = result.fetchone()
        
        if permiso:
            if permiso[0]:
                print(f'   ✅ {modulo}.{accion} → PERMITIDO (TRUE)')
            else:
                print(f'   ❌ {modulo}.{accion} → DENEGADO (FALSE)')
        else:
            print(f'   ⚠️ {modulo}.{accion} → NO EXISTE EN BD')
    
    print()
    
    # PASO 5: Verificar rutas protegidas
    print('🔒 PASO 5: RUTAS CON DECORADORES')
    print('-' * 80)
    
    import os
    import re
    
    archivos_rutas = [
        'modules/recibir_facturas/routes.py',
        'modules/relaciones/routes.py',
        'modules/facturas_digitales/routes.py',
        'modules/causaciones/routes.py',
        'modules/notas_contables/routes.py',
        'modules/configuracion/routes.py',
        'modules/admin/usuarios_permisos/routes.py',
        'modules/admin/monitoreo/routes.py',
    ]
    
    for archivo in archivos_rutas:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
                # Contar decoradores
                decoradores = re.findall(r'@requiere_permiso(_html)?\(', contenido)
                
                print(f'   {"✅" if decoradores else "❌"} {archivo}: {len(decoradores)} decoradores')
    
    print()
    
    # PASO 6: Verificar tablas existentes
    print('📊 PASO 6: TABLAS DE PERMISOS EN BD')
    print('-' * 80)
    
    result = db.session.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_name LIKE '%permiso%'
        ORDER BY table_name
    """))
    
    tablas = result.fetchall()
    
    print('Tablas relacionadas con permisos:')
    for tabla in tablas:
        result_count = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla[0]}"))
        count = result_count.scalar()
        
        # Marcar cuál es la tabla activa
        if tabla[0] == 'permisos_usuarios':
            print(f'   ✅ {tabla[0]}: {count} registros (TABLA ACTIVA)')
        elif tabla[0] == 'permisos_usuario_backup_20251127':
            print(f'   📦 {tabla[0]}: {count} registros (BACKUP)')
        else:
            print(f'   • {tabla[0]}: {count} registros')
    
    print()
    
    # PASO 7: Verificar si existe tabla vieja SIN renombrar
    print('⚠️  PASO 7: VERIFICAR SI EXISTE TABLA VIEJA')
    print('-' * 80)
    
    result = db.session.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_name = 'permisos_usuario'
        )
    """))
    
    existe_tabla_vieja = result.scalar()
    
    if existe_tabla_vieja:
        print('❌ PROBLEMA: La tabla "permisos_usuario" (singular) AÚN EXISTE')
        print('   Esto significa que la migración NO se completó')
        print()
        
        result = db.session.execute(text("SELECT COUNT(*) FROM permisos_usuario"))
        count = result.scalar()
        print(f'   Registros en tabla vieja: {count}')
        print()
        print('🔧 SOLUCIÓN: Ejecutar script de migración nuevamente')
    else:
        print('✅ Tabla vieja "permisos_usuario" NO existe (migración exitosa)')
    
    print()
    
    # PASO 8: Probar login simulado
    print('🔐 PASO 8: SIMULAR PROCESO DE LOGIN')
    print('-' * 80)
    
    print('Al hacer login, la sesión debería tener:')
    print(f'   • session["usuario_id"] = {usuario_id}')
    print(f'   • session["usuario"] = "{usuario}"')
    print(f'   • session["nit"] = "{nit}"')
    print()
    
    print('='  * 80)
    print('💡 RESUMEN DEL DIAGNÓSTICO')
    print('=' * 80)
    print()
    
    if not permisos_activos:
        print('❌ PROBLEMA PRINCIPAL: El usuario NO tiene ningún permiso ACTIVO')
        print('   Solución: Ir a /admin/usuarios-permisos/ y activar permisos')
    elif existe_tabla_vieja:
        print('❌ PROBLEMA PRINCIPAL: Tabla vieja "permisos_usuario" aún existe')
        print('   Los decoradores pueden estar consultando la tabla incorrecta')
        print('   Solución: Ejecutar migración para renombrar tabla vieja')
    else:
        print('✅ Usuario tiene permisos correctos en BD')
        print('✅ Tabla de permisos correcta')
        print()
        print('⚠️ Si aún puede acceder a todo, el problema es que:')
        print('   1. Las rutas NO tienen decoradores aplicados')
        print('   2. Hay validaciones manuales que permiten acceso')
        print('   3. El dashboard permite acceso a todos autenticados')
