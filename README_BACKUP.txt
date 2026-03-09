# 📦 BACKUP COMPLETO - GESTOR DOCUMENTAL

**Fecha de creación:** 26/12/2025 22:04:49
**Versión:** 1.0.0
**Estado:** Productivo y Funcional

---

## 📋 CONTENIDO DEL BACKUP

Este backup incluye:

### 1. Código Fuente
- ✅ Archivo principal: `app.py`
- ✅ Módulos: `modules/` (recibir_facturas, relaciones, causaciones, dian_vs_erp, etc.)
- ✅ Templates: `templates/`
- ✅ Estilos: `static/`
- ✅ Utilities: `extensions.py`, `decoradores_permisos.py`, `utils_fecha.py`
- ✅ Scripts SQL: `sql/`
- ✅ Dependencias: `requirements.txt`

### 2. Base de Datos PostgreSQL
- ✅ Backup completo formato custom (.backup)
- ✅ Todas las tablas con datos
- ✅ Índices y constraints
- ✅ Secuencias y triggers
- ✅ Usuarios y permisos

**Tablas incluidas (40+):**
- Maestro DIAN: `maestro_dian_vs_erp`
- Envíos programados: `envios_programados_dian_vs_erp`
- Usuarios asignados: `usuarios_asignados`
- Historial: `historial_envios_dian_vs_erp`
- Facturas: `facturas_temporales`, `facturas_recibidas`
- Relaciones: `relaciones_facturas`, `recepciones_digitales`
- Core: `terceros`, `usuarios`, `accesos`
- Y más...

### 3. Configuraciones
- ✅ Archivo `.env` (variables de entorno)
- ✅ Logs del sistema: `logs/`
- ✅ Documentación: `DOCUMENTACION_MODULO_DIAN_VS_ERP.md`
- ✅ Instrucciones: `README_Estructura.txt`, `REQUISITOS_INSTALACION.txt`

### 4. Documentación
- ✅ Manual completo del módulo DIAN vs ERP
- ✅ Instrucciones de instalación
- ✅ Guías de configuración
- ✅ Copilot instructions para IA

---

## 🔄 CÓMO RESTAURAR EL BACKUP

### Opción 1: Script Automático (Recomendado)

1. Ejecutar: `RESTAURAR_BACKUP.bat`
2. Seguir instrucciones en pantalla
3. Listo - Sistema restaurado

### Opción 2: Manual

#### Paso 1: Extraer archivos
```cmd
powershell -Command "Expand-Archive -Path 'BACKUP_COMPLETO_YYYYMMDD_HHMMSS.zip' -DestinationPath 'gestor_restaurado'"
cd gestor_restaurado
```

#### Paso 2: Restaurar base de datos
```cmd
REM Crear base de datos
psql -U postgres -c "DROP DATABASE IF EXISTS gestor_documental;"
psql -U postgres -c "CREATE DATABASE gestor_documental OWNER gestor_user;"

REM Restaurar backup
pg_restore -U gestor_user -d gestor_documental -v backup_gestor_documental_YYYYMMDD_HHMMSS.backup
```

#### Paso 3: Configurar entorno
```cmd
REM Crear virtualenv
python -m venv .venv
.venv\Scripts\activate

REM Instalar dependencias
pip install -r requirements.txt
```

#### Paso 4: Verificar configuración
```cmd
REM Editar .env si es necesario
notepad .env

REM Verificar conexión BD
python -c "from app import db; print('DB OK')"
```

#### Paso 5: Iniciar sistema
```cmd
python app.py
```

Acceder a: http://localhost:8099

---

## ⚙️ REQUISITOS DEL SISTEMA

### Software Necesario
- **Python:** 3.11+ (3.11.9 recomendado)
- **PostgreSQL:** 14+ (18 recomendado)
- **pip:** Última versión
- **virtualenv:** Para entorno aislado

### Configuraciones PostgreSQL
```sql
-- Usuario: gestor_user
-- Password: abc123
-- Base de datos: gestor_documental
-- Puerto: 5432
```

### Variables de Entorno (.env)
```env
SECRET_KEY=tu_secret_key_aqui
DATABASE_URL=postgresql://gestor_user:abc123@localhost:5432/gestor_documental

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=urjrkjlogcfdtynq
```

---

## 🧪 VERIFICACIÓN POST-RESTAURACIÓN

### 1. Verificar Base de Datos
```sql
-- Conectar a PostgreSQL
psql -U gestor_user -d gestor_documental

-- Verificar tablas
\dt

-- Verificar datos en tabla principal
SELECT COUNT(*) FROM maestro_dian_vs_erp;
SELECT COUNT(*) FROM usuarios_asignados;
SELECT COUNT(*) FROM envios_programados_dian_vs_erp;
```

### 2. Verificar Módulos
```bash
# Probar imports
python -c "from modules.dian_vs_erp.routes import dian_vs_erp_bp; print('OK')"
python -c "from modules.dian_vs_erp.scheduler_envios import EnviosProgramadosSchedulerDianVsErp; print('OK')"
```

### 3. Verificar Servidor
```bash
# Iniciar servidor
python app.py

# En otra terminal, probar endpoints
curl http://localhost:8099/
curl http://localhost:8099/dian_vs_erp/api/maestro/documentos?page=1
```

---

## 📊 INFORMACIÓN DEL BACKUP

### Tamaño Estimado
- Código fuente: ~50 MB
- Base de datos: ~10-50 MB (depende de datos)
- Total: ~60-100 MB comprimido

### Tiempo de Restauración
- Extracción ZIP: 1-2 minutos
- Restauración BD: 2-5 minutos
- Instalación dependencias: 3-5 minutos
- **Total:** 10-15 minutos

---

## 🆘 PROBLEMAS COMUNES

### Error: "pg_restore: command not found"
**Solución:** Agregar PostgreSQL al PATH:
```cmd
set PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin
```

### Error: "psycopg2 import error"
**Solución:**
```cmd
pip uninstall psycopg2 psycopg2-binary
pip install psycopg2-binary==2.9.9
```

### Error: "Puerto 8099 ya en uso"
**Solución:**
```cmd
REM Matar proceso en puerto 8099
netstat -ano | findstr :8099
taskkill /PID <PID> /F
```

### Error: "SMTP Authentication failed"
**Solución:** Verificar variables MAIL_* en .env y usar App Password de Gmail (2FA habilitado)

---

## 📞 SOPORTE

**Desarrollador:** Ricardo Riascos  
**Email:** ricardoriascos07@gmail.com  
**Empresa:** Supertiendas Cañaveral  

---

## 📝 NOTAS IMPORTANTES

⚠️ **SEGURIDAD:**
- Este backup contiene archivo `.env` con credenciales
- NO compartir públicamente
- Guardar en ubicación segura con acceso restringido

⚠️ **PRODUCCIÓN:**
- Sistema completamente funcional y testeado
- Incluye módulo DIAN vs ERP operativo
- Scheduler de envíos programados funcionando
- Excel con hipervínculos a DIAN implementado

⚠️ **VERSIONES:**
- Última actualización: 26/12/2025
- Todas las funcionalidades documentadas están operativas
- Sistema listo para uso en producción

---

**FIN DEL README**
