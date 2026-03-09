-- Consultar permisos del usuario 14652319

\echo '===== INFORMACIÓN DEL USUARIO ====='
SELECT id, usuario, nit, activo, rol 
FROM usuarios 
WHERE usuario = '14652319';

\echo ''
\echo '===== RESUMEN DE PERMISOS ====='
SELECT 
    COUNT(*) as total_registros,
    COUNT(*) FILTER (WHERE permitido = true) as permisos_activos,
    COUNT(*) FILTER (WHERE permitido = false) as permisos_inactivos
FROM permisos_usuarios
WHERE usuario_id = 22;

\echo ''
\echo '===== PERMISOS ACTIVOS (permitido=TRUE) ====='
SELECT modulo, accion, permitido
FROM permisos_usuarios
WHERE usuario_id = 22 AND permitido = true
ORDER BY modulo, accion;

\echo ''
\echo '===== VERIFICAR TABLA ANTIGUA ====='
SELECT COUNT(*) as registros_tabla_antigua
FROM information_schema.tables 
WHERE table_name = 'permisos_usuario';
