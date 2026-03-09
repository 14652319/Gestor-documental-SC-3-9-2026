"""
Script de prueba para verificar el filtro de tipos_tercero en envíos programados DIAN VS ERP
"""

from app import app, db
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp, MaestroDianVsErp
import json

def test_tipos_tercero():
    """Prueba el filtro de tipos_tercero"""
    with app.app_context():
        print("\n" + "="*80)
        print("🧪 PRUEBA: FILTRO TIPOS DE TERCERO")
        print("="*80)
        
        # 1. Verificar que la columna existe
        print("\n📋 1. Verificando columna tipos_tercero...")
        try:
            configs = EnvioProgramadoDianVsErp.query.all()
            for config in configs:
                print(f"   Config ID {config.id}: tipos_tercero = {config.tipos_tercero}")
            print("   ✅ Columna tipos_tercero existe")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # 2. Contar documentos por tipo_tercero
        print("\n📊 2. Distribución de documentos por tipo_tercero:")
        tipos = db.session.query(
            MaestroDianVsErp.tipo_tercero,
            db.func.count(MaestroDianVsErp.id)
        ).group_by(MaestroDianVsErp.tipo_tercero).all()
        
        for tipo, count in tipos:
            tipo_display = tipo if tipo else "(NULL)"
            print(f"   {tipo_display:40s}: {count:,} documentos")
        
        # 3. Probar filtro con diferentes tipos
        print("\n🔍 3. Probando filtros de tipos_tercero:")
        
        filtros_prueba = [
            (["PROVEEDORES"], "solo PROVEEDORES"),
            (["ACREEDORES"], "solo ACREEDORES"),
            (["PROVEEDORES", "ACREEDORES"], "PROVEEDORES + ACREEDORES"),
            (["NO REGISTRADOS"], "solo NO REGISTRADOS"),
            ([], "sin filtro (todos)")
        ]
        
        for tipos_filtro, descripcion in filtros_prueba:
            query = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.dias_desde_emision >= 3
            )
            
            if tipos_filtro:
                query = query.filter(MaestroDianVsErp.tipo_tercero.in_(tipos_filtro))
            
            count = query.count()
            print(f"   📌 {descripcion:35s}: {count:,} documentos")
        
        # 4. Probar creación de configuración con tipos_tercero
        print("\n🆕 4. Creando configuración de prueba...")
        try:
            nueva_config = EnvioProgramadoDianVsErp(
                nombre="PRUEBA - Filtro Tipos Tercero",
                tipo="PENDIENTES_DIAS",
                dias_minimos=5,
                tipos_tercero=json.dumps(["PROVEEDORES", "ACREEDORES"]),
                hora_envio="10:00",
                frecuencia="DIARIO",
                tipo_destinatario="UsuariosNIT",
                activo=False  # Inactivo para no ejecutarse
            )
            db.session.add(nueva_config)
            db.session.commit()
            
            # Verificar que se guardó correctamente
            config_guardada = EnvioProgramadoDianVsErp.query.get(nueva_config.id)
            tipos_guardados = json.loads(config_guardada.tipos_tercero)
            
            print(f"   ✅ Configuración creada con ID: {config_guardada.id}")
            print(f"   ✅ Tipos guardados: {tipos_guardados}")
            
            # Eliminar configuración de prueba
            db.session.delete(config_guardada)
            db.session.commit()
            print(f"   🗑️ Configuración de prueba eliminada")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            db.session.rollback()
        
        print("\n" + "="*80)
        print("✅ PRUEBAS COMPLETADAS")
        print("="*80)

if __name__ == "__main__":
    test_tipos_tercero()
