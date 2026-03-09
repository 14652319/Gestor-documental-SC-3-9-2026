#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Consulta completa del tercero 29590569
"""
import os
import sys
from datetime import datetime

# Configurar el path para importar módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from app import app, Tercero, SolicitudRegistro, Usuario, DocumentoTercero

def consultar_tercero_completo(nit):
    """Consulta todos los datos de un tercero por NIT"""
    
    with app.app_context():
        print("\n" + "="*80)
        print(f"   CONSULTA COMPLETA DEL TERCERO: {nit}")
        print("="*80 + "\n")
        
        # 1. Buscar tercero
        tercero = Tercero.query.filter_by(nit=nit).first()
        
        if not tercero:
            print(f"❌ NO se encontró tercero con NIT {nit}\n")
            return
        
        print("📋 DATOS DEL TERCERO:")
        print("-" * 80)
        print(f"   ID:              {tercero.id}")
        print(f"   NIT:             {tercero.nit}")
        print(f"   Razón Social:    {tercero.razon_social}")
        print(f"   Tipo Persona:    {tercero.tipo_persona}")
        print(f"   Correo:          {tercero.correo}")
        print(f"   Celular:         {tercero.celular}")
        print(f"   Estado:          {tercero.estado}")
        print(f"   Fecha Registro:  {tercero.fecha_registro}")
        print()
        
        # 2. Buscar solicitud de registro
        solicitud = SolicitudRegistro.query.filter_by(tercero_id=tercero.id).first()
        
        if solicitud:
            print("📄 SOLICITUD DE REGISTRO:")
            print("-" * 80)
            print(f"   Radicado:        {solicitud.radicado}")
            print(f"   Estado:          {solicitud.estado}")
            # Intentar ambos nombres de campo
            fecha = getattr(solicitud, 'fecha_creacion', None) or getattr(solicitud, 'fecha_registro', None)
            print(f"   Fecha Solicitud: {fecha}")
            print()
        else:
            print("⚠️  No se encontró solicitud de registro\n")
        
        # 3. Buscar usuarios asociados
        usuarios = Usuario.query.filter_by(tercero_id=tercero.id).all()
        
        if usuarios:
            print(f"👥 USUARIOS ASOCIADOS ({len(usuarios)}):")
            print("-" * 80)
            for idx, user in enumerate(usuarios, 1):
                print(f"   {idx}. Usuario:  {user.usuario}")
                # Intentar varios nombres de campo
                nombre = getattr(user, 'nombre_completo', None) or getattr(user, 'nombre', None) or "N/A"
                print(f"      Nombre:   {nombre}")
                print(f"      Correo:   {user.correo}")
                activo = getattr(user, 'activo', None)
                print(f"      Activo:   {'✅ SÍ' if activo else '❌ NO'}")
                fecha = getattr(user, 'fecha_creacion', None) or getattr(user, 'fecha_registro', None)
                print(f"      Fecha:    {fecha}")
                print()
        else:
            print("⚠️  No se encontraron usuarios asociados\n")
        
        # 4. Buscar documentos
        documentos = DocumentoTercero.query.filter_by(tercero_id=tercero.id).all()
        
        if documentos:
            print(f"📎 DOCUMENTOS CARGADOS ({len(documentos)}):")
            print("-" * 80)
            for idx, doc in enumerate(documentos, 1):
                print(f"   {idx}. Tipo:         {doc.tipo_documento}")
                print(f"      Nombre:       {doc.nombre_archivo}")
                print(f"      Ruta:         {doc.ruta_archivo}")
                fecha = getattr(doc, 'fecha_subida', None) or getattr(doc, 'fecha_creacion', None) or getattr(doc, 'fecha_registro', None)
                print(f"      Fecha:        {fecha}")
                
                # Verificar si el archivo existe físicamente
                ruta_completa = os.path.join(
                    os.path.dirname(__file__),
                    doc.ruta_archivo
                )
                if os.path.exists(ruta_completa):
                    tamaño = os.path.getsize(ruta_completa)
                    print(f"      Archivo:      ✅ EXISTE ({tamaño:,} bytes)")
                else:
                    print(f"      Archivo:      ❌ NO ENCONTRADO")
                print()
        else:
            print("⚠️  No se encontraron documentos\n")
        
        # 5. Carpeta física
        if solicitud:
            # Intentar ambos nombres de campo
            fecha_obj = getattr(solicitud, 'fecha_creacion', None) or getattr(solicitud, 'fecha_registro', None)
            fecha_str = fecha_obj.strftime("%d-%m-%Y") if fecha_obj else "fecha-desconocida"
            carpeta_nombre = f"{tercero.nit}-{solicitud.radicado}-{fecha_str}"
            carpeta_ruta = os.path.join(
                os.path.dirname(__file__),
                "documentos_terceros",
                carpeta_nombre
            )
            
            print("📁 CARPETA FÍSICA:")
            print("-" * 80)
            print(f"   Nombre:   {carpeta_nombre}")
            print(f"   Ruta:     {carpeta_ruta}")
            
            if os.path.exists(carpeta_ruta):
                archivos = os.listdir(carpeta_ruta)
                print(f"   Estado:   ✅ EXISTE")
                print(f"   Archivos: {len(archivos)} PDFs")
                print()
                
                if archivos:
                    print("   📄 Archivos en carpeta:")
                    for archivo in sorted(archivos):
                        ruta_archivo = os.path.join(carpeta_ruta, archivo)
                        tamaño = os.path.getsize(ruta_archivo)
                        print(f"      • {archivo} ({tamaño:,} bytes)")
            else:
                print(f"   Estado:   ❌ NO ENCONTRADA")
            print()
        
        print("="*80)
        print("   CONSULTA COMPLETADA")
        print("="*80 + "\n")

if __name__ == "__main__":
    consultar_tercero_completo("29590569")
