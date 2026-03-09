"""
Script para analizar referencias a ambas tablas de permisos en todo el código
y verificar qué módulos/rutas están protegidos con decoradores
"""
import os
import re
from app import app, db
from sqlalchemy import text

print('=' * 80)
print('🔍 ANÁLISIS COMPLETO DE PERMISOS Y PROTECCIÓN DE RUTAS')
print('=' * 80)
print()

# PARTE 1: Buscar todas las referencias en el código
print('📂 PARTE 1: REFERENCIAS EN EL CÓDIGO')
print('-' * 80)

archivos_python = []
for root, dirs, files in os.walk('.'):
    if '.venv' in root or '__pycache__' in root or '.git' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            archivos_python.append(os.path.join(root, file))

referencias = {
    'permisos_usuario': [],
    'permisos_usuarios': []
}

for archivo in archivos_python:
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            lineas = contenido.split('\n')
            
            for i, linea in enumerate(lineas, 1):
                # Buscar permisos_usuario (singular)
                if 'permisos_usuario' in linea.lower() and 'permisos_usuarios' not in linea.lower():
                    referencias['permisos_usuario'].append({
                        'archivo': archivo,
                        'linea': i,
                        'codigo': linea.strip()[:100]
                    })
                
                # Buscar permisos_usuarios (plural)
                if 'permisos_usuarios' in linea.lower():
                    referencias['permisos_usuarios'].append({
                        'archivo': archivo,
                        'linea': i,
                        'codigo': linea.strip()[:100]
                    })
    except:
        pass

print(f'\n📊 RESULTADOS:')
print(f'  • permisos_usuario (singular): {len(referencias["permisos_usuario"])} referencias')
print(f'  • permisos_usuarios (plural): {len(referencias["permisos_usuarios"])} referencias')

if referencias['permisos_usuario']:
    print(f'\n⚠️  REFERENCIAS A permisos_usuario (TABLA VIEJA):')
    archivos_unicos = {}
    for ref in referencias['permisos_usuario']:
        archivo = ref['archivo']
        if archivo not in archivos_unicos:
            archivos_unicos[archivo] = []
        archivos_unicos[archivo].append((ref['linea'], ref['codigo']))
    
    for archivo, refs in archivos_unicos.items():
        print(f'\n  📄 {archivo}:')
        for linea, codigo in refs[:3]:  # Máximo 3 por archivo
            print(f'     Línea {linea}: {codigo}')

# PARTE 2: Verificar rutas protegidas con decoradores
print('\n' + '=' * 80)
print('🔒 PARTE 2: RUTAS PROTEGIDAS CON DECORADORES')
print('-' * 80)

rutas_con_decorador = []
rutas_sin_decorador = []

# Buscar en archivos de rutas
archivos_rutas = []
for archivo in archivos_python:
    if 'routes.py' in archivo or 'app.py' in archivo:
        archivos_rutas.append(archivo)

for archivo in archivos_rutas:
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            lineas = contenido.split('\n')
            
            i = 0
            while i < len(lineas):
                linea = lineas[i]
                
                # Buscar definiciones de rutas
                if '@' in linea and ('route(' in linea or 'bp.route(' in linea):
                    ruta_match = re.search(r"route\(['\"]([^'\"]+)", linea)
                    if ruta_match:
                        ruta = ruta_match.group(1)
                        
                        # Buscar si hay decorador de permisos en las líneas anteriores
                        tiene_decorador = False
                        for j in range(max(0, i-5), i):
                            if 'requiere_permiso' in lineas[j]:
                                tiene_decorador = True
                                break
                        
                        # Buscar el nombre de la función
                        for j in range(i+1, min(i+10, len(lineas))):
                            if lineas[j].strip().startswith('def '):
                                func_name = lineas[j].strip().split('(')[0].replace('def ', '')
                                
                                if tiene_decorador:
                                    rutas_con_decorador.append({
                                        'archivo': archivo.replace('.\\', ''),
                                        'ruta': ruta,
                                        'funcion': func_name
                                    })
                                else:
                                    rutas_sin_decorador.append({
                                        'archivo': archivo.replace('.\\', ''),
                                        'ruta': ruta,
                                        'funcion': func_name
                                    })
                                break
                i += 1
    except:
        pass

print(f'\n✅ Rutas PROTEGIDAS con decoradores: {len(rutas_con_decorador)}')
if rutas_con_decorador:
    for i, ruta in enumerate(rutas_con_decorador[:10], 1):
        print(f'  {i}. {ruta["ruta"]} → {ruta["funcion"]} ({ruta["archivo"]})')
    if len(rutas_con_decorador) > 10:
        print(f'  ... y {len(rutas_con_decorador) - 10} más')

print(f'\n⚠️  Rutas SIN PROTECCIÓN (sin decorador): {len(rutas_sin_decorador)}')
if rutas_sin_decorador:
    # Agrupar por archivo
    rutas_por_archivo = {}
    for ruta in rutas_sin_decorador:
        archivo = ruta['archivo']
        if archivo not in rutas_por_archivo:
            rutas_por_archivo[archivo] = []
        rutas_por_archivo[archivo].append(ruta)
    
    for archivo, rutas in rutas_por_archivo.items():
        print(f'\n  📄 {archivo}:')
        for ruta in rutas[:5]:  # Máximo 5 por archivo
            print(f'     • {ruta["ruta"]} → {ruta["funcion"]}')
        if len(rutas) > 5:
            print(f'     ... y {len(rutas) - 5} más')

# PARTE 3: Comparar datos entre ambas tablas
print('\n' + '=' * 80)
print('📊 PARTE 3: COMPARACIÓN DE DATOS ENTRE TABLAS')
print('-' * 80)

with app.app_context():
    # Obtener datos de tabla singular
    result1 = db.session.execute(text("""
        SELECT usuario_id, modulo, accion, permitido
        FROM permisos_usuario
        ORDER BY usuario_id, modulo, accion
    """))
    datos_singular = result1.fetchall()
    
    # Obtener datos de tabla plural
    result2 = db.session.execute(text("""
        SELECT usuario_id, modulo, accion, permitido
        FROM permisos_usuarios
        ORDER BY usuario_id, modulo, accion
    """))
    datos_plural = result2.fetchall()
    
    print(f'\n📋 permisos_usuario (singular): {len(datos_singular)} registros')
    print(f'📋 permisos_usuarios (plural): {len(datos_plural)} registros')
    
    # Convertir a sets para comparar
    set_singular = set(datos_singular)
    set_plural = set(datos_plural)
    
    # Encontrar registros únicos en cada tabla
    solo_en_singular = set_singular - set_plural
    solo_en_plural = set_plural - set_singular
    en_ambas = set_singular & set_plural
    
    print(f'\n🔍 ANÁLISIS:')
    print(f'  • Registros en AMBAS tablas: {len(en_ambas)}')
    print(f'  • Solo en permisos_usuario (singular): {len(solo_en_singular)}')
    print(f'  • Solo en permisos_usuarios (plural): {len(solo_en_plural)}')
    
    if solo_en_singular:
        print(f'\n⚠️  REGISTROS ÚNICOS EN TABLA SINGULAR (se perderían al eliminar):')
        for registro in list(solo_en_singular)[:10]:
            print(f'     • Usuario {registro[0]} | {registro[1]}.{registro[2]} | permitido={registro[3]}')
        if len(solo_en_singular) > 10:
            print(f'     ... y {len(solo_en_singular) - 10} más')
    
    # PARTE 4: Verificar usuario 14652319 específicamente
    print('\n' + '=' * 80)
    print('👤 PARTE 4: ANÁLISIS DEL USUARIO 14652319')
    print('-' * 80)
    
    # Buscar el usuario_id correspondiente al NIT 14652319
    result = db.session.execute(text("""
        SELECT u.id, u.usuario, u.activo, t.razon_social
        FROM usuarios u
        JOIN terceros t ON u.tercero_id = t.id
        WHERE t.nit = '14652319'
    """))
    usuario_info = result.fetchone()
    
    if usuario_info:
        usuario_id, usuario, activo, razon_social = usuario_info
        print(f'\n✅ Usuario encontrado:')
        print(f'   • ID: {usuario_id}')
        print(f'   • Usuario: {usuario}')
        print(f'   • Activo: {activo}')
        print(f'   • Razón social: {razon_social}')
        
        # Ver permisos en tabla PLURAL (activa)
        result = db.session.execute(text("""
            SELECT modulo, accion, permitido
            FROM permisos_usuarios
            WHERE usuario_id = :uid
            ORDER BY modulo, accion
        """), {'uid': usuario_id})
        permisos_plural = result.fetchall()
        
        print(f'\n📋 Permisos en tabla ACTIVA (permisos_usuarios): {len(permisos_plural)}')
        
        permisos_activos = [p for p in permisos_plural if p[2]]
        permisos_inactivos = [p for p in permisos_plural if not p[2]]
        
        print(f'   • Permisos ACTIVOS (permitido=TRUE): {len(permisos_activos)}')
        if permisos_activos:
            for p in permisos_activos[:10]:
                print(f'      ✅ {p[0]}.{p[1]}')
            if len(permisos_activos) > 10:
                print(f'      ... y {len(permisos_activos) - 10} más')
        
        print(f'   • Permisos INACTIVOS (permitido=FALSE): {len(permisos_inactivos)}')
        if permisos_inactivos:
            for p in permisos_inactivos[:5]:
                print(f'      ❌ {p[0]}.{p[1]}')
            if len(permisos_inactivos) > 5:
                print(f'      ... y {len(permisos_inactivos) - 5} más')

print('\n' + '=' * 80)
print('💡 RECOMENDACIONES')
print('=' * 80)

if len(referencias['permisos_usuario']) <= 2:
    print('\n✅ SEGURO PARA ELIMINAR:')
    print('   • Solo 2 o menos referencias (scripts de diagnóstico)')
    print('   • Todos los módulos usan la tabla plural')
else:
    print('\n⚠️  REQUIERE MIGRACIÓN:')
    print(f'   • {len(referencias["permisos_usuario"])} referencias activas')
    print('   • Migrar código antes de eliminar tabla')

if solo_en_singular:
    print('\n⚠️  MIGRAR DATOS:')
    print(f'   • {len(solo_en_singular)} registros únicos en tabla singular')
    print('   • Ejecutar migración antes de eliminar')
else:
    print('\n✅ NO HAY DATOS ÚNICOS:')
    print('   • Tabla singular no contiene datos que no estén en tabla plural')
    print('   • Seguro eliminar después de actualizar código')

print('\n' + '=' * 80)
