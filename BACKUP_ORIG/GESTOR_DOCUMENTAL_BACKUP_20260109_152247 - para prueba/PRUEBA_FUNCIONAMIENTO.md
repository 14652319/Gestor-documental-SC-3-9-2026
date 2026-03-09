# 🧪 PRUEBA DE FUNCIONAMIENTO - Botón DIAN vs ERP

## ¿Cómo funciona el botón "⚖️ Validación DIAN vs ERP"?

### 📍 **Ubicación del botón**
- Dashboard → Menú lateral izquierdo
- Sección "ANÁLISIS Y REPORTES"
- Icono: ⚖️ con enlace verde 🔗

### 🔄 **Proceso cuando haces clic:**

```
1. CLICK en botón
    ↓
2. JavaScript ejecuta: abrirDianVsERP()
    ↓
3. Verifica disponibilidad: fetch('http://localhost:8097/api/health')
    ↓
4. Abre NUEVA VENTANA: window.open('http://localhost:8097', '_blank')
    ↓
5. Muestra notificación: "✅ Abriendo DIAN vs ERP en nueva ventana"
    ↓
6. RESULTADO: Nueva ventana 1400x900 con sistema DIAN vs ERP
```

---

## ✅ **PASOS PARA PROBAR**

### **Opción 1: Inicio Manual (Recomendado para entender)**

```cmd
# Terminal 1: Iniciar Gestor Documental
cd "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
1_iniciar_gestor.bat

# Terminal 2: Iniciar DIAN vs ERP
cd "C:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
2_iniciar_dian.bat

# Navegador: Abrir Dashboard
http://localhost:8099

# Dashboard: Hacer clic en botón ⚖️ Validación DIAN vs ERP
```

### **Opción 2: Inicio Automático (Más rápido)**

```cmd
# Un solo comando inicia ambos sistemas
iniciar_ambos_sistemas.bat
```

---

## 🎬 **Lo que verás:**

### **ANTES del clic:**
- 1 pestaña: Dashboard en http://localhost:8099

### **DESPUÉS del clic:**
- 2 pestañas/ventanas:
  - **Pestaña 1** (original): Dashboard http://localhost:8099
  - **Pestaña 2** (nueva): DIAN vs ERP http://localhost:8097

### **Comportamiento:**
- ✅ La ventana nueva es **INDEPENDIENTE** (puedes cerrarla sin afectar el Dashboard)
- ✅ Puedes tener **ambos sistemas visibles** al mismo tiempo
- ✅ Son **dos Flask servers separados** comunicándose solo por navegación

---

## ⚠️ **PROBLEMAS COMUNES**

### **Problema 1: "No se abre nada"**
**Causa**: Sistema DIAN vs ERP no está iniciado en puerto 8097  
**Solución**: 
```cmd
2_iniciar_dian.bat
# Espera ver: "Running on http://0.0.0.0:8097"
```

### **Problema 2: "Página no cargada"**
**Causa**: Puerto 8097 ocupado por otro proceso  
**Solución**: 
```powershell
netstat -ano | Select-String ":8097"
# Si hay algo ocupando el puerto, cambiar puerto o detener proceso
```

### **Problema 3: "Error de conexión"**
**Causa**: Firewall bloqueando conexión local  
**Solución**: 
```cmd
# Permitir conexiones locales en firewall Windows
netsh advfirewall firewall add rule name="Gestor DIAN 8097" dir=in action=allow protocol=TCP localport=8097
```

---

## 🔍 **VERIFICACIÓN TÉCNICA**

### **1. Verificar que Flask está escuchando:**
```powershell
netstat -ano | Select-String ":8097" | Select-String "LISTENING"
# Debe mostrar: TCP 0.0.0.0:8097 ... LISTENING
```

### **2. Probar acceso directo:**
Abre manualmente: http://localhost:8097  
Si carga → Sistema funciona ✅  
Si no carga → Revisa logs del servidor

### **3. Ver logs en consola:**
Al hacer clic, la consola de `2_iniciar_dian.bat` debe mostrar:
```
127.0.0.1 - - [30/Nov/2025 15:30:45] "GET /api/health HTTP/1.1" 200 -
127.0.0.1 - - [30/Nov/2025 15:30:45] "GET / HTTP/1.1" 200 -
```

---

## 📱 **COMPORTAMIENTO DE window.open()**

```javascript
window.open(
    'http://localhost:8097',  // URL a abrir
    '_blank',                  // Nueva pestaña/ventana
    'width=1400,height=900'    // Tamaño de ventana emergente
);
```

**Notas:**
- `_blank` = Nueva pestaña (o ventana emergente si el navegador lo permite)
- Algunos navegadores modernos abren en pestaña en vez de ventana emergente
- Puedes cambiar `_blank` por `_self` si quieres reemplazar la pestaña actual

---

## 🎓 **RESUMEN EJECUTIVO**

| Aspecto | Detalle |
|---------|---------|
| **Acción** | Click en botón "⚖️ Validación DIAN vs ERP" |
| **Resultado** | Nueva ventana/pestaña con http://localhost:8097 |
| **Requisito** | Ambos sistemas corriendo (8099 + 8097) |
| **Ventana** | 1400x900 píxeles |
| **Impacto** | Dashboard original NO se cierra |
| **Ventaja** | Trabajar con ambos sistemas simultáneamente |

---

## 🚀 **PRUÉBALO AHORA**

```cmd
# 1. Inicia ambos sistemas
iniciar_ambos_sistemas.bat

# 2. Espera 5-10 segundos

# 3. El navegador abrirá automáticamente:
#    - http://localhost:8099 (Dashboard)

# 4. En el Dashboard, haz clic en:
#    ⚖️ Validación DIAN vs ERP

# 5. Verás aparecer nueva ventana con sistema DIAN vs ERP
```

---

📝 **Documentación generada:** 30/Nov/2025  
✅ **Última actualización puerto:** 8097
