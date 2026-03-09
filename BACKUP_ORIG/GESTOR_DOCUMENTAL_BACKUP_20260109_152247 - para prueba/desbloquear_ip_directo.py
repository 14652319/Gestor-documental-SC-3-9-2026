#!/usr/bin/env python3
"""
Desbloquear IP directamente desde la base de datos
Solución directa para el usuario
Fecha: 28 Noviembre 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from app import app
from sqlalchemy import text
from datetime import datetime

def desbloquear_ip_directo(ip):
    """Desbloquea una IP removiéndola de todas las listas de bloqueo"""
    try:
        with app.app_context():
            print(f"🔓 DESBLOQUEANDO IP: {ip}")
            print("=" * 50)
            
            # 1. Verificar si está en ips_negras
            query_check_negras = text("SELECT COUNT(*) FROM ips_negras WHERE ip = :ip")
            count_negras = db.session.execute(query_check_negras, {'ip': ip}).scalar()
            
            if count_negras > 0:
                print(f"📍 IP {ip} encontrada en lista NEGRA")
                # Eliminar de ips_negras
                query_delete_negras = text("DELETE FROM ips_negras WHERE ip = :ip")
                result = db.session.execute(query_delete_negras, {'ip': ip})
                print(f"✅ Eliminadas {result.rowcount} entradas de lista NEGRA")
            else:
                print(f"ℹ️  IP {ip} NO estaba en lista negra")
            
            # 2. Verificar si está en ips_sospechosas
            query_check_sospechosas = text("SELECT COUNT(*) FROM ips_sospechosas WHERE ip = :ip")
            count_sospechosas = db.session.execute(query_check_sospechosas, {'ip': ip}).scalar()
            
            if count_sospechosas > 0:
                print(f"📍 IP {ip} encontrada en lista SOSPECHOSA")
                # Eliminar de ips_sospechosas
                query_delete_sospechosas = text("DELETE FROM ips_sospechosas WHERE ip = :ip")
                result = db.session.execute(query_delete_sospechosas, {'ip': ip})
                print(f"✅ Eliminadas {result.rowcount} entradas de lista SOSPECHOSA")
            else:
                print(f"ℹ️  IP {ip} NO estaba en lista sospechosa")
            
            # 3. Agregar a lista blanca para asegurar acceso
            try:
                from modules.admin.monitoreo.models import IPBlanca
                
                # Verificar si ya está en lista blanca
                ip_blanca_existe = IPBlanca.query.filter_by(ip=ip).first()
                
                if not ip_blanca_existe:
                    nueva_ip_blanca = IPBlanca(
                        ip=ip,
                        descripcion=f"Desbloqueada automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        usuario_agrego="admin_auto",
                        activa=True,
                        fecha=datetime.now()
                    )
                    db.session.add(nueva_ip_blanca)
                    print(f"✅ IP {ip} agregada a lista BLANCA")
                else:
                    print(f"ℹ️  IP {ip} ya estaba en lista blanca")
                    
            except Exception as e:
                print(f"⚠️  No se pudo agregar a lista blanca: {e}")
                print("🔄 Intentando con SQL directo...")
                
                # Fallback con SQL directo
                query_check_blanca = text("SELECT COUNT(*) FROM ips_blancas WHERE ip = :ip")
                count_blanca = db.session.execute(query_check_blanca, {'ip': ip}).scalar()
                
                if count_blanca == 0:
                    query_insert_blanca = text("""
                        INSERT INTO ips_blancas (ip, descripcion, usuario_agrego, activa, fecha) 
                        VALUES (:ip, :desc, :usuario, :activa, :fecha)
                    """)
                    db.session.execute(query_insert_blanca, {
                        'ip': ip,
                        'desc': f"Desbloqueada automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        'usuario': 'admin_auto',
                        'activa': True,
                        'fecha': datetime.now()
                    })
                    print(f"✅ IP {ip} agregada a lista blanca con SQL directo")
            
            # Confirmar cambios
            db.session.commit()
            
            print("=" * 50)
            print("🎉 ¡DESBLOQUEO COMPLETADO!")
            print(f"🔓 La IP {ip} ha sido completamente desbloqueada")
            print("✅ Removida de listas negra y sospechosa")
            print("✅ Agregada a lista blanca para acceso garantizado")
            print("")
            print("🔄 Recarga la página del monitoreo para ver los cambios")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR durante el desbloqueo: {e}")
        db.session.rollback()
        return False

def listar_estado_ip(ip):
    """Lista el estado actual de una IP en todas las listas"""
    try:
        with app.app_context():
            print(f"📊 ESTADO ACTUAL DE IP: {ip}")
            print("=" * 50)
            
            # Lista negra
            query_negra = text("SELECT COUNT(*), MIN(fecha) FROM ips_negras WHERE ip = :ip")
            result = db.session.execute(query_negra, {'ip': ip}).fetchone()
            if result[0] > 0:
                print(f"🚫 Lista NEGRA: SÍ (desde {result[1]})")
            else:
                print(f"✅ Lista NEGRA: NO")
            
            # Lista sospechosa
            query_sospechosa = text("SELECT COUNT(*), MIN(fecha) FROM ips_sospechosas WHERE ip = :ip")
            result = db.session.execute(query_sospechosa, {'ip': ip}).fetchone()
            if result[0] > 0:
                print(f"⚠️  Lista SOSPECHOSA: SÍ (desde {result[1]})")
            else:
                print(f"✅ Lista SOSPECHOSA: NO")
            
            # Lista blanca
            try:
                from modules.admin.monitoreo.models import IPBlanca
                ip_blanca = IPBlanca.query.filter_by(ip=ip).first()
                if ip_blanca:
                    print(f"🟢 Lista BLANCA: SÍ (desde {ip_blanca.fecha})")
                else:
                    print(f"❌ Lista BLANCA: NO")
            except:
                # Fallback con SQL
                query_blanca = text("SELECT COUNT(*), MIN(fecha) FROM ips_blancas WHERE ip = :ip")
                result = db.session.execute(query_blanca, {'ip': ip}).fetchone()
                if result[0] > 0:
                    print(f"🟢 Lista BLANCA: SÍ (desde {result[1]})")
                else:
                    print(f"❌ Lista BLANCA: NO")
            
            print("=" * 50)
            
    except Exception as e:
        print(f"❌ Error consultando estado: {e}")

if __name__ == '__main__':
    print("🔧 DESBLOQUEO DIRECTO DE IP")
    print("🎯 Script de emergencia para desbloquear IPs")
    print("")
    
    # IP por defecto (la tuya local)
    ip_desbloquear = "127.0.0.1"
    
    if len(sys.argv) > 1:
        ip_desbloquear = sys.argv[1]
    
    print(f"🎯 IP a desbloquear: {ip_desbloquear}")
    print("")
    
    # Mostrar estado actual
    print("📊 ESTADO ANTES DEL DESBLOQUEO:")
    listar_estado_ip(ip_desbloquear)
    print("")
    
    # Realizar desbloqueo
    if desbloquear_ip_directo(ip_desbloquear):
        print("")
        print("📊 ESTADO DESPUÉS DEL DESBLOQUEO:")
        listar_estado_ip(ip_desbloquear)
    else:
        print("❌ El desbloqueo falló")