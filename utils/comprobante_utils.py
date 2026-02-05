"""
Utilidades para generación de comprobantes de pago
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import io
from PIL import Image as PILImage


def generar_comprobante_pdf(datos, config):
    """
    Genera un PDF de comprobante de pago
    
    Args:
        datos (dict): Diccionario con la información del comprobante
        config (dict): Configuración general del sistema
    
    Returns:
        bytes: PDF generado en bytes
    """
    buffer = io.BytesIO()
    
    # Crear documento
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Contenedor de elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitulo_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    texto_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2C3E50'),
        alignment=TA_LEFT
    )
    
    texto_derecha = ParagraphStyle(
        'CustomRight',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2C3E50'),
        alignment=TA_RIGHT
    )
    
    # ===== ENCABEZADO =====
    empresa = datos['empresa']
    
    # Logo (25%) y Título (75%) en la parte superior
    try:
        logo = Image(empresa['logo'], width=1.2*inch, height=1.2*inch)
        encabezado_data = [
            [logo, Paragraph("COMPROBANTE DE PAGO", titulo_style)]
        ]
        
        tabla_encabezado = Table(encabezado_data, colWidths=[1.75*inch, 5.25*inch])
        tabla_encabezado.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ]))
        
        elements.append(tabla_encabezado)
    except:
        # Si no hay logo, solo mostrar título
        elements.append(Paragraph("COMPROBANTE DE PAGO", titulo_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Folio y fecha
    info_folio = [
        [Paragraph(f"<b>Folio:</b> {datos['folio']}", texto_normal),
         Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}", texto_derecha)]
    ]
    tabla_folio = Table(info_folio, colWidths=[3.5*inch, 3.5*inch])
    tabla_folio.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(tabla_folio)
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== INFORMACIÓN DEL CLIENTE =====
    elements.append(Paragraph("DATOS DEL CLIENTE", subtitulo_style))
    
    cliente = datos['cliente']
    datos_cliente = [
        [Paragraph("<b>Nombre completo:</b>", texto_normal), 
         Paragraph(cliente['nombre'], texto_normal)],
        [Paragraph("<b>Número celular:</b>", texto_normal), 
         Paragraph(cliente['telefono'], texto_normal)]
    ]
    
    tabla_cliente = Table(datos_cliente, colWidths=[2*inch, 5*inch])
    tabla_cliente.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(tabla_cliente)
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== CONCEPTOS =====
    elements.append(Paragraph("CONCEPTOS", subtitulo_style))
    
    # Encabezado de tabla de conceptos
    datos_conceptos = [[
        Paragraph("<b>No</b>", texto_normal),
        Paragraph("<b>Concepto</b>", texto_normal),
        Paragraph("<b>Monto</b>", texto_derecha)
    ]]
    
    # Agregar conceptos
    total_conceptos = 0
    for idx, concepto in enumerate(datos['conceptos'], 1):
        monto = float(concepto['monto'])
        total_conceptos += monto
        
        datos_conceptos.append([
            Paragraph(str(idx), texto_normal),
            Paragraph(concepto['descripcion'], texto_normal),
            Paragraph(f"${monto:,.2f}", texto_derecha)
        ])
    
    # Agregar fila de total
    datos_conceptos.append([
        Paragraph("", texto_normal),
        Paragraph("<b>TOTAL:</b>", texto_derecha),
        Paragraph(f"<b>${total_conceptos:,.2f} {config['configuracion']['moneda']}</b>", texto_derecha)
    ])
    
    tabla_conceptos = Table(datos_conceptos, colWidths=[0.5*inch, 4.5*inch, 2*inch])
    tabla_conceptos.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -2), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
        # Fila de total
        ('BACKGROUND', (1, -1), (-1, -1), colors.HexColor('#ECF0F1')),
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, -1), (-1, -1), 12),
        ('TOPPADDING', (1, -1), (-1, -1), 10),
        ('BOTTOMPADDING', (1, -1), (-1, -1), 10),
        ('LINEABOVE', (1, -1), (-1, -1), 2, colors.HexColor('#2C3E50')),
    ]))
    
    elements.append(tabla_conceptos)
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== DATOS DE LA EMPRESA AL FINAL DE LA HOJA 1 =====
    
    # Información de la empresa
    info_empresa_data = [
        [Paragraph("<b>Datos de la empresa:</b>", texto_normal)],
        [Paragraph(f"<b>{empresa['razon_social']}</b>", texto_normal)],
        [Paragraph(f"RFC: {empresa['rfc']}", texto_normal)],
        [Paragraph(f"{empresa['direccion']}", texto_normal)],
        [Paragraph(f"Tel: {empresa['telefono']} | Email: {empresa['email']}", texto_normal)]
    ]
    
    tabla_info_empresa = Table(info_empresa_data, colWidths=[7*inch])
    tabla_info_empresa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(tabla_info_empresa)
    
    # ===== COMPROBANTE DE PAGO EN HOJA 2 =====
    if 'comprobante_imagen' in datos and datos['comprobante_imagen']:
        # Salto de página
        elements.append(PageBreak())
        
        elements.append(Paragraph("COMPROBANTE DE PAGO", subtitulo_style))
        
        try:
            # Cargar y redimensionar imagen
            img = PILImage.open(datos['comprobante_imagen'])
            
            # Calcular dimensiones manteniendo proporción
            max_width = 4 * inch
            max_height = 5 * inch
            
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            if img_width > img_height:
                new_width = min(max_width, img_width)
                new_height = new_width / aspect_ratio
            else:
                new_height = min(max_height, img_height)
                new_width = new_height * aspect_ratio
            
            # Agregar imagen al PDF
            img_reportlab = Image(datos['comprobante_imagen'], width=new_width, height=new_height)
            
            # Centrar imagen
            tabla_img = Table([[img_reportlab]], colWidths=[7*inch])
            tabla_img.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(tabla_img)
            elements.append(Spacer(1, 0.2*inch))
            
        except Exception as e:
            elements.append(Paragraph(f"<i>Error al cargar comprobante: {str(e)}</i>", texto_normal))
    
    # ===== PIE DE PÁGINA =====
    elements.append(Spacer(1, 0.2*inch))
    
    pie_texto = f"""
    <para align=center>
    <font size=8 color='grey'>
    Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}<br/>
    Este comprobante tiene validez como constancia de pago
    </font>
    </para>
    """
    
    elements.append(Paragraph(pie_texto, styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
