
-- Limpiar todas las tablas del módulo DIAN vs ERP

-- Ver conteo ANTES
SELECT 'ANTES - Maestro' as tabla, COUNT(*) as registros FROM maestro_dian_vs_erp
UNION ALL SELECT 'ANTES - DIAN', COUNT(*) FROM dian
UNION ALL SELECT 'ANTES - ERP FN', COUNT(*) FROM erp_financiero
UNION ALL SELECT 'ANTES - ERP CM', COUNT(*) FROM erp_comercial
UNION ALL SELECT 'ANTES - Acuses', COUNT(*) FROM acuses;

-- ELIMINAR todos los datos
DELETE FROM maestro_dian_vs_erp;
DELETE FROM dian;
DELETE FROM erp_financiero;
DELETE FROM erp_comercial;
DELETE FROM errores_erp;
DELETE FROM acuses;

-- Ver conteo DESPUÉS (todos deben estar en 0)
SELECT 'DESPUÉS - Maestro' as tabla, COUNT(*) as registros FROM maestro_dian_vs_erp
UNION ALL SELECT 'DESPUÉS - DIAN', COUNT(*) FROM dian
UNION ALL SELECT 'DESPUÉS - ERP FN', COUNT(*) FROM erp_financiero
UNION ALL SELECT 'DESPUÉS - ERP CM', COUNT(*) FROM erp_comercial
UNION ALL SELECT 'DESPUÉS - Acuses', COUNT(*) FROM acuses;
