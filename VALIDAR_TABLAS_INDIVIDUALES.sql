-- ============================================================================
-- SCRIPT DE VALIDACIÓN: Tablas Individuales (dian, erp, acuses)
-- ============================================================================
-- Ejecutar DESPUÉS de cargar los archivos en Visor V2
-- Fecha: 19 de Febrero de 2026
-- ============================================================================

-- 1️⃣ CONTEO DE REGISTROS POR TABLA
-- Debe mostrar datos en todas las tablas
-- ============================================================================
SELECT 
    'dian' AS tabla, 
    COUNT(*) AS total_registros,
    COUNT(CASE WHEN clave IS NOT NULL THEN 1 END) AS con_clave,
    COUNT(CASE WHEN cufe_cude IS NOT NULL AND cufe_cude != '' THEN 1 END) AS con_cufe,
    COUNT(CASE WHEN tipo_tercero IS NOT NULL AND tipo_tercero != '' THEN 1 END) AS con_tipo_tercero
FROM dian

UNION ALL

SELECT 
    'erp_comercial',
    COUNT(*),
    COUNT(CASE WHEN clave_erp_comercial IS NOT NULL THEN 1 END),
    COUNT(CASE WHEN doc_causado_por IS NOT NULL AND doc_causado_por != '' THEN 1 END),
    COUNT(CASE WHEN prefijo IS NOT NULL AND prefijo != '' THEN 1 END)
FROM erp_comercial

UNION ALL

SELECT 
    'erp_financiero',
    COUNT(*),
    COUNT(CASE WHEN clave_erp_financiero IS NOT NULL THEN 1 END),
    COUNT(CASE WHEN doc_causado_por IS NOT NULL AND doc_causado_por != '' THEN 1 END),
    COUNT(CASE WHEN prefijo IS NOT NULL AND prefijo != '' THEN 1 END)
FROM erp_financiero

UNION ALL

SELECT 
    'acuses',
    COUNT(*),
    COUNT(CASE WHEN clave_acuse IS NOT NULL AND clave_acuse != '' THEN 1 END),
    COUNT(CASE WHEN estado_docto IS NOT NULL THEN 1 END),
    COUNT(CASE WHEN cufe IS NOT NULL AND cufe != '' THEN 1 END)
FROM acuses

UNION ALL

SELECT 
    'maestro',
    COUNT(*),
    COUNT(CASE WHEN cufe IS NOT NULL AND cufe != '' THEN 1 END),
    COUNT(CASE WHEN estado_aprobacion != 'No Registra' THEN 1 END),
    COUNT(CASE WHEN modulo IS NOT NULL AND modulo != '' THEN 1 END)
FROM maestro_dian_vs_erp

ORDER BY tabla;


-- ============================================================================
-- 2️⃣ MUESTRA DE DATOS DE TABLA DIAN
-- Verifica que los campos calculados estén correctos
-- ============================================================================
SELECT 
    nit_emisor,
    nombre_emisor,
    prefijo,
    folio,
    clave,  -- Debe tener formato: NITPREFIJOfolio
    SUBSTRING(cufe_cude, 1, 20) || '...' AS cufe_inicio,
    LENGTH(cufe_cude) AS cufe_length,  -- Debe ser 96 caracteres
    tipo_tercero,  -- PROVEEDOR / ACREEDOR / PROVEEDOR Y ACREEDOR
    n_dias,  -- Días desde emisión
    modulo  -- Siempre "DIAN"
FROM dian 
ORDER BY fecha_emision DESC
LIMIT 10;


-- ============================================================================
-- 3️⃣ MUESTRA DE DATOS DE ERP COMERCIAL
-- Verifica extracción de prefijo, folio y doc_causado_por
-- ============================================================================
SELECT 
    proveedor,
    razon_social,
    docto_proveedor,  -- Original: "FE-00003951"
    prefijo,          -- Extraído: "FE"
    folio,            -- Extraído sin ceros: "3951"
    clave_erp_comercial,  -- NIT + PREFIJO + FOLIO_8
    doc_causado_por,  -- Formato: "001 - RRIASCOS - 3951"
    modulo            -- Siempre "Comercial"
FROM erp_comercial 
LIMIT 10;


-- ============================================================================
-- 4️⃣ MUESTRA DE DATOS DE ERP FINANCIERO
-- Misma estructura que Comercial
-- ============================================================================
SELECT 
    proveedor,
    razon_social,
    docto_proveedor,
    prefijo,
    folio,
    clave_erp_financiero,
    doc_causado_por,
    modulo  -- Siempre "Financiero"
FROM erp_financiero 
LIMIT 10;


-- ============================================================================
-- 5️⃣ MUESTRA DE ACUSES CON MATCHING
-- Verifica que clave_acuse coincida con CUFE de DIAN
-- ============================================================================
SELECT 
    a.nit_proveedor,
    a.razon_social,
    SUBSTRING(a.cufe, 1, 20) || '...' AS cufe_inicio,
    SUBSTRING(a.clave_acuse, 1, 20) || '...' AS clave_acuse_inicio,
    a.estado_docto,
    -- Verificar match con DIAN
    CASE 
        WHEN d.id IS NOT NULL THEN '✅ MATCH DIAN'
        ELSE '❌ NO MATCH'
    END AS match_dian
FROM acuses a
LEFT JOIN dian d ON a.clave_acuse = d.clave_acuse
LIMIT 10;


-- ============================================================================
-- 6️⃣ ESTADÍSTICAS DE MATCHING ENTRE TABLAS
-- ============================================================================

-- 6.1 Facturas DIAN que tienen match en ERP
SELECT 
    'DIAN → ERP' AS relacion,
    COUNT(DISTINCT d.id) AS total_dian,
    COUNT(DISTINCT CASE 
        WHEN erp_cm.id IS NOT NULL OR erp_fn.id IS NOT NULL THEN d.id 
    END) AS con_match_erp,
    ROUND(
        100.0 * COUNT(DISTINCT CASE 
            WHEN erp_cm.id IS NOT NULL OR erp_fn.id IS NOT NULL THEN d.id 
        END) / NULLIF(COUNT(DISTINCT d.id), 0), 
        2
    ) AS porcentaje_match
FROM dian d
LEFT JOIN erp_comercial erp_cm ON d.clave = erp_cm.clave_erp_comercial
LEFT JOIN erp_financiero erp_fn ON d.clave = erp_fn.clave_erp_financiero;


-- 6.2 Facturas DIAN que tienen acuse
SELECT 
    'DIAN → ACUSES' AS relacion,
    COUNT(DISTINCT d.id) AS total_dian,
    COUNT(DISTINCT CASE WHEN a.id IS NOT NULL THEN d.id END) AS con_acuse,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN a.id IS NOT NULL THEN d.id END) / 
        NULLIF(COUNT(DISTINCT d.id), 0), 
        2
    ) AS porcentaje_con_acuse
FROM dian d
LEFT JOIN acuses a ON d.clave_acuse = a.clave_acuse;


-- ============================================================================
-- 7️⃣ DISTRIBUCIÓN DE ESTADOS DE APROBACIÓN
-- Verifica diversidad de estados (no solo "No Registra")
-- ============================================================================
SELECT 
    estado_docto,
    COUNT(*) AS cantidad,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje
FROM acuses
GROUP BY estado_docto
ORDER BY cantidad DESC;


-- ============================================================================
-- 8️⃣ DISTRIBUCIÓN DE TIPOS DE TERCERO
-- Verifica clasificación PROVEEDOR/ACREEDOR/AMBOS
-- ============================================================================
SELECT 
    tipo_tercero,
    COUNT(*) AS cantidad_facturas,
    COUNT(DISTINCT nit_emisor) AS cantidad_nit,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS porcentaje
FROM dian
WHERE tipo_tercero IS NOT NULL AND tipo_tercero != ''
GROUP BY tipo_tercero
ORDER BY cantidad_facturas DESC;


-- ============================================================================
-- 9️⃣ VERIFICAR CAMPOS VACÍOS (NO DEBERÍA HABERLOS)
-- ============================================================================

-- 9.1 Verificar DIAN
SELECT 
    'dian' AS tabla,
    'clave' AS campo,
    COUNT(*) AS total_registros,
    COUNT(clave) AS registros_con_valor,
    COUNT(*) - COUNT(clave) AS registros_sin_valor
FROM dian
UNION ALL
SELECT 
    'dian',
    'clave_acuse',
    COUNT(*),
    COUNT(CASE WHEN clave_acuse != '' THEN 1 END),
    COUNT(*) - COUNT(CASE WHEN clave_acuse != '' THEN 1 END)
FROM dian
UNION ALL
SELECT 
    'dian',
    'cufe_cude',
    COUNT(*),
    COUNT(CASE WHEN cufe_cude != '' THEN 1 END),
    COUNT(*) - COUNT(CASE WHEN cufe_cude != '' THEN 1 END)
FROM dian;

-- 9.2 Verificar ERP Comercial
SELECT 
    'erp_comercial' AS tabla,
    'prefijo' AS campo,
    COUNT(*) AS total_registros,
    COUNT(CASE WHEN prefijo != '' THEN 1 END) AS registros_con_valor,
    COUNT(*) - COUNT(CASE WHEN prefijo != '' THEN 1 END) AS registros_sin_valor
FROM erp_comercial
UNION ALL
SELECT 
    'erp_comercial',
    'folio',
    COUNT(*),
    COUNT(CASE WHEN folio != '' THEN 1 END),
    COUNT(*) - COUNT(CASE WHEN folio != '' THEN 1 END)
FROM erp_comercial
UNION ALL
SELECT 
    'erp_comercial',
    'doc_causado_por',
    COUNT(*),
    COUNT(CASE WHEN doc_causado_por != '' THEN 1 END),
    COUNT(*) - COUNT(CASE WHEN doc_causado_por != '' THEN 1 END)
FROM erp_comercial;


-- ============================================================================
-- 🔟 VERIFICAR FORMATO DE CLAVES (ÚNICO)
-- Las claves deben ser únicas y tener el formato correcto
-- ============================================================================

-- 10.1 Verificar duplicados en dian.clave
SELECT 
    clave,
    COUNT(*) AS cantidad_duplicados
FROM dian
WHERE clave IS NOT NULL
GROUP BY clave
HAVING COUNT(*) > 1
ORDER BY cantidad_duplicados DESC
LIMIT 10;

-- 10.2 Verificar duplicados en erp_comercial.clave_erp_comercial
SELECT 
    clave_erp_comercial,
    COUNT(*) AS cantidad_duplicados
FROM erp_comercial
WHERE clave_erp_comercial IS NOT NULL
GROUP BY clave_erp_comercial
HAVING COUNT(*) > 1
ORDER BY cantidad_duplicados DESC
LIMIT 10;


-- ============================================================================
-- 1️⃣1️⃣ QUERY FINAL: VISOR V2 SIMULADO
-- Simula la consulta que hace Visor V2 para mostrar datos
-- ============================================================================
SELECT 
    d.nit_emisor,
    d.nombre_emisor,
    d.prefijo || '-' || d.folio AS factura,
    d.valor,
    d.fecha_emision,
    
    -- "Ver PDF" debería mostrar el CUFE
    CASE 
        WHEN d.cufe_cude IS NOT NULL AND d.cufe_cude != '' 
        THEN SUBSTRING(d.cufe_cude, 1, 30) || '...' 
        ELSE '❌ SIN CUFE'
    END AS ver_pdf,
    
    -- "Estado Aprobación" viene de acuses
    COALESCE(a.estado_docto, 'No Registra') AS estado_aprobacion,
    
    -- "Módulo" viene de ERP
    COALESCE(erp_cm.modulo, erp_fn.modulo, '❌ No Registrada') AS modulo,
    
    -- "Doc Causado Por"
    COALESCE(erp_cm.doc_causado_por, erp_fn.doc_causado_por, '') AS doc_causado_por,
    
    -- Tipo de tercero
    d.tipo_tercero,
    
    -- Días desde emisión
    d.n_dias
    
FROM dian d
LEFT JOIN acuses a ON d.clave_acuse = a.clave_acuse
LEFT JOIN erp_comercial erp_cm ON d.clave = erp_cm.clave_erp_comercial
LEFT JOIN erp_financiero erp_fn ON d.clave = erp_fn.clave_erp_financiero

ORDER BY d.fecha_emision DESC
LIMIT 20;


-- ============================================================================
-- RESULTADO ESPERADO DEL QUERY FINAL:
-- ============================================================================
-- Todas las filas deben tener:
-- ✅ ver_pdf con datos (no "SIN CUFE")
-- ✅ estado_aprobacion variado (no solo "No Registra")
-- ✅ modulo con "Comercial" o "Financiero" donde aplique
-- ✅ doc_causado_por con formato "CO - Usuario - Nro"
-- ============================================================================
