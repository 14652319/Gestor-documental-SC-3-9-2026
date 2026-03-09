"""
Script para corregir las rutas de los adjuntos del documento 33
"""
import os
import sys
from app import app, db
from modules.notas_contables.models import DocumentoContable, AdjuntoDocumento

def main():
    with app.app_context():
        # Obtener documento 33
        documento = db.session.get(DocumentoContable, 33)
        if not documento:
            print("❌ Documento 33 no encontrado")
            return
        
        print(f"📄 Documento 33: {documento.nombre_archivo}")
        print(f"   Ruta: {documento.ruta_archivo}")
        
        # Obtener directorio del documento
        # El documento está en: SC\2025\12\001\NOC\001-NOC-00000013
        directorio_doc = os.path.dirname(documento.ruta_archivo)
        nombre_base = documento.nombre_archivo  # 001-NOC-00000013
        
        # La ruta correcta para adjuntos es: SC/2025/12/001/NOC/001-NOC-00000013/archivo.pdf
        directorio_adjuntos = os.path.join(directorio_doc, nombre_base)
        
        print(f"\n📁 Directorio de adjuntos: {directorio_adjuntos}")
        
        # Obtener adjuntos del documento
        adjuntos = AdjuntoDocumento.query.filter_by(documento_id=33).all()
        print(f"\n📎 Encontrados {len(adjuntos)} adjuntos\n")
        
        corregidos = 0
        
        for adj in adjuntos:
            print(f"📎 Adjunto ID {adj.id}: {adj.nombre_archivo}")
            
            # Construir ruta correcta
            ruta_correcta = os.path.join(directorio_adjuntos, adj.nombre_archivo)
            # Convertir a formato con barras normales
            ruta_correcta = ruta_correcta.replace('\\', '/')
            
            print(f"   Ruta actual: {adj.ruta_archivo}")
            print(f"   Ruta correcta: {ruta_correcta}")
            
            # Verificar que el archivo existe
            ruta_completa = os.path.join("D:/DOCUMENTOS_CONTABLES", ruta_correcta)
            if os.path.exists(ruta_completa):
                print(f"   ✅ Archivo encontrado")
                
                # Actualizar ruta en BD
                adj.ruta_archivo = ruta_correcta
                corregidos += 1
            else:
                print(f"   ❌ Archivo no encontrado en: {ruta_completa}")
            
            print()
        
        # Guardar cambios
        if corregidos > 0:
            db.session.commit()
            print(f"\n✅ Se corrigieron {corregidos} rutas de adjuntos")
        else:
            print(f"\n⚠️ No se encontraron adjuntos para corregir")

if __name__ == '__main__':
    main()
