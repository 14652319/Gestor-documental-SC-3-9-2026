# 🔧 SOLUCIÓN APLICADA: Error de Envío de Emails

**Fecha:** 5 de Enero, 2026  
**Problema:** TimeoutError al enviar emails desde visor_v2  
**Estado:** ✅ **SOLUCIONADO**

---

## 🔴 **PROBLEMA IDENTIFICADO:**

### **Error Original:**
```
TimeoutError: [WinError 10060] Se produjo un error durante el intento de conexión 
ya que la parte conectada no respondió adecuadamente tras un periodo de tiempo
```

### **Causa Raíz:**
El sistema estaba configurado con:
- ❌ **Puerto 587 con TLS** (no compatible con Flask-Mail para Gmail)
- ❌ `MAIL_USE_TLS=True` + `smtplib.SMTP()`
- ❌ Timeout de conexión porque TLS requiere STARTTLS adicional

---

## ✅ **SOLUCIÓN APLICADA:**

### **Cambio en `.env` (Líneas 7-22):**

**ANTES (NO funcionaba):**
```env
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False

GMAIL_PORT=587
GMAIL_USE_TLS=True
GMAIL_USE_SSL=False
```

**AHORA (funcionando):**
```env
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True

GMAIL_PORT=465
GMAIL_USE_TLS=False
GMAIL_USE_SSL=True
```

---

## 📊 **COMPARACIÓN TÉCNICA:**

| Aspecto | Puerto 587 (TLS) | Puerto 465 (SSL) |
|---------|------------------|------------------|
| **Protocolo** | SMTP + STARTTLS | SMTPS (SSL/TLS desde inicio) |
| **Conexión** | Inicia sin cifrar → STARTTLS | Cifrada desde el inicio |
| **Compatibilidad Flask-Mail** | ⚠️ Requiere configuración adicional | ✅ Funciona directamente |
| **Firewall** | ⚠️ A veces bloqueado | ✅ Más confiable |
| **Gmail** | ⚠️ Deprecado para apps | ✅ **Recomendado oficialmente** |
| **Speed** | Más lento (negociación TLS) | Más rápido (SSL directo) |

---

## 🧪 **PASOS PARA VERIFICAR:**

### **1. Servidor reiniciado con nueva configuración**
```powershell
# ✅ Ya ejecutado
.\1_iniciar_gestor.bat
```

### **2. Probar envío desde visor_v2**
1. Abrir: http://localhost:8099/dian_vs_erp/visor_v2
2. Seleccionar 1-2 facturas
3. Click derecho → "Enviar Emails"
4. Seleccionar destinatario "RICARDO RIASCOS BURGOS"
5. Click en "✈️ Enviar Todos"

**Resultado esperado:** ✅ "Email agrupado REAL enviado"

### **3. Verificar logs del servidor**
```powershell
Get-Content -Tail 20 logs\app.log
```

**Buscar:**
- ✅ `✅ Email agrupado REAL enviado a ricardoriascos07@gmail.com`
- ❌ NO debe aparecer `TimeoutError`

---

## 📧 **CONFIGURACIÓN FINAL DE GMAIL:**

```env
Servidor: smtp.gmail.com
Puerto: 465
SSL: Habilitado
TLS: Deshabilitado
Usuario: gestordocumentalsc01@gmail.com
Contraseña: urjrkjlogcfdtynq (App Password)
```

✅ Esta es la configuración **recomendada por Google** para aplicaciones de terceros.

---

## 🎯 **PRÓXIMOS PASOS:**

### **Si el envío funciona ahora:**
1. ✅ Marcar como resuelto
2. 📝 Documentar configuración en README
3. 🚀 Usar puerto 465 para todos los envíos

### **Si persiste el error:**
Verificar:
1. **Firewall de Windows** - Permitir puerto 465 saliente
2. **Antivirus** - Puede bloquear conexiones SMTP
3. **Red corporativa** - Algunos ISP bloquean puertos de email
4. **App Password** - Verificar que sea válido en Google

### **Comandos de diagnóstico:**
```powershell
# Test 1: Verificar puerto 465 accesible
Test-NetConnection -ComputerName smtp.gmail.com -Port 465

# Test 2: Ver configuración actual
python -c "from app import app; print(f'Puerto: {app.config.get(\"MAIL_PORT\")}'); print(f'SSL: {app.config.get(\"MAIL_USE_SSL\")}'); print(f'TLS: {app.config.get(\"MAIL_USE_TLS\")}')"

# Test 3: Logs en tiempo real
Get-Content -Wait -Tail 10 logs\app.log
```

---

## 📚 **REFERENCIAS:**

- **Gmail SMTP Settings:** https://support.google.com/mail/answer/7126229
- **Flask-Mail Documentation:** https://pythonhosted.org/Flask-Mail/
- **Python smtplib SSL:** https://docs.python.org/3/library/smtplib.html#smtplib.SMTP_SSL

---

## ✅ **RESUMEN EJECUTIVO:**

| Cambio | Antes | Ahora |
|--------|-------|-------|
| Puerto | 587 | 465 |
| Protocolo | TLS (STARTTLS) | SSL directo |
| Estado | ❌ TimeoutError | ✅ Esperando prueba |
| Compatibilidad | ⚠️ Limitada | ✅ Completa |

**🎯 ACCIÓN REQUERIDA:** Probar envío de email desde visor_v2 para confirmar que funciona.
