"""
Convertir archivos .xls a .xlsx para evitar problemas con xlrd
Usa xlrd 1.2.0 directamente (sin pandas) + openpyxl
"""
import xlrd
from openpyxl import Workbook
from pathlib import Path

acuses_path = Path(r"D:\PERFIL\Descargas\1.A. Para pruebas dian vs erp 29 12 2025\Acuses")

print("🔄 Convirtiendo archivos .xls a .xlsx...")

for archivo_xls in acuses_path.glob("*.xls"):
    try:
        print(f"\n📄 Procesando: {archivo_xls.name}")
        
        # Leer con xlrd 1.2.0
        book = xlrd.open_workbook(str(archivo_xls))
        sheet = book.sheet_by_index(0)
        
        # Crear nuevo workbook con openpyxl
        wb = Workbook()
        ws = wb.active
        
        # Copiar datos
        for row_idx in range(sheet.nrows):
            row_data = []
            for col_idx in range(sheet.ncols):
                cell_value = sheet.cell_value(row_idx, col_idx)
                row_data.append(cell_value)
            ws.append(row_data)
        
        # Guardar como .xlsx
        archivo_xlsx = archivo_xls.with_suffix('.xlsx')
        wb.save(str(archivo_xlsx))
        
        print(f"   ✅ Convertido a: {archivo_xlsx.name}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n✅ Conversión completada")
