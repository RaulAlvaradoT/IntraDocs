"""
Utilidades para manipulación de PDFs y aplicación de membretes
"""
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image


def aplicar_membrete_pdf(pdf_file, membrete_path):
    """
    Aplica un membrete a todas las páginas de un PDF.
    
    Args:
        pdf_file: Archivo PDF de entrada (bytes o file-like object)
        membrete_path: Ruta al archivo PNG del membrete
        
    Returns:
        bytes: PDF con el membrete aplicado
    """
    # Leer el PDF original
    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()
    
    # Crear overlay del membrete
    overlay_buffer = crear_overlay_membrete(membrete_path)
    overlay_pdf = PdfReader(overlay_buffer)
    overlay_page = overlay_pdf.pages[0]
    
    # Aplicar el membrete a cada página
    for page in pdf_reader.pages:
        # Superponer el membrete sobre la página original
        page.merge_page(overlay_page)
        pdf_writer.add_page(page)
    
    # Escribir el resultado a un buffer
    output_buffer = io.BytesIO()
    pdf_writer.write(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer.getvalue()


def crear_overlay_membrete(membrete_path):
    """
    Crea un PDF de una página con el membrete como overlay transparente.
    
    Args:
        membrete_path: Ruta al archivo PNG del membrete
        
    Returns:
        BytesIO: Buffer con el PDF del overlay
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  # 8.5 x 11 pulgadas (612 x 792 puntos)
    
    try:
        # Abrir imagen del membrete
        img = Image.open(membrete_path)
        img_width, img_height = img.size
        
        # Calcular la proporción de la imagen
        aspect_ratio = img_width / img_height
        page_aspect_ratio = width / height
        
        # Ajustar para cubrir toda la página manteniendo proporción
        if aspect_ratio > page_aspect_ratio:
            # La imagen es más ancha proporcionalmente
            new_height = height
            new_width = height * aspect_ratio
            x_offset = -(new_width - width) / 2
            y_offset = 0
        else:
            # La imagen es más alta proporcionalmente
            new_width = width
            new_height = width / aspect_ratio
            x_offset = 0
            y_offset = 0
        
        # Dibujar la imagen como overlay desde la parte superior
        # En ReportLab, y=0 es abajo, así que para que esté arriba usamos height - new_height
        c.drawImage(membrete_path, x_offset, height - new_height + y_offset, 
                   width=new_width, height=new_height, mask='auto')
    except Exception as e:
        print(f"Error al cargar membrete: {e}")
    
    c.save()
    buffer.seek(0)
    return buffer


def validar_pdf(file):
    """
    Valida que el archivo sea un PDF válido.
    
    Args:
        file: Archivo a validar
        
    Returns:
        tuple: (bool: es válido, str: mensaje de error si aplica)
    """
    try:
        PdfReader(file)
        file.seek(0)  # Resetear el puntero del archivo
        return True, None
    except Exception as e:
        return False, f"Error al leer el PDF: {str(e)}"
