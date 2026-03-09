# 📋 GESTOR DOCUMENTAL - Supertiendas Cañaveral

Sistema integral de gestión documental con múltiples módulos especializados.

---

## 📚 DOCUMENTACIÓN PRINCIPAL

### 🎯 Para empezar:

**Ver:** [.github/copilot-instructions.md](.github/copilot-instructions.md) - Guía completa del sistema

### 🔥 MÓDULO DIAN vs ERP (ACTUALIZADO - 20 Feb 2026)

**✅ Sistema 100% funcional - 173,342 registros procesados**

**LEE ESTO:** [SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md](SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md)

Documento completo con:
- ✅ Arquitectura y funcionamiento
- ✅ 8 bugs resueltos con explicaciones
- ✅ Código crítico con ejemplos
- ✅ Cómo ejecutar y mantener
- ✅ Troubleshooting completo

**ÍNDICE de documentos:** [INDEX_DOCUMENTACION_DIAN.md](INDEX_DOCUMENTACION_DIAN.md)

---

## 🚀 INICIO RÁPIDO

### Iniciar el sistema:

```bash
# Activar entorno virtual
.\.venv\Scripts\activate

# Iniciar aplicación principal (puerto 8099)
.\1_iniciar_gestor.bat

# O manualmente:
python app.py
```

### Iniciar módulo DIAN vs ERP standalone (opcional):

```bash
# Iniciar módulo DIAN independiente (puerto 8097)
.\2_iniciar_dian.bat
```

---

## 📊 MÓDULOS DISPONIBLES

### ✅ Módulos Operativos (Productivos)

1. **Recibir Facturas** - Recepción de facturas de proveedores
2. **Relaciones** - Generación de relaciones digitales de facturas
3. **Terceros** - Gestión de proveedores y terceros
4. **DIAN vs ERP** - Reconciliación de facturas electrónicas ⭐ **ACTUALIZADO**
5. **Facturas Digitales** - Gestión de facturas electrónicas
6. **SAGRILAFT** - Sistema de prevención de lavado de activos
7. **Archivo Digital** - Repositorio digital de documentos
8. **Monitoreo** - Dashboard de sesiones activas

### ⚠️ Módulos en Desarrollo

- **Causaciones** - En construcción
- **Notas Contables** - En construcción
- **Admin** - Gestión de usuarios y permisos

---

## 🗄️ BASE DE DATOS

**PostgreSQL 18** - Base de datos principal  
**SQLite** - Caché de alto rendimiento (módulo DIAN standalone)

### Comandos útiles:

```bash
# Actualizar esquema de base de datos
python update_tables.py

# Verificar estado de tablas DIAN vs ERP
python CHECK_ALL_TABLES.py

# Backup manual de base de datos
.\BACKUP_BD_MANUAL.bat
```

---

## 🔧 CONFIGURACIÓN

### Variables de entorno (.env)

```env
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/gestor_documental

# Seguridad
SECRET_KEY=your_secret_key_here

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your_app_password

# Telegram (opcional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Licencia
LICENSE_ENFORCE=True
LICENSE_FILE=license.lic
LICENSE_GRACE_DAYS=180
```

---

## 📖 DOCUMENTACIÓN ADICIONAL

### Guías de instalación:
- [GUIA_INSTALACION_COMPLETA.md](GUIA_INSTALACION_COMPLETA.md) - Instalación completa paso a paso

### Configuración específica:
- [docs/CONFIGURACION_CORREO.md](docs/CONFIGURACION_CORREO.md) - Configurar email
- [docs/SISTEMA_TELEGRAM.md](docs/SISTEMA_TELEGRAM.md) - Configurar Telegram
- [COMO_CAMBIAR_CORREO.md](COMO_CAMBIAR_CORREO.md) - Cambiar entre proveedores de email

### Módulos específicos:
- **DIAN vs ERP:** [SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md](SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md) ⭐
- **Terceros:** [ACTUALIZACION_COMPLETA_TERCEROS_30ENE2026.md](ACTUALIZACION_COMPLETA_TERCEROS_30ENE2026.md)
- **SAGRILAFT:** [ANALISIS_TABLAS_SAGRILAFT.md](ANALISIS_TABLAS_SAGRILAFT.md)

---

## 🧪 TESTING

```bash
# Ejecutar tests
python test_endpoints.py

# Crear usuario de prueba
python crear_usuario_prueba.py

# Verificar estado de usuario
python check_user_status.py
python verificar_usuario.py
```

---

## 📁 ESTRUCTURA DEL PROYECTO

```
/
├── app.py                          # Aplicación Flask principal
├── modules/                        # Módulos Blueprint
│   ├── recibir_facturas/          # Recepción de facturas
│   ├── relaciones/                # Relaciones digitales
│   ├── terceros/                  # Gestión de terceros
│   ├── dian_vs_erp/               # DIAN vs ERP ⭐
│   ├── facturas_digitales/        # Facturas digitales
│   ├── sagrilaft/                 # SAGRILAFT
│   └── ...
├── templates/                      # Plantillas HTML
├── static/                         # Archivos estáticos
├── logs/                          # Logs del sistema
├── documentos_terceros/           # Archivos de terceros
├── uploads/                       # Archivos cargados (DIAN)
└── sql/                           # Scripts SQL
```

---

## 🛠️ UTILIDADES

### Scripts de mantenimiento:

```bash
# Activar usuario admin
python activar_admin.py

# Actualizar sistema completo
python actualizar_sistema_completo.py

# Agregar permisos faltantes
python agregar_permisos_faltantes.py

# Actualizar IPs blancas
python actualizar_ips_blancas.py
```

---

## 🔒 SEGURIDAD

- **Licencia:** Sistema de licencias con periodo de gracia
- **Sesiones:** 25 minutos de inactividad
- **Permisos:** Sistema granular de permisos por módulo
- **IPs:** Lista blanca/negra/sospechosas
- **Logs:** Auditoría completa en `logs/security.log`

---

## 📊 ESTADÍSTICAS ACTUALES (20 Feb 2026)

### Módulo DIAN vs ERP:
```
✅ dian:                1,400 registros
✅ erp_comercial:      57,191 registros
✅ erp_financiero:      2,995 registros
✅ acuses:             46,650 registros
✅ maestro:            65,106 registros
─────────────────────────────────────
   TOTAL:            173,342 registros
```

**Velocidad:** ~25,000 registros/segundo  
**Tecnología:** PostgreSQL COPY FROM + Polars

---

## 🆘 TROUBLESHOOTING

### El servidor no inicia:
1. Verificar que el puerto 8099 esté libre
2. Revisar `logs/security.log` para errores
3. Verificar conexión a PostgreSQL

### Problemas con DIAN vs ERP:
Ver documentación completa: [SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md](SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md)

### Error de licencia:
1. Verificar archivo `license.lic` existe
2. Verificar variable `LICENSE_ENFORCE` en `.env`
3. Verificar periodo de gracia `LICENSE_GRACE_DAYS`

---

## 📞 CONTACTO

**Empresa:** Supertiendas Cañaveral S.A.  
**NIT:** 805028041  

---

**Última actualización:** 20 de Febrero de 2026  
**Versión del sistema:** v1.0 - Producción
