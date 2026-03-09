# 📁 LÓGICA DE GUARDADO DE FACTURAS DIGITALES

**Fecha de documentación:** 8 de diciembre de 2025  
**Módulo:** `facturas_digitales`  
**Archivo:** `modules/facturas_digitales/routes.py`

---

## 🎯 DESCRIPCIÓN GENERAL

El módulo de Facturas Digitales implementa un sistema de almacenamiento de archivos con **dos flujos distintos** según el tipo de usuario que carga la factura:

1. **Usuario EXTERNO** → Guarda en carpeta temporal → Usuario interno completa campos → Mueve a ubicación final
2. **Usuario INTERNO** → Guarda directamente en ubicación final organizada

---

## 📂 ESTRUCTURA DE CARPETAS

### **Ruta Base Configurable**
```
D:/facturas_digitales/
```
Esta ruta se obtiene de la tabla `config_rutas_facturas` (campo `ruta_local` donde `activa=True`).

### **Estructura para Usuario EXTERNO (Temporal)**
```
D:/facturas_digitales/
└── TEMPORALES/
    └── {NIT}/
        └── {NIT-PREFIJO-FOLIO}/
            ├── {NIT-PREFIJO-FOLIO}-PRINCIPAL.pdf
            ├── {NIT-PREFIJO-FOLIO}_XML.zip
            ├── {NIT-PREFIJO-FOLIO}_SEG.pdf
            └── {NIT-PREFIJO-FOLIO}_SOP1.pdf
```

**Ejemplo:**
```
D:/facturas_digitales/TEMPORALES/14652319/14652319-FE-123/
├── 14652319-FE-123-PRINCIPAL.pdf
├── 14652319-FE-123_XML.zip
├── 14652319-FE-123_SEG.pdf
└── 14652319-FE-123_SOP1.pdf
```

### **Estructura para Usuario INTERNO o después de Completar Campos (Final)**
```
D:/facturas_digitales/
└── {EMPRESA}/
    └── {AÑO}/
        └── {MES}/
            └── {DEPARTAMENTO}/
                └── {FORMA_PAGO}/
                    ├── {NIT-PREFIJO-FOLIO}-PRINCIPAL.pdf
                    ├── {NIT-PREFIJO-FOLIO}_XML.zip
                    ├── {NIT-PREFIJO-FOLIO}_SEG.pdf
                    └── {NIT-PREFIJO-FOLIO}_SOP1.pdf
```

**Ejemplo:**
```
D:/facturas_digitales/SC/2025/12/TIC/CREDITO/
├── 14652319-FE-123-PRINCIPAL.pdf
├── 14652319-FE-123_XML.zip
├── 14652319-FE-123_SEG.pdf
└── 14652319-FE-123_SOP1.pdf
```

---

## 🔄 FLUJOS DE TRABAJO COMPLETOS

### **FLUJO 1: Usuario EXTERNO Carga Factura**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USUARIO EXTERNO CARGA FACTURA                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SISTEMA CREA CARPETA TEMPORAL                            │
│    D:/facturas_digitales/TEMPORALES/{NIT}/{NIT-PREF-FOL}/  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. GUARDA ARCHIVOS EN CARPETA TEMPORAL                      │
│    - PDF Principal                                           │
│    - XML (opcional)                                          │
│    - Seguridad Social (opcional)                            │
│    - Soportes (opcional)                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. GUARDA EN BD CON RUTA COMPLETA                          │
│    factura.ruta_carpeta = D:/facturas_digitales/TEMPORALES/...│
│    factura.estado = 'pendiente_revision'                    │
│    factura.tipo_usuario = 'externo'                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. ESPERA QUE USUARIO INTERNO COMPLETE CAMPOS               │
│    (Empresa, Departamento, Forma Pago, etc.)                │
└─────────────────────────────────────────────────────────────┘
```

### **FLUJO 2: Usuario INTERNO Completa Campos de Factura Externa**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USUARIO INTERNO COMPLETA FORMULARIO                      │
│    - Empresa: SC                                             │
│    - Departamento: TIC                                       │
│    - Forma Pago: CREDITO                                     │
│    - Tipo Documento: FC                                      │
│    - Tipo Servicio: COMP                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SISTEMA DETECTA QUE ESTÁ EN TEMPORALES                  │
│    if 'TEMPORALES' in factura.ruta_carpeta.upper()         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CREA ESTRUCTURA DE CARPETA FINAL                         │
│    D:/facturas_digitales/{EMP}/{AÑO}/{MES}/{DEP}/{PAGO}/   │
│    Ejemplo: D:/facturas_digitales/SC/2025/12/TIC/CREDITO/  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. MUEVE TODOS LOS ARCHIVOS                                 │
│    Origen: D:/facturas_digitales/TEMPORALES/14652319/...   │
│    Destino: D:/facturas_digitales/SC/2025/12/TIC/CREDITO/  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. ELIMINA CARPETAS TEMPORALES VACÍAS                       │
│    - Elimina carpeta de factura                             │
│    - Elimina carpeta de NIT si está vacía                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. ACTUALIZA BASE DE DATOS                                  │
│    factura.empresa = 'SC'                                    │
│    factura.departamento = 'TIC'                              │
│    factura.forma_pago = 'CREDITO'                            │
│    factura.ruta_carpeta = 'D:/facturas_digitales/SC/...'   │
│    factura.estado = 'pendiente_firma'                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. LOG DE SEGURIDAD                                         │
│    MOVIMIENTO TEMPORALES->FINAL | archivos_movidos=4 | ... │
└─────────────────────────────────────────────────────────────┘
```

### **FLUJO 3: Usuario INTERNO Carga Factura Directamente**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USUARIO INTERNO CARGA FACTURA CON TODOS LOS DATOS       │
│    - Empresa: LG                                             │
│    - Departamento: DOM                                       │
│    - Forma Pago: CONTADO                                     │
│    - PDF Principal                                           │
│    - Archivos adicionales                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SISTEMA CREA ESTRUCTURA FINAL DIRECTAMENTE               │
│    D:/facturas_digitales/{EMP}/{AÑO}/{MES}/{DEP}/{PAGO}/   │
│    Ejemplo: D:/facturas_digitales/LG/2025/12/DOM/CONTADO/  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. GUARDA ARCHIVOS DIRECTAMENTE EN UBICACIÓN FINAL         │
│    NO pasa por TEMPORALES                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. GUARDA EN BD CON RUTA COMPLETA                          │
│    factura.ruta_carpeta = D:/facturas_digitales/LG/2025/... │
│    factura.estado = 'pendiente_firma'                       │
│    factura.tipo_usuario = 'interno'                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. LOG DE SEGURIDAD                                         │
│    INTERNO CARGA | empresa=LG | factura=FE-456 | ruta=...  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTACIÓN TÉCNICA

### **Endpoint: POST /facturas-digitales/api/cargar-nueva**

#### **Lógica de Usuario EXTERNO** (Líneas 858-920 aproximadamente)

```python
if tipo_usuario == 'externo':
    # ========================================
    # Usuario EXTERNO: Guardar en TEMPORALES
    # ========================================
    # Estructura: D:/facturas_digitales/TEMPORALES/{NIT}/{NIT-PREFIJO-FOLIO}/
    nombre_carpeta = f"{nit_proveedor}-{prefijo}-{folio}"
    ruta_principal = os.path.join(ruta_base, 'TEMPORALES', nit_proveedor, nombre_carpeta)
    
    # Crear estructura completa
    os.makedirs(ruta_principal, exist_ok=True)
    ruta_anexos = ruta_principal  # Misma carpeta para anexos
    
    # Guardar RUTA COMPLETA en BD (no relativa)
    ruta_completa_bd = ruta_principal
    
    log_security(f"EXTERNO CARGA | nit={nit_proveedor} | factura={prefijo}-{folio} | ruta={ruta_principal}")
```

**Características:**
- ✅ Guarda ruta COMPLETA en BD (no relativa)
- ✅ Crea carpeta por NIT y subfolder por factura
- ✅ Estado inicial: `pendiente_revision`
- ✅ Log de seguridad con detalles completos

#### **Lógica de Usuario INTERNO** (Líneas 921-968 aproximadamente)

```python
else:
    # ========================================
    # Usuario INTERNO: Guardar en ubicación FINAL
    # ========================================
    # Estructura: D:/facturas_digitales/{EMPRESA}/{AÑO}/{MES}/{DEPARTAMENTO}/{FORMA_PAGO}/
    año = fecha_actual.year
    mes = f"{fecha_actual.month:02d}"  # 01, 02, ..., 12
    
    ruta_principal = os.path.join(
        ruta_base,
        empresa,           # SC, LG, etc.
        str(año),          # 2025
        mes,               # 01, 02, etc.
        departamento,      # TIC, DOM, CYS, etc.
        forma_pago if forma_pago else 'SIN_FORMA_PAGO'  # CREDITO, CONTADO, etc.
    )
    
    # Crear estructura completa
    os.makedirs(ruta_principal, exist_ok=True)
    ruta_anexos = ruta_principal  # Misma carpeta para anexos
    
    # Guardar RUTA COMPLETA en BD (no relativa)
    ruta_completa_bd = ruta_principal
    
    log_security(f"INTERNO CARGA | empresa={empresa} | factura={prefijo}-{folio} | ruta={ruta_principal}")
```

**Características:**
- ✅ Guarda ruta COMPLETA en BD (no relativa)
- ✅ Organiza por empresa/año/mes/departamento/forma_pago
- ✅ Estado inicial: `pendiente_firma`
- ✅ Log de seguridad con detalles completos

### **Endpoint: POST /facturas-digitales/api/factura/<id>/actualizar**

#### **Lógica de Movimiento de TEMPORALES a FINAL** (Líneas 1566-1633 aproximadamente)

```python
# ========================================
# 🔥 MOVER ARCHIVOS DE TEMPORALES A UBICACIÓN FINAL
# ========================================
if factura.ruta_carpeta and 'TEMPORALES' in factura.ruta_carpeta.upper():
    # Obtener configuración de rutas
    config = ConfigRutasFacturas.query.filter_by(activa=True).first()
    ruta_base = config.ruta_local if config else 'D:/facturas_digitales'
    
    # 📁 CONSTRUIR RUTA FINAL: {EMPRESA}/{AÑO}/{MES}/{DEPARTAMENTO}/{FORMA_PAGO}/
    año = factura.fecha_emision.year if factura.fecha_emision else datetime.now().year
    mes = f"{factura.fecha_emision.month:02d}" if factura.fecha_emision else f"{datetime.now().month:02d}"
    
    nueva_ruta = os.path.join(
        ruta_base,
        empresa,           # SC, LG, etc.
        str(año),          # 2025
        mes,               # 01, 02, etc.
        departamento,      # TIC, DOM, CYS, etc.
        forma_pago if forma_pago else 'SIN_FORMA_PAGO'  # CREDITO, CONTADO, etc.
    )
    
    # Crear directorio destino si no existe
    os.makedirs(nueva_ruta, exist_ok=True)
    
    # Validar que carpeta temporal existe
    if not os.path.exists(factura.ruta_carpeta):
        log_security(f"⚠️ CARPETA TEMPORAL NO EXISTE | factura_id={id} | ruta={factura.ruta_carpeta}")
        return jsonify({
            'success': False, 
            'message': f'La carpeta temporal no existe: {factura.ruta_carpeta}'
        }), 400
    
    # Mover todos los archivos
    import shutil
    archivos_movidos = 0
    errores = []
    
    for archivo in os.listdir(factura.ruta_carpeta):
        origen = os.path.join(factura.ruta_carpeta, archivo)
        destino = os.path.join(nueva_ruta, archivo)
        
        if os.path.isfile(origen):
            try:
                # Si archivo ya existe en destino, agregar sufijo
                if os.path.exists(destino):
                    nombre, ext = os.path.splitext(archivo)
                    contador = 1
                    while os.path.exists(destino):
                        destino = os.path.join(nueva_ruta, f"{nombre}_{contador}{ext}")
                        contador += 1
                
                shutil.move(origen, destino)
                archivos_movidos += 1
                print(f"✅ Movido: {archivo} -> {nueva_ruta}")
            except Exception as e:
                errores.append(f"{archivo}: {str(e)}")
                print(f"❌ Error moviendo {archivo}: {str(e)}")
    
    # Eliminar carpeta temporal vacía (y carpetas padre si están vacías)
    try:
        os.rmdir(factura.ruta_carpeta)  # Elimina carpeta de factura
        print(f"✅ Carpeta temporal eliminada: {factura.ruta_carpeta}")
        
        # Intentar eliminar carpeta padre (NIT) si está vacía
        carpeta_nit = os.path.dirname(factura.ruta_carpeta)
        if os.path.exists(carpeta_nit) and not os.listdir(carpeta_nit):
            os.rmdir(carpeta_nit)
            print(f"✅ Carpeta NIT eliminada: {carpeta_nit}")
    except Exception as e:
        print(f"⚠️ No se pudo eliminar carpeta temporal: {str(e)}")
    
    # Actualizar ruta en BD
    factura.ruta_carpeta = nueva_ruta
    
    log_security(
        f"MOVIMIENTO TEMPORALES->FINAL | factura_id={id} | "
        f"nit={factura.nit_proveedor} | numero={factura.numero_factura} | "
        f"archivos_movidos={archivos_movidos} | errores={len(errores)} | "
        f"desde={os.path.basename(os.path.dirname(factura.ruta_carpeta))} | "
        f"hacia={empresa}/{año}/{mes}/{departamento}/{forma_pago}"
    )
```

**Características:**
- ✅ Detecta automáticamente si está en TEMPORALES
- ✅ Construye ruta final con todos los componentes
- ✅ Mueve TODOS los archivos (principal, XML, seg. social, soportes)
- ✅ Maneja colisiones de nombres (agrega sufijo _1, _2, etc.)
- ✅ Elimina carpetas temporales vacías (factura y NIT)
- ✅ Actualiza ruta en BD con ruta completa nueva
- ✅ Cambia estado a `pendiente_firma`
- ✅ Log detallado del movimiento con contadores

---

## 📊 MODELO DE BASE DE DATOS

### **Tabla: facturas_digitales**

**Campos relacionados con rutas:**
```sql
ruta_carpeta TEXT,           -- Ruta COMPLETA de la carpeta (ej: D:/facturas_digitales/SC/2025/12/TIC/CREDITO/)
ruta_archivo TEXT,           -- Ruta COMPLETA del archivo principal (ej: D:/facturas_digitales/SC/2025/12/TIC/CREDITO/14652319-FE-123-PRINCIPAL.pdf)
ruta_archivo_principal TEXT, -- Nombre del archivo principal (ej: 14652319-FE-123-PRINCIPAL.pdf)
```

**Campos de estado:**
```sql
estado VARCHAR(50),          -- 'pendiente_revision' (externo) o 'pendiente_firma' (interno/completado)
tipo_usuario VARCHAR(20),    -- 'externo' o 'interno'
```

**Campos de organización:**
```sql
empresa VARCHAR(10),         -- SC, LG, SC1, SC2, etc.
departamento VARCHAR(50),    -- TIC, DOM, CYS, MER, etc.
forma_pago VARCHAR(50),      -- CREDITO, CONTADO, etc.
tipo_documento VARCHAR(10),  -- FC, NC, ND, etc.
tipo_servicio VARCHAR(50),   -- COMP, SERV, BIEN, etc.
```

---

## 🔍 VALIDACIONES Y CONTROLES

### **Al Cargar Factura**
1. ✅ Validar que NIT existe en tabla `terceros`
2. ✅ Validar duplicados (mismo NIT+PREFIJO+FOLIO)
3. ✅ Validar extensiones de archivo permitidas
4. ✅ Validar tamaño máximo de archivo (50 MB)
5. ✅ Calcular hash SHA256 de cada archivo
6. ✅ Guardar ruta COMPLETA (no relativa) en BD

### **Al Completar Campos (Movimiento)**
1. ✅ Validar que factura existe y está en TEMPORALES
2. ✅ Validar campos obligatorios: empresa, departamento
3. ✅ Validar que carpeta temporal existe en disco
4. ✅ Crear carpeta destino si no existe
5. ✅ Manejar colisiones de nombres de archivo
6. ✅ Eliminar carpetas temporales vacías después del movimiento
7. ✅ Actualizar estado a `pendiente_firma`

---

## 📝 LOGS DE SEGURIDAD

### **Carga de Factura Externa**
```
EXTERNO CARGA | nit=14652319 | factura=FE-123 | ruta=D:/facturas_digitales/TEMPORALES/14652319/14652319-FE-123
```

### **Carga de Factura Interna**
```
INTERNO CARGA | empresa=SC | factura=FE-456 | ruta=D:/facturas_digitales/SC/2025/12/TIC/CREDITO
```

### **Movimiento de TEMPORALES a FINAL**
```
MOVIMIENTO TEMPORALES->FINAL | factura_id=7 | nit=14652319 | numero=FE-123 | 
archivos_movidos=4 | errores=0 | desde=14652319 | hacia=SC/2025/12/TIC/CREDITO
```

---

## ⚠️ NOTAS IMPORTANTES

1. **SIEMPRE guarda ruta COMPLETA en BD**, nunca ruta relativa
2. **Carpeta TEMPORALES** debe existir en `D:/facturas_digitales/TEMPORALES/`
3. **Usuario externo** NO puede especificar empresa, departamento, etc. (campos NULL)
4. **Usuario interno** DEBE especificar todos los campos obligatorios
5. **Movimiento de archivos** es atómico: si falla, la factura mantiene ruta temporal
6. **Eliminación de carpetas temporales** es segura: solo elimina si están vacías
7. **Colisiones de nombres** se manejan agregando sufijo `_1`, `_2`, etc.

---

## 🧪 TESTING

### **Test 1: Usuario Externo Carga Factura**
```python
# Simular carga desde usuario externo
POST /facturas-digitales/api/cargar-nueva
{
    "nit": "14652319",
    "prefijo": "FE",
    "folio": "999",
    "tipo_usuario": "externo",
    # ... otros campos
}

# Verificar:
# 1. Archivo en: D:/facturas_digitales/TEMPORALES/14652319/14652319-FE-999/
# 2. BD: estado='pendiente_revision', tipo_usuario='externo'
# 3. BD: empresa=NULL, departamento=NULL
```

### **Test 2: Usuario Interno Completa Campos**
```python
# Completar campos de factura externa
POST /facturas-digitales/api/factura/123/actualizar
{
    "empresa": "SC",
    "departamento": "TIC",
    "formaPago": "CREDITO",
    # ... otros campos
}

# Verificar:
# 1. Archivos movidos a: D:/facturas_digitales/SC/2025/12/TIC/CREDITO/
# 2. BD: estado='pendiente_firma'
# 3. BD: ruta_carpeta actualizada
# 4. Carpeta temporal eliminada
```

### **Test 3: Usuario Interno Carga Directamente**
```python
# Carga directa con todos los datos
POST /facturas-digitales/api/cargar-nueva
{
    "nit": "805013653",
    "prefijo": "FC",
    "folio": "888",
    "tipo_usuario": "interno",
    "empresa": "LG",
    "departamento": "DOM",
    "forma_pago": "CONTADO",
    # ... otros campos
}

# Verificar:
# 1. Archivo en: D:/facturas_digitales/LG/2025/12/DOM/CONTADO/
# 2. BD: estado='pendiente_firma', tipo_usuario='interno'
# 3. NO pasa por TEMPORALES
```

---

## 📚 REFERENCIAS

- **Archivo principal:** `modules/facturas_digitales/routes.py`
- **Modelo:** `modules/facturas_digitales/models.py` → Clase `FacturaDigital`
- **Configuración:** Tabla `config_rutas_facturas` → Campo `ruta_local`
- **Logs:** `logs/security.log`

---

**Última actualización:** 8 de diciembre de 2025  
**Autor:** Sistema Gestor Documental - Supertiendas Cañaveral
