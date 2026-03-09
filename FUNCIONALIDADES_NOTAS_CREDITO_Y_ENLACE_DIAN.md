# ✅ Nuevas Funcionalidades: Notas Crédito + Enlace DIAN

**Fecha:** 27 de febrero de 2026  
**Módulo:** DIAN vs ERP - Visor V2 + Reportes Dinámicos

---

## 🎯 Funcionalidades Implementadas

### 1. 🔴 Valores Negativos para Notas Crédito

**Detección automática:**
- Si `Tipo Documento` contiene:
  * `"Nota de crédito electrónica"`
  * `"Nota de ajuste crédito del documento equivalente"`
- Entonces el campo `Valor` se convierte a **negativo** automáticamente

**Visualización:**
- **Visor HTML (tabla):** Valores negativos en **rojo** y **negrita**
- **Excel descargable:** Valores negativos en **rojo** y **negrita**

**Lógica implementada:**
```python
# Si es nota crédito, convertir a negativo
es_nota_credito = (
    'Nota de crédito electrónica' in tipo_doc or
    'Nota de ajuste crédito del documento equivalente' in tipo_doc
)

valor_final = -abs(valor_original) if es_nota_credito else valor_original
```

---

### 2. 🔗 Columna "Ver DIAN" con Enlace Directo

**Nueva columna en Excel:**
- **Nombre:** `Ver DIAN`
- **Contenido:** Enlace directo al documento en el portal de la DIAN
- **Formato:** `https://catalogo-vpfe.dian.gov.co/User/SearchDocument?DocumentKey={CUFE}`
- **Función:** Copiar + pegar en navegador → abre directamente el documento oficial

**Ejemplo de enlace:**
```
https://catalogo-vpfe.dian.gov.co/User/SearchDocument?DocumentKey=a1b2c3d4e5f6...
```

**Visualización en Excel:**
- Texto: `🔗 Ver en DIAN`
- Formato: Hipervínculo azul clickeable
- Al hacer clic: Abre navegador con el documento

---

### 3. 📥 Exportar Facturas Seleccionadas con Ver DIAN

**Funcionalidad mejorada:**
- **Endpoint:** `/api/exportar_seleccionadas` (POST)
- **Características:**
  * Exporta SOLO las facturas seleccionadas en el visor
  * Aplica valores negativos automáticamente a notas crédito
  * Formatea valores negativos en **rojo** y **negrita**
  * **INCLUYE columna "Ver DIAN"** con hipervínculo al portal DIAN

**Columnas en el Excel exportado (19 total):**
1. NIT Emisor
2. Razón Social
3. Tipo Tercero
4. Fecha Emisión
5. Tipo Documento
6. Prefijo
7. Folio
8. Valor (con formato negativo en rojo)
9. Estado Aprobación
10. Forma de Pago
11. Estado Contable
12. N° Días
13. Usuario Solicitante
14. Usuario Aprobador
15. Observaciones
16. Módulo
17. Causador
18. **CUFE** (código único del documento)
19. **Ver DIAN** (hipervínculo clickeable al portal)

**Cómo usar:**
1. En el Visor V2, marcar checkboxes de facturas deseadas
2. Click en botón **"📥 Exportar seleccionadas"**
3. Se genera Excel con valores negativos y enlace DIAN
4. Abrir Excel → click en hipervínculo **"🔗 Ver en DIAN"** → abre navegador

---

## 📋 Archivos Modificados

### Backend: `modules/dian_vs_erp/routes.py`

**1. API Visor V2** (líneas ~820-840):
```python
# Detectar notas crédito
es_nota_credito = (
    'Nota de crédito electrónica' in tipo_doc or
    'Nota de ajuste crédito del documento equivalente' in tipo_doc
)

# Aplicar signo negativo si corresponde
valor_final = -abs(valor_original) if es_nota_credito else valor_original

datos.append({
    ...
    "valor": valor_final,  # 🔴 Negativo para notas crédito
    ...
})
```

**2. API Reportes Dinámicos** (líneas ~6205-6250):
```python
# Detectar notas crédito y generar enlace DIAN
tipo_doc = registro.tipo_documento or ''
valor_original = float(registro.valor) if registro.valor else 0

es_nota_credito = (
    'Nota de crédito electrónica' in tipo_doc or
    'Nota de ajuste crédito del documento equivalente' in tipo_doc
)

valor_final = -abs(valor_original) if es_nota_credito else valor_original

# 🔗 Enlace DIAN
cufe = registro.cufe or ''
enlace_dian = f"https://catalogo-vpfe.dian.gov.co/User/SearchDocument?DocumentKey={cufe}"

datos_excel.append({
    ...
    'Valor': valor_final,
    'CUFE': cufe,
    'Ver DIAN': enlace_dian  # Nueva columna
})
```

**3. Formato Excel** (líneas ~6265-6280):
```python
# Valores negativos en rojo
if c_idx == 8:  # Columna Valor
    cell.number_format = '#,##0.00'
    cell.alignment = Alignment(horizontal='right')
    
    # 🔴 VALORES NEGATIVOS EN ROJO
    if isinstance(value, (int, float)) and value < 0:
        cell.font = Font(color="FF0000", bold=True)

# Hipervínculo para columna Ver DIAN
if c_idx == 18 and value:  # Última columna
    cell.hyperlink = value
    cell.style = "Hyperlink"
    cell.value = "🔗 Ver en DIAN"
```

**3. API Exportar Seleccionadas** (líneas ~865-1009):
```python
@dian_vs_erp_bp.route('/api/exportar_seleccionadas', methods=['POST'])
def exportar_seleccionadas():
    """Exporta solo las facturas seleccionadas con valores negativos y enlace DIAN"""
    
    datos_seleccionados = request.json.get('datos', [])
    datos_procesados = []
    
    # Procesar cada registro seleccionado
    for row in datos_seleccionados:
        row_copy = row.copy()
        
        # 🔴 DETECTAR NOTAS CRÉDITO Y CONVERTIR A NEGATIVO
        tipo_doc = row.get('tipo_documento', '')
        es_nota_credito = (
            'Nota de crédito electrónica' in tipo_doc or
            'Nota de ajuste crédito del documento equivalente' in tipo_doc
        )
        
        if es_nota_credito and row.get('valor'):
            row_copy['valor'] = -abs(float(row['valor']))
        
        datos_procesados.append(row_copy)
    
    # Crear Excel con 19 columnas (incluyendo CUFE y Ver DIAN)
    headers = [
        'NIT Emisor', 'Razón Social', 'Tipo Tercero', 'Fecha Emisión',
        'Tipo Documento', 'Prefijo', 'Folio', 'Valor',
        'Estado Aprobación', 'Forma de Pago', 'Estado Contable',
        'N° Días', 'Usuario Solicitante', 'Usuario Aprobador',
        'Observaciones', 'Módulo', 'Causador', 'CUFE', 'Ver DIAN'
    ]
    
    # Escribir datos con formato
    for r_idx, row in enumerate(datos_procesados, 2):
        # ... (columnas 1-17 estándar)
        
        # 🔗 COLUMNA CUFE (columna 18)
        cufe = row.get('cufe', '')
        ws.cell(row=r_idx, column=18, value=cufe)
        
        # 🔗 COLUMNA VER DIAN con hipervínculo (columna 19)
        if cufe:
            enlace_dian = f"https://catalogo-vpfe.dian.gov.co/User/SearchDocument?DocumentKey={cufe}"
            cell_link = ws.cell(row=r_idx, column=19, value="🔗 Ver en DIAN")
            cell_link.hyperlink = enlace_dian
            cell_link.style = "Hyperlink"
            cell_link.font = Font(color="0563C1", underline="single")
```

---

### Frontend: `templates/dian_vs_erp/visor_dian_v2.html`

**Columna Valor con formato condicional** (líneas ~353-375):
```javascript
{
  title:"Valor", 
  field:"valor", 
  formatter: function(cell) {
    const valor = cell.getValue();
    if (valor === null || valor === undefined) return '$0.00';
    
    // Formatear como moneda
    const formatoMoneda = new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(valor);
    
    // 🔴 VALORES NEGATIVOS EN ROJO
    if (valor < 0) {
      return `<span style="color: #dc3545; font-weight: bold;">${formatoMoneda}</span>`;
    }
    
    return formatoMoneda;
  },
  hozAlign:"right", 
  headerFilter:"input", 
  width:130
}
```

---

## 📊 Estructura del Excel Generado (Actualizada)

```
Reporte_DIAN_vs_ERP_20260227_HHMMSS.xlsx
│
├── 🗂️ Hoja 1: "Datos"
│   ├── 18 columnas (antes 17)
│   ├── Nueva columna 18: "Ver DIAN" 🔗
│   ├── Columna 8 "Valor":
│   │   • Valores positivos: Negro
│   │   • Valores negativos: ROJO + NEGRITA 🔴
│   │   • Formato: $#,##0.00
│   └── Columna 18 "Ver DIAN":
│       • Hipervínculo clickeable: "🔗 Ver en DIAN"
│       • Abre portal DIAN con el documento
│
├── 📊 Hoja 2: "Resumen"
│   └── Tabla agregada por Tipo de Tercero y Forma de Pago
│
└── 📖 Hoja 3: "Instrucciones"
    └── Guía para crear tabla dinámica manualmente
```

---

## 🧪 Casos de Prueba

### Caso 1: Factura Normal
**Datos:**
- Tipo Documento: `Factura electrónica de venta`
- Valor original: `1.000.000`

**Resultado:**
- Valor en sistema: `$1.000.000`
- Color: Negro (texto normal)

---

### Caso 2: Nota Crédito Electrónica
**Datos:**
- Tipo Documento: `Nota de crédito electrónica`
- Valor original: `500.000`

**Resultado:**
- Valor en sistema: `-$500.000` (automáticamente negativo)
- Color: **ROJO + NEGRITA** 🔴

---

### Caso 3: Nota Ajuste Crédito
**Datos:**
- Tipo Documento: `Nota de ajuste crédito del documento equivalente`
- Valor original: `250.000`

**Resultado:**
- Valor en sistema: `-$250.000` (automáticamente negativo)
- Color: **ROJO + NEGRITA** 🔴

---

### Caso 4: Enlace DIAN
**Datos:**
- CUFE: `a1b2c3d4e5f6789...`

**Resultado en Excel:**
- Columna "Ver DIAN": `🔗 Ver en DIAN` (azul, subrayado)
- Al hacer clic: Abre `https://catalogo-vpfe.dian.gov.co/User/SearchDocument?DocumentKey=a1b2c3d4e5f6789...`
- En el portal DIAN: Muestra el documento oficial con todos sus detalles

---

## 🚀 Cómo Probar

### 1. Reiniciar el servidor:
```cmd
.\REINICIAR_SERVIDOR.bat
```

### 2. Probar en el Visor:
1. Ir a: http://localhost:8099/dian_vs_erp/visor_v2
2. Cargar datos con filtro de fecha
3. **Buscar facturas con notas crédito**:
   - Filtrar por "Tipo Documento" = "Nota de crédito"
4. **Verificar**:
   - Valores deben aparecer en ROJO y negativos
   - Ejemplo: `-$500.000` en rojo

### 3. Probar en Reportes Dinámicos:
1. Ir a: http://localhost:8099/dian_vs_erp/reportes_dinamicos
2. Llenar filtros (fecha desde/hasta + módulo)
3. Click en "📊 Generar Reporte"
4. Esperar descarga del Excel
5. **Abrir Excel y verificar**:
   - Hoja "Datos" debe tener **18 columnas** (antes 17)
   - Última columna: "Ver DIAN" con enlaces
   - Columna "Valor": Negativos en ROJO
6. **Probar enlace DIAN**:
   - Hacer clic en un enlace "🔗 Ver en DIAN"
   - Debe abrir navegador con el documento

---

## 💡 Preguntas Frecuentes

### ¿Por qué se convierten a negativos?
Las notas crédito representan **devoluciones o descuentos**, por lo que contablemente deben restarse. El sistema ahora lo hace automáticamente.

### ¿Qué pasa si edito el valor manualmente?
La conversión a negativo **solo se aplica al cargar los datos**. Si luego editas el valor en el visor, se guardará tal cual lo ingreses.

### ¿El enlace DIAN funciona sin internet?
No, necesitas conexión a internet para abrir el portal de la DIAN.

### ¿Todos los CUFEs tienen documento en la DIAN?
Solo los documentos electrónicos válidos transmitidos a la DIAN. Si el CUFE es inválido o el documento no existe, la DIAN mostrará un error.

### ¿Puedo copiar el enlace desde Excel?
Sí, puedes:
- **Opción 1:** Hacer clic derecho en la celda → "Editar hipervínculo" → Copiar dirección
- **Opción 2:** Hacer clic en la celda → Barra de fórmulas muestra el enlace completo

---

## 📝 Notas Técnicas

### Detección de Notas Crédito
La detección usa `in` (contiene) en lugar de `==` (exacto) para ser más flexible:
```python
'Nota de crédito electrónica' in tipo_doc  # ✅ Flexible
# vs
tipo_doc == 'Nota de crédito electrónica'  # ❌ Muy estricto
```

Esto permite detectar variaciones como:
- `"01 - Nota de crédito electrónica"`
- `"Nota de crédito electrónica (NC)"`

### Función `abs()` para Garantizar Negativo
```python
valor_final = -abs(valor_original)
```
Esto garantiza que **siempre** sea negativo, incluso si:
- El valor ya venía negativo en la base de datos
- Hay un error de duplicación de signo

### Formato de Moneda en Excel
```python
cell.number_format = '#,##0.00'
```
Esto formatea:
- `1000000` → `1.000.000,00`
- `-500000` → `-500.000,00`

### Color Rojo en Excel
```python
cell.font = Font(color="FF0000", bold=True)
```
- `FF0000` = Rojo puro en hexadecimal
- `bold=True` = Negrita para mayor visibilidad

---

## ✅ Checklist de Implementación

- [x] Backend: Detectar notas crédito en API Visor V2
- [x] Backend: Detectar notas crédito en API Reportes Dinámicos
- [x] Backend: Generar enlace DIAN con CUFE
- [x] Backend: Aplicar formato rojo en Excel a negativos
- [x] Backend: Agregar columna "Ver DIAN" con hipervínculo
- [x] Frontend: Formatter para valores negativos en rojo
- [x] Frontend: Formato moneda para columna Valor
- [x] Documentación: Documento técnico completo
- [ ] Testing: Probar con datos reales del sistema
- [ ] Testing: Validar enlaces DIAN funcionan correctamente

---

## 🔄 Próximos Pasos (Tareas Pendientes)

1. **Reiniciar servidor** para aplicar cambios backend
2. **Probar en visor** con datos que contengan notas crédito
3. **Generar Excel** y verificar:
   - 18 columnas (incluye "Ver DIAN")
   - Valores negativos en rojo
   - Enlaces DIAN clickeables
4. **Validar en portal DIAN** que los enlaces abren correctamente

---

**FIN DEL DOCUMENTO**
