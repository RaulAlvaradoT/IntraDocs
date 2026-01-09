"""
Utilidades para generación de cotizaciones en PDF
"""
import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os


def generar_cotizacion_pdf(datos_cotizacion, config):
    """
    Genera un PDF de cotización profesional.
    
    Args:
        datos_cotizacion: Dict con los datos de la cotizacion
        config: Configuración del sistema
        
    Returns:
        bytes: PDF generado
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.60*inch,
        leftMargin=0.60*inch,
        topMargin=0.05*inch,
        bottomMargin=0.15*inch
    )
    
    # Contenedor de elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.black,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    style_heading = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica'
    )
    
    style_small = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        fontName='Helvetica'
    )
    
    # --- ENCABEZADO CON TÍTULO Y LOGO ---
    empresa = datos_cotizacion['empresa']
    
    # Crear tabla con título a la izquierda y logo a la derecha
    header_data = []
    
    # Título de cotización
    titulo_cotizacion = Paragraph("COTIZACIÓN", style_title)
    
    # Logo a la derecha
    if os.path.exists(empresa['logo']):
        try:
            logo = Image(empresa['logo'], width=1.75*inch, height=1.75*inch)
            header_data.append([titulo_cotizacion, logo])
        except:
            header_data.append([titulo_cotizacion, ""])
    else:
        header_data.append([titulo_cotizacion, ""])
    
    # Crear tabla con distribución 60% - 40%
    header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.015*inch))
    
    # --- INFORMACIÓN DE LA COTIZACIÓN ---
    fecha_actual = datetime.now()
    fecha_validez = fecha_actual + timedelta(days=config['configuracion']['validez_cotizacion_dias'])
    
    info_data = [
        ['Folio:', datos_cotizacion['folio']],
        ['Fecha:', fecha_actual.strftime('%d/%m/%Y'), 'Cotización válida hasta el:', fecha_validez.strftime('%d/%m/%Y')]
    ]
    
    info_table = Table(info_data, colWidths=[0.9*inch, 2.06*inch, 2.06*inch, 2.06*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 1), (2, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 1), (2, 1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('SPAN', (1, 0), (3, 0)),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- DATOS DEL CLIENTE ---
    cliente = datos_cotizacion['cliente']
    elements.append(Paragraph("DATOS DEL CLIENTE", style_heading))
    
    cliente_data = [
        ['Cliente:', cliente.get('nombre', '')],
        ['Empresa:', cliente.get('empresa', '')],
        ['Dirección:', cliente.get('direccion', '')],
        ['Teléfono:', cliente.get('telefono', '')],
        ['Email:', cliente.get('email', '')]
    ]
    
    cliente_table = Table(cliente_data, colWidths=[0.9*inch, 6.2*inch])
    cliente_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(cliente_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- TABLA DE PRODUCTOS/SERVICIOS ---
    elements.append(Paragraph("DETALLE", style_heading))
    
    # Encabezados de la tabla
    productos_data = [['Código', 'Descripción', 'Cantidad', '$ Unit.', 'Subtotal']]
    
    # Agregar productos
    subtotal_general = 0
    for item in datos_cotizacion['items']:
        codigo = item['codigo']
        descripcion = item['descripcion']
        cantidad = item['cantidad']
        precio_unitario = item['precio_unitario']
        subtotal = cantidad * precio_unitario
        subtotal_general += subtotal
        
        productos_data.append([
            codigo,
            descripcion,
            str(cantidad),
            f"${precio_unitario:,.2f}",
            f"${subtotal:,.2f}"
        ])
    
    productos_table = Table(productos_data, colWidths=[0.8*inch, 3.8*inch, 0.7*inch, 0.9*inch, 0.9*inch])
    productos_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    elements.append(productos_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # --- TOTALES ---
    # Calcular descuento
    descuento_valor = 0
    descuento_config = datos_cotizacion.get('descuento', {})
    
    if descuento_config.get('aplicar', False):
        tipo_descuento = descuento_config.get('tipo', 'porcentaje')
        valor_descuento = descuento_config.get('valor', 0)
        
        if tipo_descuento == 'porcentaje':
            descuento_valor = subtotal_general * (valor_descuento / 100)
        else:  # monto fijo
            descuento_valor = valor_descuento
    
    subtotal_con_descuento = subtotal_general - descuento_valor
    iva = subtotal_con_descuento * config['configuracion']['iva']
    total = subtotal_con_descuento + iva
    
    totales_data = [
        ['Subtotal:', f"${subtotal_general:,.2f}"]
    ]
    
    if descuento_valor > 0:
        tipo_desc = descuento_config.get('tipo', 'porcentaje')
        valor_desc = descuento_config.get('valor', 0)
        desc_label = f"Descuento ({valor_desc}%):" if tipo_desc == 'porcentaje' else "Descuento:"
        totales_data.append([desc_label, f"-${descuento_valor:,.2f}"])
    
    totales_data.extend([
        [f"IVA ({config['configuracion']['iva']*100:.0f}%):", f"${iva:,.2f}"],
        ['TOTAL:', f"${total:,.2f}"]
    ])
    
    totales_table = Table(totales_data, colWidths=[4.8*inch, 1.7*inch])
    totales_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -2), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))

    elements.append(totales_table)
    elements.append(Spacer(1, 0.75*inch))
    
    # --- TÉRMINOS Y CONDICIONES Y DATOS DE EMPRESA EN COLUMNAS ---
    # Estilo para datos de empresa alineados a la derecha
    style_empresa = ParagraphStyle(
        'CustomEmpresa',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        fontName='Helvetica',
        alignment=TA_RIGHT
    )
    
    # Crear párrafo de términos y condiciones (40% del ancho)
    terminos_text = config['configuracion']['terminos_condiciones'].replace('\n', '<br/>')
    terminos_para = Paragraph(f"<b>TÉRMINOS Y CONDICIONES</b><br/><br/>{terminos_text}", style_small)
    
    # Crear párrafo de datos de empresa (60% del ancho)
    empresa_text = (f"<b>{empresa['razon_social']}</b><br/>"
                   f"RFC: {empresa['rfc']}<br/>"
                   f"{empresa['direccion']}<br/>"
                   f"Tel: {empresa['telefono']}<br/>"
                   f"Email: {empresa['email']}")
    empresa_para = Paragraph(empresa_text, style_empresa)
    
    # Tabla con dos columnas: 40% términos, 60% datos empresa
    footer_data = [[terminos_para, empresa_para]]
    footer_table = Table(footer_data, colWidths=[3*inch, 4*inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('LEFTPADDING', (1, 0), (1, -1), 10),
    ]))
    
    elements.append(footer_table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer.getvalue()
