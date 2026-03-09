# Mapeo de Columnas - Archivos Excel → Tablas PostgreSQL

**Fecha creación**: 23 de Febrero de 2026
**Fuente**: Información proporcionada por usuario
**Propósito**: Referencia para carga de archivos Excel a base de datos

---

## 📊 Tabla DIAN

| Campo Tabla DIAN | Columna Excel | Ejemplo Valor Excel | Tipo de Campo |
|------------------|---------------|---------------------|---------------|
| id | (auto-generado) | - | auto-increment |
| tipo_documento | Tipo de documento | Factura electrónica | cadena de texto |
| cufe_cude | CUFE/CUDE | 066253dc4aa26d3248656... | cadena de texto |
| folio | **Folio** | 116922, 57, 168 | cadena de texto |
| prefijo | **Prefijo** | F3VB, 1FEV, 1FEA, 6841 | cadena de texto |
| divisa | Divisa | COP | cadena de texto |
| forma_pago | Forma de Pago | 2 | numerico |
| medio_pago | Medio de Pago | 1 | numerico |
| fecha_emision | **Fecha Emisión** | 14-02-2026 | fecha con formato dd-mm-aaaa |
| fecha_recepcion | Fecha Recepción | 14-02-2026 10:36:52 | fecha con formato dd-mm-aaaa |
| nit_emisor | NIT Emisor | 900397839 | cadena de texto |
| nombre_emisor | Nombre Emisor | COMPAÑÍA DSIERRA SAS | cadena de texto |
| nit_receptor | NIT Receptor | 805028041 | numerico |
| nombre_receptor | Nombre Receptor | SUPERTIENDAS CAÑAVERAL A S | cadena de texto |
| iva | IVA | 204219 | numerico |
| ica | ICA | 0 | numerico |
| ic | IC | 0 | numerico |
| inc | INC | 0 | numerico |
| timbre | Timbre | 0 | numerico |
| inc_bolsas | INC Bolsas | 0 | numerico |
| in_carbono | IN Carbono | 0 | numerico |
| in_combustibles | IN Combustibles | 0 | numerico |
| ic_datos | IC Datos | 0 | numerico |
| icl | ICL | 0 | numerico |
| inpp | INPP | 0 | numerico |
| ibua | IBUA | 0 | numerico |
| icui | ICUI | 0 | numerico |
| rete_iva | Rete IVA | 0 | numerico |
| rete_renta | Rete Renta | 0 | numerico |
| rete_ica | Rete ICA | 0 | numerico |
| total | **Total** | 1279054, 204219 | numerico |
| estado | Estado | Aprobado con notificación | cadena de texto |
| grupo | Grupo | Recibido | cadena de texto |
| clave | (generado) | NIT+Prefijo+Folio | cadena de texto |
| clave_acuse | (de ACUSES) | Ver tabla ACUSES | cadena de texto |
| modulo | (calculado) | DEPENDE SI EL NIT Emisor... | cadena de texto |
| tipo_tercero | (calculado) | SI NIT Emisor ESTA EN EL... | cadena de texto |
| n_dias | (calculado) | LA RESTA ENTRE FECHA ACTU... | NUMERO |
| fecha_carga | (sistema) | FECHA EN LA QUE SE SUBE EL... | fecha con formato dd-mm-aaaa |
| fecha_actualizacion | (sistema) | FECHA EN AL QUE SE SUBE OT... | fecha con formato dd-mm-aaaa |

---

## 🗂️ NOTAS IMPORTANTES

### Columnas Críticas (Frecuentes problemas):
1. **Folio**: Debe ser cadena de texto (puede tener valores como "116922", "57", "168")
2. **Prefijo**: Debe ser alfanumérico o cadena de texto (puede ser "F3VB", "1FEV", "1FEA", "6841")
3. **Fecha Emisión**: Con tilde, formato dd-mm-aaaa (ej: "14-02-2026")
4. **Total**: Numérico, valores grandes (ej: 1279054, 204219)

### Columnas Calculadas:
- **clave**: Se genera concatenando NIT Emisor + Prefijo + Folio (últimos 8 dígitos)
- **clave_acuse**: Se obtiene del archivo ACUSES (columna "factura")
- **modulo**: Se calcula según reglas de negocio (COMERCIAL/FINANCIERO)
- **tipo_tercero**: Se calcula según si el NIT está en listados específicos
- **n_dias**: Diferencia entre fecha actual y fecha de emisión

---

## 📝 Tabla ERP COMERCIAL (erp_comercial)

**Archivo**: `ERP_comercial_23022026.xlsx` (o similar)

TODO: Pendiente documentar columnas de ERP Comercial

---

## 📝 Tabla ERP FINANCIERO (erp_financiero)

**Archivo**: `ERP_financiero_23022026.xlsx` (o similar)

TODO: Pendiente documentar columnas de ERP Financiero

---

## 📝 Tabla ACUSES (acuses)

**Archivo**: `acuses_23022026.xlsx` (o similar)

| Campo Tabla | Columna Excel | Notas |
|-------------|---------------|-------|
| factura | (calculada) | Prefijo+Folio - últimos 8 dígitos del folio |

TODO: Pendiente completar mapeo de ACUSES

---

## 🔧 Ubicación de Archivos

### Archivos Excel Subidos:
```
D:\0.1. Backup Equipo Contablilidad\Gestor Documental\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059\uploads\
├── dian\Dian.xlsx
├── erp_cm\ERP_comercial_23022026.xlsx
├── erp_fn\erp_financiero_23022026.xlsx
└── acuses\acuses_23022026.xlsx
```

### Código de Procesamiento:
- Archivo: `modules/dian_vs_erp/routes.py`
- Función principal: `actualizar_maestro()` (línea ~1768)
- Función de lectura: `read_csv()` (línea ~244)

---

## 🐛 Problemas Comunes y Soluciones

### Problema 1: Folio y Prefijo salen NULL/0
**Causa**: Las columnas en Excel están correctas, pero el código normaliza mal los nombres
**Solución**: Verificar que el diccionario `columnas_originales` mapea correctamente

### Problema 2: Fecha Emisión sale con fecha de hoy
**Causa**: Columna "Fecha Emisión" tiene tilde y espacio
**Solución**: El código normaliza "fecha emisión" → "fecha_emision" (sin tilde, con guion bajo)

### Problema 3: Total sale en 0.00
**Causa**: Columna "Total" no se encuentra en el diccionario
**Solución**: Verificar que existe la columna "total" (lowercase) después de normalización

---

**Última actualización**: 23/02/2026 15:00
