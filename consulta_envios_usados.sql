-- Consulta para ver qué envíos programados se están usando
-- Ejecutar en pgAdmin o cliente PostgreSQL

-- 1. Configuraciones con su historial de uso
SELECT 
    ep.id,
    ep.nombre,
    ep.tipo,
    ep.activo,
    ep.frecuencia,
    ep.hora_envio,
    ep.proximo_envio,
    COUNT(he.id) as total_envios,
    SUM(CASE WHEN he.exitoso = TRUE THEN 1 ELSE 0 END) as envios_exitosos,
    SUM(CASE WHEN he.exitoso = FALSE THEN 1 ELSE 0 END) as envios_fallidos,
    MAX(he.fecha_envio) as ultimo_envio,
    MIN(he.fecha_envio) as primer_envio
FROM envios_programados_dian_vs_erp ep
LEFT JOIN historial_envios_dian_vs_erp he ON ep.id = he.configuracion_id
GROUP BY ep.id, ep.nombre, ep.tipo, ep.activo, ep.frecuencia, ep.hora_envio, ep.proximo_envio
ORDER BY 
    ep.activo DESC,
    COUNT(he.id) DESC,
    ep.nombre;

-- 2. Solo configuraciones activas con uso
SELECT 
    ep.id,
    ep.nombre,
    COUNT(he.id) as total_envios,
    MAX(he.fecha_envio) as ultimo_envio
FROM envios_programados_dian_vs_erp ep
LEFT JOIN historial_envios_dian_vs_erp he ON ep.id = he.configuracion_id
WHERE ep.activo = TRUE
GROUP BY ep.id, ep.nombre
HAVING COUNT(he.id) > 0
ORDER BY COUNT(he.id) DESC;

-- 3. Configuraciones activas SIN uso (nunca ejecutadas)
SELECT 
    ep.id,
    ep.nombre,
    ep.tipo,
    ep.proximo_envio
FROM envios_programados_dian_vs_erp ep
LEFT JOIN historial_envios_dian_vs_erp he ON ep.id = he.configuracion_id
WHERE ep.activo = TRUE
GROUP BY ep.id, ep.nombre, ep.tipo, ep.proximo_envio
HAVING COUNT(he.id) = 0;

-- 4. Últimos 20 envíos ejecutados
SELECT 
    he.fecha_envio,
    ep.nombre,
    he.exitoso,
    he.mensaje
FROM historial_envios_dian_vs_erp he
JOIN envios_programados_dian_vs_erp ep ON he.configuracion_id = ep.id
ORDER BY he.fecha_envio DESC
LIMIT 20;
