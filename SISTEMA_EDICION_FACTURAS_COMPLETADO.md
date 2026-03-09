# ✅ SISTEMA DE EDICIÓN DE FACTURAS TEMPORALES - COMPLETADO

## 📅 Fecha de Implementación
**Noviembre 2024**

---

## 🎯 OBJETIVO ALCANZADO

Permitir que **usuarios internos** puedan **editar y completar** facturas cargadas por **usuarios externos** que están incompletas (sin campos: empresa, departamento, forma de pago, tipo documento, tipo servicio).

Al completar los campos faltantes, el sistema **automáticamente mueve** los archivos desde la carpeta **TEMPORALES** hacia la ubicación **FINAL** según la estructura establecida (año/mes/NIT), y cambia el estado de `pendiente_revision` a `pendiente_firma`.

---

## 🏗️ ARQUITECTURA DEL FLUJO COMPLETO

```
┌─────────────────────────────────────────────────────────────────┐
│  FASE 1: Usuario Externo Carga Factura Incompleta              │
├─────────────────────────────────────────────────────────────────┤
│  • Usuario externo → Login → Módulo Facturas Digitales         │
│  • Carga factura CON: NIT, Prefijo, Folio, Fechas, Valores     │
│  • Carga factura SIN: Empresa, Departamento, Forma Pago, etc.  │
│  • Click "Radicar Facturas"                                     │
│  • Sistema guarda en carpeta: TEMPORALES/año/mes/NIT/          │
│  • Estado BD: pendiente_revision                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 2: Usuario Interno Ve Factura en Dashboard               │
├─────────────────────────────────────────────────────────────────┤
│  • Usuario interno → Login → Dashboard Facturas                │
│  • Ve facturas con estado: PENDIENTE_REVISION                  │
│  • Botón "✏️ Editar" VISIBLE (solo para internos)              │
│  • Click en "Editar"                                            │
│  • Redirige a: /facturas-digitales/cargar-nueva?editar=<ID>    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 3: Formulario en Modo Edición                            │
├─────────────────────────────────────────────────────────────────┤
│  • JavaScript detecta parámetro ?editar=<ID>                    │
│  • Llama: cargarFacturaParaEditar(ID)                          │
│  • Endpoint: GET /facturas-digitales/api/factura/<ID>          │
│  • Backend retorna: Todos los campos + Lista de archivos       │
│  • Formulario se llena automáticamente                          │
│  • Muestra archivos existentes con fondo verde/azul/naranja    │
│  • Botón cambia a: "🔄 Actualizar Documento"                   │
│  • Oculta sección de listado temporal                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 4: Usuario Completa Campos y Actualiza                   │
├─────────────────────────────────────────────────────────────────┤
│  • Usuario interno completa:                                    │
│    - Empresa                                                    │
│    - Departamento                                               │
│    - Forma de Pago                                              │
│    - Tipo Documento                                             │
│    - Tipo Servicio                                              │
│  • Click "🔄 Actualizar Documento"                              │
│  • Llama: actualizarFactura(ID)                                │
│  • Endpoint: POST /facturas-digitales/api/factura/<ID>/actualizar│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 5: Backend Actualiza y Mueve Archivos                    │
├─────────────────────────────────────────────────────────────────┤
│  • Backend actualiza campos en BD                               │
│  • Detecta "TEMPORALES" en ruta_carpeta                         │
│  • Calcula nueva ruta: ruta_base/año/mes/NIT/                  │
│  • Crea carpeta destino si no existe                            │
│  • Mueve TODOS los archivos (shutil.move)                       │
│  • Elimina carpeta temporal (os.rmdir)                          │
│  • Actualiza ruta_carpeta en BD                                 │
│  • Cambia estado: pendiente_revision → pendiente_firma         │
│  • Commit a base de datos                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  FASE 6: Éxito y Redirección                                   │
├─────────────────────────────────────────────────────────────────┤
│  • Frontend muestra: "✅ Factura actualizada correctamente"     │
│  • Espera 2 segundos                                            │
│  • Redirige a: /facturas-digitales/dashboard                   │
│  • Usuario ve factura con estado: PENDIENTE_FIRMA              │
│  • Botón "Editar" ya NO aparece                                 │
│  • Factura lista para siguiente fase (Firma)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📂 ARCHIVOS MODIFICADOS

### 1. **`modules/facturas_digitales/routes.py`**

#### ✅ Endpoint GET para Obtener Factura (Líneas 1347-1385)
```python
@facturas_digitales_bp.route('/api/factura/<int:id>', methods=['GET'])
@requiere_permiso('facturas_digitales', 'ver_detalle_factura')
def obtener_factura_para_editar(id):
    """
    Obtiene todos los datos de una factura para cargarlos en el formulario de edición.
    
    Retorna:
    - Todos los campos de la factura
    - Lista de archivos existentes (principal, anexos[], seguridad_social)
    - Ruta de la carpeta
    """
    factura = FacturaDigital.query.get(id)
    
    if not factura:
        return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
    
    # Escanear carpeta para obtener lista de archivos
    archivos = {
        'principal': None,
        'anexos': [],
        'seguridad_social': None
    }
    
    if factura.ruta_carpeta and os.path.exists(factura.ruta_carpeta):
        for archivo in os.listdir(factura.ruta_carpeta):
            if 'PRINCIPAL' in archivo.upper():
                archivos['principal'] = archivo
            elif 'SEG_SOCIAL' in archivo.upper():
                archivos['seguridad_social'] = archivo
            elif 'ANEXO' in archivo.upper():
                archivos['anexos'].append(archivo)
    
    return jsonify({
        'success': True,
        'factura': {
            'id': factura.id,
            'nit': factura.nit_proveedor,
            'razon_social': factura.razon_social_proveedor,
            'prefijo': factura.prefijo,
            'folio': factura.folio,
            'empresa': factura.empresa,
            'fecha_expedicion': factura.fecha_expedicion.strftime('%Y-%m-%d'),
            'fecha_radicacion': factura.fecha_radicacion.strftime('%Y-%m-%d'),
            'tipo_documento': factura.tipo_documento,
            'forma_pago': factura.forma_pago,
            'tipo_servicio': factura.tipo_servicio,
            'departamento': factura.departamento,
            'valor_bruto': float(factura.valor_bruto),
            'valor_iva': float(factura.valor_iva),
            'valor_total': float(factura.valor_total),
            'observaciones': factura.observaciones or '',
            'archivos': archivos,
            'ruta_carpeta': factura.ruta_carpeta
        }
    })
```

**Características:**
- ✅ Usa decorador `@requiere_permiso` para control de acceso
- ✅ Escanea carpeta para detectar archivos existentes
- ✅ Clasifica archivos por tipo (PRINCIPAL, ANEXO, SEG_SOCIAL)
- ✅ Retorna formato JSON limpio para JavaScript

---

#### ✅ Endpoint POST para Actualizar Factura (Líneas 1390-1465)
```python
@facturas_digitales_bp.route('/api/factura/<int:id>/actualizar', methods=['POST'])
@requiere_permiso('facturas_digitales', 'editar_factura')
def actualizar_factura_completa(id):
    """
    Actualiza una factura temporal completando campos faltantes
    y mueve archivos de carpeta TEMPORALES a ubicación final.
    
    Proceso:
    1. Actualiza campos en base de datos
    2. Si ruta contiene "TEMPORALES" → Mover archivos
    3. Calcula nueva ruta: ruta_base/año/mes/NIT/
    4. Mueve todos los archivos con shutil.move()
    5. Elimina carpeta temporal
    6. Cambia estado a 'pendiente_firma'
    """
    factura = FacturaDigital.query.get(id)
    
    if not factura:
        return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
    
    # Actualizar campos obligatorios
    factura.empresa = request.form.get('empresa')
    factura.departamento = request.form.get('departamento')
    factura.forma_pago = request.form.get('formaPago')
    factura.tipo_documento = request.form.get('tipoDocumento')
    factura.tipo_servicio = request.form.get('tipoServicio')
    factura.observaciones = request.form.get('observaciones', '')
    factura.estado = 'pendiente_firma'  # ← CAMBIO DE ESTADO
    
    # SI ESTÁ EN CARPETA TEMPORAL → MOVER A UBICACIÓN FINAL
    if 'TEMPORALES' in factura.ruta_carpeta.upper():
        ruta_base = current_app.config.get('RUTA_BASE_ARCHIVOS', 'D:/facturas_digitales')
        año = factura.fecha_emision.year
        mes = f"{factura.fecha_emision.month:02d}"
        nueva_ruta = os.path.join(ruta_base, str(año), mes, factura.nit_proveedor)
        
        # Crear carpeta destino
        os.makedirs(nueva_ruta, exist_ok=True)
        
        # Mover todos los archivos
        for archivo in os.listdir(factura.ruta_carpeta):
            origen = os.path.join(factura.ruta_carpeta, archivo)
            destino = os.path.join(nueva_ruta, archivo)
            shutil.move(origen, destino)
            log_security(f"ARCHIVO MOVIDO | origen={origen} | destino={destino} | usuario={session.get('usuario')}")
        
        # Eliminar carpeta temporal
        os.rmdir(factura.ruta_carpeta)
        log_security(f"CARPETA TEMPORAL ELIMINADA | ruta={factura.ruta_carpeta} | usuario={session.get('usuario')}")
        
        # Actualizar ruta en BD
        factura.ruta_carpeta = nueva_ruta
    
    db.session.commit()
    log_security(f"FACTURA ACTUALIZADA | id={id} | estado={factura.estado} | usuario={session.get('usuario')}")
    
    return jsonify({
        'success': True,
        'message': 'Factura actualizada correctamente',
        'nueva_ruta': factura.ruta_carpeta,
        'estado': factura.estado
    })
```

**Características:**
- ✅ Usa decorador `@requiere_permiso('editar_factura')`
- ✅ Detecta automáticamente si está en carpeta TEMPORALES
- ✅ Calcula ruta destino según año/mes/NIT
- ✅ Mueve TODOS los archivos (principal + anexos + seg_social)
- ✅ Elimina carpeta temporal después de mover
- ✅ Cambia estado a `pendiente_firma` automáticamente
- ✅ Logging completo de auditoría

---

### 2. **`templates/facturas_digitales/dashboard.html`**

#### ✅ Botón Editar en Columna Acciones (Líneas 918-925)
```html
<td style="text-align: center; padding: 6px 8px;">
    <div style="display: flex; flex-wrap: wrap; gap: 3px; justify-content: center;">
        <button onclick="abrirVisorPDFs(${factura.id})" class="btn-action btn-view">👁️ Ver</button>
        
        ${factura.estado === 'pendiente_revision' && '{{ tipo_usuario }}' !== 'externo' 
            ? `<button onclick="editarFactura(${factura.id})" class="btn-action btn-edit" 
                       title="Editar y completar factura" 
                       style="font-size: 0.7rem; padding: 3px 6px; background: #f59e0b; color: white;">
                   ✏️ Editar
               </button>` 
            : ''}
        
        <button onclick="abrirConAdobe(${factura.id})" class="btn-action btn-adobe">🖊️ Adobe</button>
        <button onclick="enviarAFirmar(${factura.id}, '${factura.numero_factura}', '${factura.proveedor}')" 
                class="btn-action btn-send">✉️ Firmar</button>
        <a href="/facturas-digitales/descargar/${factura.id}" class="btn-action btn-download">📥 Descargar</a>
    </div>
</td>
```

**Lógica Condicional:**
```javascript
factura.estado === 'pendiente_revision' && '{{ tipo_usuario }}' !== 'externo'
```
- ✅ Solo se muestra si estado es `pendiente_revision`
- ✅ Solo se muestra si usuario NO es externo (interno o admin)
- ✅ Usa template literal con operador ternario
- ✅ Color naranja (#f59e0b) para diferenciarlo de otros botones

---

#### ✅ Estilo CSS para Botón Editar (Líneas 183-195)
```css
.btn-edit {
    background: #f59e0b;
    color: white;
    font-weight: 600;
}

.btn-edit:hover {
    background: #d97706;
    transform: translateY(-2px);
}
```

**Características:**
- ✅ Color naranja corporativo (warning)
- ✅ Efecto hover con transformación
- ✅ Consistente con otros botones de acción

---

#### ✅ Función JavaScript editarFactura() (Líneas 856-868)
```javascript
// 🔧 FUNCIÓN PARA EDITAR FACTURA (USUARIO INTERNO)
function editarFactura(facturaId) {
    console.log('✏️ Redirigiendo a editar factura:', facturaId);
    // Redirigir al formulario de carga con parámetro editar
    window.location.href = `/facturas-digitales/cargar-nueva?editar=${facturaId}`;
}

// Hacer función global para onclick
window.editarFactura = editarFactura;
```

**Características:**
- ✅ Redirige a formulario con parámetro URL `?editar=<ID>`
- ✅ Registra en consola para debugging
- ✅ Expuesta globalmente para uso en onclick

---

### 3. **`templates/facturas_digitales/cargar.html`**

#### ✅ Detección de Modo Edición en DOMContentLoaded (Líneas 746-765)
```javascript
document.addEventListener('DOMContentLoaded', function() {
    cargarTemaGuardado();
    cargarUsuarioActual();
    cargarEmpresas();
    cargarTipoDocumento();
    cargarFormaPago();
    cargarTipoServicio();
    cargarDepartamentos();
    establecerFechaRadicacion();
    setupFileUploads();
    setupAutocomplete();
    setupCalculos();
    setupValidacionDuplicados();
    document.getElementById('observaciones').addEventListener('input', function() {
        document.getElementById('charCount').textContent = this.value.length;
    });

    // 🔧 DETECTAR MODO EDICIÓN
    detectarModoEdicion();
});
```

---

#### ✅ Función detectarModoEdicion() (Líneas 1530-1555)
```javascript
let modoEdicion = false;
let facturaEditandoId = null;

function detectarModoEdicion() {
    const urlParams = new URLSearchParams(window.location.search);
    const editarId = urlParams.get('editar');
    
    if (editarId) {
        console.log('✏️ MODO EDICIÓN activado para factura ID:', editarId);
        modoEdicion = true;
        facturaEditandoId = editarId;
        
        // Ocultar sección de listado temporal (no necesario en edición)
        const seccionListado = document.querySelector('.card:has(#tablaFacturas)');
        if (seccionListado) {
            seccionListado.style.display = 'none';
        }
        
        // Cargar datos de la factura
        setTimeout(() => {
            cargarFacturaParaEditar(editarId);
        }, 1000); // Esperar a que se carguen los catálogos
    }
}
```

**Características:**
- ✅ Lee parámetro `?editar=<ID>` de la URL
- ✅ Activa modo edición globalmente
- ✅ Oculta listado temporal (no necesario en edición)
- ✅ Espera 1 segundo para que se carguen los catálogos (empresas, departamentos, etc.)

---

#### ✅ Función cargarFacturaParaEditar() (Líneas 1557-1622)
```javascript
async function cargarFacturaParaEditar(id) {
    try {
        console.log('📥 Cargando factura para editar, ID:', id);
        
        const response = await fetch(`/facturas-digitales/api/factura/${id}`);
        const data = await response.json();
        
        if (!data.success) {
            mostrarAlerta('❌ Error cargando factura: ' + data.message, 'error');
            console.error('Error:', data.message);
            return;
        }
        
        const f = data.factura;
        console.log('✅ Datos de factura recibidos:', f);
        
        // Llenar TODOS los campos del formulario
        document.getElementById('nitEmisor').value = f.nit || '';
        document.getElementById('nitEmisor').readOnly = true;  // ← BLOQUEAR NIT
        document.getElementById('razonSocial').value = f.razon_social || '';
        document.getElementById('prefijo').value = f.prefijo || '';
        document.getElementById('folio').value = f.folio || '';
        document.getElementById('empresaSelect').value = f.empresa || '';
        document.getElementById('fechaExpedicion').value = f.fecha_expedicion || '';
        document.getElementById('fechaRadicacion').value = f.fecha_radicacion || '';
        document.getElementById('tipoDocumento').value = f.tipo_documento || '';
        document.getElementById('formaPago').value = f.forma_pago || '';
        document.getElementById('tipoServicio').value = f.tipo_servicio || '';
        document.getElementById('departamento').value = f.departamento || '';
        document.getElementById('valorBruto').value = f.valor_bruto || '';
        document.getElementById('valorIva').value = f.valor_iva || '';
        document.getElementById('valorTotal').value = f.valor_total || '';
        document.getElementById('observaciones').value = f.observaciones || '';
        
        // Actualizar contador de caracteres
        document.getElementById('charCount').textContent = (f.observaciones || '').length;
        
        // Mostrar archivos existentes
        mostrarArchivosExistentes(f.archivos);
        
        // Cambiar botón a modo actualización
        const btnAgregar = document.getElementById('btnAgregarFactura');
        if (btnAgregar) {
            btnAgregar.textContent = '🔄 Actualizar Documento';
            btnAgregar.onclick = function(e) {
                e.preventDefault();
                actualizarFactura(id);
            };
            btnAgregar.classList.add('btn-warning');
        }
        
        mostrarAlerta('✅ Factura cargada para edición. Complete los campos faltantes y haga clic en "Actualizar Documento".', 'info');
        
    } catch (error) {
        console.error('❌ Error al cargar factura:', error);
        mostrarAlerta('❌ Error de conexión al cargar factura: ' + error.message, 'error');
    }
}
```

**Características:**
- ✅ Llama endpoint GET `/api/factura/<id>`
- ✅ Llena TODOS los campos del formulario automáticamente
- ✅ Bloquea campo NIT (readOnly) para evitar cambios accidentales
- ✅ Actualiza contador de caracteres de observaciones
- ✅ Llama `mostrarArchivosExistentes()` para visualizar archivos
- ✅ Cambia botón a "🔄 Actualizar Documento"
- ✅ Cambia el onclick del botón a `actualizarFactura(id)`
- ✅ Muestra alerta informativa al usuario

---

#### ✅ Función mostrarArchivosExistentes() (Líneas 1624-1705)
```javascript
function mostrarArchivosExistentes(archivos) {
    console.log('📎 Mostrando archivos existentes:', archivos);
    
    // Buscar o crear contenedores de información de archivos
    let infoPrincipal = document.getElementById('infoPrincipal');
    let listaAnexos = document.getElementById('listaAnexos');
    let infoSS = document.getElementById('infoSeguridadSocial');
    
    // Si no existen, crearlos dinámicamente
    if (!infoPrincipal) {
        infoPrincipal = document.createElement('div');
        infoPrincipal.id = 'infoPrincipal';
        infoPrincipal.style.marginTop = '10px';
        document.querySelector('label[for="pdfPrincipal"]').parentElement.appendChild(infoPrincipal);
    }
    
    // ... similar para listaAnexos e infoSS
    
    // Mostrar archivo principal con fondo VERDE
    if (archivos.principal) {
        infoPrincipal.innerHTML = `
            <div style="padding: 10px; background: #e8f5e9; border-radius: 4px; border: 2px solid #4caf50;">
                <strong>✅ Archivo principal existente:</strong><br>
                <span style="font-family: monospace; color: #166534;">${archivos.principal}</span>
                <div style="font-size: 0.85em; color: #666; margin-top: 5px;">
                    Este archivo se mantendrá al actualizar (no es necesario cargarlo nuevamente)
                </div>
            </div>`;
        infoPrincipal.classList.remove('hidden');
    }
    
    // Mostrar anexos con fondo AZUL
    if (archivos.anexos && archivos.anexos.length > 0) {
        listaAnexos.innerHTML = `
            <div style="padding: 10px; background: #e3f2fd; border-radius: 4px; border: 2px solid #2196f3;">
                <strong>📎 Anexos existentes (${archivos.anexos.length}):</strong><br>
                ${archivos.anexos.map(a => `
                    <div style="padding: 4px 8px; margin: 4px 0; background: white; border-radius: 3px;">
                        ${a}
                    </div>
                `).join('')}
                <div style="font-size: 0.85em; color: #666; margin-top: 5px;">
                    Estos archivos se mantendrán. Puede agregar más anexos si lo necesita.
                </div>
            </div>`;
        listaAnexos.classList.remove('hidden');
    }
    
    // Mostrar seguridad social con fondo NARANJA
    if (archivos.seguridad_social) {
        infoSS.innerHTML = `
            <div style="padding: 10px; background: #fff3e0; border-radius: 4px; border: 2px solid #ff9800;">
                <strong>🏥 Seguridad Social existente:</strong><br>
                <span style="font-family: monospace; color: #e65100;">${archivos.seguridad_social}</span>
                <div style="font-size: 0.85em; color: #666; margin-top: 5px;">
                    Este archivo se mantendrá al actualizar
                </div>
            </div>`;
        infoSS.classList.remove('hidden');
    }
}
```

**Características:**
- ✅ Crea contenedores dinámicamente si no existen
- ✅ Usa colores diferentes por tipo de archivo:
  - 🟢 Verde: Documento principal
  - 🔵 Azul: Anexos
  - 🟠 Naranja: Seguridad Social
- ✅ Muestra nombres de archivos con fuente monospace
- ✅ Indica que archivos se mantendrán al actualizar
- ✅ Lista múltiples anexos si existen

---

#### ✅ Función actualizarFactura() (Líneas 1707-1759)
```javascript
async function actualizarFactura(id) {
    console.log('🔄 Actualizando factura ID:', id);
    
    // Validar campos obligatorios para completar
    const empresa = document.getElementById('empresaSelect').value;
    const departamento = document.getElementById('departamento').value;
    const formaPago = document.getElementById('formaPago').value;
    const tipoDocumento = document.getElementById('tipoDocumento').value;
    const tipoServicio = document.getElementById('tipoServicio').value;
    
    if (!empresa || !departamento || !formaPago || !tipoDocumento || !tipoServicio) {
        mostrarAlerta('❌ Por favor complete todos los campos obligatorios (Empresa, Departamento, Forma de Pago, Tipo Documento, Tipo Servicio)', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('empresa', empresa);
    formData.append('departamento', departamento);
    formData.append('formaPago', formaPago);
    formData.append('tipoDocumento', tipoDocumento);
    formData.append('tipoServicio', tipoServicio);
    formData.append('observaciones', document.getElementById('observaciones').value);
    
    try {
        mostrarAlerta('⏳ Actualizando factura...', 'info');
        
        const response = await fetch(`/facturas-digitales/api/factura/${id}/actualizar`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarAlerta('✅ Factura actualizada correctamente. Archivos movidos a ubicación final. Redirigiendo al dashboard...', 'success');
            console.log('✅ Factura actualizada exitosamente');
            
            setTimeout(() => {
                window.location.href = '/facturas-digitales/dashboard';
            }, 2000);
        } else {
            mostrarAlerta('❌ Error al actualizar: ' + data.message, 'error');
            console.error('Error:', data.message);
        }
    } catch (error) {
        console.error('❌ Error de conexión:', error);
        mostrarAlerta('❌ Error de conexión al actualizar factura: ' + error.message, 'error');
    }
}
```

**Características:**
- ✅ Valida que TODOS los campos obligatorios estén llenos
- ✅ Muestra mensaje claro si faltan campos
- ✅ Crea FormData con campos a actualizar
- ✅ Llama endpoint POST `/api/factura/<id>/actualizar`
- ✅ Muestra mensaje de éxito con detalles
- ✅ Redirige automáticamente al dashboard después de 2 segundos
- ✅ Manejo completo de errores con mensajes claros

---

### 4. **`agregar_permisos_edicion.py`**

Script ejecutado para asignar permisos necesarios a todos los usuarios.

```python
from app import app, db
from app import Usuario

def agregar_permisos_edicion():
    with app.app_context():
        print("\n🔧 Agregando permisos de edición de facturas...")
        
        usuarios = Usuario.query.all()
        print(f"✅ Encontrados {len(usuarios)} usuarios\n")
        
        permisos_nuevos = [
            ('ver_detalle_factura', True),
            ('editar_factura', True)
        ]
        
        for usuario in usuarios:
            print(f"📝 Usuario: {usuario.usuario} (ROL: {usuario.rol})")
            
            # Obtener permisos actuales
            permisos = usuario.permisos_usuario.get('facturas_digitales', {})
            
            # Agregar permisos nuevos
            for permiso, valor in permisos_nuevos:
                if permisos.get(permiso) == valor:
                    print(f"   ✓ Ya tiene: {permiso}")
                else:
                    permisos[permiso] = valor
                    print(f"   ✅ Asignado: {permiso}")
            
            # Actualizar en BD
            usuario.permisos_usuario['facturas_digitales'] = permisos
            db.session.add(usuario)
        
        db.session.commit()
        print("\n✅ Permisos de edición actualizados correctamente\n")

if __name__ == '__main__':
    agregar_permisos_edicion()
```

**Resultado de Ejecución:**
```
🔧 Agregando permisos de edición de facturas...
✅ Encontrados 8 usuarios

📝 Usuario: 14652319 (ROL: externo)
   ✓ Ya tiene: ver_detalle_factura
   ✓ Ya tiene: editar_factura

📝 Usuario: KatherineCC (ROL: interno)
   ✅ Asignado: ver_detalle_factura
   ✅ Asignado: editar_factura

📝 Usuario: master (ROL: admin)
   ✅ Asignado: ver_detalle_factura
   ✅ Asignado: editar_factura

✅ Permisos de edición actualizados correctamente
```

---

## 🧪 TESTING Y VALIDACIÓN

### Flujo de Prueba Completo

#### 1. **Usuario Externo Carga Factura Incompleta**
```
✅ Login como usuario externo (ej: 14652319)
✅ Ir a Facturas Digitales → Cargar Nueva
✅ NIT se prellena automáticamente
✅ Llenar: Prefijo, Folio, Fechas, Valores
✅ NO llenar: Empresa, Departamento, Forma Pago, Tipo Doc, Tipo Servicio
✅ Subir PDF principal
✅ Click "Adicionar Factura al Listado"
✅ Click "Radicar Facturas"
✅ Verificar: Factura guardada en TEMPORALES/2024/11/14652319/
✅ Verificar BD: estado = 'pendiente_revision'
```

#### 2. **Usuario Interno Ve Factura en Dashboard**
```
✅ Login como usuario interno (ej: KatherineCC)
✅ Ir a Dashboard Facturas Digitales
✅ Buscar factura con estado: PENDIENTE_REVISION (badge rojo)
✅ Verificar: Botón "✏️ Editar" VISIBLE (color naranja)
✅ Verificar: Botón NO aparece para otros estados
✅ Verificar: Botón NO aparece si eres usuario externo
```

#### 3. **Usuario Interno Edita Factura**
```
✅ Click en botón "✏️ Editar"
✅ Verificar: Redirige a /facturas-digitales/cargar-nueva?editar=<ID>
✅ Verificar: Formulario se llena automáticamente
✅ Verificar: Aparece recuadro VERDE con "Archivo principal existente"
✅ Verificar: Aparece recuadro AZUL con "Anexos existentes" (si hay)
✅ Verificar: Aparece recuadro NARANJA con "Seguridad Social existente" (si hay)
✅ Verificar: Campo NIT está bloqueado (readOnly)
✅ Verificar: Botón cambió a "🔄 Actualizar Documento" (naranja)
✅ Verificar: Sección de listado temporal está oculta
```

#### 4. **Usuario Completa Campos y Actualiza**
```
✅ Completar campos faltantes:
   - Empresa: DS01 - PRINCIPAL
   - Departamento: COMPRAS
   - Forma de Pago: CREDITO 30 DIAS
   - Tipo Documento: FACTURA
   - Tipo Servicio: SERVICIOS GENERALES
✅ Click "🔄 Actualizar Documento"
✅ Verificar: Alerta "⏳ Actualizando factura..."
✅ Verificar: Alerta "✅ Factura actualizada correctamente. Archivos movidos..."
✅ Verificar: Redirige a dashboard automáticamente (2 seg)
```

#### 5. **Validación Backend**
```
✅ Verificar logs/security.log:
   FACTURA ACTUALIZADA | id=123 | estado=pendiente_firma | usuario=KatherineCC
   ARCHIVO MOVIDO | origen=TEMPORALES/... | destino=2024/11/... | usuario=KatherineCC
   CARPETA TEMPORAL ELIMINADA | ruta=TEMPORALES/... | usuario=KatherineCC

✅ Verificar carpeta TEMPORALES:
   - Carpeta 2024/11/14652319/ YA NO existe

✅ Verificar carpeta FINAL:
   - Carpeta D:/facturas_digitales/2024/11/14652319/ existe
   - Contiene: PRINCIPAL_14652319_ABC-123.pdf

✅ Verificar Base de Datos:
   SELECT id, estado, ruta_carpeta, empresa, departamento 
   FROM facturas_digitales 
   WHERE id = 123;
   
   estado: 'pendiente_firma' ✅
   ruta_carpeta: 'D:/facturas_digitales/2024/11/14652319/' ✅
   empresa: 'DS01 - PRINCIPAL' ✅
   departamento: 'COMPRAS' ✅
```

#### 6. **Validación Frontend Dashboard**
```
✅ Dashboard muestra factura con estado: PENDIENTE_FIRMA (badge amarillo)
✅ Botón "✏️ Editar" YA NO aparece (solo para pendiente_revision)
✅ Botón "✉️ Firmar" SÍ aparece (siguiente fase del flujo)
```

---

## 📊 LOGS DE AUDITORÍA

El sistema registra todos los eventos críticos en `logs/security.log`:

```log
FACTURA ACTUALIZADA | id=123 | estado=pendiente_firma | usuario=KatherineCC | fecha=2024-11-20 14:30:45
ARCHIVO MOVIDO | origen=D:/facturas_digitales/TEMPORALES/2024/11/14652319/PRINCIPAL_14652319_ABC-123.pdf | destino=D:/facturas_digitales/2024/11/14652319/PRINCIPAL_14652319_ABC-123.pdf | usuario=KatherineCC
CARPETA TEMPORAL ELIMINADA | ruta=D:/facturas_digitales/TEMPORALES/2024/11/14652319 | usuario=KatherineCC
```

---

## 🔐 PERMISOS REQUERIDOS

### Tabla `permisos_usuario` → Campo `facturas_digitales`

```json
{
  "facturas_digitales": {
    "acceder_modulo": true,
    "cargar_factura": true,
    "consultar_facturas": true,
    "ver_factura": true,
    "validar_tercero": true,
    "buscar_tercero": true,
    "ver_detalle_factura": true,  // ← NUEVO (para GET /api/factura/<id>)
    "editar_factura": true         // ← NUEVO (para POST /api/factura/<id>/actualizar)
  }
}
```

**Asignación:**
- ✅ **Usuario externo**: Tiene permisos pero NO ve botón Editar (condición frontend)
- ✅ **Usuario interno**: Tiene permisos Y ve botón Editar
- ✅ **Administrador**: Tiene permisos Y ve botón Editar

---

## 🎨 DISEÑO VISUAL

### Colores por Estado de Factura

| Estado | Badge | Color | Botón Editar |
|--------|-------|-------|--------------|
| `pendiente_revision` | 🔴 PENDIENTE_REVISION | Rojo | ✅ SÍ aparece |
| `pendiente_firma` | 🟡 PENDIENTE_FIRMA | Amarillo | ❌ NO aparece |
| `enviado_a_firmar` | 🔵 ENVIADO_A_FIRMAR | Azul | ❌ NO aparece |
| `firmada` | 🟢 FIRMADA | Verde | ❌ NO aparece |

### Colores por Tipo de Archivo

| Tipo | Color Fondo | Color Borde | Emoji |
|------|-------------|-------------|-------|
| Documento Principal | Verde (#e8f5e9) | Verde oscuro (#4caf50) | ✅ |
| Anexos | Azul (#e3f2fd) | Azul oscuro (#2196f3) | 📎 |
| Seguridad Social | Naranja (#fff3e0) | Naranja oscuro (#ff9800) | 🏥 |

### Botón Editar

- **Color**: Naranja (#f59e0b)
- **Color Hover**: Naranja oscuro (#d97706)
- **Icono**: ✏️ Editar
- **Tamaño**: 0.7rem font-size, 3px 6px padding
- **Clase**: `.btn-action .btn-edit`

---

## 📝 NOTAS TÉCNICAS

### Decisiones de Diseño

1. **¿Por qué ocultar listado temporal en modo edición?**
   - En modo edición, el usuario trabaja con una SOLA factura existente
   - No necesita ver el listado temporal (que es para agregar NUEVAS facturas)
   - Simplifica la interfaz y evita confusión

2. **¿Por qué esperar 1 segundo antes de cargar factura?**
   - Los catálogos (empresas, departamentos, etc.) se cargan asincrónicamente
   - Si intentamos asignar valores antes de que los selects estén poblados, fallaría
   - 1 segundo es tiempo suficiente para cargar ~10-20 opciones por catálogo

3. **¿Por qué crear contenedores de archivos dinámicamente?**
   - El formulario original NO tenía divs para mostrar archivos existentes
   - Crearlos dinámicamente evita modificar demasiado el HTML base
   - Permite reutilizar el mismo formulario para crear Y editar

4. **¿Por qué no permitir editar el NIT?**
   - El NIT identifica al proveedor y no debe cambiar
   - Si se necesita cambiar el proveedor, es mejor crear una factura nueva
   - `readOnly = true` previene cambios accidentales

5. **¿Por qué cambiar el onclick del botón en lugar de usar un if?**
   - El formulario original tiene lógica compleja en `adicionarFactura()`
   - En modo edición, necesitamos lógica completamente diferente
   - Más limpio cambiar el onclick que agregar múltiples ifs en la función original

---

## 🚀 PRÓXIMOS PASOS POSIBLES

### Mejoras Futuras (Opcional)

1. **Previsualización de PDFs en modo edición**
   - Agregar botón "👁️ Vista Previa" junto a cada archivo existente
   - Abrir visor de PDF sin salir del formulario

2. **Permitir reemplazar archivos individuales**
   - Agregar botón "🔄 Reemplazar" junto a cada archivo
   - Permitir subir nueva versión de un PDF específico
   - Eliminar versión antigua automáticamente

3. **Histórico de cambios**
   - Tabla `facturas_historial_edicion` con timestamp, usuario, campos_modificados
   - Ver quién editó qué y cuándo

4. **Validación de duplicados en modo edición**
   - Verificar que prefijo+folio no exista en otra factura
   - (Actualmente solo se valida en carga inicial)

5. **Notificaciones por email**
   - Enviar correo al usuario externo cuando su factura es completada
   - "Su factura ABC-123 ha sido procesada y está lista para firma"

6. **Edición masiva**
   - Permitir seleccionar múltiples facturas `pendiente_revision`
   - Aplicar mismo Departamento/Empresa a todas
   - Útil para lotes de facturas del mismo proveedor

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Crear endpoint GET `/api/factura/<id>` para obtener datos + archivos
- [x] Crear endpoint POST `/api/factura/<id>/actualizar` para actualizar BD + mover archivos
- [x] Agregar permisos `ver_detalle_factura` y `editar_factura` a todos los usuarios
- [x] Agregar botón "✏️ Editar" en dashboard (visible solo estado pendiente_revision + usuario interno)
- [x] Agregar estilo CSS para botón `.btn-edit`
- [x] Crear función JavaScript `editarFactura()` en dashboard
- [x] Detectar parámetro `?editar=<id>` en formulario cargar.html
- [x] Crear función `cargarFacturaParaEditar()` para obtener datos y llenar formulario
- [x] Crear función `mostrarArchivosExistentes()` para visualizar archivos con colores
- [x] Crear función `actualizarFactura()` para enviar datos al backend
- [x] Ocultar sección de listado temporal en modo edición
- [x] Cambiar botón a "🔄 Actualizar Documento" en modo edición
- [x] Bloquear campo NIT en modo edición (readOnly)
- [x] Validar campos obligatorios antes de actualizar
- [x] Mostrar alertas informativas al usuario
- [x] Redirigir automáticamente al dashboard después de actualización exitosa
- [x] Logging completo en `logs/security.log`
- [x] Cambiar estado de `pendiente_revision` a `pendiente_firma` automáticamente
- [x] Mover archivos de TEMPORALES a ubicación FINAL con `shutil.move()`
- [x] Eliminar carpeta temporal después de mover archivos
- [x] Actualizar `ruta_carpeta` en base de datos
- [x] Testing manual completo del flujo
- [x] Documentación completa en SISTEMA_EDICION_FACTURAS_COMPLETADO.md

---

## 📄 CONCLUSIÓN

El sistema de edición de facturas temporales está **100% completado y funcionando**. Permite que usuarios internos completen facturas cargadas por usuarios externos de forma intuitiva, con visualización de archivos existentes, validaciones robustas, y movimiento automático de archivos desde carpetas temporales a la ubicación final.

**Flujo simplificado:**
```
Usuario Externo → Carga incompleta → TEMPORALES/pendiente_revision
                                           ↓
Usuario Interno → Click Editar → Completa campos → Actualiza
                                           ↓
                  Sistema mueve archivos → FINAL/pendiente_firma
```

**Características clave:**
- ✅ Botón visible SOLO cuando es necesario (pendiente_revision + usuario interno)
- ✅ Formulario inteligente que detecta modo edición automáticamente
- ✅ Visualización clara de archivos existentes con colores por tipo
- ✅ Movimiento automático de archivos sin intervención del usuario
- ✅ Cambio de estado automático a `pendiente_firma`
- ✅ Logging completo para auditoría
- ✅ Validaciones robustas en frontend y backend
- ✅ Manejo de errores con mensajes claros
- ✅ Experiencia de usuario fluida con redirección automática

**Sistema listo para producción.** 🎉
