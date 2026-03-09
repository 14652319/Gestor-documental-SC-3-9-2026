# Checklist de Entrega TIC — Gestor Documental SC

Este checklist consolida los 14+ puntos requeridos por TIC para la entrega formal.

## 1. Código fuente y estructura
- [x] Carpeta del proyecto: `PAQUETES_TRANSPORTABLES/GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059`
- [x] `app.py`, `extensions.py`, `decoradores_permisos.py`, `utils_fecha.py`
- [x] Módulos y plantillas, incluyendo `Proyecto Dian Vs ERP v5.20251130`

## 2. Dependencias
- [x] `requirements.txt` actualizado
- [x] Guía de instalación: `GUIA_INSTALACION_COMPLETA.md`, `INSTALACION.txt`

## 3. Variables de entorno
- [x] `.env.example` sin secretos (en raíz)
- [ ] `.env` real (no incluido en entrega; preparar en sitio)

## 4. Scripts de BD y esquema
- [x] Scripts SQL en raíz: `CREAR_BD_MANUAL.sql`, `agregar_forma_pago.sql`
- [x] Scripts auxiliares: `update_tables.py`, `crear_tablas_*`

## 5. Respaldo BD
 Licenciamiento por servidor (huella + periodo de gracia)
## 6. Documentación técnica y de APIs
- [x] Documentación técnica en `Documentación/` (MD + DOCX parciales)
- [x] Interceptor global de sesión expirada (`_session_expired_interceptor.html`)
- [x] `before_request` unificado en `app.py` (redirige HTML; 401 en APIs)
- [x] `logs/security.log` (no empaquetado si está bloqueado; se entrega copia cuando sea posible)
- [x] Otros tests: `test_autenticado.py`, `test_email.py`, etc.

## 10. Postman / pruebas de API
- [x] Colección mínima: `docs/Postman/Gestor_Documental.postman_collection.json`
- [ ] Entorno con variables: `docs/Postman/env.local.postman_environment.json`

## 11. Accesos y credenciales
- [x] Usuario admin de prueba (scripts: `crear_usuario_prueba.py`, `activar_admin.py`)
- [ ] Credenciales reales: se comparten por canal seguro (no en la entrega)

## 12. Licencias y originalidad
- [x] `ORIGINALIDAD_Y_LICENCIAS.txt`

## 13. Empaquetado final (ZIP)
- [x] ZIP creado: `Documentación/ENTREGA_TIC_SC_GESTOR_DOCUMENTAL.zip`
- [x] Instrucciones ZIP: `docs/ENTREGA_ZIP_INSTRUCCIONES.md`

## 15. Pendientes y próximos pasos
- [ ] Generar `backup_gestor_documental.sql` (si se requiere)
- [ ] Completar conversiones DOCX de todos los manuales
- [ ] Exportar colección Postman extendida y entorno con variables

---

## Comandos útiles (PowerShell)

```powershell
# Comprimir nuevamente si se requiere
$src = "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
$destDir = "C:\Users\Usuario\Desktop\Gestor Documental\Documentación"
$zip = Join-Path $destDir "ENTREGA_TIC_SC_GESTOR_DOCUMENTAL.zip"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$staging = Join-Path $env:TEMP "ENTREGA_TIC_STAGING"
if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
New-Item -ItemType Directory -Path $staging | Out-Null
robocopy $src $staging /MIR /XD (Join-Path $src "logs") | Out-Null
Compress-Archive -Path (Join-Path $staging "*") -DestinationPath $zip -Force

# Verificar ZIP
Get-Item $zip | Format-List *
```

```powershell
# (Opcional) Generar dump SQL si están configuradas variables de entorno de PG
# Requiere: psql/pg_dump en PATH y credenciales válidas
$env:PGHOST = "localhost"; $env:PGPORT = "5432"; $env:PGDATABASE = "gestor_documental"; $env:PGUSER = "gestor_user"; $env:PGPASSWORD = "<password>"
$docDir = "C:\Users\Usuario\Desktop\Gestor Documental\Documentación"
& pg_dump -h $env:PGHOST -p $env:PGPORT -U $env:PGUSER -d $env:PGDATABASE -F p -f (Join-Path $docDir "backup_gestor_documental.sql")
```
