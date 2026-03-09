"""
Script para renombrar archivos que no coinciden con el nombre de su carpeta padre
"""
import os
import re
from extensions import db
from modules.notas_contables.models import DocumentoContable, AdjuntoDocumento

def renombrar_archivos_incorrectos():
    base_dir = "D:/DOCUMENTOS_CONTABLES"
    
    print("🔍 Buscando archivos con nombres incorrectos...")
    
    # Patrón para nombres de carpeta: 019-NOC-00000013
    patron_carpeta = re.compile(r'(\d{3})-([A-Z]{3,4})-(\d{8})')
    
    archivos_renombrados = 0
    
    for root, dirs, files in os.walk(base_dir):
        # Verificar si estamos en una carpeta de documento
        carpeta_nombre = os.path.basename(root)
        match_carpeta = patron_carpeta.match(carpeta_nombre)
        
        if match_carpeta:
            codigo_esperado = carpeta_nombre  # Ej: 019-NOC-00000013
            print(f"\n📁 Carpeta: {carpeta_nombre}")
            
            for archivo in files:
                if archivo.endswith('.pdf'):
                    ruta_completa = os.path.join(root, archivo)
                    
                    # Verificar si es archivo principal o anexo
                    if '_ANEXO_' in archivo:
                        # Es un anexo
                        partes = archivo.split('_ANEXO_', 1)
                        prefijo_actual = partes[0]
                        etiqueta_con_ext = partes[1]
                        
                        if prefijo_actual != codigo_esperado:
                            nuevo_nombre = f"{codigo_esperado}_ANEXO_{etiqueta_con_ext}"
                            nueva_ruta = os.path.join(root, nuevo_nombre)
                            
                            print(f"   📎 Anexo a renombrar:")
                            print(f"      De: {archivo}")
                            print(f"      A:  {nuevo_nombre}")
                            
                            try:
                                os.rename(ruta_completa, nueva_ruta)
                                print(f"      ✅ Renombrado exitosamente")
                                archivos_renombrados += 1
                                
                                # Actualizar en BD
                                adjunto = AdjuntoDocumento.query.filter_by(nombre_archivo=archivo).first()
                                if adjunto:
                                    adjunto.nombre_archivo = nuevo_nombre
                                    # Actualizar también la ruta si es necesaria
                                    if adjunto.ruta_archivo:
                                        adjunto.ruta_archivo = adjunto.ruta_archivo.replace(archivo, nuevo_nombre)
                                    print(f"      ✅ BD actualizada")
                            except Exception as e:
                                print(f"      ❌ Error: {str(e)}")
                    else:
                        # Es archivo principal
                        nombre_sin_ext = os.path.splitext(archivo)[0]
                        extension = os.path.splitext(archivo)[1]
                        
                        if nombre_sin_ext != codigo_esperado:
                            nuevo_nombre = f"{codigo_esperado}{extension}"
                            nueva_ruta = os.path.join(root, nuevo_nombre)
                            
                            print(f"   📄 Archivo principal a renombrar:")
                            print(f"      De: {archivo}")
                            print(f"      A:  {nuevo_nombre}")
                            
                            try:
                                os.rename(ruta_completa, nueva_ruta)
                                print(f"      ✅ Renombrado exitosamente")
                                archivos_renombrados += 1
                                
                                # Actualizar en BD
                                doc = DocumentoContable.query.filter_by(nombre_archivo=archivo).first()
                                if doc:
                                    doc.nombre_archivo = nuevo_nombre
                                    # Actualizar también la ruta
                                    if doc.ruta_archivo:
                                        doc.ruta_archivo = doc.ruta_archivo.replace(archivo, nuevo_nombre)
                                    print(f"      ✅ BD actualizada")
                            except Exception as e:
                                print(f"      ❌ Error: {str(e)}")
    
    if archivos_renombrados > 0:
        try:
            db.session.commit()
            print(f"\n✅ {archivos_renombrados} archivos renombrados correctamente")
            print(f"✅ Base de datos actualizada")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar en BD: {str(e)}")
    else:
        print(f"\n✅ No se encontraron archivos para renombrar")

if __name__ == "__main__":
    from app import app
    
    with app.app_context():
        renombrar_archivos_incorrectos()
