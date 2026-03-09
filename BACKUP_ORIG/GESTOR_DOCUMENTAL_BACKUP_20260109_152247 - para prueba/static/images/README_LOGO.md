# 🎨 CONFIGURACIÓN DE LOGO - Supertiendas Cañaveral

## 📁 Ruta del Logo

**Ubicación del archivo:**
```
/static/images/logo_supertiendas.png
```

## 🖼️ Especificaciones Recomendadas del Logo

### Dimensiones
- **Ancho máximo:** 150-200 px
- **Alto máximo:** 50-60 px
- **Formato:** PNG con fondo transparente (preferido) o JPG

### Calidad
- **Resolución:** 72-150 DPI (para web)
- **Tamaño de archivo:** Máximo 100 KB
- **Transparencia:** Sí (PNG con canal alpha)

## 🔧 Configuración en el Sistema

### Variable Centralizada en app.py

**Agregar en la sección de configuración (líneas ~48-60):**

```python
# =============================================
# 🎨 CONFIGURACIÓN DE MARCA (BRANDING)
# =============================================
LOGO_PATH = '/static/images/logo_supertiendas.png'  # Ruta relativa desde la raíz web
LOGO_ALT_TEXT = 'Supertiendas Cañaveral'
EMPRESA_NOMBRE = 'Supertiendas Cañaveral'
EMPRESA_NIT = '805.028.041-1'
```

### Hacer Disponible para Todos los Templates

**Agregar context processor en app.py (después de línea 1850):**

```python
# =============================================
# 🎨 CONTEXT PROCESSOR - Variables Globales
# =============================================
@app.context_processor
def inject_branding():
    """Inyecta variables de marca en todos los templates"""
    return {
        'LOGO_PATH': LOGO_PATH,
        'LOGO_ALT_TEXT': LOGO_ALT_TEXT,
        'EMPRESA_NOMBRE': EMPRESA_NOMBRE,
        'EMPRESA_NIT': EMPRESA_NIT
    }
```

## 📝 Uso en Templates

### Ejemplo 1: Header Fijo (reimprimir_relacion.html)

**Reemplazar línea ~347 (el h1 actual):**

```html
<!-- ANTES -->
<h1>🔄 Reimprimir Relación</h1>

<!-- DESPUÉS -->
<div class="header-logo-container">
    <img src="{{ LOGO_PATH }}" alt="{{ LOGO_ALT_TEXT }}" class="header-logo">
    <h1>🔄 Reimprimir Relación</h1>
</div>
```

**CSS para el logo (agregar en <style>):**

```css
/* Logo en Header */
.header-logo-container {
    display: flex;
    align-items: center;
    gap: 15px;
}

.header-logo {
    height: 40px;  /* Altura fija */
    width: auto;   /* Ancho proporcional */
    object-fit: contain;  /* Mantener proporción */
    /* Protección contra copia */
    user-select: none;
    -webkit-user-drag: none;
    pointer-events: none;  /* No se puede hacer clic derecho */
}

/* Marca de agua (opcional para documentos) */
.header-logo.watermark {
    opacity: 0.15;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    height: 200px;
    z-index: 0;
}
```

### Ejemplo 2: Login (login.html)

```html
<div class="card-header">
    <img src="{{ LOGO_PATH }}" alt="{{ LOGO_ALT_TEXT }}" class="login-logo">
    <h1>Iniciar Sesión</h1>
</div>
```

**CSS específico:**

```css
.login-logo {
    height: 60px;
    margin-bottom: 15px;
    user-select: none;
    -webkit-user-drag: none;
    pointer-events: none;
}
```

### Ejemplo 3: Marca de Agua en PDFs (opcional)

```python
# En generar_relacion() cuando se crea PDF
from PIL import Image
import io

# Agregar logo al PDF
logo_path = os.path.join('static', 'images', 'logo_supertiendas.png')
if os.path.exists(logo_path):
    pdf.image(logo_path, x=150, y=10, w=40)  # Esquina superior derecha
```

## 🔒 Protecciones Implementadas

### 1. Prevenir Descarga/Arrastre
```css
img.header-logo {
    user-select: none;           /* No seleccionar */
    -webkit-user-drag: none;     /* No arrastrar */
    pointer-events: none;        /* No interactuar */
}
```

### 2. Prevenir Click Derecho (JavaScript)
```javascript
document.querySelectorAll('.header-logo').forEach(img => {
    img.addEventListener('contextmenu', (e) => {
        e.preventDefault();  // Bloquear menú contextual
        return false;
    });
});
```

### 3. Marca de Agua Incrustada
- Si quieres que NO sea fácil de copiar, convertir el logo a base64:

```python
import base64

def logo_to_base64(image_path):
    with open(image_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode()

# Usar en template
LOGO_BASE64 = f"data:image/png;base64,{logo_to_base64('static/images/logo_supertiendas.png')}"
```

```html
<img src="{{ LOGO_BASE64 }}" alt="Logo" class="header-logo">
```

**Ventaja:** No hay archivo físico accesible por URL, el logo está "embebido" en el HTML.

## 📦 Archivos a Crear/Modificar

### 1. Crear archivo de logo
```
📁 static/
  └── 📁 images/
      └── 🖼️ logo_supertiendas.png  ← CREAR ESTE ARCHIVO
```

### 2. Modificar app.py
- Agregar variables LOGO_PATH, LOGO_ALT_TEXT, etc.
- Agregar context_processor inject_branding()

### 3. Modificar templates
- reimprimir_relacion.html
- generar_relacion_REFACTORED.html
- login.html
- nueva_factura_REFACTORED.html

## 🎯 Posiciones Recomendadas del Logo

### En Headers (Parte Superior)
```
┌─────────────────────────────────────┐
│ [LOGO] 🔄 Reimprimir Relación      │  ← Logo + Título
│              [Usuario] [Salir]      │
└─────────────────────────────────────┘
```

### En Esquina Superior Derecha
```
┌─────────────────────────────────────┐
│ 🔄 Reimprimir Relación      [LOGO]  │  ← Logo en esquina
│              [Usuario] [Salir]      │
└─────────────────────────────────────┘
```

### Como Marca de Agua (Fondo)
```
┌─────────────────────────────────────┐
│                                     │
│         [LOGO TRANSPARENTE]         │  ← 15% opacidad
│      (Fondo de todo el contenido)   │
│                                     │
└─────────────────────────────────────┘
```

## 🔄 Cambiar el Logo en el Futuro

### Paso 1: Reemplazar archivo
```cmd
copy nuevo_logo.png static\images\logo_supertiendas.png
```

### Paso 2: Limpiar caché del navegador
- Presionar Ctrl + F5 (recarga forzada)
- O agregar versión al archivo: `logo_supertiendas.png?v=2`

### Paso 3: (Opcional) Cambiar configuración
```python
# En app.py
LOGO_PATH = '/static/images/logo_supertiendas_v2.png'
```

## ⚙️ Variables CSS Personalizables

```css
:root {
    --logo-height-header: 40px;   /* Altura en headers */
    --logo-height-login: 60px;    /* Altura en login */
    --logo-opacity-watermark: 0.15;  /* Opacidad marca de agua */
}

.header-logo {
    height: var(--logo-height-header);
}

.login-logo {
    height: var(--logo-height-login);
}
```

## 📊 Ubicaciones Sugeridas por Página

| Página | Ubicación | Tamaño | Opacidad |
|--------|-----------|--------|----------|
| Login | Centro superior | 80px | 100% |
| Dashboard | Header izquierda | 40px | 100% |
| Reimprimir Relaciones | Header izquierda | 40px | 100% |
| Nueva Factura | Header izquierda | 40px | 100% |
| Generar Relación | Header izquierda | 40px | 100% |
| PDFs Exportados | Esquina sup. der. | 30px | 100% |
| Excel (opcional) | No aplica | - | - |

## 🚀 Implementación Rápida

### Script de Conversión a Base64

```python
# convertir_logo_base64.py
import base64

with open('static/images/logo_supertiendas.png', 'rb') as img:
    logo_base64 = base64.b64encode(img.read()).decode()
    
with open('logo_base64.txt', 'w') as f:
    f.write(f"data:image/png;base64,{logo_base64}")

print("✅ Logo convertido a base64 en: logo_base64.txt")
```

### Insertar en app.py

```python
LOGO_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSU..."  # Copiar de logo_base64.txt
```

## 📞 Soporte

**Para cambiar el logo:**
1. Reemplazar archivo en `static/images/logo_supertiendas.png`
2. Limpiar caché del navegador (Ctrl + F5)
3. Si no funciona, verificar ruta en `app.py`

**Para cambiar posición:**
1. Modificar CSS en cada template
2. Ajustar `height` y `width` según necesidad
3. Usar `position: absolute` para marcas de agua

**Para proteger más:**
1. Convertir a base64 (sin archivo físico)
2. Agregar JavaScript para bloquear click derecho
3. Usar marca de agua con opacidad baja

---

**Creado:** Octubre 20, 2025  
**Sistema:** Gestor Documental - Supertiendas Cañaveral  
**Versión:** 1.0
