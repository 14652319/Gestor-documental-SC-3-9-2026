"""
Script para consultar la ubicación de una factura específica
"""
from app import app, db
from modules.facturas_digitales.models import FacturaDigital

def ver_ruta_factura(numero_factura):
    """Muestra la ruta completa de una factura"""
    with app.app_context():
        factura = FacturaDigital.query.filter_by(numero_factura=numero_factura).first()
        
        if not factura:
            print(f"❌ No se encontró la factura: {numero_factura}")
            return
        
        print(f"\n{'='*80}")
        print(f"📄 INFORMACIÓN DE LA FACTURA: {numero_factura}")
        print(f"{'='*80}")
        print(f"ID: {factura.id}")
        print(f"Proveedor: {factura.razon_social_proveedor} (NIT: {factura.nit_proveedor})")
        print(f"Empresa: {factura.empresa or 'NO ASIGNADA'}")
        print(f"Departamento: {factura.departamento or 'NO ASIGNADO'}")
        print(f"Tipo Documento: {factura.tipo_documento or 'NO ASIGNADO'}")
        print(f"Forma Pago: {factura.forma_pago or 'NO ASIGNADA'}")
        print(f"Tipo Servicio: {factura.tipo_servicio or 'NO ASIGNADO'}")
        print(f"Valor Total: ${factura.valor_total:,.2f}")
        print(f"Estado: {factura.estado.upper()}")
        print(f"\n{'='*80}")
        print(f"📁 UBICACIÓN DE ARCHIVOS")
        print(f"{'='*80}")
        print(f"Carpeta: {factura.ruta_carpeta or 'NO ESPECIFICADA'}")
        print(f"Ruta completa: {factura.ruta_archivo or 'NO ESPECIFICADA'}")
        print(f"\nArchivo principal: {factura.ruta_archivo_principal or 'NO ESPECIFICADO'}")
        if factura.ruta_archivo_anexo1:
            print(f"Anexo 1: {factura.ruta_archivo_anexo1}")
        if factura.ruta_archivo_anexo2:
            print(f"Anexo 2: {factura.ruta_archivo_anexo2}")
        if factura.ruta_archivo_seg_social:
            print(f"Seg. Social: {factura.ruta_archivo_seg_social}")
        
        print(f"\nNombre original: {factura.nombre_archivo_original}")
        print(f"Nombre sistema: {factura.nombre_archivo_sistema}")
        print(f"Tipo archivo: {factura.tipo_archivo}")
        print(f"Tamaño: {factura.tamanio_kb or 0} KB")
        
        print(f"\n{'='*80}")
        print(f"👤 INFORMACIÓN DE CARGA")
        print(f"{'='*80}")
        print(f"Usuario: {factura.usuario_carga}")
        print(f"Tipo: {factura.tipo_usuario}")
        print(f"Fecha: {factura.fecha_carga}")
        print(f"IP: {factura.ip_carga or 'N/A'}")
        
        if factura.observaciones:
            print(f"\n📝 Observaciones: {factura.observaciones}")
        
        print(f"\n{'='*80}\n")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        numero = sys.argv[1]
    else:
        numero = 'FE-44'  # Por defecto
    
    ver_ruta_factura(numero)
