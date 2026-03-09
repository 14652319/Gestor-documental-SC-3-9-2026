"""
Script para clasificar terceros según presencia en ERP Comercial y/o Financiero
Lógica de clasificación:
1. Si NIT está en ERP Comercial → "Proveedor"
2. Si NIT está en ERP Financiero → "Acreedor"  
3. Si NIT está en AMBOS → "Proveedor y Acreedor"
4. Si NIT no está en ninguno → "No Registrado" (hereda tipo de documentos DIAN anteriores)
"""
from extensions import db
from modules.dian_vs_erp.models import TipoTerceroDianErp, Dian, ErpComercial, ErpFinanciero
from sqlalchemy import func, distinct
from app import app
import time

def clasificar_terceros():
    with app.app_context():
        print("\n" + "="*90)
        print("🏢 CLASIFICANDO TERCEROS SEGÚN PRESENCIA EN ERP")
        print("="*90 + "\n")
        
        # Crear la tabla si no existe
        try:
            db.create_all()
            print("✅ Tabla tipo_tercero_dian_erp creada/verificada\n")
        except Exception as e:
            print(f"⚠️ Error creando tabla: {e}\n")
        
        inicio = time.time()
        
        # PASO 1: Obtener todos los NITs únicos de DIAN
        print("📋 PASO 1: Extrayendo NITs únicos de tabla DIAN...")
        nits_dian = db.session.query(
            Dian.nit_emisor,
            func.max(Dian.nombre_emisor).label('razon_social'),
            func.max(Dian.tipo_tercero).label('tipo_tercero_dian')  # Para heredar si es "No Registrado"
        ).filter(
            Dian.nit_emisor != None,
            Dian.nit_emisor != ''
        ).group_by(
            Dian.nit_emisor
        ).all()
        
        print(f"   ✅ {len(nits_dian):,} NITs únicos encontrados en DIAN\n")
        
        # PASO 2: Obtener NITs de ERP Comercial
        print("📋 PASO 2: Extrayendo NITs de ERP Comercial...")
        nits_comercial = set(
            nit for (nit,) in db.session.query(
                distinct(ErpComercial.proveedor)
            ).filter(
                ErpComercial.proveedor != None,
                ErpComercial.proveedor != ''
            ).all()
        )
        print(f"   ✅ {len(nits_comercial):,} NITs únicos en ERP Comercial\n")
        
        # PASO 3: Obtener NITs de ERP Financiero
        print("📋 PASO 3: Extrayendo NITs de ERP Financiero...")
        nits_financiero = set(
            nit for (nit,) in db.session.query(
                distinct(ErpFinanciero.proveedor)
            ).filter(
                ErpFinanciero.proveedor != None,
                ErpFinanciero.proveedor != ''
            ).all()
        )
        print(f"   ✅ {len(nits_financiero):,} NITs únicos en ERP Financiero\n")
        
        # PASO 4: Clasificar y crear registros
        print("📋 PASO 4: Clasificando terceros...\n")
        print(f"{'NIT':<15} {'RAZÓN SOCIAL':<40} {'TIPO TERCERO':<25} {'ERP-C':<6} {'ERP-F':<6} {'HEREDADO':<10}")
        print("-" * 110)
        
        contador_proveedor = 0
        contador_acreedor = 0
        contador_ambos = 0
        contador_no_registrado = 0
        contador_heredado = 0
        
        batch_size = 1000
        registros_batch = []
        
        for i, (nit, razon_social, tipo_dian) in enumerate(nits_dian, 1):
            # Verificar presencia en ERP
            en_comercial = nit in nits_comercial
            en_financiero = nit in nits_financiero
            heredado = False
            
            # Determinar tipo de tercero según lógica
            if en_comercial and en_financiero:
                tipo_tercero = "Proveedor y Acreedor"
                contador_ambos += 1
            elif en_comercial:
                tipo_tercero = "Proveedor"
                contador_proveedor += 1
            elif en_financiero:
                tipo_tercero = "Acreedor"
                contador_acreedor += 1
            else:
                # No está en ningún ERP → heredar de DIAN si existe
                if tipo_dian and tipo_dian.strip() and tipo_dian.strip() != 'No Registrado':
                    tipo_tercero = tipo_dian.strip()
                    heredado = True
                    contador_heredado += 1
                else:
                    tipo_tercero = "No Registrado"
                contador_no_registrado += 1
            
            # Verificar si ya existe
            tercero_existente = TipoTerceroDianErp.query.filter_by(nit_emisor=nit).first()
            
            if tercero_existente:
                # Actualizar
                tercero_existente.razon_social = razon_social or tercero_existente.razon_social
                tercero_existente.tipo_tercero = tipo_tercero
                tercero_existente.en_erp_comercial = en_comercial
                tercero_existente.en_erp_financiero = en_financiero
                tercero_existente.heredado_dian = heredado
            else:
                # Crear nuevo
                nuevo_tercero = TipoTerceroDianErp(
                    nit_emisor=nit,
                    razon_social=razon_social or "Sin razón social",
                    tipo_tercero=tipo_tercero,
                    en_erp_comercial=en_comercial,
                    en_erp_financiero=en_financiero,
                    heredado_dian=heredado
                )
                registros_batch.append(nuevo_tercero)
            
            # Mostrar primeros 10
            if i <= 10:
                c_mark = "✅" if en_comercial else "❌"
                f_mark = "✅" if en_financiero else "❌"
                h_mark = "🔄" if heredado else "  "
                print(f"{nit:<15} {(razon_social or 'Sin razón social')[:40]:<40} {tipo_tercero:<25} {c_mark:<6} {f_mark:<6} {h_mark:<10}")
            
            # Commit en batch
            if len(registros_batch) >= batch_size:
                db.session.bulk_save_objects(registros_batch)
                db.session.commit()
                registros_batch = []
                print(f"   💾 Guardados {i:,} de {len(nits_dian):,} terceros... ({(i/len(nits_dian)*100):.1f}%)")
        
        # Commit final
        if registros_batch:
            db.session.bulk_save_objects(registros_batch)
        db.session.commit()
        
        tiempo_total = time.time() - inicio
        
        print("\n" + "="*90)
        print("✅ CLASIFICACIÓN COMPLETADA")
        print("="*90)
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   🏢 Proveedor:             {contador_proveedor:>8,} ({contador_proveedor/len(nits_dian)*100:>5.1f}%)")
        print(f"   💰 Acreedor:              {contador_acreedor:>8,} ({contador_acreedor/len(nits_dian)*100:>5.1f}%)")
        print(f"   🔀 Proveedor y Acreedor:  {contador_ambos:>8,} ({contador_ambos/len(nits_dian)*100:>5.1f}%)")
        print(f"   ⚠️  No Registrado:         {contador_no_registrado:>8,} ({contador_no_registrado/len(nits_dian)*100:>5.1f}%)")
        print(f"       └─ 🔄 Heredados DIAN:  {contador_heredado:>8,}")
        print(f"\n   📋 Total terceros:        {len(nits_dian):>8,}")
        print(f"   ⏱️  Tiempo total:          {tiempo_total:.2f} segundos")
        print(f"   🚀 Velocidad:             {len(nits_dian)/tiempo_total:,.0f} terceros/segundo")
        print("="*90 + "\n")

if __name__ == '__main__':
    clasificar_terceros()
