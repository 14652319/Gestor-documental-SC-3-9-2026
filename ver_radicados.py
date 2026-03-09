#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar los radicados existentes en la base de datos
"""
from app import app, SolicitudRegistro, db

def ver_radicados():
    with app.app_context():
        solicitudes = SolicitudRegistro.query.all()
        print(f'📋 Radicados en la base de datos: {len(solicitudes)}')
        print('-' * 50)
        
        if not solicitudes:
            print('❌ No hay radicados en la base de datos')
        else:
            for s in solicitudes:
                print(f'📄 Radicado: {s.radicado}')
                print(f'   Estado: {s.estado}')
                print(f'   Tercero ID: {s.tercero_id}')
                print(f'   Fecha: {s.fecha_solicitud}')
                print('-' * 30)

if __name__ == "__main__":
    ver_radicados()