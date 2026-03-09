from app import app, db
from sqlalchemy import text

with app.app_context():
    print('=' * 80)
    print('🔍 ANÁLISIS DE TABLAS DE PERMISOS DUPLICADAS')
    print('=' * 80)
    print()
    
    # Analizar permisos_usuario (104 registros)
    print('📋 TABLA: permisos_usuario (104 registros)')
    print('-' * 80)
    
    result = db.session.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT usuario_id) as usuarios_distintos,
            COUNT(DISTINCT modulo) as modulos_distintos,
            COUNT(CASE WHEN permitido = TRUE THEN 1 END) as permisos_activos,
            COUNT(CASE WHEN permitido = FALSE THEN 1 END) as permisos_inactivos,
            MIN(fecha_asignacion) as fecha_mas_antigua,
            MAX(fecha_asignacion) as fecha_mas_reciente
        FROM permisos_usuario
    """))
    
    stats = result.fetchone()
    print(f'  Total registros: {stats[0]}')
    print(f'  Usuarios distintos: {stats[1]}')
    print(f'  Módulos distintos: {stats[2]}')
    print(f'  Permisos ACTIVOS (permitido=TRUE): {stats[3]}')
    print(f'  Permisos INACTIVOS (permitido=FALSE): {stats[4]}')
    print(f'  Fecha más antigua: {stats[5]}')
    print(f'  Fecha más reciente: {stats[6]}')
    print()
    
    # Muestra de datos
    sample = db.session.execute(text("""
        SELECT usuario_id, modulo, accion, permitido, fecha_asignacion
        FROM permisos_usuario
        ORDER BY fecha_asignacion DESC
        LIMIT 5
    """))
    
    print('  📋 Últimos 5 registros:')
    for row in sample:
        print(f'    • Usuario {row[0]} | {row[1]}.{row[2]} | permitido={row[3]} | {row[4]}')
    
    print()
    print('=' * 80)
    
    # Analizar permisos_usuarios (587 registros)
    print('📋 TABLA: permisos_usuarios (587 registros)')
    print('-' * 80)
    
    result = db.session.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT usuario_id) as usuarios_distintos,
            COUNT(DISTINCT modulo) as modulos_distintos,
            COUNT(CASE WHEN permitido = TRUE THEN 1 END) as permisos_activos,
            COUNT(CASE WHEN permitido = FALSE THEN 1 END) as permisos_inactivos,
            MIN(fecha_asignacion) as fecha_mas_antigua,
            MAX(fecha_asignacion) as fecha_mas_reciente
        FROM permisos_usuarios
    """))
    
    stats = result.fetchone()
    print(f'  Total registros: {stats[0]}')
    print(f'  Usuarios distintos: {stats[1]}')
    print(f'  Módulos distintos: {stats[2]}')
    print(f'  Permisos ACTIVOS (permitido=TRUE): {stats[3]}')
    print(f'  Permisos INACTIVOS (permitido=FALSE): {stats[4]}')
    print(f'  Fecha más antigua: {stats[5]}')
    print(f'  Fecha más reciente: {stats[6]}')
    print()
    
    # Muestra de datos
    sample = db.session.execute(text("""
        SELECT usuario_id, modulo, accion, permitido, fecha_asignacion
        FROM permisos_usuarios
        ORDER BY fecha_asignacion DESC NULLS LAST
        LIMIT 5
    """))
    
    print('  📋 Últimos 5 registros:')
    for row in sample:
        print(f'    • Usuario {row[0]} | {row[1]}.{row[2]} | permitido={row[3]} | {row[4]}')
    
    print()
    print('=' * 80)
    print('🔍 BUSCAR REFERENCIAS EN EL CÓDIGO')
    print('=' * 80)
    print()
    
    # Buscar en el código cuál tabla se usa
    import os
    import re
    
    archivos_python = []
    for root, dirs, files in os.walk('.'):
        # Ignorar .venv y otras carpetas
        if '.venv' in root or '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                archivos_python.append(os.path.join(root, file))
    
    referencias_usuario = []
    referencias_usuarios = []
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                if 'permisos_usuario' in contenido and 'permisos_usuarios' not in contenido:
                    # Contar líneas que mencionan permisos_usuario
                    lineas = contenido.split('\n')
                    for i, linea in enumerate(lineas, 1):
                        if 'permisos_usuario' in linea.lower():
                            referencias_usuario.append((archivo, i, linea.strip()[:80]))
                
                if 'permisos_usuarios' in contenido:
                    # Contar líneas que mencionan permisos_usuarios
                    lineas = contenido.split('\n')
                    for i, linea in enumerate(lineas, 1):
                        if 'permisos_usuarios' in linea.lower():
                            referencias_usuarios.append((archivo, i, linea.strip()[:80]))
        except:
            pass
    
    print(f'📊 REFERENCIAS EN CÓDIGO:')
    print(f'  • permisos_usuario: {len(referencias_usuario)} referencias')
    print(f'  • permisos_usuarios: {len(referencias_usuarios)} referencias')
    print()
    
    if referencias_usuario:
        print('  📄 Archivos que usan permisos_usuario:')
        archivos_unicos = set([r[0] for r in referencias_usuario])
        for archivo in sorted(archivos_unicos):
            print(f'    • {archivo}')
    
    print()
    
    if referencias_usuarios:
        print('  📄 Archivos que usan permisos_usuarios:')
        archivos_unicos = set([r[0] for r in referencias_usuarios])
        for archivo in sorted(archivos_unicos):
            print(f'    • {archivo}')
    
    print()
    print('=' * 80)
    print('💡 CONCLUSIÓN')
    print('=' * 80)
    print()
    
    if len(referencias_usuario) > len(referencias_usuarios):
        print('✅ La tabla ACTIVA es: permisos_usuario')
        print(f'   • {len(referencias_usuario)} referencias en el código')
        print()
        print('⚠️  La tabla permisos_usuarios parece ser LEGACY:')
        print(f'   • {len(referencias_usuarios)} referencias en el código')
        print(f'   • Tiene {stats[0]} registros pero puede ser data antigua')
    elif len(referencias_usuarios) > len(referencias_usuario):
        print('✅ La tabla ACTIVA es: permisos_usuarios')
        print(f'   • {len(referencias_usuarios)} referencias en el código')
        print()
        print('⚠️  La tabla permisos_usuario parece ser NUEVA:')
        print(f'   • {len(referencias_usuario)} referencias en el código')
    else:
        print('⚠️  CONFLICTO: Ambas tablas tienen referencias similares')
        print('   Se recomienda consolidar en UNA SOLA tabla')
