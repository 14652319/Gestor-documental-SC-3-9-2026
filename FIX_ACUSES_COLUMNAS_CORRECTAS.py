"""
🔧 FIX CRÍTICO: insertar_acuses_bulk() con columnas correctas

PROBLEMA: El código usa columnas de DIAN ('nit_proveedor', 'razon_social', etc.)
         pero la tabla acuses tiene columnas diferentes.

CAUSA RAÍZ: insertar_acuses_bulk() fue copiado de insertar_dian_bulk() 
           sin adaptar las columnas.

SOLUCIÓN: Usar las columnas REALES de la tabla acuses que coinciden con el Excel.

COLUMNAS REALES de tabla acuses (del modelo línea 466):
- fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,
- estado_docto, descripcion_reclamo, tipo_documento, cufe, valor,
- acuse_recibido, recibo_bien_servicio, aceptacion_expresa,
- reclamo, aceptacion_tacita, clave_acuse

COLUMNAS del Excel ACUSES:
- 'fecha', 'adquiriente', 'factura', 'emisor', 'nit emisor', 'nit. pt',
- 'estado docto.', 'descripción reclamo', 'tipo documento', 'cufe', 'valor',
- 'acuse recibido', 'recibo bien servicio', 'aceptación expresa',
- 'reclamo', 'aceptación tacita'
"""

# Este es el código CORRECTO para insertar_acuses_bulk()
CODIGO_CORRECTO = """
def insertar_acuses_bulk(acuses_df, cursor):
    '''
    Inserta acuses en PostgreSQL usando COPY FROM (bulk insert)
    Usa ON CONFLICT para actualizar si jerarquía de estado es mayor
    '''
    import io
    from datetime import datetime
    
    print("\\n📊 Insertando en tabla ACUSES...")
    
    # Convertir a pandas y preparar registros
    acuses_pd = acuses_df.to_pandas()
    
    # 🆕 MAPEAR COLUMNAS: Excel → PostgreSQL
    # Las columnas de Excel tienen acentos y espacios, necesitamos normalizar
    column_mapping = {
        'fecha': 'fecha',
        'adquiriente': 'adquiriente',
        'factura': 'factura',
        'emisor': 'emisor',
        'nit emisor': 'nit_emisor',
        'nit. pt': 'nit_pt',
        'estado docto.': 'estado_docto',
        'descripción reclamo': 'descripcion_reclamo',
        'tipo documento': 'tipo_documento',
        'cufe': 'cufe',
        'valor': 'valor',
        'acuse recibido': 'acuse_recibido',
        'recibo bien servicio': 'recibo_bien_servicio',
        'aceptación expresa': 'aceptacion_expresa',
        'reclamo': 'reclamo',
        'aceptación tacita': 'aceptacion_tacita'
    }
    
    # Renombrar columnas
    acuses_pd = acuses_pd.rename(columns=column_mapping)
    
    # Generar clave_acuse (CUFE + Estado)
    acuses_pd['clave_acuse'] = (
        acuses_pd['cufe'].fillna('').astype(str) + '|' + 
        acuses_pd['estado_docto'].fillna('Pendiente').astype(str)
    )
    
    registros = acuses_pd.to_dict('records')
    
    print(f"   🔄 Carga INCREMENTAL (actualiza solo si jerarquía mayor)")
    print(f"   📋 {len(registros):,} registros a procesar")
    
    # Crear tabla temporal (sin restricciones UNIQUE para permitir duplicados internos)
    cursor.execute('''
        CREATE TEMP TABLE temp_acuses_nuevos (LIKE acuses INCLUDING DEFAULTS) ON COMMIT DROP
    ''')
    
    # COPY FROM a tabla temporal usando las columnas CORRECTAS
    buffer = io.StringIO()
    for reg in registros:
        # Usar format_value_for_copy() para manejar None correctamente
        buffer.write(f"{format_value_for_copy(reg.get('fecha'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('adquiriente'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('factura'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('emisor'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('nit_emisor'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('nit_pt'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('estado_docto'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('descripcion_reclamo'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('tipo_documento'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('cufe'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('valor'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('acuse_recibido'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('recibo_bien_servicio'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('aceptacion_expresa'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('reclamo'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('aceptacion_tacita'))}\t")
        buffer.write(f"{format_value_for_copy(reg.get('clave_acuse'))}\\n")
    
    buffer.seek(0)
    
    # COPY FROM temp table con columnas CORRECTAS
    cursor.copy_from(
        buffer,
        'temp_acuses_nuevos',
        sep='\\t',
        null='',
        columns=(
            'fecha', 'adquiriente', 'factura', 'emisor', 'nit_emisor', 'nit_pt',
            'estado_docto', 'descripcion_reclamo', 'tipo_documento', 'cufe', 'valor',
            'acuse_recibido', 'recibo_bien_servicio', 'aceptacion_expresa',
            'reclamo', 'aceptacion_tacita', 'clave_acuse'
        )
    )
    
    # INSERT con UPDATE si jerarquía mayor
    cursor.execute('''
        INSERT INTO acuses (
            fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,
            estado_docto, descripcion_reclamo, tipo_documento, cufe, valor,
            acuse_recibido, recibo_bien_servicio, aceptacion_expresa,
            reclamo, aceptacion_tacita, clave_acuse, fecha_carga
        )
        SELECT 
            fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,
            estado_docto, descripcion_reclamo, tipo_documento, cufe, valor,
            acuse_recibido, recibo_bien_servicio, aceptacion_expresa,
            reclamo, aceptacion_tacita, clave_acuse, NOW()
        FROM temp_acuses_nuevos
        ON CONFLICT (clave_acuse) DO UPDATE SET
            fecha = EXCLUDED.fecha,
            adquiriente = EXCLUDED.adquiriente,
            factura = EXCLUDED.factura,
            emisor = EXCLUDED.emisor,
            nit_emisor = EXCLUDED.nit_emisor,
            nit_pt = EXCLUDED.nit_pt,
            estado_docto = EXCLUDED.estado_docto,
            descripcion_reclamo = EXCLUDED.descripcion_reclamo,
            tipo_documento = EXCLUDED.tipo_documento,
            cufe = EXCLUDED.cufe,
            valor = EXCLUDED.valor,
            acuse_recibido = EXCLUDED.acuse_recibido,
            recibo_bien_servicio = EXCLUDED.recibo_bien_servicio,
            aceptacion_expresa = EXCLUDED.aceptacion_expresa,
            reclamo = EXCLUDED.reclamo,
            aceptacion_tacita = EXCLUDED.aceptacion_tacita,
            fecha_actualizacion = NOW()
        WHERE calcular_jerarquia_acuse(EXCLUDED.estado_docto) > calcular_jerarquia_acuse(acuses.estado_docto)
    ''')
    
    # Contar registros procesados
    cursor.execute("SELECT COUNT(*) FROM temp_acuses_nuevos")
    registros_procesados = cursor.fetchone()[0]
    
    print(f"   ✅ {registros_procesados:,} registros procesados (nuevos + actualizaciones)")
"""

print("📋 ANÁLISIS DEL PROBLEMA:")
print("=" * 80)
print()
print("❌ COLUMNAS INCORRECTAS (actuales en insertar_acuses_bulk):")
print("   nit_proveedor, razon_social, nro_docto, prefijo, folio,")
print("   fecha_docto, fecha_recepcion, tipo_docto, tipo_operacion,")
print("   descripcion_evento, codigo_rechazo")
print()
print("✅ COLUMNAS CORRECTAS (tabla acuses + Excel):")
print("   fecha, adquiriente, factura, emisor, nit_emisor, nit_pt,")
print("   estado_docto, descripcion_reclamo, tipo_documento, cufe, valor,")
print("   acuse_recibido, recibo_bien_servicio, aceptacion_expresa,")
print("   reclamo, aceptacion_tacita, clave_acuse")
print()
print("=" * 80)
print()
print("📝 PASOS PARA APLICAR EL FIX:")
print()
print("1. Buscar línea 1685 en routes.py (def insertar_acuses_bulk)")
print("2. REEMPLAZAR toda la función con el código de arriba")
print("3. Asegurar que calcular_jerarquia_acuse() existe en PostgreSQL")
print("4. Ejecutar: python PROC_DIRECTO_REAL.py")
print("5. Verificar éxito: python VERIFICAR_ESTADO_RAPIDO.py")
print()
print("🎯 RESULTADO ESPERADO:")
print("   ✅ 46,650 registros procesados en tabla acuses")
print("   ✅ Todas las 4 tablas con datos")
print("   ✅ Sin errores de columnas")
print()
