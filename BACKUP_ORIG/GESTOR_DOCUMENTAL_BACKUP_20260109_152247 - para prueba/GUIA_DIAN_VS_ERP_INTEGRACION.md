# 🚀 GUÍA RÁPIDA: SISTEMA DIAN VS ERP

## ⚡ INICIO RÁPIDO

### Opción 1: Usar el archivo .bat (MÁS FÁCIL) ⭐ RECOMENDADO
```
1. Hacer doble clic en: INICIAR_AMBOS_SISTEMAS.bat
2. Esperar 5-10 segundos
3. El navegador se abrirá automáticamente
```

### Opción 2: Manual (Terminal)
```powershell
# Terminal 1 - Gestor Documental (Puerto 8099)
cd "c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
.\.venv\Scripts\activate
python app.py

# Terminal 2 - DIAN vs ERP (Puerto 8097)
cd "c:\Users\Usuario\Desktop\Gestor Documental\PAQUETES_TRANSPORTABLES\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\Proyecto Dian Vs ERP v5.20251130"
python app.py
```

---

## 🔗 INTEGRACIÓN ENTRE SISTEMAS

### Cómo Funciona el Botón "DIAN vs ERP"

Cuando haces clic en el botón "DIAN vs ERP" desde el dashboard:

1. **✅ Sistema verifica disponibilidad** (puerto 8097)
2. **🔄 Si está disponible**: Abre en nueva ventana
3. **⚠️ Si NO está disponible**: Muestra mensaje con instrucciones

### Mensaje de Alerta

Si el sistema DIAN vs ERP no está corriendo, verás:

```
⚠️ El sistema DIAN vs ERP no está disponible en el puerto 8097

Para iniciarlo:
1. Abre una terminal en la carpeta del proyecto
2. Ejecuta: cd "Proyecto Dian Vs ERP v5.20251130"
3. Ejecuta: python app.py

O usa el archivo .bat si está disponible.

¿Deseas intentar abrir la ventana de todas formas?
```

### URLs de los Sistemas

| Sistema | URL | Puerto |
|---------|-----|--------|
| Gestor Documental | http://localhost:8099 | 8099 |
| DIAN vs ERP | http://localhost:8097 | 8097 |

---

## 🛠️ SOLUCIÓN DE PROBLEMAS

### ❌ Error: "ERR_CONNECTION_REFUSED"

**Causa**: El servidor DIAN vs ERP no está corriendo en el puerto 8097

**Solución**:
1. Ejecutar `INICIAR_AMBOS_SISTEMAS.bat`
2. O iniciar manualmente con `python app.py` en la carpeta DIAN vs ERP
3. Esperar 5-10 segundos hasta que el servidor esté listo

### ❌ Error: "Puerto 8099 ya está en uso"

**Causa**: Ya hay un servidor corriendo en ese puerto

**Solución**:
```powershell
# Ver procesos usando el puerto
netstat -ano | Select-String ":8099"

# Detener todos los procesos Python
Get-Process python* | Stop-Process -Force

# Reiniciar sistemas
INICIAR_AMBOS_SISTEMAS.bat
```

### ❌ Error: "No se encuentra Python"

**Causa**: Python no está instalado o no está en el PATH

**Solución**:
1. Instalar Python desde https://www.python.org
2. Durante instalación, marcar "Add Python to PATH"
3. Reiniciar terminal

---

## 📊 VERIFICACIÓN DE ESTADO

### Verificar si los servidores están corriendo

```powershell
# Ver todos los puertos en uso
netstat -ano | Select-String ":8099"
netstat -ano | Select-String ":8097"
```

**Salida esperada**:
```
TCP    0.0.0.0:8099    0.0.0.0:0    LISTENING    12345
TCP    0.0.0.0:8097    0.0.0.0:0    LISTENING    67890
```

Si ves `LISTENING`, el servidor está corriendo correctamente.

---

## 🎯 MEJORAS IMPLEMENTADAS (30 NOV 2025)

### 1. Verificación Automática
- ✅ El botón verifica si el puerto 8097 está disponible (timeout 3 segundos)
- ✅ Usa `fetch()` con `AbortController` para timeout rápido
- ✅ Maneja errores de conexión de forma elegante

### 2. Mensajes Claros
- ✅ Notificación de verificación: "🔍 Verificando disponibilidad..."
- ✅ Éxito: "✅ Abriendo DIAN vs ERP en nueva ventana"
- ✅ Error: Alerta con instrucciones completas

### 3. Archivo .bat Mejorado
- ✅ Verifica que Python esté instalado
- ✅ Verifica que la carpeta DIAN vs ERP exista
- ✅ Inicia ambos servidores en ventanas separadas
- ✅ Espera 5 segundos y abre el navegador automáticamente
- ✅ Emojis y colores para mejor UX

### 4. Opción de Usuario
- ✅ Si el servidor no responde, el usuario puede decidir:
  - Cancelar (recomendado)
  - Intentar abrir de todas formas (si el servidor está iniciándose)

---

## 🔒 SEGURIDAD

### Timeout de Sesión
- ⏰ **25 minutos** de inactividad → Cierre automático
- 🔄 Se reinicia con cualquier actividad (mouse, teclado, click, scroll)
- 🚪 Redirección automática a login al expirar

### CORS (Cross-Origin)
- ⚠️ El fetch usa `mode: 'no-cors'` para evitar errores de CORS
- ✅ Solo verifica disponibilidad, no lee respuesta
- ✅ Si hay error de red, asume que el servidor no está disponible

---

## 📝 NOTAS TÉCNICAS

### Código JavaScript Implementado

```javascript
async function abrirDianVsERP() {
    // Mostrar mensaje de verificación
    mostrarNotificacion('info', '🔍 Verificando disponibilidad...');
    
    try {
        // Timeout de 3 segundos
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch('http://localhost:8097/', {
            method: 'HEAD',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        // Si responde, abrir
        if (response.ok || response.status === 404 || response.type === 'opaque') {
            window.open('http://localhost:8097', '_blank', 'width=1400,height=900');
            mostrarNotificacion('success', '✅ Abriendo DIAN vs ERP...');
        }
    } catch (error) {
        // Servidor no disponible
        // Mostrar alerta con instrucciones
        if (confirm(mensaje)) {
            window.open('http://localhost:8097', '_blank');
        }
    }
}
```

### Ventajas del Nuevo Sistema

| Antes | Ahora |
|-------|-------|
| ❌ Siempre intentaba abrir sin verificar | ✅ Verifica disponibilidad primero |
| ❌ Error genérico del navegador | ✅ Mensaje personalizado con instrucciones |
| ❌ Usuario no sabía qué hacer | ✅ Guía clara de solución |
| ❌ Timeout indefinido | ✅ Timeout de 3 segundos |
| ❌ Sin opción de cancelar | ✅ Usuario decide si intenta o cancela |

---

## 🎉 RESUMEN

**Antes**: Click → Error de conexión → Usuario confundido

**Ahora**: Click → Verificación (3s) → Si OK: Abre | Si NO: Instrucciones claras

**Para Iniciar Ambos Sistemas**:
1. Doble click en `INICIAR_AMBOS_SISTEMAS.bat`
2. Esperar 5-10 segundos
3. ¡Listo! Ambos sistemas funcionando

**Para Detener**:
- Cerrar las ventanas de terminal que se abrieron

---

## 📞 SOPORTE

Si tienes problemas:
1. Verifica que Python esté instalado: `python --version`
2. Verifica que los puertos estén libres: `netstat -ano | Select-String ":8099"`
3. Revisa los logs en las ventanas de terminal
4. Usa el .bat para inicio automático

**Fecha de última actualización**: 30 de Noviembre 2025
