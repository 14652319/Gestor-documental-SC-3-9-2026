-- SCRIPT DE LIMPIEZA PARA NUEVA CARGA
-- Fecha: 19 de febrero, 2026
-- ======================================

-- PASO 1: Respaldar datos de causación (si existen)
DROP TABLE IF EXISTS backup_causacion_temp;

CREATE TABLE backup_causacion_temp AS
SELECT 
    nit_emisor, prefijo, folio,
    causada, fecha_causacion, usuario_causacion, doc_causado_por,
    recibida, fecha_recibida, usuario_recibio,
    rechazada, fecha_rechazo, motivo_rechazo,
    estado_contable, origen_sincronizacion
FROM maestro_dian_vs_erp
WHERE causada = TRUE 
   OR rechazada = TRUE
   OR doc_causado_por IS NOT NULL;

-- PASO 2: Limpiar tablas
-- Opción A: LIMPIEZA COMPLETA (descomentar si quieres empezar de cero)
-- DELETE FROM dian;
-- DELETE FROM erp_financiero;
-- DELETE FROM erp_comercial;
-- DELETE FROM acuses;
-- DELETE FROM maestro_dian_vs_erp;

-- Opción B: SOLO MAESTRO (recomendado si ya tienes los datos cargados)
DELETE FROM maestro_dian_vs_erp;

-- PASO 3: Verificar limpieza
SELECT 'DIAN' as tabla, COUNT(*) as registros FROM dian
UNION ALL
SELECT 'ERP Financiero', COUNT(*) FROM erp_financiero
UNION ALL
SELECT 'ERP Comercial', COUNT(*) FROM erp_comercial
UNION ALL
SELECT 'Acuses', COUNT(*) FROM acuses
UNION ALL
SELECT 'Maestro', COUNT(*) FROM maestro_dian_vs_erp
UNION ALL
SELECT 'Backup Causación', COUNT(*) FROM backup_causacion_temp;

-- ======================================
-- DESPUÉS DE PROCESAR DESDE LA WEB:
-- ======================================

-- PASO 4: Restaurar datos de causación (ejecutar DESPUÉS de procesar)
-- UPDATE maestro_dian_vs_erp m
-- SET causada = b.causada,
--     fecha_causacion = b.fecha_causacion,
--     usuario_causacion = b.usuario_causacion,
--     doc_causado_por = b.doc_causado_por,
--     recibida = b.recibida,
--     fecha_recibida = b.fecha_recibida,
--     usuario_recibio = b.usuario_recibio,
--     rechazada = b.rechazada,
--     fecha_rechazo = b.fecha_rechazo,
--     motivo_rechazo = b.motivo_rechazo,
--     estado_contable = b.estado_contable,
--     origen_sincronizacion = b.origen_sincronizacion
-- FROM backup_causacion_temp b
-- WHERE m.nit_emisor = b.nit_emisor
--   AND m.prefijo = b.prefijo
--   AND m.folio = b.folio;

-- PASO 5: Verificar resultados finales
SELECT 
    estado_aprobacion,
    COUNT(*) as cantidad,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as porcentaje
FROM maestro_dian_vs_erp
GROUP BY estado_aprobacion
ORDER BY cantidad DESC;

-- Verificar CUFEs
SELECT 
    'Con CUFE' as descripcion,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp
WHERE cufe IS NOT NULL AND cufe != ''
UNION ALL
SELECT 
    'Con estado != No Registra',
    COUNT(*)
FROM maestro_dian_vs_erp
WHERE estado_aprobacion != 'No Registra';
