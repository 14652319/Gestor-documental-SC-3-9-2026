# 🤖 Bot de Telegram - Guía Rápida de Uso

## ✅ ¿Qué está Implementado?

**Comando disponible AHORA:**
- 🔓 `/desbloquear [IP]` - Desbloquear IPs bloqueadas por intentos fallidos

**Funciones automáticas activas:**
- 🚨 **Alertas de IP bloqueada** (cuando se bloquea automáticamente)
  - ✅ Detalles de la IP bloqueada
  - ✅ Usuario que intentó ingresar
  - ✅ **LISTADO COMPLETO de todas las IPs bloqueadas** (nuevo!)
  - ✅ Sugerencia de comando `/desbloquear`
- 🚨 Alertas de intentos fallidos (3-4 intentos)
- 🔑 Envío de tokens de recuperación de contraseña

---

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Probar el bot
```bash
python test_bot_telegram.py
```
Verifica que el bot esté configurado y funciona.

### 2️⃣ Abrir Telegram
- Abre el chat con tu bot
- Verás un mensaje de activación
- Usa `/ayuda` para ver comandos

### 3️⃣ Usar comandos
```
/desbloquear 192.168.1.100
```

---

## 📋 Flujo de Uso Real

### Escenario: Usuario bloqueado por intentos fallidos

**1. Recibes alerta automática:**
```
🚨 ALERTA: IP BLOQUEADA

📅 Fecha: 2026-02-27 15:30:45
🌐 IP: 192.168.1.100
👤 Usuario: juanperez
🏢 NIT: 900123456
🔢 Intentos: 5
📋 Motivo: Exceso de intentos fallidos de login

🚫 TODAS LAS IPS BLOQUEADAS ACTUALMENTE:
Total: 5 IP(s)

1. 192.168.1.100 - Exceso de intentos fallidos
2. 10.0.0.50 - Brute-force
3. 172.16.0.25 - Intentos fallidos
4. 192.168.2.15 - Brute-force
5. 10.10.10.10 - Exceso de intentos fallidos

💡 Para desbloquear: /desbloquear [IP]
```

**2. Respondes en el mismo chat:**
```
/desbloquear 192.168.1.100
```

**3. Bot confirma:**
```
✅ IP DESBLOQUEADA EXITOSAMENTE

🌐 IP: 192.168.1.100
📅 Fecha: 2026-02-27 15:31:00

🔓 Acciones realizadas:
✅ Eliminada de lista negra (1 registros)
✅ Eliminada de IPs sospechosas (1 registros)
✅ Agregada a lista blanca

🎯 La IP ahora tiene acceso completo al sistema
```

**4. Usuario puede ingresar nuevamente ✅**

---

## 🛠️ Scripts Disponibles

### Desbloqueo desde consola
```bash
# Forma 1: Interactivo
python desbloquear_ip_telegram.py

# Forma 2: Directo con argumento
python desbloquear_ip_telegram.py 192.168.1.100

# Forma 3: Sin Telegram (directo a BD)
python desbloquear_ip_directo.py
```

### Ver IPs bloqueadas actuales
```bash
python ver_ips_bloqueadas.py
```
Muestra todas las IPs bloqueadas sin esperar a que se bloquee una nueva.

### Test completo
```bash
python test_bot_telegram.py
```

### Probar alerta de IP bloqueada con listado (nuevo!)
```bash
python test_alerta_ip_bloqueada.py
```
Simula el bloqueo de una IP y envía el mensaje completo con listado de IPs bloqueadas.

### Configurar comandos del bot
```bash
python -c "from telegram_bot import configurar_comandos_bot; configurar_comandos_bot()"
```

---

## 🔧 Configuración (ya hecha en su sistema)

```env
# .env (ya configurado)
TELEGRAM_BOT_TOKEN=8132808615:AAFU-StA-ujNN-5bm_5UQLW_IHXuFEwcW38
TELEGRAM_CHAT_ID=7602447172
```

✅ **No necesitas hacer nada**, el bot ya está configurado.

---

## 📱 Comandos Disponibles (v1.0)

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/desbloquear [IP]` | Desbloquea una IP | `/desbloquear 192.168.1.100` |
| `/ayuda` | Muestra ayuda | `/ayuda` |

---

## 🔮 Próximos Comandos (en desarrollo)

Ver **TELEGRAM_BOT_ROADMAP.md** para el roadmap completo (45+ comandos planeados).

**Próximos a implementar:**
- `/bloquear [IP]` - Bloquear IP manualmente
- `/whois [IP]` - Ver información de una IP
- `/ips_bloqueadas` - Listar IPs bloqueadas
- `/usuarios_activos` - Ver sesiones activas
- `/backup_ahora` - Crear backup manual
- `/radicados_hoy` - Radicados del día
- `/facturas_hoy` - Facturas recibidas hoy

**Tiempo estimado implementación completa:** 60-80 horas

---

## ⚙️ Webhooks (Opcional - Solo Producción)

El bot funciona **sin webhooks** en desarrollo local. Los comandos se ejecutan directamente.

**Para producción con dominio público:**

```bash
# Configurar webhook
curl -X POST https://api.telegram.org/bot<TU_TOKEN>/setWebhook \
     -d "url=https://tudominio.com/api/telegram/webhook"

# O desde la app:
POST http://localhost:8099/api/telegram/setup_webhook
Body: {"webhook_url": "https://tudominio.com/api/telegram/webhook"}
```

⚠️ **Requiere:** HTTPS público, no funciona con HTTP o localhost.

---

## 🐛 Troubleshooting

### "Bot no responde"
**Solución:**
1. Verifica configuración:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'Token: {os.getenv(\"TELEGRAM_BOT_TOKEN\")[:20]}...')print(f'Chat: {os.getenv(\"TELEGRAM_CHAT_ID\")}')"
   ```

2. Prueba el test:
   ```bash
   python test_bot_telegram.py
   ```

### "Error enviando mensaje"
**Causas:**
- Token incorrecto
- Chat ID incorrecto
- Bot bloqueado por el usuario
- Sin internet

**Solución:** Verifica .env y prueba con:
```bash
python -c "from telegram_bot import enviar_mensaje_telegram; enviar_mensaje_telegram('Test')"
```

### "IP no se desbloquea"
**Usa el script directo:**
```bash
python desbloquear_ip_directo.py
```
Este script trabaja directo con la base de datos sin usar Telegram.

---

## 📊 Logs y Auditoría

Todos los comandos se registran en:
```
logs/security.log
```

Buscar comandos ejecutados:
```bash
type logs\security.log | findstr "TELEGRAM"
```

Registros de desbloqueo:
```bash
type logs\security.log | findstr "DESBLOQUEADA"
```

---

## 🎯 Casos de Uso

### 1. Usuario olvidó su contraseña (automático)
Sistema envía token por Telegram automáticamente. No requiere comando.

### 2. IP bloqueada por error
Usar `/desbloquear [IP]` para restaurar acceso inmediatamente.

### 3. Monitoreo de seguridad (automático)
Recibes alertas cuando hay:
- 3+ intentos fallidos (advertencia)
- 5+ intentos fallidos (bloqueo automático)

### 4. Gestión remota
Desde cualquier lugar con Telegram:
- Desbloquear IPs
- (Futuro) Ver usuarios activos
- (Futuro) Crear backups
- (Futuro) Ver estadísticas

---

## 📚 Documentación Adicional

- **TELEGRAM_BOT_ROADMAP.md** - Roadmap completo de comandos futuros
- **SISTEMA_BLOQUEO_IPS_CON_INFORMES.md** - ⭐ Documentación del sistema de informes de IPs bloqueadas
- **telegram_bot.py** - Código fuente del bot
- **test_bot_telegram.py** - Script de pruebas
- **test_alerta_ip_bloqueada.py** - ⭐ Script de prueba de alertas con listado
- **.env.example** - Plantilla de configuración

---

## 🆕 Nueva Funcionalidad: Informe de IPs Bloqueadas

Cuando se bloquea una IP, ahora recibes:

✅ **Antes:** Solo detalles de la IP bloqueada  
✅ **Ahora:** Detalles + **listado completo** de todas las IPs bloqueadas

**Beneficios:**
- 📊 Visibilidad total de IPs bloqueadas
- 🎯 Identifica patrones de ataque
- ⚡ Acción inmediata con `/desbloquear`
- 🛡️ Mejor control de seguridad

**Límites:**
- Muestra hasta 10 IPs (evitar mensajes largos)
- Si hay más, indica "... y X IP(s) más"
- Incluye sugerencia de comando `/desbloquear`

Ver **SISTEMA_BLOQUEO_IPS_CON_INFORMES.md** para detalles completos.

---

## ✅ Verificación Rápida

```bash
# 1. Verificar configuración
python test_bot_telegram.py

# 2. Recibir mensaje en Telegram
# (Deberías ver: "🤖 BOT DE ADMINISTRACIÓN ACTIVADO")

# 3. Probar comando
# En Telegram: /ayuda

# 4. Ver comandos configurados
# En Telegram verás /desbloquear y /ayuda en el menú

# ✅ Si todo funciona, el bot está operativo
```

---

**Última actualización:** 27 Febrero 2026  
**Versión:** 1.1 (Informes de IPs bloqueadas)  
**Estado:** ✅ Operativo (comando /desbloquear + informes automáticos)
