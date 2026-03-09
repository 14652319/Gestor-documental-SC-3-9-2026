# -*- coding: utf-8 -*-
"""
Script para verificar las rutas de documentos guardadas en la BD
"""
from app import app, db, DocumentoTercero, Tercero
import os

with app.app_context():
    # Buscar documentos del tercero 29590569
    tercero = Tercero.query.filter_by(nit='29590569').first()
    
    if tercero:
        print(f"\n{'='*70}")
        print(f"📋 TERCERO: {tercero.razon_social}")
        print(f"   NIT: {tercero.nit}")
        print(f"   ID: {tercero.id}")
        print(f"{'='*70}\n")
        
        # Buscar documentos
        documentos = DocumentoTercero.query.filter_by(tercero_id=tercero.id).all()
        
        print(f"📄 DOCUMENTOS ENCONTRADOS: {len(documentos)}\n")
        
        for i, doc in enumerate(documentos, 1):
            print(f"{i}. {doc.tipo_documento}")
            print(f"   ID: {doc.id}")
            print(f"   Ruta en BD: {doc.ruta_archivo}")
            
            # Verificar si existe el archivo
            ruta_completa = os.path.join('documentos_terceros', doc.ruta_archivo)
            existe = os.path.exists(ruta_completa)
            
            print(f"   Ruta completa: {ruta_completa}")
            print(f"   ¿Existe? {'✅ SÍ' if existe else '❌ NO'}")
            
            # Intentar ruta alternativa (sin duplicar)
            if not existe:
                ruta_alt = doc.ruta_archivo
                existe_alt = os.path.exists(ruta_alt)
                print(f"   Ruta alternativa: {ruta_alt}")
                print(f"   ¿Existe alternativa? {'✅ SÍ' if existe_alt else '❌ NO'}")
            
            print()
    else:
        print("❌ Tercero no encontrado")
