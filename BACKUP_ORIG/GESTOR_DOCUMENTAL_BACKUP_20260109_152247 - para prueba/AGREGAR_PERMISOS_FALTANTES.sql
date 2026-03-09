-- ============================================================================
-- SQL PARA AGREGAR PERMISOS FALTANTES AL CATÁLOGO
-- Fecha: jue 11/12/2025 - 07:55 a.ÿm.
-- Total de permisos a agregar: 326
-- ============================================================================

-- ----------------------------------------------------------------------------
-- MÓDULO: ARCHIVO_DIGITAL (2 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('archivo_digital', 'Archivo Digital', 'Módulo archivo_digital', 'editar', 'Editar registros en archivo_digital', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('archivo_digital', 'Archivo Digital', 'Módulo archivo_digital', 'editar', 'Editar registros en archivo_digital', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:documento_id>


-- ----------------------------------------------------------------------------
-- MÓDULO: CAUSACIONES (6 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('causaciones', 'Causaciones', 'Módulo causaciones', 'eliminar', 'Eliminar registros en causaciones', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/eliminar/<sede>/<path:archivo>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('causaciones', 'Causaciones', 'Módulo causaciones', 'eliminar', 'Eliminar registros en causaciones', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/eliminar/<sede>/<path:archivo>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('causaciones', 'Causaciones', 'Módulo causaciones', 'exportar', 'Exportar datos de causaciones', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /exportar/excel

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('causaciones', 'Causaciones', 'Módulo causaciones', 'exportar', 'Exportar datos de causaciones', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /exportar/excel

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('causaciones', 'Causaciones', 'Módulo causaciones', 'ver', 'Ver detalles de registros en causaciones', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /ver/<sede>/<path:archivo>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('causaciones', 'Causaciones', 'Módulo causaciones', 'ver', 'Ver detalles de registros en causaciones', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /ver/<sede>/<path:archivo>


-- ----------------------------------------------------------------------------
-- MÓDULO: CONFIGURACION (36 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'crear', 'Crear nuevo registro en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /tipos_documento/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'crear', 'Crear nuevo registro en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /centros_operacion/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'crear', 'Crear nuevo registro en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /empresas/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'crear', 'Crear nuevo registro en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /tipos_documento/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'crear', 'Crear nuevo registro en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /centros_operacion/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'crear', 'Crear nuevo registro en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /empresas/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'editar', 'Editar registros en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /tipos_documento/editar/<int:tipo_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'editar', 'Editar registros en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /centros_operacion/editar/<int:centro_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'editar', 'Editar registros en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /empresas/editar/<int:empresa_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'editar', 'Editar registros en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /tipos_documento/editar/<int:tipo_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'editar', 'Editar registros en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /centros_operacion/editar/<int:centro_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'editar', 'Editar registros en configuracion', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /empresas/editar/<int:empresa_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /tipos_documento/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /centros_operacion/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /empresas/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /formas_pago/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /tipos_servicio/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /departamentos/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /tipos_documento/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /centros_operacion/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /empresas/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /formas_pago/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /tipos_servicio/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'listar', 'Listar registros de configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /departamentos/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /centros_operacion_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /tipos_documento_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /empresas_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /formas_pago_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /tipos_servicio_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /departamentos_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /centros_operacion_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /tipos_documento_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /empresas_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /formas_pago_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /tipos_servicio_view

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('configuracion', 'Configuracion', 'Módulo configuracion', 'ver', 'Ver detalles de registros en configuracion', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /departamentos_view


-- ----------------------------------------------------------------------------
-- MÓDULO: CORE (142 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/logout

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /license/notice

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /dashboard

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /recibir_facturas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/login

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET, POST /establecer-password/<token>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/solicitar-recuperacion

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/registro/check_nit

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/registro/proveedor

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/registro/usuarios

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/documentos/upload

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/registro/finalizar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/consulta/radicado

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/forgot_request

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/change_password

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/logout

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/admin/activar_usuario

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/admin/agregar_usuario_tercero

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/telegram/webhook

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/telegram/setup_webhook

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/notificaciones/stats

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /fix-admin-nit-805028041

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /dashboard

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /admin/usuarios

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/factura/<int:factura_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/monitoreo/heartbeat

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/logout

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /cargar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /cargar_archivos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visor

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /validaciones

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /reportes

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /configuracion

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/dian

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /subir_archivos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/subir_archivos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/forzar_procesar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios/por_nit/<nit>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/enviar_emails

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/enviar_email_agrupado

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /config

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/dian_usuarios/por_nit/<nit>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/dian_usuarios/agregar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/config/smtp

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/config/smtp

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/config/smtp/probar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/config/envios

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/logs

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/dian_usuarios/desactivar/<int:user_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/logs/recientes

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/tipo-documento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/tipo-documento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/tipo-documento/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/tipo-documento/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/forma-pago

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/forma-pago

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/forma-pago/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/forma-pago/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/tipo-servicio

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/tipo-servicio

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/tipo-servicio/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/tipo-servicio/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/departamento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/departamento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/departamento/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/departamento/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/activos/tipo-documento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/activos/forma-pago

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/activos/tipo-servicio

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/activos/departamento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios/<int:usuario_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/usuarios/<int:usuario_id>/departamento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/usuarios/<int:usuario_id>/departamento/<string:departamento>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/monitoreo/heartbeat

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/logout

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /cargar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /cargar_archivos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visor

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /validaciones

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /reportes

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /configuracion

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/dian

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /subir_archivos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/subir_archivos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/forzar_procesar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios/por_nit/<nit>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/enviar_emails

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/enviar_email_agrupado

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /config

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/dian_usuarios/por_nit/<nit>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/dian_usuarios/agregar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/config/smtp

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/config/smtp

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/config/smtp/probar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/config/envios

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/logs

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/dian_usuarios/desactivar/<int:user_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/logs/recientes

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/tipo-documento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/tipo-documento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/tipo-documento/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/tipo-documento/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/forma-pago

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/forma-pago

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/forma-pago/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/forma-pago/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/tipo-servicio

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/tipo-servicio

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/tipo-servicio/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/tipo-servicio/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/departamento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/departamento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/departamento/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/departamento/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/activos/tipo-documento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/activos/forma-pago

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/activos/tipo-servicio

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/activos/departamento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios/<int:usuario_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/usuarios/<int:usuario_id>/departamento

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'acceder_modulo', 'Acceder al módulo core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/usuarios/<int:usuario_id>/departamento/<string:departamento>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'editar', 'Editar registros en core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_nit

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'editar', 'Editar registros en core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_campo

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'editar', 'Editar registros en core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/dian_usuarios/actualizar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'editar', 'Editar registros en core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_nit

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'editar', 'Editar registros en core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_campo

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'editar', 'Editar registros en core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/dian_usuarios/actualizar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'eliminar', 'Eliminar registros en core', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/dian_usuarios/eliminar/<int:user_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'eliminar', 'Eliminar registros en core', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /api/dian_usuarios/eliminar/<int:user_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'exportar', 'Exportar datos de core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar_plantilla/<tipo>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'exportar', 'Exportar datos de core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar_plantilla/<tipo>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'listar', 'Listar registros de core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/admin/listar_usuarios

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'listar', 'Listar registros de core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/dian_usuarios/todos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'listar', 'Listar registros de core', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/dian_usuarios/todos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('core', 'Core', 'Módulo core', 'ver', 'Ver detalles de registros en core', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/auth/forgot_verify


-- ----------------------------------------------------------------------------
-- MÓDULO: DIAN_VS_ERP (12 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'buscar', 'Buscar registros en dian_vs_erp', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios/buscar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'buscar', 'Buscar registros en dian_vs_erp', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios/buscar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'editar', 'Editar registros en dian_vs_erp', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/usuarios/actualizar/<int:usuario_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'editar', 'Editar registros en dian_vs_erp', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_campo

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'editar', 'Editar registros en dian_vs_erp', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_nit

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'editar', 'Editar registros en dian_vs_erp', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /api/usuarios/actualizar/<int:usuario_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'editar', 'Editar registros en dian_vs_erp', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_campo

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'editar', 'Editar registros en dian_vs_erp', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_nit

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'exportar', 'Exportar datos de dian_vs_erp', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar_plantilla/<tipo>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'exportar', 'Exportar datos de dian_vs_erp', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar_plantilla/<tipo>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'listar', 'Listar registros de dian_vs_erp', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios/todos

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('dian_vs_erp', 'Dian Vs Erp', 'Módulo dian_vs_erp', 'listar', 'Listar registros de dian_vs_erp', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/usuarios/todos


-- ----------------------------------------------------------------------------
-- MÓDULO: FACTURAS_DIGITALES (32 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'aprobar', 'Acción aprobar en facturas_digitales', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /validar_factura_registrada

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'aprobar', 'Acción aprobar en facturas_digitales', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/validar-duplicada

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'aprobar', 'Acción aprobar en facturas_digitales', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /validar_factura_registrada

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'aprobar', 'Acción aprobar en facturas_digitales', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/validar-duplicada

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'buscar', 'Buscar registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/ordenes-compra/buscar-tercero/<nit>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'buscar', 'Buscar registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/buscar-tercero

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'buscar', 'Buscar registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/ordenes-compra/buscar-tercero/<nit>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'buscar', 'Buscar registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/buscar-tercero

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'buscar', 'Buscar registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/ordenes-compra/buscar-tercero/<nit>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'crear', 'Crear nuevo registro en facturas_digitales', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/ordenes-compra/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'crear', 'Crear nuevo registro en facturas_digitales', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/ordenes-compra/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'crear', 'Crear nuevo registro en facturas_digitales', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/ordenes-compra/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'editar', 'Editar registros en facturas_digitales', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar-ruta

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'editar', 'Editar registros en facturas_digitales', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/factura/<int:id>/actualizar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'editar', 'Editar registros en facturas_digitales', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar-ruta

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'editar', 'Editar registros en facturas_digitales', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/factura/<int:id>/actualizar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'exportar', 'Exportar datos de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'exportar', 'Exportar datos de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar-factura/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'exportar', 'Exportar datos de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'exportar', 'Exportar datos de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar-factura/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'listar', 'Listar registros de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/listar-facturas-paginadas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'listar', 'Listar registros de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /listado

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'listar', 'Listar registros de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /listar-archivos/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'listar', 'Listar registros de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/listar-facturas-paginadas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'listar', 'Listar registros de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /listado

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'listar', 'Listar registros de facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /listar-archivos/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'ver', 'Ver detalles de registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /detalle/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'ver', 'Ver detalles de registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /ver-pdf/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'ver', 'Ver detalles de registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /ver-pdf/<int:id>/<path:nombre_archivo>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'ver', 'Ver detalles de registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /detalle/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'ver', 'Ver detalles de registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /ver-pdf/<int:id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('facturas_digitales', 'Facturas Digitales', 'Módulo facturas_digitales', 'ver', 'Ver detalles de registros en facturas_digitales', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /ver-pdf/<int:id>/<path:nombre_archivo>


-- ----------------------------------------------------------------------------
-- MÓDULO: GESTION_USUARIOS (4 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('gestion_usuarios', 'Gestion Usuarios', 'Módulo gestion_usuarios', 'aprobar', 'Acción aprobar en gestion_usuarios', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/invitaciones/<token>/validar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('gestion_usuarios', 'Gestion Usuarios', 'Módulo gestion_usuarios', 'aprobar', 'Acción aprobar en gestion_usuarios', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/validar-nit/<nit>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('gestion_usuarios', 'Gestion Usuarios', 'Módulo gestion_usuarios', 'aprobar', 'Acción aprobar en gestion_usuarios', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/invitaciones/<token>/validar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('gestion_usuarios', 'Gestion Usuarios', 'Módulo gestion_usuarios', 'aprobar', 'Acción aprobar en gestion_usuarios', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/validar-nit/<nit>


-- ----------------------------------------------------------------------------
-- MÓDULO: MONITOREO (4 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('monitoreo', 'Monitoreo', 'Módulo monitoreo', 'crear', 'Crear nuevo registro en monitoreo', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/alertas/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('monitoreo', 'Monitoreo', 'Módulo monitoreo', 'crear', 'Crear nuevo registro en monitoreo', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/alertas/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('monitoreo', 'Monitoreo', 'Módulo monitoreo', 'listar', 'Listar registros de monitoreo', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/ips/listar_completo

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('monitoreo', 'Monitoreo', 'Módulo monitoreo', 'listar', 'Listar registros de monitoreo', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/ips/listar_completo


-- ----------------------------------------------------------------------------
-- MÓDULO: NOTAS_CONTABLES (54 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /cargar/validar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /validar-consecutivo-correccion/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /validar-correccion/<int:token_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /cargar/validar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /validar-correccion/<int:token_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /cargar/validar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /validar-consecutivo-correccion/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /validar-correccion/<int:token_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /cargar/validar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'aprobar', 'Acción aprobar en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /validar-correccion/<int:token_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'editar', 'Editar registros en notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'editar', 'Editar registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'editar', 'Editar registros en notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'editar', 'Editar registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'editar', 'Editar registros en notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'editar', 'Editar registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'editar', 'Editar registros en notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'editar', 'Editar registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'eliminar', 'Eliminar registros en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /eliminar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'eliminar', 'Eliminar registros en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /eliminar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'eliminar', 'Eliminar registros en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /eliminar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'eliminar', 'Eliminar registros en notas_contables', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /eliminar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar_adjunto/<int:adjunto_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /descargar_notas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /exportar_excel_notas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar_adjunto/<int:adjunto_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /descargar_notas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /exportar_excel_notas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar_adjunto/<int:adjunto_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /descargar_notas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /exportar_excel_notas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /descargar_adjunto/<int:adjunto_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /descargar_notas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'exportar', 'Exportar datos de notas_contables', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /exportar_excel_notas

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'listar', 'Listar registros de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'listar', 'Listar registros de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'listar', 'Listar registros de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'listar', 'Listar registros de notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visualizar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /detalle/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visualizar_adjunto/<int:adjunto_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visualizar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /detalle/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visualizar_adjunto/<int:adjunto_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visualizar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /detalle/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visualizar_adjunto/<int:adjunto_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visualizar/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /detalle/<int:documento_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('notas_contables', 'Notas Contables', 'Módulo notas_contables', 'ver', 'Ver detalles de registros en notas_contables', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /visualizar_adjunto/<int:adjunto_id>


-- ----------------------------------------------------------------------------
-- MÓDULO: RECIBIR_FACTURAS (14 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'aprobar', 'Acción aprobar en recibir_facturas', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /validar_factura_registrada

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'aprobar', 'Acción aprobar en recibir_facturas', 'lectura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /validar_factura_registrada

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'editar', 'Editar registros en recibir_facturas', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_temporales

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'editar', 'Editar registros en recibir_facturas', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /actualizar_factura_temporal/<int:factura_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'editar', 'Editar registros en recibir_facturas', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/actualizar_temporales

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'editar', 'Editar registros en recibir_facturas', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: PUT /actualizar_factura_temporal/<int:factura_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'eliminar', 'Eliminar registros en recibir_facturas', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /borrar_factura_temporal/<int:factura_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'eliminar', 'Eliminar registros en recibir_facturas', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: DELETE /borrar_factura_temporal/<int:factura_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'exportar', 'Exportar datos de recibir_facturas', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/exportar_excel

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'exportar', 'Exportar datos de recibir_facturas', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/exportar_temporales

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'exportar', 'Exportar datos de recibir_facturas', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/exportar_excel

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'exportar', 'Exportar datos de recibir_facturas', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/exportar_temporales

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'ver', 'Ver detalles de registros en recibir_facturas', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /verificar_tercero

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('recibir_facturas', 'Recibir Facturas', 'Módulo recibir_facturas', 'ver', 'Ver detalles de registros en recibir_facturas', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /verificar_tercero


-- ----------------------------------------------------------------------------
-- MÓDULO: RELACIONES (4 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('relaciones', 'Relaciones', 'Módulo relaciones', 'aprobar', 'Acción aprobar en relaciones', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /validar_token_y_firmar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('relaciones', 'Relaciones', 'Módulo relaciones', 'aprobar', 'Acción aprobar en relaciones', 'escritura', true, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /validar_token_y_firmar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('relaciones', 'Relaciones', 'Módulo relaciones', 'buscar', 'Buscar registros en relaciones', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /consultar_recepcion/<numero_relacion>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('relaciones', 'Relaciones', 'Módulo relaciones', 'buscar', 'Buscar registros en relaciones', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /consultar_recepcion/<numero_relacion>


-- ----------------------------------------------------------------------------
-- MÓDULO: TERCEROS (16 permisos)
-- ----------------------------------------------------------------------------

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'crear', 'Crear nuevo registro en terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'crear', 'Crear nuevo registro en terceros', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'crear', 'Crear nuevo registro en terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'crear', 'Crear nuevo registro en terceros', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'crear', 'Crear nuevo registro en terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'crear', 'Crear nuevo registro en terceros', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'crear', 'Crear nuevo registro en terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'crear', 'Crear nuevo registro en terceros', 'escritura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: POST /api/crear

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'editar', 'Editar registros en terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:tercero_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'editar', 'Editar registros en terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:tercero_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'editar', 'Editar registros en terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:tercero_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'editar', 'Editar registros en terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /editar/<int:tercero_id>

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'listar', 'Listar registros de terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'listar', 'Listar registros de terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'listar', 'Listar registros de terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/listar

INSERT INTO catalogo_permisos (modulo, modulo_nombre, modulo_descripcion, accion, accion_descripcion, tipo_accion, es_critico, activo, fecha_creacion)
VALUES ('terceros', 'Terceros', 'Módulo terceros', 'listar', 'Listar registros de terceros', 'lectura', false, true, NOW())
ON CONFLICT (modulo, accion) DO NOTHING;  -- Endpoint: GET /api/listar


-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
