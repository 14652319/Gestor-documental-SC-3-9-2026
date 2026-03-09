"""
🔍 ESCÁNER COMPLETO DE ENDPOINTS Y FUNCIONALIDADES
Script para encontrar TODOS los endpoints del backend y funcionalidades del frontend
Fecha: 11 de Diciembre, 2025
"""

import os
import re
from sqlalchemy import text
from app import app, db

def escanear_endpoints_python():
    """Escanea TODOS los archivos .py buscando @app.route y @bp.route"""
    print("\n" + "="*80)
    print("📂 ESCANEANDO ENDPOINTS EN ARCHIVOS PYTHON")
    print("="*80)
    
    endpoints = []
    patron_route = re.compile(r"@(\w+)\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?")
    
    # Directorios a escanear
    directorios = [
        '.',  # Raíz (app.py)
        'modules',
        'Proyecto Dian Vs ERP v5.20251130'
    ]
    
    archivos_escaneados = 0
    
    for directorio in directorios:
        if not os.path.exists(directorio):
            continue
            
        for root, dirs, files in os.walk(directorio):
            # Ignorar .venv, __pycache__, node_modules
            dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', 'node_modules', '.git']]
            
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                if file.startswith('test_') or file.endswith('_backup.py'):
                    continue  # Ignorar archivos de test y backup
                    
                filepath = os.path.join(root, file)
                archivos_escaneados += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        contenido = f.read()
                        lineas = contenido.split('\n')
                        
                        for i, linea in enumerate(lineas, 1):
                            match = patron_route.search(linea)
                            if match:
                                bp_name = match.group(1)
                                ruta = match.group(2)
                                metodos_str = match.group(3)
                                metodos = ['GET']  # Default
                                
                                if metodos_str:
                                    metodos = [m.strip().strip('"\'') for m in metodos_str.split(',')]
                                
                                # Detectar módulo desde la ruta del archivo o nombre del blueprint
                                modulo = 'core'  # Default
                                
                                # Mapeo de blueprints a módulos
                                bp_a_modulo = {
                                    'recibir_facturas_bp': 'recibir_facturas',
                                    'relaciones_bp': 'relaciones',
                                    'archivo_digital_bp': 'archivo_digital',
                                    'causaciones_bp': 'causaciones',
                                    'notas_bp': 'notas_contables',
                                    'facturas_digitales_bp': 'facturas_digitales',
                                    'dian_bp': 'dian_vs_erp',
                                    'monitoreo_bp': 'monitoreo',
                                    'configuracion_bp': 'configuracion',
                                    'terceros_bp': 'terceros',
                                    'usuarios_permisos_bp': 'gestion_usuarios',
                                    'permisos_api_bp': 'gestion_usuarios',
                                    'admin_bp': 'admin',
                                    'usuarios_internos_bp': 'usuarios_internos',
                                    'reportes_bp': 'reportes',
                                    'archivo_digital_pages_bp': 'archivo_digital'
                                }
                                
                                # Primero intentar desde el nombre del blueprint
                                if bp_name in bp_a_modulo:
                                    modulo = bp_a_modulo[bp_name]
                                # Luego desde la ruta del archivo
                                elif 'modules/' in filepath:
                                    partes = filepath.split('modules/')[1].split('/')
                                    if len(partes) > 0:
                                        primer_nivel = partes[0]
                                        # Si es admin, puede tener submódulos
                                        if primer_nivel == 'admin' and len(partes) > 1:
                                            segundo_nivel = partes[1]
                                            if segundo_nivel == 'monitoreo':
                                                modulo = 'monitoreo'
                                            elif segundo_nivel == 'usuarios_permisos':
                                                modulo = 'gestion_usuarios'
                                            else:
                                                modulo = 'admin'
                                        else:
                                            modulo = primer_nivel
                                elif 'Proyecto Dian' in filepath:
                                    modulo = 'dian_vs_erp'
                                
                                endpoints.append({
                                    'archivo': filepath.replace('\\', '/'),
                                    'linea': i,
                                    'blueprint': bp_name,
                                    'ruta': ruta,
                                    'metodos': metodos,
                                    'modulo': modulo
                                })
                except Exception as e:
                    print(f"⚠️  Error leyendo {filepath}: {e}")
    
    print(f"\n✅ Archivos Python escaneados: {archivos_escaneados}")
    print(f"✅ Endpoints encontrados: {len(endpoints)}")
    
    return endpoints

def escanear_funcionalidades_frontend():
    """Escanea templates HTML buscando botones, formularios, llamadas AJAX"""
    print("\n" + "="*80)
    print("🎨 ESCANEANDO FUNCIONALIDADES EN TEMPLATES HTML")
    print("="*80)
    
    funcionalidades = []
    
    # Patrones a buscar
    patrones = {
        'boton': re.compile(r'<button[^>]*onclick=["\']([^"\']+)["\']'),
        'form': re.compile(r'<form[^>]*action=["\']([^"\']+)["\']'),
        'ajax': re.compile(r'fetch\(["\']([^"\']+)["\']'),
        'ajax_jquery': re.compile(r'\$\.ajax\({[^}]*url:\s*["\']([^"\']+)["\']'),
        'menu_item': re.compile(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>')
    }
    
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        print("⚠️  No se encontró carpeta 'templates'")
        return funcionalidades
    
    archivos_escaneados = 0
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if not file.endswith('.html'):
                continue
                
            filepath = os.path.join(root, file)
            archivos_escaneados += 1
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()
                    
                    # Buscar cada tipo de patrón
                    for tipo, patron in patrones.items():
                        matches = patron.findall(contenido)
                        for match in matches:
                            if tipo == 'menu_item':
                                ruta, texto = match
                                funcionalidades.append({
                                    'archivo': filepath.replace('\\', '/'),
                                    'tipo': tipo,
                                    'ruta': ruta,
                                    'descripcion': texto.strip()
                                })
                            else:
                                funcionalidades.append({
                                    'archivo': filepath.replace('\\', '/'),
                                    'tipo': tipo,
                                    'ruta': match,
                                    'descripcion': ''
                                })
            except Exception as e:
                print(f"⚠️  Error leyendo {filepath}: {e}")
    
    print(f"\n✅ Templates HTML escaneados: {archivos_escaneados}")
    print(f"✅ Funcionalidades frontend encontradas: {len(funcionalidades)}")
    
    return funcionalidades

def obtener_permisos_catalogo():
    """Obtiene TODOS los permisos del catálogo"""
    print("\n" + "="*80)
    print("📊 OBTENIENDO PERMISOS DEL CATÁLOGO")
    print("="*80)
    
    query = text("""
        SELECT id, modulo, modulo_nombre, accion, accion_descripcion, tipo_accion, es_critico
        FROM catalogo_permisos
        WHERE activo = true
        ORDER BY modulo, accion
    """)
    
    result = db.session.execute(query)
    permisos = []
    
    for row in result:
        permisos.append({
            'id': row[0],
            'modulo': row[1],
            'modulo_nombre': row[2],
            'accion': row[3],
            'descripcion': row[4],
            'tipo_accion': row[5],
            'es_critico': row[6]
        })
    
    print(f"✅ Permisos en catálogo: {len(permisos)}")
    
    # Agrupar por módulo
    por_modulo = {}
    for permiso in permisos:
        modulo = permiso['modulo']
        if modulo not in por_modulo:
            por_modulo[modulo] = []
        por_modulo[modulo].append(permiso)
    
    print("\n📋 DISTRIBUCIÓN POR MÓDULO:")
    for modulo in sorted(por_modulo.keys()):
        print(f"   - {modulo}: {len(por_modulo[modulo])} permisos")
    
    return permisos, por_modulo

def analizar_endpoint(ruta, metodos):
    """Analiza un endpoint y sugiere nombre de acción para permiso"""
    ruta_limpia = ruta.strip('/')
    
    # Mapeo de patrones comunes
    mapeos = {
        'crear': ['crear', 'add', 'nuevo', 'registrar'],
        'editar': ['editar', 'actualizar', 'update', 'modificar'],
        'eliminar': ['eliminar', 'delete', 'borrar', 'remove'],
        'ver': ['ver', 'visualizar', 'view', 'detalle'],
        'listar': ['listar', 'list', 'api/listar', 'todos'],
        'exportar': ['exportar', 'export', 'descargar'],
        'buscar': ['buscar', 'search', 'consultar'],
        'aprobar': ['aprobar', 'approve', 'validar'],
        'rechazar': ['rechazar', 'reject'],
        'acceder_modulo': ['', '/', 'dashboard', 'index']
    }
    
    ruta_lower = ruta_limpia.lower()
    
    for accion, palabras in mapeos.items():
        for palabra in palabras:
            if palabra in ruta_lower:
                return accion
    
    # Si no hay match, extraer última parte de la ruta
    partes = ruta_limpia.split('/')
    ultima_parte = partes[-1] if partes else 'accion'
    
    # Limpiar parámetros <int:id>, etc.
    ultima_parte = re.sub(r'<[^>]+>', '', ultima_parte)
    
    return ultima_parte or 'accion'

def comparar_endpoints_con_permisos(endpoints, permisos_catalogo, por_modulo):
    """Compara endpoints encontrados con permisos existentes"""
    print("\n" + "="*80)
    print("🔍 COMPARANDO ENDPOINTS CON PERMISOS")
    print("="*80)
    
    permisos_faltantes = []
    endpoints_sin_permiso = []
    
    # Agrupar endpoints por módulo
    endpoints_por_modulo = {}
    for endpoint in endpoints:
        modulo = endpoint['modulo']
        if modulo not in endpoints_por_modulo:
            endpoints_por_modulo[modulo] = []
        endpoints_por_modulo[modulo].append(endpoint)
    
    print(f"\n📊 ENDPOINTS POR MÓDULO:")
    for modulo in sorted(endpoints_por_modulo.keys()):
        count = len(endpoints_por_modulo[modulo])
        permisos_count = len(por_modulo.get(modulo, []))
        print(f"   - {modulo}: {count} endpoints | {permisos_count} permisos en catálogo")
    
    # Analizar cada módulo
    for modulo, endpoints_modulo in endpoints_por_modulo.items():
        permisos_modulo = por_modulo.get(modulo, [])
        acciones_existentes = [p['accion'] for p in permisos_modulo]
        
        for endpoint in endpoints_modulo:
            accion_sugerida = analizar_endpoint(endpoint['ruta'], endpoint['metodos'])
            
            # Verificar si existe permiso para esta acción
            if accion_sugerida not in acciones_existentes:
                endpoints_sin_permiso.append({
                    'modulo': modulo,
                    'endpoint': endpoint['ruta'],
                    'metodos': endpoint['metodos'],
                    'accion_sugerida': accion_sugerida,
                    'archivo': endpoint['archivo']
                })
    
    print(f"\n⚠️  ENDPOINTS SIN PERMISO: {len(endpoints_sin_permiso)}")
    
    return endpoints_sin_permiso

def generar_reporte_completo(endpoints, funcionalidades, permisos, por_modulo, endpoints_sin_permiso):
    """Genera reporte completo en Markdown"""
    print("\n" + "="*80)
    print("📝 GENERANDO REPORTE COMPLETO")
    print("="*80)
    
    with open('REPORTE_ENDPOINTS_Y_PERMISOS.md', 'w', encoding='utf-8') as f:
        f.write("# 🔍 REPORTE COMPLETO DE ENDPOINTS Y PERMISOS\n")
        f.write(f"**Fecha:** {os.popen('date /t').read().strip()} - {os.popen('time /t').read().strip()}\n\n")
        f.write("---\n\n")
        
        # Resumen
        f.write("## 📊 RESUMEN EJECUTIVO\n\n")
        f.write(f"- **Endpoints backend encontrados:** {len(endpoints)}\n")
        f.write(f"- **Funcionalidades frontend encontradas:** {len(funcionalidades)}\n")
        f.write(f"- **Permisos en catálogo:** {len(permisos)}\n")
        f.write(f"- **Módulos con permisos:** {len(por_modulo)}\n")
        f.write(f"- **⚠️ Endpoints SIN permiso:** {len(endpoints_sin_permiso)}\n\n")
        
        # Endpoints por módulo
        f.write("---\n\n## 📂 ENDPOINTS POR MÓDULO\n\n")
        
        endpoints_por_modulo = {}
        for endpoint in endpoints:
            modulo = endpoint['modulo']
            if modulo not in endpoints_por_modulo:
                endpoints_por_modulo[modulo] = []
            endpoints_por_modulo[modulo].append(endpoint)
        
        for modulo in sorted(endpoints_por_modulo.keys()):
            endpoints_modulo = endpoints_por_modulo[modulo]
            permisos_count = len(por_modulo.get(modulo, []))
            
            f.write(f"### {modulo.upper()} ({len(endpoints_modulo)} endpoints | {permisos_count} permisos)\n\n")
            f.write("| Ruta | Métodos | Archivo | Línea |\n")
            f.write("|------|---------|---------|-------|\n")
            
            for ep in sorted(endpoints_modulo, key=lambda x: x['ruta']):
                metodos = ', '.join(ep['metodos'])
                archivo_corto = ep['archivo'].split('/')[-1]
                f.write(f"| `{ep['ruta']}` | {metodos} | {archivo_corto} | {ep['linea']} |\n")
            
            f.write("\n")
        
        # Endpoints sin permiso
        if endpoints_sin_permiso:
            f.write("---\n\n## ⚠️ ENDPOINTS SIN PERMISO EN CATÁLOGO\n\n")
            f.write("Estos endpoints NO tienen un permiso correspondiente en `catalogo_permisos`:\n\n")
            
            sin_permiso_por_modulo = {}
            for ep in endpoints_sin_permiso:
                modulo = ep['modulo']
                if modulo not in sin_permiso_por_modulo:
                    sin_permiso_por_modulo[modulo] = []
                sin_permiso_por_modulo[modulo].append(ep)
            
            for modulo in sorted(sin_permiso_por_modulo.keys()):
                eps = sin_permiso_por_modulo[modulo]
                f.write(f"### {modulo.upper()} ({len(eps)} faltantes)\n\n")
                f.write("| Endpoint | Métodos | Acción Sugerida |\n")
                f.write("|----------|---------|------------------|\n")
                
                for ep in sorted(eps, key=lambda x: x['endpoint']):
                    metodos = ', '.join(ep['metodos'])
                    f.write(f"| `{ep['endpoint']}` | {metodos} | `{ep['accion_sugerida']}` |\n")
                
                f.write("\n")
        
        # Funcionalidades frontend
        f.write("---\n\n## 🎨 FUNCIONALIDADES FRONTEND\n\n")
        
        if funcionalidades:
            func_por_tipo = {}
            for func in funcionalidades:
                tipo = func['tipo']
                if tipo not in func_por_tipo:
                    func_por_tipo[tipo] = []
                func_por_tipo[tipo].append(func)
            
            for tipo in sorted(func_por_tipo.keys()):
                funcs = func_por_tipo[tipo]
                f.write(f"### {tipo.upper()} ({len(funcs)} encontrados)\n\n")
                f.write("| Archivo | Ruta/Función | Descripción |\n")
                f.write("|---------|--------------|-------------|\n")
                
                for func in funcs[:50]:  # Limitar a 50 por tipo
                    archivo_corto = func['archivo'].split('/')[-1]
                    desc = func['descripcion'][:50] if func['descripcion'] else '-'
                    f.write(f"| {archivo_corto} | `{func['ruta'][:40]}` | {desc} |\n")
                
                if len(funcs) > 50:
                    f.write(f"\n*(Mostrando 50 de {len(funcs)} - ver archivo completo para detalles)*\n")
                
                f.write("\n")
        
        # Permisos actuales
        f.write("---\n\n## 📋 PERMISOS EN CATÁLOGO (171 totales)\n\n")
        
        for modulo in sorted(por_modulo.keys()):
            permisos_modulo = por_modulo[modulo]
            f.write(f"### {modulo.upper()} ({len(permisos_modulo)} permisos)\n\n")
            f.write("| ID | Acción | Descripción | Tipo | Crítico |\n")
            f.write("|----|--------|-------------|------|--------|\n")
            
            for permiso in permisos_modulo:
                desc = permiso['descripcion'][:50] if permiso['descripcion'] else '-'
                tipo = permiso['tipo_accion'] or '-'
                critico = '✅' if permiso['es_critico'] else '❌'
                f.write(f"| {permiso['id']} | `{permiso['accion']}` | {desc} | {tipo} | {critico} |\n")
            
            f.write("\n")
    
    print(f"✅ Reporte generado: REPORTE_ENDPOINTS_Y_PERMISOS.md")

def generar_sql_permisos_faltantes(endpoints_sin_permiso):
    """Genera SQL INSERT para agregar permisos faltantes"""
    print("\n" + "="*80)
    print("🛠️  GENERANDO SQL PARA PERMISOS FALTANTES")
    print("="*80)
    
    if not endpoints_sin_permiso:
        print("✅ No hay permisos faltantes - sistema completo!")
        return
    
    with open('AGREGAR_PERMISOS_FALTANTES.sql', 'w', encoding='utf-8') as f:
        f.write("-- ============================================================================\n")
        f.write("-- SQL PARA AGREGAR PERMISOS FALTANTES AL CATÁLOGO\n")
        f.write(f"-- Fecha: {os.popen('date /t').read().strip()} - {os.popen('time /t').read().strip()}\n")
        f.write(f"-- Total de permisos a agregar: {len(endpoints_sin_permiso)}\n")
        f.write("-- ============================================================================\n\n")
        
        # Agrupar por módulo
        por_modulo = {}
        for ep in endpoints_sin_permiso:
            modulo = ep['modulo']
            if modulo not in por_modulo:
                por_modulo[modulo] = []
            por_modulo[modulo].append(ep)
        
        # Generar INSERTs por módulo
        for modulo in sorted(por_modulo.keys()):
            eps = por_modulo[modulo]
            f.write(f"-- ----------------------------------------------------------------------------\n")
            f.write(f"-- MÓDULO: {modulo.upper()} ({len(eps)} permisos)\n")
            f.write(f"-- ----------------------------------------------------------------------------\n\n")
            
            for ep in sorted(eps, key=lambda x: x['accion_sugerida']):
                accion = ep['accion_sugerida']
                endpoint = ep['endpoint']
                metodos = ', '.join(ep['metodos'])
                
                # Generar descripción automática
                if accion == 'acceder_modulo':
                    descripcion = f"Acceder al módulo {modulo}"
                elif accion == 'crear':
                    descripcion = f"Crear nuevo registro en {modulo}"
                elif accion == 'editar':
                    descripcion = f"Editar registros en {modulo}"
                elif accion == 'eliminar':
                    descripcion = f"Eliminar registros en {modulo}"
                elif accion == 'ver':
                    descripcion = f"Ver detalles de registros en {modulo}"
                elif accion == 'listar':
                    descripcion = f"Listar registros de {modulo}"
                elif accion == 'exportar':
                    descripcion = f"Exportar datos de {modulo}"
                elif accion == 'buscar':
                    descripcion = f"Buscar registros en {modulo}"
                else:
                    descripcion = f"Acción {accion} en {modulo}"
                
                # Determinar tipo y criticidad
                tipo_accion = 'lectura' if 'GET' in ep['metodos'] and len(ep['metodos']) == 1 else 'escritura'
                es_critico = 'true' if accion in ['eliminar', 'aprobar', 'rechazar'] else 'false'
                
                f.write(f"INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)\n")
                f.write(f"VALUES ('{modulo}', '{modulo.replace('_', ' ').title()}', 'Módulo {modulo}', '{accion}', '{descripcion}', '{tipo_accion}', {es_critico}, true, NOW())\n")
                f.write(f"ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: {metodos} {endpoint}\n\n")
            
            f.write("\n")
        
        f.write("-- ============================================================================\n")
        f.write("-- FIN DEL SCRIPT\n")
        f.write("-- ============================================================================\n")
    
    print(f"✅ SQL generado: AGREGAR_PERMISOS_FALTANTES.sql")

def main():
    """Función principal"""
    print("\n" + "="*80)
    print("🚀 ESCÁNER COMPLETO DE FUNCIONALIDADES Y PERMISOS")
    print("="*80)
    print("Sistema: Gestor Documental - Supertiendas Cañaveral")
    print("Fecha: 11 de Diciembre, 2025")
    print("="*80)
    
    with app.app_context():
        # 1. Escanear endpoints backend
        endpoints = escanear_endpoints_python()
        
        # 2. Escanear funcionalidades frontend
        funcionalidades = escanear_funcionalidades_frontend()
        
        # 3. Obtener permisos del catálogo
        permisos, por_modulo = obtener_permisos_catalogo()
        
        # 4. Comparar y encontrar faltantes
        endpoints_sin_permiso = comparar_endpoints_con_permisos(endpoints, permisos, por_modulo)
        
        # 5. Generar reporte completo
        generar_reporte_completo(endpoints, funcionalidades, permisos, por_modulo, endpoints_sin_permiso)
        
        # 6. Generar SQL para permisos faltantes
        generar_sql_permisos_faltantes(endpoints_sin_permiso)
    
    print("\n" + "="*80)
    print("✅ ESCANEO COMPLETO TERMINADO")
    print("="*80)
    print("\n📄 Archivos generados:")
    print("   1. REPORTE_ENDPOINTS_Y_PERMISOS.md  (Reporte completo)")
    print("   2. AGREGAR_PERMISOS_FALTANTES.sql   (SQL para agregar permisos)")
    print("\n💡 Siguiente paso: Revisar el reporte y ejecutar el SQL si es necesario.\n")

if __name__ == "__main__":
    main()
