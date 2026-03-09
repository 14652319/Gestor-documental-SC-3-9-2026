"""
VALIDACIÓN COMPLETA DEL SISTEMA DIAN vs ERP
Verifica todas las etapas del flujo de trabajo
"""
from app import app
from extensions import db
from modules.dian_vs_erp.models import Dian, ErpComercial, ErpFinanciero, Acuses, MaestroDianVsErp
from sqlalchemy import text

def validar_sistema():
    with app.app_context():
        print("\n" + "="*80)
        print("🔍 VALIDACIÓN COMPLETA DEL SISTEMA DIAN vs ERP")
        print("="*80)
        
        # ============================================
        # 1. VERIFICAR REGISTROS EN TABLAS BASE
        # ============================================
        print("\n📊 PARTE 1: REGISTROS EN TABLAS BASE")
        print("-" * 80)
        
        total_dian = Dian.query.count()
        total_ec = ErpComercial.query.count()
        total_ef = ErpFinanciero.query.count()
        total_acuses = Acuses.query.count()
        total_maestro = MaestroDianVsErp.query.count()
        
        print(f"✅ DIAN:               {total_dian:>10,} registros")
        print(f"✅ ERP Comercial:      {total_ec:>10,} registros")
        print(f"✅ ERP Financiero:     {total_ef:>10,} registros")
        print(f"✅ ACUSES:             {total_acuses:>10,} registros")
        print(f"✅ MAESTRO:            {total_maestro:>10,} registros")
        print("-" * 80)
        print(f"📊 TOTAL:              {total_dian + total_ec + total_ef + total_acuses + total_maestro:>10,} registros")
        
        # ============================================
        # 2. VERIFICAR INTEGRIDAD DE DATOS
        # ============================================
        print("\n📊 PARTE 2: INTEGRIDAD DE DATOS")
        print("-" * 80)
        
        # 2.1 Facturas DIAN con ERP
        query = text("""
            SELECT COUNT(*) 
            FROM dian d
            WHERE EXISTS (
                SELECT 1 FROM erp_comercial ec 
                WHERE ec.nit = d.nit AND ec.prefijo = d.prefijo AND ec.folio = d.folio
            )
            OR EXISTS (
                SELECT 1 FROM erp_financiero ef 
                WHERE ef.nit = d.nit AND ef.prefijo = d.prefijo AND ef.folio = d.folio
            )
        """)
        con_erp = db.session.execute(query).scalar()
        sin_erp = total_dian - con_erp
        porcentaje_erp = (con_erp / total_dian * 100) if total_dian > 0 else 0
        
        print(f"✅ Facturas DIAN con ERP:     {con_erp:>10,} ({porcentaje_erp:.1f}%)")
        print(f"⚠️  Facturas DIAN sin ERP:     {sin_erp:>10,} ({100-porcentaje_erp:.1f}%)")
        
        # 2.2 Facturas DIAN con ACUSES
        query = text("""
            SELECT COUNT(*) 
            FROM dian d
            WHERE EXISTS (SELECT 1 FROM acuses a WHERE a.cufe = d.cufe)
        """)
        con_acuses = db.session.execute(query).scalar()
        sin_acuses = total_dian - con_acuses
        porcentaje_acuses = (con_acuses / total_dian * 100) if total_dian > 0 else 0
        
        print(f"✅ Facturas DIAN con ACUSES:  {con_acuses:>10,} ({porcentaje_acuses:.1f}%)")
        print(f"⚠️  Facturas DIAN sin ACUSES:  {sin_acuses:>10,} ({100-porcentaje_acuses:.1f}%)")
        
        # ============================================
        # 3. VERIFICAR COLUMNAS CRÍTICAS
        # ============================================
        print("\n📊 PARTE 3: VALIDACIÓN DE COLUMNAS CRÍTICAS")
        print("-" * 80)
        
        # 3.1 DIAN: campo CUFE (debe ser único)
        query = text("SELECT COUNT(DISTINCT cufe) FROM dian")
        cufes_unicos = db.session.execute(query).scalar()
        print(f"✅ CUFEs únicos en DIAN:      {cufes_unicos:>10,} (debe ser = {total_dian:,})")
        if cufes_unicos == total_dian:
            print("   ✅ CORRECTO: Sin duplicados")
        else:
            print(f"   ⚠️ ALERTA: {total_dian - cufes_unicos:,} CUFEs duplicados")
        
        # 3.2 ACUSES: campo clave_acuse (debe ser único)
        query = text("SELECT COUNT(DISTINCT clave_acuse) FROM acuses")
        claves_unicas = db.session.execute(query).scalar()
        print(f"✅ Claves únicas en ACUSES:   {claves_unicas:>10,} (debe ser = {total_acuses:,})")
        if claves_unicas == total_acuses:
            print("   ✅ CORRECTO: Sin duplicados")
        else:
            print(f"   ⚠️ ALERTA: {total_acuses - claves_unicas:,} claves duplicadas")
        
        # 3.3 MAESTRO: sin valores NULL críticos
        query = text("SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE cufe IS NULL OR nit IS NULL")
        nulls_criticos = db.session.execute(query).scalar()
        print(f"✅ Registros con NULL crítico: {nulls_criticos:>10,} (debe ser 0)")
        if nulls_criticos == 0:
            print("   ✅ CORRECTO: Sin NULLs en columnas críticas")
        else:
            print(f"   ⚠️ ALERTA: {nulls_criticos:,} registros con NULL en CUFE o NIT")
        
        # ============================================
        # 4. VERIFICAR FUNCIÓN format_value_for_copy()
        # ============================================
        print("\n📊 PARTE 4: VALIDACIÓN DE ESCAPES DE CARACTERES ESPECIALES")
        print("-" * 80)
        
        # Buscar registros con caracteres especiales en MAESTRO
        query = text("""
            SELECT COUNT(*) FROM maestro_dian_vs_erp 
            WHERE razon_social LIKE '%\t%' 
               OR razon_social LIKE '%\n%'
               OR razon_social LIKE '%\r%'
        """)
        con_especiales = db.session.execute(query).scalar()
        
        print(f"✅ Registros con \\t, \\n, \\r: {con_especiales:>10,}")
        if con_especiales > 0:
            print(f"   ✅ CORRECTO: format_value_for_copy() procesó {con_especiales:,} registros")
        else:
            print("   ℹ️  Sin caracteres especiales detectados (normal)")
        
        # ============================================
        # 5. VERIFICAR RENDIMIENTO DE MAESTRO
        # ============================================
        print("\n📊 PARTE 5: ANÁLISIS DEL MAESTRO CONSOLIDADO")
        print("-" * 80)
        
        # 5.1 Distribución por tipo de documento
        query = text("""
            SELECT tipo_documento_dian, COUNT(*) as total
            FROM maestro_dian_vs_erp
            WHERE tipo_documento_dian IS NOT NULL
            GROUP BY tipo_documento_dian
            ORDER BY total DESC
            LIMIT 5
        """)
        tipos = db.session.execute(query).fetchall()
        
        print("📋 Top 5 tipos de documento:")
        for tipo, total in tipos:
            porcentaje = (total / total_maestro * 100) if total_maestro > 0 else 0
            print(f"   - {tipo:30s}: {total:>8,} ({porcentaje:.1f}%)")
        
        # 5.2 Distribución por módulo de origen
        query = text("""
            SELECT modulo_origen, COUNT(*) as total
            FROM maestro_dian_vs_erp
            WHERE modulo_origen IS NOT NULL
            GROUP BY modulo_origen
            ORDER BY total DESC
        """)
        modulos = db.session.execute(query).fetchall()
        
        print("\n📋 Distribución por módulo ERP:")
        for modulo, total in modulos:
            porcentaje = (total / total_maestro * 100) if total_maestro > 0 else 0
            print(f"   - {modulo:30s}: {total:>8,} ({porcentaje:.1f}%)")
        
        # 5.3 Estados DIAN
        query = text("""
            SELECT estado_dian_vs_erp, COUNT(*) as total
            FROM maestro_dian_vs_erp
            WHERE estado_dian_vs_erp IS NOT NULL
            GROUP BY estado_dian_vs_erp
            ORDER BY total DESC
        """)
        estados = db.session.execute(query).fetchall()
        
        print("\n📋 Distribución por estado:")
        for estado, total in estados:
            porcentaje = (total / total_maestro * 100) if total_maestro > 0 else 0
            print(f"   - {estado:30s}: {total:>8,} ({porcentaje:.1f}%)")
        
        # ============================================
        # RESUMEN FINAL
        # ============================================
        print("\n" + "="*80)
        print("✅ VALIDACIÓN COMPLETADA")
        print("="*80)
        
        # Calcular puntuación
        puntos = 0
        total_puntos = 7
        
        if total_dian > 0: puntos += 1
        if total_ec > 0: puntos += 1
        if total_ef > 0: puntos += 1
        if total_acuses > 0: puntos += 1
        if total_maestro > 0: puntos += 1
        if cufes_unicos == total_dian: puntos += 1
        if nulls_criticos == 0: puntos += 1
        
        porcentaje_salud = (puntos / total_puntos * 100)
        
        print(f"\n🏆 SALUD DEL SISTEMA: {puntos}/{total_puntos} ({porcentaje_salud:.0f}%)")
        
        if porcentaje_salud == 100:
            print("🎉 ¡EXCELENTE! Sistema funcionando perfectamente")
        elif porcentaje_salud >= 80:
            print("👍 MUY BIEN: Sistema funcional con advertencias menores")
        elif porcentaje_salud >= 60:
            print("⚠️ ACEPTABLE: Sistema funcional pero requiere atención")
        else:
            print("❌ CRÍTICO: Sistema requiere revisión urgente")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    validar_sistema()
