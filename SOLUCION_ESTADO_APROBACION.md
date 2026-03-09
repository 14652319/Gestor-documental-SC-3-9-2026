# SOLUCIÓN: Estado Aprobación muestra "No Registra"

## Problema Identificado

La tabla `maestro_dian_vs_erp` tiene 77,139 registros con `cufe = NULL`.
Esto impide que se haga match con la tabla `acuses` (que tiene 714,414 registros).

**Causa:** Los registros actuales en maestro son de una carga anterior, 
antes de que se agregara el campo `cufe` al proceso de consolidación.

## Verificaciones Realizadas

✅ La columna `cufe` existe en la tabla maestro  
✅ El archivo DIAN tiene CUFEs válidos (96 caracteres c/u)  
✅ El código lee correctamente los CUFEs del Excel  
✅ El código escribe correctamente los CUFEs al maestro  
✅ La tabla `dian` tiene 535,350 registros con CUFE  
✅ La tabla `acuses` tiene 714,414 registros con CUFE  
✅ Hay 711,666 coincidencias entre DIAN y ACUSES  

❌ Pero maestro tiene CUFE = NULL para todos los registros

## SOLUCIÓN

### Opción 1: Borrar y Re-procesar (RECOMENDADO)

```sql
-- Paso 1: Hacer backup de datos de causación (por si acaso)
CREATE TABLE backup_maestro_causacion AS
SELECT * FROM maestro_dian_vs_erp
WHERE causada = TRUE 
   OR rechazada = TRUE
   OR doc_causado_por IS NOT NULL;

-- Paso 2: Borrar datos actuales
DELETE FROM maestro_dian_vs_erp;

-- Paso 3: Re-procesar archivos desde la interfaz web
-- (Subir DIAN + ERP + ACUSES nuevamente)
```

### Opción 2: Actualizar CUFEs desde tabla DIAN (MÁS RÁPIDO)

```sql
-- Copiar CUFEs de tabla DIAN a maestro
UPDATE maestro_dian_vs_erp m
SET cufe = d.cufe_cude
FROM dian d
WHERE m.nit_emisor = d.nit_emisor
  AND m.prefijo = d.prefijo
  AND m.folio = d.folio
  AND d.cufe_cude IS NOT NULL
  AND d.cufe_cude != '';

-- Verificar
SELECT COUNT(*) FROM maestro_dian_vs_erp WHERE cufe IS NOT NULL;
-- Debería mostrar ~77,139 (todos los registros)
```

### Paso Final: Re-procesar Estados de Aprobación

Después de actualizar los CUFEs, ejecuta este query para poblar los estados:

```sql
-- Actualizar estados de aprobación desde tabla acuses
UPDATE maestro_dian_vs_erp m
SET estado_aprobacion = a.estado_docto,
    acuses_recibidos = CASE 
        WHEN a.estado_docto = 'Pendiente' THEN 1
        WHEN a.estado_docto = 'Reclamado' THEN 2
        WHEN a.estado_docto = 'Rechazado' THEN 3
        WHEN a.estado_docto = 'Acuse Bien/Servicio' THEN 4
        WHEN a.estado_docto = 'Aceptación Expresa' THEN 5
        WHEN a.estado_docto = 'Aceptación Tácita' THEN 6
        ELSE 0
    END
FROM acuses a
WHERE m.cufe = a.cufe
  AND m.cufe IS NOT NULL
  AND m.cufe != '';

-- Verificar distribución
SELECT 
    estado_aprobacion,
    COUNT(*) as cantidad
FROM maestro_dian_vs_erp
GROUP BY estado_aprobacion
ORDER BY cantidad DESC;
```

## Resultados Esperados

Después de la solución, deberías ver en el Visor V2:

- **Acuse Bien/Servicio**: ~500,000+ registros
- **Aceptación Expresa**: ~100,000+ registros
- **Aceptación Tácita**: ~50,000+ registros
- **Pendiente**: ~30,000 registros
- etc.

En lugar de:
- **No Registra**: 73,128 (94.80%) ❌
- **Pendiente**: 4,011 (5.20%) ❌

## Validación Final

```sql
-- Verificar que haya matches
SELECT 
    'Maestro con CUFE' as metrica,
    COUNT(*) as valor
FROM maestro_dian_vs_erp
WHERE cufe IS NOT NULL

UNION ALL

SELECT 
    'Con estado diferente a No Registra',
    COUNT(*)
FROM maestro_dian_vs_erp
WHERE estado_aprobacion != 'No Registra'

UNION ALL

SELECT 
    'Matches con acuses',
    COUNT(*)
FROM maestro_dian_vs_erp m
INNER JOIN acuses a ON m.cufe = a.cufe;
```

Deberías ver:
- Maestro con CUFE: ~77,000
- Con estado diferente: ~70,000+
- Matches con acuses: ~70,000+

## Nota Importante

**El campo "Fecha" en ACUSES NO es la fecha de las facturas**.  
Es la fecha de generación del reporte. Por eso es NORMAL que:
- DIAN tenga facturas del 13-16 febrero
- ACUSES tenga fecha del 18 febrero

El matching se hace **SOLO por CUFE**, independiente de fechas.

## Scripts de Diagnóstico Creados

Para futuras verificaciones, se crearon:

1. `verificar_match_database.py` - Verifica coincidencias entre tablas
2. `diagnostico_rapido_maestro.py` - Estados en tabla maestro
3. `diagnostico_cufe_null.py` - Verifica por qué CUFE está NULL
4. `diagnostico_lectura_cufe.py` - Verifica lectura desde Excel
5. `comparar_valores_cufe.py` - Compara CUFEs entre archivos
6. `verificar_fechas_archivos.py` - Ver períodos de archivos

## Resumen

**Problema:** CUFE en maestro est  NULL → No hace match con acuses  
**Causa:** Registros de carga anterior (antes de Dec 29, 2025)  
**Solución:** Actualizar CUFEs desde tabla DIAN con UPDATE  
**Resultado:** Estados de aprobación se mostrarán correctamente  

---
**Fecha diagnóstico:** 19 de febrero, 2026  
**Registros afectados:** 77,139  
**Coincidencias DIAN-ACUSES:** 711,666  
