#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configurador inicial del sistema de monitoreo
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def configurar_monitoreo_inicial():
    """Configura datos iniciales para el sistema de monitoreo"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="gestor_documental",
            user="postgres", 
            password="G3st0radm$2025.",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("🔧 CONFIGURANDO SISTEMA DE MONITOREO")
        print("-" * 50)
        
        # 1. Agregar IPs localhost a lista blanca
        print("📝 Agregando IPs localhost a lista blanca...")
        
        ips_localhost = [
            ('127.0.0.1', 'IPv4 localhost - Acceso local al sistema'),
            ('::1', 'IPv6 localhost - Acceso local al sistema'),
            ('192.168.11.33', 'IP local del servidor - Red interna')
        ]
        
        for ip, descripcion in ips_localhost:
            try:
                cursor.execute("""
                    INSERT INTO ips_blancas (ip, descripcion, usuario_agrego, activa)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (ip) DO NOTHING
                """, (ip, descripcion, 'sistema', True))
                print(f"   ✅ {ip} agregada a lista blanca")
            except Exception as e:
                print(f"   ⚠️ Error con {ip}: {e}")
        
        # 2. Crear alerta de bienvenida
        print("\n📝 Creando alerta de bienvenida...")
        try:
            cursor.execute("""
                INSERT INTO alertas_sistema (tipo, severidad, titulo, descripcion, detalles, usuario_creador)
                VALUES (
                    'SISTEMA',
                    'BAJA', 
                    'Sistema de Monitoreo Activado',
                    'El sistema de monitoreo está ahora completamente operativo con tracking en tiempo real de usuarios, gestión de IPs, logs multi-nivel y alertas configurables.',
                    '{"version": "2.0", "fecha_activacion": "2025-11-28", "funcionalidades": ["tracking_usuarios", "gestion_ips", "logs_sistema", "alertas", "metricas"]}',
                    'sistema'
                )
                ON CONFLICT DO NOTHING
            """)
            print("   ✅ Alerta de bienvenida creada")
        except Exception as e:
            print(f"   ⚠️ Error creando alerta: {e}")
        
        # 3. Verificar estado final
        print("\n📊 VERIFICANDO ESTADO FINAL:")
        
        # Contar IPs blancas
        cursor.execute("SELECT COUNT(*) FROM ips_blancas WHERE activa = true")
        ips_blancas = cursor.fetchone()[0]
        print(f"   ✅ IPs en lista blanca: {ips_blancas}")
        
        # Contar alertas
        cursor.execute("SELECT COUNT(*) FROM alertas_sistema")
        alertas = cursor.fetchone()[0]
        print(f"   ✅ Alertas en sistema: {alertas}")
        
        # Mostrar sesiones activas (debería estar vacía por ahora)
        cursor.execute("SELECT COUNT(*) FROM sesiones_activas WHERE activa = true")
        sesiones = cursor.fetchone()[0]
        print(f"   ℹ️ Sesiones activas: {sesiones}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 CONFIGURACIÓN INICIAL COMPLETADA")
        print("✅ El sistema de monitoreo está listo para usar")
        print("🔍 Los usuarios conectados aparecerán en tiempo real")
        print("🔒 Las IPs se gestionan automáticamente")
        print("📊 Las métricas se recolectan cada 5 minutos")
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")

if __name__ == "__main__":
    configurar_monitoreo_inicial()