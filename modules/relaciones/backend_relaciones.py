# ============================================
# backend_relaciones.py
# ============================================
# Este módulo maneja la generación de relaciones de facturas
# Incluye: lectura/escritura CSV, consecutivos, exportar Excel/PDF,
# resaltar facturas ya relacionadas y validaciones de selección.
# ============================================

from flask import Blueprint, request, send_file, session, render_template, flash, redirect, url_for
import csv, os
from datetime import datetime
import pandas as pd
from fpdf import FPDF

# Crear blueprint para este módulo
relaciones_bp = Blueprint('relaciones', __name__)

# ==========================
# Rutas de archivos del sistema
# ==========================
BD_PATH = r"D:/PERFIL/Escritorio/Escritorio/100. Proyecto/Proyecto Gestor Documental/bd"
DESTINO_ARCHIVOS = r"D:/PERFIL/Escritorio/Escritorio/100. Proyecto/Proyecto Gestor Documental/relaciones_generadas"
FACTURAS_CSV = os.path.join(BD_PATH, "facturas_recibidas.csv")
TERCEROS_CSV = os.path.join(BD_PATH, "terceros.csv")
RELACIONES_CSV = os.path.join(BD_PATH, "relaciones_facturas.csv")
CONSECUTIVO_PATH = os.path.join(BD_PATH, "consecutivos.csv")

# ==========================
# Funciones auxiliares
# ==========================

# Leer un CSV en forma de lista de diccionarios
def leer_csv(ruta):
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    except UnicodeDecodeError:
        with open(ruta, newline='', encoding='latin-1') as f:
            return list(csv.DictReader(f))

# Escribir fila en CSV, agregando encabezados si no existen
def escribir_csv(ruta, fila, encabezados):
    existe = os.path.exists(ruta)
    with open(ruta, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        if not existe:
            writer.writeheader()
        writer.writerow(fila)

# Generar consecutivo REL-XXX y actualizar consecutivos.csv
def generar_consecutivo():
    registros = leer_csv(CONSECUTIVO_PATH)
    fila = next((r for r in registros if r['tipo_documento'] == 'relacion_facturas'), None)
    if not fila:
        fila = {'tipo_documento': 'relacion_facturas', 'prefijo': 'REL', 'ultimo_consecutivo': '0'}
        registros.append(fila)
    numero = int(fila['ultimo_consecutivo']) + 1
    fila['ultimo_consecutivo'] = str(numero)
    with open(CONSECUTIVO_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['tipo_documento', 'prefijo', 'ultimo_consecutivo'])
        writer.writeheader()
        writer.writerows(registros)
    return f"REL-{str(numero).zfill(3)}"

# ==========================
# RUTA: POST -> Generar relación
# ==========================
@relaciones_bp.route('/generar_relacion', methods=['POST'])
def generar_relacion():
    datos = request.form
    seleccionadas = datos.getlist('factura')     # Facturas seleccionadas en el formulario
    destino = datos.get('destino')
    formato = datos.get('formato')
    sede = datos.get('sede') or 'GUADALUPE'
    usuario = session.get('usuario', 'anonimo')

    if not seleccionadas:
        flash("Debe seleccionar al menos una factura.", "warning")
        return redirect(url_for('relaciones.mostrar_formulario'))

    facturas = leer_csv(FACTURAS_CSV)
    terceros = {t['nit']: t['razon_social'] for t in leer_csv(TERCEROS_CSV)}
    relaciones_previas = leer_csv(RELACIONES_CSV)

    consecutivo = generar_consecutivo()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    seleccion = []
    ya_relacionadas = []

    # ==========================
    # Recorrer facturas recibidas
    # ==========================
    for f in facturas:
        clave = f"{f['nit']}-{f['prefijo']}-{f['folio']}"
        if clave in seleccionadas:
            # Revisar si ya está en alguna relación previa
            existente = next((r for r in relaciones_previas
                              if r['nit'] == f['nit'] and r['prefijo'] == f['prefijo'] and r['folio'] == f['folio']), None)

            razon = terceros.get(f['nit'], 'NO REGISTRADO')

            fila = {
                'numero_relacion': consecutivo,
                'fecha_generacion': fecha_hoy,  # Fecha de la RELACIÓN
                'para': destino,
                'usuario': usuario,
                'nit': f['nit'],
                'razon_social': razon,
                'prefijo': f['prefijo'],
                'folio': f['folio'],
                'co': f['co'],
                'valor_total': f['valor'],
                'fecha_factura': f.get('fecha', '')  # Fecha de la factura original
            }

            if not existente:
                escribir_csv(RELACIONES_CSV, fila, encabezados=fila.keys())
                seleccion.append(fila)
            else:
                ya_relacionadas.append(
                    f"Factura {f['prefijo']}-{f['folio']} ya fue relacionada "
                    f"el {existente['fecha_generacion']} en la relación {existente['numero_relacion']}"
                )

    if ya_relacionadas:
        flash(" ".join(ya_relacionadas), 'warning')

    if not seleccion:
        return redirect(url_for('relaciones.mostrar_formulario'))

    # Nombre del archivo generado
    nombre_archivo = f"Relacion_Facturas_{consecutivo}.{ 'pdf' if formato == 'pdf' else 'xlsx' }"
    ruta_local = os.path.join(DESTINO_ARCHIVOS, nombre_archivo)

    # ==========================
    # Exportar en formato PDF
    # ==========================
    if formato == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"RELACIÓN DE FACTURAS {consecutivo}", ln=True, align="C")
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, f"SEDE: {sede} — DESTINO: {destino} — FECHA: {fecha_hoy}", ln=True)
        pdf.ln(5)
        for f in seleccion:
            texto = f"{f['nit']} — {f['razon_social']} — {f['co']} — {f['prefijo']}-{f['folio']} — ${f['valor_total']}"
            pdf.multi_cell(0, 8, texto)
        pdf.output(ruta_local)
        flash(f"Relación generada correctamente: {nombre_archivo}", "success")
        return send_file(ruta_local, as_attachment=True)

    # ==========================
    # Exportar en formato Excel
    # ==========================
    else:
        # Guardar Excel completo (todos los campos)
        nombre_archivo_completo = f"Relacion_Facturas_{consecutivo}_COMPLETO.xlsx"
        ruta_completo = os.path.join(DESTINO_ARCHIVOS, nombre_archivo_completo)
        df_completo = pd.DataFrame(seleccion)
        df_completo.to_excel(ruta_completo, index=False)

        # Excel reducido para el usuario
        columnas_exportar = ["nit", "razon_social", "prefijo", "folio", "valor_total", "co", "fecha_factura"]
        df_export = pd.DataFrame(seleccion)[columnas_exportar]
        df_export.rename(columns={
            "nit": "NIT",
            "razon_social": "Razón Social",
            "prefijo": "Prefijo",
            "folio": "Folio",
            "valor_total": "Valor",
            "co": "Sede",
            "fecha_factura": "Fecha Generación"
        }, inplace=True)

        nombre_archivo_export = f"Relacion_Facturas_{consecutivo}.xlsx"
        ruta_local = os.path.join(DESTINO_ARCHIVOS, nombre_archivo_export)
        df_export.to_excel(ruta_local, index=False)

        flash(f"Relación generada correctamente: {nombre_archivo_export} "
              f"(también se guardó {nombre_archivo_completo})", "success")
        return send_file(ruta_local, as_attachment=True)


@relaciones_bp.route('/generar_relacion', methods=['GET'])
def mostrar_formulario():
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    co = request.args.get('co')
    destino = request.args.get('destino', 'CONTABILIDAD')
    formato = request.args.get('formato', 'Excel')

    hoy = datetime.now().strftime('%Y-%m-%d')
    desde = desde or hoy
    hasta = hasta or hoy

    facturas = leer_csv(FACTURAS_CSV)
    terceros = {t['nit']: t['razon_social'] for t in leer_csv(TERCEROS_CSV)}
    relaciones_previas = leer_csv(RELACIONES_CSV)

    # --------------------------
    # Normalizar clave de factura
    # --------------------------
    def clave_factura(nit, prefijo, folio):
        return (str(nit).strip(), str(prefijo).strip().upper(), str(folio).strip())

    # Crear índice de facturas ya relacionadas con número y fecha
    claves_relacionadas = {}
    for r in relaciones_previas:
        clave = clave_factura(r['nit'], r['prefijo'], r['folio'])
        claves_relacionadas[clave] = {
            "numero_relacion": r.get('numero_relacion', ''),
            "fecha_generacion": r.get('fecha_generacion', '')   # la fecha guardada en CSV
        }

    seleccionadas = []
    centros = set()

    # --------------------------
    # Recorrer facturas actuales
    # --------------------------
    for f in facturas:
        fecha_doc = f.get('fecha_radicacion')
        if not fecha_doc or not f.get('co'):
            continue
        if desde and fecha_doc < desde:
            continue
        if hasta and fecha_doc > hasta:
            continue

        f['co'] = str(f['co']).zfill(3)
        if co and co != f['co']:
            continue

        f['razon_social'] = terceros.get(f['nit'], 'NO REGISTRADO')
        f['clave'] = f"{f['nit']}-{f['prefijo']}-{f['folio']}"

        # Convertir valor
        valor_str = f['valor'].replace('.', '').replace(',', '.')
        try:
            f['valor'] = float(valor_str)
        except:
            f['valor'] = 0

        # Verificar si ya estaba relacionada
        clave = clave_factura(f['nit'], f['prefijo'], f['folio'])
        if clave in claves_relacionadas:
            rel = claves_relacionadas[clave]
            f['color'] = 'relacionada'
            f['tooltip'] = f"Factura {f['prefijo']}-{f['folio']} relacionada en {rel['numero_relacion']} el {rel['fecha_generacion']}"
            f['numero_relacion'] = rel['numero_relacion']
            f['fecha_relacion'] = rel['fecha_generacion']
        else:
            f['color'] = ''
            f['tooltip'] = ''
            f['numero_relacion'] = ''
            f['fecha_relacion'] = ''

        seleccionadas.append(f)
        centros.add(f['co'])

    lista_co = sorted(centros)

    return render_template('generar_relacion.html',
                           facturas=seleccionadas,
                           desde=desde,
                           hasta=hasta,
                           co=co or '',
                           destino=destino,
                           formato=formato,
                           lista_co=lista_co)
