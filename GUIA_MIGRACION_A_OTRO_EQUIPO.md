# 📦 GUÍA COMPLETA: MIGRAR EL GESTOR DOCUMENTAL A OTRO EQUIPO

**Fecha:** 05/03/2026  
**Objetivo:** Copiar la aplicación completa con base de datos a otro equipo en red

---

## 🎯 RESUMEN EJECUTIVO

Para que la aplicación funcione en otro equipo necesitas:
1. ✅ Los archivos del proyecto (código)
2. ✅ La base de datos PostgreSQL (tablas + datos)
3. ✅ Configurar el entorno Python
4. ✅ Ajustar el archivo .env

---

## 📋 PROCESO COMPLETO (PASO A PASO)

### 🖥️ EN EL EQUIPO ORIGINAL (DONDE ESTÁ FUNCIONANDO)

#### ✅ Paso 1: Exportar la Base de Datos

Ejecuta uno de estos scripts:

**Opción A - Automático (RECOMENDADO):**
```batch
1_EXPORTAR_BD_PARA_OTRO_EQUIPO.bat
```

**Opción B - Con pg_dump (Manual):**
```batch
exportar_bd_completa.py
```

**Resultado:** Se creará una carpeta `EXPORT_BD_YYYYMMDD_HHMMSS` con:
- `backup_completo.sql` (todas las tablas y datos)
- `info_backup.json` (metadata)
- `INSTRUCCIONES_IMPORTAR.txt` (guía)

#### ✅ Paso 2: Copiar Todo al Otro Equipo

Copia estas carpetas/archivos al otro equipo:

**OBLIGATORIOS:**
- ✅ Toda la carpeta del proyecto completo
- ✅ Carpeta `EXPORT_BD_*` (con el backup SQL)
- ✅ Archivo `.env` (configuración)
- ✅ Carpeta `templates/` (HTML)
- ✅ Carpeta `static/` (CSS, JS, imágenes)
- ✅ Carpeta `modules/` (módulos del sistema)
- ✅ Archivo `requirements.txt` (dependencias)
- ✅ Archivo `app.py` (aplicación principal)

**OPCIONALES (pero recomendados):**
- 📁 `documentos_terceros/` (PDFs almacenados)
- 📁 `logs/` (historiales)
- 📁 `sql/` (scripts SQL adicionales)

---

### 🖥️ EN EL EQUIPO NUEVO (DONDE QUIERES INSTALAR)

#### ✅ Paso 1: Instalar PostgreSQL

1. Descarga PostgreSQL 18: https://www.postgresql.org/download/
2. Ejecuta el instalador
3. **IMPORTANTE:** Anota la contraseña que uses para el usuario `postgres`
4. Puerto por defecto: 5432

**Verificar instalación:**
```batch
psql --version
```

#### ✅ Paso 2: Instalar Python

1. Descarga Python 3.8+: https://www.python.org/downloads/
2. **IMPORTANTE:** Marca "Add Python to PATH" durante instalación
3. Verifica:
```batch
python --version
```

#### ✅ Paso 3: Crear Virtualenv e Instalar Dependencias

Abre PowerShell en la carpeta del proyecto:

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### ✅ Paso 4: Configurar el Archivo .env

Edita el archivo `.env` y ajusta estas líneas:

```env
# BASE DE DATOS (CAMBIAR EL PASSWORD)
DATABASE_URL=postgresql://postgres:TU_PASSWORD_AQUI@localhost:5432/gestor_documental

# El resto puede quedar igual (correo, telegram, etc.)
```

**IMPORTANTE:** Cambia `TU_PASSWORD_AQUI` por la contraseña que pusiste al instalar PostgreSQL.

#### ✅ Paso 5: Importar la Base de Datos

**Opción A - Script Automático (RECOMENDADO):**
```batch
2_IMPORTAR_BD_DESDE_BACKUP.bat
```

El script te pedirá:
- Contraseña de PostgreSQL
- Confirmación para continuar

**Opción B - Manual (Línea de comandos):**
```batch
# Crear la base de datos
psql -U postgres -c "CREATE DATABASE gestor_documental;"

# Importar el backup
psql -U postgres -d gestor_documental -f EXPORT_BD_*/backup_completo.sql
```

**Resultado esperado:**
```
✅ Base de datos: gestor_documental creada
✅ XX tablas importadas
✅ XXXX registros importados
```

#### ✅ Paso 6: Verificar la Importación

```batch
# Conectar a la base de datos
psql -U postgres -d gestor_documental

# Ver tablas
\dt

# Ver usuarios (ejemplo)
SELECT * FROM usuarios LIMIT 5;

# Salir
\q
```

#### ✅ Paso 7: Iniciar la Aplicación

```batch
1_iniciar_gestor.bat
```

Deberías ver:
```
* Running on http://0.0.0.0:8099
* Running on http://192.168.X.X:8099
```

#### ✅ Paso 8: Probar el Acceso

Abre un navegador:
```
http://localhost:8099
```

**Debería cargar el login del Gestor Documental.**

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "No se puede conectar a PostgreSQL"

**Causa:** PostgreSQL no está corriendo o puerto incorrecto

**Solución:**
1. Abre "Servicios" de Windows
2. Busca "postgresql-x64-18"
3. Click derecho → Iniciar
4. O ejecuta:
```batch
net start postgresql-x64-18
```

### ❌ Error: "Authentication failed for user postgres"

**Causa:** Contraseña incorrecta en .env

**Solución:**
1. Edita `.env`
2. Verifica la contraseña en DATABASE_URL
3. Si olvidaste la contraseña, reinstala PostgreSQL

### ❌ Error: "Database 'gestor_documental' does not exist"

**Causa:** No se ejecutó el paso de importación

**Solución:**
1. Ejecuta: `2_IMPORTAR_BD_DESDE_BACKUP.bat`
2. O manualmente:
```batch
psql -U postgres -c "CREATE DATABASE gestor_documental;"
psql -U postgres -d gestor_documental -f EXPORT_BD_*/backup_completo.sql
```

### ❌ Error: "ModuleNotFoundError: No module named 'flask'"

**Causa:** Dependencias no instaladas

**Solución:**
```batch
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### ❌ Error: "Puerto 8099 ya está en uso"

**Causa:** Otra aplicación usa el puerto

**Solución:**
1. Cambia el puerto en `app.py` (línea ~3024):
```python
app.run(host="0.0.0.0", port=8100, debug=True, use_reloader=False)
```
2. O cierra la aplicación que usa el puerto

---

## 📊 CHECKLIST DE VERIFICACIÓN

### ✅ Antes de Copiar (Equipo Original)
- [ ] Exportar base de datos (EXPORT_BD_*)
- [ ] Copiar toda la carpeta del proyecto
- [ ] Copiar carpeta de documentos (documentos_terceros/)
- [ ] Anotar configuraciones especiales del .env

### ✅ En el Equipo Nuevo
- [ ] PostgreSQL instalado y corriendo
- [ ] Python 3.8+ instalado
- [ ] Virtualenv creado (.venv)
- [ ] Dependencias instaladas (requirements.txt)
- [ ] Archivo .env configurado (PASSWORD correcto)
- [ ] Base de datos importada (gestor_documental)
- [ ] Aplicación inicia sin errores
- [ ] Login funciona correctamente
- [ ] Puedes ver datos (usuarios, facturas, etc.)

---

## 🌐 ACCESO POR RED WIFI

Si quieres acceder desde otros equipos:

1. **Obtén tu IP:**
```batch
ipconfig
```
Busca: Adaptador de LAN inalámbrica Wi-Fi → Dirección IPv4

2. **Abre el Firewall:**
```batch
ABRIR_FIREWALL_GESTOR.bat
```

3. **Accede desde otros dispositivos:**
```
http://TU_IP:8099
```

Ejemplo: `http://192.168.100.121:8099`

---

## 🆘 SOPORTE ADICIONAL

Si tienes problemas:

1. **Revisa los logs:**
```
logs/security.log
logs/app.log
```

2. **Verifica la conexión a BD:**
```batch
python
>>> from extensions import db
>>> from app import app
>>> with app.app_context(): db.engine.execute('SELECT 1')
```

3. **Scripts de diagnóstico:**
```batch
verificar_usuario.py
check_user_status.py
```

---

## 📝 NOTAS IMPORTANTES

- ⚠️ La exportación incluye **TODOS los datos** (usuarios, contraseñas, facturas, etc.)
- ⚠️ El backup SQL puede ser muy grande (100-500 MB según datos)
- ⚠️ PostgreSQL debe tener la **misma versión** o superior en el nuevo equipo
- ⚠️ Los NITs especiales y configuraciones se mantienen
- ⚠️ Las contraseñas de usuarios están hasheadas (seguras)

---

## 🎯 SCRIPTS CREADOS PARA TI

1. `1_EXPORTAR_BD_PARA_OTRO_EQUIPO.bat` - Ejecutar en equipo original
2. `2_IMPORTAR_BD_DESDE_BACKUP.bat` - Ejecutar en equipo nuevo
3. `ABRIR_FIREWALL_GESTOR.bat` - Para acceso en red
4. `1_iniciar_gestor.bat` - Iniciar aplicación

---

**¿Dudas? Revisa esta guía paso a paso o consulta los archivos INSTRUCCIONES_IMPORTAR.txt que se generan automáticamente.**

---

Última actualización: 05/03/2026
