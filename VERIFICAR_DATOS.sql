-- Verificación rápida de datos en tablas

-- 1. Contar registros en todas las tablas
SELECT 'DIAN' as tabla, COUNT(*) as registros FROM dian
UNION ALL SELECT 'ERP Financiero', COUNT(*) FROM erp_financiero
UNION ALL SELECT 'ERP Comercial', COUNT(*) FROM erp_comercial
UNION ALL SELECT 'Acuses', COUNT(*) FROM acuses
UNION ALL SELECT 'Maestro', COUNT(*) FROM maestro_dian_vs_erp;

-- 2. Verificar CUFE en maestro
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN cufe IS NOT NULL AND cufe != '' THEN 1 END) as con_cufe,
    COUNT(CASE WHEN cufe IS NULL OR cufe = '' THEN 1 END) as sin_cufe
FROM maestro_dian_vs_erp;

-- 3. Ver primeros 5 registros de maestro
SELECT 
    nit_emisor, 
    prefijo, 
    folio, 
    LEFT(cufe, 20) as cufe_inicio,
    estado_aprobacion
FROM maestro_dian_vs_erp
LIMIT 5;

-- 4. Distribución de estados
SELECT 
    estado_aprobacion,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp
GROUP BY estado_aprobacion
ORDER BY cantidad DESC;
