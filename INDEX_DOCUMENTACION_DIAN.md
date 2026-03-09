# 📚 ÍNDICE DE DOCUMENTACIÓN - MÓDULO DIAN vs ERP

**Fecha de actualización:** 20 de Febrero de 2026

---

## 🎯 DOCUMENTO PRINCIPAL (LEE ESTE)

### ⭐ [SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md](SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md)

**ESTE ES EL ÚNICO DOCUMENTO QUE NECESITAS LEER**

Incluye TODO sobre el sistema:
- ✅ Arquitectura completa del sistema
- ✅ Los 8 bugs resueltos con explicaciones detalladas
- ✅ Función crítica `format_value_for_copy()` con ejemplos
- ✅ Estructura de TODAS las tablas (especialmente ACUSES)
- ✅ Mapeo Excel → PostgreSQL con todos los casos especiales
- ✅ Cómo ejecutar el sistema (3 métodos)
- ✅ Troubleshooting completo
- ✅ Reglas para NO romper el sistema
- ✅ Scripts de utilidad
- ✅ Resultados finales: 173,342 registros exitosos

**📊 Estado:** ✅ Sistema 100% funcional en producción

---

## 📁 DOCUMENTOS HISTÓRICOS (Referencia únicamente)

Estos documentos fueron útiles durante el desarrollo pero están **desactualizados** o **incompletos**.  
**NO los uses como referencia principal.**

### Documentos Obsoletos (Solo lectura histórica)

1. **MODULO_DIAN_vs_ERP_COMPLETO.md** (Obsoleto)
   - Fecha: ~Diciembre 2025
   - Estado: ⚠️ No incluye bugs #7 y #8 (los más críticos)
   - Usa sistema anterior SQLite standalone

2. **DOCUMENTACION_MODULO_DIAN_VS_ERP_COMPLETA.md** (Obsoleto)
   - Fecha: ~Enero 2026
   - Estado: ⚠️ No incluye correcciones de ACUSES

3. **DOCUMENTACION_MODULO_DIAN_VS_ERP.md** (Obsoleto)
   - Fecha: ~Enero 2026
   - Estado: ⚠️ Documentación parcial sin bugs resueltos

4. **INTEGRACION_DIAN_vs_ERP_COMPLETADA.md** (Obsoleto)
   - Fecha: ~Enero 2026
   - Estado: ⚠️ Integración inicial, sin optimizaciones

5. **GUIA_DIAN_VS_ERP_INTEGRACION.md** (Obsoleto)
   - Fecha: ~Enero 2026
   - Estado: ⚠️ Guía de integración preliminar

6. **OPTIMIZACION_DIAN_29DIC2025.md** (Histórico)
   - Fecha: 29 de Diciembre 2025
   - Estado: ⚠️ Optimización inicial, sin bugs resueltos

7. **MAPEO_COLUMNAS_DIAN_COMPLETO.md** (Histórico)
   - Estado: ⚠️ Solo DIAN, no incluye ACUSES/ERP

8. **MANUAL_ELIMINACION_DATOS_DIAN_ERP.md** (Útil)
   - Estado: ✅ Aún válido para eliminación de datos

9. **VALIDACION_CARGA_ARCHIVOS_DIAN_VS_ERP_17FEB2026.md** (Histórico)
   - Fecha: 17 de Febrero 2026
   - Estado: ⚠️ Validación en proceso, bugs no resueltos aún

10. **RESUMEN_VALIDACION_DIAN_17FEB2026.md** (Histórico)
    - Fecha: 17 de Febrero 2026
    - Estado: ⚠️ Resumen parcial

11. **SESION_27ENE2026_CORRECCIONES_DIAN_VS_ERP.md** (Histórico)
    - Fecha: 27 de Enero 2026
    - Estado: ⚠️ Correcciones intermedias

---

## 🗂️ BACKUPS (No modificar)

Los documentos en `BACKUP_ORIG/` y `BACKUP_INTEGRACION_SAGRILAFT_*/` son **backups históricos** para recuperación de desastres.

**NO USAR COMO REFERENCIA - Pueden estar muy desactualizados**

---

## 🎯 RESUMEN PARA NUEVOS USUARIOS

### Si eres nuevo en el sistema:

1. **LEE SOLO:** [SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md](SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md)

2. **NO LEAS** los demás documentos DIAN (te confundirán con información desactualizada)

3. **Si necesitas eliminar datos:** Ver [MANUAL_ELIMINACION_DATOS_DIAN_ERP.md](MANUAL_ELIMINACION_DATOS_DIAN_ERP.md)

### Si necesitas hacer cambios al sistema:

1. **LEE COMPLETO:** [SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md](SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md)

2. **PRESTA ESPECIAL ATENCIÓN A:**
   - Sección "🔧 FUNCIÓN CRÍTICA: format_value_for_copy()"
   - Sección "🔒 REGLAS PARA MANTENER EL SISTEMA FUNCIONANDO"
   - Sección "🐛 BUGS RESUELTOS (8 EN TOTAL)"

3. **HAZ BACKUP de routes.py** antes de cambiar

4. **PRUEBA CON ARCHIVOS PEQUEÑOS** antes de producción

### Si algo se rompe:

1. **CONSULTA:** Sección "🔍 TROUBLESHOOTING" en el documento principal

2. **REVISA LOGS:** `logs/security.log` para errores detallados

3. **RESTAURA BACKUP:** Si no funciona, vuelve a la versión anterior

---

## 📊 ESTADO ACTUAL DEL SISTEMA

**Fecha:** 20 de Febrero de 2026  
**Versión:** v1.0 - Producción  
**Estado:** ✅ 100% Funcional

**Registros procesados exitosamente:**
```
dian                     :   1,400
erp_comercial            :  57,191
erp_financiero           :   2,995
acuses                   :  46,650
maestro_dian_vs_erp      :  65,106
─────────────────────────────────────
TOTAL                    : 173,342 ✅
```

**Velocidad:** ~25,000 registros/segundo  
**Bugs resueltos:** 8 bugs críticos  
**Problemas conocidos:** Ninguno

---

## 🆘 SOPORTE

**¿Tienes dudas?**
1. Busca en el documento principal primero
2. Revisa la sección de troubleshooting
3. Verifica los logs del sistema

**¿Necesitas hacer cambios?**
1. Lee las reglas de mantenimiento
2. Haz backup primero
3. Prueba con datos pequeños

**¿Algo se rompió?**
1. No entres en pánico
2. Revisa los logs
3. Restaura el backup
4. Consulta el troubleshooting

---

**Última actualización:** 20 de Febrero de 2026  
**Documento principal:** SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md
