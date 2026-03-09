# 📧 Configuración de Envío de Correos - Gestor Login Seguro

## 📋 Resumen

El sistema ahora envía automáticamente un correo de confirmación con el número de radicado cuando un proveedor completa su registro exitosamente.

---

## ✅ Funcionalidad Implementada

### ¿Qué hace?
Cuando un proveedor finaliza su registro:
1. Se genera el radicado (ej: RAD-000027)
2. Se guardan todos los datos en la base de datos
3. **AUTOMÁTICAMENTE** se envía un correo al email del proveedor con:
   - ✅ Número de radicado
   - 🏢 NIT y nombre de la empresa
   - 📋 Próximos pasos del proceso
   - 💡 Recordatorio de conservar el radicado

### Contenido del Correo
El correo tiene el mismo diseño visual que la pantalla de éxito:
- Icono de confirmación ✅
- Número de radicado destacado
- Información de la empresa
- Lista de próximos pasos
- Advertencia importante sobre conservar el radicado

---

## 🔧 Configuración Necesaria

### Paso 1: Crear archivo `.env`

Si no existe, copia el archivo `.env.example` a `.env`:

```cmd
copy .env.example .env
```

### Paso 2: Configurar Variables de Correo

Edita el archivo `.env` y configura las siguientes variables:

```bash
# Para Gmail
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_aplicacion
MAIL_DEFAULT_SENDER=tu_correo@gmail.com
```

---

## 📧 Configuración por Proveedor de Correo

### Gmail

1. **Habilitar verificación en 2 pasos:**
   - Ve a: https://myaccount.google.com/security
   - Activa la verificación en 2 pasos

2. **Generar contraseña de aplicación:**
   - Ve a: https://myaccount.google.com/apppasswords
   - Selecciona "Correo" y "Otro" (dispositivo personalizado)
   - Nombre: "Gestor Documental"
   - Copia la contraseña de 16 caracteres generada
   - Úsala en `MAIL_PASSWORD` (sin espacios)

3. **Variables en .env:**
   ```bash
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=gestordocumentalsc01@gmail.com
   MAIL_PASSWORD=abcd efgh ijkl mnop  # (sin espacios)
   MAIL_DEFAULT_SENDER=gestordocumentalsc01@gmail.com
   ```

### Outlook / Hotmail

```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@outlook.com
MAIL_PASSWORD=tu_contraseña_normal
MAIL_DEFAULT_SENDER=tu_correo@outlook.com
```

### Office 365 (Empresarial)

```bash
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_correo@empresa.com
MAIL_PASSWORD=tu_contraseña
MAIL_DEFAULT_SENDER=tu_correo@empresa.com
```

---

## 🧪 Pruebas

### 1. Sin Configuración de Correo
- El sistema funcionará normalmente
- El registro se completará exitosamente
- Se generará el radicado
- **No se enviará correo** (se registra advertencia en logs)
- El usuario ve el mensaje de éxito en pantalla

### 2. Con Configuración de Correo
- El sistema funcionará normalmente
- El registro se completará exitosamente
- Se generará el radicado
- **Se enviará correo automáticamente**
- Se registra en logs: `CORREO CONFIRMACIÓN ENVIADO`

### Verificar en Logs

Abre `logs/security.log` y busca:

```
CORREO ENVIADO | destinatario=correo@ejemplo.com | radicado=RAD-000027
```

O si hay error:

```
ERROR ENVÍO CORREO | destinatario=correo@ejemplo.com | error=...
ADVERTENCIA: Correo no configurado. No se envió notificación...
```

---

## 🔍 Código Implementado

### Ubicación de la Función
- **Archivo**: `app.py`
- **Función**: `enviar_correo_confirmacion_radicado()`
- **Líneas**: Aproximadamente 50-250 (después de `log_security`)

### Integración en el Endpoint
- **Endpoint**: `/api/registro/finalizar`
- **Acción**: Se llama automáticamente después del `db.session.commit()`
- **Parámetros**: destinatario, nit, razon_social, radicado

---

## ⚠️ Solución de Problemas

### Error: "Import flask_mail could not be resolved"
**Solución**: Instalar flask-mail
```cmd
pip install flask-mail
```

### Error: "Authentication failed" (Gmail)
**Causa**: Usando contraseña normal en vez de contraseña de aplicación
**Solución**: Generar contraseña de aplicación en https://myaccount.google.com/apppasswords

### Error: "SMTP connection failed"
**Posibles causas**:
1. Firewall bloqueando puerto 587
2. Servidor SMTP incorrecto
3. Puerto incorrecto

**Solución**: Verificar configuración de red y variables en `.env`

### Los correos van a Spam
**Solución**: 
1. Verificar que el dominio tenga registros SPF y DKIM configurados
2. Añadir el remitente a contactos
3. Usar un servidor SMTP empresarial (Office 365, SendGrid, etc.)

---

## 📝 Notas Importantes

1. **El correo es opcional**: Si no se configura, el sistema funciona igual pero sin enviar correos
2. **Los errores no afectan el registro**: Si falla el envío de correo, el registro se completa de todas formas
3. **Se registra todo en logs**: Tanto éxitos como fallos de envío quedan registrados
4. **HTML + Texto plano**: El correo incluye ambas versiones para compatibilidad

---

## 🚀 Próximas Mejoras

- [ ] Plantillas de correo personalizables
- [ ] Correo de notificación cuando se aprueba la solicitud
- [ ] Correo con credenciales de acceso
- [ ] Sistema de colas para envíos masivos
- [ ] Integración con servicios de correo profesionales (SendGrid, Mailgun)

---

**Fecha de implementación**: Octubre 15, 2025
**Documentado por**: Copilot AI Assistant
