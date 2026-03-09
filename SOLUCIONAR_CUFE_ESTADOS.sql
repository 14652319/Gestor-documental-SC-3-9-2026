-- ================================================================
-- SOLUCIÓN RÁPIDA: Actualizar CUFEs y Estados de Aprobación
-- ================================================================
-- Fecha: 19 de febrero, 2026
-- Problema: maestro_dian_vs_erp tiene CUFE = NULL
-- Solución: Copiar CUFEs desde tabla DIAN y estados desde ACUSES
-- ================================================================

-- PASO 1: Verificar estado actual
SELECT 
    'Maestro - Total registros' as descripcion,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp

UNION ALL

SELECT 
    'Maestro - Con CUFE NULL',
    COUNT(*)
FROM maestro_dian_vs_erp
WHERE cufe IS NULL OR cufe = ''

UNION ALL

SELECT 
    'DIAN - Con CUFE válidos',
    COUNT(*)
FROM dian
WHERE cufe_cude IS NOT NULL AND cufe_cude != ''

UNION ALL

SELECT 
    'ACUSES - Con CUFE válidos',
    COUNT(*)
FROM acuses
WHERE cufe IS NOT NULL AND cufe != '';

-- ================================================================
-- PASO 2: Actualizar CUFEs desde tabla DIAN
-- ================================================================
-- Esto copiará los CUFEs de la tabla DIAN a la tabla maestro
-- haciendo match por NIT + Prefijo + Folio

UPDATE maestro_dian_vs_erp m
SET cufe = d.cufe_cude
FROM dian d
WHERE m.nit_emisor = d.nit_emisor
  AND m.prefijo = d.prefijo
  AND m.folio = d.folio
  AND d.cufe_cude IS NOT NULL
  AND d.cufe_cude != ''
  AND (m.cufe IS NULL OR m.cufe = '');

-- Verificar resultado
SELECT 
    'CUFEs actualizados' as resultado,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp
WHERE cufe IS NOT NULL AND cufe != '';

-- ================================================================
-- PASO 3: Actualizar Estados de Aprobación desde ACUSES
-- ================================================================
-- Esto actualizará el campo estado_aprobacion haciendo match por CUFE

UPDATE maestro_dian_vs_erp m
SET 
    estado_aprobacion = a.estado_docto,
    acuses_recibidos = CASE 
        WHEN a.estado_docto = 'Pendiente' THEN 1
        WHEN a.estado_docto = 'Reclamado' THEN 2
        WHEN a.estado_docto = 'Rechazado' THEN 3
        WHEN a.estado_docto = 'Rechazada' THEN 3
        WHEN a.estado_docto = 'Acuse Bien/Servicio' THEN 4
        WHEN a.estado_docto = 'Acuse Recibido' THEN 4
        WHEN a.estado_docto = 'Aceptación Expresa' THEN 5
        WHEN a.estado_docto = 'Aceptación Tácita' THEN 6
        ELSE 0
    END
FROM acuses a
WHERE m.cufe = a.cufe
  AND m.cufe IS NOT NULL
  AND m.cufe != ''
  AND a.cufe IS NOT NULL
  AND a.cufe != '';

-- Verificar resultado
SELECT 
    'Estados actualizados' as resultado,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp
WHERE estado_aprobacion != 'No Registra'
  AND estado_aprobacion IS NOT NULL;

-- ================================================================
-- PASO 4: Verificar distribución final de estados
-- ================================================================
SELECT 
    COALESCE(estado_aprobacion, 'NULL') as estado,
    COUNT(*) as cantidad,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as porcentaje
FROM maestro_dian_vs_erp
GROUP BY estado_aprobacion
ORDER BY cantidad DESC;

-- ================================================================
-- PASO 5: Ver ejemplos de registros actualizados
-- ================================================================
SELECT 
    nit_emisor,
    razon_social,
    prefijo,
    folio,
    SUBSTRING(cufe, 1, 40) as cufe_inicio,
    estado_aprobacion,
    acuses_recibidos
FROM maestro_dian_vs_erp
WHERE estado_aprobacion != 'No Registra'
  AND cufe IS NOT NULL
ORDER BY id DESC
LIMIT 10;

-- ================================================================
-- CONSULTAS DE VERIFICACIÓN ADICIONALES
-- ================================================================

-- Ver facturas con match entre DIAN y ACUSES
SELECT 
    'Matches DIAN-ACUSES' as metrica,
    COUNT(*) as valor
FROM dian d
INNER JOIN acuses a ON d.cufe_cude = a.cufe;

-- Ver distribución de estados en ACUSES
SELECT 
    estado_docto,
    COUNT(*) as cantidad
FROM acuses
GROUP BY estado_docto
ORDER BY cantidad DESC;

-- Ver registros que aún no tienen acuse (esperado)
SELECT 
    'Facturas sin acuse' as descripcion,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp
WHERE estado_aprobacion = 'No Registra'
  AND cufe IS NOT NULL;

-- ================================================================
-- NOTAS FINALES
-- ================================================================
-- Si después de ejecutar esto todavía ves "No Registra":
--  1. Verifica que los CUFEs en maestro sean correctos:
--     SELECT cufe FROM maestro_dian_vs_erp WHERE cufe IS NOT NULL LIMIT 5;
--
--  2. Verifica que haya matches:
--     SELECT COUNT(*) FROM maestro_dian_vs_erp m
--     INNER JOIN acuses a ON m.cufe = a.cufe;
--
--  3. Si no hay matches, verifica que los archivos DIAN y ACUSES 
--     correspondan al mismo período/empresa
--
-- Recuerda: El campo "Fecha" en ACUSES es la fecha del reporte,
-- NO la fecha de las facturas. El matching es SOLO por CUFE.
-- ================================================================
