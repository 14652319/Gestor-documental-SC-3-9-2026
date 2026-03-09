"""
Script para verificar y ejecutar manualmente el envío de supervisión con filtros de tipo_tercero
"""
from app import app, db
from modules.dian_vs_erp.models import EnvioProgramadoDianVsErp, MaestroDianVsErp
import json

with app.app_context():
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN CON FILTRO TIPOS_TERCERO")
    print("="*80)
    
    # Buscar la configuración recién creada
    config = EnvioProgramadoDianVsErp.query.filter_by(
        nombre='Alerta doc sin causar 5 dias'
    ).first()
    
    if not config:
        print("❌ No se encontró la configuración 'Alerta doc sin causar 5 dias'")
        print("\n📋 Configuraciones disponibles:")
        todas = EnvioProgramadoDianVsErp.query.all()
        for c in todas:
            print(f"  - ID {c.id}: {c.nombre} (Supervisión: {c.es_supervision})")
        exit(1)
    
    print(f"\n✅ Configuración encontrada:")
    print(f"   ID: {config.id}")
    print(f"   Nombre: {config.nombre}")
    print(f"   Tipo: {config.tipo}")
    print(f"   Es Supervisión: {config.es_supervision}")
    print(f"   Email Supervisor: {config.email_supervisor}")
    print(f"   Días Mínimos: {config.dias_minimos}")
    print(f"   Activo: {config.activo}")
    
    # Verificar tipos_tercero
    print(f"\n📊 FILTRO TIPOS_TERCERO:")
    print(f"   Valor en BD (raw): {config.tipos_tercero}")
    
    if config.tipos_tercero:
        try:
            tipos_parsed = json.loads(config.tipos_tercero)
            print(f"   Tipos parseados: {tipos_parsed}")
            print(f"   Cantidad de tipos: {len(tipos_parsed)}")
        except Exception as e:
            print(f"   ❌ ERROR al parsear: {e}")
            tipos_parsed = []
    else:
        print(f"   ⚠️ TIPOS_TERCERO ESTÁ VACÍO - Se incluirán TODOS los tipos")
        tipos_parsed = []
    
    # Probar query CON filtro
    print(f"\n🔍 PROBANDO QUERY CON FILTRO:")
    
    dias_min = config.dias_minimos or 5
    
    # Query base
    query = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.dias_desde_emision >= dias_min,
        MaestroDianVsErp.causada == False
    )
    
    total_sin_filtro = query.count()
    print(f"   📄 Documentos sin filtro tipo_tercero: {total_sin_filtro}")
    
    # Aplicar filtro de tipos_tercero
    if tipos_parsed:
        query_con_filtro = query.filter(MaestroDianVsErp.tipo_tercero.in_(tipos_parsed))
        total_con_filtro = query_con_filtro.count()
        print(f"   📄 Documentos CON filtro tipo_tercero: {total_con_filtro}")
        
        # Mostrar distribución por tipo
        print(f"\n📊 Distribución por tipo_tercero:")
        for tipo in tipos_parsed:
            count = MaestroDianVsErp.query.filter(
                MaestroDianVsErp.dias_desde_emision >= dias_min,
                MaestroDianVsErp.causada == False,
                MaestroDianVsErp.tipo_tercero == tipo
            ).count()
            print(f"      {tipo}: {count} documentos")
        
        # Mostrar ejemplos
        if total_con_filtro > 0:
            print(f"\n📋 Primeros 5 documentos que coinciden:")
            ejemplos = query_con_filtro.limit(5).all()
            for doc in ejemplos:
                print(f"      NIT: {doc.nit_emisor} | {doc.razon_social}")
                print(f"      Tipo: {doc.tipo_tercero} | Días: {doc.dias_desde_emision}")
                print(f"      Prefijo-Folio: {doc.prefijo}-{doc.folio}")
                print(f"      ---")
    else:
        print(f"   ⚠️ No hay filtro de tipos_tercero configurado")
    
    print(f"\n" + "="*80)
    print(f"✅ VERIFICACIÓN COMPLETADA")
    print(f"="*80)
    
    # Verificar si hay problema con el guardado
    if not config.tipos_tercero or config.tipos_tercero == 'null' or config.tipos_tercero == '[]':
        print(f"\n⚠️ PROBLEMA DETECTADO:")
        print(f"   El campo tipos_tercero está vacío o null.")
        print(f"   Posibles causas:")
        print(f"   1. El formulario no está enviando los datos correctamente")
        print(f"   2. El JavaScript no está capturando las selecciones")
        print(f"   3. El endpoint no está guardando el campo")
        print(f"\n💡 SOLUCIÓN:")
        print(f"   Verifica el código JavaScript que captura las selecciones del select multiple")
        print(f"   y asegúrate de que se envía en el request.json como 'tipos_tercero'")
