/* ============================================
   🎯 GESTOR DE FACTURAS - JAVASCRIPT COMPLETO
   Sistema de Recibir Facturas con Timer 25 min
   Modo Oscuro/Claro, Validaciones, API REST
   ============================================ */

// ============================================
// 🌍 VARIABLES GLOBALES
// ============================================
let facturasData = [];
let proveedoresData = [];
let currentSort = { field: 'fecha_recepcion', direction: 'desc' };
let selectedFacturas = new Set();
let inactivityTimer = null;
let inactivitySeconds = 1500; // 25 minutos = 1500 segundos
let facturaEnEdicion = null;
let modalInactividadMostrado = false;

// ============================================
// ⏰ SISTEMA DE TIMER DE INACTIVIDAD (25 MIN)
// ============================================
function iniciarTimerInactividad() {
    const eventos = ['mousemove', 'keydown', 'scroll', 'click', 'touchstart'];
    
    eventos.forEach(evento => {
        document.addEventListener(evento, resetearTimer);
    });
    
    // Iniciar el contador
    inactivityTimer = setInterval(() => {
        inactivitySeconds--;
        actualizarDisplayTimer();
        
        // Advertencia a 1 minuto
        if (inactivitySeconds === 60 && !modalInactividadMostrado) {
            mostrarModalInactividad();
        }
        
        // Cerrar sesión a 0 segundos
        if (inactivitySeconds === 0) {
            cerrarSesionPorInactividad();
        }
    }, 1000);
}

function resetearTimer() {
    inactivitySeconds = 1500; // Reset a 25 minutos
    modalInactividadMostrado = false;
    cerrarModal('modalInactividad');
    actualizarDisplayTimer();
}

function actualizarDisplayTimer() {
    const minutos = Math.floor(inactivitySeconds / 60);
    const segundos = inactivitySeconds % 60;
    const display = `${minutos}:${segundos.toString().padStart(2, '0')}`;
    
    const timerElement = document.getElementById('timerDisplay');
    const timerContainer = document.getElementById('inactivityTimer');
    
    if (timerElement) {
        timerElement.textContent = display;
    }
    
    // Cambiar colores según tiempo restante
    if (timerContainer) {
        timerContainer.classList.remove('warning', 'danger');
        
        if (inactivitySeconds <= 60) {
            timerContainer.classList.add('danger');
        } else if (inactivitySeconds <= 300) { // 5 minutos
            timerContainer.classList.add('warning');
        }
    }
}

function mostrarModalInactividad() {
    modalInactividadMostrado = true;
    mostrarModal('modalInactividad');
    
    // Actualizar contador en modal
    const intervalo = setInterval(() => {
        const tiempoRestante = document.getElementById('tiempoRestante');
        if (tiempoRestante) {
            const segundos = inactivitySeconds % 60;
            tiempoRestante.textContent = `0:${segundos.toString().padStart(2, '0')}`;
        }
        
        if (inactivitySeconds === 0 || !modalInactividadMostrado) {
            clearInterval(intervalo);
        }
    }, 1000);
}

function continuarSesion() {
    resetearTimer();
    cerrarModal('modalInactividad');
    mostrarToast('success', '✅ Sesión renovada correctamente');
}

function cerrarSesionPorInactividad() {
    clearInterval(inactivityTimer);
    mostrarToast('warning', '⏰ Sesión cerrada por inactividad');
    
    setTimeout(() => {
        window.location.href = '/logout';
    }, 2000);
}

// ============================================
// 🌙 SISTEMA DE TEMA OSCURO/CLARO
// ============================================
function inicializarTema() {
    const temaGuardado = localStorage.getItem('theme') || 'light';
    aplicarTema(temaGuardado);
}

function aplicarTema(tema) {
    document.documentElement.setAttribute('data-theme', tema);
    localStorage.setItem('theme', tema);
    
    const icono = document.getElementById('themeIcon');
    if (icono) {
        icono.textContent = tema === 'dark' ? '☀️' : '🌙';
    }
}

function toggleTema() {
    const temaActual = document.documentElement.getAttribute('data-theme');
    const nuevoTema = temaActual === 'dark' ? 'light' : 'dark';
    aplicarTema(nuevoTema);
}

// ============================================
// 📊 CARGA DE KPIs
// ============================================
async function cargarKPIs() {
    try {
        const response = await fetch('/api/facturas/kpis');
        
        if (!response.ok) {
            throw new Error('Error al cargar KPIs');
        }
        
        const data = await response.json();
        
        if (data.success) {
            const kpis = data.data;
            
            // Animar valores
            animarValor('kpiPendientes', kpis.pendientes || 0);
            animarValor('kpiProximas', kpis.proximas_vencer || 0);
            animarValor('kpiVencidas', kpis.vencidas || 0);
            animarValor('kpiMonto', formatearMoneda(kpis.monto_pendiente || 0));
        }
    } catch (error) {
        console.error('Error cargando KPIs:', error);
        mostrarToast('error', 'Error al cargar estadísticas');
    }
}

function animarValor(elementId, valorFinal) {
    const elemento = document.getElementById(elementId);
    if (!elemento) return;
    
    // Remover skeleton si existe
    const skeleton = elemento.querySelector('.skeleton');
    if (skeleton) {
        skeleton.remove();
    }
    
    // Si es texto (moneda), mostrar directamente
    if (typeof valorFinal === 'string') {
        elemento.textContent = valorFinal;
        return;
    }
    
    // Animación numérica
    let valorActual = 0;
    const duracion = 1000;
    const incremento = valorFinal / (duracion / 16);
    
    const intervalo = setInterval(() => {
        valorActual += incremento;
        
        if (valorActual >= valorFinal) {
            valorActual = valorFinal;
            clearInterval(intervalo);
        }
        
        elemento.textContent = Math.floor(valorActual);
    }, 16);
}

// ============================================
// 📋 CARGA DE FACTURAS
// ============================================
async function cargarFacturas() {
    try {
        // Obtener filtros
        const filtros = obtenerFiltros();
        
        // Construir query string
        const params = new URLSearchParams();
        Object.keys(filtros).forEach(key => {
            if (filtros[key]) {
                params.append(key, filtros[key]);
            }
        });
        
        const response = await fetch(`/api/facturas/listar?${params}`);
        
        if (!response.ok) {
            throw new Error('Error al cargar facturas');
        }
        
        const data = await response.json();
        
        if (data.success) {
            facturasData = data.data;
            renderizarTabla();
            actualizarContadorTotal();
        } else {
            mostrarToast('error', data.message || 'Error al cargar facturas');
        }
    } catch (error) {
        console.error('Error cargando facturas:', error);
        mostrarToast('error', 'Error al cargar las facturas');
        
        // Mostrar mensaje en tabla
        const tbody = document.getElementById('facturasTableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align:center;padding:2rem;color:var(--color-danger);">
                    ❌ Error al cargar facturas. Por favor, recargue la página.
                </td>
            </tr>
        `;
    }
}

function obtenerFiltros() {
    return {
        estado: document.getElementById('filterEstado')?.value || '',
        nit: document.getElementById('filterNit')?.value || '',
        fecha_desde: document.getElementById('filterFechaDesde')?.value || '',
        fecha_hasta: document.getElementById('filterFechaHasta')?.value || '',
        buscar: document.getElementById('filterBuscar')?.value || '',
        vencimiento: document.getElementById('filterVencimiento')?.value || ''
    };
}

function aplicarFiltros() {
    cargarFacturas();
    mostrarToast('success', '🔍 Filtros aplicados');
}

function limpiarFiltros() {
    document.getElementById('filterEstado').value = '';
    document.getElementById('filterNit').value = '';
    document.getElementById('filterFechaDesde').value = '';
    document.getElementById('filterFechaHasta').value = '';
    document.getElementById('filterBuscar').value = '';
    document.getElementById('filterVencimiento').value = '';
    
    cargarFacturas();
    mostrarToast('success', '🔄 Filtros limpiados');
}

// ============================================
// 🎨 RENDERIZAR TABLA
// ============================================
function renderizarTabla() {
    const tbody = document.getElementById('facturasTableBody');
    
    if (!facturasData || facturasData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align:center;padding:3rem;color:var(--text-secondary);">
                    📭 No se encontraron facturas con los filtros seleccionados
                </td>
            </tr>
        `;
        return;
    }
    
    // Ordenar datos
    const datosOrdenados = ordenarDatos(facturasData);
    
    tbody.innerHTML = datosOrdenados.map(factura => `
        <tr>
            <td>
                <input type="checkbox" class="checkbox" 
                       value="${factura.id}" 
                       onchange="toggleSeleccion(${factura.id})"
                       ${selectedFacturas.has(factura.id) ? 'checked' : ''}>
            </td>
            <td><strong>${factura.numero_factura}</strong></td>
            <td>${factura.nit}</td>
            <td>${factura.razon_social}</td>
            <td>${formatearFecha(factura.fecha_factura)}</td>
            <td>${formatearFecha(factura.fecha_vencimiento)}</td>
            <td><span class="${obtenerClaseDias(factura.dias_restantes)}">${factura.dias_restantes} días</span></td>
            <td>${formatearMoneda(factura.valor_neto)}</td>
            <td><span class="badge ${factura.estado.toLowerCase()}">${factura.estado}</span></td>
            <td>
                <div style="display:flex;gap:0.5rem;">
                    <button class="btn btn-secondary" style="padding:0.4rem 0.8rem;font-size:0.85rem;" 
                            onclick="verDetalle(${factura.id})" title="Ver detalle">
                        👁️
                    </button>
                    ${factura.estado === 'RECIBIDA' ? `
                        <button class="btn btn-primary" style="padding:0.4rem 0.8rem;font-size:0.85rem;" 
                                onclick="editarFactura(${factura.id})" title="Editar">
                            ✏️
                        </button>
                        <button class="btn btn-success" style="padding:0.4rem 0.8rem;font-size:0.85rem;" 
                                onclick="validarFactura(${factura.id})" title="Validar">
                            ✅
                        </button>
                        <button class="btn btn-danger" style="padding:0.4rem 0.8rem;font-size:0.85rem;" 
                                onclick="rechazarFactura(${factura.id})" title="Rechazar">
                            ❌
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

function ordenarDatos(datos) {
    return [...datos].sort((a, b) => {
        const aVal = a[currentSort.field];
        const bVal = b[currentSort.field];
        
        if (aVal === null || aVal === undefined) return 1;
        if (bVal === null || bVal === undefined) return -1;
        
        if (currentSort.direction === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
}

function ordenarPor(campo) {
    if (currentSort.field === campo) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.field = campo;
        currentSort.direction = 'asc';
    }
    
    renderizarTabla();
}

function obtenerClaseDias(dias) {
    if (dias < 0) return 'dias-vencida';
    if (dias <= 2) return 'dias-critica';
    if (dias <= 7) return 'dias-urgente';
    if (dias <= 15) return 'dias-proximo';
    return 'dias-normal';
}

function actualizarContadorTotal() {
    const contador = document.getElementById('totalFacturas');
    if (contador) {
        contador.textContent = `(${facturasData.length} registros)`;
    }
}

// ============================================
// 📦 SELECCIÓN MÚLTIPLE
// ============================================
function toggleSeleccion(id) {
    if (selectedFacturas.has(id)) {
        selectedFacturas.delete(id);
    } else {
        selectedFacturas.add(id);
    }
    
    actualizarBotonZip();
}

function toggleSelectAll() {
    const checkbox = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.checkbox[value]');
    
    if (checkbox.checked) {
        checkboxes.forEach(cb => {
            const id = parseInt(cb.value);
            selectedFacturas.add(id);
            cb.checked = true;
        });
    } else {
        selectedFacturas.clear();
        checkboxes.forEach(cb => cb.checked = false);
    }
    
    actualizarBotonZip();
}

function seleccionarTodas() {
    const selectAll = document.getElementById('selectAll');
    if (selectAll) {
        selectAll.checked = true;
        toggleSelectAll();
    }
}

function actualizarBotonZip() {
    const boton = document.getElementById('btnDescargarZip');
    if (boton) {
        boton.disabled = selectedFacturas.size === 0;
        boton.textContent = `📦 Descargar PDFs (${selectedFacturas.size})`;
    }
}

// ============================================
// 👥 CARGA DE PROVEEDORES
// ============================================
async function cargarProveedores() {
    try {
        const response = await fetch('/api/facturas/proveedores');
        
        if (!response.ok) {
            throw new Error('Error al cargar proveedores');
        }
        
        const data = await response.json();
        
        if (data.success) {
            proveedoresData = data.data;
            llenarSelectProveedores();
        }
    } catch (error) {
        console.error('Error cargando proveedores:', error);
        mostrarToast('error', 'Error al cargar lista de proveedores');
    }
}

function llenarSelectProveedores() {
    const select = document.getElementById('tercero_id');
    if (!select) return;
    
    select.innerHTML = '<option value="">Seleccione un proveedor...</option>';
    
    proveedoresData.forEach(proveedor => {
        const option = document.createElement('option');
        option.value = proveedor.id;
        option.textContent = `${proveedor.nit} - ${proveedor.razon_social}`;
        option.dataset.nit = proveedor.nit;
        option.dataset.razon = proveedor.razon_social;
        select.appendChild(option);
    });
    
    // Event listener para auto-llenar
    select.addEventListener('change', function() {
        const option = this.options[this.selectedIndex];
        if (option.value) {
            document.getElementById('nit').value = option.dataset.nit || '';
            document.getElementById('razon_social').value = option.dataset.razon || '';
        } else {
            document.getElementById('nit').value = '';
            document.getElementById('razon_social').value = '';
        }
    });
}

// ============================================
// ➕ CREAR/EDITAR FACTURA
// ============================================
function mostrarModalCrear() {
    facturaEnEdicion = null;
    document.getElementById('modalCrearEditarTitle').innerHTML = '<span>➕</span><span>Nueva Factura</span>';
    document.getElementById('formFactura').reset();
    
    // Deshabilitar campos read-only
    document.getElementById('numero_factura').removeAttribute('readonly');
    
    mostrarModal('modalCrearEditar');
}

async function editarFactura(id) {
    try {
        const response = await fetch(`/api/facturas/${id}`);
        
        if (!response.ok) {
            throw new Error('Error al cargar factura');
        }
        
        const data = await response.json();
        
        if (data.success) {
            facturaEnEdicion = data.data;
            
            // Cambiar título
            document.getElementById('modalCrearEditarTitle').innerHTML = '<span>✏️</span><span>Editar Factura</span>';
            
            // Llenar formulario
            document.getElementById('tercero_id').value = facturaEnEdicion.tercero_id;
            document.getElementById('nit').value = facturaEnEdicion.nit;
            document.getElementById('razon_social').value = facturaEnEdicion.razon_social;
            document.getElementById('numero_factura').value = facturaEnEdicion.numero_factura;
            document.getElementById('fecha_factura').value = facturaEnEdicion.fecha_factura;
            document.getElementById('fecha_vencimiento').value = facturaEnEdicion.fecha_vencimiento;
            document.getElementById('forma_pago').value = facturaEnEdicion.forma_pago || 'CREDITO';
            document.getElementById('plazo_pago').value = facturaEnEdicion.plazo_pago || '';
            document.getElementById('valor_bruto').value = facturaEnEdicion.valor_bruto;
            document.getElementById('valor_descuento').value = facturaEnEdicion.valor_descuento || 0;
            document.getElementById('valor_iva').value = facturaEnEdicion.valor_iva || 0;
            document.getElementById('valor_retefuente').value = facturaEnEdicion.valor_retefuente || 0;
            document.getElementById('valor_reteiva').value = facturaEnEdicion.valor_reteiva || 0;
            document.getElementById('valor_reteica').value = facturaEnEdicion.valor_reteica || 0;
            document.getElementById('valor_neto').value = facturaEnEdicion.valor_neto;
            document.getElementById('observaciones').value = facturaEnEdicion.observaciones || '';
            
            // Deshabilitar número de factura en edición
            document.getElementById('numero_factura').setAttribute('readonly', 'readonly');
            
            mostrarModal('modalCrearEditar');
        } else {
            mostrarToast('error', data.message || 'Error al cargar factura');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarToast('error', 'Error al cargar la factura');
    }
}

async function guardarFactura() {
    // Validar formulario
    const form = document.getElementById('formFactura');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Recopilar datos
    const datos = {
        tercero_id: parseInt(document.getElementById('tercero_id').value),
        numero_factura: document.getElementById('numero_factura').value.trim(),
        fecha_factura: document.getElementById('fecha_factura').value,
        fecha_vencimiento: document.getElementById('fecha_vencimiento').value,
        forma_pago: document.getElementById('forma_pago').value,
        plazo_pago: parseInt(document.getElementById('plazo_pago').value) || null,
        valor_bruto: parseFloat(document.getElementById('valor_bruto').value),
        valor_descuento: parseFloat(document.getElementById('valor_descuento').value) || 0,
        valor_iva: parseFloat(document.getElementById('valor_iva').value) || 0,
        valor_retefuente: parseFloat(document.getElementById('valor_retefuente').value) || 0,
        valor_reteiva: parseFloat(document.getElementById('valor_reteiva').value) || 0,
        valor_reteica: parseFloat(document.getElementById('valor_reteica').value) || 0,
        valor_neto: parseFloat(document.getElementById('valor_neto').value),
        observaciones: document.getElementById('observaciones').value.trim() || null
    };
    
    // Validar fechas
    if (new Date(datos.fecha_vencimiento) < new Date(datos.fecha_factura)) {
        mostrarToast('error', '❌ La fecha de vencimiento debe ser posterior a la fecha de factura');
        return;
    }
    
    // Deshabilitar botón
    const btnGuardar = document.getElementById('btnGuardarFactura');
    btnGuardar.disabled = true;
    btnGuardar.innerHTML = '<span>⏳</span><span>Guardando...</span>';
    
    try {
        let response;
        
        if (facturaEnEdicion) {
            // Editar
            response = await fetch(`/api/facturas/${facturaEnEdicion.id}/editar`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos)
            });
        } else {
            // Crear
            response = await fetch('/api/facturas/crear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos)
            });
        }
        
        const data = await response.json();
        
        if (data.success) {
            mostrarToast('success', `✅ Factura ${facturaEnEdicion ? 'actualizada' : 'creada'} exitosamente`);
            cerrarModal('modalCrearEditar');
            cargarFacturas();
            cargarKPIs();
        } else {
            mostrarToast('error', data.message || 'Error al guardar factura');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarToast('error', 'Error al guardar la factura');
    } finally {
        btnGuardar.disabled = false;
        btnGuardar.innerHTML = '<span>💾</span><span>Guardar Factura</span>';
    }
}

function calcularValorNeto() {
    const bruto = parseFloat(document.getElementById('valor_bruto').value) || 0;
    const descuento = parseFloat(document.getElementById('valor_descuento').value) || 0;
    const iva = parseFloat(document.getElementById('valor_iva').value) || 0;
    const retefuente = parseFloat(document.getElementById('valor_retefuente').value) || 0;
    const reteiva = parseFloat(document.getElementById('valor_reteiva').value) || 0;
    const reteica = parseFloat(document.getElementById('valor_reteica').value) || 0;
    
    const neto = bruto - descuento + iva - retefuente - reteiva - reteica;
    
    document.getElementById('valor_neto').value = neto.toFixed(2);
}

// ============================================
// 👁️ VER DETALLE
// ============================================
async function verDetalle(id) {
    try {
        const response = await fetch(`/api/facturas/${id}?include_items=true&include_documentos=true`);
        
        if (!response.ok) {
            throw new Error('Error al cargar detalle');
        }
        
        const data = await response.json();
        
        if (data.success) {
            const factura = data.data;
            
            document.getElementById('modalDetalleTitle').innerHTML = `
                <span>📋</span>
                <span>Detalle: ${factura.numero_factura}</span>
            `;
            
            const contenido = document.getElementById('detalleContent');
            contenido.innerHTML = `
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;">
                    <div>
                        <strong>NIT:</strong> ${factura.nit}
                    </div>
                    <div>
                        <strong>Proveedor:</strong> ${factura.razon_social}
                    </div>
                    <div>
                        <strong>Fecha Factura:</strong> ${formatearFecha(factura.fecha_factura)}
                    </div>
                    <div>
                        <strong>Vencimiento:</strong> ${formatearFecha(factura.fecha_vencimiento)}
                    </div>
                    <div>
                        <strong>Estado:</strong> <span class="badge ${factura.estado.toLowerCase()}">${factura.estado}</span>
                    </div>
                    <div>
                        <strong>Valor Neto:</strong> ${formatearMoneda(factura.valor_neto)}
                    </div>
                </div>
                
                ${factura.observaciones ? `
                    <div style="margin-top:1.5rem;padding:1rem;background:var(--bg-primary);border-radius:8px;">
                        <strong>📝 Observaciones:</strong><br>
                        ${factura.observaciones}
                    </div>
                ` : ''}
                
                ${factura.items && factura.items.length > 0 ? `
                    <h3 style="margin-top:2rem;margin-bottom:1rem;color:var(--brand-green);">📦 Items</h3>
                    <div style="overflow-x:auto;">
                        <table style="width:100%;border-collapse:collapse;">
                            <thead>
                                <tr style="background:var(--bg-primary);">
                                    <th style="padding:0.5rem;text-align:left;">Línea</th>
                                    <th style="padding:0.5rem;text-align:left;">Descripción</th>
                                    <th style="padding:0.5rem;text-align:right;">Cantidad</th>
                                    <th style="padding:0.5rem;text-align:right;">Valor Unit</th>
                                    <th style="padding:0.5rem;text-align:right;">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${factura.items.map(item => `
                                    <tr>
                                        <td style="padding:0.5rem;">${item.linea}</td>
                                        <td style="padding:0.5rem;">${item.descripcion}</td>
                                        <td style="padding:0.5rem;text-align:right;">${item.cantidad}</td>
                                        <td style="padding:0.5rem;text-align:right;">${formatearMoneda(item.valor_unitario)}</td>
                                        <td style="padding:0.5rem;text-align:right;">${formatearMoneda(item.valor_total)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                ` : ''}
            `;
            
            mostrarModal('modalDetalle');
        } else {
            mostrarToast('error', data.message || 'Error al cargar detalle');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarToast('error', 'Error al cargar el detalle');
    }
}

// ============================================
// ✅ VALIDAR FACTURA
// ============================================
let facturaAValidar = null;

function validarFactura(id) {
    facturaAValidar = id;
    document.getElementById('validarObservaciones').value = '';
    mostrarModal('modalValidar');
}

async function confirmarValidar() {
    if (!facturaAValidar) return;
    
    const observaciones = document.getElementById('validarObservaciones').value.trim() || null;
    
    try {
        const response = await fetch(`/api/facturas/${facturaAValidar}/validar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ observaciones })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarToast('success', '✅ Factura validada exitosamente');
            cerrarModal('modalValidar');
            cargarFacturas();
            cargarKPIs();
            facturaAValidar = null;
        } else {
            mostrarToast('error', data.message || 'Error al validar factura');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarToast('error', 'Error al validar la factura');
    }
}

// ============================================
// ❌ RECHAZAR FACTURA
// ============================================
let facturaARechazar = null;

function rechazarFactura(id) {
    facturaARechazar = id;
    document.getElementById('rechazarMotivo').value = '';
    document.getElementById('rechazarMotivoError').style.display = 'none';
    mostrarModal('modalRechazar');
}

async function confirmarRechazar() {
    if (!facturaARechazar) return;
    
    const motivo = document.getElementById('rechazarMotivo').value.trim();
    const errorSpan = document.getElementById('rechazarMotivoError');
    
    if (!motivo) {
        errorSpan.style.display = 'block';
        return;
    }
    
    errorSpan.style.display = 'none';
    
    try {
        const response = await fetch(`/api/facturas/${facturaARechazar}/rechazar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo_rechazo: motivo })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarToast('success', '❌ Factura rechazada');
            cerrarModal('modalRechazar');
            cargarFacturas();
            cargarKPIs();
            facturaARechazar = null;
        } else {
            mostrarToast('error', data.message || 'Error al rechazar factura');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarToast('error', 'Error al rechazar la factura');
    }
}

// ============================================
// 📊 EXPORTAR EXCEL
// ============================================
async function exportarExcel() {
    try {
        const filtros = obtenerFiltros();
        
        const response = await fetch('/api/facturas/exportar_excel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filtros, detallado: false })
        });
        
        if (!response.ok) {
            throw new Error('Error al exportar');
        }
        
        // Descargar archivo
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `facturas_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        mostrarToast('success', '📊 Excel generado exitosamente');
    } catch (error) {
        console.error('Error:', error);
        mostrarToast('error', 'Error al generar el Excel');
    }
}

// ============================================
// 📦 DESCARGAR ZIP
// ============================================
async function descargarSeleccionadasZip() {
    if (selectedFacturas.size === 0) {
        mostrarToast('warning', '⚠️ Seleccione al menos una factura');
        return;
    }
    
    try {
        const ids = Array.from(selectedFacturas);
        
        const response = await fetch('/api/facturas/documentos/descargar_zip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ factura_ids: ids })
        });
        
        if (!response.ok) {
            throw new Error('Error al descargar');
        }
        
        // Descargar archivo
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `facturas_documentos_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        mostrarToast('success', '📦 ZIP descargado exitosamente');
    } catch (error) {
        console.error('Error:', error);
        mostrarToast('error', 'Error al descargar el ZIP');
    }
}

// ============================================
// 🪟 GESTIÓN DE MODALES
// ============================================
function mostrarModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.classList.add('show');
        
        // Cerrar con ESC
        document.addEventListener('keydown', cerrarConEsc);
        
        // Cerrar al hacer clic fuera
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                cerrarModal(idModal);
            }
        });
    }
}

function cerrarModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.classList.remove('show');
        document.removeEventListener('keydown', cerrarConEsc);
    }
}

function cerrarConEsc(e) {
    if (e.key === 'Escape') {
        const modalesAbiertos = document.querySelectorAll('.modal.show');
        modalesAbiertos.forEach(modal => {
            modal.classList.remove('show');
        });
    }
}

// ============================================
// 🍞 TOAST NOTIFICATIONS
// ============================================
function mostrarToast(tipo, mensaje) {
    const iconos = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    toast.innerHTML = `
        <span class="toast-icon">${iconos[tipo] || 'ℹ️'}</span>
        <span class="toast-message">${mensaje}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-cerrar después de 4 segundos
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 4000);
}

// ============================================
// 🔧 UTILIDADES
// ============================================
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(valor);
}

function formatearFecha(fecha) {
    if (!fecha) return '-';
    
    const [anio, mes, dia] = fecha.split('-');
    return `${dia}/${mes}/${anio}`;
}

function cerrarSesion() {
    if (confirm('¿Está seguro de cerrar sesión?')) {
        window.location.href = '/logout';
    }
}

// ============================================
// 🚀 INICIALIZACIÓN
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando sistema de facturas...');
    
    // Inicializar tema
    inicializarTema();
    
    // Event listener para toggle de tema
    const btnTema = document.getElementById('themeToggle');
    if (btnTema) {
        btnTema.addEventListener('click', toggleTema);
    }
    
    // Iniciar timer de inactividad
    iniciarTimerInactividad();
    
    // Cargar datos iniciales
    cargarKPIs();
    cargarFacturas();
    cargarProveedores();
    
    console.log('✅ Sistema inicializado correctamente');
});
