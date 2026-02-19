"""
Utilidades para manipulación de PDFs y aplicación de membretes
"""
import io
import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image

try:
    from docx2pdf import convert
    DOCX2PDF_DISPONIBLE = True
except ImportError:
    DOCX2PDF_DISPONIBLE = False


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


def convertir_word_a_pdf(docx_file):
    """
    Convierte un archivo Word (.docx) a PDF.
    
    Args:
        docx_file: Archivo Word de entrada (file-like object de Streamlit)
        
    Returns:
        bytes: PDF convertido en bytes, o None si falla
    """
    if not DOCX2PDF_DISPONIBLE:
        raise ImportError("La librería docx2pdf no está instalada. Instala con: pip install docx2pdf")
    
    try:
        # Crear archivos temporales
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_docx:
            tmp_docx.write(docx_file.read())
            tmp_docx_path = tmp_docx.name
        
        tmp_pdf_path = tmp_docx_path.replace('.docx', '.pdf')
        
        # Convertir Word a PDF
        convert(tmp_docx_path, tmp_pdf_path)
        
        # Leer el PDF generado
        with open(tmp_pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        # Limpiar archivos temporales
        try:
            os.unlink(tmp_docx_path)
            os.unlink(tmp_pdf_path)
        except:
            pass
        
        return pdf_bytes
        
    except Exception as e:
        # Limpiar archivos temporales en caso de error
        try:
            if 'tmp_docx_path' in locals():
                os.unlink(tmp_docx_path)
            if 'tmp_pdf_path' in locals() and os.path.exists(tmp_pdf_path):
                os.unlink(tmp_pdf_path)
        except:
            pass
        raise Exception(f"Error al convertir Word a PDF: {str(e)}")


def validar_documento(file, nombre_archivo):
    """
    Valida que el archivo sea PDF o Word válido.
    
    Args:
        file: Archivo a validar
        nombre_archivo: Nombre del archivo
        
    Returns:
        tuple: (bool: es válido, str: tipo de archivo ('pdf' o 'docx'), str: mensaje de error si aplica)
    """
    extension = nombre_archivo.lower().split('.')[-1]
    
    if extension == 'pdf':
        es_valido, error = validar_pdf(file)
        return es_valido, 'pdf', error
    elif extension in ['docx', 'doc']:
        # Para Word, solo verificamos que no esté vacío
        if file.size > 0:
            return True, 'docx', None
        else:
            return False, 'docx', "El archivo Word está vacío"
    else:
        return False, None, f"Formato no soportado: {extension}"

