
-- ============================================
-- SOLUCION: Eliminar UNIQUE constraint en clave
-- ============================================

-- 1. Eliminar constraint UNIQUE
ALTER TABLE dian DROP CONSTRAINT IF EXISTS uk_dian_clave;

-- 2. Limpiar tabla para recarga completa
TRUNCATE TABLE dian CASCADE;

-- 3. Verificar que se elimino (debe retornar 0 filas)
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint 
WHERE conrelid = 'dian'::regclass 
  AND conname = 'uk_dian_clave';

-- 4. Ver estructura actual de la tabla
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as definition
FROM pg_constraint 
WHERE conrelid = 'dian'::regclass
ORDER BY contype;

