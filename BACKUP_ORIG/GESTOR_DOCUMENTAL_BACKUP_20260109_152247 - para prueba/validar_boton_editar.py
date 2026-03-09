# -*- coding: utf-8 -*-
"""
Script de Validación: Botón Editar Facturas
Fecha: 8 Diciembre 2025
Propósito: Verificar que las 3 correcciones estén funcionando correctamente
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def validar_session_tipo_usuario():
    """Valida que el código de login incluya session['tipo_usuario']"""
    print("\n" + "="*80)
    print("🔍 VALIDACIÓN 1: Verificar session['tipo_usuario'] en app.py")
    print("="*80)
    
    with open('app.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
        
    # Buscar la línea específica
    if "session['tipo_usuario']" in contenido:
        print("✅ CORRECTO: session['tipo_usuario'] encontrado en app.py")
        
        # Encontrar la línea exacta
        lineas = contenido.split('\n')
        for i, linea in enumerate(lineas, 1):
            if "session['tipo_usuario']" in linea:
                print(f"   📍 Línea {i}: {linea.strip()}")
        return True
    else:
        print("❌ ERROR: session['tipo_usuario'] NO encontrado en app.py")
        print("   💡 Acción requerida: Agregar línea 1277 en endpoint /api/auth/login")
        return False

def validar_dashboard_html():
    """Valida cambios en dashboard.html"""
    print("\n" + "="*80)
    print("🔍 VALIDACIÓN 2: Verificar cambios en dashboard.html")
    print("="*80)
    
    archivo = 'templates/facturas_digitales/dashboard.html'
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    checks = {
        'empresa_null': {
            'patron': "empresa: {{ 'null' if not factura.empresa",
            'descripcion': 'Valor NULL para empresa (lógica JavaScript)'
        },
        'empresa_display': {
            'patron': "empresa_display: '{{ factura.empresa|default('N/A') }}'",
            'descripcion': 'Valor display para empresa (UI)'
        },
        'departamento_null': {
            'patron': "departamento: {{ 'null' if not factura.departamento",
            'descripcion': 'Valor NULL para departamento (lógica JavaScript)'
        },
        'departamento_display': {
            'patron': "departamento_display: '{{ factura.departamento|default('N/A') }}'",
            'descripcion': 'Valor display para departamento (UI)'
        },
        'condicion_boton': {
            'patron': '(!factura.empresa || !factura.departamento)',
            'descripcion': 'Condición del botón Editar'
        },
        'render_empresa_display': {
            'patron': '${factura.empresa_display}',
            'descripcion': 'Renderizado usa empresa_display'
        },
        'render_depto_display': {
            'patron': '${factura.departamento_display}',
            'descripcion': 'Renderizado usa departamento_display'
        },
        'filtro_empresa_display': {
            'patron': 'factura.empresa_display.toLowerCase()',
            'descripcion': 'Filtro usa empresa_display'
        },
        'filtro_depto_display': {
            'patron': 'factura.departamento_display.toLowerCase()',
            'descripcion': 'Filtro usa departamento_display'
        }
    }
    
    resultados = {}
    for key, check in checks.items():
        if check['patron'] in contenido:
            print(f"✅ {check['descripcion']}")
            resultados[key] = True
        else:
            print(f"❌ {check['descripcion']}")
            resultados[key] = False
    
    return all(resultados.values())

def validar_facturas_sin_empresa_departamento():
    """Consulta facturas que deberían mostrar el botón Editar"""
    print("\n" + "="*80)
    print("🔍 VALIDACIÓN 3: Facturas sin Empresa o Departamento en BD")
    print("="*80)
    
    try:
        with app.app_context():
            query = text("""
                SELECT 
                    id,
                    numero_factura,
                    nit_proveedor,
                    razon_social_proveedor,
                    empresa,
                    departamento,
                    estado,
                    fecha_carga
                FROM facturas_digitales
                WHERE (empresa IS NULL OR departamento IS NULL)
                ORDER BY fecha_carga DESC
                LIMIT 10
            """)
            
            result = db.session.execute(query)
            facturas = result.fetchall()
            
            if facturas:
                print(f"✅ Encontradas {len(facturas)} facturas con campos faltantes:")
                print("\n" + "-"*80)
                for f in facturas:
                    print(f"\n📄 Factura ID: {f.id}")
                    print(f"   Número: {f.numero_factura}")
                    print(f"   Proveedor: {f.razon_social_proveedor} (NIT: {f.nit_proveedor})")
                    print(f"   Empresa: {f.empresa if f.empresa else '❌ NULL'}")
                    print(f"   Departamento: {f.departamento if f.departamento else '❌ NULL'}")
                    print(f"   Estado: {f.estado}")
                    print(f"   Fecha: {f.fecha_carga}")
                    print(f"   👉 Botón Editar DEBERÍA aparecer para usuarios interno/admin")
                
                return True
            else:
                print("⚠️ No se encontraron facturas con campos faltantes")
                print("   💡 Esto es normal si todas las facturas están completas")
                return True
                
    except Exception as e:
        print(f"❌ ERROR al consultar base de datos: {str(e)}")
        return False

def validar_usuarios_y_tipos():
    """Valida usuarios y sus tipos"""
    print("\n" + "="*80)
    print("🔍 VALIDACIÓN 4: Usuarios y Tipos")
    print("="*80)
    
    try:
        with app.app_context():
            # Contar usuarios por rol
            query = text("""
                SELECT 
                    rol,
                    COUNT(*) as cantidad
                FROM usuarios
                WHERE activo = true
                GROUP BY rol
                ORDER BY rol
            """)
            
            result = db.session.execute(query)
            roles = result.fetchall()
            
            print("\n📊 Usuarios activos por rol:")
            for r in roles:
                print(f"   {r.rol}: {r.cantidad} usuario(s)")
            
            # Ejemplos de cada tipo
            print("\n👥 Ejemplos de usuarios:")
            
            query_externos = text("""
                SELECT usuario, rol
                FROM usuarios
                WHERE rol = 'externo' AND activo = true
                LIMIT 3
            """)
            externos = db.session.execute(query_externos).fetchall()
            
            if externos:
                print("\n   🔸 Externos (NO deberían ver botón Editar):")
                for u in externos:
                    print(f"      - Usuario: {u.usuario}")
            
            query_internos = text("""
                SELECT usuario, rol
                FROM usuarios
                WHERE rol IN ('admin', 'interno') AND activo = true
                LIMIT 3
            """)
            internos = db.session.execute(query_internos).fetchall()
            
            if internos:
                print("\n   🔹 Internos/Admin (SÍ deberían ver botón Editar):")
                for u in internos:
                    print(f"      - Usuario: {u.usuario}, Rol: {u.rol}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR al consultar usuarios: {str(e)}")
        return False

def main():
    """Función principal que ejecuta todas las validaciones"""
    print("\n" + "="*80)
    print("🧪 VALIDACIÓN COMPLETA: CORRECCIONES BOTÓN EDITAR")
    print("="*80)
    print("📅 Fecha: 8 Diciembre 2025")
    print("🎯 Objetivo: Verificar que las 3 correcciones estén funcionando")
    print("="*80)
    
    resultados = {
        'session': validar_session_tipo_usuario(),
        'dashboard': validar_dashboard_html(),
        'facturas': validar_facturas_sin_empresa_departamento(),
        'usuarios': validar_usuarios_y_tipos()
    }
    
    print("\n" + "="*80)
    print("📋 RESUMEN DE VALIDACIONES")
    print("="*80)
    
    for nombre, resultado in resultados.items():
        estado = "✅ CORRECTO" if resultado else "❌ ERROR"
        print(f"{estado} - {nombre.upper()}")
    
    print("\n" + "="*80)
    
    if all(resultados.values()):
        print("✅ TODAS LAS VALIDACIONES PASARON CORRECTAMENTE")
        print("\n📝 Próximos pasos:")
        print("   1. Reiniciar servidor Flask: python app.py")
        print("   2. Probar login con usuario interno/admin")
        print("   3. Verificar que botón Editar aparece en facturas con campos faltantes")
        print("   4. Probar login con usuario externo")
        print("   5. Verificar que botón Editar NO aparece para externos")
    else:
        print("❌ ALGUNAS VALIDACIONES FALLARON")
        print("\n📝 Acciones requeridas:")
        print("   1. Revisar mensajes de error arriba")
        print("   2. Aplicar correcciones necesarias")
        print("   3. Ejecutar este script nuevamente")
    
    print("="*80 + "\n")
    
    return all(resultados.values())

if __name__ == '__main__':
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
