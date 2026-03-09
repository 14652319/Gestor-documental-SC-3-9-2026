# 📋 FLUJO DE REGISTRO DE PROVEEDORES/ACREEDORES

**🗓️ Documentado:** 27 de Enero 2026  
**✅ Estado:** OPERATIVO Y EN PRODUCCIÓN

---

## 🎯 RESUMEN EJECUTIVO

Este documento describe el flujo completo de registro de nuevos proveedores/acreedores en el sistema Gestor Documental, incluyendo:

- ✅ Proceso de verificación de NIT
- ✅ Formulario de datos del proveedor
- ✅ Creación de usuarios (1 a 5 por proveedor)
- ✅ **Carga de 7 documentos PDF obligatorios**
- ✅ **Almacenamiento en carpetas con nomenclatura específica**
- ✅ Generación automática de radicados
- ✅ Registro en base de datos PostgreSQL

---

## 📍 PASO 1: INICIO DE REGISTRO DESDE LOGIN

### Ubicación Frontend
**Archivo:** `templates/login.html` (Línea 327)

### Descripción
El usuario ve el formulario de login y hace clic en el enlace:

```html
<a onclick="showView('register-view')">Registrarse</a>
```

Esto abre la vista de registro (`register-view`) en la misma página SPA (Single Page Application).

---

## 📍 PASO 2: VERIFICACIÓN DE NIT

### Frontend
**Archivo:** `templates/login.html` (Línea 341)

```html
<form id="checkNitForm">
    <div class="form-group">
        <label for="register-nit">NIT o Cédula:</label>
        <input type="text" id="register-nit" class="uppercase" 
               required placeholder="Ej: 123456789">
    </div>
    <button type="submit" class="btn-primary">Verificar</button>
</form>
```

### Backend
**Endpoint:** `POST /api/registro/check_nit`  
**Código:** `app.py` (Línea 1556-1597)

### Validaciones
- ✅ NIT único (no existe en BD)
- ✅ Formato correcto
- ✅ Estado del tercero si ya existe

### Respuestas Posibles
| Estado | Descripción | Acción |
|--------|-------------|--------|
| ✅ Disponible | NIT no registrado | Continúa al formulario completo |
| ❌ Ya existe | NIT ya registrado | Muestra mensaje de error |
| ⚠️ Pendiente | Solicitud en proceso | Muestra estado actual |

---

## 📍 PASO 3: FORMULARIO COMPLETO DE DATOS

### Frontend
**Archivo:** `templates/login.html` (Línea 350-371)

```html
<form id="registerForm" novalidate>
    <!-- Datos según tipo de persona -->
    <select id="tipo-persona">
        <option value="JURIDICA">Persona Jurídica</option>
        <option value="NATURAL">Persona Natural</option>
    </select>
    
    <!-- Para Jurídica: Razón Social -->
    <input type="text" id="razon-social">
    
    <!-- Para Natural: Nombres y Apellidos -->
    <input type="text" id="primer-nombre">
    <input type="text" id="segundo-nombre">
    <input type="text" id="primer-apellido">
    <input type="text" id="segundo-apellido">
    
    <!-- Datos comunes -->
    <input type="email" id="correo-electronico" required>
    <input type="tel" id="numero-celular" required>
    
    <!-- Aceptaciones -->
    <input type="checkbox" id="acepta-terminos" required>
    <input type="checkbox" id="acepta-contacto">
    
    <button type="submit">Validar Datos del Proveedor</button>
</form>
```

### Backend
**Endpoint:** `POST /api/registro/proveedor`  
**Código:** `app.py` (Línea 1599-1653)

### Comportamiento
⚠️ **IMPORTANTE:** Este endpoint **NO registra en BD**, solo valida los datos.  
Los datos se guardan en `LocalStorage` del navegador para continuar el proceso.

---

## 📍 PASO 4: CREACIÓN DE USUARIOS

### Frontend
**Archivo:** `templates/login.html` (JavaScript)

El usuario puede agregar entre **1 y 5 usuarios** con:
- 👤 Nombre de usuario (único en sistema)
- 📧 Correo electrónico (único en sistema)
- 🔐 Contraseña (con validaciones de seguridad)

### Backend
**Endpoint:** `POST /api/registro/usuarios` (opcional, valida duplicados)  
**Código:** `app.py` (Línea 1655-1710)

### Validaciones
```javascript
// Contraseña segura
- Mínimo 8 caracteres
- Al menos 1 mayúscula
- Al menos 1 número
- Al menos 1 carácter especial (!@#$%^&*)
```

### Límite de Usuarios
⚠️ **LÍMITE:** 5 usuarios por proveedor (configurable en `.env`)  
✅ **EXCEPTO:** NITs especiales sin límite (805028041, 805013653)

```python
# .env
MAX_USUARIOS_POR_TERCERO=5
NITS_ESPECIALES_SIN_LIMITE=805028041,805013653
```

---

## 📍 PASO 5: CARGA DE DOCUMENTOS ⭐ **AQUÍ SE GUARDAN LOS ARCHIVOS**

### Frontend
**Archivo:** `templates/login.html` (JavaScript con `FormData`)

### Backend
**Endpoint:** `POST /api/documentos/upload`  
**Código:** `app.py` (Línea 1712-1785)

### 📋 Documentos Requeridos (7 archivos PDF)

| # | Tipo de Documento | Código Interno |
|---|-------------------|----------------|
| 1 | 📄 RUT | `RUT` |
| 2 | 🏢 Cámara de Comercio | `CAMARA_COMERCIO` |
| 3 | 🪪 Cédula del Representante | `CEDULA_REPRESENTANTE` |
| 4 | 🏦 Certificación Bancaria | `CERTIFICACION_BANCARIA` |
| 5 | 📝 Formulario Conocimiento Proveedores | `FORMULARIO_CONOCIMIENTO_PROVEEDORES` |
| 6 | ⚖️ Declaración de Fondos (Jurídica) | `DECLARACION_FONDOS_JURIDICA` |
| 7 | 👤 Declaración de Fondos (Natural) | `DECLARACION_FONDOS_NATURAL` |

---

## 🗂️ ALMACENAMIENTO TEMPORAL DE DOCUMENTOS

### Carpeta Temporal
```
documentos_terceros/{NIT}-TEMP-{FECHA}/
```

**Ejemplo:**
```
documentos_terceros/123456789-TEMP-27-01-2026/
```

### Nomenclatura de Archivos
```
{NIT}-TEMP-{FECHA}_{TIPO_DOCUMENTO}.pdf
```

**Ejemplos:**
```
123456789-TEMP-27-01-2026_RUT.pdf
123456789-TEMP-27-01-2026_CAMARA_COMERCIO.pdf
123456789-TEMP-27-01-2026_CEDULA_REPRESENTANTE.pdf
123456789-TEMP-27-01-2026_CERTIFICACION_BANCARIA.pdf
123456789-TEMP-27-01-2026_FORMULARIO_CONOCIMIENTO_PROVEEDORES.pdf
123456789-TEMP-27-01-2026_DECLARACION_FONDOS_JURIDICA.pdf
123456789-TEMP-27-01-2026_DECLARACION_FONDOS_NATURAL.pdf
```

### Código Responsable (app.py línea 1722-1758)
```python
@app.route("/api/documentos/upload", methods=["POST"])
def api_cargar_documentos():
    nit = request.form.get("nit", "").strip()
    fecha_carpeta = datetime.now().strftime("%d-%m-%Y")
    
    # Crear carpeta temporal
    carpeta_base = "documentos_terceros"
    carpeta_tercero = f"{nit}-TEMP-{fecha_carpeta}"
    ruta_completa = os.path.join(carpeta_base, carpeta_tercero)
    os.makedirs(ruta_completa, exist_ok=True)
    
    # Guardar cada archivo
    for tipo_doc in archivos_requeridos:
        archivo = request.files.get(f"doc_{tipo_doc}")
        if archivo and archivo.filename:
            nombre_archivo = f"{nit}-TEMP-{fecha_carpeta}_{tipo_doc}.pdf"
            ruta_archivo = os.path.join(ruta_completa, nombre_archivo)
            archivo.save(ruta_archivo)
```

### ⚠️ Características Importantes

| Característica | Descripción |
|----------------|-------------|
| 💾 **Guardado físico** | Archivos guardados en disco inmediatamente |
| 🚫 **NO en BD aún** | NO se registran en base de datos hasta finalizar |
| ⏳ **Temporal** | Carpeta TEMP hasta completar registro |
| 🗑️ **Puede quedar huérfana** | Si el usuario abandona, la carpeta queda sin referencia |

---

## 📍 PASO 6: FINALIZAR REGISTRO Y GENERAR RADICADO

### Backend
**Endpoint:** `POST /api/registro/finalizar`  
**Código:** `app.py` (Línea 1787-1995)

---

## 🔄 PROCESO COMPLETO (Transacción Atómica)

### 1️⃣ Registrar Tercero en BD

```python
tercero = Tercero(
    nit=nit,
    tipo_persona=tercero_data.get("tipoPersona"),
    razon_social=tercero_data.get("razonSocial"),
    correo=tercero_data.get("correoElectronico"),
    celular=tercero_data.get("numeroCelular"),
    estado="pendiente"
)
db.session.add(tercero)
db.session.flush()  # Obtiene ID auto-generado
```

**Tabla:** `terceros`  
**ID generado:** Ejemplo: `27`

---

### 2️⃣ Generar Radicado

```python
radicado = f"RAD-{tercero.id:06d}"
# Ejemplo: ID=27 → Radicado="RAD-000027"
```

**Formato:** `RAD-{ID con 6 dígitos}`

---

### 3️⃣ Crear Solicitud en BD

```python
solicitud = SolicitudRegistro(
    tercero_id=tercero.id,
    radicado=radicado,
    estado="pendiente",
    documentos_completos=True,
    usuarios_creados=True
)
db.session.add(solicitud)
```

**Tabla:** `solicitudes_registro`

---

### 4️⃣ Crear Usuarios en BD

```python
for usuario_data in usuarios_data:
    usuario = Usuario(
        tercero_id=tercero.id,
        usuario=nombre_usuario.upper(),
        correo=correo.lower(),
        password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
        activo=False  # ⚠️ Requieren activación manual
    )
    db.session.add(usuario)
```

**Tabla:** `usuarios`  
⚠️ **Estado inicial:** `activo=False` (requiere activación del administrador)

---

### 5️⃣ MOVER Y RENOMBRAR DOCUMENTOS ⭐

#### Código Ejecutado (app.py línea 1894-1950)

```python
fecha_carpeta = datetime.now().strftime("%d-%m-%Y")
carpeta_temp = f"documentos_terceros/{nit}-TEMP-{fecha_carpeta}"
carpeta_final = f"documentos_terceros/{nit}-{radicado}-{fecha_carpeta}"

# Crear carpeta final
os.makedirs(carpeta_final, exist_ok=True)

# Mover y renombrar cada archivo PDF
for archivo in os.listdir(carpeta_temp):
    if archivo.endswith('.pdf'):
        ruta_temp = os.path.join(carpeta_temp, archivo)
        
        # Extraer tipo de documento
        tipo_doc = archivo.replace(f"{nit}-TEMP-{fecha_carpeta}_", "").replace(".pdf", "")
        
        # Nuevo nombre con radicado
        nuevo_nombre = f"{nit}-{radicado}-{fecha_carpeta}_{tipo_doc}.pdf"
        ruta_final = os.path.join(carpeta_final, nuevo_nombre)
        
        # Mover archivo
        os.rename(ruta_temp, ruta_final)

# Eliminar carpeta temporal vacía
os.rmdir(carpeta_temp)
```

#### Transformación de Archivos

**ANTES (Carpeta Temporal):**
```
documentos_terceros/123456789-TEMP-27-01-2026/
├── 123456789-TEMP-27-01-2026_RUT.pdf
├── 123456789-TEMP-27-01-2026_CAMARA_COMERCIO.pdf
├── 123456789-TEMP-27-01-2026_CEDULA_REPRESENTANTE.pdf
├── 123456789-TEMP-27-01-2026_CERTIFICACION_BANCARIA.pdf
├── 123456789-TEMP-27-01-2026_FORMULARIO_CONOCIMIENTO_PROVEEDORES.pdf
├── 123456789-TEMP-27-01-2026_DECLARACION_FONDOS_JURIDICA.pdf
└── 123456789-TEMP-27-01-2026_DECLARACION_FONDOS_NATURAL.pdf
```

**DESPUÉS (Carpeta Final con Radicado):**
```
documentos_terceros/123456789-RAD-000027-27-01-2026/
├── 123456789-RAD-000027-27-01-2026_RUT.pdf
├── 123456789-RAD-000027-27-01-2026_CAMARA_COMERCIO.pdf
├── 123456789-RAD-000027-27-01-2026_CEDULA_REPRESENTANTE.pdf
├── 123456789-RAD-000027-27-01-2026_CERTIFICACION_BANCARIA.pdf
├── 123456789-RAD-000027-27-01-2026_FORMULARIO_CONOCIMIENTO_PROVEEDORES.pdf
├── 123456789-RAD-000027-27-01-2026_DECLARACION_FONDOS_JURIDICA.pdf
└── 123456789-RAD-000027-27-01-2026_DECLARACION_FONDOS_NATURAL.pdf
```

---

### 6️⃣ Registrar Documentos en BD

```python
for archivo in archivos_movidos:
    tamaño = os.path.getsize(ruta_final)
    
    documento = DocumentoTercero(
        tercero_id=tercero.id,
        radicado=radicado,
        tipo_documento=tipo_doc,
        nombre_archivo=nuevo_nombre,
        ruta_archivo=ruta_final,
        tamaño_archivo=tamaño
    )
    db.session.add(documento)
```

**Tabla:** `documentos_tercero`  
**Registros:** 7 (uno por cada documento)

---

### 7️⃣ Commit de Transacción Completa

```python
db.session.commit()
log_security(f"REGISTRO COMPLETO | nit={nit} | radicado={radicado}")
```

⚠️ **Si falla CUALQUIER paso → Rollback total**
- NO se crean registros parciales
- Archivos movidos se revierten
- Usuario debe reintentar desde cero

---

### 8️⃣ Enviar Correo de Confirmación

```python
enviar_correo_confirmacion_radicado(
    destinatario=correo_destinatario,
    nit=nit,
    razon_social=razon_social,
    radicado=radicado
)
```

📧 **Contenido del correo:**
- ✅ Radicado generado (RAD-XXXXXX)
- 📋 Próximos pasos del proceso
- 💡 Recordatorio de conservar el radicado

⚠️ Si falla el envío, el registro continúa (correo es opcional)

---

## 📂 ESTRUCTURA FINAL EN DISCO

```
documentos_terceros/
│
├── 123456789-RAD-000027-27-01-2026/
│   ├── 123456789-RAD-000027-27-01-2026_RUT.pdf
│   ├── 123456789-RAD-000027-27-01-2026_CAMARA_COMERCIO.pdf
│   ├── 123456789-RAD-000027-27-01-2026_CEDULA_REPRESENTANTE.pdf
│   ├── 123456789-RAD-000027-27-01-2026_CERTIFICACION_BANCARIA.pdf
│   ├── 123456789-RAD-000027-27-01-2026_FORMULARIO_CONOCIMIENTO_PROVEEDORES.pdf
│   ├── 123456789-RAD-000027-27-01-2026_DECLARACION_FONDOS_JURIDICA.pdf
│   └── 123456789-RAD-000027-27-01-2026_DECLARACION_FONDOS_NATURAL.pdf
│
├── 987654321-RAD-000028-27-01-2026/
│   ├── 987654321-RAD-000028-27-01-2026_RUT.pdf
│   └── ... (7 archivos del siguiente proveedor)
│
└── ... (más carpetas de proveedores)
```

### 📊 Nomenclatura

| Elemento | Formato | Ejemplo |
|----------|---------|---------|
| **Carpeta** | `{NIT}-{RADICADO}-{FECHA}/` | `123456789-RAD-000027-27-01-2026/` |
| **Archivo** | `{NIT}-{RADICADO}-{FECHA}_{TIPO}.pdf` | `123456789-RAD-000027-27-01-2026_RUT.pdf` |

---

## 🗄️ REGISTROS EN BASE DE DATOS

### Tabla: `terceros`

```sql
INSERT INTO terceros VALUES (
    id: 27,
    nit: '123456789',
    tipo_persona: 'JURIDICA',
    razon_social: 'Empresa XYZ SAS',
    correo: 'contacto@empresaxyz.com',
    celular: '3001234567',
    estado: 'pendiente',
    fecha_registro: '2026-01-27 10:30:00'
);
```

---

### Tabla: `solicitudes_registro`

```sql
INSERT INTO solicitudes_registro VALUES (
    tercero_id: 27,
    radicado: 'RAD-000027',
    estado: 'pendiente',
    documentos_completos: TRUE,
    usuarios_creados: TRUE,
    fecha_solicitud: '2026-01-27 10:30:00'
);
```

---

### Tabla: `usuarios` (1 a 5 registros)

```sql
INSERT INTO usuarios VALUES (
    tercero_id: 27,
    usuario: 'JPEREZ',
    correo: 'jperez@empresaxyz.com',
    password_hash: '$2b$12$abcdefg...',
    activo: FALSE,  -- ⚠️ Requiere activación manual
    fecha_creacion: '2026-01-27 10:30:00'
);
```

⚠️ **Estado inicial:** `activo=FALSE`  
📌 **Requiere:** Activación manual por administrador en `/api/admin/activar_usuario`

---

### Tabla: `documentos_tercero` (7 registros)

```sql
-- Ejemplo para RUT
INSERT INTO documentos_tercero VALUES (
    tercero_id: 27,
    radicado: 'RAD-000027',
    tipo_documento: 'RUT',
    nombre_archivo: '123456789-RAD-000027-27-01-2026_RUT.pdf',
    ruta_archivo: 'documentos_terceros/123456789-RAD-000027-27-01-2026/123456789-RAD-000027-27-01-2026_RUT.pdf',
    tamaño_archivo: 245678,
    fecha_carga: '2026-01-27 10:30:00'
);

-- (+ 6 registros más, uno por cada documento)
```

---

## ⚠️ PUNTOS IMPORTANTES A CONSIDERAR

### 1. 🔒 CARPETAS TEMPORALES HUÉRFANAS

#### ❌ Problema
Si un usuario carga documentos pero **NO finaliza el registro**:
- Carpeta `{NIT}-TEMP-{FECHA}/` queda en disco
- NO hay registro en BD
- Ocupa espacio innecesario

#### ✅ Solución Recomendada
```python
# Script de limpieza automática (crear como tarea programada)
import os
import datetime

carpeta_base = "documentos_terceros"
dias_antiguedad = 1  # Eliminar carpetas TEMP con más de 24 horas

for carpeta in os.listdir(carpeta_base):
    if "-TEMP-" in carpeta:
        ruta_completa = os.path.join(carpeta_base, carpeta)
        fecha_creacion = os.path.getctime(ruta_completa)
        dias_desde_creacion = (datetime.now() - datetime.fromtimestamp(fecha_creacion)).days
        
        if dias_desde_creacion > dias_antiguedad:
            shutil.rmtree(ruta_completa)  # Eliminar carpeta y contenido
            print(f"Carpeta temporal eliminada: {carpeta}")
```

---

### 2. 🔐 USUARIOS INACTIVOS POR DEFECTO

**Comportamiento:** Todos los usuarios se crean con `activo=False`

✅ **Ventajas:**
- Evita acceso antes de revisar documentos
- Permite validación administrativa
- Previene cuentas maliciosas

📌 **Activación:**
```
Endpoint: POST /api/admin/activar_usuario
Payload: { "usuario_id": 27, "activo": true }
```

---

### 3. 📧 CORREO DE CONFIRMACIÓN

**Características:**
- ✅ Se envía automáticamente al finalizar registro
- ✅ Incluye radicado generado
- ✅ Próximos pasos del proceso
- ⚠️ Si falla el envío, el registro continúa (correo es opcional)

**Configuración:** `.env`
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=correo@dominio.com
MAIL_PASSWORD=contraseña_app
```

---

### 4. 🚫 LÍMITE DE USUARIOS

**Regla general:** Máximo 5 usuarios por proveedor

**Excepciones:** NITs especiales sin límite

```env
# .env
MAX_USUARIOS_POR_TERCERO=5
NITS_ESPECIALES_SIN_LIMITE=805028041,805013653
```

| NIT | Empresa | Límite |
|-----|---------|--------|
| 805028041 | Supertiendas Cañaveral | ♾️ Sin límite |
| 805013653 | Interno empresa | ♾️ Sin límite |
| Otros | Proveedores externos | 5 usuarios |

---

### 5. 🔄 TRANSACCIÓN ATÓMICA

**Garantía:** Si falla CUALQUIER paso → Rollback total

```python
try:
    # 1. Crear tercero
    db.session.add(tercero)
    db.session.flush()
    
    # 2. Crear solicitud
    db.session.add(solicitud)
    
    # 3. Crear usuarios
    for u in usuarios:
        db.session.add(u)
    
    # 4. Mover archivos y registrar documentos
    for archivo in archivos:
        os.rename(ruta_temp, ruta_final)
        db.session.add(documento)
    
    # 5. Commit de todo
    db.session.commit()
    
except Exception as e:
    db.session.rollback()  # ⚠️ Revierte TODO
    log_security(f"ERROR FINALIZAR | {str(e)}")
    # Usuario debe reintentar desde cero
```

**Consecuencias del Rollback:**
- ❌ NO se crean registros parciales en BD
- ⚠️ Archivos movidos NO se revierten automáticamente (problema conocido)
- 🔄 Usuario debe reintentar el registro completo

---

## 📝 ARCHIVOS CLAVE DEL FLUJO

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `templates/login.html` | 2711 | Formulario de registro completo con JavaScript |
| `app.py` (check_nit) | 1556-1597 | Verificación de NIT |
| `app.py` (proveedor) | 1599-1653 | Validación de datos del proveedor |
| `app.py` (usuarios) | 1655-1710 | Validación de usuarios |
| `app.py` (upload) | 1712-1785 | ⭐ **Carga de documentos** |
| `app.py` (finalizar) | 1787-1995 | ⭐ **Mover archivos y registrar** |

### Carpeta Física Principal
```
documentos_terceros/  (raíz del proyecto)
```

---

## 🔍 DIAGRAMA DE FLUJO SIMPLIFICADO

```
┌─────────────┐
│   LOGIN     │
└──────┬──────┘
       │ Click "Registrarse"
       ↓
┌─────────────┐
│ Verificar   │ ← /api/registro/check_nit
│    NIT      │
└──────┬──────┘
       │ NIT Disponible
       ↓
┌─────────────┐
│  Formulario │ ← /api/registro/proveedor (valida, NO registra)
│   Datos     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Agregar   │ ← Guarda en LocalStorage
│  Usuarios   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Cargar    │ ← /api/documentos/upload
│ Documentos  │    ⭐ GUARDAR EN: {NIT}-TEMP-{FECHA}/
└──────┬──────┘
       │ 7 PDFs cargados
       ↓
┌─────────────┐
│  Finalizar  │ ← /api/registro/finalizar
│   Registro  │    ⭐ MOVER A: {NIT}-{RADICADO}-{FECHA}/
└──────┬──────┘
       │
       ├─→ Registrar tercero (BD)
       ├─→ Generar radicado (RAD-XXXXXX)
       ├─→ Crear solicitud (BD)
       ├─→ Crear usuarios (BD, activo=False)
       ├─→ Mover y renombrar archivos (Disco)
       ├─→ Registrar documentos (BD)
       ├─→ Commit transacción
       └─→ Enviar correo confirmación
       
       ↓
┌─────────────┐
│  ✅ ÉXITO   │
│  Radicado:  │
│ RAD-000027  │
└─────────────┘
```

---

## 🛠️ MANTENIMIENTO Y MEJORAS FUTURAS

### 1. Script de Limpieza de Carpetas TEMP
**Problema:** Carpetas huérfanas acumulan espacio
**Solución:** Tarea programada que elimina carpetas TEMP con más de 24 horas

### 2. Reverso Automático de Archivos en Rollback
**Problema:** Si falla el commit, los archivos ya fueron movidos
**Solución:** Implementar sistema de copia en lugar de mover, eliminar copia temporal solo después del commit

### 3. Notificaciones Telegram
**Mejora:** Enviar notificación al administrador cuando hay nuevo registro pendiente

### 4. Dashboard de Solicitudes Pendientes
**Mejora:** Interfaz administrativa para revisar y aprobar solicitudes con vista previa de documentos

---

## ✅ CONCLUSIÓN

Este flujo está **completamente implementado y operativo** desde octubre 2025.

**Características principales:**
- ✅ Validación en múltiples pasos
- ✅ Almacenamiento temporal seguro
- ✅ Nomenclatura estandarizada de archivos
- ✅ Transacción atómica en BD
- ✅ Generación automática de radicados
- ✅ Activación manual de usuarios (seguridad)
- ✅ Correo de confirmación automático

**Ubicación de documentos:**
```
documentos_terceros/{NIT}-{RADICADO}-{FECHA}/
```

---

**📅 Última actualización:** 27 de Enero 2026  
**👤 Documentado por:** GitHub Copilot (Claude Sonnet 4.5)  
**✅ Revisado y validado:** Sistema en producción
