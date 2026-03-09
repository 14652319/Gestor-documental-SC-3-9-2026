# 🤖 Bot de Telegram - Roadmap de Comandos
**Gestor Documental v2.0**  
**Fecha:** 27 Febrero 2026  
**Estado:** Implementación Mínima (Comando /desbloquear)

---

## ✅ COMANDOS IMPLEMENTADOS (v1.0)

### 🔓 `/desbloquear [IP]`
**Descripción:** Desbloquea una IP previamente bloqueada por intentos fallidos de login  
**Uso:** `/desbloquear 192.168.1.100`  
**Permisos:** Solo administrador autorizado  
**Acciones:**
- ✅ Elimina IP de lista negra
- ✅ Elimina IP de IPs sospechosas
- ✅ Agrega IP a lista blanca automáticamente
- ✅ Registra en logs de seguridad

**Ejemplo de respuesta:**
```
✅ IP DESBLOQUEADA EXITOSAMENTE

🌐 IP: 192.168.1.100
📅 Fecha: 2026-02-27 15:30:45

🔓 Acciones realizadas:
✅ Eliminada de lista negra (1 registros)
✅ Eliminada de IPs sospechosas (1 registros)
✅ Agregada a lista blanca

🎯 La IP ahora tiene acceso completo al sistema
```

### ❓ `/ayuda`
**Descripción:** Muestra lista de comandos disponibles  
**Uso:** `/ayuda`  
**Permisos:** Todos

---

## 📋 COMANDOS FUTUROS POR NIVEL

### **NIVEL 1: Seguridad y Monitoreo** 🛡️ (Prioridad: ALTA)

#### `/bloquear [IP]`
- **ETA:** 2-3 horas
- **Descripción:** Bloquea una IP manualmente (opuesto a /desbloquear)
- **Uso:** `/bloquear 192.168.1.50 Intento de ataque detectado`
- **Acciones:**
  - Agrega IP a lista negra
  - Marca como bloqueada en IPs sospechosas
  - Registra motivo del bloqueo
  - Envía confirmación con timestamp

#### `/whois [IP]`
- **ETA:** 3-4 horas
- **Descripción:** Información detallada de una IP
- **Uso:** `/whois 192.168.1.100`
- **Muestra:**
  - Estado actual (bloqueada/sospechosa/blanca)
  - Número de intentos fallidos
  - Último usuario que intentó ingresar
  - Última actividad (fecha/hora)
  - Historial de accesos (últimos 10)

#### `/ips_bloqueadas`
- **ETA:** 2-3 horas
- **Descripción:** Lista todas las IPs actualmente bloqueadas
- **Uso:** `/ips_bloqueadas`
- **Muestra:** Tabla con IP, Usuario, Intentos, Fecha de bloqueo
- **Opciones:** 
  - `/ips_bloqueadas hoy` - Solo bloqueadas hoy
  - `/ips_bloqueadas semana` - Últimos 7 días

#### `/ips_sospechosas`
- **ETA:** 2 horas
- **Descripción:** IPs con 3-4 intentos fallidos (aún no bloqueadas)
- **Uso:** `/ips_sospechosas`
- **Muestra:** IPs en "zona de peligro"

#### `/limpiar_logs [días]`
- **ETA:** 3-4 horas
- **Descripción:** Elimina logs antiguos para liberar espacio
- **Uso:** `/limpiar_logs 30` (elimina logs >30 días)
- **Seguridad:** Requiere confirmación antes de eliminar
- **Backup:** Crea backup antes de eliminar

#### `/alertas [on|off]`
- **ETA:** 2 horas
- **Descripción:** Activar/desactivar notificaciones de alertas
- **Uso:** `/alertas off` (modo silencioso temporalmente)
- **Nota:** Se reactivan automáticamente en 4 horas

---

### **NIVEL 2: Gestión de Usuarios** 👥 (Prioridad: MEDIA-ALTA)

#### `/usuarios_activos`
- **ETA:** 2-3 horas
- **Descripción:** Ver sesiones activas en este momento
- **Uso:** `/usuarios_activos`
- **Muestra:**
  - Usuario, NIT, IP, Módulo actual, Tiempo online
  - Total de usuarios conectados
  - Alertas si hay sesiones sospechosas

#### `/usuarios_pendientes`
- **ETA:** 3 horas
- **Descripción:** Solicitudes de registro pendientes de aprobación
- **Uso:** `/usuarios_pendientes`
- **Muestra:**
  - NIT, Razón Social, Radicado, Fecha solicitud
  - Total pendientes
  - Link directo para aprobar desde dashboard

#### `/activar_usuario [NIT]`
- **ETA:** 3-4 horas
- **Descripción:** Activar usuario pendiente directamente desde Telegram
- **Uso:** `/activar_usuario 900123456`
- **Acciones:**
  - Activa todos los usuarios asociados al NIT
  - Envía email de bienvenida automáticamente
  - Registra en auditoría

#### `/bloquear_usuario [NIT]`
- **ETA:** 3 horas
- **Descripción:** Desactivar usuario (opuesto a activar)
- **Uso:** `/bloquear_usuario 900123456 Documentación vencida`
- **Seguridad:** Requiere confirmación
- **Acciones:**
  - Desactiva todos los usuarios del NIT
  - Cierra sesiones activas
  - Envía notificación al usuario

#### `/reset_password [NIT]`
- **ETA:** 4-5 horas
- **Descripción:** Genera y envía token de recuperación de contraseña
- **Uso:** `/reset_password 900123456`
- **Acciones:**
  - Genera token de 6 dígitos
  - Envía por email + Telegram (si configurado)
  - Muestra token al admin por Telegram también

#### `/info_usuario [NIT]`
- **ETA:** 3 horas
- **Descripción:** Ver información completa de un usuario/tercero
- **Uso:** `/info_usuario 900123456`
- **Muestra:**
  - Datos del tercero (razón social, email, teléfono)
  - Usuarios asociados (cuántos, activos/inactivos)
  - Última conexión
  - Módulos a los que tiene acceso
  - Estadísticas (facturas recibidas, relaciones generadas)

#### `/radicados_hoy`
- **ETA:** 2 horas
- **Descripción:** Radicados generados en el día actual
- **Uso:** `/radicados_hoy`
- **Muestra:** Lista de radicados con NIT y hora

---

### **NIVEL 3: Monitoreo de Facturas** 📄 (Prioridad: MEDIA)

#### `/facturas_hoy`
- **ETA:** 3 horas
- **Descripción:** Facturas recibidas en el día
- **Uso:** `/facturas_hoy`
- **Muestra:**
  - Total de facturas
  - Valor total
  - Proveedores únicos
  - Top 5 proveedores por monto

#### `/relaciones_pendientes`
- **ETA:** 3 horas
- **Descripción:** Relaciones generadas pero no recibidas digitalmente
- **Uso:** `/relaciones_pendientes`
- **Muestra:** Número de relación, proveedor, fecha, facturas

#### `/facturas_proveedor [NIT]`
- **ETA:** 3-4 horas
- **Descripción:** Facturas de un proveedor específico
- **Uso:** `/facturas_proveedor 900123456`
- **Opciones:**
  - `/facturas_proveedor 900123456 mes` - Solo del mes actual
  - `/facturas_proveedor 900123456 pendientes` - Pendientes de recibir

#### `/alertas_vencimiento`
- **ETA:** 4-5 horas
- **Descripción:** Facturas próximas a vencer (fecha de pago)
- **Uso:** `/alertas_vencimiento`
- **Configuración:** Alertas automáticas diarias a las 08:00 AM

#### `/estadisticas_mes`
- **ETA:** 4 horas
- **Descripción:** Resumen estadístico del mes actual
- **Uso:** `/estadisticas_mes`
- **Muestra:**
  - Total facturas recibidas
  - Total relaciones generadas
  - Proveedores activos
  - Valor total facturado
  - Gráfico de tendencia (imagen PNG)

---

### **NIVEL 4: Sistema DIAN** 🏛️ (Prioridad: BAJA-MEDIA)

#### `/dian_procesar`
- **ETA:** 5-6 horas
- **Descripción:** Forzar procesamiento de archivos DIAN vs ERP
- **Uso:** `/dian_procesar`
- **Acciones:**
  - Inicia procesamiento inmediato
  - Muestra barra de progreso en tiempo real
  - Notifica cuando termine

#### `/dian_errores`
- **ETA:** 3 horas
- **Descripción:** Ver errores recientes del módulo DIAN
- **Uso:** `/dian_errores`
- **Muestra:** Últimos 20 errores con timestamp y descripción

#### `/dian_pendientes`
- **ETA:** 3 horas
- **Descripción:** Acuses pendientes de actualizar
- **Uso:** `/dian_pendientes`
- **Muestra:** Cantidad y detalle de acuses no procesados

#### `/dian_stats`
- **ETA:** 4 horas
- **Descripción:** Estadísticas completas del sistema DIAN
- **Uso:** `/dian_stats`
- **Muestra:**
  - Total registros DIAN
  - Total registros ERP
  - Diferencias encontradas
  - Porcentaje de coincidencia

---

### **NIVEL 5: Base de Datos y Backups** 💾 (Prioridad: ALTA)

#### `/backup_ahora`
- **ETA:** 4-5 horas
- **Descripción:** Crear backup manual de la base de datos
- **Uso:** `/backup_ahora`
- **Acciones:**
  - Crea backup PostgreSQL
  - Comprime en .zip
  - Muestra tamaño y ubicación
  - Tiempo estimado de creación

#### `/backup_ultimo`
- **ETA:** 2 horas
- **Descripción:** Información del último backup realizado
- **Uso:** `/backup_ultimo`
- **Muestra:**
  - Fecha y hora del backup
  - Tamaño del archivo
  - Ubicación
  - Éxito/error

#### `/espacio_disco`
- **ETA:** 2 horas
- **Descripción:** Espacio en disco del servidor
- **Uso:** `/espacio_disco`
- **Muestra:**
  - Total disponible
  - Usado
  - Libre
  - Porcentaje de uso
  - Alerta si <10% libre

#### `/salud_bd`
- **ETA:** 3-4 horas
- **Descripción:** Estado de salud de PostgreSQL
- **Uso:** `/salud_bd`
- **Muestra:**
  - Estado del servidor (running/stopped)
  - Conexiones activas
  - Queries lentas
  - Uso de memoria

#### `/tablas_tamaño`
- **ETA:** 3 horas
- **Descripción:** Tamaño de las tablas principales
- **Uso:** `/tablas_tamaño`
- **Muestra:** Top 20 tablas más grandes con tamaño en MB

---

### **NIVEL 6: Administración Avanzada** ⚙️ (Prioridad: BAJA)

#### `/restart_app`
- **ETA:** 4-5 horas
- **Descripción:** Reiniciar aplicación Flask
- **Uso:** `/restart_app`
- **Seguridad:** Requiere doble confirmación
- **Advertencia:** Cierra todas las sesiones activas

#### `/logs [modulo]`
- **ETA:** 4 horas
- **Descripción:** Ver últimos logs de un módulo
- **Uso:** 
  - `/logs security` - Logs de seguridad
  - `/logs error` - Errores de aplicación
  - `/logs app` - Log general
- **Muestra:** Últimas 50 líneas

#### `/permisos_usuario [NIT]`
- **ETA:** 3 horas
- **Descripción:** Ver permisos de un usuario
- **Uso:** `/permisos_usuario 900123456`
- **Muestra:** Lista de módulos y acciones permitidas

#### `/sesiones_forzar_logout`
- **ETA:** 3-4 horas
- **Descripción:** Cerrar todas las sesiones activas (emergencia)
- **Uso:** `/sesiones_forzar_logout`
- **Seguridad:** Requiere confirmación con código
- **Uso:** Mantenimiento o seguridad comprometida

#### `/config [variable]`
- **ETA:** 3 horas
- **Descripción:** Ver valor de una variable de configuración
- **Uso:** `/config MAIL_SERVER`
- **Seguridad:** NO muestra passwords ni tokens

#### `/licencia`
- **ETA:** 2 horas
- **Descripción:** Estado de la licencia del sistema
- **Uso:** `/licencia`
- **Muestra:**
  - Días restantes de evaluación
  - Estado (activo/vencido)
  - Información del servidor

---

### **NIVEL 7: Reportes y Analíticas** 📊 (Prioridad: MEDIA)

#### `/reporte_diario`
- **ETA:** 5-6 horas
- **Descripción:** Resumen automático del día
- **Uso:** `/reporte_diario`
- **Configuración:** Puede enviarse automáticamente a las 18:00
- **Muestra:**
  - Usuarios conectados hoy
  - Facturas recibidas
  - Relaciones generadas
  - Errores detectados
  - IPs bloqueadas

#### `/reporte_semanal`
- **ETA:** 6-8 horas
- **Descripción:** Resumen semanal completo (PDF)
- **Uso:** `/reporte_semanal`
- **Configuración:** Auto-envío los lunes 08:00 AM
- **Formato:** PDF profesional con gráficos

#### `/top_proveedores`
- **ETA:** 4 horas
- **Descripción:** Top 10 proveedores por número de facturas
- **Uso:** `/top_proveedores`
- **Opciones:**
  - `/top_proveedores mes` - Solo del mes
  - `/top_proveedores monto` - Ordenar por valor total

#### `/actividad_reciente`
- **ETA:** 3 horas
- **Descripción:** Últimas 20 acciones del sistema
- **Uso:** `/actividad_reciente`
- **Muestra:** Log en tiempo real de acciones importantes

#### `/graficos_mes`
- **ETA:** 6-8 horas
- **Descripción:** Gráficos estadísticos del mes actual
- **Uso:** `/graficos_mes`
- **Envía:** Imagen PNG con:
  - Tendencia de facturas diarias
  - Top proveedores (gráfico de barras)
  - Distribución por módulo

---

### **NIVEL 8: Integraciones** 🔗 (Prioridad: BAJA)

#### `/email_test [destino]`
- **ETA:** 2 horas
- **Descripción:** Probar envío de correo electrónico
- **Uso:** `/email_test correo@example.com`
- **Resultado:** Éxito/error con detalles técnicos

#### `/telegram_test`
- **ETA:** 1 hora
- **Descripción:** Probar conectividad de Telegram
- **Uso:** `/telegram_test`
- **Resultado:** Estado de la API, latencia, límites restantes

#### `/adobe_status`
- **ETA:** 3 horas
- **Descripción:** Estado de integración con Adobe Sign
- **Uso:** `/adobe_status`
- **Muestra:**
  - Token válido/expirado
  - Acuerdos pendientes
  - Límite de API usado

#### `/zimbra_status`
- **ETA:** 3 horas
- **Descripción:** Estado del servidor de correo Zimbra
- **Uso:** `/zimbra_status`
- **Muestra:** Conexión OK/error, últimos correos enviados

---

## 🎯 ROADMAP DE IMPLEMENTACIÓN

### **FASE 1 - Seguridad Básica** (2-3 días)
- ✅ /desbloquear ✅ **COMPLETADO**
- ✅ /ayuda ✅ **COMPLETADO**
- ⏳ /bloquear
- ⏳ /whois
- ⏳ /ips_bloqueadas
- ⏳ /ips_sospechosas

### **FASE 2 - Gestión de Usuarios** (3-4 días)
- ⏳ /usuarios_activos
- ⏳ /usuarios_pendientes
- ⏳ /activar_usuario
- ⏳ /info_usuario

### **FASE 3 - Monitoreo de Sistema** (2-3 días)
- ⏳ /backup_ahora
- ⏳ /espacio_disco
- ⏳ /salud_bd
- ⏳ /licencia

### **FASE 4 - Facturas y Negocio** (4-5 días)
- ⏳ /facturas_hoy
- ⏳ /relaciones_pendientes
- ⏳ /estadisticas_mes

### **FASE 5 - Reportería** (5-7 días)
- ⏳ /reporte_diario
- ⏳ /reporte_semanal
- ⏳ /graficos_mes

### **FASE 6 - Integraciones y Avanzado** (3-4 días)
- ⏳ /dian_procesar
- ⏳ /logs
- ⏳ /restart_app

---

## 📝 NOTAS DE DESARROLLO

### Consideraciones Técnicas:
- Todos los comandos requieren autenticación con TELEGRAM_CHAT_ID
- Los comandos críticos (restart, sesiones_logout) requieren confirmación doble
- Límite de mensajes de Telegram: 30 mensajes/segundo (gestionar rate limiting)
- Mensajes >4096 caracteres se dividen automáticamente

### Seguridad:
- Log de todos los comandos ejecutados (quién, cuándo, resultado)
- Alertas de comandos críticos al admin secundario
- Timeout de 5 minutos si no hay confirmación en comandos peligrosos

### Performance:
- Caché de resultados para comandos frecuentes (5 minutos)
- Queries optimizadas para comandos pesados (/estadisticas_mes)
- Procesamiento asíncrono para comandos lentos (/backup_ahora)

---

## 🔮 FUTURO (v2.0+)

### Comandos con IA:
- `/analizar_fraude [factura_id]` - Detectar facturas sospechosas con ML
- `/predecir_consumo` - Predecir consumo del próximo mes
- `/chatbot [pregunta]` - Bot conversacional para consultas complejas

### Dashboard Interactivo:
- Envío de gráficos interactivos (links a Plotly)
- Reportes personalizables con botones inline
- Menú de navegación con callbacks

### Automatización:
- Alertas proactivas configurables
- Workflows automáticos (si X entonces Y)
- Integración con calendarios (Google Calendar)

---

**Última actualización:** 27 Febrero 2026  
**Versión actual:** 1.0 (Comando /desbloquear implementado)  
**Total de comandos propuestos:** 45+  
**Tiempo estimado implementación completa:** 60-80 horas
