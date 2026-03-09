# 🌐 INSTRUCCIONES: Cargar archivos desde el navegador

## ✅ LAS TABLAS YA ESTÁN LIMPIAS (0 registros)
## ✅ LOS ARCHIVOS YA ESTÁN EN uploads/

Ahora solo necesitas:

## 📝 PASO 1: Iniciar el servidor

Abre PowerShell y ejecuta:

```powershell
python app.py
```

**Espera a ver este mensaje:**
```
✅ SERVIDOR INICIANDO - Módulos HABILITADOS
```

## 📝 PASO 2: Abrir el navegador

Abre tu navegador y ve a:

```
http://localhost:8099/dian_vs_erp/visor_v2
```

## 📝 PASO 3: Cargar y consolidar

1. **Haz clic en el botón "⚙️ Configuración"** (arriba a la derecha)

2. **Baja hasta la sección "🔄 Procesar & Consolidar"**

3. **Haz clic en el botón "🚀 Procesar & Consolidar Datos"**

4. **ESPERA** a que termine (puede tomar 1-2 minutos)

5. Verás un mensaje de **éxito** y los datos aparecerán en la tabla

## 🎯 RESULTADO ESPERADO

Después de la consolidación verás:

- ✅ **~170,000 registros** en la tabla
- ✅ Columna **"Ver PDF"** con enlaces clickeables
- ✅ Columna **"Estado Aprobación"** con valores
- ✅ Datos de **ERP_FINANCIERO** y **ERP_COMERCIAL**
- ✅ Filtros funcionando correctamente

## ❓ SI NO FUNCIONA

Si al hacer clic en "Procesar & Consolidar" NO pasa nada o da error:

1. Abre la **Consola del navegador** (F12)
2. Ve a la pestaña **"Console"**
3. Mira si hay errores en rojo
4. **Toma captura** y compártela

---

**IMPORTANTE:** NO subas archivos manualmente. El botón "Procesar & Consolidar" ya los leerá de `uploads/`
