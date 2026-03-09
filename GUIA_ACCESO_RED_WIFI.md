# 📡 GUÍA RÁPIDA: Acceso por Red WiFi

## ✅ Tu configuración actual:

- **IP del servidor:** 192.168.100.121
- **Puerto:** 8099
- **URL de acceso:** http://192.168.100.121:8099

---

## 🚀 PASOS PARA ACTIVAR ACCESO EN RED:

### Paso 1: Abrir el puerto en el Firewall

1. Busca el archivo: **ABRIR_FIREWALL_GESTOR.bat**
2. Click derecho sobre él
3. Selecciona: **"Ejecutar como administrador"**
4. Acepta el control de cuentas de usuario (UAC)
5. Presiona una tecla cuando te lo pida
6. Deberías ver: "ÉXITO: Puerto 8099 abierto en el firewall"

### Paso 2: Iniciar la aplicación

Ejecuta: **1_iniciar_gestor.bat**

### Paso 3: Acceder desde otros dispositivos

Desde cualquier dispositivo conectado a la **misma red WiFi**, abre un navegador:

```
http://192.168.100.121:8099
```

---

## 🔧 NO NECESITAS MODIFICAR NINGÚN CÓDIGO

Tu archivo app.py ya está configurado correctamente con:
- `host="0.0.0.0"` ✅ (escucha en todas las interfaces)
- `port=8099` ✅

---

## 📱 Dispositivos compatibles:

- ✅ Otras computadoras en la red
- ✅ Laptops
- ✅ Tablets (Android/iPad)
- ✅ Celulares (Android/iPhone)

**Requisito:** Deben estar conectados a la misma red WiFi (192.168.100.x)

---

## ⚠️ Solución de problemas:

### Si no puedes acceder desde otros dispositivos:

1. **Verifica que ambos dispositivos estén en la misma red WiFi**
2. **Verifica que la aplicación esté corriendo** (ventana de PowerShell abierta)
3. **Prueba desde tu PC primero:** http://localhost:8099
4. **Verifica el firewall:** Ejecuta ABRIR_FIREWALL_GESTOR.bat como administrador
5. **Desactiva temporalmente el firewall** para probar (Panel de Control → Firewall)

### Si tu IP cambia:

Tu IP actual es asignada por DHCP y puede cambiar. Para verificar:

```powershell
ipconfig | Select-String "IPv4"
```

---

## 🎯 Resumen visual:

```
┌─────────────────────┐
│  Tu PC (Servidor)   │
│  IP: 192.168.100.121│ ← Ejecutando 1_iniciar_gestor.bat
│  Puerto: 8099       │
└──────────┬──────────┘
           │
      Red WiFi (192.168.100.x)
           │
    ┌──────┴─────────┐
    ▼                ▼
┌────────┐      ┌─────────┐
│  PC #2 │      │  Móvil  │
└────────┘      └─────────┘
    │                │
    └────────┬───────┘
             ▼
   http://192.168.100.121:8099
```

---

Fecha: 05/03/2026
