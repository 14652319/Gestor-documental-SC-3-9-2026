=================================================================
GUÍA DE INSTALACIÓN COMPLETA - GESTOR DOCUMENTAL
=================================================================
Fecha: 13 de Noviembre 2025
Sistema: Windows con PostgreSQL 18

PASO 1: PREPARAR EL ENTORNO
---------------------------
1. Abrir PowerShell como Administrador (opcional pero recomendado)
2. Navegar a la carpeta del proyecto:
   cd "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"

PASO 2: CREAR ENTORNO VIRTUAL DE PYTHON
----------------------------------------
1. Crear el virtualenv:
   python -m venv .venv

2. Activar el virtualenv:
   .\.venv\Scripts\activate

3. Actualizar pip (recomendado):
   python -m pip install --upgrade pip

4. Instalar dependencias:
   pip install -r requirements.txt

PASO 3: CONFIGURAR BASE DE DATOS POSTGRESQL
--------------------------------------------
1. Crear base de datos vacía (ejecutar en PowerShell):
   & "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres gestor_documental

   NOTA: Te pedirá la contraseña de PostgreSQL (la que definiste al instalar).

2. Restaurar el backup incluido (OPCIÓN RECOMENDADA):
   & "C:\Program Files\PostgreSQL\18\bin\pg_restore.exe" -U postgres -d gestor_documental -v "backup_gestor_documental.backup"

   ALTERNATIVA - Si pg_restore falla, usar el SQL:
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d gestor_documental -f "..\..\..\BACKUPS_TRANSPORTABLES\gestor_documental_SQL_20251113_202140.sql"

PASO 4: CONFIGURAR ARCHIVO .env
--------------------------------
1. Copiar el archivo de ejemplo:
   copy .env.example .env

2. Editar .env con tus configuraciones:
   - DATABASE_URL: Cambiar puerto, usuario y contraseña si es necesario
     Ejemplo: postgresql://postgres:tu_password@localhost:5432/gestor_documental
   
   - SECRET_KEY: Generar una clave segura (puedes usar Python):
     python -c "import secrets; print(secrets.token_hex(32))"
   
   - MAIL_*: Configurar correo si quieres notificaciones (opcional para empezar)

PASO 5: VERIFICAR INSTALACIÓN
------------------------------
1. Verificar tablas de la base de datos:
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d gestor_documental -c "\dt"

2. Ejecutar script de actualización (crea tablas faltantes si las hay):
   python update_tables.py

PASO 6: INICIAR EL SERVIDOR
----------------------------
1. Opción A - Comando directo:
   python app.py

2. Opción B - Usar el script batch:
   .\iniciar_servidor.bat

3. El servidor se iniciará en: http://localhost:8099

PASO 7: VERIFICAR FUNCIONAMIENTO
---------------------------------
1. Abrir navegador en: http://localhost:8099

2. Ejecutar tests (opcional):
   python test_endpoints.py

3. Crear usuario de prueba (opcional):
   python crear_usuario_prueba.py

PASO 8: CREDENCIALES DE ACCESO
-------------------------------
Si restauraste el backup, deberías tener usuarios pre-creados.
Verifica usuarios disponibles con:
   python check_user_status.py

Para ver todos los usuarios:
   python verificar_usuario.py

SOLUCIÓN DE PROBLEMAS COMUNES
==============================

1. ERROR: "psql no se reconoce"
   - Agregar PostgreSQL al PATH o usar rutas completas:
     $env:Path += ";C:\Program Files\PostgreSQL\18\bin"

2. ERROR: "database already exists"
   - La base de datos ya existe, solo ejecuta pg_restore o psql para restaurar

3. ERROR: "authentication failed"
   - Verifica la contraseña de PostgreSQL
   - Edita DATABASE_URL en .env con las credenciales correctas

4. ERROR: "No module named..."
   - Asegúrate de tener el virtualenv activado (.venv\Scripts\activate)
   - Reinstala dependencias: pip install -r requirements.txt

5. ERROR: "Port 8099 already in use"
   - Otro proceso usa el puerto, cambia el puerto en app.py (última línea)
   - O detén el proceso que usa el puerto 8099

COMANDOS DE REFERENCIA RÁPIDA
==============================
# Activar entorno virtual
.\.venv\Scripts\activate

# Iniciar servidor
python app.py

# Ver logs
type logs\security.log

# Actualizar base de datos
python update_tables.py

# Crear backup manual
& "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U postgres -F c -b -v -f "backup_manual.backup" gestor_documental

NOTAS IMPORTANTES
=================
- Puerto por defecto del servidor: 8099
- Puerto por defecto de PostgreSQL: 5432 (o 5436 según tu .env.example)
- Logs de seguridad: logs/security.log
- Archivos de terceros: documentos_terceros/

¡INSTALACIÓN COMPLETADA!
=========================
Una vez completados todos los pasos, el sistema estará listo para usar.
Accede a http://localhost:8099 para comenzar.
