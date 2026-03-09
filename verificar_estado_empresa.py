#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar estado de empresa y usuario
"""

from app import app, db, Usuario
from modules.configuracion.models import Empresa

with app.app_context():
    # Verificar empresa
    empresa = Empresa.query.filter_by(nit='805028041').first()
    if empresa:
        print("=" * 60)
        print("EMPRESA 805028041")
        print("=" * 60)
        print(f"NIT: {empresa.nit}")
        print(f"Razón Social: {empresa.razon_social}")
        print(f"Activa: {empresa.activa}")
        print(f"Bloqueada: {empresa.bloqueada}")
        print(f"Lista Negra: {empresa.lista_negra}")
        print()
        
        # Si está en lista negra o bloqueada, corregir
        if empresa.lista_negra or empresa.bloqueada or not empresa.activa:
            print("⚠️ CORRIGIENDO ESTADO...")
            empresa.lista_negra = False
            empresa.bloqueada = False
            empresa.activa = True
            db.session.commit()
            print("✅ Empresa corregida: activa=True, bloqueada=False, lista_negra=False")
        else:
            print("✅ Empresa en estado correcto")
    else:
        print("❌ Empresa 805028041 NO ENCONTRADA")
    
    print()
    
    # Verificar usuario
    usuario = Usuario.query.filter_by(username='admin').first()
    if usuario:
        print("=" * 60)
        print("USUARIO ADMIN")
        print("=" * 60)
        print(f"Username: {usuario.username}")
        print(f"NIT Asociado: {usuario.nit_asociado}")
        print(f"Activo: {usuario.activo}")
        print(f"Bloqueado: {usuario.bloqueado}")
        print(f"Intentos Login: {usuario.intentos_login}")
        print()
        
        # Si está bloqueado, corregir
        if usuario.bloqueado or not usuario.activo or usuario.intentos_login > 0:
            print("⚠️ CORRIGIENDO ESTADO...")
            usuario.bloqueado = False
            usuario.activo = True
            usuario.intentos_login = 0
            db.session.commit()
            print("✅ Usuario corregido: activo=True, bloqueado=False, intentos=0")
        else:
            print("✅ Usuario en estado correcto")
    else:
        print("❌ Usuario admin NO ENCONTRADO")
