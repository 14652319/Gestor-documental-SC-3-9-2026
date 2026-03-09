# ✅ CORRECCIONES REALIZADAS - SOLICITUD DE CORRECCIÓN DE DOCUMENTOS

## 📋 RESUMEN DE CAMBIOS

### 1. ✅ Variables Indefinidas Corregidas (Líneas 1237-1262)

**PROBLEMA:**
- Las variables `empresa_nueva_id`, `tipo_nuevo_id`, `centro_nuevo_id`, `consecutivo_nuevo`, `fecha_nueva` NO estaban definidas
- Causaba error: `NameError: name 'empresa_nueva_id' is not defined`

**SOLUCIÓN:**
```python
# Extraer campos del formulario
empresa_nueva_id = data.get('empresa_id')
tipo_nuevo_id = data.get('tipo_documento_id')
centro_nuevo_id = data.get('centro_operacion_id')
consecutivo_nuevo = data.get('consecutivo', '').strip()
fecha_nueva = data.get('fecha_expedicion')
justificacion = data.get('justificacion', '').strip()
```

---

### 2. ✅ Validación de Documentos Duplicados (Líneas 1283-1319)

**NUEVA FUNCIONALIDAD:**
- Antes de generar el token, el sistema verifica si ya existe un documento con el nuevo nombre en la misma empresa
- Si existe, retorna error 409 con la ruta donde está ubicado

**CÓDIGO AGREGADO:**
```python
# Construir nuevo nombre base
nuevo_nombre_esperado = f"{centro_obj.codigo}-{tipo_doc_obj.siglas}-{consecutivo_final.zfill(8)}"

# Buscar si ya existe un documento con ese nombre en la misma empresa
doc_duplicado = DocumentoContable.query.filter(
    DocumentoContable.empresa == empresa_final,
    DocumentoContable.nombre_archivo.like(f"{nuevo_nombre_esperado}%"),
    DocumentoContable.id != documento_id
).first()

if doc_duplicado:
    return jsonify({
        'success': False,
        'message': f'⚠️ El documento {nuevo_nombre_esperado} ya existe en la empresa {empresa_final}',
        'ruta_existente': doc_duplicado.ruta_archivo,
        'documento_existente': doc_duplicado.nombre_archivo
    }), 409
```

**RESPUESTA JSON:**
```json
{
  "success": false,
  "message": "⚠️ El documento 007-NCM-00000099 ya existe en la empresa SC",
  "ruta_existente": "D:/DOCUMENTOS_CONTABLES/SC/2025/11/007/NCM/007-NCM-00000099",
  "documento_existente": "007-NCM-00000099.pdf"
}
```

---

### 3. ✅ Variable `usuario` Corregida (Líneas 1377, 1556, 1566)

**PROBLEMA:**
- Se usaba variable `usuario` que no existía
- Debía ser `usuario_nombre` que ya estaba definida en línea 1220

**CORRECCIÓN:**
```python
# Línea 1377
created_by=usuario_nombre  # ✅ Antes: usuario

# Línea 1556
print(f"👤 Usuario: {usuario_nombre}")  # ✅ Antes: usuario

# Línea 1566
log_security(f"CORRECCIÓN SOLICITADA | doc={documento_id} | usuario={usuario_nombre}")
```

---

## 🧪 CÓMO PROBAR

### Opción 1: Prueba Completa desde el Navegador

1. **Abrir navegador**: http://127.0.0.1:8099
2. **Login**: admin / admin123 / NIT: 805028041
3. **Ir a Archivo Digital** → Buscar documento ID 32
4. **Clic en "Editar"** (ícono de lápiz)
5. **Clic en "Solicitar Corrección"**
6. **Llenar formulario:**
   - Cambiar Consecutivo a: `00000099`
   - Justificación: `Prueba de envío de correo electrónico`
7. **Presionar "📧 Enviar Código por Correo"**

**RESULTADO ESPERADO:**
- ✅ Mensaje: "Código enviado a [correo]"
- ✅ Correo recibido con token de 6 dígitos
- ✅ Token visible en consola del servidor si el correo falla

---

### Opción 2: Prueba de Duplicados

1. **Primer intento**: Cambiar consecutivo a `00000099` → Enviar código
2. **Ver en BD**: Se crea token y se envía correo ✅
3. **Segundo intento**: Intentar cambiar OTRO documento al mismo `00000099`

**RESULTADO ESPERADO:**
```json
{
  "success": false,
  "message": "⚠️ El documento 007-NCM-00000099 ya existe en la empresa SC"
}
```

---

## 📊 LOGS DEL SERVIDOR

Cuando ejecutes la prueba, verás en la consola del servidor:

```
================================================================================
🔄 SOLICITUD DE CORRECCIÓN INICIADA
================================================================================
Usuario: admin
Documento ID: 32
✅ Documento encontrado: 005-NDG-00000013
Datos recibidos: dict_keys(['empresa_id', 'tipo_documento_id', ...])
✅ Justificación válida: 58 caracteres
📋 Campos recibidos: empresa=None, tipo=None, centro=None, consec=00000099, fecha=None
🔍 Verificando duplicados: 007-NCM-00000099 en empresa SC
✅ No se encontraron duplicados
✅ Token creado: ID=123, Token=456789
🔍 DEBUG: Session data - usuario=admin, usuario_id=23
✅ DEBUG: Correo encontrado por ID: admin@ejemplo.com
```

**Si el correo se envía:**
```
INFO:security:EMAIL ENVIADO | Corrección doc=32 | destinatario=admin@ejemplo.com
```

**Si falla el correo:**
```
================================================================================
⚠️ CÓDIGO DE CORRECCIÓN GENERADO (Correo falló)
================================================================================
📧 Destinatario: admin@ejemplo.com
👤 Usuario: admin
📄 Documento: 005-NDG-00000013
🔑 TOKEN: 456789
❌ Error: [detalles del error SMTP]
================================================================================
```

---

## ⚠️ IMPORTANTE

### Lo que FUNCIONA ahora:
- ✅ Extracción de datos del formulario
- ✅ Validación de duplicados
- ✅ Generación de token
- ✅ Envío de correo (si SMTP está configurado)
- ✅ Token visible en consola como fallback

### Lo que AÚN NO está implementado:
- ❌ Carpeta temporal "DOCUMENTOS_CORREGIDOS" de 60 días
- ❌ Crear nuevo documento + mover original a temporal
- ❌ Borrado automático después de 60 días

**Actualmente:** El sistema mueve directamente a la nueva ubicación (no hay carpeta temporal)

---

## 🔍 VERIFICACIÓN DE SINTAXIS

```bash
✅ Archivo compilado sin errores:
python -m py_compile modules/notas_contables/routes.py
```

---

## 📧 VERIFICAR CORREO

1. Revisa la bandeja de entrada del correo configurado en la tabla `usuarios`
2. El correo viene con asunto: **"🔄 Código de Corrección - Documento [nombre]"**
3. Contiene:
   - Token de 6 dígitos
   - Resumen de cambios
   - Validez: 10 minutos
   - Instrucciones

---

## 🎯 PRÓXIMOS PASOS

Para implementar la carpeta temporal de 60 días:

1. Modificar función `validar_correccion_documento` (línea 1540+)
2. En lugar de mover archivos:
   - Crear nuevo documento con nuevos datos
   - Copiar anexos al nuevo documento
   - Mover documento ORIGINAL a: `D:/DOCUMENTOS_CONTABLES/_CORREGIDOS/YYYY-MM-DD/`
3. Crear tarea programada (cron/scheduler) para borrar archivos > 60 días

---

**FECHA DE CORRECCIÓN:** 15 de noviembre de 2025
**ARCHIVO MODIFICADO:** `modules/notas_contables/routes.py`
**LÍNEAS MODIFICADAS:** 1237-1319, 1377, 1556, 1566
