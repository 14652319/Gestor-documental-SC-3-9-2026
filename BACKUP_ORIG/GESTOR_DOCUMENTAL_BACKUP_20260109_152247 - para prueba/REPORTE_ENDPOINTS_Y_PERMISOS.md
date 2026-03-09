# 🔍 REPORTE COMPLETO DE ENDPOINTS Y PERMISOS
**Fecha:** jue 11/12/2025 - 07:55 a.ÿm.

---

## 📊 RESUMEN EJECUTIVO

- **Endpoints backend encontrados:** 679
- **Funcionalidades frontend encontradas:** 801
- **Permisos en catálogo:** 171
- **Módulos con permisos:** 14
- **⚠️ Endpoints SIN permiso:** 326

---

## 📂 ENDPOINTS POR MÓDULO

### ARCHIVO_DIGITAL (8 endpoints | 6 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | pages.py | 101 |
| `/` | GET | pages.py | 101 |
| `/cargar` | GET | pages.py | 26 |
| `/cargar` | GET | pages.py | 26 |
| `/editar/<int:documento_id>` | GET | pages.py | 92 |
| `/editar/<int:documento_id>` | GET | pages.py | 92 |
| `/visor` | GET | pages.py | 35 |
| `/visor` | GET | pages.py | 35 |

### CAUSACIONES (12 endpoints | 16 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | routes.py | 24 |
| `/` | GET | routes.py | 24 |
| `/api/eliminar/<sede>/<path:archivo>` | POST | routes.py | 490 |
| `/api/eliminar/<sede>/<path:archivo>` | POST | routes.py | 490 |
| `/api/metadata/<sede>/<path:archivo>` | GET | routes.py | 208 |
| `/api/metadata/<sede>/<path:archivo>` | GET | routes.py | 208 |
| `/exportar/excel` | GET | routes.py | 291 |
| `/exportar/excel` | GET | routes.py | 291 |
| `/renombrar/<sede>/<path:archivo>` | GET, POST | routes.py | 534 |
| `/renombrar/<sede>/<path:archivo>` | GET, POST | routes.py | 534 |
| `/ver/<sede>/<path:archivo>` | GET | routes.py | 152 |
| `/ver/<sede>/<path:archivo>` | GET | routes.py | 152 |

### CONFIGURACION (46 endpoints | 5 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/centros_operacion/crear` | POST | routes.py | 214 |
| `/centros_operacion/crear` | POST | routes.py | 214 |
| `/centros_operacion/editar/<int:centro_id>` | PUT | routes.py | 284 |
| `/centros_operacion/editar/<int:centro_id>` | PUT | routes.py | 284 |
| `/centros_operacion/listar` | GET | routes.py | 193 |
| `/centros_operacion/listar` | GET | routes.py | 193 |
| `/centros_operacion/opciones` | GET | routes.py | 59 |
| `/centros_operacion/opciones` | GET | routes.py | 59 |
| `/centros_operacion/toggle/<int:centro_id>` | PATCH | routes.py | 373 |
| `/centros_operacion/toggle/<int:centro_id>` | PATCH | routes.py | 373 |
| `/centros_operacion_view` | GET | routes.py | 406 |
| `/centros_operacion_view` | GET | routes.py | 406 |
| `/departamentos/listar` | GET | routes.py | 643 |
| `/departamentos/listar` | GET | routes.py | 643 |
| `/departamentos_view` | GET | routes.py | 679 |
| `/departamentos_view` | GET | routes.py | 679 |
| `/empresas/crear` | POST | routes.py | 450 |
| `/empresas/crear` | POST | routes.py | 450 |
| `/empresas/editar/<int:empresa_id>` | PUT | routes.py | 502 |
| `/empresas/editar/<int:empresa_id>` | PUT | routes.py | 502 |
| `/empresas/listar` | GET | routes.py | 429 |
| `/empresas/listar` | GET | routes.py | 429 |
| `/empresas/opciones` | GET | routes.py | 35 |
| `/empresas/opciones` | GET | routes.py | 35 |
| `/empresas/toggle/<int:empresa_id>` | PATCH | routes.py | 557 |
| `/empresas/toggle/<int:empresa_id>` | PATCH | routes.py | 557 |
| `/empresas_view` | GET | routes.py | 594 |
| `/empresas_view` | GET | routes.py | 594 |
| `/formas_pago/listar` | GET | routes.py | 609 |
| `/formas_pago/listar` | GET | routes.py | 609 |
| `/formas_pago_view` | GET | routes.py | 659 |
| `/formas_pago_view` | GET | routes.py | 659 |
| `/tipos_documento/crear` | POST | routes.py | 96 |
| `/tipos_documento/crear` | POST | routes.py | 96 |
| `/tipos_documento/editar/<int:tipo_id>` | PUT | routes.py | 147 |
| `/tipos_documento/editar/<int:tipo_id>` | PUT | routes.py | 147 |
| `/tipos_documento/listar` | GET | routes.py | 75 |
| `/tipos_documento/listar` | GET | routes.py | 75 |
| `/tipos_documento/opciones` | GET | routes.py | 47 |
| `/tipos_documento/opciones` | GET | routes.py | 47 |
| `/tipos_documento_view` | GET | routes.py | 416 |
| `/tipos_documento_view` | GET | routes.py | 416 |
| `/tipos_servicio/listar` | GET | routes.py | 626 |
| `/tipos_servicio/listar` | GET | routes.py | 626 |
| `/tipos_servicio_view` | GET | routes.py | 669 |
| `/tipos_servicio_view` | GET | routes.py | 669 |

### CORE (142 endpoints | 0 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | app.py | 1113 |
| `/` | GET | routes.py | 163 |
| `/` | GET | config_routes.py | 16 |
| `/` | GET | routes.py | 163 |
| `/` | GET | config_routes.py | 16 |
| `/admin/usuarios` | GET | security_utils.py | 581 |
| `/api/activos/departamento` | GET | config_routes.py | 450 |
| `/api/activos/departamento` | GET | config_routes.py | 450 |
| `/api/activos/forma-pago` | GET | config_routes.py | 424 |
| `/api/activos/forma-pago` | GET | config_routes.py | 424 |
| `/api/activos/tipo-documento` | GET | config_routes.py | 411 |
| `/api/activos/tipo-documento` | GET | config_routes.py | 411 |
| `/api/activos/tipo-servicio` | GET | config_routes.py | 437 |
| `/api/activos/tipo-servicio` | GET | config_routes.py | 437 |
| `/api/actualizar_campo` | POST | routes.py | 626 |
| `/api/actualizar_campo` | POST | routes.py | 626 |
| `/api/actualizar_nit` | POST | routes.py | 599 |
| `/api/actualizar_nit` | POST | routes.py | 599 |
| `/api/admin/activar_usuario` | POST | app.py | 2347 |
| `/api/admin/agregar_usuario_tercero` | POST | app.py | 2385 |
| `/api/admin/listar_usuarios` | GET | app.py | 2468 |
| `/api/auth/change_password` | POST | app.py | 2172 |
| `/api/auth/forgot_request` | POST | app.py | 2072 |
| `/api/auth/forgot_verify` | POST | app.py | 2147 |
| `/api/auth/login` | POST | app.py | 1156 |
| `/api/auth/logout` | POST | actualizar_sistema_completo.py | 280 |
| `/api/auth/logout` | POST | app.py | 2210 |
| `/api/auth/logout` | POST | routes.py | 132 |
| `/api/auth/logout` | POST | routes.py | 132 |
| `/api/auth/solicitar-recuperacion` | POST | app.py | 1438 |
| `/api/config/envios` | GET | routes.py | 1014 |
| `/api/config/envios` | GET | routes.py | 1014 |
| `/api/config/smtp` | GET | routes.py | 914 |
| `/api/config/smtp` | POST | routes.py | 945 |
| `/api/config/smtp` | GET | routes.py | 914 |
| `/api/config/smtp` | POST | routes.py | 945 |
| `/api/config/smtp/probar` | GET | routes.py | 954 |
| `/api/config/smtp/probar` | GET | routes.py | 954 |
| `/api/consulta/radicado` | POST | app.py | 2005 |
| `/api/departamento` | GET | config_routes.py | 315 |
| `/api/departamento` | POST | config_routes.py | 337 |
| `/api/departamento` | GET | config_routes.py | 315 |
| `/api/departamento` | POST | config_routes.py | 337 |
| `/api/departamento/<int:id>` | PUT | config_routes.py | 364 |
| `/api/departamento/<int:id>` | DELETE | config_routes.py | 392 |
| `/api/departamento/<int:id>` | PUT | config_routes.py | 364 |
| `/api/departamento/<int:id>` | DELETE | config_routes.py | 392 |
| `/api/dian` | GET | routes.py | 230 |
| `/api/dian` | GET | routes.py | 230 |
| `/api/dian_usuarios/actualizar` | PUT | routes.py | 882 |
| `/api/dian_usuarios/actualizar` | PUT | routes.py | 882 |
| `/api/dian_usuarios/agregar` | POST | routes.py | 844 |
| `/api/dian_usuarios/agregar` | POST | routes.py | 844 |
| `/api/dian_usuarios/desactivar/<int:user_id>` | POST | routes.py | 1176 |
| `/api/dian_usuarios/desactivar/<int:user_id>` | POST | routes.py | 1176 |
| `/api/dian_usuarios/eliminar/<int:user_id>` | DELETE | routes.py | 1195 |
| `/api/dian_usuarios/eliminar/<int:user_id>` | DELETE | routes.py | 1195 |
| `/api/dian_usuarios/por_nit/<nit>` | GET | routes.py | 810 |
| `/api/dian_usuarios/por_nit/<nit>` | GET | routes.py | 810 |
| `/api/dian_usuarios/todos` | GET | routes.py | 1120 |
| `/api/dian_usuarios/todos` | GET | routes.py | 1120 |
| `/api/documentos/upload` | POST | app.py | 1707 |
| `/api/enviar_email_agrupado` | POST | routes.py | 715 |
| `/api/enviar_email_agrupado` | POST | routes.py | 715 |
| `/api/enviar_emails` | POST | routes.py | 687 |
| `/api/enviar_emails` | POST | routes.py | 687 |
| `/api/factura/<int:factura_id>` | GET | security_utils.py | 614 |
| `/api/forma-pago` | GET | config_routes.py | 123 |
| `/api/forma-pago` | POST | config_routes.py | 145 |
| `/api/forma-pago` | GET | config_routes.py | 123 |
| `/api/forma-pago` | POST | config_routes.py | 145 |
| `/api/forma-pago/<int:id>` | PUT | config_routes.py | 172 |
| `/api/forma-pago/<int:id>` | DELETE | config_routes.py | 200 |
| `/api/forma-pago/<int:id>` | PUT | config_routes.py | 172 |
| `/api/forma-pago/<int:id>` | DELETE | config_routes.py | 200 |
| `/api/forzar_procesar` | GET | routes.py | 447 |
| `/api/forzar_procesar` | GET | routes.py | 447 |
| `/api/logs` | GET | routes.py | 1058 |
| `/api/logs` | GET | routes.py | 1058 |
| `/api/logs/recientes` | GET | routes.py | 1214 |
| `/api/logs/recientes` | GET | routes.py | 1214 |
| `/api/monitoreo/heartbeat` | POST | MIDDLEWARE_SESIONES.py | 95 |
| `/api/monitoreo/heartbeat` | POST | MIDDLEWARE_SESIONES.py | 95 |
| `/api/notificaciones/stats` | GET | app.py | 2576 |
| `/api/registro/check_nit` | POST | app.py | 1551 |
| `/api/registro/finalizar` | POST | app.py | 1782 |
| `/api/registro/proveedor` | POST | app.py | 1594 |
| `/api/registro/usuarios` | POST | app.py | 1650 |
| `/api/subir_archivos` | POST | routes.py | 396 |
| `/api/subir_archivos` | POST | routes.py | 396 |
| `/api/telegram/setup_webhook` | POST | app.py | 2536 |
| `/api/telegram/webhook` | POST | app.py | 2503 |
| `/api/tipo-documento` | GET | config_routes.py | 27 |
| `/api/tipo-documento` | POST | config_routes.py | 49 |
| `/api/tipo-documento` | GET | config_routes.py | 27 |
| `/api/tipo-documento` | POST | config_routes.py | 49 |
| `/api/tipo-documento/<int:id>` | PUT | config_routes.py | 76 |
| `/api/tipo-documento/<int:id>` | DELETE | config_routes.py | 104 |
| `/api/tipo-documento/<int:id>` | PUT | config_routes.py | 76 |
| `/api/tipo-documento/<int:id>` | DELETE | config_routes.py | 104 |
| `/api/tipo-servicio` | GET | config_routes.py | 219 |
| `/api/tipo-servicio` | POST | config_routes.py | 241 |
| `/api/tipo-servicio` | GET | config_routes.py | 219 |
| `/api/tipo-servicio` | POST | config_routes.py | 241 |
| `/api/tipo-servicio/<int:id>` | PUT | config_routes.py | 268 |
| `/api/tipo-servicio/<int:id>` | DELETE | config_routes.py | 296 |
| `/api/tipo-servicio/<int:id>` | PUT | config_routes.py | 268 |
| `/api/tipo-servicio/<int:id>` | DELETE | config_routes.py | 296 |
| `/api/usuarios` | GET | config_routes.py | 466 |
| `/api/usuarios` | GET | config_routes.py | 466 |
| `/api/usuarios/<int:usuario_id>` | GET | config_routes.py | 506 |
| `/api/usuarios/<int:usuario_id>` | GET | config_routes.py | 506 |
| `/api/usuarios/<int:usuario_id>/departamento` | POST | config_routes.py | 563 |
| `/api/usuarios/<int:usuario_id>/departamento` | POST | config_routes.py | 563 |
| `/api/usuarios/<int:usuario_id>/departamento/<string:departamento>` | DELETE | config_routes.py | 631 |
| `/api/usuarios/<int:usuario_id>/departamento/<string:departamento>` | DELETE | config_routes.py | 631 |
| `/api/usuarios/por_nit/<nit>` | GET | routes.py | 652 |
| `/api/usuarios/por_nit/<nit>` | GET | routes.py | 652 |
| `/cargar` | GET | routes.py | 184 |
| `/cargar` | GET | routes.py | 184 |
| `/cargar_archivos` | GET | routes.py | 185 |
| `/cargar_archivos` | GET | routes.py | 185 |
| `/config` | GET | routes.py | 804 |
| `/config` | GET | routes.py | 804 |
| `/configuracion` | GET | routes.py | 221 |
| `/configuracion` | GET | routes.py | 221 |
| `/dashboard` | GET | app.py | 1120 |
| `/dashboard` | GET | security_utils.py | 547 |
| `/descargar_plantilla/<tipo>` | GET | routes.py | 332 |
| `/descargar_plantilla/<tipo>` | GET | routes.py | 332 |
| `/establecer-password/<token>` | GET, POST | app.py | 1301 |
| `/fix-admin-nit-805028041` | GET | app.py | 2734 |
| `/license/notice` | GET | app.py | 69 |
| `/recibir_facturas` | GET | app.py | 1140 |
| `/reportes` | GET | routes.py | 212 |
| `/reportes` | GET | routes.py | 212 |
| `/subir_archivos` | POST | routes.py | 395 |
| `/subir_archivos` | POST | routes.py | 395 |
| `/validaciones` | GET | routes.py | 203 |
| `/validaciones` | GET | routes.py | 203 |
| `/visor` | GET | routes.py | 194 |
| `/visor` | GET | routes.py | 194 |

### DIAN_VS_ERP (50 endpoints | 13 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | app.py | 221 |
| `/` | GET | app.py | 221 |
| `/api/actualizar_campo` | POST | app.py | 1315 |
| `/api/actualizar_campo` | POST | app.py | 1315 |
| `/api/actualizar_nit` | POST | app.py | 1359 |
| `/api/actualizar_nit` | POST | app.py | 1359 |
| `/api/config/smtp` | POST | app.py | 1732 |
| `/api/config/smtp` | GET | app.py | 1752 |
| `/api/config/smtp` | POST | app.py | 1732 |
| `/api/config/smtp` | GET | app.py | 1752 |
| `/api/config/smtp/probar` | GET | app.py | 1767 |
| `/api/config/smtp/probar` | GET | app.py | 1767 |
| `/api/dian` | GET | app.py | 227 |
| `/api/dian` | GET | app.py | 227 |
| `/api/enviar_email_agrupado` | POST | app.py | 1507 |
| `/api/enviar_email_agrupado` | POST | app.py | 1507 |
| `/api/enviar_emails` | POST | app.py | 1409 |
| `/api/enviar_emails` | POST | app.py | 1409 |
| `/api/estadisticas/destinatarios` | GET | app.py | 1692 |
| `/api/estadisticas/destinatarios` | GET | app.py | 1692 |
| `/api/estadisticas/envios` | GET | app.py | 1601 |
| `/api/estadisticas/envios` | GET | app.py | 1601 |
| `/api/estadisticas/factura/<cufe>` | GET | app.py | 1651 |
| `/api/estadisticas/factura/<cufe>` | GET | app.py | 1651 |
| `/api/forzar_procesar` | GET | app.py | 1151 |
| `/api/forzar_procesar` | GET | app.py | 1151 |
| `/api/logs/recientes` | GET | app.py | 1284 |
| `/api/logs/recientes` | GET | app.py | 1284 |
| `/api/usuarios/actualizar/<int:usuario_id>` | PUT | app.py | 1232 |
| `/api/usuarios/actualizar/<int:usuario_id>` | PUT | app.py | 1232 |
| `/api/usuarios/agregar` | POST | app.py | 1180 |
| `/api/usuarios/agregar` | POST | app.py | 1180 |
| `/api/usuarios/buscar` | GET | app.py | 1266 |
| `/api/usuarios/buscar` | GET | app.py | 1266 |
| `/api/usuarios/desactivar/<int:usuario_id>` | POST | app.py | 1250 |
| `/api/usuarios/desactivar/<int:usuario_id>` | POST | app.py | 1250 |
| `/api/usuarios/por_nit/<nit>` | GET | app.py | 1207 |
| `/api/usuarios/por_nit/<nit>` | GET | app.py | 1207 |
| `/api/usuarios/todos` | GET | app.py | 1221 |
| `/api/usuarios/todos` | GET | app.py | 1221 |
| `/cargar` | GET | app.py | 1169 |
| `/cargar` | GET | app.py | 1169 |
| `/configuracion` | GET | app.py | 1304 |
| `/configuracion` | GET | app.py | 1304 |
| `/descargar_plantilla/<tipo>` | GET | app.py | 1139 |
| `/descargar_plantilla/<tipo>` | GET | app.py | 1139 |
| `/subir_archivos` | POST | app.py | 939 |
| `/subir_archivos` | POST | app.py | 939 |
| `/visor` | GET | app.py | 1162 |
| `/visor` | GET | app.py | 1162 |

### FACTURAS_DIGITALES (90 endpoints | 15 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | routes.py | 659 |
| `/` | GET | routes.py | 659 |
| `/abrir-adobe/<int:id>` | POST | routes.py | 2981 |
| `/abrir-adobe/<int:id>` | POST | routes.py | 2981 |
| `/api/actualizar-ruta` | POST | routes.py | 2231 |
| `/api/actualizar-ruta` | POST | routes.py | 2231 |
| `/api/buscar-tercero` | GET | routes.py | 1367 |
| `/api/buscar-tercero` | GET | routes.py | 1367 |
| `/api/cambiar-estado/<int:id>` | POST | routes.py | 2171 |
| `/api/cambiar-estado/<int:id>` | POST | routes.py | 2171 |
| `/api/cargar-factura` | POST | routes.py | 1539 |
| `/api/cargar-factura` | POST | routes.py | 1539 |
| `/api/empresas` | GET | routes.py | 1327 |
| `/api/empresas` | GET | routes.py | 1327 |
| `/api/enviar-firma-masiva` | POST | routes.py | 3059 |
| `/api/enviar-firma-masiva` | POST | routes.py | 3059 |
| `/api/factura/<int:id>` | GET | routes.py | 2464 |
| `/api/factura/<int:id>` | GET | routes.py | 2464 |
| `/api/factura/<int:id>/actualizar` | POST | routes.py | 2525 |
| `/api/factura/<int:id>/actualizar` | POST | routes.py | 2525 |
| `/api/facturas` | GET | routes.py | 1936 |
| `/api/facturas` | GET | routes.py | 1936 |
| `/api/finalizar-lote-rfd` | POST | routes.py | 1810 |
| `/api/finalizar-lote-rfd` | POST | routes.py | 1810 |
| `/api/listar-facturas-paginadas` | GET | routes.py | 923 |
| `/api/listar-facturas-paginadas` | GET | routes.py | 923 |
| `/api/ordenes-compra/buscar-tercero/<nit>` | GET | endpoints_ordenes_compra.py | 102 |
| `/api/ordenes-compra/buscar-tercero/<nit>` | GET | routes.py | 3590 |
| `/api/ordenes-compra/buscar-tercero/<nit>` | GET | routes.py | 3590 |
| `/api/ordenes-compra/centros-costo` | GET | endpoints_ordenes_compra.py | 75 |
| `/api/ordenes-compra/centros-costo` | GET | routes.py | 3498 |
| `/api/ordenes-compra/centros-costo` | GET | routes.py | 3498 |
| `/api/ordenes-compra/centros-operacion` | GET | routes.py | 3525 |
| `/api/ordenes-compra/centros-operacion` | GET | routes.py | 3525 |
| `/api/ordenes-compra/consecutivo` | GET | endpoints_ordenes_compra.py | 21 |
| `/api/ordenes-compra/consecutivo` | GET | routes.py | 3444 |
| `/api/ordenes-compra/consecutivo` | GET | routes.py | 3444 |
| `/api/ordenes-compra/crear` | POST | endpoints_ordenes_compra.py | 130 |
| `/api/ordenes-compra/crear` | POST | routes.py | 3633 |
| `/api/ordenes-compra/crear` | POST | routes.py | 3633 |
| `/api/ordenes-compra/enviar-correo` | POST | endpoints_ordenes_compra.py | 249 |
| `/api/ordenes-compra/enviar-correo` | POST | routes.py | 3752 |
| `/api/ordenes-compra/enviar-correo` | POST | routes.py | 3752 |
| `/api/ordenes-compra/pdf/<int:orden_id>` | GET | endpoints_ordenes_compra.py | 275 |
| `/api/ordenes-compra/pdf/<int:orden_id>` | GET | routes.py | 3778 |
| `/api/ordenes-compra/pdf/<int:orden_id>` | GET | routes.py | 3778 |
| `/api/ordenes-compra/unidades-negocio` | GET | endpoints_ordenes_compra.py | 48 |
| `/api/ordenes-compra/unidades-negocio` | GET | routes.py | 3471 |
| `/api/ordenes-compra/unidades-negocio` | GET | routes.py | 3471 |
| `/api/radicar` | POST | routes.py | 2272 |
| `/api/radicar` | POST | routes.py | 2272 |
| `/api/usuario-actual` | GET | routes.py | 1354 |
| `/api/usuario-actual` | GET | routes.py | 1354 |
| `/api/validar-duplicada` | GET | routes.py | 1475 |
| `/api/validar-duplicada` | GET | routes.py | 1475 |
| `/cargar` | GET | routes.py | 1228 |
| `/cargar` | GET | routes.py | 1228 |
| `/cargar-nueva` | GET | routes.py | 1229 |
| `/cargar-nueva` | GET | routes.py | 1229 |
| `/completar-campos/<int:id>` | GET, POST | routes.py | 1124 |
| `/completar-campos/<int:id>` | GET, POST | routes.py | 1124 |
| `/configuracion` | GET | routes.py | 2212 |
| `/configuracion` | GET | routes.py | 2212 |
| `/dashboard` | GET | routes.py | 660 |
| `/dashboard` | GET | routes.py | 660 |
| `/descargar-factura/<int:id>` | GET | routes.py | 3359 |
| `/descargar-factura/<int:id>` | GET | routes.py | 3359 |
| `/descargar/<int:id>` | GET | routes.py | 2098 |
| `/descargar/<int:id>` | GET | routes.py | 2098 |
| `/detalle/<int:id>` | GET | routes.py | 2077 |
| `/detalle/<int:id>` | GET | routes.py | 2077 |
| `/enviar-firmar/<int:id>` | POST | routes.py | 3317 |
| `/enviar-firmar/<int:id>` | POST | routes.py | 3317 |
| `/listado` | GET | routes.py | 1924 |
| `/listado` | GET | routes.py | 1924 |
| `/listar-archivos/<int:id>` | GET | routes.py | 2773 |
| `/listar-archivos/<int:id>` | GET | routes.py | 2773 |
| `/mis-facturas` | GET | routes.py | 1271 |
| `/mis-facturas` | GET | routes.py | 1271 |
| `/ordenes-compra` | GET | endpoints_ordenes_compra.py | 13 |
| `/ordenes-compra` | GET | routes.py | 3433 |
| `/ordenes-compra` | GET | routes.py | 3433 |
| `/test-simple` | GET | routes.py | 1119 |
| `/test-simple` | GET | routes.py | 1119 |
| `/validar_factura_registrada` | GET | routes.py | 1403 |
| `/validar_factura_registrada` | GET | routes.py | 1403 |
| `/ver-pdf/<int:id>` | GET | routes.py | 2898 |
| `/ver-pdf/<int:id>` | GET | routes.py | 2898 |
| `/ver-pdf/<int:id>/<path:nombre_archivo>` | GET | routes.py | 2899 |
| `/ver-pdf/<int:id>/<path:nombre_archivo>` | GET | routes.py | 2899 |

### GESTION_USUARIOS (37 endpoints | 22 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | routes.py | 239 |
| `/` | GET | routes.py | 239 |
| `/api/auditoria` | GET | routes.py | 982 |
| `/api/auditoria` | GET | routes.py | 982 |
| `/api/catalogo-permisos` | GET | routes.py | 966 |
| `/api/catalogo-permisos` | GET | routes.py | 966 |
| `/api/estadisticas` | GET | routes.py | 1101 |
| `/api/estadisticas` | GET | routes.py | 1101 |
| `/api/invitaciones/<token>/activar` | POST | routes.py | 928 |
| `/api/invitaciones/<token>/activar` | POST | routes.py | 928 |
| `/api/invitaciones/<token>/validar` | GET | routes.py | 906 |
| `/api/invitaciones/<token>/validar` | GET | routes.py | 906 |
| `/api/mis-permisos` | GET | permisos_api.py | 8 |
| `/api/roles` | GET | routes.py | 1040 |
| `/api/roles` | GET | routes.py | 1040 |
| `/api/usuarios` | GET | routes.py | 267 |
| `/api/usuarios` | POST | routes.py | 326 |
| `/api/usuarios` | GET | routes.py | 267 |
| `/api/usuarios` | POST | routes.py | 326 |
| `/api/usuarios/<int:usuario_id>` | GET | routes.py | 421 |
| `/api/usuarios/<int:usuario_id>` | PUT | routes.py | 477 |
| `/api/usuarios/<int:usuario_id>` | GET | routes.py | 421 |
| `/api/usuarios/<int:usuario_id>` | PUT | routes.py | 477 |
| `/api/usuarios/<int:usuario_id>/estado` | PUT | routes.py | 555 |
| `/api/usuarios/<int:usuario_id>/estado` | PUT | routes.py | 555 |
| `/api/usuarios/<int:usuario_id>/invitacion` | POST | routes.py | 851 |
| `/api/usuarios/<int:usuario_id>/invitacion` | POST | routes.py | 851 |
| `/api/usuarios/<int:usuario_id>/permisos` | GET | routes.py | 655 |
| `/api/usuarios/<int:usuario_id>/permisos` | PUT | routes.py | 730 |
| `/api/usuarios/<int:usuario_id>/permisos` | GET | routes.py | 655 |
| `/api/usuarios/<int:usuario_id>/permisos` | PUT | routes.py | 730 |
| `/api/validar-nit/<nit>` | GET | routes.py | 1065 |
| `/api/validar-nit/<nit>` | GET | routes.py | 1065 |
| `/dashboard` | GET | routes.py | 240 |
| `/dashboard` | GET | routes.py | 240 |
| `/estadisticas` | GET | routes.py | 1102 |
| `/estadisticas` | GET | routes.py | 1102 |

### MONITOREO (78 endpoints | 13 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | routes.py | 37 |
| `/` | GET | routes_funcional.py | 40 |
| `/` | GET | routes.py | 37 |
| `/` | GET | routes_funcional.py | 40 |
| `/api/alertas` | GET | routes.py | 455 |
| `/api/alertas` | GET | routes_funcional.py | 308 |
| `/api/alertas` | GET | routes.py | 455 |
| `/api/alertas` | GET | routes_funcional.py | 308 |
| `/api/alertas/crear` | POST | routes.py | 861 |
| `/api/alertas/crear` | POST | routes.py | 861 |
| `/api/alertas_simple` | GET | endpoints_simples.py | 167 |
| `/api/alertas_simple` | GET | endpoints_simples.py | 167 |
| `/api/analytics/tiempo-real` | GET | routes.py | 991 |
| `/api/analytics/tiempo-real` | GET | routes.py | 991 |
| `/api/backup/configuracion` | GET | routes.py | 1452 |
| `/api/backup/configuracion` | GET | routes.py | 1452 |
| `/api/backup/configuracion/<tipo>` | PUT | routes.py | 1479 |
| `/api/backup/configuracion/<tipo>` | PUT | routes.py | 1479 |
| `/api/backup/ejecutar/<tipo>` | POST | routes.py | 1357 |
| `/api/backup/ejecutar/<tipo>` | POST | routes.py | 1357 |
| `/api/backup/estado` | GET | routes.py | 1252 |
| `/api/backup/estado` | GET | routes.py | 1252 |
| `/api/backup/historial` | GET | routes.py | 1401 |
| `/api/backup/historial` | GET | routes.py | 1401 |
| `/api/disk_simple` | GET | endpoints_simples.py | 123 |
| `/api/disk_simple` | GET | endpoints_simples.py | 123 |
| `/api/disk_usage_mejorado` | GET | endpoints_nuevos.py | 194 |
| `/api/disk_usage_mejorado` | GET | routes.py | 336 |
| `/api/disk_usage_mejorado` | GET | routes_funcional.py | 238 |
| `/api/disk_usage_mejorado` | GET | endpoints_nuevos.py | 194 |
| `/api/disk_usage_mejorado` | GET | routes.py | 336 |
| `/api/disk_usage_mejorado` | GET | routes_funcional.py | 238 |
| `/api/geolocalizacion/ips` | GET | routes.py | 902 |
| `/api/geolocalizacion/ips` | GET | routes.py | 902 |
| `/api/ips/gestionar` | POST | routes.py | 617 |
| `/api/ips/gestionar` | POST | routes.py | 617 |
| `/api/ips/listar_completo` | GET | routes.py | 729 |
| `/api/ips/listar_completo` | GET | routes.py | 729 |
| `/api/ips_simple` | GET | endpoints_simples.py | 78 |
| `/api/ips_simple` | GET | endpoints_simples.py | 78 |
| `/api/ips_tiempo_real` | GET | endpoints_nuevos.py | 112 |
| `/api/ips_tiempo_real` | GET | routes.py | 242 |
| `/api/ips_tiempo_real` | GET | routes_funcional.py | 187 |
| `/api/ips_tiempo_real` | GET | endpoints_nuevos.py | 112 |
| `/api/ips_tiempo_real` | GET | routes.py | 242 |
| `/api/ips_tiempo_real` | GET | routes_funcional.py | 187 |
| `/api/logs/archivos` | GET | routes.py | 489 |
| `/api/logs/archivos` | GET | routes_funcional.py | 342 |
| `/api/logs/archivos` | GET | routes.py | 489 |
| `/api/logs/archivos` | GET | routes_funcional.py | 342 |
| `/api/logs_seguridad` | GET | routes.py | 533 |
| `/api/logs_seguridad` | GET | routes.py | 533 |
| `/api/metricas/sistema` | GET | routes.py | 801 |
| `/api/metricas/sistema` | GET | routes.py | 801 |
| `/api/notificaciones/push` | POST | routes.py | 1208 |
| `/api/notificaciones/push` | POST | routes.py | 1208 |
| `/api/seguridad/detectar-amenazas` | GET | routes.py | 1112 |
| `/api/seguridad/detectar-amenazas` | GET | routes.py | 1112 |
| `/api/stats_simple` | GET | endpoints_simples.py | 15 |
| `/api/stats_simple` | GET | endpoints_simples.py | 15 |
| `/api/stats_sorprendentes` | GET | endpoints_nuevos.py | 301 |
| `/api/stats_sorprendentes` | GET | routes.py | 51 |
| `/api/stats_sorprendentes` | GET | routes_funcional.py | 53 |
| `/api/stats_sorprendentes` | GET | endpoints_nuevos.py | 301 |
| `/api/stats_sorprendentes` | GET | routes.py | 51 |
| `/api/stats_sorprendentes` | GET | routes_funcional.py | 53 |
| `/api/usuarios_simple` | GET | endpoints_simples.py | 38 |
| `/api/usuarios_simple` | GET | endpoints_simples.py | 38 |
| `/api/usuarios_tiempo_real` | GET | endpoints_nuevos.py | 11 |
| `/api/usuarios_tiempo_real` | GET | routes.py | 137 |
| `/api/usuarios_tiempo_real` | GET | routes_funcional.py | 138 |
| `/api/usuarios_tiempo_real` | GET | endpoints_nuevos.py | 11 |
| `/api/usuarios_tiempo_real` | GET | routes.py | 137 |
| `/api/usuarios_tiempo_real` | GET | routes_funcional.py | 138 |
| `/dashboard` | GET | routes.py | 38 |
| `/dashboard` | GET | routes_funcional.py | 41 |
| `/dashboard` | GET | routes.py | 38 |
| `/dashboard` | GET | routes_funcional.py | 41 |

### NOTAS_CONTABLES (102 endpoints | 19 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/agregar_adjuntos/<int:documento_id>` | POST | routes.py | 1171 |
| `/agregar_adjuntos/<int:documento_id>` | POST | routes_backup_20251114_162917.py | 1096 |
| `/agregar_adjuntos/<int:documento_id>` | POST | routes.py | 1171 |
| `/agregar_adjuntos/<int:documento_id>` | POST | routes_backup_20251114_162917.py | 1096 |
| `/cargar/subir` | POST | routes.py | 205 |
| `/cargar/subir` | POST | routes_backup_20251114_162917.py | 132 |
| `/cargar/subir` | POST | routes.py | 205 |
| `/cargar/subir` | POST | routes_backup_20251114_162917.py | 132 |
| `/cargar/validar` | POST | routes.py | 89 |
| `/cargar/validar` | POST | routes_backup_20251114_162917.py | 89 |
| `/cargar/validar` | POST | routes.py | 89 |
| `/cargar/validar` | POST | routes_backup_20251114_162917.py | 89 |
| `/cargar_notas` | GET | routes.py | 959 |
| `/cargar_notas` | GET | routes_backup_20251114_162917.py | 884 |
| `/cargar_notas` | GET | routes.py | 959 |
| `/cargar_notas` | GET | routes_backup_20251114_162917.py | 884 |
| `/dashboard/opciones` | GET | routes.py | 587 |
| `/dashboard/opciones` | GET | routes_backup_20251114_162917.py | 513 |
| `/dashboard/opciones` | GET | routes.py | 587 |
| `/dashboard/opciones` | GET | routes_backup_20251114_162917.py | 513 |
| `/datos-documento/<int:documento_id>` | GET | routes.py | 2151 |
| `/datos-documento/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 1844 |
| `/datos-documento/<int:documento_id>` | GET | routes.py | 2151 |
| `/datos-documento/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 1844 |
| `/descargar/<int:documento_id>` | GET | routes.py | 462 |
| `/descargar/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 389 |
| `/descargar/<int:documento_id>` | GET | routes.py | 462 |
| `/descargar/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 389 |
| `/descargar_adjunto/<int:adjunto_id>` | GET | routes.py | 878 |
| `/descargar_adjunto/<int:adjunto_id>` | GET | routes_backup_20251114_162917.py | 804 |
| `/descargar_adjunto/<int:adjunto_id>` | GET | routes.py | 878 |
| `/descargar_adjunto/<int:adjunto_id>` | GET | routes_backup_20251114_162917.py | 804 |
| `/descargar_notas` | POST | routes.py | 1054 |
| `/descargar_notas` | POST | routes_backup_20251114_162917.py | 979 |
| `/descargar_notas` | POST | routes.py | 1054 |
| `/descargar_notas` | POST | routes_backup_20251114_162917.py | 979 |
| `/detalle/<int:documento_id>` | GET | routes.py | 632 |
| `/detalle/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 558 |
| `/detalle/<int:documento_id>` | GET | routes.py | 632 |
| `/detalle/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 558 |
| `/editar/<int:documento_id>` | PUT | routes.py | 694 |
| `/editar/<int:documento_id>` | GET | routes.py | 1036 |
| `/editar/<int:documento_id>` | PUT | routes_backup_20251114_162917.py | 620 |
| `/editar/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 961 |
| `/editar/<int:documento_id>` | PUT | routes.py | 694 |
| `/editar/<int:documento_id>` | GET | routes.py | 1036 |
| `/editar/<int:documento_id>` | PUT | routes_backup_20251114_162917.py | 620 |
| `/editar/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 961 |
| `/eliminar/<int:documento_id>` | DELETE | routes.py | 810 |
| `/eliminar/<int:documento_id>` | DELETE | routes_backup_20251114_162917.py | 736 |
| `/eliminar/<int:documento_id>` | DELETE | routes.py | 810 |
| `/eliminar/<int:documento_id>` | DELETE | routes_backup_20251114_162917.py | 736 |
| `/estadisticas` | GET | routes.py | 532 |
| `/estadisticas` | GET | routes_backup_20251114_162917.py | 458 |
| `/estadisticas` | GET | routes.py | 532 |
| `/estadisticas` | GET | routes_backup_20251114_162917.py | 458 |
| `/exportar_excel_notas` | POST | routes.py | 1080 |
| `/exportar_excel_notas` | POST | routes_backup_20251114_162917.py | 1005 |
| `/exportar_excel_notas` | POST | routes.py | 1080 |
| `/exportar_excel_notas` | POST | routes_backup_20251114_162917.py | 1005 |
| `/historial/<int:documento_id>` | GET | routes.py | 855 |
| `/historial/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 781 |
| `/historial/<int:documento_id>` | GET | routes.py | 855 |
| `/historial/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 781 |
| `/listar` | GET | routes.py | 396 |
| `/listar` | GET | routes_backup_20251114_162917.py | 323 |
| `/listar` | GET | routes.py | 396 |
| `/listar` | GET | routes_backup_20251114_162917.py | 323 |
| `/observacion/<int:documento_id>` | POST | routes.py | 1109 |
| `/observacion/<int:documento_id>` | POST | routes_backup_20251114_162917.py | 1034 |
| `/observacion/<int:documento_id>` | POST | routes.py | 1109 |
| `/observacion/<int:documento_id>` | POST | routes_backup_20251114_162917.py | 1034 |
| `/opciones-correccion` | GET | routes.py | 2205 |
| `/opciones-correccion` | GET | routes_backup_20251114_162917.py | 1898 |
| `/opciones-correccion` | GET | routes.py | 2205 |
| `/opciones-correccion` | GET | routes_backup_20251114_162917.py | 1898 |
| `/solicitar-correccion/<int:documento_id>` | POST | fix_routes.py | 12 |
| `/solicitar-correccion/<int:documento_id>` | GET | fix_routes.py | 165 |
| `/solicitar-correccion/<int:documento_id>` | POST | routes.py | 1285 |
| `/solicitar-correccion/<int:documento_id>` | POST | routes_backup_20251114_162917.py | 1210 |
| `/solicitar-correccion/<int:documento_id>` | POST | route_correccion_simple.py | 12 |
| `/solicitar-correccion/<int:documento_id>` | POST | routes.py | 1285 |
| `/solicitar-correccion/<int:documento_id>` | POST | routes_backup_20251114_162917.py | 1210 |
| `/solicitar-correccion/<int:documento_id>` | POST | route_correccion_simple.py | 12 |
| `/validar-consecutivo-correccion/<int:documento_id>` | POST | routes.py | 131 |
| `/validar-consecutivo-correccion/<int:documento_id>` | POST | routes.py | 131 |
| `/validar-correccion/<int:token_id>` | POST | routes.py | 1681 |
| `/validar-correccion/<int:token_id>` | POST | routes_backup_20251114_162917.py | 1536 |
| `/validar-correccion/<int:token_id>` | POST | routes.py | 1681 |
| `/validar-correccion/<int:token_id>` | POST | routes_backup_20251114_162917.py | 1536 |
| `/visor` | GET | routes.py | 974 |
| `/visor` | GET | routes_backup_20251114_162917.py | 899 |
| `/visor` | GET | routes.py | 974 |
| `/visor` | GET | routes_backup_20251114_162917.py | 899 |
| `/visualizar/<int:documento_id>` | GET | routes.py | 496 |
| `/visualizar/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 423 |
| `/visualizar/<int:documento_id>` | GET | routes.py | 496 |
| `/visualizar/<int:documento_id>` | GET | routes_backup_20251114_162917.py | 423 |
| `/visualizar_adjunto/<int:adjunto_id>` | GET | routes.py | 910 |
| `/visualizar_adjunto/<int:adjunto_id>` | GET | routes_backup_20251114_162917.py | 836 |
| `/visualizar_adjunto/<int:adjunto_id>` | GET | routes.py | 910 |
| `/visualizar_adjunto/<int:adjunto_id>` | GET | routes_backup_20251114_162917.py | 836 |

### RECIBIR_FACTURAS (42 endpoints | 15 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | routes.py | 40 |
| `/` | GET | routes.py | 40 |
| `/<int:factura_id>` | PATCH | endpoints_nuevos.py | 122 |
| `/<int:factura_id>` | DELETE | endpoints_nuevos.py | 212 |
| `/<int:factura_id>` | PATCH | endpoints_nuevos.py | 122 |
| `/<int:factura_id>` | DELETE | endpoints_nuevos.py | 212 |
| `/actualizar_factura_temporal/<int:factura_id>` | PUT | routes.py | 876 |
| `/actualizar_factura_temporal/<int:factura_id>` | PUT | routes.py | 876 |
| `/api/actualizar_temporales` | POST | routes.py | 507 |
| `/api/actualizar_temporales` | POST | routes.py | 507 |
| `/api/agregar_observacion` | POST | routes.py | 582 |
| `/api/agregar_observacion` | POST | routes.py | 582 |
| `/api/exportar_excel` | POST | routes.py | 721 |
| `/api/exportar_excel` | POST | routes.py | 721 |
| `/api/exportar_temporales` | POST | routes.py | 1019 |
| `/api/exportar_temporales` | POST | routes.py | 1019 |
| `/api/limpiar_temporales` | POST | routes.py | 551 |
| `/api/limpiar_temporales` | POST | routes.py | 551 |
| `/api/obtener_kpis` | GET | routes.py | 678 |
| `/api/obtener_kpis` | GET | routes.py | 678 |
| `/api/obtener_observaciones` | GET | routes.py | 637 |
| `/api/obtener_observaciones` | GET | routes.py | 637 |
| `/borrar_factura_temporal/<int:factura_id>` | DELETE | routes.py | 825 |
| `/borrar_factura_temporal/<int:factura_id>` | DELETE | routes.py | 825 |
| `/cargar_facturas_temporales` | GET | routes.py | 309 |
| `/cargar_facturas_temporales` | GET | routes.py | 309 |
| `/centros-operacion` | GET | endpoints_nuevos.py | 11 |
| `/centros-operacion` | GET | endpoints_nuevos.py | 11 |
| `/estadisticas` | GET | endpoints_nuevos.py | 251 |
| `/estadisticas` | GET | endpoints_nuevos.py | 251 |
| `/guardar_factura_temporal` | POST | routes.py | 215 |
| `/guardar_factura_temporal` | POST | routes.py | 215 |
| `/guardar_facturas_masivo` | POST | routes.py | 361 |
| `/guardar_facturas_masivo` | POST | routes.py | 361 |
| `/nueva_factura` | GET | routes.py | 50 |
| `/nueva_factura` | GET | routes.py | 50 |
| `/proveedores` | GET | endpoints_nuevos.py | 59 |
| `/proveedores` | GET | endpoints_nuevos.py | 59 |
| `/validar_factura_registrada` | GET | routes.py | 148 |
| `/validar_factura_registrada` | GET | routes.py | 148 |
| `/verificar_tercero` | GET | routes.py | 85 |
| `/verificar_tercero` | GET | routes.py | 85 |

### RELACIONES (26 endpoints | 14 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | routes.py | 177 |
| `/` | GET | routes.py | 177 |
| `/confirmar_recepcion` | POST | routes.py | 836 |
| `/confirmar_recepcion` | POST | routes.py | 836 |
| `/confirmar_retiro_firma` | POST | routes.py | 1597 |
| `/confirmar_retiro_firma` | POST | routes.py | 1597 |
| `/consultar_recepcion/<numero_relacion>` | GET | routes.py | 1518 |
| `/consultar_recepcion/<numero_relacion>` | GET | routes.py | 1518 |
| `/generar_relacion` | POST | backend_relaciones.py | 70 |
| `/generar_relacion` | GET | backend_relaciones.py | 188 |
| `/generar_relacion` | GET | routes.py | 178 |
| `/generar_relacion` | POST | routes.py | 329 |
| `/generar_relacion` | POST | backend_relaciones.py | 70 |
| `/generar_relacion` | GET | backend_relaciones.py | 188 |
| `/generar_relacion` | GET | routes.py | 178 |
| `/generar_relacion` | POST | routes.py | 329 |
| `/historial_recepciones` | GET | routes.py | 1568 |
| `/historial_recepciones` | GET | routes.py | 1568 |
| `/recepcion_digital` | GET, POST | routes.py | 685 |
| `/recepcion_digital` | GET, POST | routes.py | 685 |
| `/reimprimir_relacion` | GET, POST | routes.py | 519 |
| `/reimprimir_relacion` | GET, POST | routes.py | 519 |
| `/solicitar_token_firma` | POST | routes.py | 980 |
| `/solicitar_token_firma` | POST | routes.py | 980 |
| `/validar_token_y_firmar` | POST | routes.py | 1189 |
| `/validar_token_y_firmar` | POST | routes.py | 1189 |

### TERCEROS (46 endpoints | 16 permisos)

| Ruta | Métodos | Archivo | Línea |
|------|---------|---------|-------|
| `/` | GET | routes.py | 24 |
| `/` | GET | routes_simple.py | 24 |
| `/` | GET | routes.py | 24 |
| `/` | GET | routes_simple.py | 24 |
| `/api/cambiar_estado/<int:tercero_id>` | POST | routes.py | 308 |
| `/api/cambiar_estado/<int:tercero_id>` | POST | routes.py | 308 |
| `/api/crear` | POST | routes.py | 237 |
| `/api/crear` | POST | routes_simple.py | 157 |
| `/api/crear` | POST | routes.py | 237 |
| `/api/crear` | POST | routes_simple.py | 157 |
| `/api/estadisticas` | GET | routes.py | 200 |
| `/api/estadisticas` | GET | routes_simple.py | 120 |
| `/api/estadisticas` | GET | routes.py | 200 |
| `/api/estadisticas` | GET | routes_simple.py | 120 |
| `/api/listar` | GET | routes.py | 47 |
| `/api/listar` | GET | routes_simple.py | 47 |
| `/api/listar` | GET | routes.py | 47 |
| `/api/listar` | GET | routes_simple.py | 47 |
| `/api/obtener/<int:tercero_id>` | GET | routes.py | 357 |
| `/api/obtener/<int:tercero_id>` | GET | routes_simple.py | 228 |
| `/api/obtener/<int:tercero_id>` | GET | routes.py | 357 |
| `/api/obtener/<int:tercero_id>` | GET | routes_simple.py | 228 |
| `/configuracion` | GET | routes.py | 421 |
| `/configuracion` | GET | routes_simple.py | 292 |
| `/configuracion` | GET | routes.py | 421 |
| `/configuracion` | GET | routes_simple.py | 292 |
| `/consulta` | GET | routes.py | 38 |
| `/consulta` | GET | routes_simple.py | 38 |
| `/consulta` | GET | routes.py | 38 |
| `/consulta` | GET | routes_simple.py | 38 |
| `/crear` | GET | routes.py | 228 |
| `/crear` | GET | routes_simple.py | 148 |
| `/crear` | GET | routes.py | 228 |
| `/crear` | GET | routes_simple.py | 148 |
| `/dashboard` | GET | routes.py | 25 |
| `/dashboard` | GET | routes_simple.py | 25 |
| `/dashboard` | GET | routes.py | 25 |
| `/dashboard` | GET | routes_simple.py | 25 |
| `/documentos/<int:tercero_id>` | GET | routes.py | 401 |
| `/documentos/<int:tercero_id>` | GET | routes_simple.py | 272 |
| `/documentos/<int:tercero_id>` | GET | routes.py | 401 |
| `/documentos/<int:tercero_id>` | GET | routes_simple.py | 272 |
| `/editar/<int:tercero_id>` | GET | routes.py | 292 |
| `/editar/<int:tercero_id>` | GET | routes_simple.py | 212 |
| `/editar/<int:tercero_id>` | GET | routes.py | 292 |
| `/editar/<int:tercero_id>` | GET | routes_simple.py | 212 |

---

## ⚠️ ENDPOINTS SIN PERMISO EN CATÁLOGO

Estos endpoints NO tienen un permiso correspondiente en `catalogo_permisos`:

### ARCHIVO_DIGITAL (2 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/editar/<int:documento_id>` | GET | `editar` |
| `/editar/<int:documento_id>` | GET | `editar` |

### CAUSACIONES (6 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/api/eliminar/<sede>/<path:archivo>` | POST | `eliminar` |
| `/api/eliminar/<sede>/<path:archivo>` | POST | `eliminar` |
| `/exportar/excel` | GET | `exportar` |
| `/exportar/excel` | GET | `exportar` |
| `/ver/<sede>/<path:archivo>` | GET | `ver` |
| `/ver/<sede>/<path:archivo>` | GET | `ver` |

### CONFIGURACION (36 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/centros_operacion/crear` | POST | `crear` |
| `/centros_operacion/crear` | POST | `crear` |
| `/centros_operacion/editar/<int:centro_id>` | PUT | `editar` |
| `/centros_operacion/editar/<int:centro_id>` | PUT | `editar` |
| `/centros_operacion/listar` | GET | `listar` |
| `/centros_operacion/listar` | GET | `listar` |
| `/centros_operacion_view` | GET | `ver` |
| `/centros_operacion_view` | GET | `ver` |
| `/departamentos/listar` | GET | `listar` |
| `/departamentos/listar` | GET | `listar` |
| `/departamentos_view` | GET | `ver` |
| `/departamentos_view` | GET | `ver` |
| `/empresas/crear` | POST | `crear` |
| `/empresas/crear` | POST | `crear` |
| `/empresas/editar/<int:empresa_id>` | PUT | `editar` |
| `/empresas/editar/<int:empresa_id>` | PUT | `editar` |
| `/empresas/listar` | GET | `listar` |
| `/empresas/listar` | GET | `listar` |
| `/empresas_view` | GET | `ver` |
| `/empresas_view` | GET | `ver` |
| `/formas_pago/listar` | GET | `listar` |
| `/formas_pago/listar` | GET | `listar` |
| `/formas_pago_view` | GET | `ver` |
| `/formas_pago_view` | GET | `ver` |
| `/tipos_documento/crear` | POST | `crear` |
| `/tipos_documento/crear` | POST | `crear` |
| `/tipos_documento/editar/<int:tipo_id>` | PUT | `editar` |
| `/tipos_documento/editar/<int:tipo_id>` | PUT | `editar` |
| `/tipos_documento/listar` | GET | `listar` |
| `/tipos_documento/listar` | GET | `listar` |
| `/tipos_documento_view` | GET | `ver` |
| `/tipos_documento_view` | GET | `ver` |
| `/tipos_servicio/listar` | GET | `listar` |
| `/tipos_servicio/listar` | GET | `listar` |
| `/tipos_servicio_view` | GET | `ver` |
| `/tipos_servicio_view` | GET | `ver` |

### CORE (142 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/` | GET | `acceder_modulo` |
| `/` | GET | `acceder_modulo` |
| `/` | GET | `acceder_modulo` |
| `/` | GET | `acceder_modulo` |
| `/` | GET | `acceder_modulo` |
| `/admin/usuarios` | GET | `acceder_modulo` |
| `/api/activos/departamento` | GET | `acceder_modulo` |
| `/api/activos/departamento` | GET | `acceder_modulo` |
| `/api/activos/forma-pago` | GET | `acceder_modulo` |
| `/api/activos/forma-pago` | GET | `acceder_modulo` |
| `/api/activos/tipo-documento` | GET | `acceder_modulo` |
| `/api/activos/tipo-documento` | GET | `acceder_modulo` |
| `/api/activos/tipo-servicio` | GET | `acceder_modulo` |
| `/api/activos/tipo-servicio` | GET | `acceder_modulo` |
| `/api/actualizar_campo` | POST | `editar` |
| `/api/actualizar_campo` | POST | `editar` |
| `/api/actualizar_nit` | POST | `editar` |
| `/api/actualizar_nit` | POST | `editar` |
| `/api/admin/activar_usuario` | POST | `acceder_modulo` |
| `/api/admin/agregar_usuario_tercero` | POST | `acceder_modulo` |
| `/api/admin/listar_usuarios` | GET | `listar` |
| `/api/auth/change_password` | POST | `acceder_modulo` |
| `/api/auth/forgot_request` | POST | `acceder_modulo` |
| `/api/auth/forgot_verify` | POST | `ver` |
| `/api/auth/login` | POST | `acceder_modulo` |
| `/api/auth/logout` | POST | `acceder_modulo` |
| `/api/auth/logout` | POST | `acceder_modulo` |
| `/api/auth/logout` | POST | `acceder_modulo` |
| `/api/auth/logout` | POST | `acceder_modulo` |
| `/api/auth/solicitar-recuperacion` | POST | `acceder_modulo` |
| `/api/config/envios` | GET | `acceder_modulo` |
| `/api/config/envios` | GET | `acceder_modulo` |
| `/api/config/smtp` | GET | `acceder_modulo` |
| `/api/config/smtp` | POST | `acceder_modulo` |
| `/api/config/smtp` | GET | `acceder_modulo` |
| `/api/config/smtp` | POST | `acceder_modulo` |
| `/api/config/smtp/probar` | GET | `acceder_modulo` |
| `/api/config/smtp/probar` | GET | `acceder_modulo` |
| `/api/consulta/radicado` | POST | `acceder_modulo` |
| `/api/departamento` | GET | `acceder_modulo` |
| `/api/departamento` | POST | `acceder_modulo` |
| `/api/departamento` | GET | `acceder_modulo` |
| `/api/departamento` | POST | `acceder_modulo` |
| `/api/departamento/<int:id>` | PUT | `acceder_modulo` |
| `/api/departamento/<int:id>` | DELETE | `acceder_modulo` |
| `/api/departamento/<int:id>` | PUT | `acceder_modulo` |
| `/api/departamento/<int:id>` | DELETE | `acceder_modulo` |
| `/api/dian` | GET | `acceder_modulo` |
| `/api/dian` | GET | `acceder_modulo` |
| `/api/dian_usuarios/actualizar` | PUT | `editar` |
| `/api/dian_usuarios/actualizar` | PUT | `editar` |
| `/api/dian_usuarios/agregar` | POST | `acceder_modulo` |
| `/api/dian_usuarios/agregar` | POST | `acceder_modulo` |
| `/api/dian_usuarios/desactivar/<int:user_id>` | POST | `acceder_modulo` |
| `/api/dian_usuarios/desactivar/<int:user_id>` | POST | `acceder_modulo` |
| `/api/dian_usuarios/eliminar/<int:user_id>` | DELETE | `eliminar` |
| `/api/dian_usuarios/eliminar/<int:user_id>` | DELETE | `eliminar` |
| `/api/dian_usuarios/por_nit/<nit>` | GET | `acceder_modulo` |
| `/api/dian_usuarios/por_nit/<nit>` | GET | `acceder_modulo` |
| `/api/dian_usuarios/todos` | GET | `listar` |
| `/api/dian_usuarios/todos` | GET | `listar` |
| `/api/documentos/upload` | POST | `acceder_modulo` |
| `/api/enviar_email_agrupado` | POST | `acceder_modulo` |
| `/api/enviar_email_agrupado` | POST | `acceder_modulo` |
| `/api/enviar_emails` | POST | `acceder_modulo` |
| `/api/enviar_emails` | POST | `acceder_modulo` |
| `/api/factura/<int:factura_id>` | GET | `acceder_modulo` |
| `/api/forma-pago` | GET | `acceder_modulo` |
| `/api/forma-pago` | POST | `acceder_modulo` |
| `/api/forma-pago` | GET | `acceder_modulo` |
| `/api/forma-pago` | POST | `acceder_modulo` |
| `/api/forma-pago/<int:id>` | PUT | `acceder_modulo` |
| `/api/forma-pago/<int:id>` | DELETE | `acceder_modulo` |
| `/api/forma-pago/<int:id>` | PUT | `acceder_modulo` |
| `/api/forma-pago/<int:id>` | DELETE | `acceder_modulo` |
| `/api/forzar_procesar` | GET | `acceder_modulo` |
| `/api/forzar_procesar` | GET | `acceder_modulo` |
| `/api/logs` | GET | `acceder_modulo` |
| `/api/logs` | GET | `acceder_modulo` |
| `/api/logs/recientes` | GET | `acceder_modulo` |
| `/api/logs/recientes` | GET | `acceder_modulo` |
| `/api/monitoreo/heartbeat` | POST | `acceder_modulo` |
| `/api/monitoreo/heartbeat` | POST | `acceder_modulo` |
| `/api/notificaciones/stats` | GET | `acceder_modulo` |
| `/api/registro/check_nit` | POST | `acceder_modulo` |
| `/api/registro/finalizar` | POST | `acceder_modulo` |
| `/api/registro/proveedor` | POST | `acceder_modulo` |
| `/api/registro/usuarios` | POST | `acceder_modulo` |
| `/api/subir_archivos` | POST | `acceder_modulo` |
| `/api/subir_archivos` | POST | `acceder_modulo` |
| `/api/telegram/setup_webhook` | POST | `acceder_modulo` |
| `/api/telegram/webhook` | POST | `acceder_modulo` |
| `/api/tipo-documento` | GET | `acceder_modulo` |
| `/api/tipo-documento` | POST | `acceder_modulo` |
| `/api/tipo-documento` | GET | `acceder_modulo` |
| `/api/tipo-documento` | POST | `acceder_modulo` |
| `/api/tipo-documento/<int:id>` | PUT | `acceder_modulo` |
| `/api/tipo-documento/<int:id>` | DELETE | `acceder_modulo` |
| `/api/tipo-documento/<int:id>` | PUT | `acceder_modulo` |
| `/api/tipo-documento/<int:id>` | DELETE | `acceder_modulo` |
| `/api/tipo-servicio` | GET | `acceder_modulo` |
| `/api/tipo-servicio` | POST | `acceder_modulo` |
| `/api/tipo-servicio` | GET | `acceder_modulo` |
| `/api/tipo-servicio` | POST | `acceder_modulo` |
| `/api/tipo-servicio/<int:id>` | PUT | `acceder_modulo` |
| `/api/tipo-servicio/<int:id>` | DELETE | `acceder_modulo` |
| `/api/tipo-servicio/<int:id>` | PUT | `acceder_modulo` |
| `/api/tipo-servicio/<int:id>` | DELETE | `acceder_modulo` |
| `/api/usuarios` | GET | `acceder_modulo` |
| `/api/usuarios` | GET | `acceder_modulo` |
| `/api/usuarios/<int:usuario_id>` | GET | `acceder_modulo` |
| `/api/usuarios/<int:usuario_id>` | GET | `acceder_modulo` |
| `/api/usuarios/<int:usuario_id>/departamento` | POST | `acceder_modulo` |
| `/api/usuarios/<int:usuario_id>/departamento` | POST | `acceder_modulo` |
| `/api/usuarios/<int:usuario_id>/departamento/<string:departamento>` | DELETE | `acceder_modulo` |
| `/api/usuarios/<int:usuario_id>/departamento/<string:departamento>` | DELETE | `acceder_modulo` |
| `/api/usuarios/por_nit/<nit>` | GET | `acceder_modulo` |
| `/api/usuarios/por_nit/<nit>` | GET | `acceder_modulo` |
| `/cargar` | GET | `acceder_modulo` |
| `/cargar` | GET | `acceder_modulo` |
| `/cargar_archivos` | GET | `acceder_modulo` |
| `/cargar_archivos` | GET | `acceder_modulo` |
| `/config` | GET | `acceder_modulo` |
| `/config` | GET | `acceder_modulo` |
| `/configuracion` | GET | `acceder_modulo` |
| `/configuracion` | GET | `acceder_modulo` |
| `/dashboard` | GET | `acceder_modulo` |
| `/dashboard` | GET | `acceder_modulo` |
| `/descargar_plantilla/<tipo>` | GET | `exportar` |
| `/descargar_plantilla/<tipo>` | GET | `exportar` |
| `/establecer-password/<token>` | GET, POST | `acceder_modulo` |
| `/fix-admin-nit-805028041` | GET | `acceder_modulo` |
| `/license/notice` | GET | `acceder_modulo` |
| `/recibir_facturas` | GET | `acceder_modulo` |
| `/reportes` | GET | `acceder_modulo` |
| `/reportes` | GET | `acceder_modulo` |
| `/subir_archivos` | POST | `acceder_modulo` |
| `/subir_archivos` | POST | `acceder_modulo` |
| `/validaciones` | GET | `acceder_modulo` |
| `/validaciones` | GET | `acceder_modulo` |
| `/visor` | GET | `acceder_modulo` |
| `/visor` | GET | `acceder_modulo` |

### DIAN_VS_ERP (12 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/api/actualizar_campo` | POST | `editar` |
| `/api/actualizar_campo` | POST | `editar` |
| `/api/actualizar_nit` | POST | `editar` |
| `/api/actualizar_nit` | POST | `editar` |
| `/api/usuarios/actualizar/<int:usuario_id>` | PUT | `editar` |
| `/api/usuarios/actualizar/<int:usuario_id>` | PUT | `editar` |
| `/api/usuarios/buscar` | GET | `buscar` |
| `/api/usuarios/buscar` | GET | `buscar` |
| `/api/usuarios/todos` | GET | `listar` |
| `/api/usuarios/todos` | GET | `listar` |
| `/descargar_plantilla/<tipo>` | GET | `exportar` |
| `/descargar_plantilla/<tipo>` | GET | `exportar` |

### FACTURAS_DIGITALES (32 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/api/actualizar-ruta` | POST | `editar` |
| `/api/actualizar-ruta` | POST | `editar` |
| `/api/buscar-tercero` | GET | `buscar` |
| `/api/buscar-tercero` | GET | `buscar` |
| `/api/factura/<int:id>/actualizar` | POST | `editar` |
| `/api/factura/<int:id>/actualizar` | POST | `editar` |
| `/api/listar-facturas-paginadas` | GET | `listar` |
| `/api/listar-facturas-paginadas` | GET | `listar` |
| `/api/ordenes-compra/buscar-tercero/<nit>` | GET | `buscar` |
| `/api/ordenes-compra/buscar-tercero/<nit>` | GET | `buscar` |
| `/api/ordenes-compra/buscar-tercero/<nit>` | GET | `buscar` |
| `/api/ordenes-compra/crear` | POST | `crear` |
| `/api/ordenes-compra/crear` | POST | `crear` |
| `/api/ordenes-compra/crear` | POST | `crear` |
| `/api/validar-duplicada` | GET | `aprobar` |
| `/api/validar-duplicada` | GET | `aprobar` |
| `/descargar-factura/<int:id>` | GET | `exportar` |
| `/descargar-factura/<int:id>` | GET | `exportar` |
| `/descargar/<int:id>` | GET | `exportar` |
| `/descargar/<int:id>` | GET | `exportar` |
| `/detalle/<int:id>` | GET | `ver` |
| `/detalle/<int:id>` | GET | `ver` |
| `/listado` | GET | `listar` |
| `/listado` | GET | `listar` |
| `/listar-archivos/<int:id>` | GET | `listar` |
| `/listar-archivos/<int:id>` | GET | `listar` |
| `/validar_factura_registrada` | GET | `aprobar` |
| `/validar_factura_registrada` | GET | `aprobar` |
| `/ver-pdf/<int:id>` | GET | `ver` |
| `/ver-pdf/<int:id>` | GET | `ver` |
| `/ver-pdf/<int:id>/<path:nombre_archivo>` | GET | `ver` |
| `/ver-pdf/<int:id>/<path:nombre_archivo>` | GET | `ver` |

### GESTION_USUARIOS (4 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/api/invitaciones/<token>/validar` | GET | `aprobar` |
| `/api/invitaciones/<token>/validar` | GET | `aprobar` |
| `/api/validar-nit/<nit>` | GET | `aprobar` |
| `/api/validar-nit/<nit>` | GET | `aprobar` |

### MONITOREO (4 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/api/alertas/crear` | POST | `crear` |
| `/api/alertas/crear` | POST | `crear` |
| `/api/ips/listar_completo` | GET | `listar` |
| `/api/ips/listar_completo` | GET | `listar` |

### NOTAS_CONTABLES (54 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/cargar/validar` | POST | `aprobar` |
| `/cargar/validar` | POST | `aprobar` |
| `/cargar/validar` | POST | `aprobar` |
| `/cargar/validar` | POST | `aprobar` |
| `/descargar/<int:documento_id>` | GET | `exportar` |
| `/descargar/<int:documento_id>` | GET | `exportar` |
| `/descargar/<int:documento_id>` | GET | `exportar` |
| `/descargar/<int:documento_id>` | GET | `exportar` |
| `/descargar_adjunto/<int:adjunto_id>` | GET | `exportar` |
| `/descargar_adjunto/<int:adjunto_id>` | GET | `exportar` |
| `/descargar_adjunto/<int:adjunto_id>` | GET | `exportar` |
| `/descargar_adjunto/<int:adjunto_id>` | GET | `exportar` |
| `/descargar_notas` | POST | `exportar` |
| `/descargar_notas` | POST | `exportar` |
| `/descargar_notas` | POST | `exportar` |
| `/descargar_notas` | POST | `exportar` |
| `/detalle/<int:documento_id>` | GET | `ver` |
| `/detalle/<int:documento_id>` | GET | `ver` |
| `/detalle/<int:documento_id>` | GET | `ver` |
| `/detalle/<int:documento_id>` | GET | `ver` |
| `/editar/<int:documento_id>` | PUT | `editar` |
| `/editar/<int:documento_id>` | GET | `editar` |
| `/editar/<int:documento_id>` | PUT | `editar` |
| `/editar/<int:documento_id>` | GET | `editar` |
| `/editar/<int:documento_id>` | PUT | `editar` |
| `/editar/<int:documento_id>` | GET | `editar` |
| `/editar/<int:documento_id>` | PUT | `editar` |
| `/editar/<int:documento_id>` | GET | `editar` |
| `/eliminar/<int:documento_id>` | DELETE | `eliminar` |
| `/eliminar/<int:documento_id>` | DELETE | `eliminar` |
| `/eliminar/<int:documento_id>` | DELETE | `eliminar` |
| `/eliminar/<int:documento_id>` | DELETE | `eliminar` |
| `/exportar_excel_notas` | POST | `exportar` |
| `/exportar_excel_notas` | POST | `exportar` |
| `/exportar_excel_notas` | POST | `exportar` |
| `/exportar_excel_notas` | POST | `exportar` |
| `/listar` | GET | `listar` |
| `/listar` | GET | `listar` |
| `/listar` | GET | `listar` |
| `/listar` | GET | `listar` |
| `/validar-consecutivo-correccion/<int:documento_id>` | POST | `aprobar` |
| `/validar-consecutivo-correccion/<int:documento_id>` | POST | `aprobar` |
| `/validar-correccion/<int:token_id>` | POST | `aprobar` |
| `/validar-correccion/<int:token_id>` | POST | `aprobar` |
| `/validar-correccion/<int:token_id>` | POST | `aprobar` |
| `/validar-correccion/<int:token_id>` | POST | `aprobar` |
| `/visualizar/<int:documento_id>` | GET | `ver` |
| `/visualizar/<int:documento_id>` | GET | `ver` |
| `/visualizar/<int:documento_id>` | GET | `ver` |
| `/visualizar/<int:documento_id>` | GET | `ver` |
| `/visualizar_adjunto/<int:adjunto_id>` | GET | `ver` |
| `/visualizar_adjunto/<int:adjunto_id>` | GET | `ver` |
| `/visualizar_adjunto/<int:adjunto_id>` | GET | `ver` |
| `/visualizar_adjunto/<int:adjunto_id>` | GET | `ver` |

### RECIBIR_FACTURAS (14 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/actualizar_factura_temporal/<int:factura_id>` | PUT | `editar` |
| `/actualizar_factura_temporal/<int:factura_id>` | PUT | `editar` |
| `/api/actualizar_temporales` | POST | `editar` |
| `/api/actualizar_temporales` | POST | `editar` |
| `/api/exportar_excel` | POST | `exportar` |
| `/api/exportar_excel` | POST | `exportar` |
| `/api/exportar_temporales` | POST | `exportar` |
| `/api/exportar_temporales` | POST | `exportar` |
| `/borrar_factura_temporal/<int:factura_id>` | DELETE | `eliminar` |
| `/borrar_factura_temporal/<int:factura_id>` | DELETE | `eliminar` |
| `/validar_factura_registrada` | GET | `aprobar` |
| `/validar_factura_registrada` | GET | `aprobar` |
| `/verificar_tercero` | GET | `ver` |
| `/verificar_tercero` | GET | `ver` |

### RELACIONES (4 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/consultar_recepcion/<numero_relacion>` | GET | `buscar` |
| `/consultar_recepcion/<numero_relacion>` | GET | `buscar` |
| `/validar_token_y_firmar` | POST | `aprobar` |
| `/validar_token_y_firmar` | POST | `aprobar` |

### TERCEROS (16 faltantes)

| Endpoint | Métodos | Acción Sugerida |
|----------|---------|------------------|
| `/api/crear` | POST | `crear` |
| `/api/crear` | POST | `crear` |
| `/api/crear` | POST | `crear` |
| `/api/crear` | POST | `crear` |
| `/api/listar` | GET | `listar` |
| `/api/listar` | GET | `listar` |
| `/api/listar` | GET | `listar` |
| `/api/listar` | GET | `listar` |
| `/crear` | GET | `crear` |
| `/crear` | GET | `crear` |
| `/crear` | GET | `crear` |
| `/crear` | GET | `crear` |
| `/editar/<int:tercero_id>` | GET | `editar` |
| `/editar/<int:tercero_id>` | GET | `editar` |
| `/editar/<int:tercero_id>` | GET | `editar` |
| `/editar/<int:tercero_id>` | GET | `editar` |

---

## 🎨 FUNCIONALIDADES FRONTEND

### AJAX (217 encontrados)

| Archivo | Ruta/Función | Descripción |
|---------|--------------|-------------|
| cargar_documentos_contables.html | `/api/notas/dashboard/opciones` | - |
| cargar_documentos_contables.html | `/api/notas/cargar/validar` | - |
| cargar_documentos_contables.html | `/api/notas/cargar/subir` | - |
| cargar_documentos_contables.html | `/api/auth/logout` | - |
| causacion.html | `/api/auth/logout` | - |
| causacion_BACKUP.html | `/visualizar_archivo` | - |
| causacion_BACKUP.html | `/liberar_manual` | - |
| causacion_BACKUP.html | `/liberar_manual` | - |
| causacion_BACKUP.html | `/mover_a_papelera` | - |
| causacion_BACKUP.html | `/causaciones/api/documentos` | - |
| causacion_BACKUP.html | `/api/auth/logout` | - |
| causacion_mejorado.html | `/api/auth/logout` | - |
| centros_operacion.html | `/api/configuracion/empresas/listar` | - |
| centros_operacion.html | `/api/auth/logout` | - |
| correo_recepcion_firmada_relacion.html | `/api/auth/logout` | - |
| dashboard.html | `http://localhost:8097/` | - |
| dashboard.html | `/api/auth/logout` | - |
| dashboard_principal.html | `/api/descargar_nuevas` | - |
| dashboard_principal.html | `/api/estadisticas` | - |
| dashboard_principal.html | `/api/auth/logout` | - |
| departamentos.html | `/api/configuracion/departamentos/listar` | - |
| departamentos.html | `/api/auth/logout` | - |
| detalle_factura.html | `/api/auth/logout` | - |
| editar_nota.html | `/api/auth/logout` | - |
| editar_nota.html | `/api/auth/logout` | - |
| editar_nota_v2.html | `/api/auth/logout` | - |
| editar_nota_v3.html | `/api/notas/opciones-correccion` | - |
| editar_nota_v3.html | `/api/auth/logout` | - |
| empresas.html | `/api/auth/logout` | - |
| establecer_password.html | `/api/auth/logout` | - |
| explorador_archivos.html | `/api/actualizar_exploracion` | - |
| explorador_archivos.html | `/api/auth/logout` | - |
| formas_pago.html | `/api/configuracion/formas_pago/listar` | - |
| formas_pago.html | `/api/auth/logout` | - |
| frontend_recibir_facturas.html | `/api/auth/logout` | - |
| generar_relacion.html | `/api/auth/logout` | - |
| generar_relacion.html | `/api/auth/logout` | - |
| generar_relacion_REFACTORED.html | `/api/auth/logout` | - |
| login.html | `/api/auth/login` | - |
| login.html | `/api/registro/check_nit` | - |
| login.html | `/api/registro/proveedor` | - |
| login.html | `/api/consulta/radicado` | - |
| login.html | `/api/auth/forgot_request` | - |
| login.html | `/api/auth/forgot_verify` | - |
| login.html | `/api/auth/change_password` | - |
| login.html | `/api/registro/finalizar` | - |
| login.html | `/api/documentos/upload` | - |
| login.html | `/api/registro` | - |
| monitor.html | `/admin/monitoreo/api/stats` | - |
| monitor.html | `/admin/monitoreo/api/disk_usage` | - |

*(Mostrando 50 de 217 - ver archivo completo para detalles)*

### AJAX_JQUERY (2 encontrados)

| Archivo | Ruta/Función | Descripción |
|---------|--------------|-------------|
| empresas.html | `/api/configuracion/empresas/listar` | - |
| empresas.html | `/api/configuracion/empresas/listar` | - |

### BOTON (486 encontrados)

| Archivo | Ruta/Función | Descripción |
|---------|--------------|-------------|
| cargar_documentos_contables.html | `toggleTheme()` | - |
| cargar_documentos_contables.html | `cerrarSesion()` | - |
| cargar_documentos_contables.html | `limpiarFormulario()` | - |
| cargar_documentos_contables.html | `guardarDocumento(event)` | - |
| cargar_documentos_contables.html | `eliminarAdjunto(` | - |
| cargar_documentos_contables.html | `eliminarAdjunto(` | - |
| causacion_BACKUP.html | `toggleTheme()` | - |
| causacion_BACKUP.html | `window.location.href=` | - |
| causacion_BACKUP.html | `verPDF(` | - |
| causacion_BACKUP.html | `renombrarArchivo(` | - |
| causacion_BACKUP.html | `borrarArchivo(` | - |
| causacion_BACKUP.html | `hideInvoicePanel()` | - |
| causacion_mejorado.html | `togglePanelIzquierdo()` | - |
| causacion_mejorado.html | `toggleTheme()` | - |
| causacion_mejorado.html | `seleccionarTodas()` | - |
| causacion_mejorado.html | `seleccionarAprobadas()` | - |
| causacion_mejorado.html | `seleccionarCausadas()` | - |
| causacion_mejorado.html | `exportarExcel()` | - |
| causacion_mejorado.html | `togglePanelIzquierdo()` | - |
| causacion_mejorado.html | `irRenombrar()` | - |
| causacion_mejorado.html | `togglePanelDerecho()` | - |
| causacion_mejorado.html | `eliminarDocumento()` | - |
| causacion_mejorado.html | `togglePanelDerecho()` | - |
| centros_operacion.html | `toggleDarkMode()` | - |
| centros_operacion.html | `window.location.href=` | - |
| centros_operacion.html | `abrirModalCrear()` | - |
| centros_operacion.html | `cerrarModal()` | - |
| centros_operacion.html | `cerrarModal()` | - |
| centros_operacion.html | `abrirModalEditar(${centro.id})` | - |
| centros_operacion.html | `toggleEstado(${centro.id}, ` | - |
| dashboard.html | `cerrarSesion()` | - |
| dashboard.html | `volverInicio()` | - |
| dashboard_principal.html | `realizarBusqueda()` | - |
| dashboard_principal.html | `descargarNuevas()` | - |
| dashboard_principal.html | `actualizarEstadisticas()` | - |
| dashboard_principal.html | `mostrarConfiguracion()` | - |
| departamentos.html | `toggleDarkMode()` | - |
| departamentos.html | `window.location.href=` | - |
| detalle_factura.html | `window.history.back()` | - |
| detalle_factura.html | `intentarDescargarArchivos()` | - |
| editar_nota.html | `toggleTheme()` | - |
| editar_nota.html | `cerrarSesion()` | - |
| editar_nota.html | `window.location.href=` | - |
| editar_nota.html | `eliminarDocumento()` | - |
| editar_nota.html | `rechazarDocumento()` | - |
| editar_nota_v2.html | `guardarCambios()` | - |
| editar_nota_v2.html | `volverAlListado()` | - |
| editar_nota_v2.html | `subirAnexos()` | - |
| editar_nota_v2.html | `navegarPDF(-1)` | - |
| editar_nota_v2.html | `navegarPDF(1)` | - |

*(Mostrando 50 de 486 - ver archivo completo para detalles)*

### FORM (6 encontrados)

| Archivo | Ruta/Función | Descripción |
|---------|--------------|-------------|
| causacion_mejorado.html | `{{ url_for(` | - |
| generar_relacion.html | `/generar_relacion` | - |
| generar_relacion_REFACTORED.html | `/relaciones/generar_relacion` | - |
| recepcion_digital.html | `{{ url_for(` | - |
| recepcion_digital_MEJORADO.html | `{{ url_for(` | - |
| reimprimir_relacion.html | `{{ url_for(` | - |

### MENU_ITEM (90 encontrados)

| Archivo | Ruta/Función | Descripción |
|---------|--------------|-------------|
| cargar_documentos_contables.html | `/dashboard` | 🔙 Dashboard |
| causacion.html | `{{ url_for(` | Salir |
| causacion.html | `?pagina=1&por_pagina={{ por_pagina }}&ca` | « |
| causacion.html | `?pagina={{ pagina - 1 }}&por_pagina={{ p` | ‹ |
| causacion.html | `?pagina={{ pagina + 1 }}&por_pagina={{ p` | = total_paginas %}text-text-secondary pointer-even |
| causacion.html | `?pagina={{ total_paginas }}&por_pagina={` | = total_paginas %}text-text-secondary pointer-even |
| causacion_BACKUP.html | `/exportar-excel?{% for s in sede %}sede=` | 📥 Exportar Excel |
| causacion_BACKUP.html | `{{ url_for(` | Salir |
| causacion_BACKUP.html | `?pagina=1&por_pagina={{ por_pagina }}&ca` | « |
| causacion_BACKUP.html | `?pagina={{ pagina - 1 }}&por_pagina={{ p` | ‹ |
| causacion_BACKUP.html | `?pagina={{ pagina + 1 }}&por_pagina={{ p` | = total_paginas %}text-text-secondary pointer-even |
| causacion_BACKUP.html | `?pagina={{ total_paginas }}&por_pagina={` | = total_paginas %}text-text-secondary pointer-even |
| causacion_mejorado.html | `?pagina={{ pagina - 1 }}&sede={{ sede | ` | ← Ant |
| causacion_mejorado.html | `?pagina={{ pagina + 1 }}&sede={{ sede | ` | Siguiente → |
| dashboard_principal.html | `/explorar` | 📁 Explorar Archivos |
| dashboard_principal.html | `/dian_vs_erp/` | 📊 DIAN vs ERP |
| dashboard_principal.html | `/buscar?tipo=todo` | Ver Todas |
| dashboard_principal.html | `/factura/{{ factura.clave_busqueda }}` | Ver |
| dashboard_principal.html | `/tercero/{{ factura.nit_tercero }}` | Tercero |
| detalle_factura.html | `/descargar_pdf/{{ factura.clave_busqueda` | 📄 Descargar PDF |
| detalle_factura.html | `/descargar_xml/{{ factura.clave_busqueda` | 📄 Descargar XML |
| detalle_factura.html | `/ver_carpeta/{{ factura.clave_busqueda }` | 📁 Ver Carpeta Completa |
| detalle_factura.html | `/tercero/{{ factura.nit_tercero }}` | Ver Todas las Facturas del Tercero |
| detalle_factura.html | `/` | Volver al Dashboard |
| editar_nota.html | `/archivo_digital/visor` | 🔙 Volver al Visor |
| empresas.html | `/dashboard` | 🏠 Volver al Menú |
| error.html | `/` | 🏠 Ir al Dashboard |
| establecer_password.html | `/` | ← Volver al inicio de sesión |
| explorador_archivos.html | `/` | 🏠 Dashboard |
| explorador_archivos.html | `/explorar{{ item.url }}` | {{ item.nombre }} |
| explorador_archivos.html | `/descargar_archivo{{ archivo.ruta_comple` | ⬇️ Descargar |
| explorador_archivos.html | `/ver_pdf{{ archivo.ruta_completa }}` | 👁️ Ver |
| generar_relacion.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | « Primera |
| generar_relacion.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | ‹ Anterior |
| generar_relacion.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | {{ p }} |
| generar_relacion.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | Siguiente › |
| generar_relacion.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | Última » |
| generar_relacion_REFACTORED.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | « Primera |
| generar_relacion_REFACTORED.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | ‹ Anterior |
| generar_relacion_REFACTORED.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | {{ p }} |
| generar_relacion_REFACTORED.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | Siguiente › |
| generar_relacion_REFACTORED.html | `?desde={{ desde }}&hasta={{ hasta }}&co=` | Última » |
| login.html | `#` | Términos y Condiciones |
| login.html | `/ruta/a/documentos.zip` | Descargue Documentos Aquí |
| recepcion_digital.html | `{{ url_for(` | ⬅️ Volver |
| recepcion_digital.html | `{{ url_for(` | ⬅️ Buscar Otra Relación |
| recepcion_digital.html | `{{ url_for(` | 🏠 Volver al Menú Principal |
| recepcion_digital_MEJORADO.html | `{{ url_for(` | ⬅️ Buscar Otra Relación |
| recepcion_digital_MEJORADO.html | `{{ url_for(` | 🏠 Volver al Menú Principal |
| renombrar.html | `{{ url_for(` | ⏪ Volver al Listado |

*(Mostrando 50 de 90 - ver archivo completo para detalles)*

---

## 📋 PERMISOS EN CATÁLOGO (171 totales)

### ADMIN (9 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 52 | `acceder_modulo` | Permiso para acceder modulo | accion | ❌ |
| 53 | `configuracion_avanzada` | Permiso para configuracion avanzada | accion | ❌ |
| 100 | `gestionar_permisos` | Asignar y modificar permisos de usuarios | accion | ✅ |
| 54 | `gestionar_sistema` | Permiso para gestionar sistema | accion | ❌ |
| 99 | `gestionar_usuarios` | Crear, editar y eliminar usuarios del sistema | accion | ✅ |
| 102 | `monitoreo_sistema` | Panel de monitoreo en tiempo real | vista | ❌ |
| 101 | `ver_auditoria` | Acceso a logs de auditoría y cambios | vista | ❌ |
| 98 | `ver_dashboard` | Acceso al panel de administración principal | vista | ✅ |
| 55 | `ver_logs` | Permiso para ver logs | accion | ❌ |

### ARCHIVO_DIGITAL (6 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 32 | `acceder_modulo` | Acceso general al archivo digital | acceso | ❌ |
| 33 | `buscar_documento` | Localizar documentos en el archivo | busqueda | ❌ |
| 34 | `descargar_documento` | Descargar documentos del archivo | descarga | ❌ |
| 35 | `eliminar_documento` | Borrar documentos del archivo | eliminacion | ✅ |
| 36 | `subir_documento` | Cargar nuevos documentos al archivo | carga | ❌ |
| 37 | `ver_documento` | Visualizar documentos almacenados | vista | ❌ |

### CAUSACIONES (16 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 29 | `acceder_modulo` | Acceso general a causaciones | acceso | ❌ |
| 56 | `agregar_observacion` | Permiso para agregar observacion | accion | ❌ |
| 30 | `consultar_causaciones` | Ver causaciones existentes | consulta | ❌ |
| 57 | `consultar_documentos` | Permiso para consultar documentos | accion | ❌ |
| 58 | `editar_causacion` | Permiso para editar causacion | accion | ❌ |
| 59 | `eliminar_archivo` | Permiso para eliminar archivo | accion | ❌ |
| 60 | `eliminar_causacion` | Permiso para eliminar causacion | accion | ❌ |
| 115 | `escanear_carpetas` | Escanear carpetas de red en busca de documentos | consulta | ❌ |
| 113 | `exportar_excel` | Exportar listado de archivos a Excel | exportacion | ❌ |
| 61 | `extraer_datos` | Permiso para extraer datos | accion | ❌ |
| 114 | `filtrar_archivos` | Buscar y filtrar archivos por criterios | filtro | ❌ |
| 31 | `nueva_causacion` | Crear nueva causación contable | formulario | ❌ |
| 62 | `renombrar_archivo` | Cambiar nombre de archivos de causaciones | edicion | ✅ |
| 63 | `ver_observaciones` | Permiso para ver observaciones | accion | ❌ |
| 112 | `ver_pdf` | Visualizar archivos PDF de causaciones | vista | ❌ |
| 64 | `visualizar_pdf` | Permiso para visualizar pdf | accion | ❌ |

### CONFIGURACION (5 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 38 | `acceder_modulo` | Acceso general a configuración | acceso | ❌ |
| 39 | `centros_operacion` | Gestionar centros operativos (tiendas/bodegas) | gestion | ❌ |
| 65 | `editar_configuracion` | Permiso para editar configuracion | accion | ❌ |
| 40 | `parametros_sistema` | Configuración general del sistema | configuracion | ✅ |
| 41 | `tipos_documento` | Configurar tipos de documentos | gestion | ❌ |

### DIAN_VS_ERP (13 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 143 | `acceder_modulo` | Acceso general al módulo DIAN vs ERP | acceso | ❌ |
| 153 | `asignar_usuario_factura` | Asignar responsable a factura | edicion | ✅ |
| 154 | `cambiar_estado_factura` | Actualizar estado de validación | edicion | ✅ |
| 148 | `cargar_acuses` | Subir archivo de acuses recibos | carga | ❌ |
| 145 | `cargar_archivo_dian` | Subir archivo de facturas DIAN | carga | ❌ |
| 147 | `cargar_archivo_erp_cm` | Subir archivo ERP Coomultrasán | carga | ❌ |
| 146 | `cargar_archivo_erp_fn` | Subir archivo ERP Fenalco | carga | ❌ |
| 155 | `configurar_smtp` | Administrar configuración de correo | configuracion | ✅ |
| 152 | `enviar_correo` | Enviar reporte por correo electrónico | accion | ❌ |
| 151 | `exportar_reporte` | Descargar reporte de validación | exportacion | ❌ |
| 149 | `procesar_archivos` | Ejecutar validación y comparación | accion | ❌ |
| 144 | `ver_dashboard` | Acceder al visor de validación | vista | ❌ |
| 150 | `ver_diferencias` | Ver discrepancias detectadas | consulta | ❌ |

### FACTURAS_DIGITALES (15 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 116 | `acceder_modulo` | Acceso general a facturas digitales | acceso | ❌ |
| 128 | `agregar_observacion` | Añadir comentarios al historial de factura | edicion | ❌ |
| 124 | `cambiar_estado` | Actualizar estado de factura (pendiente, enviada,  | edicion | ✅ |
| 118 | `cargar_factura` | Subir nueva factura digital con anexos | carga | ❌ |
| 126 | `cargar_firmado` | Subir documento firmado digitalmente | carga | ✅ |
| 130 | `configurar_rutas` | Administrar rutas de almacenamiento de facturas | configuracion | ✅ |
| 121 | `consultar_facturas` | Listar y buscar facturas digitales | consulta | ❌ |
| 127 | `descargar_soportes` | Descargar ZIP con todos los anexos | descarga | ❌ |
| 123 | `editar_factura` | Modificar datos de factura digital | edicion | ✅ |
| 125 | `enviar_a_firmar` | Enviar factura para firma digital con Adobe Sign | accion | ✅ |
| 129 | `exportar_reporte` | Exportar listado de facturas a Excel | exportacion | ❌ |
| 119 | `validar_tercero` | Verificar NIT de tercero en el sistema | validacion | ❌ |
| 117 | `ver_dashboard` | Acceder al dashboard de facturas digitales | vista | ❌ |
| 122 | `ver_detalle_factura` | Ver información completa de factura | vista | ❌ |
| 120 | `verificar_duplicados` | Validar que factura no esté duplicada | validacion | ❌ |

### GESTION_USUARIOS (22 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 66 | `acceder_modulo` | Acceso general a gestión de usuarios | acceso | ❌ |
| 67 | `activar_usuario` | Cambiar estado activo de usuarios | edicion | ✅ |
| 1 | `asignar_permisos` | Otorgar o revocar permisos a usuarios | gestion | ✅ |
| 140 | `asignar_roles` | Asignar roles predefinidos a usuarios | gestion | ✅ |
| 68 | `consultar_auditoria` | Ver logs de cambios en usuarios y permisos | consulta | ❌ |
| 69 | `consultar_permisos` | Ver permisos asignados a usuarios | consulta | ❌ |
| 70 | `consultar_roles` | Listar roles disponibles en el sistema | consulta | ❌ |
| 71 | `consultar_usuarios` | Listar y buscar usuarios del sistema | consulta | ❌ |
| 2 | `crear_usuario` | Dar de alta nuevos usuarios en el sistema | creacion | ✅ |
| 72 | `desactivar_usuario` | Permiso para desactivar usuario | accion | ❌ |
| 73 | `editar_usuario` | Modificar datos de usuarios existentes | edicion | ✅ |
| 74 | `eliminar_usuario` | Borrar usuarios del sistema (acción irreversible) | eliminacion | ✅ |
| 75 | `enviar_invitacion` | Enviar correo de invitación para configurar contra | accion | ❌ |
| 76 | `gestionar_roles` | Permiso para gestionar roles | accion | ❌ |
| 77 | `invitar_usuarios` | Permiso para invitar usuarios | accion | ❌ |
| 3 | `monitoreo_sistema` | Panel de monitoreo en tiempo real | vista | ❌ |
| 141 | `resetear_password` | Forzar cambio de contraseña de usuario | accion | ✅ |
| 4 | `ver_auditoria` | Acceso a logs de auditoría y cambios | vista | ❌ |
| 138 | `ver_dashboard` | Acceder al dashboard de gestión de usuarios | vista | ❌ |
| 5 | `ver_dashboard_admin` | Acceso al panel de administración principal | vista | ✅ |
| 142 | `ver_estadisticas` | Dashboard de estadísticas de usuarios | vista | ❌ |
| 139 | `ver_usuario` | Ver información completa de un usuario | vista | ❌ |

### MONITOREO (13 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 46 | `acceder_modulo` | Acceso general al panel de monitoreo | acceso | ❌ |
| 134 | `cerrar_sesion_remota` | Forzar cierre de sesión de otro usuario | accion | ✅ |
| 47 | `consultar_alertas` | Ver alertas del sistema | consulta | ❌ |
| 48 | `consultar_estadisticas` | Ver estadísticas generales del sistema | consulta | ❌ |
| 49 | `consultar_logs` | Ver logs del sistema | consulta | ❌ |
| 137 | `gestionar_ips` | Administrar listas blanca/negra de IPs | gestion | ✅ |
| 50 | `monitorear_ips` | Monitorear direcciones IP | monitoreo | ❌ |
| 51 | `monitorear_usuarios` | Monitorear actividad de usuarios | monitoreo | ❌ |
| 136 | `ver_alertas_seguridad` | Monitorear intentos de acceso sospechosos | consulta | ✅ |
| 131 | `ver_dashboard` | Acceder al dashboard de monitoreo | vista | ❌ |
| 135 | `ver_logs_errores` | Acceder a logs de errores del sistema | consulta | ❌ |
| 133 | `ver_sesiones_activas` | Lista de usuarios conectados en tiempo real | consulta | ❌ |
| 132 | `ver_uso_recursos` | Monitorear CPU, RAM y disco del servidor | vista | ❌ |

### NOTAS_CONTABLES (19 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 78 | `acceder_modulo` | Acceso general al archivo digital | acceso | ❌ |
| 79 | `agregar_observacion` | Permiso para agregar observacion | accion | ❌ |
| 111 | `aprobar_correccion_critica` | Autorizar correcciones de documentos que requieren | correccion | ✅ |
| 105 | `buscar_documento` | Localizar documentos en el archivo | busqueda | ❌ |
| 80 | `cargar_documento` | Permiso para cargar documento | accion | ❌ |
| 81 | `consultar_notas` | Permiso para consultar notas | accion | ❌ |
| 82 | `crear_nota` | Permiso para crear nota | accion | ❌ |
| 107 | `descargar_documento` | Descargar documentos del archivo | descarga | ❌ |
| 83 | `descargar_nota` | Permiso para descargar nota | accion | ❌ |
| 84 | `editar_nota` | Permiso para editar nota | accion | ❌ |
| 108 | `eliminar_documento` | Borrar documentos del archivo | eliminacion | ✅ |
| 85 | `eliminar_nota` | Permiso para eliminar nota | accion | ❌ |
| 86 | `exportar_excel` | Permiso para exportar excel | accion | ❌ |
| 87 | `exportar_notas` | Permiso para exportar notas | accion | ❌ |
| 109 | `solicitar_correccion_documento` | Iniciar proceso de corrección de campos críticos ( | correccion | ✅ |
| 104 | `subir_documento` | Cargar nuevos documentos al archivo | carga | ❌ |
| 110 | `validar_correccion_documento` | Ingresar código de validación enviado por correo p | correccion | ✅ |
| 106 | `ver_documento` | Visualizar documentos almacenados | vista | ❌ |
| 88 | `visualizar_nota` | Permiso para visualizar nota | accion | ❌ |

### RECIBIR_FACTURAS (15 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 6 | `acceder_modulo` | Acceso general al módulo de recibir facturas | acceso | ❌ |
| 7 | `adicionar_factura` | Agregar facturas temporales al sistema | accion | ❌ |
| 8 | `cargar_facturas` | Ver lista de facturas temporales cargadas | vista | ❌ |
| 89 | `cargar_facturas_temporales` | Permiso para cargar facturas temporales | accion | ❌ |
| 90 | `consultar_facturas` | Permiso para consultar facturas | accion | ❌ |
| 9 | `editar_factura` | Modificar facturas temporales | edicion | ❌ |
| 10 | `eliminar_factura` | Borrar facturas temporales | eliminacion | ✅ |
| 11 | `exportar_excel` | Descargar facturas temporales en Excel | exportacion | ❌ |
| 91 | `exportar_facturas` | Permiso para exportar facturas | accion | ❌ |
| 103 | `exportar_temporales` | Descargar facturas temporales en Excel | exportacion | ❌ |
| 12 | `guardar_facturas` | Confirmar y persistir facturas en BD | confirmacion | ✅ |
| 13 | `limpiar_todo` | Borrar todas las facturas temporales | eliminacion | ✅ |
| 14 | `nueva_factura` | Registrar nueva factura en el sistema | formulario | ❌ |
| 15 | `validar_factura` | Verificar claves y duplicados de facturas | validacion | ❌ |
| 16 | `verificar_tercero` | Validar información de terceros (NITs) | consulta | ❌ |

### RELACIONES (14 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 17 | `acceder_modulo` | Acceso general al módulo de relaciones | acceso | ❌ |
| 18 | `buscar_relacion` | Localizar relaciones por número | consulta | ❌ |
| 19 | `confirmar_recepcion` | Firmar digitalmente recepciones | confirmacion | ✅ |
| 20 | `consultar_recepcion` | Ver estado de recepciones digitales | consulta | ❌ |
| 92 | `consultar_relacion` | Permiso para consultar relacion | accion | ❌ |
| 93 | `eliminar_relacion` | Permiso para eliminar relacion | accion | ❌ |
| 21 | `exportar_relacion` | Descargar relación en Excel o PDF | exportacion | ❌ |
| 22 | `filtrar_facturas` | Buscar facturas por fecha y criterios | filtro | ❌ |
| 23 | `generar_relacion` | Crear nuevas relaciones de facturas | formulario | ❌ |
| 24 | `generar_token_firma` | Crear tokens de firma digital | generacion | ✅ |
| 25 | `recepcion_digital` | Recibir relaciones digitalmente | formulario | ❌ |
| 26 | `reimprimir_relacion` | Volver a generar relaciones existentes | reimpresion | ❌ |
| 27 | `seleccionar_facturas` | Marcar facturas para incluir en relación | seleccion | ❌ |
| 28 | `verificar_token` | Validar tokens de firma digital | verificacion | ✅ |

### REPORTES (4 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 42 | `acceder_modulo` | Acceso general a reportes | acceso | ❌ |
| 43 | `exportar_datos` | Exportar datos en diferentes formatos | exportacion | ❌ |
| 44 | `reporte_facturas` | Generar reportes de facturas | reporte | ❌ |
| 45 | `reporte_terceros` | Generar reportes de terceros | reporte | ❌ |

### TERCEROS (16 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 156 | `acceder_modulo` | Acceso general al módulo de terceros | acceso | ❌ |
| 162 | `activar_tercero` | Cambiar estado activo de terceros | edicion | ✅ |
| 167 | `aprobar_registro` | Aprobar solicitudes de registro de terceros | aprobacion | ✅ |
| 158 | `consultar_terceros` | Listar y buscar terceros | consulta | ❌ |
| 160 | `crear_tercero` | Dar de alta nuevos terceros | creacion | ✅ |
| 166 | `descargar_documentos` | Descargar documentos del tercero | descarga | ❌ |
| 161 | `editar_tercero` | Modificar datos de terceros existentes | edicion | ✅ |
| 163 | `eliminar_tercero` | Borrar terceros del sistema | eliminacion | ✅ |
| 170 | `exportar_terceros` | Exportar listado de terceros a Excel | exportacion | ❌ |
| 171 | `importar_terceros` | Importar terceros masivamente desde Excel | importacion | ✅ |
| 168 | `rechazar_registro` | Rechazar solicitudes de registro | aprobacion | ✅ |
| 164 | `subir_documentos` | Cargar documentos del tercero (RUT, cámara) | carga | ❌ |
| 157 | `ver_dashboard` | Acceder al dashboard de terceros | vista | ❌ |
| 165 | `ver_documentos` | Ver documentos del tercero | vista | ❌ |
| 169 | `ver_estadisticas` | Dashboard de estadísticas de terceros | vista | ❌ |
| 159 | `ver_tercero` | Ver información completa de un tercero | vista | ❌ |

### USUARIOS_INTERNOS (4 permisos)

| ID | Acción | Descripción | Tipo | Crítico |
|----|--------|-------------|------|--------|
| 94 | `asignar_permisos` | Permiso para asignar permisos | accion | ❌ |
| 95 | `consultar_usuarios` | Permiso para consultar usuarios | accion | ❌ |
| 96 | `crear_usuario` | Permiso para crear usuario | accion | ❌ |
| 97 | `enviar_invitacion` | Permiso para enviar invitacion | accion | ❌ |

