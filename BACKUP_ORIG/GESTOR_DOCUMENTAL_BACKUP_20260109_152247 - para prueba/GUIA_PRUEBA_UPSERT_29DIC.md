# 🧪 GUÍA DE PRUEBA - UPSERT DIAN VS ERP

**Fecha**: 29 Diciembre 2025  
**Versión**: Sistema con UPSERT implementado

---

## 📋 ESTADO ACTUAL DEL SISTEMA

✅ **Servidor corriendo**: http://127.0.0.1:8099  
✅ **UNIQUE constraint creada**: (nit_emisor, prefijo, folio)  
✅ **Registros actuales**: 607,184  
✅ **Duplicados**: 0  
✅ **UPSERT implementado**: Validación de jerarquía funcionando

---

## 🎯 ESCENARIOS DE PRUEBA

### PRUEBA 1: Carga Completa (Baseline)
**Objetivo**: Verificar que la carga completa funciona igual que antes.

#### Pasos:
1. Ir a: http://127.0.0.1:8099/dian_vs_erp/cargar_archivos
2. Subir los 5 archivos:
   - ✅ DIAN
   - ✅ ERP Financiero
   - ✅ ERP Comercial
   - ✅ Errores ERP
   - ✅ Acuses
3. Click en **"Procesar & Consolidar"** (botón verde)
4. Esperar ~8-10 segundos

#### Resultado Esperado:
```
✅ Archivos procesados correctamente
✅ Total de registros: ~607,184 (o similar)
✅ DIAN: ~300,000
✅ ERP FN: ~200,000
✅ ERP CM: ~100,000
✅ Acuses: ~400,000
```

#### Verificación:
```sql
-- Ver total de registros
SELECT COUNT(*) FROM maestro_dian_vs_erp;

-- Ver distribución por estado_aprobacion
SELECT estado_aprobacion, COUNT(*) 
FROM maestro_dian_vs_erp 
GROUP BY estado_aprobacion 
ORDER BY COUNT(*) DESC;

-- Ver distribución por acuses_recibidos
SELECT acuses_recibidos, COUNT(*) 
FROM maestro_dian_vs_erp 
GROUP BY acuses_recibidos 
ORDER BY acuses_recibidos;
```

---

### PRUEBA 2: Carga Parcial (Solo Acuses) ⭐ NUEVA FUNCIONALIDAD
**Objetivo**: Verificar que se pueden cargar solo acuses sin perder DIAN/ERP.

#### Preparación:
1. Tomar nota de un registro específico:
```sql
SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos, razon_social
FROM maestro_dian_vs_erp
WHERE estado_aprobacion = 'Pendiente'
LIMIT 1;

-- Ejemplo de resultado:
-- nit_emisor: 890329874
-- prefijo: FV
-- folio: 12345
-- estado_aprobacion: Pendiente
-- acuses_recibidos: 0
-- razon_social: PROVEEDOR XYZ
```

#### Pasos:
1. **Crear archivo CSV de acuses modificado**:
   - Editar el archivo de acuses
   - Cambiar el registro 890329874-FV-12345 de "Pendiente" a "Acuse Recibido"
   - Guardar como: `acuses_modificado.csv`

2. **Subir solo el archivo de acuses**:
   - Ir a: http://127.0.0.1:8099/dian_vs_erp/cargar_archivos
   - Subir SOLO: `acuses_modificado.csv`
   - NO subir DIAN, ERP FN, ERP CM, Errores
   - Click en **"Procesar & Consolidar"**

3. **Verificar resultado**:
```sql
SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos, razon_social
FROM maestro_dian_vs_erp
WHERE nit_emisor = '890329874' AND prefijo = 'FV' AND folio = '12345';

-- Resultado esperado:
-- nit_emisor: 890329874
-- prefijo: FV
-- folio: 12345
-- estado_aprobacion: Acuse Recibido  ⭐ CAMBIÓ
-- acuses_recibidos: 1  ⭐ CAMBIÓ
-- razon_social: PROVEEDOR XYZ  ✅ SE MANTIENE
```

4. **Verificar que el resto NO se afectó**:
```sql
-- Debe retornar ~607,184 (misma cantidad)
SELECT COUNT(*) FROM maestro_dian_vs_erp;

-- Debe retornar datos de DIAN/ERP intactos
SELECT COUNT(*) 
FROM maestro_dian_vs_erp 
WHERE razon_social IS NOT NULL AND razon_social != '';
```

#### Resultado Esperado:
```
✅ Solo se actualizó el registro 890329874-FV-12345
✅ Estado cambió de "Pendiente" a "Acuse Recibido"
✅ Acuses cambió de 0 a 1
✅ Todos los demás registros se mantienen INTACTOS
✅ Total de registros: 607,184 (sin cambios)
```

---

### PRUEBA 3: Validación de Jerarquía (Acuse Superior) ⭐ CRÍTICA
**Objetivo**: Verificar que un acuse con jerarquía MAYOR actualiza el registro.

#### Preparación:
```sql
-- Buscar un registro con "Acuse Recibido" (jerarquía 2)
SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
FROM maestro_dian_vs_erp
WHERE estado_aprobacion = 'Acuse Recibido'
LIMIT 1;

-- Ejemplo:
-- nit_emisor: 805028041
-- prefijo: NC
-- folio: 98765
-- estado_aprobacion: Acuse Recibido (jerarquía = 2)
-- acuses_recibidos: 1
```

#### Pasos:
1. **Modificar archivo de acuses**:
   - Cambiar 805028041-NC-98765 de "Acuse Recibido" a "Aceptación Expresa"
   - Jerarquía: 2 → 5 (MAYOR)
   - Guardar como: `acuses_jerarquia_mayor.csv`

2. **Subir archivo**:
   - Subir solo `acuses_jerarquia_mayor.csv`
   - Click en **"Procesar & Consolidar"**

3. **Verificar actualización**:
```sql
SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
FROM maestro_dian_vs_erp
WHERE nit_emisor = '805028041' AND prefijo = 'NC' AND folio = '98765';

-- Resultado esperado:
-- estado_aprobacion: Aceptación Expresa  ⭐ SE ACTUALIZÓ (5 > 2)
-- acuses_recibidos: 2  ⭐ SE ACTUALIZÓ (Expresa tiene 2 acuses)
```

#### Resultado Esperado:
```
✅ Estado SE ACTUALIZÓ (jerarquía 5 > 2)
✅ Acuses SE ACTUALIZÓ de 1 a 2
✅ Validación de jerarquía FUNCIONANDO
```

---

### PRUEBA 4: Validación de Jerarquía (Acuse Inferior) ⭐ CRÍTICA
**Objetivo**: Verificar que un acuse con jerarquía MENOR NO actualiza el registro.

#### Preparación:
```sql
-- Buscar un registro con "Aceptación Tácita" (jerarquía 6)
SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
FROM maestro_dian_vs_erp
WHERE estado_aprobacion = 'Aceptación Tácita'
LIMIT 1;

-- Ejemplo:
-- nit_emisor: 890123456
-- prefijo: FV
-- folio: 55555
-- estado_aprobacion: Aceptación Tácita (jerarquía = 6)
-- acuses_recibidos: 2
```

#### Pasos:
1. **Modificar archivo de acuses**:
   - Cambiar 890123456-FV-55555 de "Aceptación Tácita" a "Acuse Recibido"
   - Jerarquía: 6 → 2 (MENOR)
   - Guardar como: `acuses_jerarquia_menor.csv`

2. **Subir archivo**:
   - Subir solo `acuses_jerarquia_menor.csv`
   - Click en **"Procesar & Consolidar"**

3. **Verificar que NO se actualizó**:
```sql
SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
FROM maestro_dian_vs_erp
WHERE nit_emisor = '890123456' AND prefijo = 'FV' AND folio = '55555';

-- Resultado esperado:
-- estado_aprobacion: Aceptación Tácita  ✅ NO CAMBIÓ (6 > 2)
-- acuses_recibidos: 2  ✅ NO CAMBIÓ
```

#### Resultado Esperado:
```
✅ Estado NO se actualizó (jerarquía 2 < 6)
✅ Acuses NO se actualizó (permanece en 2)
✅ Validación de jerarquía BLOQUEÓ el downgrade
```

---

### PRUEBA 5: Inserción de Nuevos Registros
**Objetivo**: Verificar que registros nuevos se insertan correctamente.

#### Pasos:
1. **Crear archivo con registro nuevo**:
```csv
NIT_EMISOR,PREFIJO,FOLIO,RAZON_SOCIAL,ESTADO_APROBACION
999999999,TEST,00001,PROVEEDOR DE PRUEBA,Pendiente
```
   - Guardar como: `acuses_nuevo_registro.csv`

2. **Subir archivo**:
   - Subir solo `acuses_nuevo_registro.csv`
   - Click en **"Procesar & Consolidar"**

3. **Verificar inserción**:
```sql
SELECT nit_emisor, prefijo, folio, razon_social, estado_aprobacion, acuses_recibidos
FROM maestro_dian_vs_erp
WHERE nit_emisor = '999999999' AND prefijo = 'TEST' AND folio = '00001';

-- Resultado esperado:
-- nit_emisor: 999999999
-- prefijo: TEST
-- folio: 00001
-- razon_social: PROVEEDOR DE PRUEBA
-- estado_aprobacion: Pendiente
-- acuses_recibidos: 0
```

#### Resultado Esperado:
```
✅ Registro nuevo SE INSERTÓ correctamente
✅ Total de registros incrementó en 1
✅ Campo acuses_recibidos calculado automáticamente (0)
```

---

### PRUEBA 6: Carga Incremental por Mes
**Objetivo**: Simular carga de datos de un mes nuevo sin afectar meses anteriores.

#### Contexto:
- Datos actuales: Enero - Noviembre 2024
- Necesitas agregar: Diciembre 2024

#### Pasos:
1. **Preparar archivos de diciembre**:
   - Filtrar DIAN: Solo facturas de diciembre 2024
   - Filtrar ERP: Solo movimientos de diciembre 2024
   - Filtrar Acuses: Solo acuses de diciembre 2024
   - Guardar como: `dian_dic2024.csv`, `erp_fn_dic2024.csv`, etc.

2. **Verificar registros pre-carga**:
```sql
-- Registros actuales
SELECT COUNT(*) as total_antes FROM maestro_dian_vs_erp;

-- Registros por mes (ejemplo)
SELECT DATE_TRUNC('month', fecha_emision) as mes, COUNT(*) 
FROM maestro_dian_vs_erp 
WHERE fecha_emision >= '2024-01-01'
GROUP BY DATE_TRUNC('month', fecha_emision) 
ORDER BY mes;
```

3. **Subir archivos de diciembre**:
   - Subir: dian_dic2024.csv, erp_fn_dic2024.csv, erp_cm_dic2024.csv, errores_dic2024.csv, acuses_dic2024.csv
   - Click en **"Procesar & Consolidar"**

4. **Verificar post-carga**:
```sql
-- Total de registros después
SELECT COUNT(*) as total_despues FROM maestro_dian_vs_erp;

-- Debería haber aumentado
-- total_despues = total_antes + registros_diciembre

-- Verificar que meses anteriores NO se afectaron
SELECT DATE_TRUNC('month', fecha_emision) as mes, COUNT(*) 
FROM maestro_dian_vs_erp 
WHERE fecha_emision >= '2024-01-01'
GROUP BY DATE_TRUNC('month', fecha_emision) 
ORDER BY mes;

-- Debería mostrar:
-- 2024-01: X registros (sin cambios)
-- 2024-02: Y registros (sin cambios)
-- ...
-- 2024-11: Z registros (sin cambios)
-- 2024-12: W registros (NUEVO)
```

#### Resultado Esperado:
```
✅ Registros de ene-nov SE MANTIENEN intactos
✅ Registros de diciembre SE AGREGARON correctamente
✅ Total de registros = suma de todos los meses
✅ NO se perdió información histórica
```

---

## 🔍 CONSULTAS DE VERIFICACIÓN

### 1. Distribución de Estados de Aceptación
```sql
SELECT estado_aprobacion, COUNT(*) as cantidad
FROM maestro_dian_vs_erp
GROUP BY estado_aprobacion
ORDER BY cantidad DESC;
```

**Resultado esperado**:
```
Acuse Bien/Servicio    ~299,183
Pendiente              ~294,136
Rechazada              ~6,440
Acuse Recibido         ~5,776
Aceptación Tácita      ~1,254
Aceptación Expresa     ~388
```

---

### 2. Distribución de Acuses Recibidos
```sql
SELECT acuses_recibidos, COUNT(*) as cantidad
FROM maestro_dian_vs_erp
GROUP BY acuses_recibidos
ORDER BY acuses_recibidos;
```

**Resultado esperado**:
```
0 acuses    ~294,136  (Pendiente)
1 acuse     ~311,399  (Acuse Recibido + Bien/Servicio + Rechazada)
2 acuses    ~1,642    (Aceptación Expresa + Tácita)
```

---

### 3. Verificar Coherencia: Estado vs Acuses
```sql
-- Esta query debe retornar 0 filas (coherencia perfecta)
SELECT nit_emisor, prefijo, folio, estado_aprobacion, acuses_recibidos
FROM maestro_dian_vs_erp
WHERE 
  (estado_aprobacion = 'Pendiente' AND acuses_recibidos != 0) OR
  (estado_aprobacion = 'Acuse Recibido' AND acuses_recibidos != 1) OR
  (estado_aprobacion = 'Acuse Bien/Servicio' AND acuses_recibidos != 1) OR
  (estado_aprobacion = 'Rechazada' AND acuses_recibidos != 1) OR
  (estado_aprobacion = 'Aceptación Expresa' AND acuses_recibidos != 2) OR
  (estado_aprobacion = 'Aceptación Tácita' AND acuses_recibidos != 2);
```

**Resultado esperado**: **0 filas** (coherencia perfecta)

---

### 4. Verificar Duplicados (debe ser 0)
```sql
SELECT nit_emisor, prefijo, folio, COUNT(*) as duplicados
FROM maestro_dian_vs_erp
GROUP BY nit_emisor, prefijo, folio
HAVING COUNT(*) > 1;
```

**Resultado esperado**: **0 filas** (sin duplicados)

---

### 5. Ver Jerarquías de Estados (usando catálogo)
```sql
-- Estados de aceptación con jerarquía
SELECT 
  e.nombre, 
  e.jerarquia, 
  e.acuses_recibidos,
  COUNT(m.id) as registros_en_maestro
FROM estado_aceptacion e
LEFT JOIN maestro_dian_vs_erp m ON m.estado_aprobacion = e.nombre
GROUP BY e.nombre, e.jerarquia, e.acuses_recibidos
ORDER BY e.jerarquia;
```

**Resultado esperado**:
```
Pendiente              (1)  0 acuses   ~294,136 registros
Acuse Recibido         (2)  1 acuse    ~5,776 registros
Acuse Bien/Servicio    (3)  1 acuse    ~299,183 registros
Rechazada              (4)  1 acuse    ~6,440 registros
Aceptación Expresa     (5)  2 acuses   ~388 registros
Aceptación Tácita      (6)  2 acuses   ~1,254 registros
```

---

## 📊 MÉTRICAS DE ÉXITO

| Métrica | Objetivo | Cómo Verificar |
|---------|----------|----------------|
| **Sin duplicados** | 0 filas | Query #4 |
| **Coherencia acuses** | 0 filas | Query #3 |
| **Jerarquía respetada** | Solo upgrades | Prueba 3 y 4 |
| **Cargas parciales** | Funciona | Prueba 2 |
| **Carga incremental** | Funciona | Prueba 6 |
| **Nuevos registros** | Se insertan | Prueba 5 |
| **Rendimiento** | 8-10 seg | Tiempo de carga |

---

## 🐛 PROBLEMAS ESPERABLES Y SOLUCIONES

### Problema 1: "duplicate key value violates unique constraint"
**Causa**: Archivo tiene duplicados internos (misma factura 2 veces).  
**Solución**: Limpiar archivo antes de subir.

### Problema 2: Acuses no se actualizan
**Causa**: Jerarquía del nuevo acuse es MENOR que el actual.  
**Solución**: Esto es correcto (working as intended). Ver Prueba 4.

### Problema 3: Total de registros NO cambia
**Causa**: Todos los registros del archivo ya existían (UPDATE, no INSERT).  
**Solución**: Esto es correcto (UPSERT funcionando).

### Problema 4: Rendimiento lento (>20 seg)
**Causa**: Archivo muy grande (>1M registros).  
**Solución**: Dividir archivo en chunks más pequeños o aumentar memoria.

---

## ✅ CHECKLIST FINAL DE PRUEBAS

- [ ] Prueba 1: Carga completa (baseline)
- [ ] Prueba 2: Carga parcial (solo acuses)
- [ ] Prueba 3: Jerarquía mayor (actualiza)
- [ ] Prueba 4: Jerarquía menor (no actualiza)
- [ ] Prueba 5: Nuevos registros (inserta)
- [ ] Prueba 6: Carga incremental (por mes)
- [ ] Query 1: Distribución de estados
- [ ] Query 2: Distribución de acuses
- [ ] Query 3: Coherencia estado-acuses
- [ ] Query 4: Sin duplicados
- [ ] Query 5: Jerarquías correctas

---

## 📝 REPORTE DE PRUEBAS

Después de ejecutar las pruebas, documenta los resultados:

```markdown
### Resultados de Pruebas - [FECHA]

**Prueba 1 (Carga completa)**:
- Estado: [PASÓ / FALLÓ]
- Tiempo: [X segundos]
- Registros: [X]
- Notas: [...]

**Prueba 2 (Carga parcial)**:
- Estado: [PASÓ / FALLÓ]
- Registros afectados: [X]
- Notas: [...]

**Prueba 3 (Jerarquía mayor)**:
- Estado: [PASÓ / FALLÓ]
- Estado previo: [...]
- Estado post: [...]
- Notas: [...]

... (continuar con todas las pruebas)
```

---

## 🚀 SIGUIENTE PASO

Una vez completadas las pruebas exitosamente:

1. ✅ Documentar resultados
2. ✅ Notificar a usuarios finales
3. ✅ Actualizar manual de usuario
4. ✅ Monitorear primeras cargas en producción

---

**¡Listo para probar!** 🎉

El sistema está corriendo en: http://127.0.0.1:8099/dian_vs_erp/cargar_archivos
