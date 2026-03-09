"""
Script para corregir todas las rutas de adjuntos en la base de datos
"""
from extensions import db
from modules.notas_contables.models import DocumentoContable, AdjuntoDocumento
import os

def corregir_rutas_adjuntos():
    print("🔧 Corrigiendo rutas de adjuntos...\n")
    
    adjuntos = AdjuntoDocumento.query.all()
    corregidos = 0
    
    for adj in adjuntos:
        documento = DocumentoContable.query.get(adj.documento_id)
        
        if not documento:
            print(f"⚠️ Adjunto {adj.id}: Documento {adj.documento_id} no encontrado")
            continue
        
        # Obtener el directorio del documento principal
        directorio_documento = os.path.dirname(documento.ruta_archivo)
        
        # Construir la ruta correcta del adjunto (relativa)
        ruta_correcta = os.path.join(directorio_documento, adj.nombre_archivo)
        
        # Verificar si necesita corrección
        if adj.ruta_archivo != ruta_correcta:
            print(f"📎 Adjunto ID {adj.id} (Documento {adj.documento_id}):")
            print(f"   Nombre: {adj.nombre_archivo}")
            print(f"   Ruta actual: {adj.ruta_archivo}")
            print(f"   Ruta correcta: {ruta_correcta}")
            
            # Verificar que el archivo existe
            ruta_completa = os.path.join("D:/DOCUMENTOS_CONTABLES", ruta_correcta)
            if os.path.exists(ruta_completa):
                adj.ruta_archivo = ruta_correcta
                corregidos += 1
                print(f"   ✅ Corregido")
            else:
                # Buscar el archivo en el directorio correcto
                directorio_completo = os.path.join("D:/DOCUMENTOS_CONTABLES", directorio_documento)
                if os.path.exists(directorio_completo):
                    archivos = os.listdir(directorio_completo)
                    if adj.nombre_archivo in archivos:
                        adj.ruta_archivo = ruta_correcta
                        corregidos += 1
                        print(f"   ✅ Corregido (archivo encontrado)")
                    else:
                        print(f"   ❌ Archivo no encontrado en {directorio_completo}")
                        print(f"      Archivos disponibles: {archivos}")
                else:
                    print(f"   ❌ Directorio no existe: {directorio_completo}")
            
            print()
    
    if corregidos > 0:
        try:
            db.session.commit()
            print(f"\n✅ {corregidos} rutas de adjuntos corregidas")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar: {str(e)}")
    else:
        print("\n✅ No se encontraron rutas para corregir")

if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        corregir_rutas_adjuntos()
