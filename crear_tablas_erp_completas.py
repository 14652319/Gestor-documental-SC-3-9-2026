"""
Crear tablas ERP COMERCIAL y ERP FINANCIERO con campos calculados automáticamente
Fecha: 30 de diciembre de 2025
"""
import psycopg2
from psycopg2 import sql

# Configuración de conexión
DB_CONFIG = {
    'dbname': 'gestor_documental',
    'user': 'gestor_user',
    'password': 'Cañaveral2024*',
    'host': 'localhost',
    'port': '5432'
}

def crear_tablas_erp():
    """Crea las tablas ERP con triggers para campos calculados"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("📋 Creando tablas ERP...")
        
        # ========================================
        # 1️⃣ TABLA: clase_docto_erp
        # ========================================
        print("\n1️⃣ Creando tabla clase_docto_erp...")
        cursor.execute("""
            DROP TABLE IF EXISTS clase_docto_erp CASCADE;
            
            CREATE TABLE clase_docto_erp (
                id SERIAL PRIMARY KEY,
                clase_docto VARCHAR(255) NOT NULL UNIQUE,
                tipo_tercero VARCHAR(50) NOT NULL,  -- 'ACREEDOR', 'PROVEEDOR', 'PROVEEDOR Y ACREEDOR'
                modulo VARCHAR(50) NOT NULL,  -- 'FINANCIERO', 'COMERCIAL', 'AMBOS'
                descripcion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX idx_clase_docto ON clase_docto_erp(clase_docto);
            
            COMMENT ON TABLE clase_docto_erp IS 'Catálogo de clases de documentos ERP con su clasificación';
        """)
        print("   ✅ Tabla clase_docto_erp creada")
        
        # Insertar datos de clasificación
        print("   📝 Insertando clasificaciones de documentos...")
        cursor.execute("""
            INSERT INTO clase_docto_erp (clase_docto, tipo_tercero, modulo, descripcion) VALUES
            -- ERP FINANCIERO (8 clases ACREEDOR)
            ('Factura de servicio desde sol. anticipo', 'ACREEDOR', 'FINANCIERO', 'Factura de servicio generada desde solicitud de anticipo'),
            ('Factura de servicio de reg.fijo compra', 'ACREEDOR', 'FINANCIERO', 'Factura de servicio de registro fijo de compra'),
            ('Factura de servicio compra', 'ACREEDOR', 'FINANCIERO', 'Factura de servicio de compra estándar'),
            ('Legalización factura anticipos', 'ACREEDOR', 'FINANCIERO', 'Legalización de factura de anticipos'),
            ('Legalización factura caja menor', 'ACREEDOR', 'FINANCIERO', 'Legalización de factura de caja menor'),
            ('Nota débito de servicios - compra', 'ACREEDOR', 'FINANCIERO', 'Nota débito relacionada con servicios de compra'),
            ('Factura de servicio, legalizacion gastos', 'ACREEDOR', 'FINANCIERO', 'Factura de servicio para legalización de gastos'),
            ('Legalización nota debito anticipos', 'ACREEDOR', 'FINANCIERO', 'Legalización de nota débito de anticipos'),
            
            -- ERP COMERCIAL (3 clases PROVEEDOR)
            ('Notas débito de proveedor', 'PROVEEDOR', 'COMERCIAL', 'Notas débito emitidas por proveedores'),
            ('Factura de proveedor', 'PROVEEDOR', 'COMERCIAL', 'Factura estándar de proveedor'),
            ('Factura de consignación', 'PROVEEDOR', 'COMERCIAL', 'Factura de mercancía en consignación')
            
            ON CONFLICT (clase_docto) DO NOTHING;
        """)
        print(f"   ✅ Insertadas 11 clasificaciones de documentos")
        
        # ========================================
        # 2️⃣ TABLA: erp_comercial
        # ========================================
        print("\n2️⃣ Creando tabla erp_comercial...")
        cursor.execute("""
            DROP TABLE IF EXISTS erp_comercial CASCADE;
            
            CREATE TABLE erp_comercial (
                id SERIAL PRIMARY KEY,
                
                -- 📥 CAMPOS CARGADOS DESDE ARCHIVO
                proveedor VARCHAR(50) NOT NULL,
                razon_social_proveedor VARCHAR(255),
                fecha_docto_prov DATE,
                docto_proveedor VARCHAR(100) NOT NULL,
                valor_bruto NUMERIC(15, 2),
                valor_imptos NUMERIC(15, 2),
                co VARCHAR(10),
                usuario_creacion VARCHAR(100),
                clase_docto VARCHAR(255),
                nro_documento VARCHAR(50),
                
                -- 🔧 CAMPOS CALCULADOS AUTOMÁTICAMENTE
                prefijo VARCHAR(20),
                folio VARCHAR(20),
                clave_erp_comercial VARCHAR(100),
                
                -- 📊 AUDITORÍA
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- 🔑 CONSTRAINT
                UNIQUE(proveedor, docto_proveedor)
            );
            
            -- Índices para búsqueda rápida
            CREATE INDEX idx_erp_comercial_proveedor ON erp_comercial(proveedor);
            CREATE INDEX idx_erp_comercial_clave ON erp_comercial(clave_erp_comercial);
            CREATE INDEX idx_erp_comercial_clase ON erp_comercial(clase_docto);
            CREATE INDEX idx_erp_comercial_fecha ON erp_comercial(fecha_docto_prov);
            
            COMMENT ON TABLE erp_comercial IS 'Registros del módulo ERP Comercial con campos calculados automáticamente';
        """)
        print("   ✅ Tabla erp_comercial creada")
        
        # ========================================
        # 3️⃣ FUNCIÓN PARA CALCULAR CAMPOS (COMERCIAL)
        # ========================================
        print("   🔧 Creando función de cálculo para erp_comercial...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION calcular_campos_erp_comercial()
            RETURNS TRIGGER AS $$
            DECLARE
                v_prefijo VARCHAR(20);
                v_folio VARCHAR(20);
                v_docto VARCHAR(100);
            BEGIN
                -- Obtener el valor de docto_proveedor
                v_docto := COALESCE(NEW.docto_proveedor, '');
                
                -- EXTRAER PREFIJO (lado izquierdo del guion)
                IF v_docto LIKE '%-%' THEN
                    v_prefijo := SPLIT_PART(v_docto, '-', 1);
                ELSE
                    v_prefijo := '';
                END IF;
                
                -- EXTRAER FOLIO (lado derecho del guion, sin ceros a la izquierda)
                IF v_docto LIKE '%-%' THEN
                    v_folio := LTRIM(SPLIT_PART(v_docto, '-', 2), '0');
                    -- Si queda vacío después de quitar ceros, poner '0'
                    IF v_folio = '' THEN
                        v_folio := '0';
                    END IF;
                ELSE
                    -- Si no hay guion, intentar extraer solo números
                    v_folio := LTRIM(REGEXP_REPLACE(v_docto, '[^0-9]', '', 'g'), '0');
                    IF v_folio = '' THEN
                        v_folio := '0';
                    END IF;
                END IF;
                
                -- Asignar valores calculados
                NEW.prefijo := v_prefijo;
                NEW.folio := v_folio;
                
                -- CALCULAR CLAVE: Proveedor + Prefijo + Folio
                NEW.clave_erp_comercial := CONCAT(
                    COALESCE(NEW.proveedor, ''),
                    '-',
                    v_prefijo,
                    '-',
                    v_folio
                );
                
                -- Actualizar fecha de modificación
                NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("   ✅ Función calcular_campos_erp_comercial creada")
        
        # ========================================
        # 4️⃣ TRIGGER PARA COMERCIAL
        # ========================================
        print("   ⚡ Creando trigger para erp_comercial...")
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_calcular_erp_comercial ON erp_comercial;
            
            CREATE TRIGGER trigger_calcular_erp_comercial
                BEFORE INSERT OR UPDATE ON erp_comercial
                FOR EACH ROW
                EXECUTE FUNCTION calcular_campos_erp_comercial();
        """)
        print("   ✅ Trigger para erp_comercial creado")
        
        # ========================================
        # 5️⃣ TABLA: erp_financiero
        # ========================================
        print("\n3️⃣ Creando tabla erp_financiero...")
        cursor.execute("""
            DROP TABLE IF EXISTS erp_financiero CASCADE;
            
            CREATE TABLE erp_financiero (
                id SERIAL PRIMARY KEY,
                
                -- 📥 CAMPOS CARGADOS DESDE ARCHIVO
                proveedor VARCHAR(50) NOT NULL,
                razon_social_proveedor VARCHAR(255),
                fecha_proveedor DATE,
                docto_proveedor VARCHAR(100) NOT NULL,
                valor_subtotal NUMERIC(15, 2),
                valor_impuestos NUMERIC(15, 2),
                co VARCHAR(10),
                usuario_creacion VARCHAR(100),
                clase_docto VARCHAR(255),
                nro_documento VARCHAR(50),
                
                -- 🔧 CAMPOS CALCULADOS AUTOMÁTICAMENTE
                prefijo VARCHAR(20),
                folio VARCHAR(20),
                clave_erp_financiero VARCHAR(100),
                
                -- 📊 AUDITORÍA
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- 🔑 CONSTRAINT
                UNIQUE(proveedor, docto_proveedor)
            );
            
            -- Índices para búsqueda rápida
            CREATE INDEX idx_erp_financiero_proveedor ON erp_financiero(proveedor);
            CREATE INDEX idx_erp_financiero_clave ON erp_financiero(clave_erp_financiero);
            CREATE INDEX idx_erp_financiero_clase ON erp_financiero(clase_docto);
            CREATE INDEX idx_erp_financiero_fecha ON erp_financiero(fecha_proveedor);
            
            COMMENT ON TABLE erp_financiero IS 'Registros del módulo ERP Financiero con campos calculados automáticamente';
        """)
        print("   ✅ Tabla erp_financiero creada")
        
        # ========================================
        # 6️⃣ FUNCIÓN PARA CALCULAR CAMPOS (FINANCIERO)
        # ========================================
        print("   🔧 Creando función de cálculo para erp_financiero...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION calcular_campos_erp_financiero()
            RETURNS TRIGGER AS $$
            DECLARE
                v_prefijo VARCHAR(20);
                v_folio VARCHAR(20);
                v_docto VARCHAR(100);
            BEGIN
                -- Obtener el valor de docto_proveedor
                v_docto := COALESCE(NEW.docto_proveedor, '');
                
                -- EXTRAER PREFIJO (lado izquierdo del guion)
                IF v_docto LIKE '%-%' THEN
                    v_prefijo := SPLIT_PART(v_docto, '-', 1);
                ELSE
                    v_prefijo := '';
                END IF;
                
                -- EXTRAER FOLIO (lado derecho del guion, sin ceros a la izquierda)
                IF v_docto LIKE '%-%' THEN
                    v_folio := LTRIM(SPLIT_PART(v_docto, '-', 2), '0');
                    -- Si queda vacío después de quitar ceros, poner '0'
                    IF v_folio = '' THEN
                        v_folio := '0';
                    END IF;
                ELSE
                    -- Si no hay guion, intentar extraer solo números
                    v_folio := LTRIM(REGEXP_REPLACE(v_docto, '[^0-9]', '', 'g'), '0');
                    IF v_folio = '' THEN
                        v_folio := '0';
                    END IF;
                END IF;
                
                -- Asignar valores calculados
                NEW.prefijo := v_prefijo;
                NEW.folio := v_folio;
                
                -- CALCULAR CLAVE: Proveedor + Prefijo + Folio
                NEW.clave_erp_financiero := CONCAT(
                    COALESCE(NEW.proveedor, ''),
                    '-',
                    v_prefijo,
                    '-',
                    v_folio
                );
                
                -- Actualizar fecha de modificación
                NEW.fecha_actualizacion := CURRENT_TIMESTAMP;
                
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("   ✅ Función calcular_campos_erp_financiero creada")
        
        # ========================================
        # 7️⃣ TRIGGER PARA FINANCIERO
        # ========================================
        print("   ⚡ Creando trigger para erp_financiero...")
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_calcular_erp_financiero ON erp_financiero;
            
            CREATE TRIGGER trigger_calcular_erp_financiero
                BEFORE INSERT OR UPDATE ON erp_financiero
                FOR EACH ROW
                EXECUTE FUNCTION calcular_campos_erp_financiero();
        """)
        print("   ✅ Trigger para erp_financiero creado")
        
        # ========================================
        # 8️⃣ INSERTAR DATOS DE PRUEBA
        # ========================================
        print("\n4️⃣ Insertando registros de prueba...")
        
        cursor.execute("""
            -- PRUEBA ERP COMERCIAL
            INSERT INTO erp_comercial (
                proveedor, razon_social_proveedor, fecha_docto_prov, docto_proveedor,
                valor_bruto, valor_imptos, co, usuario_creacion, clase_docto, nro_documento
            ) VALUES
            ('805028041', 'SUPERTIENDAS CAÑAVERAL', '2025-12-30', 'FE-0000000049', 1500000, 285000, '001', 'aframirezc', 'Factura de proveedor', '123456'),
            ('900123456', 'PROVEEDOR EJEMPLO SAS', '2025-12-29', '-00000123', 2000000, 380000, '002', 'jperez', 'Factura de consignación', '789012')
            ON CONFLICT (proveedor, docto_proveedor) DO NOTHING;
            
            -- PRUEBA ERP FINANCIERO
            INSERT INTO erp_financiero (
                proveedor, razon_social_proveedor, fecha_proveedor, docto_proveedor,
                valor_subtotal, valor_impuestos, co, usuario_creacion, clase_docto, nro_documento
            ) VALUES
            ('805028041', 'SUPERTIENDAS CAÑAVERAL', '2025-12-30', 'SETT-12345', 500000, 95000, '001', 'aframirezc', 'Factura de servicio compra', '654321'),
            ('900654321', 'SERVICIOS EJEMPLO LTDA', '2025-12-29', 'NC-00999', 300000, 57000, '003', 'mgarcia', 'Legalización factura caja menor', '111222')
            ON CONFLICT (proveedor, docto_proveedor) DO NOTHING;
        """)
        
        # Verificar datos insertados
        cursor.execute("SELECT COUNT(*) FROM erp_comercial")
        count_cm = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM erp_financiero")
        count_fn = cursor.fetchone()[0]
        
        print(f"   ✅ Insertados {count_cm} registros de prueba en erp_comercial")
        print(f"   ✅ Insertados {count_fn} registros de prueba en erp_financiero")
        
        # ========================================
        # 9️⃣ VERIFICAR CÁLCULOS
        # ========================================
        print("\n5️⃣ Verificando cálculos automáticos...")
        
        cursor.execute("""
            SELECT 
                docto_proveedor,
                prefijo,
                folio,
                clave_erp_comercial
            FROM erp_comercial
            ORDER BY id
            LIMIT 5
        """)
        
        print("\n   📊 ERP COMERCIAL - Ejemplos:")
        print("   " + "-" * 90)
        print(f"   {'Docto. Proveedor':<20} {'Prefijo':<15} {'Folio':<15} {'Clave':<40}")
        print("   " + "-" * 90)
        for row in cursor.fetchall():
            print(f"   {row[0]:<20} {row[1] or '':<15} {row[2] or '':<15} {row[3] or '':<40}")
        
        cursor.execute("""
            SELECT 
                docto_proveedor,
                prefijo,
                folio,
                clave_erp_financiero
            FROM erp_financiero
            ORDER BY id
            LIMIT 5
        """)
        
        print("\n   📊 ERP FINANCIERO - Ejemplos:")
        print("   " + "-" * 90)
        print(f"   {'Docto. Proveedor':<20} {'Prefijo':<15} {'Folio':<15} {'Clave':<40}")
        print("   " + "-" * 90)
        for row in cursor.fetchall():
            print(f"   {row[0]:<20} {row[1] or '':<15} {row[2] or '':<15} {row[3] or '':<40}")
        
        # Commit final
        conn.commit()
        
        print("\n" + "=" * 90)
        print("✅ TABLAS ERP CREADAS EXITOSAMENTE")
        print("=" * 90)
        print("\n📋 RESUMEN:")
        print(f"   1. clase_docto_erp: Catálogo con 11 clasificaciones")
        print(f"   2. erp_comercial: Tabla con triggers automáticos (prefijo, folio, clave)")
        print(f"   3. erp_financiero: Tabla con triggers automáticos (prefijo, folio, clave)")
        print(f"\n⚡ LOS CAMPOS SE CALCULAN AUTOMÁTICAMENTE AL INSERTAR O ACTUALIZAR")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    crear_tablas_erp()
