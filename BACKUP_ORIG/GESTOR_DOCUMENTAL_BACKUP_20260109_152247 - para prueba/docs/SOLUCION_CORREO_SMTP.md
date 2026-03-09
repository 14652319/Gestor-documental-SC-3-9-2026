# 🔧 SOLUCIÓN TÉCNICA: Error de Envío de Correos
**Problema:** Recuperación de contraseña no envía correos  
**Estado:** ✅ RESUELTO  
**Fecha:** 14 de Noviembre 2025

---

## 🚨 DESCRIPCIÓN DEL PROBLEMA

### Síntoma
Al solicitar recuperación de contraseña desde el formulario web:
- ✅ Sistema muestra mensaje: "Código de verificación enviado"
- ❌ El correo **nunca llega** a la bandeja del usuario
- ❌ No aparece en SPAM ni en correo no deseado

### Impacto
- Los usuarios no pueden recuperar sus contraseñas
- El sistema queda parcialmente inoperativo
- Dependencia de administrador para resetear contraseñas manualmente

---

## 🔍 DIAGNÓSTICO REALIZADO

### 1. Verificación de Configuración
**Archivo revisado:** `.env`

```properties
# Configuración inicial (NO FUNCIONABA)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=gestordocumentalsc01@gmail.com
MAIL_PASSWORD=urjrkjlogcfdtynq  # Contraseña de aplicación válida
```

**Resultado:** ✅ Configuración correcta

### 2. Test de Conexión SMTP (Puerto 587)
**Script ejecutado:** `test_smtp_directo.py`

```python
server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
```

**Resultado:** ❌ TIMEOUT

```
❌ ERROR INESPERADO:
   timed out
   Tipo: TimeoutError

Traceback:
  File "smtplib.py", line 255, in __init__
    (code, msg) = self.connect(host, port)
  File "smtplib.py", line 341, in connect
    self.sock = self._get_socket(host, port, self.timeout)
  File "socket.py", line 851, in create_connection
    raise exceptions[0]
TimeoutError: timed out
```

**Conclusión:** El puerto 587 está **BLOQUEADO** por:
- Firewall de Windows
- Antivirus corporativo
- Restricciones de red del ISP
- Configuración de router/switch

### 3. Test de Puerto Alternativo (465/SSL)
**Script ejecutado:** `test_smtp_465.py`

```python
server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
server.login(username, password)
```

**Resultado:** ✅ EXITOSO

```
✅ Conexión SSL establecida
✅ Autenticación exitosa
✅ CORREO ENVIADO EXITOSAMENTE
```

---

## ✅ SOLUCIÓN IMPLEMENTADA

### Cambio 1: Modificar `.env`

**Antes:**
```properties
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

**Después:**
```properties
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
```

### Cambio 2: Configuración de Flask
**Archivo:** `app.py` (líneas 34-36)

El código ya soportaba SSL, solo necesitaba actualizar variables de entorno:

```python
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
```

**Nota:** Flask-Mail automáticamente usa `SMTP_SSL` cuando `MAIL_USE_SSL=True`

### Cambio 3: Reinicio del Servidor
```powershell
# Detener servidor (Ctrl+C)
# Reiniciar para cargar nueva configuración
python app.py
```

---

## 📊 COMPARACIÓN DE PROTOCOLOS

| Característica | Puerto 587 (TLS) | Puerto 465 (SSL) |
|----------------|------------------|------------------|
| **Protocolo** | STARTTLS | SSL/TLS directo |
| **Seguridad** | Alta | Alta |
| **Estado** | ❌ Bloqueado | ✅ Funcional |
| **Compatibilidad** | Mayor | Estándar |
| **Uso** | Más común | Gmail preferido |

### Flujo de Conexión

**Puerto 587 (TLS):**
```
1. Conectar en texto plano → smtp.gmail.com:587
2. Enviar comando STARTTLS
3. Negociar cifrado TLS
4. Autenticar
5. Enviar correo
```

**Puerto 465 (SSL):**
```
1. Conectar con SSL → smtp.gmail.com:465
2. Conexión ya cifrada desde el inicio
3. Autenticar
4. Enviar correo
```

---

## 🧪 PRUEBAS DE VERIFICACIÓN

### Test 1: Conexión Básica
```powershell
python test_smtp_465.py
```

**Resultado esperado:**
```
✅ Conexión SSL establecida
✅ Autenticación exitosa
✅ CORREO ENVIADO EXITOSAMENTE
```

### Test 2: Recuperación de Contraseña
1. Ir a: http://127.0.0.1:8099/recuperar
2. Ingresar:
   - NIT: 805028041
   - Usuario: admin
   - Correo: (cualquier correo válido)
3. Click en "Enviar código"

**Resultado esperado:**
- ✅ Mensaje: "Código de verificación enviado por correo electrónico"
- ✅ Correo recibido en bandeja de entrada (o SPAM)

### Test 3: Logs del Servidor
Verificar en consola del servidor:

```
INFO:security:TOKEN RECUPERACION ENVIADO POR CORREO | destinatario=xxx@xxx.com | usuario=admin | nit=805028041
```

---

## 🔒 SEGURIDAD

### Gmail - Contraseña de Aplicación
La contraseña utilizada es una **"Contraseña de aplicación"** de Gmail:
- ✅ No es la contraseña real de la cuenta
- ✅ Puede ser revocada sin afectar la cuenta principal
- ✅ Tiene permisos específicos solo para SMTP

**Generar nueva contraseña de aplicación:**
1. Ir a: https://myaccount.google.com/security
2. "Verificación en 2 pasos" → "Contraseñas de aplicaciones"
3. Seleccionar "Correo" y "Otro dispositivo personalizado"
4. Copiar la contraseña de 16 caracteres generada
5. Actualizar en `.env` → `MAIL_PASSWORD`

### Encriptación
- ✅ **SSL/TLS**: Todo el tráfico cifrado
- ✅ **Puerto 465**: Conexión segura desde el inicio
- ✅ **Autenticación**: OAuth2 compatible (usando app password)

---

## 📝 NOTAS ADICIONALES

### Por qué el puerto 587 está bloqueado

**Razones comunes:**
1. **Firewall corporativo**: Bloquea SMTP saliente para prevenir spam
2. **ISP**: Algunos proveedores bloquean 587 por política
3. **Antivirus**: Software de seguridad puede bloquear conexiones SMTP
4. **Configuración de red**: Router o switch con reglas restrictivas

### Ventajas del puerto 465

1. **Más difícil de bloquear**: Al ser SSL desde el inicio
2. **Mayor compatibilidad**: Con firewalls modernos
3. **Más rápido**: No requiere negociación STARTTLS
4. **Preferido por Gmail**: Recomendado oficialmente

### Desventajas del puerto 465

1. **Menos común**: Algunos servicios solo soportan 587
2. **Legacy support**: Técnicamente "deprecado" pero ampliamente usado
3. **Configuración**: Algunos frameworks no lo soportan bien (Flask-Mail sí)

---

## 🎯 LECCIONES APRENDIDAS

### 1. Siempre tener plan B
- ✅ Probar múltiples puertos SMTP (25, 587, 465)
- ✅ Tener scripts de diagnóstico preparados

### 2. Diagnóstico antes de modificar código
- ✅ El código de Flask estaba correcto
- ✅ El problema era de infraestructura de red

### 3. Logs mejorados
- ✅ Añadido mensaje visible cuando falla envío
- ✅ Token mostrado en consola como fallback

### 4. Documentación
- ✅ Crear guías de solución de problemas
- ✅ Mantener historial de cambios

---

## 🔄 PROCEDIMIENTO DE ROLLBACK

Si necesitas volver al puerto 587 (si se habilita en el firewall):

### 1. Modificar `.env`
```properties
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

### 2. Probar conexión
```powershell
python test_smtp_directo.py
```

### 3. Si funciona, reiniciar servidor
```powershell
python app.py
```

---

## 📚 REFERENCIAS

- **Gmail SMTP:** https://support.google.com/mail/answer/7126229
- **Flask-Mail:** https://pythonhosted.org/Flask-Mail/
- **SMTP RFC:** RFC 5321 (Simple Mail Transfer Protocol)
- **TLS/SSL:** RFC 8314 (Secure SMTP)

---

## ✅ ESTADO FINAL

| Componente | Estado | Notas |
|------------|--------|-------|
| **Conexión SMTP** | ✅ Funcional | Puerto 465/SSL |
| **Autenticación** | ✅ Funcional | App Password válido |
| **Envío de correo** | ✅ Funcional | Probado exitosamente |
| **Recuperación de contraseña** | ✅ Funcional | End-to-end verificado |
| **Logs** | ✅ Mejorados | Mensajes claros |

---

**Problema:** RESUELTO ✅  
**Tiempo de diagnóstico:** ~45 minutos  
**Tiempo de implementación:** ~10 minutos  
**Última prueba exitosa:** 14/11/2025
