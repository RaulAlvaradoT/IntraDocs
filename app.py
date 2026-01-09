"""
Aplicación Streamlit - Sistema de Membretes y Cotizaciones
"""
import streamlit as st
import os
import json
from datetime import datetime
from utils.pdf_utils import aplicar_membrete_pdf, validar_pdf
from utils.cotizacion_utils import generar_cotizacion_pdf


# Configuración de la página
st.set_page_config(
    page_title="Documentador - Membretes y Cotizaciones",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para reducir padding inferior
st.markdown("""
    <style>
    .stMainBlockContainer.block-container.st-emotion-cache-zy6yx3.e4man114 {
        padding: 3rem 3rem 3rem !important;
    }
    .block-container {
        padding-bottom: 1rem !important;
    }
    </style>
""", unsafe_allow_html=True)


def cargar_configuracion():
    """Carga la configuración desde el archivo JSON"""
    config_path = "data/config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def obtener_membretes_disponibles():
    """Obtiene la lista de membretes disponibles en la carpeta"""
    membretes_dir = "membretes"
    if not os.path.exists(membretes_dir):
        return []
    
    membretes = []
    for archivo in os.listdir(membretes_dir):
        if archivo.lower().endswith('.png'):
            membretes.append(os.path.join(membretes_dir, archivo))
    
    return sorted(membretes)


def modulo_membretes():
    """Módulo para aplicar membretes"""
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Selecciona el membrete")
        
        membretes = obtener_membretes_disponibles()
        
        if not membretes:
            st.warning("⚠️ No se encontraron membretes en la carpeta 'membretes/'")
            st.info("📝 Coloca tus archivos PNG de membretes en la carpeta 'membretes/' con nombres como: membrete_1.png, membrete_2.png, etc.")
            return
        
        # Selector de membrete
        membrete_nombres = [os.path.basename(m) for m in membretes]
        membrete_seleccionado_idx = st.selectbox(
            "Elige un membrete:",
            range(len(membrete_nombres)),
            format_func=lambda x: membrete_nombres[x]
        )
        
        membrete_path = membretes[membrete_seleccionado_idx]
        
        # Previsualización del membrete
        st.image(membrete_path, caption=f"Previsualización: {membrete_nombres[membrete_seleccionado_idx]}", 
            width=250)
    
    with col2:
        st.subheader("2. Sube tu PDF")
        
        pdf_file = st.file_uploader(
            "Selecciona el archivo PDF",
            type=['pdf'],
            help="Sube el documento PDF al que quieres aplicar el membrete"
        )
        
        if pdf_file:
            st.success(f"✅ Archivo cargado")
            
            # Validar PDF
            es_valido, error = validar_pdf(pdf_file)
            
            if not es_valido:
                st.error(f"❌ {error}")
                return

            # Botón para procesar
            if st.button("🎨 Aplicar Membrete", type="primary", use_container_width=True):
                with st.spinner("Procesando PDF..."):
                    try:
                        # Aplicar membrete
                        pdf_con_membrete = aplicar_membrete_pdf(pdf_file, membrete_path)
                        
                        st.success("✅ ¡Membrete aplicado correctamente!")
                        
                        # Nombre del archivo de salida
                        nombre_salida = f"{os.path.splitext(pdf_file.name)[0]}_con_membrete.pdf"
                        
                        # Botón de descarga
                        st.download_button(
                            label="📥 Descargar PDF con Membrete",
                            data=pdf_con_membrete,
                            file_name=nombre_salida,
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Error al procesar el PDF: {str(e)}")


def modulo_cotizaciones():
    
    # Cargar configuración
    config = cargar_configuracion()
    if not config:
        st.error("❌ No se pudo cargar la configuración. Verifica el archivo data/config.json")
        return
    
    # Inicializar session state para items
    if 'items_cotizacion' not in st.session_state:
        st.session_state.items_cotizacion = []
    
    # SECCIÓN 1: Información de la Empresa
    st.subheader("1. Selecciona la Empresa")
    
    empresas = config['empresas']
    empresa_nombres = [emp['nombre'] for emp in empresas]
    
    empresa_idx = st.selectbox(
        "Empresa que cotiza:",
        range(len(empresa_nombres)),
        format_func=lambda x: empresa_nombres[x]
    )
    
    empresa_seleccionada = empresas[empresa_idx]
    
    # Mostrar info de la empresa
    with st.expander("📋 Ver datos de la empresa"):
        st.write(f"**Razón Social:** {empresa_seleccionada['razon_social']}")
        st.write(f"**RFC:** {empresa_seleccionada['rfc']}")
        st.write(f"**Dirección:** {empresa_seleccionada['direccion']}")
        st.write(f"**Teléfono:** {empresa_seleccionada['telefono']}")
        st.write(f"**Email:** {empresa_seleccionada['email']}")
    
    # SECCIÓN 2: Información del Cliente
    st.subheader("2. Datos del Cliente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cliente_nombre = st.text_input("Nombre del cliente *", placeholder="Juan Pérez")
        cliente_empresa = st.text_area("Empresa", placeholder="Empresa del Cliente S.A.")
        cliente_email = st.text_input("Email", placeholder="cliente@email.com")
    
    with col2:
        cliente_telefono = st.text_input("Teléfono", placeholder="+52 123 456 7890")
        cliente_direccion = st.text_area("Dirección", placeholder="Calle, Ciudad, CP")
        folio = st.text_input("Folio de Cotización *", value=f"COT-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    
    # SECCIÓN 3: Productos/Servicios
    st.subheader("3. Productos y Servicios")
    
    col_agregar, col_items = st.columns([1, 1])
    
    with col_agregar:
        st.markdown("### ➕ Agregar Items")
        
        catalogo = config['catalogo_productos']
        producto_opciones = [f"{p['codigo']} - {p['descripcion']}" for p in catalogo]
        
        producto_idx = st.selectbox(
            "",
            range(len(producto_opciones)),
            format_func=lambda x: producto_opciones[x],
            label_visibility="collapsed"
        )
        
        if st.button("➕ Agregar", use_container_width=True):
            producto = catalogo[producto_idx]
            st.session_state.items_cotizacion.append({
                'codigo': producto['codigo'],
                'descripcion': producto['descripcion'],
                'cantidad': 1,
                'precio_unitario': producto['precio_unitario']
            })
            st.rerun()
        
        st.markdown("---")
        st.write("**Agregar producto personalizado:**")
        
        nuevo_codigo = st.text_input("Código", key="nuevo_codigo", placeholder="PROD-XXX")
        nueva_descripcion = st.text_input("Descripción", key="nueva_desc", placeholder="Descripción del producto/servicio")
        
        col_cant, col_precio = st.columns(2)
        with col_cant:
            nueva_cantidad = st.number_input("Cantidad", min_value=1, value=1, key="nueva_cant")
        with col_precio:
            nuevo_precio = st.number_input("Precio Unit.", min_value=0.0, value=0.0, step=10.0, key="nuevo_precio")
        
        if st.button("➕ Agregar personalizado", use_container_width=True, type="primary"):
            if nuevo_codigo and nueva_descripcion and nuevo_precio > 0:
                st.session_state.items_cotizacion.append({
                    'codigo': nuevo_codigo,
                    'descripcion': nueva_descripcion,
                    'cantidad': nueva_cantidad,
                    'precio_unitario': nuevo_precio
                })
                st.rerun()
            else:
                st.error("Completa todos los campos")
    
    with col_items:
        st.markdown("### 📋 Items en Cotización")
        
        if st.session_state.items_cotizacion:
            st.write(f"**Total de items:** {len(st.session_state.items_cotizacion)}")
            
            # Mostrar items de forma compacta
            for idx, item in enumerate(st.session_state.items_cotizacion):
                with st.container():
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.markdown(f"**{item['codigo']}** - {item['descripcion']}")
                        st.caption(f"Cantidad: {item['cantidad']} | Precio: ${item['precio_unitario']:,.2f} | Subtotal: ${item['cantidad'] * item['precio_unitario']:,.2f}")
                    
                    with col2:
                        if st.button("🗑️", key=f"del_{idx}", help="Eliminar item"):
                            st.session_state.items_cotizacion.pop(idx)
                            st.rerun()
                    
                    st.divider()
            
            if st.button("🗑️ Limpiar todos los items", type="secondary", use_container_width=True):
                st.session_state.items_cotizacion = []
                st.rerun()
        else:
            st.info("No hay items agregados a la cotización")
    
    st.markdown("---")
    st.subheader("4. Descuentos y Totales")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        aplicar_descuento = st.checkbox("Aplicar descuento")
    
    with col2:
        if aplicar_descuento:
            tipo_descuento = st.selectbox("Tipo de descuento:", ["Porcentaje", "Monto"])
    
    with col3:
        if aplicar_descuento:
            if tipo_descuento == "Porcentaje":
                valor_descuento = st.number_input("Descuento (%):", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
            else:
                valor_descuento = st.number_input("Descuento ($):", min_value=0.0, value=0.0, step=10.0)
    
    # Calcular totales
    if st.session_state.items_cotizacion:
        subtotal = sum(item['cantidad'] * item['precio_unitario'] for item in st.session_state.items_cotizacion)
        
        descuento_valor = 0
        if aplicar_descuento:
            if tipo_descuento == "Porcentaje":
                descuento_valor = subtotal * (valor_descuento / 100)
            else:
                descuento_valor = valor_descuento
        
        subtotal_con_desc = subtotal - descuento_valor
        iva = subtotal_con_desc * config['configuracion']['iva']
        total = subtotal_con_desc + iva
        
        # Mostrar resumen
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            st.metric("Subtotal", f"${subtotal:,.2f}")
            if aplicar_descuento and descuento_valor > 0:
                st.metric("Descuento", f"-${descuento_valor:,.2f}")
            st.metric(f"IVA ({config['configuracion']['iva']*100:.0f}%)", f"${iva:,.2f}")
        
        with col3:
            st.markdown("### TOTAL")
            st.markdown(f"## ${total:,.2f} {config['configuracion']['moneda']}")
    
    # SECCIÓN 5: Generar PDF
    st.subheader("5. Generar Cotización")
    
    col_btn1, col_btn2 = st.columns([5,1])
    
    with col_btn1:
        generar_pdf = st.button("📄 Generar PDF de Cotización", type="primary", use_container_width=True)
    
    with col_btn2:
        generar_prueba = st.button("PDF de Prueba", use_container_width=True, help="Genera un PDF con datos de ejemplo para ver el diseño")
    
    if generar_prueba:
        with st.spinner("Generando PDF de prueba..."):
            try:
                # Datos de prueba
                datos_prueba = {
                    'empresa': empresa_seleccionada,
                    'folio': f"PRUEBA-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    'cliente': {
                        'nombre': 'Cliente de Prueba',
                        'empresa': 'Empresa Demo S.A. de C.V.',
                        'direccion': 'Av. Principal 123, Col. Centro, CP 12345, Ciudad, Estado',
                        'telefono': '+52 123 456 7890',
                        'email': 'cliente@ejemplo.com'
                    },
                    'items': [
                        {
                            'codigo': 'SERV-001',
                            'descripcion': 'Servicio de Consultoría',
                            'cantidad': 10,
                            'precio_unitario': 1500.00
                        },
                        {
                            'codigo': 'PROD-002',
                            'descripcion': 'Producto de ejemplo con descripción larga para probar el formato',
                            'cantidad': 5,
                            'precio_unitario': 850.00
                        },
                        {
                            'codigo': 'SERV-003',
                            'descripcion': 'Mantenimiento mensual',
                            'cantidad': 1,
                            'precio_unitario': 3200.00
                        }
                    ],
                    'descuento': {
                        'aplicar': True,
                        'tipo': 'Porcentaje',
                        'valor': 10
                    }
                }
                
                # Generar PDF de prueba
                pdf_bytes = generar_cotizacion_pdf(datos_prueba, config)
                
                st.success("✅ ¡PDF de prueba generado!")
                
                # Botón de descarga
                nombre_archivo = f"Cotizacion_PRUEBA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                st.download_button(
                    label="📥 Descargar PDF de Prueba",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error al generar PDF de prueba: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    if generar_pdf:
        # Validaciones
        if not cliente_nombre:
            st.error("❌ Ingresa el nombre del cliente")
            return
        
        if not folio:
            st.error("❌ Ingresa el folio de la cotización")
            return
        
        if not st.session_state.items_cotizacion:
            st.error("❌ Agrega al menos un item a la cotización")
            return
        
        with st.spinner("Generando cotización..."):
            try:
                # Preparar datos
                datos_cotizacion = {
                    'empresa': empresa_seleccionada,
                    'folio': folio,
                    'cliente': {
                        'nombre': cliente_nombre,
                        'empresa': cliente_empresa,
                        'direccion': cliente_direccion,
                        'telefono': cliente_telefono,
                        'email': cliente_email
                    },
                    'items': st.session_state.items_cotizacion,
                    'descuento': {
                        'aplicar': aplicar_descuento,
                        'tipo': tipo_descuento if aplicar_descuento else 'Porcentaje',
                        'valor': valor_descuento if aplicar_descuento else 0
                    }
                }
                
                # Generar PDF
                pdf_bytes = generar_cotizacion_pdf(datos_cotizacion, config)
                
                st.success("✅ ¡Cotización generada correctamente!")
                
                # Botón de descarga
                nombre_archivo = f"Cotizacion_{folio}_{datetime.now().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="📥 Descargar Cotización PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    type="primary",
                    type="primary",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error al generar la cotización: {str(e)}")


def main():
    """Función principal de la aplicación"""
    # Sidebar
    st.sidebar.title("🔧 Menú Principal")
    st.sidebar.markdown("---")
    
    modulo = st.sidebar.radio(
        "Selecciona un módulo:",
        ["📄 Aplicar Membretes", "💼 Generar Cotizaciones"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")
    
    
    # Mostrar el módulo seleccionado
    if modulo == "📄 Aplicar Membretes":
        modulo_membretes()
    else:
        modulo_cotizaciones()


if __name__ == "__main__":
    main()
