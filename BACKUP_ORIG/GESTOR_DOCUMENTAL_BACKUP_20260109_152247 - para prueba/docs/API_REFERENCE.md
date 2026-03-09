# Referencia de API — Gestor Documental

## Autenticación
- `POST /api/auth/login`
  - Body: `{ nit, usuario, password }`
  - Respuesta: `{ ok: true/false, message }`

- `POST /api/auth/forgot_request`
  - Body: `{ nit, usuario, correo }`
  - Respuesta: `{ ok, message }`

- `POST /api/auth/forgot_verify`
  - Body: `{ nit, usuario, token }`
  - Respuesta: `{ ok, message }`

- `POST /api/auth/change_password`
  - Body: `{ nit, usuario, token, new_password }`
  - Respuesta: `{ ok, message }`

## Registro de Proveedores
- `POST /api/registro/check_nit`
  - Body: `{ nit }`
  - Respuesta: `{ success, data }`

- `POST /api/registro/proveedor`
  - Body: datos del proveedor (JSON)
  - Respuesta: validación sin persistir

- `POST /api/registro/cargar_documentos`
  - Files: 7 PDFs requeridos
  - Respuesta: `{ success, carpeta_temp }`

- `POST /api/registro/finalizar`
  - Respuesta: `{ success, radicado }`

## Consultas
- `POST /api/consulta/radicado`
  - Body: `{ radicado }`
  - Respuesta: estado de solicitud

## Administración
- `POST /api/admin/activar_usuario`
  - Body: `{ usuario_id, activo }`
  - Respuesta: `{ success }`

- `GET /api/admin/listar_usuarios`
  - Respuesta: lista de usuarios con tercero

## Recibir Facturas
- `GET /recibir_facturas/nueva_factura`
  - Página HTML

- `GET /recibir_facturas/verificar_tercero?nit=...`
  - Respuesta: datos del tercero

- `POST /recibir_facturas/validar_factura`
  - Body: `{ prefijo, folio }`

- `POST /recibir_facturas/adicionar_factura`
  - Body: datos factura temporal

- `GET /recibir_facturas/cargar_facturas`
  - Respuesta: array de temporales del usuario

- `PUT /recibir_facturas/actualizar_factura_temporal/<id>`
  - Body: cambios y observaciones

- `DELETE /recibir_facturas/eliminar_factura/<id>`

- `POST /recibir_facturas/guardar_facturas`

- `POST /recibir_facturas/exportar_temporales`

## Relaciones de Facturas
- `GET /relaciones/generar_relacion`
- `POST /relaciones/filtrar_facturas`
- `POST /relaciones/generar_relacion` (digital/física)
- `GET /relaciones/recepcion_digital`
- `POST /relaciones/buscar_relacion_recepcion`
- `POST /relaciones/confirmar_recepcion_digital`
- `POST /relaciones/generar_token_firma`
- `POST /relaciones/verificar_token_firma`
- `GET /relaciones/exportar_relacion/<numero>`
- `GET /relaciones/consultar_recepcion/<numero>`
- `GET /relaciones/reimpimir_relacion/<numero>`
- `DELETE /relaciones/eliminar_relacion/<numero>`
- `GET /relaciones/listar_recepciones`
- `GET /relaciones/facturas_relacionadas/<numero>`
- `GET /relaciones/historial_recepciones/<numero>`

## Proyecto DIAN vs ERP (vistas clave)
- `GET /api/dian`
  - Respuesta: lista de documentos (DIAN/ERP)

- `POST /api/actualizar_nit`
  - Body: `{ nit, campo, valor }`

- `POST /api/actualizar_campo`
  - Body: `{ cufe, campo, valor }`

- `GET /api/usuarios/por_nit/<nit>`
  - Respuesta: `{ exito, usuarios: [...] }`

- `POST /api/enviar_emails`
  - Body: `{ cufe, destinatarios: [{correo, nombre}] }`

- `POST /api/enviar_email_agrupado`
  - Body: `{ destinatarios: [{correo, nombre}], cufes: [...] }`

## Notas
- Autenticación por sesión; expiración 25 minutos. 401 redirige a login con `?expired=1`.
- Fechas en zona Colombia (naive datetimes).
- Respuestas JSON siguen `{success: bool, message?: string, data?: any}`.
