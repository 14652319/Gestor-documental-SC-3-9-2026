# PLAN DE IMPLEMENTACIÓN - Guardar en Tablas Individuales
## Fecha: 19 Febrero 2026

## 🎯 OBJETIVO
Modificar `actualizar_maestro()` para que inserte datos en tablas individuales (dian, erp, acuses) ANTES de consolidar en maestro.

## 📝 CAMBIOS NECESARIOS

### Ubicación: modules/dian_vs_erp/routes.py

### FUNCIÓN: actualizar_maestro()

**Estructura actual:**
```
1. Leer archivo DIAN
2. Leer archivos ERP  
3. Leer archivo ACUSES
4. Consolidar → INSERT maestro
```

**Estructura nueva:**
```
1. Leer archivo DIAN
   → INSERT en tabla dian (con clave, clave_acuse, tipo_tercero, n_dias)

2. Leer archivos ERP
   → INSERT en erp_comercial (con prefijo, folio, clave, doc_causado_por)
   → INSERT en erp_financiero (con prefijo, folio, clave, doc_causado_por)

3. Leer archivo ACUSES
   → INSERT en acuses (con clave_acuse)

4. Consolidar → INSERT maestro (mantener lógica actual)
```

## 🔧 FUNCIONES A AGREGAR

### 1. insertar_dian_bulk(registros: List[dict]) → None
```python
"""Inserta registros en tabla dian usando COPY FROM"""
- Crea buffer io.StringIO
- Para cada registro:
  - Calcula clave = crear_clave_factura(nit, prefijo, folio)
  - Calcula clave_acuse = cufe
  - Calcula tipo_tercero (clasificación)
  - Calcula n_dias
  - Escribe al buffer
- Usa COPY FROM para insert masivo
```

### 2. insertar_erp_comercial_bulk(registros: List[dict]) → None
```python
"""Inserta registros en erp_comercial usando COPY FROM"""
- Extrae prefijo y folio de docto_proveedor
- Calcula clave_erp_comercial
- Calcula doc_causado_por
- COPY FROM insert masivo
```

### 3. insertar_erp_financiero_bulk(registros: List[dict]) → None
Similar a comercial

### 4. insertar_acuses_bulk(registros: List[dict]) → None
```python
"""Inserta registros en acuses usando COPY FROM"""
- Calcula clave_acuse = cufe
- COPY FROM insert masivo
```

## ⚡ OPTIMIZACIÓN

**Mantener velocidad:**
- Usar COPY FROM (nativo PostgreSQL) para todas las inserts
- Procesar en memoria primero
- Insertar en bloques grandes

**Orden de ejecución:**
1. INSERT dian (535K registros) → 21 segundos
2. INSERT erp_comercial (432K registros) → 17 segundos  
3. INSERT erp_financiero (29K registros) → 1 segundo
4. INSERT acuses (714K registros) → 28 segundos
5. INSERT maestro (78K registros) → 3 segundos

**Total estimado: ~70 segundos** (vs 8 segundos actual, pero con datos completos)

## 🐛 CONSIDERACIONES

1. **Duplicados:** Usar ON CONFLICT DO NOTHING en claves únicas
2. **Encoding:** Manejar caracteres especiales en buffer
3. **Transacciones:** Usar BEGIN/COMMIT para atomicidad
4. **Rollback:** Si falla cualquier paso, hacer rollback completo

## 📊 VALIDACIÓN POST-CARGA

Después de implementar, verificar:
```sql
-- Todas las tablas deben tener datos
SELECT 'dian' as tabla, COUNT(*) FROM dian
UNION ALL SELECT 'erp_comercial', COUNT(*) FROM erp_comercial
UNION ALL SELECT 'erp_financiero', COUNT(*) FROM erp_financiero
UNION ALL SELECT 'acuses', COUNT(*) FROM acuses
UNION ALL SELECT 'maestro', COUNT(*) FROM maestro_dian_vs_erp;

-- Verificar campos calculados
SELECT clave, clave_acuse, tipo_tercero, n_dias 
FROM dian LIMIT 5;

SELECT clave_erp_comercial, doc_causado_por
FROM erp_comercial LIMIT 5;
```

## ✅ RESULTADO ESPERADO

Después de "Procesar & Consolidar":
- ✅ Tabla dian: 535,350 registros con clave y cufe
- ✅ Tabla erp_comercial: 432,911 registros con clave
- ✅ Tabla erp_financiero: 29,085 registros con clave
- ✅ Tabla acuses: 714,414 registros con clave_acuse
- ✅ Tabla maestro: ~78,000 registros consolidados

Visor V2 muestra datos porque consulta tablas individuales ✅
