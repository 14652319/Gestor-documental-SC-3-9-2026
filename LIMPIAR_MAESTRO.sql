-- =====================================================
-- LIMPIAR TABLA MAESTRO (sin tocar archivos fuente)
-- =====================================================

-- Ver estado ANTES
SELECT 'ANTES - Maestro:' as tabla, COUNT(*) as registros FROM maestro_dian_vs_erp
UNION ALL
SELECT 'ANTES - DIAN:', COUNT(*) FROM dian
UNION ALL
SELECT 'ANTES - Acuses:', COUNT(*) FROM acuses;

-- ELIMINAR todos los registros de maestro
DELETE FROM maestro_dian_vs_erp;

-- Ver estado DESPUÉS
SELECT 'DESPUÉS - Maestro:' as tabla, COUNT(*) as registros FROM maestro_dian_vs_erp
UNION ALL
SELECT 'DESPUÉS - DIAN:', COUNT(*) FROM dian
UNION ALL
SELECT 'DESPUÉS - Acuses:', COUNT(*) FROM acuses;

-- Mensaje final
SELECT '✅ MAESTRO LIMPIADO - Ahora procesa desde la web' as mensaje;
