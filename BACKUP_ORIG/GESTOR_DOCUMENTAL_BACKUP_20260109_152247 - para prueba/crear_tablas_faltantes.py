#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Creador de tablas faltantes de monitoreo
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def crear_tablas_faltantes():
    """Crea solo las tablas que faltan del sistema de monitoreo"""
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
        
        print("🔧 CREANDO TABLAS FALTANTES DE MONITOREO")
        print("-" * 50)
        
        # SQL para crear las 4 tablas faltantes
        tablas_sql = {
            'logs_sistema': """
                CREATE TABLE IF NOT EXISTS logs_sistema (
                    id SERIAL PRIMARY KEY,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('ERROR', 'WARNING', 'INFO', 'DEBUG')),
                    modulo VARCHAR(100),
                    mensaje TEXT NOT NULL,
                    detalles JSONB,
                    usuario VARCHAR(100),
                    ip VARCHAR(50),
                    stack_trace TEXT,
                    archivo_origen VARCHAR(255),
                    linea_codigo INTEGER,
                    resuelto BOOLEAN DEFAULT FALSE
                )
            """,
            
            'logs_auditoria': """
                CREATE TABLE IF NOT EXISTS logs_auditoria (
                    id SERIAL PRIMARY KEY,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tabla VARCHAR(100) NOT NULL,
                    registro_id INTEGER,
                    accion VARCHAR(20) NOT NULL CHECK (accion IN ('INSERT', 'UPDATE', 'DELETE')),
                    datos_anteriores JSONB,
                    datos_nuevos JSONB,
                    usuario VARCHAR(100),
                    ip VARCHAR(50),
                    user_agent TEXT,
                    sesion_id VARCHAR(255),
                    motivo TEXT
                )
            """,
            
            'alertas_sistema': """
                CREATE TABLE IF NOT EXISTS alertas_sistema (
                    id SERIAL PRIMARY KEY,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('SEGURIDAD', 'RENDIMIENTO', 'ESPACIO', 'ERROR', 'SISTEMA')),
                    severidad VARCHAR(20) NOT NULL CHECK (severidad IN ('CRITICA', 'ALTA', 'MEDIA', 'BAJA')),
                    titulo VARCHAR(255) NOT NULL,
                    descripcion TEXT NOT NULL,
                    detalles JSONB,
                    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'vista', 'resuelta', 'ignorada')),
                    usuario_creador VARCHAR(100),
                    usuario_asignado VARCHAR(100),
                    fecha_visto TIMESTAMP NULL,
                    fecha_resuelto TIMESTAMP NULL,
                    notas_resolucion TEXT,
                    contador_ocurrencias INTEGER DEFAULT 1,
                    ultima_ocurrencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            
            'metricas_rendimiento': """
                CREATE TABLE IF NOT EXISTS metricas_rendimiento (
                    id SERIAL PRIMARY KEY,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent DECIMAL(5,2),
                    memoria_percent DECIMAL(5,2),
                    memoria_total_mb INTEGER,
                    memoria_usada_mb INTEGER,
                    disco_percent DECIMAL(5,2),
                    disco_total_gb INTEGER,
                    disco_usado_gb INTEGER,
                    conexiones_bd INTEGER,
                    requests_por_minuto INTEGER,
                    tiempo_respuesta_promedio_ms INTEGER,
                    usuarios_activos INTEGER,
                    errores_ultimo_minuto INTEGER,
                    alertas_activas INTEGER,
                    temperatura_cpu DECIMAL(4,1),
                    load_average DECIMAL(4,2),
                    red_entrada_mb DECIMAL(8,2),
                    red_salida_mb DECIMAL(8,2)
                )
            """
        }
        
        # Crear índices
        indices_sql = [
            "CREATE INDEX IF NOT EXISTS idx_logs_sistema_fecha ON logs_sistema(fecha)",
            "CREATE INDEX IF NOT EXISTS idx_logs_sistema_tipo ON logs_sistema(tipo)",
            "CREATE INDEX IF NOT EXISTS idx_logs_sistema_modulo ON logs_sistema(modulo)",
            "CREATE INDEX IF NOT EXISTS idx_logs_auditoria_fecha ON logs_auditoria(fecha)",
            "CREATE INDEX IF NOT EXISTS idx_logs_auditoria_tabla ON logs_auditoria(tabla)",
            "CREATE INDEX IF NOT EXISTS idx_logs_auditoria_usuario ON logs_auditoria(usuario)",
            "CREATE INDEX IF NOT EXISTS idx_alertas_estado ON alertas_sistema(estado)",
            "CREATE INDEX IF NOT EXISTS idx_alertas_severidad ON alertas_sistema(severidad)",
            "CREATE INDEX IF NOT EXISTS idx_alertas_tipo ON alertas_sistema(tipo)",
            "CREATE INDEX IF NOT EXISTS idx_metricas_fecha ON metricas_rendimiento(fecha)"
        ]
        
        # Ejecutar creación de tablas
        exitos = 0
        errores = 0
        
        for tabla, sql in tablas_sql.items():
            try:
                print(f"📝 Creando tabla: {tabla}")
                cursor.execute(sql)
                exitos += 1
                print(f"   ✅ {tabla} creada")
            except Exception as e:
                print(f"   ❌ Error en {tabla}: {str(e)[:100]}")
                errores += 1
        
        # Crear índices
        print(f"\n📝 Creando {len(indices_sql)} índices...")
        for sql in indices_sql:
            try:
                cursor.execute(sql)
            except Exception as e:
                print(f"   ⚠️ Error en índice: {str(e)[:80]}")
        
        # Insertar datos iniciales en alertas_sistema
        print(f"\n📝 Insertando alerta inicial...")
        try:
            cursor.execute("""
                INSERT INTO alertas_sistema (tipo, severidad, titulo, descripcion, detalles, usuario_creador)
                VALUES (
                    'SISTEMA',
                    'MEDIA', 
                    'Sistema de monitoreo inicializado',
                    'Las tablas del sistema de monitoreo han sido creadas exitosamente',
                    '{"version": "1.0", "fecha_instalacion": "2025-11-28", "tablas_creadas": 4}',
                    'sistema'
                )
            """)
            print("   ✅ Alerta inicial creada")
        except Exception as e:
            print(f"   ⚠️ Error en alerta inicial: {e}")
        
        print(f"\n✅ Tablas creadas: {exitos}")
        print(f"⚠️ Errores: {errores}")
        
        # Verificar resultado final
        print("\n📊 ESTADO FINAL:")
        tablas_verificar = ['logs_sistema', 'logs_auditoria', 'alertas_sistema', 'metricas_rendimiento']
        
        for tabla in tablas_verificar:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {tabla:25s} | {count:3d} registros")
            except Exception as e:
                print(f"   ❌ {tabla:25s} | Error: {str(e)[:50]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 PROCESO COMPLETADO")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    crear_tablas_faltantes()