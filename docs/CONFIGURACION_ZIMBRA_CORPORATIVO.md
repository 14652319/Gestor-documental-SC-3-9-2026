# Configuración de Correo Corporativo Zimbra

## 📋 Información Necesaria de Servi Unix

Para usar el correo corporativo `rriascos@supertiendascanaveral.com` necesitas obtener de **Servi Unix** (tu proveedor de hosting) los siguientes datos:

### 1. Servidor SMTP
```
Puede ser algo como:
- smtp.supertiendascanaveral.com
- mail.supertiendascanaveral.com
- zimbra.servi-unix.com
- O una IP: 192.168.x.x
```

### 2. Puerto SMTP
```
Común en Zimbra:
- Puerto 587 (TLS) - RECOMENDADO
- Puerto 465 (SSL)
- Puerto 25 (sin cifrado - NO recomendado)
```

### 3. Tipo de Cifrado
```
- TLS (STARTTLS) - Más común
- SSL
```

### 4. Credenciales
```
Usuario: rriascos@supertiendascanaveral.com (o solo "rriascos")
Contraseña: La contraseña del correo
```

---

## 🔧 Configuración en .env

Una vez tengas esos datos de Servi Unix, actualiza el archivo `.env`:

```env
# Zimbra Corporativo - Supertiendas Cañaveral
MAIL_SERVER=smtp.supertiendascanaveral.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=rriascos@supertiendascanaveral.com
MAIL_PASSWORD=ContraseñaDelCorreo
MAIL_DEFAULT_SENDER=rriascos@supertiendascanaveral.com
```

### Variantes según configuración:

#### Si usa SSL en puerto 465:
```env
MAIL_SERVER=smtp.supertiendascanaveral.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=rriascos@supertiendascanaveral.com
MAIL_PASSWORD=ContraseñaDelCorreo
MAIL_DEFAULT_SENDER=rriascos@supertiendascanaveral.com
```

#### Si el usuario es solo el nombre (sin @dominio):
```env
MAIL_USERNAME=rriascos
MAIL_DEFAULT_SENDER=rriascos@supertiendascanaveral.com
```

---

## 📧 Correo que NO Acepta Respuestas

Para que el correo **solo envíe y no reciba respuestas**, tienes 2 opciones:

### ✅ Opción 1: Crear un correo específico (RECOMENDADO)

Pide a Servi Unix crear un correo dedicado:
```
noreply@supertiendascanaveral.com
o
notificaciones@supertiendascanaveral.com
o
gestordocumental@supertiendascanaveral.com
```

**Ventajas:**
- Más profesional
- No mezcla notificaciones automáticas con correo personal
- Puedes configurar respuesta automática explicando que es solo envío
- Separa logs y seguimiento

**Configuración:**
```env
MAIL_USERNAME=noreply@supertiendascanaveral.com
MAIL_PASSWORD=ContraseñaDelCorreo
MAIL_DEFAULT_SENDER=noreply@supertiendascanaveral.com
```

### ✅ Opción 2: Usar correo existente con Reply-To

Si no puedes crear un correo nuevo, usas el actual pero modificas el código para que las respuestas vayan a otro lado (o ninguno):

```python
# En la función enviar_correo_confirmacion_radicado() de app.py
msg = Message(
    subject=f"Confirmación de Registro - Radicado {radicado}",
    recipients=[destinatario],
    sender=current_app.config['MAIL_DEFAULT_SENDER'],
    reply_to="noreply@supertiendascanaveral.com"  # ← AGREGAR ESTO
)
```

---

## 🔍 Cómo Obtener la Información de Servi Unix

### Método 1: Contactar a Soporte
```
Solicita a Servi Unix:
"Necesito la configuración SMTP para envío automático de correos 
desde la aplicación Gestor Documental usando el correo 
rriascos@supertiendascanaveral.com"

Específicamente necesito:
1. Servidor SMTP (hostname o IP)
2. Puerto SMTP (587, 465, o 25)
3. Tipo de cifrado (TLS o SSL)
4. Formato del usuario (correo completo o solo nombre)
```

### Método 2: Revisar Webmail de Zimbra
```
1. Entra al webmail: https://mail.supertiendascanaveral.com
2. Ve a: Preferencias > Cuentas > Configuración de correo
3. Busca la sección "Servidor saliente (SMTP)"
```

### Método 3: Revisar en Outlook/Thunderbird
```
Si ya tienes configurado el correo en un cliente:
- Outlook: Archivo > Configuración de cuenta > Ver detalles
- Thunderbird: Herramientas > Configuración de cuentas
```

---

## 🧪 Prueba Rápida

Una vez configurado el `.env`, prueba:

```cmd
python test_envio_correo.py
```

**Si falla**, revisa los logs para identificar el problema:
```
❌ Error común 1: "Connection refused" → Puerto o servidor incorrecto
❌ Error común 2: "Authentication failed" → Usuario o contraseña incorrectos
❌ Error común 3: "TLS error" → Cambiar de TLS a SSL o viceversa
```

---

## 📊 Comparación: Gmail vs Zimbra Corporativo

| Característica | Gmail | Zimbra Corporativo |
|----------------|-------|-------------------|
| **Profesionalismo** | ⚠️ Medio | ✅ Alto (@supertiendascanaveral.com) |
| **Límites de envío** | 500/día | Depende de plan (generalmente mayor) |
| **Configuración** | Requiere 2FA + App Password | Directo con contraseña |
| **Costo** | Gratis | Ya incluido en hosting |
| **Control** | ❌ Google | ✅ Tu empresa |
| **Logs/Auditoría** | ❌ Limitado | ✅ Completo (Servi Unix) |

---

## 💡 Recomendación Final

### Para Producción (IDEAL):
```
Crear: noreply@supertiendascanaveral.com
Configurar: Respuesta automática en Zimbra explicando que no se monitorea
Usar: Para todas las notificaciones del sistema
```

### Configuración Provisional (Mientras tanto):
```
Usar: rriascos@supertiendascanaveral.com
Agregar: reply_to="noreply@supertiendascanaveral.com" en el código
```

---

## 📞 Próximo Paso

**Contacta a Servi Unix y solicita:**

1. ✅ Configuración SMTP del servidor Zimbra
2. ✅ (OPCIONAL pero RECOMENDADO) Crear correo: `noreply@supertiendascanaveral.com`
3. ✅ (OPCIONAL) Configurar respuesta automática en ese correo

**Cuando tengas esa información, actualiza el `.env` y prueba con:**
```cmd
python test_envio_correo.py
```

---

## 🔒 Seguridad Adicional

Si Servi Unix lo soporta, considera:

### IP Whitelisting
```
Configura en Zimbra que solo tu servidor pueda enviar correos
desde esa cuenta (evita uso no autorizado)
```

### SPF/DKIM/DMARC
```
Pide a Servi Unix configurar registros DNS para evitar que
los correos caigan en SPAM:
- SPF: Autoriza servidores para enviar correo
- DKIM: Firma digital en correos
- DMARC: Política de validación
```

Esto mejorará significativamente la **tasa de entrega** de los correos.
