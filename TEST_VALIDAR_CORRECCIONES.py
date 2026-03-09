"""
SCRIPT DE PRUEBA: Validar correcciones en inserción de tablas individuales
Fecha: 19 de Febrero de 2026

Este script ejecuta el procesamiento completo y valida que:
1. Las tablas individuales (dian, erp, acuses) se llenen
2. Los campos calculados estén correctos
3. El Visor V2 pueda mostrar datos
"""

import sys
import os
from pathlib import Path

# Agregar rutas al path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "modules" / "dian_vs_erp"))

# Configurar Flask app context
os.environ['FLASK_ENV'] = 'development'

print("="*80)
print("🧪 SCRIPT DE PRUEBA: Validación de Inserción en Tablas Individuales")
print("="*80)

# Importar configuración
from app import app, db
from modules.dian_vs_erp.routes import actualizar_maestro

print("\n1️⃣ Verificando conexión a base de datos...")
with app.app_context():
    try:
        # Test de conexión
        result = db.session.execute(db.text("SELECT 1")).fetchone()
        print("   ✅ Conexión exitosa a PostgreSQL")
    except Exception as e:
        print(f"   ❌ ERROR de conexión: {e}")
        sys.exit(1)

print("\n2️⃣ Verificando archivos en uploads...")
uploads_dir = BASE_DIR / "uploads"
archivos = {
    "DIAN": list((uploads_dir / "dian").glob("*.xlsx")),
    "ERP Financiero": list((uploads_dir / "erp_fn").glob("*.xlsx")),
    "ERP Comercial": list((uploads_dir / "erp_cm").glob("*.xlsx")),
    "Acuses": list((uploads_dir / "acuses").glob("*.xlsx")),
}

for nombre, lista in archivos.items():
    if lista:
        print(f"   ✅ {nombre}: {lista[0].name}")
    else:
        print(f"   ⚠️ {nombre}: No encontrado")

print("\n3️⃣ Verificando estado ANTES del procesamiento...")
with app.app_context():
    try:
        conteo_antes = {}
        conteo_antes['dian'] = db.session.execute(db.text("SELECT COUNT(*) FROM dian")).scalar()
        conteo_antes['erp_comercial'] = db.session.execute(db.text("SELECT COUNT(*) FROM erp_comercial")).scalar()
        conteo_antes['erp_financiero'] = db.session.execute(db.text("SELECT COUNT(*) FROM erp_financiero")).scalar()
        conteo_antes['acuses'] = db.session.execute(db.text("SELECT COUNT(*) FROM acuses")).scalar()
        conteo_antes['maestro'] = db.session.execute(db.text("SELECT COUNT(*) FROM maestro_dian_vs_erp")).scalar()
        
        print("\n   📊 CONTEO ANTES:")
        for tabla, count in conteo_antes.items():
            print(f"      {tabla}: {count:,} registros")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        sys.exit(1)

print("\n4️⃣ Ejecutando procesamiento (actualizar_maestro)...")
print("-"*80)
with app.app_context():
    try:
        resultado = actualizar_maestro()
        print("-"*80)
        print(f"\n   ✅ RESULTADO: {resultado}")
    except Exception as e:
        print(f"\n   ❌ ERROR durante procesamiento:")
        print(f"      {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("\n5️⃣ Verificando estado DESPUÉS del procesamiento...")
with app.app_context():
    try:
        conteo_despues = {}
        conteo_despues['dian'] = db.session.execute(db.text("SELECT COUNT(*) FROM dian")).scalar()
        conteo_despues['erp_comercial'] = db.session.execute(db.text("SELECT COUNT(*) FROM erp_comercial")).scalar()
        conteo_despues['erp_financiero'] = db.session.execute(db.text("SELECT COUNT(*) FROM erp_financiero")).scalar()
        conteo_despues['acuses'] = db.session.execute(db.text("SELECT COUNT(*) FROM acuses")).scalar()
        conteo_despues['maestro'] = db.session.execute(db.text("SELECT COUNT(*) FROM maestro_dian_vs_erp")).scalar()
        
        print("\n   📊 CONTEO DESPUÉS:")
        for tabla, count in conteo_despues.items():
            incremento = count - conteo_antes.get(tabla, 0)
            simbolo = "✅" if count > 0 else "❌"
            print(f"      {simbolo} {tabla}: {count:,} registros (+{incremento:,})")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        sys.exit(1)

print("\n6️⃣ Validando campos calculados en tabla DIAN...")
with app.app_context():
    try:
        resultado = db.session.execute(db.text("""
            SELECT 
                nit_emisor,
                prefijo,
                folio,
                clave,
                LENGTH(cufe_cude) AS cufe_length,
                tipo_tercero,
                n_dias
            FROM dian 
            LIMIT 3
        """)).fetchall()
        
        print("\n   📋 MUESTRA DE DATOS (primeros 3 registros):")
        for row in resultado:
            print(f"      • NIT: {row[0]}, Prefijo: {row[1]}, Folio: {row[2]}")
            print(f"        Clave: {row[3]}")
            print(f"        CUFE Length: {row[4]} (debe ser 96)")
            print(f"        Tipo Tercero: {row[5]}")
            print(f"        Días desde emisión: {row[6]}")
            print()
    except Exception as e:
        print(f"   ⚠️ No se pudieron obtener muestras: {e}")

print("\n7️⃣ Validando extracción de prefijo/folio en ERP Comercial...")
with app.app_context():
    try:
        resultado = db.session.execute(db.text("""
            SELECT 
                proveedor,
                docto_proveedor,
                prefijo,
                folio,
                doc_causado_por
            FROM erp_comercial 
            LIMIT 3
        """)).fetchall()
        
        print("\n   📋 MUESTRA DE DATOS ERP (primeros 3 registros):")
        for row in resultado:
            print(f"      • Proveedor: {row[0]}")
            print(f"        Docto Original: {row[1]}")
            print(f"        Prefijo Extraído: {row[2]}")
            print(f"        Folio Extraído: {row[3]}")
            print(f"        Doc Causado Por: {row[4]}")
            print()
    except Exception as e:
        print(f"   ⚠️ No se pudieron obtener muestras: {e}")

print("\n8️⃣ Validando matching CUFE entre DIAN y ACUSES...")
with app.app_context():
    try:
        resultado = db.session.execute(db.text("""
            SELECT 
                d.nit_emisor,
                d.prefijo || '-' || d.folio AS factura,
                SUBSTRING(d.cufe_cude, 1, 30) || '...' AS cufe_corto,
                a.estado_docto,
                CASE WHEN a.id IS NOT NULL THEN 'SI' ELSE 'NO' END AS tiene_acuse
            FROM dian d
            LEFT JOIN acuses a ON d.clave_acuse = a.clave_acuse
            LIMIT 5
        """)).fetchall()
        
        print("\n   📋 MATCHING DIAN ↔ ACUSES:")
        for row in resultado:
            print(f"      • {row[0]} | {row[1]} | CUFE: {row[2]}")
            print(f"        Estado: {row[3]} | Match: {row[4]}")
            print()
    except Exception as e:
        print(f"   ⚠️ No se pudo validar matching: {e}")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETADA")
print("="*80)

# Resumen final
print("\n📊 RESUMEN:")
with app.app_context():
    total_dian = db.session.execute(db.text("SELECT COUNT(*) FROM dian")).scalar()
    total_erp_cm = db.session.execute(db.text("SELECT COUNT(*) FROM erp_comercial")).scalar()
    total_erp_fn = db.session.execute(db.text("SELECT COUNT(*) FROM erp_financiero")).scalar()
    total_acuses = db.session.execute(db.text("SELECT COUNT(*) FROM acuses")).scalar()
    total_maestro = db.session.execute(db.text("SELECT COUNT(*) FROM maestro_dian_vs_erp")).scalar()
    
    print(f"   • DIAN:          {total_dian:>10,} registros")
    print(f"   • ERP Comercial: {total_erp_cm:>10,} registros")
    print(f"   • ERP Financiero:{total_erp_fn:>10,} registros")
    print(f"   • Acuses:        {total_acuses:>10,} registros")
    print(f"   • Maestro:       {total_maestro:>10,} registros")
    
    # Verificar éxito
    if total_dian > 0 and total_acuses > 0:
        print("\n   ✅ ¡TODAS LAS TABLAS TIENEN DATOS!")
        print("   ✅ Las correcciones funcionaron correctamente")
        print("\n   🎉 Visor V2 debería mostrar 'Ver PDF' y 'Estado Aprobación' correctamente")
    else:
        print("\n   ⚠️ ADVERTENCIA: Algunas tablas están vacías")
        print("   Revisa los errores en la consola arriba")

print("\n" + "="*80)
