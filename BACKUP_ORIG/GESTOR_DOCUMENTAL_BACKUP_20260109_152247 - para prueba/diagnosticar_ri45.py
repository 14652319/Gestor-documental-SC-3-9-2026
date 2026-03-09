#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para diagnosticar por qué la factura RI-45 NO fue guardada en TEMPORALES

Investiga:
1. Datos de la factura en BD
2. Tipo de usuario que la cargó
3. Ruta actual vs ruta esperada
4. Fecha de radicación
"""

import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from modules.facturas_digitales.models import FacturaDigital
from sqlalchemy import text

def diagnosticar_factura_ri45():
    """Diagnóstico completo de la factura RI-45"""
    
    with app.app_context():
        print("=" * 80)
        print("🔍 DIAGNÓSTICO: Factura RI-45")
        print("=" * 80)
        
        # Buscar factura RI-45
        factura = FacturaDigital.query.filter_by(numero_factura='RI-45').first()
        
        if not factura:
            print("❌ Factura RI-45 NO encontrada en base de datos")
            print("\nBuscando facturas con número similar...")
            
            facturas_similares = FacturaDigital.query.filter(
                FacturaDigital.numero_factura.like('%RI%')
            ).all()
            
            if facturas_similares:
                print(f"\n📋 Facturas encontradas con 'RI' en el número:")
                for f in facturas_similares:
                    print(f"   - {f.numero_factura} | NIT: {f.nit_proveedor} | Estado: {f.estado}")
            else:
                print("   No se encontraron facturas con 'RI' en el número")
            
            return
        
        print(f"✅ Factura encontrada: ID={factura.id}")
        print()
        
        # DATOS BÁSICOS
        print("📄 DATOS BÁSICOS")
        print("-" * 80)
        print(f"   ID:                  {factura.id}")
        print(f"   NIT Proveedor:       {factura.nit_proveedor}")
        print(f"   Razón Social:        {factura.razon_social_proveedor}")
        print(f"   Número Factura:      {factura.numero_factura}")
        print(f"   Fecha Radicación:    {factura.fecha_emision.strftime('%Y-%m-%d %H:%M:%S') if factura.fecha_emision else '⚠️ SIN FECHA'}")
        print(f"   Fecha Carga:         {factura.fecha_carga.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Valor Total:         ${factura.valor_total:,.2f}")
        print(f"   Estado:              {factura.estado}")
        print()
        
        # CAMPOS PARA RUTA
        print("📁 CAMPOS PARA CONSTRUCCIÓN DE RUTA")
        print("-" * 80)
        print(f"   Empresa:             {factura.empresa if factura.empresa else '❌ VACÍO (NULL)'}")
        print(f"   Departamento:        {factura.departamento if factura.departamento else '❌ VACÍO (NULL)'}")
        print(f"   Forma de Pago:       {factura.forma_pago if factura.forma_pago else '❌ VACÍO (NULL)'}")
        print(f"   Tipo Documento:      {factura.tipo_documento if factura.tipo_documento else '❌ VACÍO (NULL)'}")
        print(f"   Tipo Servicio:       {factura.tipo_servicio if factura.tipo_servicio else '❌ VACÍO (NULL)'}")
        print()
        
        # RUTA ACTUAL
        print("🗂️  UBICACIÓN ACTUAL")
        print("-" * 80)
        print(f"   Ruta en BD:          {factura.ruta_carpeta}")
        
        # Verificar si existe físicamente
        if factura.ruta_carpeta and os.path.exists(factura.ruta_carpeta):
            print(f"   Estado Físico:       ✅ La carpeta EXISTE")
            
            # Listar archivos
            archivos = os.listdir(factura.ruta_carpeta)
            print(f"   Archivos ({len(archivos)}):")
            for archivo in archivos:
                ruta_archivo = os.path.join(factura.ruta_carpeta, archivo)
                tamanio = os.path.getsize(ruta_archivo) / 1024  # KB
                print(f"      - {archivo} ({tamanio:.1f} KB)")
        else:
            print(f"   Estado Físico:       ❌ La carpeta NO EXISTE")
        print()
        
        # ANÁLISIS DE RUTA
        print("🔍 ANÁLISIS DE RUTA")
        print("-" * 80)
        
        ruta_bd = factura.ruta_carpeta if factura.ruta_carpeta else "SIN RUTA"
        
        # Verificar si está en TEMPORALES
        if 'TEMPORALES' in ruta_bd.upper():
            print("   ✅ La factura SÍ está en TEMPORALES")
            print(f"   Tipo de carga:       Usuario EXTERNO (esperado)")
        elif 'D:\\2025\\' in ruta_bd or 'D:/2025/' in ruta_bd:
            print("   ❌ La factura está en D:\\2025\\ (UBICACIÓN INCORRECTA)")
            print("   Posibles causas:")
            print("      1. Código antiguo sin validación de tipo de usuario")
            print("      2. Usuario interno sin llenar empresa/depto/forma_pago")
            print("      3. Sesión sin tipo_usuario (default='interno')")
        elif 'facturas_digitales' in ruta_bd.lower():
            # Verificar estructura completa
            partes = ruta_bd.replace('\\', '/').split('/')
            print(f"   ✅ La factura está en estructura de facturas_digitales")
            print(f"   Estructura de carpetas:")
            for i, parte in enumerate(partes):
                print(f"      Nivel {i}: {parte}")
            
            # Verificar si tiene empresa/año/mes/depto/pago
            if factura.empresa:
                print(f"   ✅ Tiene EMPRESA: {factura.empresa}")
            else:
                print(f"   ⚠️  NO tiene EMPRESA")
            
            if factura.departamento:
                print(f"   ✅ Tiene DEPARTAMENTO: {factura.departamento}")
            else:
                print(f"   ⚠️  NO tiene DEPARTAMENTO")
            
            if factura.forma_pago:
                print(f"   ✅ Tiene FORMA_PAGO: {factura.forma_pago}")
            else:
                print(f"   ⚠️  NO tiene FORMA_PAGO")
        else:
            print(f"   ⚠️  Ruta no reconocida: {ruta_bd}")
        print()
        
        # RUTA ESPERADA
        print("📋 RUTA ESPERADA (SI TUVIERA CAMPOS COMPLETOS)")
        print("-" * 80)
        
        if factura.fecha_emision and factura.empresa and factura.departamento and factura.forma_pago:
            año = factura.fecha_emision.year
            mes = f"{factura.fecha_emision.month:02d}"
            
            ruta_esperada = f"D:\\facturas_digitales\\{factura.empresa}\\{año}\\{mes}\\{factura.departamento}\\{factura.forma_pago}"
            print(f"   Ruta ideal:          {ruta_esperada}")
            print(f"   Basada en:")
            print(f"      - Empresa:        {factura.empresa}")
            print(f"      - Año:            {año} (de fecha radicación)")
            print(f"      - Mes:            {mes} (de fecha radicación)")
            print(f"      - Departamento:   {factura.departamento}")
            print(f"      - Forma de Pago:  {factura.forma_pago}")
        else:
            print("   ⚠️  NO se puede calcular ruta esperada porque faltan campos:")
            if not factura.fecha_emision:
                print("      ❌ Falta FECHA DE RADICACIÓN")
            if not factura.empresa:
                print("      ❌ Falta EMPRESA")
            if not factura.departamento:
                print("      ❌ Falta DEPARTAMENTO")
            if not factura.forma_pago:
                print("      ❌ Falta FORMA DE PAGO")
            
            # Mostrar ruta TEMPORALES esperada
            print()
            print(f"   Como ALTERNATIVA (si fuera usuario externo):")
            ruta_temporales = f"D:\\facturas_digitales\\TEMPORALES\\{factura.nit_proveedor}\\{factura.nit_proveedor}-{factura.numero_factura}"
            print(f"   Ruta TEMPORALES:     {ruta_temporales}")
        print()
        
        # AUDITORÍA
        print("📊 INFORMACIÓN DE AUDITORÍA")
        print("-" * 80)
        print(f"   Usuario Carga:       {factura.usuario_carga if factura.usuario_carga else 'NO REGISTRADO'}")
        print(f"   Observaciones:       {factura.observaciones if factura.observaciones else 'Ninguna'}")
        print()
        
        # RECOMENDACIÓN
        print("💡 RECOMENDACIÓN")
        print("=" * 80)
        
        if not factura.empresa or not factura.departamento or not factura.forma_pago:
            print("   1. Usar el formulario 'Completar Campos' en el sistema web")
            print("   2. Llenar los campos faltantes:")
            if not factura.empresa:
                print("      - Empresa (SC, LG, etc.)")
            if not factura.departamento:
                print("      - Departamento (TIC, DOM, CYS, etc.)")
            if not factura.forma_pago:
                print("      - Forma de Pago (CREDITO, CONTADO, etc.)")
            print("   3. Al guardar, el sistema moverá automáticamente los archivos a la ubicación correcta")
            print(f"      Desde: {factura.ruta_carpeta}")
            if factura.fecha_emision:
                año = factura.fecha_emision.year
                mes = f"{factura.fecha_emision.month:02d}"
                print(f"      Hacia: D:\\facturas_digitales\\[EMPRESA]\\{año}\\{mes}\\[DEPTO]\\[FORMA_PAGO]\\")
        elif 'TEMPORALES' in (factura.ruta_carpeta or '').upper():
            print("   ✅ La factura está en TEMPORALES (correcto para usuario externo)")
            print("   Completar campos para moverla a ubicación final")
        elif 'D:\\2025\\' in (factura.ruta_carpeta or ''):
            print("   ⚠️  La factura está en ubicación INCORRECTA (D:\\2025\\)")
            print("   OPCIONES:")
            print("      A) Usar formulario 'Completar Campos' (recomendado)")
            print("      B) Mover manualmente con script de corrección")
        else:
            print("   ✅ La factura parece estar en ubicación correcta")
        
        print("=" * 80)

if __name__ == "__main__":
    diagnosticar_factura_ri45()
