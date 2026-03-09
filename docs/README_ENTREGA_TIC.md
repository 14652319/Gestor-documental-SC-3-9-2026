# Entrega TIC — Gestor Documental (Python + PostgreSQL)

Este paquete cumple la solicitud de recepción formal del proyecto para el área de TIC de Supertiendas Cañaveral.

## 1. Código fuente completo
- Ubicación: carpeta raíz del proyecto y subcarpetas.
- Incluye `app.py`, `extensions.py`, `decoradores_permisos.py`, `utils_fecha.py`, módulos en `modules/`, templates en `templates/`, scripts utilitarios y subproyectos (p. ej., `Proyecto Dian Vs ERP v5.20251130`).

## 2. Estructura de carpetas
- Mantiene exactamente la estructura usada en desarrollo. Ver `README_Estructura.txt`.

## 3. Dependencias
- Archivo `requirements.txt` con todas las librerías requeridas.

## 4. Variables de entorno
- Archivo ejemplo: `.env.example` sin datos sensibles (ver raíz del proyecto).
- Copiar a `.env` y completar valores en producción.

## 5. Instalación y ejecución (Windows PowerShell)
```
cd "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python update_tables.py
python app.py  # http://localhost:8099
```

## 6. Scripts SQL
- `sql/schema_core.sql` (tablas base)
- `init_postgres.sql` (creación de DB/usuario)
- Módulos adicionales: `sql/schema_facturas.sql`, `sql/schema_relaciones.sql` (si están presentes).

## 7. Respaldo BD
- Se adjuntará un dump `.sql` o `.backup`. Restauración sugerida:
```
$PG_BIN = "C:\Program Files\PostgreSQL\18\bin"
$DB_NAME = "gestor_documental"; $DB_USER = "gestor_user"
$IN = "C:\Users\Usuario\Desktop\Gestor Documental\Backups\gestor_documental.backup"
& "$PG_BIN\pg_restore.exe" -U $DB_USER -d $DB_NAME -c $IN
```

## 8. Documentación técnica
- Ver `docs/` (Arquitectura, Técnico, Seguridad, etc.).

## 9. Documentación de API
- Ver `docs/API_REFERENCE.md`.

## 10. Manual de usuario
- `docs/GUIA_RAPIDA.md` y guías de uso incluidas.

## 11. Pruebas
- `test_endpoints.py` (suite principal). Otros tests disponibles en raíz.

## 12. Usuarios y accesos
- Usuarios de prueba y scripts: `crear_usuario_prueba.py`, `check_user_status.py`.
- Nuevos usuarios se crean con `activo=False`; activar vía `/api/admin/activar_usuario`.

## 13. Originalidad y licencias
- Ver `ORIGINALIDAD_Y_LICENCIAS.txt`.

## 14. Paquete comprimido
- Instrucciones para generar ZIP en `docs/ENTREGA_ZIP_INSTRUCCIONES.md` (incluida abajo):
```
$src = "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
$dest = "C:\Users\Usuario\Desktop\Gestor Documental\Documentación\ENTREGA_TIC_SC_GESTOR_DOCUMENTAL.zip"
Compress-Archive -Path $src -DestinationPath $dest -Force
```

---

## ENTORNO Y EJECUCIÓN RÁPIDA (Resumen)
- Requiere Python 3.8+ y PostgreSQL 18.
- Activar venv, instalar dependencias, configurar `.env`, ejecutar `app.py`.
- Actualizar tablas vía `update_tables.py`.
- Endpoints y módulos ver `docs/API_REFERENCE.md`.
