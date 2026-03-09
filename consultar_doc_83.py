# -*- coding: utf-8 -*-
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="gestor_documental",
    user="postgres",
    password="G3st0radm$2025."
)

cursor = conn.cursor()
cursor.execute("SELECT id, tipo_documento, ruta_archivo FROM documentos_tercero WHERE id = 83")
result = cursor.fetchone()

if result:
    print(f"\n📄 Documento ID {result[0]}")
    print(f"   Tipo: {result[1]}")
    print(f"   Ruta en BD: {result[2]}")
    
    # Verificar si el archivo existe
    import os
    ruta_base = r'C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\documentos_terceros'
    ruta_completa = os.path.join(ruta_base, result[2])
    
    print(f"\n🔍 Buscando en:")
    print(f"   {ruta_completa}")
    
    if os.path.exists(ruta_completa):
        print(f"\n✅ ARCHIVO EXISTE!")
    else:
        print(f"\n❌ ARCHIVO NO EXISTE")
        print(f"\n   Probando otras variantes...")
        
        # Probar sin carpeta intermedia
        ruta_alt = os.path.join(ruta_base, os.path.basename(result[2]))
        print(f"   {ruta_alt}")
        if os.path.exists(ruta_alt):
            print(f"   ✅ ENCONTRADO AQUÍ")
else:
    print("❌ Documento ID 83 no encontrado en BD")

cursor.close()
conn.close()
