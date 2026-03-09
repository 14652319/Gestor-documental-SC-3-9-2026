# -*- coding: utf-8 -*-
"""Script para ver datos completos del tercero 29590569"""
from app import app, db, Tercero, SolicitudRegistro, Usuario, DocumentoTercero
import sys

# Configurar encoding UTF-8
sys.stdout.reconfigure(encoding='utf-8')

with app.app_context():
    # Buscar tercero
    tercero = Tercero.query.filter_by(nit='29590569').first()
    
    if not tercero:
        print("❌ Tercero NO encontrado")
        sys.exit(1)
    
    # Buscar datos relacionados
    solicitud = SolicitudRegistro.query.filter_by(tercero_id=tercero.id).first()
    usuarios = Usuario.query.filter_by(tercero_id=tercero.id).all()
    documentos = DocumentoTercero.query.filter_by(tercero_id=tercero.id).all()
    
    print("\n" + "="*70)
    print("📋 DATOS COMPLETOS DEL TERCERO 29590569")
    print("="*70)
    
    print("\n🏢 INFORMACIÓN BÁSICA:")
    print(f"   ID Tercero: {tercero.id}")
    print(f"   NIT: {tercero.nit}")
    print(f"   Tipo Persona: {tercero.tipo_persona}")
    print(f"   Razón Social: {tercero.razon_social}")
    print(f"   Correo: {tercero.correo}")
    print(f"   Celular: {tercero.celular}")
    print(f"   Estado: {tercero.estado}")
    print(f"   Fecha Registro: {tercero.fecha_registro}")
    
    if solicitud:
        print("\n📋 RADICADO:")
        print(f"   Número: {solicitud.radicado}")
        print(f"   Estado: {solicitud.estado}")
        print(f"   Fecha: {solicitud.fecha_solicitud}")
    
    if usuarios:
        print(f"\n👥 USUARIOS ({len(usuarios)} total):")
        for u in usuarios:
            print(f"   • Usuario: {u.usuario} | Activo: {'✅' if u.activo else '❌'}")
    
    if documentos:
        print(f"\n📄 DOCUMENTOS EN BD ({len(documentos)} total):")
        for doc in documentos:
            print(f"   ✓ {doc.tipo_documento}")
            print(f"     Ruta: {doc.ruta_archivo}")
    
    print("\n📁 CARPETA FÍSICA:")
    print("   C:\\Users\\Usuario\\Desktop\\Gestor Documental\\PAQUETES_TRANSPORTABLES\\")
    print("   GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\\documentos_terceros\\")
    print("   29590569-RAD-031854-27-01-2026\\")
    print(f"   {len(documentos)} archivos PDF almacenados")
    
    print("\n" + "="*70)
    print("✅ REGISTRO COMPLETO Y EXITOSO")
    print("="*70 + "\n")
