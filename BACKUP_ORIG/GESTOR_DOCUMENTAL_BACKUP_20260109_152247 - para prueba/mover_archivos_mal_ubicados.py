# -*- coding: utf-8 -*-
"""
Script para mover archivos de facturas que estan en D:/2025/ a D:/facturas_digitales/
Fecha: 8 de diciembre de 2025
"""
from app import app, db
from modules.facturas_digitales.models import FacturaDigital
import os
import shutil

def mover_archivos_mal_ubicados():
    """Mueve archivos de D:/2025/ a D:/facturas_digitales/"""
    with app.app_context():
        print("=" * 80)
        print("MOVER ARCHIVOS DE UBICACIÓN INCORRECTA")
        print("=" * 80)
        
        # Buscar facturas con rutas en D:\2025\ (sin facturas_digitales)
        facturas = FacturaDigital.query.all()
        
        archivos_movidos = 0
        errores = []
        
        for factura in facturas:
            if not factura.ruta_carpeta:
                continue
            
            # Detectar si está en ubicación incorrecta (D:\2025\ en lugar de D:\facturas_digitales\)
            ruta_incorrecta = (
                factura.ruta_carpeta.startswith('D:/2025/') or 
                factura.ruta_carpeta.startswith('D:\\2025\\') or
                factura.ruta_carpeta.startswith('/2025/')
            )
            
            if not ruta_incorrecta:
                continue
            
            print(f"\n{'=' * 80}")
            print(f"📄 ID {factura.id} | {factura.numero_factura}")
            print(f"   NIT: {factura.nit_proveedor}")
            print(f"   ❌ Ruta incorrecta: {factura.ruta_carpeta}")
            
            # Construir nueva ruta
            # Detectar si los campos están vacíos
            empresa = factura.empresa if factura.empresa and factura.empresa.strip() else 'SIN_EMPRESA'
            departamento = factura.departamento if factura.departamento and factura.departamento.strip() else 'SIN_DEPARTAMENTO'
            forma_pago = factura.forma_pago if factura.forma_pago and factura.forma_pago.strip() else 'SIN_FORMA_PAGO'
            
            # Fecha de emisión o fecha actual
            if factura.fecha_emision:
                año = factura.fecha_emision.year
                mes = f"{factura.fecha_emision.month:02d}"
            else:
                from datetime import datetime
                año = datetime.now().year
                mes = f"{datetime.now().month:02d}"
            
            nueva_ruta = os.path.join(
                'D:', 'facturas_digitales',
                empresa,
                str(año),
                mes,
                departamento,
                forma_pago
            )
            
            print(f"   ✅ Nueva ruta: {nueva_ruta}")
            
            # Buscar carpeta origen (puede estar en varias ubicaciones)
            carpeta_origen = None
            
            # Intentar varias rutas posibles
            posibles_origenes = [
                factura.ruta_carpeta,  # Tal como está en BD
                factura.ruta_carpeta.replace('D:/facturas_digitales/', 'D:/'),  # Sin facturas_digitales
                factura.ruta_carpeta.replace('D:/facturas_digitales', 'D:'),  # Sin facturas_digitales
            ]
            
            for posible in posibles_origenes:
                if os.path.exists(posible):
                    carpeta_origen = posible
                    break
            
            # Buscar por nombre de carpeta en D:\2025\
            if not carpeta_origen:
                nombre_carpeta = f"{factura.nit_proveedor}-{factura.numero_factura}"
                ruta_busqueda = os.path.join('D:', '2025', '12. DICIEMBRE', nombre_carpeta)
                if os.path.exists(ruta_busqueda):
                    carpeta_origen = ruta_busqueda
            
            if not carpeta_origen:
                print(f"   ⚠️ NO se encontró carpeta origen en disco")
                errores.append(f"ID {factura.id}: Carpeta no encontrada")
                continue
            
            print(f"   📁 Carpeta origen encontrada: {carpeta_origen}")
            
            try:
                # Crear carpeta destino
                os.makedirs(nueva_ruta, exist_ok=True)
                
                # Listar archivos a mover
                archivos = os.listdir(carpeta_origen)
                print(f"   📎 Archivos a mover: {len(archivos)}")
                
                # Mover cada archivo
                for archivo in archivos:
                    origen = os.path.join(carpeta_origen, archivo)
                    destino = os.path.join(nueva_ruta, archivo)
                    
                    if os.path.isfile(origen):
                        # Si archivo ya existe, agregar sufijo
                        if os.path.exists(destino):
                            nombre, ext = os.path.splitext(archivo)
                            contador = 1
                            while os.path.exists(destino):
                                destino = os.path.join(nueva_ruta, f"{nombre}_{contador}{ext}")
                                contador += 1
                        
                        shutil.move(origen, destino)
                        print(f"      ✅ Movido: {archivo}")
                        archivos_movidos += 1
                
                # Eliminar carpeta origen vacía
                try:
                    os.rmdir(carpeta_origen)
                    print(f"   🗑️ Carpeta origen eliminada: {carpeta_origen}")
                except:
                    print(f"   ⚠️ No se pudo eliminar carpeta origen (puede no estar vacía)")
                
                # Actualizar BD
                factura.ruta_carpeta = nueva_ruta
                factura.empresa = empresa
                factura.departamento = departamento
                factura.forma_pago = forma_pago
                
                db.session.commit()
                print(f"   ✅ Base de datos actualizada")
                
            except Exception as e:
                db.session.rollback()
                print(f"   ❌ ERROR: {str(e)}")
                errores.append(f"ID {factura.id}: {str(e)}")
        
        # Resumen
        print(f"\n{'=' * 80}")
        print("RESUMEN")
        print(f"{'=' * 80}")
        print(f"✅ Archivos movidos: {archivos_movidos}")
        print(f"❌ Errores: {len(errores)}")
        
        if errores:
            print(f"\n⚠️ ERRORES ENCONTRADOS:")
            for error in errores:
                print(f"   - {error}")
        
        print(f"{'=' * 80}")

if __name__ == '__main__':
    respuesta = input("Mover archivos de D:/2025/ a D:/facturas_digitales/? (s/n): ")
    if respuesta.lower() == 's':
        mover_archivos_mal_ubicados()
    else:
        print("Operación cancelada")
