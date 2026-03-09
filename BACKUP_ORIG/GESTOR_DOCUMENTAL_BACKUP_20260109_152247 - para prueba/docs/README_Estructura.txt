
Estructura de carpetas (Gestor_Login_Seguro)
-------------------------------------------
/app.py                       -> Backend Flask (endpoints del login/registro/recuperación)
/requirements.txt             -> Dependencias
/.env.example                 -> Variables de entorno de ejemplo
/init_postgres.sql            -> Script para crear DB y usuario en PostgreSQL
/sql/schema_core.sql          -> Esquema de tablas (núcleo seguridad, IPs, tokens, etc.)

/templates/login.html         -> TU HTML original (sin tocar estilos)

/static/...                   -> Carpeta para CSS/JS/IMG adicionales
/logs/security.log            -> Log de seguridad (se genera al ejecutar)
/docs/Visión_Arquitectura.txt -> Notas de arquitectura y roadmap

/modules/                     -> Carpeta para futuros módulos (blueprints)
  admin/                      -> Administración de usuarios y permisos (por construir)
  notas_contables/
  recepcion_facturas/
  causaciones/
  seguridad_social/
  dian_vs_erp/

Notas:
- El login se sirve en "/".
- Endpoints disponibles: 
  * POST /api/auth/login
  * POST /api/registro/check_nit
  * POST /api/registro/proveedor
  * POST /api/auth/forgot_request
  * POST /api/auth/forgot_verify
  * POST /api/auth/change_password
- El log de seguridad registra intentos, cambios de contraseña y registros.
- Integra HTTPS, rate limiting y 2FA en fases siguientes.
