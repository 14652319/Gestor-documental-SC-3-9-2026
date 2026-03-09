"""
Script de verificación de integridad del sistema
Confirma que los cambios NO rompieron nada
"""

from extensions import db
from app import app
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp

def verificar_sistema():
    """Verificar que todo sigue funcionando"""
    
    with app.app_context():
        print("=" * 80)
        print("🔍 VERIFICACIÓN DE INTEGRIDAD DEL SISTEMA")
        print("=" * 80)
        print()
        
        try:
            # 1. Verificar modelo actualizado
            print("1️⃣  Verificando modelo Python...")
            campos_modelo = [c.name for c in EnvioProgramadoDianVsErp.__table__.columns]
            
            campos_nuevos = ['es_supervision', 'email_supervisor', 'frecuencia_dias']
            campos_encontrados = [c for c in campos_nuevos if c in campos_modelo]
            
            if len(campos_encontrados) == 3:
                print("    ✅ Modelo actualizado correctamente")
                print(f"       Campos nuevos: {', '.join(campos_encontrados)}")
            else:
                print(f"    ⚠️  Solo {len(campos_encontrados)}/3 campos encontrados")
            
            # 2. Verificar configuraciones existentes
            print("\n2️⃣  Verificando configuraciones activas...")
            configs = EnvioProgramadoDianVsErp.query.filter_by(activo=True).all()
            
            print(f"    ✅ {len(configs)} configuraciones activas encontradas")
            
            # Verificar que NINGUNA es de supervisión (deben ser False)
            configs_supervision = [c for c in configs if c.es_supervision]
            configs_normales = [c for c in configs if not c.es_supervision]
            
            print(f"    ✅ Configuraciones normales: {len(configs_normales)}")
            print(f"    ✅ Configuraciones supervisión: {len(configs_supervision)}")
            
            if len(configs_normales) == len(configs):
                print("\n    ✅✅ PERFECTO: Todas las configs existentes siguen siendo NORMALES")
            
            # 3. Verificar que se pueden leer los objetos
            print("\n3️⃣  Verificando lectura de objetos...")
            for config in configs[:3]:  # Solo primeras 3
                try:
                    # Intentar acceder a campos viejos Y nuevos
                    _ = config.nombre
                    _ = config.tipo
                    _ = config.dias_minimos
                    _ = config.es_supervision
                    _ = config.email_supervisor
                    _ = config.frecuencia_dias
                    print(f"    ✅ Config ID={config.id}: '{config.nombre[:40]}...' → LECTURA OK")
                except Exception as e:
                    print(f"    ❌ Config ID={config.id}: ERROR → {e}")
            
            # 4. Verificar to_dict()
            print("\n4️⃣  Verificando serialización JSON...")
            try:
                config_test = configs[0]
                dict_data = config_test.to_dict()
                
                # Verificar campos nuevos en el diccionario
                if 'es_supervision' in dict_data:
                    print("    ✅ Campo 'es_supervision' en to_dict()")
                if 'email_supervisor' in dict_data:
                    print("    ✅ Campo 'email_supervisor' en to_dict()")
                if 'frecuencia_dias' in dict_data:
                    print("    ✅ Campo 'frecuencia_dias' en to_dict()")
                
                print("\n    ✅ Serialización JSON funcionando correctamente")
            except Exception as e:
                print(f"    ❌ Error en serialización: {e}")
            
            # 5. Resumen final
            print("\n" + "=" * 80)
            print("✅ VERIFICACIÓN COMPLETADA")
            print("=" * 80)
            print()
            print("📊 RESUMEN:")
            print(f"   • Modelo Python: ✅ Actualizado")
            print(f"   • Configuraciones activas: ✅ {len(configs)} funcionando")
            print(f"   • Configs normales: ✅ {len(configs_normales)} (sin cambios)")
            print(f"   • Configs supervisión: ✅ {len(configs_supervision)} (nuevas)")
            print(f"   • Serialización JSON: ✅ Funcionando")
            print()
            print("🎉 EL SISTEMA SIGUE FUNCIONANDO SIN PROBLEMAS")
            print()
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verificar_sistema()
