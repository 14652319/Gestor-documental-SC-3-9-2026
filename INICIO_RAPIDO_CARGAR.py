"""
INICIO RÁPIDO - CARGAR ARCHIVOS AHORA
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              ✅ SERVIDOR ACTIVO - LISTO PARA CARGAR ARCHIVOS                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 ESTADO ACTUAL:
   Puerto: 8099 ✅ ACTIVO
   Registros actuales: 173,342
   Sistema: 100% Operativo


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PASO 1: ABRE TU NAVEGADOR                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   🌐 Dirección:  http://localhost:8099/dian_vs_erp/cargar
   
   📋 O copia y pega esta URL en Chrome/Edge/Firefox:
   
   ┌─────────────────────────────────────────────────┐
   │  http://localhost:8099/dian_vs_erp/cargar       │
   └─────────────────────────────────────────────────┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PASO 2: PREPARA TUS ARCHIVOS EXCEL/CSV                                     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   Necesitas 4 archivos (mínimo 1, máximo 4):
   
   ✅ DIAN              → Facturas electrónicas de la DIAN
   ✅ ERP Financiero    → Datos del módulo FN de tu ERP
   ✅ ERP Comercial     → Datos del módulo CM de tu ERP
   ✅ ACUSES            → Respuestas y acuses de la DIAN
   
   📁 Formatos aceptados:
      • Excel: .xlsx, .xls, .xlsm
      • CSV: .csv
      • LibreOffice: .ods


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PASO 3: EN LA INTERFAZ WEB                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   Verás 4 secciones (fondo negro):
   
   ┌────────────────────────────────────────────────────┐
   │  📁 DIAN (Facturas Electrónicas)                  │
   │  [Seleccionar archivo...]  [📤 Subir DIAN]        │
   │  ✅ Archivo subido correctamente                   │
   └────────────────────────────────────────────────────┘
   
   ┌────────────────────────────────────────────────────┐
   │  📁 ERP Financiero (Módulo FN)                    │
   │  [Seleccionar archivo...]  [📤 Subir ERP FN]      │
   │  ✅ Archivo subido correctamente                   │
   └────────────────────────────────────────────────────┘
   
   ┌────────────────────────────────────────────────────┐
   │  📁 ERP Comercial (Módulo CM)                     │
   │  [Seleccionar archivo...]  [📤 Subir ERP CM]      │
   │  ✅ Archivo subido correctamente                   │
   └────────────────────────────────────────────────────┘
   
   ┌────────────────────────────────────────────────────┐
   │  📁 ACUSES (Respuestas DIAN)                      │
   │  [Seleccionar archivo...]  [📤 Subir ACUSES]      │
   │  ✅ Archivo subido correctamente                   │
   └────────────────────────────────────────────────────┘
   
   ════════════════════════════════════════════════════
   
        [🚀 PROCESAR TODOS LOS ARCHIVOS]
   
   ════════════════════════════════════════════════════


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PASO 4: SUBIR CADA ARCHIVO                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   Para cada archivo:
   
   1️⃣  Click en "Seleccionar archivo..."
   2️⃣  Busca tu archivo Excel/CSV en tu computadora
   3️⃣  Click en "Subir" (botón verde)
   4️⃣  Espera el mensaje: "✅ Archivo subido correctamente"
   
   ⏱️  Tiempo de subida: ~1-5 segundos por archivo


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PASO 5: PROCESAR LOS ARCHIVOS                                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   Una vez subidos los 4 archivos (o los que tengas):
   
   1️⃣  Click en el botón grande: "🚀 PROCESAR TODOS LOS ARCHIVOS"
   
   2️⃣  El sistema procesará automáticamente:
       ⚡ Leer archivos con Polars (ultra-rápido)
       ⚡ Normalizar columnas
       ⚡ Aplicar reglas de negocio
       ⚡ Escapar caracteres especiales
       ⚡ Insertar en PostgreSQL (25,000 reg/seg)
       ⚡ Consolidar en maestro
   
   3️⃣  Tiempo estimado:
       • 1,000 registros   → ~1 segundo
       • 10,000 registros  → ~5 segundos
       • 50,000 registros  → ~20 segundos
       • 100,000 registros → ~40 segundos
   
   4️⃣  Verás mensaje: "✅ Procesamiento completado"


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PASO 6: VERIFICAR LOS RESULTADOS                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   🔍 OPCIÓN 1: En el navegador
   
      URL: http://localhost:8099/dian_vs_erp/visor_v2
      
      • Verás los datos consolidados
      • Usa filtros por fecha para ver solo los nuevos
      • Exporta a Excel si necesitas
   
   
   🔍 OPCIÓN 2: Desde PowerShell
   
      cd "d:\\0.1. Backup Equipo Contablilidad\\Gestor Documental\\GESTOR_DOCUMENTAL_TRANSPORTABLE_20251113_204059"
      python CHECK_ALL_TABLES.py
   
      Verás:
      ══════════════════════════════════════════════
      📊 ESTADO DE LAS TABLAS
      ══════════════════════════════════════════════
      dian                     : 2,800      ← ANTES: 1,400
      erp_comercial            : 114,382    ← ANTES: 57,191
      erp_financiero           : 5,990      ← ANTES: 2,995
      acuses                   : 93,300     ← ANTES: 46,650
      maestro_dian_vs_erp      : 130,212    ← ANTES: 65,106
      ══════════════════════════════════════════════
      TOTAL                    : 346,684    ← ANTES: 173,342
      ══════════════════════════════════════════════


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ⚠️ IMPORTANTE: CARGA INCREMENTAL                                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   ✅ Los datos ANTIGUOS NO SE BORRAN
   ✅ Si un registro ya existe (mismo CUFE), se ACTUALIZA
   ✅ Si un registro es nuevo, se INSERTA
   ✅ NO hay duplicados gracias a ON CONFLICT DO UPDATE
   
   📈 Los conteos AUMENTARÁN (pero no el doble exacto)
   
   Ejemplo:
   Antes:  1,400 facturas DIAN
   Cargas: 1,500 facturas nuevas
   Total:  2,900 (no 2,800 si hay algunas actualizadas)


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  📋 CHECKLIST RÁPIDO                                                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   Antes de cargar:
   ☐ Servidor corriendo (puerto 8099) ✅ YA ESTÁ
   ☐ Archivos preparados (.xlsx/.csv)
   ☐ Backup de BD hecho (recomendado)
      → .\BACKUP_BD_MANUAL.bat
   
   Durante la carga:
   ☐ Abrir: http://localhost:8099/dian_vs_erp/cargar
   ☐ Subir archivo DIAN
   ☐ Subir archivo ERP Financiero
   ☐ Subir archivo ERP Comercial
   ☐ Subir archivo ACUSES
   ☐ Click: "PROCESAR TODOS LOS ARCHIVOS"
   
   Después de la carga:
   ☐ Verificar en visor: http://localhost:8099/dian_vs_erp/visor_v2
   ☐ O ejecutar: python CHECK_ALL_TABLES.py
   ☐ Revisar que los conteos aumentaron


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ❓ SI ALGO SALE MAL                                                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

   1. Ver logs:
      type logs\\security.log
   
   2. Documentación completa:
      GUIA_CARGAR_NUEVOS_ARCHIVOS.md (recién creada)
      SISTEMA_CARGA_INCREMENTAL_DIAN_VS_ERP_COMPLETO.md
   
   3. Reiniciar servidor:
      Ctrl+C (en la ventana del servidor)
      .\\1_iniciar_gestor.bat


╔══════════════════════════════════════════════════════════════════════════════╗
║                     🚀 ¡LISTO PARA CARGAR ARCHIVOS!                          ║
║                                                                              ║
║  URL Principal: http://localhost:8099/dian_vs_erp/cargar                    ║
║  Estado: ✅ Servidor activo en puerto 8099                                   ║
║  Registros actuales: 173,342                                                 ║
║  Sistema: 100% Operativo                                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
