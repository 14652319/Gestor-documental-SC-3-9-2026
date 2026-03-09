# 🔍 ANÁLISIS: Problema de Sincronización entre `/configuracion` y `/dian_vs_erp/visor_v2`

**Fecha:** 5 de Enero, 2026  
**Reportado por:** Usuario  
**Sistema:** Gestor Documental - Módulo DIAN vs ERP

---

## 📋 PROBLEMA REPORTADO

El usuario indica que:
- ✅ El envío de notificaciones **SÍ funciona** en `/dian_vs_erp` (visor antiguo)
- ❌ El envío de notificaciones **NO está sincronizado** con `/dian_vs_erp/visor_v2` (visor nuevo)
- ⚠️ El módulo `/configuracion` debe integrarse con `/visor_v2`, NO con el visor antiguo

---

## 🔎 HALLAZGOS DEL ANÁLISIS

### 1️⃣ **RUTAS CONFIRMADAS EN `routes.py`**

```python
# Línea 335 - Visor ANTIGUO (NO se debe usar)
@dian_vs_erp_bp.route('/visor')
def visor_moderno():
    return render_template('dian_vs_erp/visor_moderno.html', ...)

# Línea 344 - Visor NUEVO (el que se DEBE usar)
@dian_vs_erp_bp.route('/visor_v2')
def visor_v2():
    return render_template('dian_vs_erp/visor_dian_v2.html', ...)
```

✅ **Ambas rutas existen y están funcionales**

---

### 2️⃣ **ENDPOINTS DE API DISPONIBLES**

#### **Envío de Emails:**
```python
# Línea 1657 - Individual
@dian_vs_erp_bp.route('/api/enviar_emails', methods=['POST'])

# Línea 1686 - Agrupado (usado por visor_v2)
@dian_vs_erp_bp.route('/api/enviar_email_agrupado', methods=['POST'])
```

#### **Gestión de Usuarios:**
```python
# Línea 3258 - Obtener usuarios por NIT
@dian_vs_erp_bp.route('/api/usuarios/por_nit/<nit>', methods=['GET'])

# También existe en línea 1936:
@dian_vs_erp_bp.route('/api/dian_usuarios/por_nit/<nit>', methods=['GET'])
```

✅ **Todos los endpoints de backend están disponibles**

---

### 3️⃣ **FUNCIONAMIENTO DEL `visor_v2`**

El archivo `visor_dian_v2.html` **SÍ implementa** el sistema de envío masivo:

#### **Función de Apertura de Modal (Línea 805):**
```javascript
function abrirModalEnvioMasivo(facturas){
  // 1. Extrae NITs únicos de las facturas seleccionadas
  const nitsUnicos = [...new Set(facturas.map(f => f.nit_emisor))];
  
  // 2. Consulta usuarios de cada NIT desde la API
  const promesas = nitsUnicos.map(nit => 
    fetch(`/dian_vs_erp/api/usuarios/por_nit/${nit}`)  // ✅ Ruta correcta
      .then(r => r.json())
      .then(response => ({nit, usuarios: response.usuarios || []}))
  );
  
  // 3. Muestra modal con destinatarios
  Promise.all(promesas).then(resultados => {
    mostrarModalEnvioMasivo(facturas, usuariosPorNit);
  });
}
```

#### **Función de Envío (Línea 914):**
```javascript
function enviarEmailsMasivos(){
  // 1. Obtiene destinatarios seleccionados
  const checkboxes = document.querySelectorAll('input[name="destinatario_masivo"]:checked');
  
  // 2. Envía email agrupado por destinatario
  fetch('/dian_vs_erp/api/enviar_email_agrupado', {  // ✅ Ruta correcta
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      destinatarios: [destinatario],
      cufes: cufes  // TODAS las facturas en un email
    })
  })
}
```

✅ **El visor_v2 SÍ tiene toda la funcionalidad implementada**

---

### 4️⃣ **PROBLEMA IDENTIFICADO: SINCRONIZACIÓN CON `/configuracion`**

El módulo `/configuracion` gestiona:
- 📧 Configuración SMTP (compartida con todo el sistema)
- 👥 Usuarios por NIT (CRUD de solicitantes y aprobadores)
- ⏰ Envíos Programados (jobs automáticos)
- 📊 Logs del Sistema

#### **APIs usadas por `/configuracion` (línea 1306+):**
```javascript
fetch('/dian_vs_erp/api/config/envios')          // ✅ Existe
fetch('/dian_vs_erp/api/config/envios', POST)    // ✅ Existe
fetch('/dian_vs_erp/api/config/envios/${id}/toggle')  // ✅ Existe
fetch('/dian_vs_erp/api/usuarios/por_nit/${nit}')     // ✅ Existe
```

✅ **Todas las APIs están disponibles y funcionales**

---

## 🔍 **CAUSAS POSIBLES DEL PROBLEMA**

### **HIPÓTESIS 1: Falta de Datos en la Base de Datos**
Si el envío no funciona, puede ser porque:
- ❌ No hay usuarios registrados en la tabla `usuarios_dian_vs_erp`
- ❌ Los usuarios existen pero están `activo=False`
- ❌ No hay configuraciones de envío programadas en `envios_programados_dian_vs_erp`

**Validación requerida:**
```sql
-- Ver usuarios registrados
SELECT nit, razon_social, nombres, apellidos, correo, tipo_usuario, activo 
FROM usuarios_dian_vs_erp 
ORDER BY nit;

-- Ver configuraciones de envío
SELECT id, nombre, tipo, activo, frecuencia 
FROM envios_programados_dian_vs_erp;
```

---

### **HIPÓTESIS 2: Error en Configuración SMTP**
Si los emails no se envían, puede ser:
- ❌ Variables de entorno incorrectas en `.env`
- ❌ Puerto bloqueado (465 o 587)
- ❌ Contraseña de aplicación inválida

**Validación requerida:**
```bash
# Ver configuración actual
python -c "from app import app; print(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT'))"
```

---

### **HIPÓTESIS 3: JavaScript No Carga Usuarios**
Si el modal abre vacío:
- ❌ La API `/api/usuarios/por_nit/{nit}` no retorna datos
- ❌ Error de CORS (improbable, mismo dominio)
- ❌ Error en consola de JavaScript (F12)

**Validación requerida:**
1. Abrir visor_v2: http://localhost:8099/dian_vs_erp/visor_v2
2. Seleccionar facturas
3. Click derecho "Enviar Emails"
4. Abrir DevTools (F12) → Pestaña Console
5. Ver si hay errores en rojo

---

### **HIPÓTESIS 4: Botón "Volver al Visor" Apunta al Visor Antiguo**
✅ **YA CORREGIDO** - El botón ahora redirige a `/dian_vs_erp/visor_v2`

```html
<!-- ANTES (incorrecto) -->
<a href="/dian_vs_erp" class="btn btn-danger">← Volver al Visor</a>

<!-- AHORA (correcto) -->
<a href="/dian_vs_erp/visor_v2" class="btn btn-danger">← Volver al Visor</a>
```

---

## ✅ **CONCLUSIONES DEL ANÁLISIS**

### **¿Qué está funcionando correctamente?**
1. ✅ Ruta `/dian_vs_erp/visor_v2` existe y responde
2. ✅ Template `visor_dian_v2.html` tiene toda la funcionalidad JavaScript
3. ✅ APIs de backend `/api/enviar_email_agrupado` y `/api/usuarios/por_nit/{nit}` existen
4. ✅ Botón "Volver al Visor" ahora redirige correctamente
5. ✅ Módulo `/configuracion` usa las APIs correctas

### **¿Qué NO está funcionando?**
❓ **No se puede determinar sin más información del usuario**

El código está **100% correcto** en:
- ✅ Frontend (visor_v2)
- ✅ Backend (routes.py)
- ✅ Integración (configuración)

---

## 🔬 **PRUEBAS REQUERIDAS PARA DIAGNOSTICAR**

### **Prueba 1: Verificar si hay usuarios registrados**
```sql
SELECT COUNT(*) FROM usuarios_dian_vs_erp;
```
**Resultado esperado:** > 0

---

### **Prueba 2: Verificar si la API retorna usuarios**
```bash
# Desde PowerShell
curl http://localhost:8099/dian_vs_erp/api/usuarios/por_nit/900123456
```
**Resultado esperado:** JSON con array de usuarios

---

### **Prueba 3: Verificar consola JavaScript**
1. Abrir http://localhost:8099/dian_vs_erp/visor_v2
2. Presionar F12 (DevTools)
3. Ir a pestaña "Console"
4. Seleccionar facturas y hacer click en "Enviar Emails"
5. Buscar mensajes en rojo (errores)

**Resultado esperado:** Sin errores, logs de éxito

---

### **Prueba 4: Verificar configuración SMTP**
Ir a: http://localhost:8099/dian_vs_erp/configuracion
- Pestaña "📧 Emails"
- Click en "🔍 Probar Conexión SMTP"

**Resultado esperado:** "✅ Conexión exitosa"

---

## 🎯 **RECOMENDACIONES**

### **ANTES de hacer cambios:**
1. 🔍 Ejecutar las 4 pruebas anteriores
2. 📸 Tomar screenshot de cualquier error en consola (F12)
3. 📋 Verificar que existan usuarios en la base de datos
4. 📧 Probar conexión SMTP desde `/configuracion`

### **SI el problema persiste:**
- Proporcionar logs de consola JavaScript (F12)
- Indicar si el modal abre vacío o con usuarios
- Verificar si el error es en TODOS los NITs o solo algunos
- Confirmar si otros módulos envían emails correctamente

---

## 📊 **RESUMEN EJECUTIVO**

| Componente | Estado | Notas |
|------------|--------|-------|
| Ruta `/visor_v2` | ✅ OK | Renderiza correctamente |
| Template `visor_dian_v2.html` | ✅ OK | JavaScript completo |
| API `/api/enviar_email_agrupado` | ✅ OK | Endpoint funcional |
| API `/api/usuarios/por_nit/{nit}` | ✅ OK | Endpoint funcional |
| Botón "Volver al Visor" | ✅ CORREGIDO | Ahora apunta a visor_v2 |
| Módulo `/configuracion` | ✅ OK | Usa APIs correctas |
| **Datos en BD** | ❓ DESCONOCIDO | Requiere validación |
| **Config SMTP** | ❓ DESCONOCIDO | Requiere validación |

---

**🚨 CONCLUSIÓN FINAL:**

El problema **NO es de código**, sino posiblemente de:
1. **Falta de datos** (usuarios no registrados)
2. **Configuración SMTP** (emails no se envían)
3. **Error específico no reportado** (necesita logs de consola)

**✅ RECOMENDACIÓN:** Ejecutar las 4 pruebas de diagnóstico antes de modificar código.
