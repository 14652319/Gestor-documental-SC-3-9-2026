# 🗑️ MANUAL DE USO: GESTIÓN DE ELIMINACIÓN DE DATOS
**Sistema DIAN vs ERP - Módulo de Configuración**  
**Fecha:** 16 de Febrero de 2026

---

## 📋 DESCRIPCIÓN GENERAL

Sistema seguro de eliminación masiva de datos con confirmación por correo electrónico. Permite borrar registros de la base de datos por rangos de fechas con validación de doble factor.

---

## ⚠️ ADVERTENCIAS CRÍTICAS

### 🔴 ESTA ACCIÓN ES IRREVERSIBLE
- Los datos eliminados **NO SE PUEDEN RECUPERAR**
- **NO existe función de deshacer** (UNDO)
- Se recomienda hacer **BACKUP** antes de eliminar datos masivos

### 🔐 SISTEMA DE SEGURIDAD
- **Doble confirmación:** Solicitud + Código por email
- **Validez del código:** 10 minutos
- **Auditoría completa:** Todos los eventos se registran en `logs/security.log`
- **IP tracking:** Se registra IP de solicitud y confirmación

---

## 🚀 CÓMO USAR EL SISTEMA

### PASO 1: Acceder al Módulo
1. Iniciar sesión en el sistema
2. Ir a `http://127.0.0.1:8099/dian_vs_erp/configuracion`
3. Click en la pestaña **"🗑️ Gestión de Datos"** (última pestaña)

### PASO 2: Configurar Eliminación
Complete el formulario con los siguientes datos:

#### A. Tipo de Rango
Seleccione una opción:
- **Rango de Días:** Elimina registros entre 2 fechas específicas
- **Rango de Meses:** Elimina registros de meses completos
- **Año Completo:** Elimina todos los registros de un año (ej: 2026)

#### B. Fechas
- **Año Completo:** Solo ingrese el año (ej: `2026`)
- **Días/Meses:** Seleccione fecha inicio y fecha fin

#### C. Email de Confirmación
- Ingrese el correo electrónico donde recibirá el código de 6 dígitos
- **IMPORTANTE:** Debe tener acceso a este correo para completar el proceso

#### D. Archivos/Tablas a Eliminar
Marque las casillas de las tablas donde desea eliminar datos:
- ✅ **Facturas DIAN** (maestro_dian_vs_erp) - **FUNCIONAL**
- ⏳ ERP Financiero (próximamente)
- ⏳ ERP Comercial (próximamente)  
- ⏳ Acuses de Recibo (próximamente)

### PASO 3: Solicitar Código
1. Click en **"🔐 Solicitar Eliminación"**
2. Confirmar en el diálogo que aparece
3. Esperar mensaje: *"✅ Código enviado a su correo electrónico"*

### PASO 4: Revisar Email
Revise su bandeja de entrada. Recibirá un correo con:
- **Asunto:** 🔐 Código de Confirmación - Eliminación de Datos DIAN vs ERP
- **Código de 6 dígitos** (ej: `123456`)
- **Detalles** de la eliminación solicitada
- **Validez:** 10 minutos

### PASO 5: Confirmar Eliminación
1. Copie el código de 6 dígitos del email
2. Péguelo en el campo **"🔢 Código de Validación"**
3. Click en **"✅ Confirmar y Ejecutar Eliminación"**
4. Confirmar en el diálogo de advertencia final
5. Esperar resultado de la eliminación

### PASO 6: Verificar Resultado
El sistema mostrará:
- ✅ Total de registros eliminados
- 📊 Cantidad eliminada por tabla
- 🔄 Botón para recargar la página

---

## 📧 EJEMPLO DE EMAIL RECIBIDO

```
🗑️ Eliminación de Datos
Sistema de Facturas DIAN vs ERP

Hola usuario123,

Has solicitado eliminar datos del sistema. Para confirmar esta acción, 
utiliza el siguiente código de validación:

    1 2 3 4 5 6

⚠️ ADVERTENCIA: Esta acción es IRREVERSIBLE. Una vez confirmada, 
los datos serán eliminados permanentemente de la base de datos.

📋 Detalles de la Eliminación:
• Tipo de rango: AÑO
• Fecha inicio: 01/01/2026
• Fecha fin: 31/12/2026
• Archivos/Tablas: Facturas DIAN
• Solicitado por: usuario123
• IP: 192.168.1.100

Validez del código: 10 minutos

Si no solicitaste esta eliminación, ignora este correo y el código 
expirará automáticamente.
```

---

## 🔍 EJEMPLOS DE USO

### Ejemplo 1: Eliminar datos de 2026 completo
```
Tipo de Rango: Año Completo
Año: 2026
Email: usuario@empresa.com
Archivos: ✅ Facturas DIAN

Resultado esperado:
- Eliminará todos los registros con fecha_emision en 2026
- Ejemplo: 610,458 registros eliminados
```

### Ejemplo 2: Eliminar rango de días específico
```
Tipo de Rango: Rango de Días
Fecha Inicio: 2026-01-01
Fecha Fin: 2026-01-15
Email: usuario@empresa.com
Archivos: ✅ Facturas DIAN

Resultado esperado:
- Eliminará solo registros del 1 al 15 de enero de 2026
```

### Ejemplo 3: Eliminar un mes específico
```
Tipo de Rango: Rango de Meses
Fecha Inicio: 2026-02-01
Fecha Fin: 2026-02-29
Email: usuario@empresa.com
Archivos: ✅ Facturas DIAN

Resultado esperado:
- Eliminará todos los registros de febrero 2026
```

---

## ❌ ERRORES COMUNES Y SOLUCIONES

### Error: "Código inválido o ya utilizado"
**Causa:** El código ya fue usado o es incorrecto  
**Solución:** Solicite un nuevo código

### Error: "Código expirado. Solicita uno nuevo"
**Causa:** Han pasado más de 10 minutos desde el envío  
**Solución:** Regrese al PASO 3 y solicite un nuevo código

### Error: "Email inválido"
**Causa:** Formato de email incorrecto  
**Solución:** Verifique que el email tenga formato `usuario@dominio.com`

### Error: "Debe seleccionar al menos un archivo/tabla"
**Causa:** No marcó ninguna casilla de archivos  
**Solución:** Marque al menos la casilla "Facturas DIAN"

### No recibí el email
**Soluciones:**
1. Revise carpeta de SPAM/Correo no deseado
2. Verifique que el email ingresado sea correcto
3. Espere 1-2 minutos (puede haber demora en entrega)
4. Solicite un nuevo código si pasaron más de 5 minutos

---

## 🔐 AUDITORÍA Y LOGS

Todas las operaciones se registran en `logs/security.log`:

### Eventos Registrados:
```
TOKEN ELIMINACIÓN GENERADO | usuario=admin | token_id=1 | archivos=Facturas DIAN | rango=2026-01-01 a 2026-12-31

ELIMINACIÓN DATOS EJECUTADA | usuario=admin | token_id=1 | eliminados=610458 | rango=2026-01-01 a 2026-12-31
```

### Información Almacenada en BD:
- Tabla: `tokens_eliminacion_dian_erp`
- Usuario solicitante
- Fechas de solicitud y uso
- IPs de origen
- Cantidad de registros eliminados
- Resultado detallado por tabla (JSON)

---

## 📊 TABLA DE TOKENS

### Estructura de `tokens_eliminacion_dian_erp`:
| Campo | Descripción |
|-------|-------------|
| `id` | ID único del token |
| `token` | Código de 6 dígitos |
| `usuario_solicitante` | Usuario que solicitó |
| `email_destino` | Email donde se envió |
| `tipo_rango` | 'dias', 'meses', 'año' |
| `fecha_inicio` | Fecha inicial del rango |
| `fecha_fin` | Fecha final del rango |
| `archivos_eliminar` | JSON array con tablas |
| `usado` | Boolean (si ya se usó) |
| `fecha_creacion` | Timestamp de generación |
| `fecha_expiracion` | Timestamp de expiración |
| `fecha_uso` | Timestamp de confirmación |
| `registros_eliminados` | Cantidad total eliminada |
| `resultado_json` | JSON con resultado detallado |
| `ip_solicitud` | IP al solicitar |
| `ip_confirmacion` | IP al confirmar |

---

## 🛡️ RECOMENDACIONES DE SEGURIDAD

### Antes de Eliminar:
1. ✅ **HACER BACKUP** de la base de datos
2. ✅ Verificar que el rango de fechas es correcto
3. ✅ Confirmar con el equipo que los datos ya no se necesitan
4. ✅ Revisar estadísticas actuales con scripts de verificación

### Durante la Eliminación:
1. ⏰ No cerrar el navegador hasta ver el resultado
2. 📧 Mantener abierto el correo electrónico
3. ⏱️ Ingresar el código en menos de 10 minutos

### Después de Eliminar:
1. 📊 Verificar el resultado mostrado en pantalla
2. 🔍 Ejecutar scripts de conteo para confirmar eliminación
3. 📝 Documentar la operación realizada
4. 🗑️ Los tokens usados quedan en BD para auditoría

---

## 📞 SOPORTE TÉCNICO

### Contacto:
- **Desarrollador:** Copilot AI Assistant
- **Sistema:** Gestor Documental - Supertiendas Cañaveral
- **Módulo:** DIAN vs ERP
- **Fecha Implementación:** 16 de Febrero de 2026

### Scripts Útiles de Verificación:
```powershell
# Contar registros por año
.\.venv\Scripts\python.exe contar_exacto_por_año.py

# Verificar integridad de 2025
.\.venv\Scripts\python.exe verificar_2025_completo.py

# Ver tokens de eliminación generados
# (consulta directa a tabla tokens_eliminacion_dian_erp)
```

---

## ✅ CHECKLIST ANTES DE ELIMINAR

- [ ] Tengo BACKUP de la base de datos
- [ ] Confirmé el rango de fechas correcto
- [ ] Verifiqué las tablas a eliminar
- [ ] Tengo acceso al email de confirmación
- [ ] El equipo está informado de la operación
- [ ] Revisé los logs y estadísticas actuales
- [ ] Tengo tiempo para completar el proceso (< 10 min)

**Si todas las casillas están marcadas, puede proceder con confianza.**

---

**🔒 FIN DEL MANUAL**
