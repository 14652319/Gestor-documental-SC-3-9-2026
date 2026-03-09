"""
Script para verificar y corregir rutas en la base de datos
"""
from extensions import db
from modules.notas_contables.models import DocumentoContable, AdjuntoDocumento
import os

def verificar_rutas():
    print("🔍 Verificando rutas del documento 33...\n")
    
    # Buscar documento 33
    doc = DocumentoContable.query.get(33)
    
    if doc:
        print(f"📄 DOCUMENTO ID: {doc.id}")
        print(f"   Nombre archivo: {doc.nombre_archivo}")
        print(f"   Ruta archivo: {doc.ruta_archivo}")
        
        # Verificar si existe
        ruta_completa = os.path.join("D:/DOCUMENTOS_CONTABLES", doc.ruta_archivo)
        print(f"   Ruta completa: {ruta_completa}")
        print(f"   ¿Existe?: {os.path.exists(ruta_completa)}")
        
        # Buscar adjuntos
        adjuntos = AdjuntoDocumento.query.filter_by(documento_id=33).all()
        print(f"\n📎 ADJUNTOS ({len(adjuntos)}):")
        
        for adj in adjuntos:
            print(f"\n   ID: {adj.id}")
            print(f"   Nombre: {adj.nombre_archivo}")
            print(f"   Ruta BD: {adj.ruta_archivo}")
            
            ruta_adj_completa = os.path.join("D:/DOCUMENTOS_CONTABLES", adj.ruta_archivo)
            print(f"   Ruta completa: {ruta_adj_completa}")
            existe = os.path.exists(ruta_adj_completa)
            print(f"   ¿Existe?: {existe}")
            
            if not existe:
                # Buscar el archivo con el nombre correcto
                directorio = os.path.dirname(ruta_adj_completa)
                nombre = adj.nombre_archivo
                
                print(f"   Buscando en: {directorio}")
                
                if os.path.exists(directorio):
                    archivos_en_dir = os.listdir(directorio)
                    print(f"   Archivos en directorio: {archivos_en_dir}")
                    
                    # Buscar archivo que coincida
                    for archivo in archivos_en_dir:
                        if archivo == nombre:
                            print(f"   ✅ Archivo encontrado: {archivo}")
                            # Actualizar ruta en BD
                            nueva_ruta_relativa = os.path.join(
                                os.path.dirname(adj.ruta_archivo),
                                nombre
                            )
                            print(f"   Actualizando ruta a: {nueva_ruta_relativa}")
                            adj.ruta_archivo = nueva_ruta_relativa
                            break

if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        verificar_rutas()
        
        # Guardar cambios
        try:
            db.session.commit()
            print("\n✅ Cambios guardados en la base de datos")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar: {str(e)}")
