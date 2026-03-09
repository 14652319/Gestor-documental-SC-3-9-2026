"""
Módulo DIAN vs ERP - Sistema Híbrido de Alto Rendimiento
SQLite para datos operativos + PostgreSQL para reportes y auditoría
Integrado al Gestor Documental - Supertiendas Cañaveral
"""

from extensions import db
from sqlalchemy import Column, String, DateTime, Integer, Text, DECIMAL
from datetime import datetime
import sqlite3
import pandas as pd
import polars as pl
from pathlib import Path
import os
from datetime import datetime, timezone
import hashlib
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Directorio base del módulo
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "dian_vs_erp.db"

# Asegurar que el directorio existe
DATA_DIR.mkdir(parents=True, exist_ok=True)

class DianSqliteManager:
    """Gestor de la base de datos SQLite para máximo rendimiento"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self.init_db()
        self.register_python_functions()
    
    def init_db(self):
        """Inicializa la base de datos SQLite con el schema optimizado"""
        conn = sqlite3.connect(self.db_path)
        schema_path = BASE_DIR / "schema.sql"
        
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
        conn.close()
    
    def register_python_functions(self):
        """Registra funciones Python personalizadas en SQLite"""
        conn = self.get_connection()
        
        def calcular_dias_diferencia(fecha_str):
            """Calcula días desde una fecha hasta hoy"""
            try:
                if not fecha_str:
                    return None
                fecha = datetime.strptime(fecha_str.split('T')[0], '%Y-%m-%d')
                return (datetime.now() - fecha).days
            except:
                return None
        
        def limpiar_nit(nit_str):
            """Limpia y normaliza un NIT"""
            if not nit_str:
                return ""
            return str(nit_str).strip().replace('.', '').replace(',', '').replace('-', '')
        
        def normalizar_texto(texto):
            """Normaliza texto para comparaciones"""
            if not texto:
                return ""
            return str(texto).upper().strip()
        
        # Registrar funciones
        conn.create_function("DIAS_DIFERENCIA", 1, calcular_dias_diferencia)
        conn.create_function("LIMPIAR_NIT", 1, limpiar_nit)
        conn.create_function("NORMALIZAR_TEXTO", 1, normalizar_texto)
        
        conn.close()
    
    def get_connection(self):
        """Conexión optimizada con WAL mode"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        conn.execute('PRAGMA cache_size=10000;')
        conn.execute('PRAGMA temp_store=memory;')
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        return conn
    
    def cargar_csv_a_tabla(self, csv_path, tabla, modo='replace'):
        """Carga un CSV a SQLite usando Polars para máximo rendimiento"""
        try:
            # Leer CSV con Polars
            df = pl.read_csv(csv_path, try_parse_dates=True, encoding='utf-8')
            
            # Convertir a pandas para SQLite
            df_pandas = df.to_pandas()
            
            # Guardar en SQLite
            with self.get_connection() as conn:
                df_pandas.to_sql(tabla, conn, if_exists=modo, index=False, method='multi')
                
            logger.info(f"Cargado {len(df_pandas)} registros en tabla {tabla}")
            return len(df_pandas)
            
        except Exception as e:
            logger.error(f"Error cargando CSV {csv_path} a tabla {tabla}: {str(e)}")
            raise e
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecuta una consulta y retorna resultados como lista de diccionarios"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Convertir a lista de diccionarios
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def obtener_facturas_consolidadas(self, limite=None, offset=None):
        """Obtiene facturas desde la vista consolidada"""
        query = """
            SELECT * FROM vista_consolidada 
            ORDER BY fecha_emision DESC
        """
        
        if limite:
            query += f" LIMIT {limite}"
            if offset:
                query += f" OFFSET {offset}"
        
        return self.ejecutar_consulta(query)
    
    def buscar_facturas(self, filtros):
        """Busca facturas con filtros avanzados"""
        where_clauses = []
        params = []
        
        if filtros.get('nit_emisor'):
            where_clauses.append("LIMPIAR_NIT(nit_emisor) LIKE ?")
            params.append(f"%{filtros['nit_emisor']}%")
        
        if filtros.get('prefijo'):
            where_clauses.append("NORMALIZAR_TEXTO(prefijo) = ?")
            params.append(filtros['prefijo'].upper())
        
        if filtros.get('folio'):
            where_clauses.append("folio = ?")
            params.append(filtros['folio'])
        
        if filtros.get('fecha_desde'):
            where_clauses.append("fecha_emision >= ?")
            params.append(filtros['fecha_desde'])
        
        if filtros.get('fecha_hasta'):
            where_clauses.append("fecha_emision <= ?")
            params.append(filtros['fecha_hasta'])
        
        query = "SELECT * FROM vista_consolidada"
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " ORDER BY fecha_emision DESC"
        
        return self.ejecutar_consulta(query, params)

# Modelos para integración con PostgreSQL (para reportes y auditoría)
class ReporteDian(db.Model):
    """Tabla en PostgreSQL para reportes consolidados"""
    __tablename__ = 'reportes_dian'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(String(50), nullable=False)
    periodo = Column(String(20), nullable=False)  # YYYY-MM
    fecha_generacion = Column(DateTime, default=datetime.utcnow)
    total_dian = Column(Integer, default=0)
    total_erp = Column(Integer, default=0)
    matches = Column(Integer, default=0)
    diferencias = Column(Integer, default=0)
    archivo_generado = Column(String(255))
    usuario_generador = Column(String(100))
    observaciones = Column(Text)

class LogProcesamiento(db.Model):
    """Log de procesamientos de archivos"""
    __tablename__ = 'logs_procesamiento_dian'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(String(50), nullable=False)
    archivo_tipo = Column(String(50), nullable=False)  # dian, erp_fn, erp_cm, etc.
    archivo_original = Column(String(255), nullable=False)
    archivo_hash = Column(String(64))  # SHA-256 del archivo
    registros_procesados = Column(Integer, default=0)
    fecha_procesamiento = Column(DateTime, default=datetime.utcnow)
    usuario = Column(String(100))
    estado = Column(String(50), default='completado')  # completado, error, en_proceso
    mensaje_error = Column(Text)

class ConfiguracionDian(db.Model):
    """Configuraciones del módulo DIAN vs ERP"""
    __tablename__ = 'configuracion_dian'
    
    id = Column(Integer, primary_key=True)
    empresa_id = Column(String(50), nullable=False)
    clave = Column(String(100), nullable=False)
    valor = Column(Text)
    descripcion = Column(Text)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)
    usuario_actualizacion = Column(String(100))

# Funciones de utilidad
def generar_hash_archivo(archivo_bytes):
    """Genera hash SHA-256 de un archivo"""
    return hashlib.sha256(archivo_bytes).hexdigest()

def obtener_estadisticas_sqlite():
    """Obtiene estadísticas desde SQLite"""
    try:
        manager = DianSqliteManager()
        with manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Estadísticas básicas
            stats = {}
            cursor.execute("SELECT COUNT(*) FROM dian")
            stats['total_dian'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM erp")
            stats['total_erp'] = cursor.fetchone()[0]
            
            # Matches DIAN ↔ ERP
            cursor.execute("""
                SELECT COUNT(*) FROM dian d 
                WHERE EXISTS (
                    SELECT 1 FROM erp e 
                    WHERE LIMPIAR_NIT(d.nit_emisor) = LIMPIAR_NIT(e.nit_proveedor) 
                    AND NORMALIZAR_TEXTO(d.prefijo) = NORMALIZAR_TEXTO(e.prefijo)
                    AND d.folio = e.folio
                )
            """)
            stats['matches_dian_erp'] = cursor.fetchone()[0]
            
            # Con módulo asignado
            cursor.execute("SELECT COUNT(*) FROM dian WHERE modulo IS NOT NULL AND modulo != ''")
            stats['dian_con_modulo'] = cursor.fetchone()[0]
            
            # Facturas por estado contable
            cursor.execute("""
                SELECT estado_contable, COUNT(*) as cantidad
                FROM dian 
                GROUP BY estado_contable
            """)
            stats['por_estado'] = dict(cursor.fetchall())
            
            return stats
            
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        return {
            'total_dian': 0,
            'total_erp': 0,
            'matches_dian_erp': 0,
            'dian_con_modulo': 0,
            'por_estado': {}
        }

def excel_a_csv(excel_path, output_dir, prefijo="archivo"):
    """Convierte Excel a CSV usando Polars para máximo rendimiento"""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Leer Excel con Polars
        df = pl.read_excel(excel_path)
        
        # Generar nombre único basado en hash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{prefijo}_{timestamp}.csv"
        csv_path = output_dir / csv_filename
        
        # Guardar como CSV
        df.write_csv(csv_path, encoding='utf-8')
        
        logger.info(f"Convertido {excel_path} a {csv_path}")
        return str(csv_path)
        
    except Exception as e:
        logger.error(f"Error convirtiendo Excel {excel_path}: {str(e)}")
        raise e

def sincronizar_reporte_postgresql(empresa_id, periodo, estadisticas, usuario):
    """Sincroniza estadísticas con PostgreSQL para reportes"""
    try:
        # Buscar reporte existente
        reporte = ReporteDian.query.filter_by(
            empresa_id=empresa_id,
            periodo=periodo
        ).first()
        
        if not reporte:
            reporte = ReporteDian(empresa_id=empresa_id, periodo=periodo)
            db.session.add(reporte)
        
        # Actualizar datos
        reporte.total_dian = estadisticas.get('total_dian', 0)
        reporte.total_erp = estadisticas.get('total_erp', 0)
        reporte.matches = estadisticas.get('matches_dian_erp', 0)
        reporte.diferencias = estadisticas['total_dian'] - estadisticas['matches_dian_erp']
        reporte.usuario_generador = usuario
        reporte.fecha_generacion = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Reporte sincronizado para empresa {empresa_id}, período {periodo}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sincronizando reporte: {str(e)}")
        raise e

def registrar_procesamiento(empresa_id, archivo_tipo, archivo_original, archivo_hash, 
                          registros_procesados, usuario, estado='completado', error=None):
    """Registra el procesamiento de un archivo en PostgreSQL"""
    try:
        log = LogProcesamiento(
            empresa_id=empresa_id,
            archivo_tipo=archivo_tipo,
            archivo_original=archivo_original,
            archivo_hash=archivo_hash,
            registros_procesados=registros_procesados,
            usuario=usuario,
            estado=estado,
            mensaje_error=error
        )
        
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"Procesamiento registrado: {archivo_tipo} - {registros_procesados} registros")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registrando procesamiento: {str(e)}")
        raise e