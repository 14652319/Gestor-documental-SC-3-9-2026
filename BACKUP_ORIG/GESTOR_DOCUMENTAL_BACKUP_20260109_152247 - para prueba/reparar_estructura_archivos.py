"""
Script para reparar la estructura de archivos con carpetas duplicadas
y actualizar la base de datos
"""
import os
import shutil
from extensions import db
from modules.notas_contables.models import DocumentoContable, AdjuntoDocumento

def reparar_estructura():
    base_dir = "D:/DOCUMENTOS_CONTABLES"
    
    # Buscar todas las carpetas con estructura duplicada
    print("🔍 Buscando estructuras duplicadas...")
    
    for root, dirs, files in os.walk(base_dir):
        # Si encontramos una carpeta que termina en un patrón como 019-NOC-00000013
        for dir_name in dirs:
            if '-' in dir_name and dir_name.count('-') >= 2:
                # Verificar si dentro hay otra carpeta con el mismo nombre
                ruta_padre = os.path.join(root, dir_name)
                ruta_hija = os.path.join(ruta_padre, dir_name)
                
                if os.path.exists(ruta_hija) and os.path.isdir(ruta_hija):
                    print(f"\n📁 Encontrada carpeta duplicada:")
                    print(f"   {ruta_hija}")
                    
                    # Listar archivos en la carpeta hija
                    archivos_hija = os.listdir(ruta_hija)
                    if archivos_hija:
                        print(f"   Contiene {len(archivos_hija)} archivos")
                        
                        # Mover archivos de hija a padre
                        for archivo in archivos_hija:
                            origen = os.path.join(ruta_hija, archivo)
                            destino = os.path.join(ruta_padre, archivo)
                            
                            if os.path.isfile(origen):
                                try:
                                    print(f"   Moviendo: {archivo}")
                                    if os.path.exists(destino):
                                        print(f"   ⚠️ Destino ya existe, omitiendo")
                                    else:
                                        shutil.move(origen, destino)
                                        print(f"   ✅ Movido a carpeta padre")
                                except Exception as e:
                                    print(f"   ❌ Error: {str(e)}")
                        
                        # Eliminar carpeta hija si está vacía
                        try:
                            if not os.listdir(ruta_hija):
                                os.rmdir(ruta_hija)
                                print(f"   🗑️ Carpeta hija eliminada")
                        except:
                            pass
    
    print("\n✅ Reparación de estructura completada")
    print("\n🔄 Actualizando base de datos...")
    
    # Actualizar base de datos
    documentos = DocumentoContable.query.all()
    
    for doc in documentos:
        # Si la ruta tiene el nombre base duplicado, corregirla
        if doc.ruta_archivo and doc.nombre_archivo:
            partes = doc.ruta_archivo.split(os.sep)
            
            # Verificar si hay duplicación del nombre
            nombre_sin_ext = os.path.splitext(doc.nombre_archivo)[0]
            if nombre_sin_ext in partes:
                # Reconstruir sin la carpeta duplicada
                partes_limpias = [p for i, p in enumerate(partes) if not (i < len(partes)-1 and partes[i] == nombre_sin_ext)]
                nueva_ruta = os.path.join(*partes_limpias)
                
                print(f"📝 Actualizando documento {doc.id}:")
                print(f"   Antes: {doc.ruta_archivo}")
                print(f"   Después: {nueva_ruta}")
                
                doc.ruta_archivo = nueva_ruta
    
    # Actualizar adjuntos
    adjuntos = AdjuntoDocumento.query.all()
    
    for adj in adjuntos:
        if adj.ruta_archivo and adj.nombre_archivo:
            partes = adj.ruta_archivo.split(os.sep)
            
            # Buscar patrones duplicados
            nombre_sin_anexo = adj.nombre_archivo.split('_ANEXO_')[0] if '_ANEXO_' in adj.nombre_archivo else None
            if nombre_sin_anexo and nombre_sin_anexo in partes:
                partes_limpias = [p for i, p in enumerate(partes) if not (i < len(partes)-1 and partes[i] == nombre_sin_anexo)]
                nueva_ruta = os.path.join(*partes_limpias)
                
                print(f"📎 Actualizando adjunto {adj.id}:")
                print(f"   Antes: {adj.ruta_archivo}")
                print(f"   Después: {nueva_ruta}")
                
                adj.ruta_archivo = nueva_ruta
    
    try:
        db.session.commit()
        print("\n✅ Base de datos actualizada correctamente")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al actualizar BD: {str(e)}")

if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        reparar_estructura()
