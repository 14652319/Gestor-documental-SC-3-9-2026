# 📝 Módulo de Configuración de Catálogos - Facturas Digitales

## ✅ Instalación Completada

Se ha creado exitosamente el módulo de administración de catálogos para Facturas Digitales.

---

## 📦 Archivos Creados

### 1. **Backend - Routes**
```
modules/facturas_digitales/config_routes.py
```
Contiene 20 endpoints API para las 4 tablas:
- `/api/tipo-documento` (GET, POST, PUT, DELETE)
- `/api/forma-pago` (GET, POST, PUT, DELETE)
- `/api/tipo-servicio` (GET, POST, PUT, DELETE)
- `/api/departamento` (GET, POST, PUT, DELETE)

### 2. **Frontend - Template HTML**
```
templates/facturas_digitales/configuracion_catalogos.html
```
Interfaz responsive con:
- ✅ Tabs para cada catálogo
- ✅ Tabla con registros activos e inactivos
- ✅ Modales para crear/editar
- ✅ Botones de activar/desactivar
- ✅ Modo claro y oscuro
- ✅ Colores institucionales (Verde #0A6E3F, Amarillo #FFB900)
- ✅ Diseño responsive (mobile, tablet, desktop)

### 3. **Database - Tablas**
```sql
- tipo_doc_facturacion (3 registros)
- forma_pago_facturacion (2 registros)
- tipo_servicio_facturacion (4 registros)
- departamentos_facturacion (5 registros)
```

### 4. **Integration - App.py**
El blueprint `config_facturas_bp` ha sido registrado automáticamente.

### 5. **Dashboard - Enlace**
Se agregó el card "📝 Otras Configuraciones" en el dashboard principal.

---

## 🚀 Cómo Usar el Módulo

### **Paso 1: Acceder al Dashboard**
```
http://127.0.0.1:8099/facturas-digitales/dashboard
```

### **Paso 2: Click en "Otras Configuraciones"**
En la sección de configuración, verás el nuevo card:
```
📝 Otras Configuraciones
   Gestión de catálogos
```

### **Paso 3: Administrar Catálogos**
URL directa:
```
http://127.0.0.1:8099/facturas-digitales/configuracion
```

---

## 🔧 Funcionalidades por Catálogo

### 📄 **Tipo Documento**
- FC - FACTURA
- NC - NOTA DÉBITO
- ND - NOTA CRÉDITO

### 💳 **Forma de Pago**
- EST - ESTÁNDAR
- TC - TARJETA DE CRÉDITO

### 🛠️ **Tipo de Servicio**
- COMP - COMPRA
- SERV - SERVICIO
- HONO - HONORARIO
- COMP-SERV - COMPRA Y SERVICIO

### 🏢 **Departamentos**
- TIC - TECNOLOGIA
- MER - MERCADEO
- MYP - MERCADEO ESTRATEGICO
- DOM - DOMICILIOS
- FIN - FINANCIERO

---

## ✨ Características Implementadas

### 1. **CRUD Completo**
- ✅ **Crear**: Botón "+ Nuevo Registro" abre modal
- ✅ **Leer**: Tabla muestra todos los registros
- ✅ **Actualizar**: Botón "✏️ Editar" abre modal con datos
- ✅ **Eliminar**: Soft delete - Botón "🚫 Desactivar"

### 2. **Validaciones**
- ✅ Sigla: Máximo 10 caracteres, obligatorio, automático UPPER
- ✅ Descripción/Nombre: Máximo 100 caracteres, obligatorio, automático UPPER
- ✅ Estado: Checkbox activo/inactivo
- ✅ No permite duplicados (constraint UNIQUE en sigla)

### 3. **Diseño Responsive**
```css
✅ Desktop: Tabla completa con todos los campos
✅ Tablet: Ajuste de columnas
✅ Mobile: Tabla scrollable horizontal
```

### 4. **Modo Claro/Oscuro**
- Botón de toggle: 🌓
- Guarda preferencia en localStorage
- Colores institucionales en ambos modos

### 5. **Seguridad**
- ✅ Decorador `@requiere_permiso('admin')`
- ✅ Solo usuarios internos pueden acceder
- ✅ Validación de sesión activa
- ✅ Auditoría: `usuario_creacion`, `fecha_creacion`

---

## 📊 Estructura de Datos

```sql
CREATE TABLE tipo_doc_facturacion (
    id SERIAL PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion VARCHAR(50)
);
```

---

## 🧪 Testing

### **Script de Prueba Incluido**
```bash
python test_configuracion_catalogos.py
```

Este script verifica:
- ✅ Conectividad al servidor
- ✅ Endpoints funcionando
- ✅ Datos en las tablas

---

## 🎨 Colores Institucionales

```css
--canaveral-green: #0A6E3F       /* Verde principal */
--canaveral-green-dark: #085330  /* Verde oscuro */
--canaveral-yellow: #FFB900      /* Amarillo principal */
--canaveral-yellow-light: #FFD966 /* Amarillo claro */
```

---

## 📱 Responsive Design

### **Breakpoints**
- 🖥️ Desktop: > 768px
- 📱 Tablet: 640px - 768px
- 📱 Mobile: < 640px

### **Adaptaciones Mobile**
- Tabs compactos
- Fuentes reducidas
- Padding ajustado
- Tabla scrollable

---

## 🔄 Próximos Pasos (Opcional)

### **Fase 1: ✅ COMPLETADA**
- [x] Crear tablas en base de datos
- [x] Crear endpoints API (CRUD)
- [x] Crear frontend HTML
- [x] Agregar enlace en dashboard
- [x] Registrar blueprint en app.py

### **Fase 2: 🔜 PENDIENTE (Opcional)**
- [ ] Conectar dropdowns del formulario de carga con las nuevas tablas
- [ ] Reemplazar opciones hardcoded por datos dinámicos
- [ ] Actualizar formulario para usar `/api/tipo-documento/activos`

---

## 🐛 Troubleshooting

### **Error: No se puede acceder al módulo**
1. Verificar que el servidor esté corriendo:
   ```bash
   netstat -ano | findstr ":8099"
   ```

2. Verificar que estés logueado como usuario interno

3. Verificar que el blueprint esté registrado:
   ```python
   # En app.py debe aparecer:
   from modules.facturas_digitales.config_routes import config_facturas_bp
   app.register_blueprint(config_facturas_bp)
   ```

### **Error: Tablas no existen**
Ejecutar el script de creación:
```bash
python crear_tablas_configuracion.py
```

### **Error: Watchdog no detecta cambios**
Reiniciar servidor manualmente:
```bash
python app.py
```

---

## 📞 Soporte

Para cualquier duda o problema:
1. Revisar logs del servidor
2. Verificar permisos de usuario
3. Verificar conexión a base de datos PostgreSQL

---

## ✅ Checklist de Verificación

- [x] Tablas creadas en PostgreSQL
- [x] Datos iniciales insertados
- [x] Endpoints API funcionando
- [x] Frontend responsive
- [x] Modo claro/oscuro
- [x] Enlace en dashboard
- [x] Colores institucionales
- [x] Seguridad con decoradores
- [x] Validaciones en formularios
- [x] Soft delete (activo/inactivo)

---

**🎉 ¡MÓDULO LISTO PARA USAR!**

Accede a: `http://127.0.0.1:8099/facturas-digitales/configuracion`
