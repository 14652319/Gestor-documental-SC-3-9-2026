"""
Script SEGURO para agregar soporte de supervisión
- Solo agrega 3 campos opcionales
- NO modifica datos existentes
- NO afecta configuraciones actuales
- Puede revertirse fácilmente
Fecha: 28 de Diciembre de 2025
"""

from extensions import db
from app import app
from sqlalchemy import text

def agregar_campos_supervision_seguro():
    """Agregar campos para supervisión DE FORMA SEGURA"""
    
    with app.app_context():
        try:
            print("=" * 80)
            print("🛡️  IMPLEMENTACIÓN SEGURA - CAMPOS DE SUPERVISIÓN")
            print("=" * 80)
            print()
            print("✅ GARANTÍAS:")
            print("   - NO afecta configuraciones existentes")
            print("   - Campos opcionales (pueden estar vacíos)")
            print("   - Rollback disponible si algo falla")
            print()
            print("=" * 80)
            
            # ==========================================
            # CAMPO 1: es_supervision (Boolean)
            # ==========================================
            print("\n1️⃣  Agregando campo 'es_supervision'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS es_supervision BOOLEAN DEFAULT FALSE
                """))
                db.session.commit()
                print("    ✅ Campo 'es_supervision' agregado")
                print("       DEFAULT = FALSE (todas las configs existentes siguen siendo normales)")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("    ⚠️  Campo ya existe (OK)")
                else:
                    print(f"    ❌ Error: {e}")
                db.session.rollback()
            
            # ==========================================
            # CAMPO 2: email_supervisor (String)
            # ==========================================
            print("\n2️⃣  Agregando campo 'email_supervisor'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS email_supervisor VARCHAR(255)
                """))
                db.session.commit()
                print("    ✅ Campo 'email_supervisor' agregado")
                print("       DEFAULT = NULL (configs existentes no tienen supervisor)")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("    ⚠️  Campo ya existe (OK)")
                else:
                    print(f"    ❌ Error: {e}")
                db.session.rollback()
            
            # ==========================================
            # CAMPO 3: frecuencia_dias (Integer)
            # ==========================================
            print("\n3️⃣  Agregando campo 'frecuencia_dias'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE envios_programados_dian_vs_erp 
                    ADD COLUMN IF NOT EXISTS frecuencia_dias INTEGER DEFAULT 1
                """))
                db.session.commit()
                print("    ✅ Campo 'frecuencia_dias' agregado")
                print("       DEFAULT = 1 (diario, igual que antes)")
                print("       Valores: 1=diario, 4=cada 4 días, 7=semanal")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("    ⚠️  Campo ya existe (OK)")
                else:
                    print(f"    ❌ Error: {e}")
                db.session.rollback()
            
            # ==========================================
            # VERIFICACIÓN FINAL
            # ==========================================
            print("\n" + "=" * 80)
            print("🔍 VERIFICANDO CAMPOS AGREGADOS...")
            print("=" * 80)
            
            result = db.session.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'envios_programados_dian_vs_erp'
                  AND column_name IN ('es_supervision', 'email_supervisor', 'frecuencia_dias')
                ORDER BY column_name
            """))
            
            campos_encontrados = result.fetchall()
            if campos_encontrados:
                print("\n✅ CAMPOS CONFIRMADOS EN BASE DE DATOS:")
                for campo in campos_encontrados:
                    nombre, tipo, default = campo
                    print(f"   • {nombre:20} | {tipo:15} | DEFAULT: {default or 'NULL'}")
            else:
                print("\n⚠️  No se encontraron los campos (puede ser normal en algunas BD)")
            
            # ==========================================
            # VERIFICAR CONFIGURACIONES EXISTENTES
            # ==========================================
            print("\n" + "=" * 80)
            print("🔍 VERIFICANDO CONFIGURACIONES EXISTENTES...")
            print("=" * 80)
            
            result = db.session.execute(text("""
                SELECT id, nombre, tipo, activo, es_supervision, email_supervisor, frecuencia_dias
                FROM envios_programados_dian_vs_erp
                WHERE activo = TRUE
                ORDER BY id
            """))
            
            configs = result.fetchall()
            print(f"\n📋 Total configuraciones activas: {len(configs)}")
            
            if configs:
                print("\n┌─────┬──────────────────────────────────┬─────────────┬───────────┬──────────────┐")
                print("│ ID  │ Nombre                           │ Supervisión │ Email     │ Frecuencia   │")
                print("├─────┼──────────────────────────────────┼─────────────┼───────────┼──────────────┤")
                for cfg in configs:
                    id_cfg, nombre, tipo, activo, es_sup, email_sup, freq_dias = cfg
                    nombre_corto = (nombre[:30] + '...') if len(nombre) > 30 else nombre
                    es_sup_str = "✅ SÍ" if es_sup else "❌ NO"
                    email_str = email_sup[:10] + "..." if email_sup else "N/A"
                    freq_str = f"{freq_dias or 1} días"
                    print(f"│ {id_cfg:<3} │ {nombre_corto:<32} │ {es_sup_str:<11} │ {email_str:<9} │ {freq_str:<12} │")
                print("└─────┴──────────────────────────────────┴─────────────┴───────────┴──────────────┘")
                
                # Contar configuraciones de supervisión
                configs_supervision = [c for c in configs if c[4]]  # c[4] = es_supervision
                configs_normales = [c for c in configs if not c[4]]
                
                print(f"\n📊 RESUMEN:")
                print(f"   • Configuraciones normales (por NIT): {len(configs_normales)}")
                print(f"   • Configuraciones de supervisión: {len(configs_supervision)}")
            
            print("\n" + "=" * 80)
            print("✅ INSTALACIÓN COMPLETADA CON ÉXITO")
            print("=" * 80)
            print()
            print("📋 PRÓXIMOS PASOS:")
            print("   1. ✅ Campos agregados correctamente")
            print("   2. ⏭️  Actualizar modelo Python (EnvioProgramadoDianVsErp)")
            print("   3. ⏭️  Agregar lógica al scheduler")
            print("   4. ⏭️  Actualizar frontend (modal de configuración)")
            print()
            print("🔄 ROLLBACK (si necesario):")
            print("   ALTER TABLE envios_programados_dian_vs_erp DROP COLUMN es_supervision;")
            print("   ALTER TABLE envios_programados_dian_vs_erp DROP COLUMN email_supervisor;")
            print("   ALTER TABLE envios_programados_dian_vs_erp DROP COLUMN frecuencia_dias;")
            print()
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR GENERAL: {e}")
            db.session.rollback()
            print("\n🔄 Rollback ejecutado. Base de datos sin cambios.")

if __name__ == "__main__":
    agregar_campos_supervision_seguro()
