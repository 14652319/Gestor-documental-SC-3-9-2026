"""Script de prueba para generar Excel con documentos pendientes"""
from app import app
from modules.dian_vs_erp.models import MaestroDianVsErp
from modules.dian_vs_erp.scheduler_envios import scheduler_dian_vs_erp_global

with app.app_context():
    print("\n" + "="*80)
    print("🧪 PRUEBA DE GENERACIÓN DE EXCEL")
    print("="*80)
    
    # 1. Consultar documentos pendientes (ordenados por días DESC)
    print("\n📊 Consultando documentos pendientes (ordenados por más antiguo primero)...")
    documentos = MaestroDianVsErp.query.filter(
        MaestroDianVsErp.dias_desde_emision >= 5
    ).order_by(MaestroDianVsErp.dias_desde_emision.desc()).limit(139).all()
    
    print(f"   Total documentos encontrados: {len(documentos)}")
    if documentos:
        print(f"   Más antiguo: {documentos[0].dias_desde_emision} días - Factura {documentos[0].prefijo}-{documentos[0].folio}")
        print(f"   Más reciente: {documentos[-1].dias_desde_emision} días - Factura {documentos[-1].prefijo}-{documentos[-1].folio}")
    
    # 2. Verificar openpyxl
    print("\n📦 Verificando openpyxl...")
    try:
        import openpyxl
        print(f"   ✅ openpyxl instalado (versión: {openpyxl.__version__})")
    except ImportError:
        print("   ❌ openpyxl NO instalado")
        exit(1)
    
    # 3. Generar Excel
    print("\n📝 Generando Excel con todos los documentos...")
    try:
        excel_bytes = scheduler_dian_vs_erp_global._generar_excel_documentos(
            documentos=documentos,
            tipo='PENDIENTES_DIAS',
            dias_min=5
        )
        
        # Guardar archivo
        filename = "TEST_Documentos_20251226_0450.xlsx"
        with open(filename, 'wb') as f:
            f.write(excel_bytes)
        
        print(f"   ✅ EXCEL GENERADO EXITOSAMENTE: {filename}")
        print(f"   📊 Tamaño: {len(excel_bytes):,} bytes ({len(excel_bytes)/1024:.1f} KB)")
        print(f"   📄 Registros: {len(documentos)}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*80)
