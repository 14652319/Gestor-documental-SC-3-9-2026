-- Script para agregar campo empresa_id a tablas de recibir_facturas
-- Ejecutar en pgAdmin o usando psql

-- 1. Agregar columna empresa_id a facturas_temporales
ALTER TABLE facturas_temporales 
ADD COLUMN IF NOT EXISTS empresa_id VARCHAR(10);

-- 2. Agregar foreign key (empresas usa 'sigla' como clave, no 'codigo')
ALTER TABLE facturas_temporales
DROP CONSTRAINT IF EXISTS fk_facturas_temporales_empresa;

ALTER TABLE facturas_temporales
ADD CONSTRAINT fk_facturas_temporales_empresa
FOREIGN KEY (empresa_id) REFERENCES empresas(sigla)
ON DELETE RESTRICT;

-- 3. Crear índice
CREATE INDEX IF NOT EXISTS idx_facturas_temporales_empresa
ON facturas_temporales(empresa_id);

-- 4. Agregar columna empresa_id a facturas_recibidas
ALTER TABLE facturas_recibidas
ADD COLUMN IF NOT EXISTS empresa_id VARCHAR(10);

-- 5. Agregar foreign key (empresas usa 'sigla' como clave, no 'codigo')
ALTER TABLE facturas_recibidas
DROP CONSTRAINT IF EXISTS fk_facturas_recibidas_empresa;

ALTER TABLE facturas_recibidas
ADD CONSTRAINT fk_facturas_recibidas_empresa
FOREIGN KEY (empresa_id) REFERENCES empresas(sigla)
ON DELETE RESTRICT;

-- 6. Crear índice
CREATE INDEX IF NOT EXISTS idx_facturas_recibidas_empresa
ON facturas_recibidas(empresa_id);

-- 7. Verificar cambios
SELECT 'facturas_temporales' as tabla, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'facturas_temporales' AND column_name = 'empresa_id'
UNION ALL
SELECT 'facturas_recibidas' as tabla, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'facturas_recibidas' AND column_name = 'empresa_id';

-- Resultado esperado:
-- tabla                  | column_name | data_type        | is_nullable
-- -----------------------+-------------+------------------+-------------
-- facturas_temporales    | empresa_id  | character varying| YES
-- facturas_recibidas     | empresa_id  | character varying| YES
