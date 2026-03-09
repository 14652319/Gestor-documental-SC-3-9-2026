# 📦 BACKUP COMPLETO - GESTOR DOCUMENTAL
**Fecha de creación**: 9 de Enero de 2026 - 15:22:47  
**Servidor**: Windows - Puerto 8099

---

## 📍 INFORMACIÓN DEL PROYECTO RESPALDADO

### Ubicación Original
```
c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059
```

### Estado del Backup
✅ **BACKUP COMPLETO Y FUNCIONAL**

---

## 📂 CONTENIDO DEL BACKUP

### 1. ✅ Código Fuente Completo
- **app.py** (2,934 líneas) - Aplicación Flask principal
- **9 módulos** en `modules/`:
  - ✅ recibir_facturas (recepción de facturas)
  - ✅ relaciones (relaciones digitales)
  - ✅ causaciones (causaciones contables) - **ÚLTIMO CAMBIO: Ordenamiento de archivos corregido**
  - ✅ archivo_digital (archivo digital)
  - ✅ dian_vs_erp (reconciliación DIAN vs ERP)
  - ✅ admin (administración)
  - ✅ configuracion (configuración del sistema)
  - ✅ facturas_digitales (facturas digitales)
  - ✅ terceros (gestión de proveedores)

### 2. ✅ Base de Datos PostgreSQL
- **Archivo**: `backup_gestor_documental_COMPLETO.backup`
- **Tamaño**: 220.04 MB
- **Base de datos**: gestor_documental
- **Servidor**: localhost:5432
- **84 tablas** con datos completos

### 3. ✅ Esquemas SQL
- `sql/schema_core.sql` - Esquema principal (84 tablas)
- 37 archivos SQL adicionales con migraciones y actualizaciones

### 4. ✅ Templates
- 60+ plantillas HTML en `templates/`
- Incluye vistas de todos los módulos

### 5. ✅ Documentación
- 16 archivos de documentación en `docs/`
- Guías de instalación
- Inventarios de módulos
- Documentación técnica

### 6. ✅ Configuración
- `.env` (configuración de entorno)
- `requirements.txt` (dependencias Python)
- Archivos de configuración de módulos

### 7. ✅ Scripts de Utilidad
- 100+ scripts Python para administración
- Scripts de backup automático
- Scripts de migración de BD

---

## 🔧 ÚLTIMOS CAMBIOS APLICADOS

### Módulo Causaciones (9 Enero 2026 - 15:20)
**Archivo**: `modules/causaciones/routes.py`
**Líneas modificadas**: 114 y 378

**Cambio aplicado**:
```python
# ANTES (mostraba más recientes primero):
archivos.sort(key=lambda x: x['timestamp'], reverse=True)

# DESPUÉS (muestra más antiguos primero):
archivos.sort(key=lambda x: x['timestamp'], reverse=False)
```

**Solución de problemas**:
- Se limpió caché de Python (`__pycache__/` y `*.pyc`)
- Se reinició servidor Flask
- **Estado**: ✅ FUNCIONANDO CORRECTAMENTE

---

## 💾 RESTAURACIÓN DEL BACKUP

### Opción 1: Restaurar Código Fuente
```cmd
1. Copiar toda la carpeta a la ubicación deseada
2. Abrir terminal en la carpeta
3. Ejecutar: pip install -r requirements.txt
4. Configurar .env con credenciales de BD
5. Ejecutar: 1_iniciar_gestor.bat
```

### Opción 2: Restaurar Base de Datos
```cmd
# Windows PowerShell
cd "ruta\del\backup"
$env:PGPASSWORD = "tu_password"
& "C:\Program Files\PostgreSQL\18\bin\pg_restore.exe" -h localhost -p 5432 -U postgres -d gestor_documental -c backup_gestor_documental_COMPLETO.backup
```

### Opción 3: Restauración Completa
1. Restaurar código fuente (Opción 1)
2. Restaurar base de datos (Opción 2)
3. Verificar configuración en `.env`
4. Iniciar servidor: `1_iniciar_gestor.bat`
5. Acceder a: http://localhost:8099

---

## 📊 ESTADÍSTICAS DEL BACKUP

| Componente | Cantidad | Estado |
|------------|----------|--------|
| **Archivos Python** | 150+ | ✅ |
| **Templates HTML** | 60+ | ✅ |
| **Módulos** | 9 | ✅ |
| **Tablas BD** | 84 | ✅ |
| **Esquemas SQL** | 37 | ✅ |
| **Documentación** | 16 archivos | ✅ |
| **Scripts utilidad** | 100+ | ✅ |
| **Tamaño BD** | 220.04 MB | ✅ |
| **Tamaño total** | ~350 MB | ✅ |

---

## 🔐 CREDENCIALES (Actualizar en .env)

```env
# Base de datos
DATABASE_URL=postgresql://gestor_user:tu_password@localhost:5432/gestor_documental

# Flask
SECRET_KEY=tu_secret_key

# Correo (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_app_password

# Adobe Sign (opcional)
ADOBE_CLIENT_ID=tu_client_id
ADOBE_CLIENT_SECRET=tu_client_secret
```

---

## ⚙️ REQUISITOS DEL SISTEMA

### Software Necesario
- ✅ Python 3.11+
- ✅ PostgreSQL 18
- ✅ Windows 10/11
- ✅ 4GB RAM mínimo
- ✅ 2GB espacio en disco

### Puertos Requeridos
- **8099** - Aplicación principal Flask
- **5432** - PostgreSQL
- **8097** - DIAN vs ERP (standalone, opcional)

---

## 📝 NOTAS IMPORTANTES

1. **Caché de Python**: Si realizas cambios en el código y no se reflejan, limpia el caché:
   ```cmd
   Get-Process python* | Stop-Process -Force
   Remove-Item modules\*\__pycache__ -Recurse -Force
   .\1_iniciar_gestor.bat
   ```

2. **Modo Debug**: El servidor corre en modo debug, los cambios en `.py` se recargan automáticamente.

3. **Backup de BD**: Se recomienda hacer backup diario de la base de datos usando `backup_bd_postgres.py`

4. **Documentos**: Los archivos PDF de proveedores NO están incluidos en este backup (se encuentran en `documentos_terceros/`)

---

## 🆘 SOPORTE

Para restaurar o consultas técnicas, contactar al administrador del sistema.

**Última actualización**: 9 de Enero de 2026 - 15:44:24
