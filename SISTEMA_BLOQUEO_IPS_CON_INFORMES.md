# 🚫 Sistema de Bloqueo de IPs con Informes Automáticos

## ✅ ¿Qué hace el sistema?

Cuando alguien intenta ingresar con contraseña incorrecta 5+ veces:

1. **Bloquea la IP automáticamente** 🚫
2. **Envía alerta por Telegram** con:
   - ✅ Detalles de la IP bloqueada
   - ✅ Usuario que intentó ingresar
   - ✅ **LISTADO COMPLETO de todas las IPs bloqueadas**
   - ✅ Sugerencia del comando `/desbloquear`

---

## 📱 Ejemplo de Mensaje que Recibirás

```
🚫 ALERTA DE SEGURIDAD

Tipo: IP BLOQUEADA
Fecha: 2026-02-27 15:30:45

IP: 192.168.1.100
Usuario: juanperez
NIT: 900123456
Intentos fallidos: 5
Motivo: Exceso de intentos fallidos de login
Navegador: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...

🚫 TODAS LAS IPS BLOQUEADAS ACTUALMENTE:
Total: 5 IP(s)

1. 192.168.1.100 - Exceso de intentos fallidos
2. 10.0.0.50 - Brute-force
3. 172.16.0.25 - Intentos fallidos
4. 192.168.2.15 - Brute-force
5. 10.10.10.10 - Exceso de intentos fallidos

💡 Para desbloquear: /desbloquear [IP]

---
📊 Sistema de Gestión Documental
```

---

## 🎯 Flujo Completo

### 1️⃣ Usuario intenta ingresar con contraseña incorrecta

```
Intento 1: ⚠️  Contraseña incorrecta
Intento 2: ⚠️  Contraseña incorrecta
Intento 3: 🚨 ALERTA: 3 intentos fallidos (se envía advertencia)
Intento 4: ⚠️  Contraseña incorrecta
Intento 5: 🚫 IP BLOQUEADA + Informe completo enviado
```

### 2️⃣ Recibes notificación en Telegram

- Detalles de la nueva IP bloqueada
- **LISTADO COMPLETO** de todas las IPs bloqueadas (hasta 10)
- Si hay más de 10, muestra "... y X IP(s) más"

### 3️⃣ Desbloqueas la IP

```
/desbloquear 192.168.1.100
```

Bot responde:
```
✅ IP DESBLOQUEADA EXITOSAMENTE

🌐 IP: 192.168.1.100
📅 Fecha: 2026-02-27 15:31:00

🔓 Acciones realizadas:
✅ Eliminada de lista negra
✅ Eliminada de IPs sospechosas
✅ Agregada a lista blanca

🎯 La IP ahora tiene acceso completo al sistema
```

---

## 🧪 Probar el Sistema

### Script de Prueba
```bash
python test_alerta_ip_bloqueada.py
```

**Qué hace:**
- ✅ Consulta IPs bloqueadas actuales
- ✅ Envía alerta de prueba a Telegram
- ✅ Muestra preview del mensaje
- ✅ Incluye listado de IPs bloqueadas

### Desbloquear IP de Prueba
```bash
python desbloquear_ip_telegram.py 192.168.1.100
```

### Ver IPs Bloqueadas Actuales
```bash
python ver_ips_bloqueadas.py
```
Muestra listado completo de todas las IPs bloqueadas en cualquier momento.

---

## 📊 Información en el Listado

Para cada IP bloqueada muestra:
- **IP:** Dirección bloqueada
- **Motivo:** Por qué fue bloqueada
  - "Exceso de intentos fallidos"
  - "Brute-force"
  - "Intentos fallidos"
  - Motivo personalizado

---

## ⚙️ Configuración Técnica

### Modificaciones en app.py

**Función:** `enviar_alerta_seguridad_telegram()` (líneas 914-1010)

**Nueva funcionalidad:**
```python
# Si es IP_BLOQUEADA, agregar listado
if tipo_alerta == 'IP_BLOQUEADA':
    # Consulta IPListaNegra + IPSospechosa bloqueadas
    # Combina y deduplica
    # Muestra hasta 10 IPs
    # Agrega comando /desbloquear al final
```

**Consultas de BD:**
- `IPListaNegra.query.all()` - IPs en lista negra
- `IPSospechosa.query.filter_by(bloqueada=True).all()` - IPs sospechosas bloqueadas

### Límites y Protecciones

- **Máximo 10 IPs** mostradas en el mensaje (evitar mensajes muy largos)
- **Deduplica IPs** (si está en ambas tablas, solo se muestra una vez)
- **No falla** si hay error al listar (envía alerta sin listado)
- **Timeout 5 segundos** para envío (no bloquea el login)

---

## 🔍 Casos de Uso

### Caso 1: Primera IP bloqueada
```
✅ Esta es la única IP bloqueada actualmente
```
No muestra listado porque es la primera.

### Caso 2: Múltiples IPs bloqueadas
```
🚫 TODAS LAS IPS BLOQUEADAS ACTUALMENTE:
Total: 3 IP(s)

1. 192.168.1.100 - Exceso de intentos fallidos
2. 10.0.0.50 - Brute-force
3. 172.16.0.25 - Intentos fallidos

💡 Para desbloquear: /desbloquear [IP]
```

### Caso 3: Más de 10 IPs bloqueadas
```
🚫 TODAS LAS IPS BLOQUEADAS ACTUALMENTE:
Total: 15 IP(s)

1. 192.168.1.100 - Exceso de intentos fallidos
... (IPs 2-9)
10. 10.10.10.10 - Brute-force

... y 5 IP(s) más

💡 Para desbloquear: /desbloquear [IP]
```

---

## 📝 Logs de Auditoría

Todos los eventos se registran en `logs/security.log`:

### Bloqueo de IP
```
IP bloqueada por intentos fallidos | IP=192.168.1.100
ALERTA TELEGRAM ENVIADA | tipo=IP_BLOQUEADA | ip=192.168.1.100
```

### Error al listar
```
ERROR LISTANDO IPS BLOQUEADAS | error=Connection timeout
```
(La alerta se envía de todos modos, sin el listado)

### Desbloqueo
```
IP DESBLOQUEADA VIA TELEGRAM | ip=192.168.1.100 | chat_id=7602447172
```

---

## 🎯 Beneficios

### Antes:
```
🚫 IP BLOQUEADA
IP: 192.168.1.100
Usuario: juanperez
```
❌ No sabías cuántas IPs estaban bloqueadas  
❌ Tenías que entrar al sistema para ver el listado

### Ahora:
```
🚫 IP BLOQUEADA
IP: 192.168.1.100
Usuario: juanperez

🚫 TODAS LAS IPS BLOQUEADAS:
1. 192.168.1.100 - Nueva
2. 10.0.0.50 - Desde ayer
3. 172.16.0.25 - Hace 3 días
```
✅ Ves todas las IPs bloqueadas al instante  
✅ Identificas patrones de ataque  
✅ Acción inmediata con `/desbloquear`

---

## 🚀 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/desbloquear [IP]` | Desbloquear una IP específica |
| `/ayuda` | Ver ayuda y comandos |

**Próximamente:**
- `/ips_bloqueadas` - Ver listado completo en cualquier momento
- `/whois [IP]` - Información detallada de una IP
- `/bloquear [IP]` - Bloquear IP manualmente

(Ver `TELEGRAM_BOT_ROADMAP.md` para roadmap completo)

---

## 🐛 Troubleshooting

### "No veo el listado de IPs"
**Causas posibles:**
1. Es la primera IP bloqueada → Mensaje dice "Esta es la única IP"
2. Error al consultar BD → Verifica logs: `type logs\security.log | findstr "ERROR LISTANDO"`
3. Todas las IPs están desbloqueadas

**Solución:** Ejecutar script de prueba:
```bash
python test_alerta_ip_bloqueada.py
```

### "El mensaje es muy largo"
El sistema limita a 10 IPs para evitar mensajes muy largos. Si hay más, muestra "... y X IP(s) más".

Para ver todas: (próximamente)
```
/ips_bloqueadas
```

---

## 📚 Archivos Relacionados

- `app.py` (líneas 914-1010) - Función de alertas modificada
- `test_alerta_ip_bloqueada.py` - Script de prueba
- `telegram_bot.py` - Comandos del bot
- `desbloquear_ip_telegram.py` - Desbloqueo rápido
- `TELEGRAM_BOT_USO.md` - Guía de uso completa

---

**Última actualización:** 27 Febrero 2026  
**Versión:** 1.1 (Informes de IPs bloqueadas)  
**Estado:** ✅ Operativo
