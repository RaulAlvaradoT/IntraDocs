import streamlit as st
import os
import io
import json
from datetime import datetime
from utils.pdf_utils import aplicar_membrete_pdf, validar_documento, convertir_word_a_pdf
from utils.cotizacion_utils import generar_cotizacion_pdf
from utils.comprobante_utils import generar_comprobante_pdf


st.set_page_config(
    page_title="Documentador - Membretes, Cotizaciones y Comprobantes",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    config_path = "data/config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def obtener_membretes_disponibles():
    membretes_dir = "membretes"
    if not os.path.exists(membretes_dir):
        return []
    
    membretes = []
    for archivo in os.listdir(membretes_dir):
        if archivo.lower().endswith('.png'):
            membretes.append(os.path.join(membretes_dir, archivo))
    
    return sorted(membretes)


def modulo_membretes():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Selecciona el membrete")
        
        membretes = obtener_membretes_disponibles()
        
        if not membretes:
            st.warning("⚠️ No se encontraron membretes en la carpeta 'membretes/'")
            st.info("📝 Coloca tus archivos PNG de membretes en la carpeta 'membretes/' con nombres como: membrete_1.png, membrete_2.png, etc.")
            return
        
        membrete_nombres = [os.path.basename(m) for m in membretes]
        membrete_seleccionado_idx = st.selectbox(
            "Elige un membrete:",
            range(len(membrete_nombres)),
            format_func=lambda x: membrete_nombres[x]
        )
        
        membrete_path = membretes[membrete_seleccionado_idx]
        
        st.image(membrete_path, caption=f"Previsualización: {membrete_nombres[membrete_seleccionado_idx]}", 
            width=250)
    
    with col2:
        st.subheader("2. Sube tu documento")
        
        documento_file = st.file_uploader(
            "Selecciona el archivo PDF o Word",
            type=['pdf', 'docx', 'doc'],
            help="Sube un documento PDF o Word (.docx) para aplicarle el membrete"
        )
        
        if documento_file:
            st.success(f"✅ Archivo cargado: {documento_file.name}")
            
            es_valido, tipo_archivo, error = validar_documento(documento_file, documento_file.name)

            if not es_valido:
                st.error(f"❌ {error}")
                return

            if tipo_archivo == 'docx':
                st.info("📄 Documento Word detectado - se convertirá a PDF antes de aplicar el membrete")

            if st.button("🎨 Aplicar Membrete", type="primary", use_container_width=True):
                with st.spinner("Procesando documento..."):
                    try:
                        if tipo_archivo == 'docx':
                            with st.spinner("Convirtiendo Word a PDF..."):
                                pdf_bytes = convertir_word_a_pdf(documento_file)
                                pdf_file = io.BytesIO(pdf_bytes)
                                nombre_base = os.path.splitext(documento_file.name)[0]
                        else:
                            pdf_file = documento_file
                            nombre_base = os.path.splitext(documento_file.name)[0]
                        
                        with st.spinner("Aplicando membrete..."):
                            pdf_con_membrete = aplicar_membrete_pdf(pdf_file, membrete_path)
                        
                        st.success("✅ ¡Membrete aplicado correctamente!")
                        
                        nombre_salida = f"{nombre_base}_con_membrete.pdf"
                        
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
    
    config = cargar_configuracion()
    if not config:
        st.error("❌ No se pudo cargar la configuración. Verifica el archivo data/config.json")
        return
    
    if 'items_cotizacion' not in st.session_state:
        st.session_state.items_cotizacion = []
    
    st.subheader("1. Selecciona la Empresa")
    
    empresas = config['empresas']
    empresa_nombres = [emp['nombre'] for emp in empresas]
    
    empresa_idx = st.selectbox(
        "Empresa que cotiza:",
        range(len(empresa_nombres)),
        format_func=lambda x: empresa_nombres[x]
    )
    
    empresa_seleccionada = empresas[empresa_idx]
    
    with st.expander("📋 Ver datos de la empresa"):
        st.write(f"**Razón Social:** {empresa_seleccionada['razon_social']}")
        st.write(f"**RFC:** {empresa_seleccionada['rfc']}")
        st.write(f"**Dirección:** {empresa_seleccionada['direccion']}")
        st.write(f"**Teléfono:** {empresa_seleccionada['telefono']}")
        st.write(f"**Email:** {empresa_seleccionada['email']}")
    
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
            
            for idx, item in enumerate(st.session_state.items_cotizacion):
                with st.expander(f"**{idx+1}.** {item['codigo']} - {item['descripcion']}", expanded=False):
                    col_edit1, col_edit2 = st.columns(2)
                    
                    with col_edit1:
                        nuevo_codigo = st.text_input("Código", value=item['codigo'], key=f"edit_codigo_{idx}")
                        nueva_cantidad = st.number_input("Cantidad", min_value=1, value=item['cantidad'], key=f"edit_cant_{idx}")
                    
                    with col_edit2:
                        nueva_desc = st.text_input("Descripción", value=item['descripcion'], key=f"edit_desc_{idx}")
                        nuevo_precio = st.number_input("Precio Unit.", min_value=0.0, value=float(item['precio_unitario']), step=10.0, key=f"edit_precio_{idx}")
                    
                    st.caption(f"**Subtotal:** ${nueva_cantidad * nuevo_precio:,.2f}")
                    
                    col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
                    
                    with col_btn1:
                        if st.button("💾 Guardar", key=f"save_{idx}", use_container_width=True):
                            st.session_state.items_cotizacion[idx] = {
                                'codigo': nuevo_codigo,
                                'descripcion': nueva_desc,
                                'cantidad': nueva_cantidad,
                                'precio_unitario': nuevo_precio
                            }
                            st.success("✅ Guardado")
                            st.rerun()
                    
                    with col_btn2:
                        if idx > 0:
                            if st.button("⬆️", key=f"up_{idx}", help="Mover arriba", use_container_width=True):
                                st.session_state.items_cotizacion[idx], st.session_state.items_cotizacion[idx-1] = \
                                    st.session_state.items_cotizacion[idx-1], st.session_state.items_cotizacion[idx]
                                st.rerun()
                    
                    with col_btn3:
                        if idx < len(st.session_state.items_cotizacion) - 1:
                            if st.button("⬇️", key=f"down_{idx}", help="Mover abajo", use_container_width=True):
                                st.session_state.items_cotizacion[idx], st.session_state.items_cotizacion[idx+1] = \
                                    st.session_state.items_cotizacion[idx+1], st.session_state.items_cotizacion[idx]
                                st.rerun()
                    
                    with col_btn4:
                        if st.button("🗑️ Eliminar", key=f"del_{idx}", type="secondary", use_container_width=True):
                            st.session_state.items_cotizacion.pop(idx)
                            st.rerun()
            
            st.markdown("---")
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
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            st.metric("Subtotal", f"${subtotal:,.2f}")
            if aplicar_descuento and descuento_valor > 0:
                st.metric("Descuento", f"-${descuento_valor:,.2f}")
            st.metric(f"IVA ({config['configuracion']['iva']*100:.0f}%)", f"${iva:,.2f}")
        
        with col3:
            st.markdown("### TOTAL")
            st.markdown(f"## ${total:,.2f} {config['configuracion']['moneda']}")
    
    st.subheader("5. Generar Cotización")
    
    col_btn1, col_btn2 = st.columns([5,1])
    
    with col_btn1:
        generar_pdf = st.button("📄 Generar PDF de Cotización", type="primary", use_container_width=True)
    
    with col_btn2:
        generar_prueba = st.button("PDF de Prueba", use_container_width=True, help="Genera un PDF con datos de ejemplo para ver el diseño")
    
    if generar_prueba:
        with st.spinner("Generando PDF de prueba..."):
            try:
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
                
                pdf_bytes = generar_cotizacion_pdf(datos_prueba, config)
                
                st.success("✅ ¡PDF de prueba generado!")
                
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
                
                pdf_bytes = generar_cotizacion_pdf(datos_cotizacion, config)
                
                st.success("✅ ¡Cotización generada correctamente!")
                
                nombre_archivo = f"Cotizacion_{folio}_{datetime.now().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="📥 Descargar Cotización PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error al generar la cotización: {str(e)}")


def modulo_comprobantes():
    
    config = cargar_configuracion()
    if not config:
        st.error("❌ No se pudo cargar la configuración. Verifica el archivo data/config.json")
        return
    
    if 'conceptos_comprobante' not in st.session_state:
        st.session_state.conceptos_comprobante = []
    
    st.subheader("1. Selecciona la División")
    
    empresas = config['empresas']
    empresa_nombres = [emp['nombre'] for emp in empresas]
    
    empresa_idx = st.selectbox(
        "División que emite el comprobante:",
        range(len(empresa_nombres)),
        format_func=lambda x: empresa_nombres[x]
    )
    
    empresa_seleccionada = empresas[empresa_idx]
    
    with st.expander("📋 Ver datos de la división"):
        st.write(f"**Razón Social:** {empresa_seleccionada['razon_social']}")
        st.write(f"**RFC:** {empresa_seleccionada['rfc']}")
        st.write(f"**Dirección:** {empresa_seleccionada['direccion']}")
        st.write(f"**Teléfono:** {empresa_seleccionada['telefono']}")
        st.write(f"**Email:** {empresa_seleccionada['email']}")
    
    st.subheader("2. Datos del Cliente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cliente_nombre = st.text_input("Nombre completo *", placeholder="Juan Pérez García")
    
    with col2:
        cliente_telefono = st.text_input("Número celular *", placeholder="+52 844 123 4567")
    
    folio = st.text_input("Folio del Comprobante *", value=f"COMP-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    
    st.subheader("3. Conceptos de Pago")
    
    col_agregar, col_conceptos = st.columns([1, 1])
    
    with col_agregar:
        st.markdown("### ➕ Agregar Concepto")
        
        concepto_desc = st.text_area("", placeholder="Ej: Constancia", label_visibility="collapsed")
        concepto_monto = st.number_input("Monto", min_value=0.0, value=0.0, step=50.0, format="%.2f")
        
        if st.button("➕ Agregar Concepto", use_container_width=True, type="primary"):
            if concepto_desc and concepto_monto > 0:
                st.session_state.conceptos_comprobante.append({
                    'descripcion': concepto_desc,
                    'monto': concepto_monto
                })
                st.rerun()
            else:
                st.error("Completa la descripción y el monto")
    
    with col_conceptos:
        st.markdown("### 📋 Conceptos Agregados")
        
        if st.session_state.conceptos_comprobante:
            st.write(f"**Total de conceptos:** {len(st.session_state.conceptos_comprobante)}")
            
            for idx, concepto in enumerate(st.session_state.conceptos_comprobante):
                with st.expander(f"**{idx+1}.** {concepto['descripcion'][:50]}...", expanded=False):
                    nueva_desc = st.text_area("Descripción", value=concepto['descripcion'], key=f"edit_desc_comp_{idx}")
                    nuevo_monto = st.number_input("Monto", min_value=0.0, value=float(concepto['monto']), step=50.0, key=f"edit_monto_comp_{idx}", format="%.2f")
                    
                    st.caption(f"**Monto:** ${nuevo_monto:,.2f}")
                    
                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                    
                    with col_btn1:
                        if st.button("💾 Guardar", key=f"save_comp_{idx}", use_container_width=True):
                            st.session_state.conceptos_comprobante[idx] = {
                                'descripcion': nueva_desc,
                                'monto': nuevo_monto
                            }
                            st.success("✅ Guardado")
                            st.rerun()
                    
                    with col_btn2:
                        if idx > 0:
                            if st.button("⬆️", key=f"up_comp_{idx}", help="Mover arriba", use_container_width=True):
                                st.session_state.conceptos_comprobante[idx], st.session_state.conceptos_comprobante[idx-1] = \
                                    st.session_state.conceptos_comprobante[idx-1], st.session_state.conceptos_comprobante[idx]
                                st.rerun()
                    
                    with col_btn3:
                        if idx < len(st.session_state.conceptos_comprobante) - 1:
                            if st.button("⬇️", key=f"down_comp_{idx}", help="Mover abajo", use_container_width=True):
                                st.session_state.conceptos_comprobante[idx], st.session_state.conceptos_comprobante[idx+1] = \
                                    st.session_state.conceptos_comprobante[idx+1], st.session_state.conceptos_comprobante[idx]
                                st.rerun()
                    
                    with col_btn4:
                        if st.button("🗑️ Eliminar", key=f"del_comp_{idx}", type="secondary", use_container_width=True):
                            st.session_state.conceptos_comprobante.pop(idx)
                            st.rerun()
            
            st.markdown("---")
            if st.button("🗑️ Limpiar todos los conceptos", type="secondary", use_container_width=True):
                st.session_state.conceptos_comprobante = []
                st.rerun()
        else:
            st.info("No hay conceptos agregados al comprobante")
    
    st.markdown("---")
    st.subheader("4. Total a Pagar")
    
    if st.session_state.conceptos_comprobante:
        total = sum(concepto['monto'] for concepto in st.session_state.conceptos_comprobante)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col3:
            st.markdown("### TOTAL")
            st.markdown(f"## ${total:,.2f} {config['configuracion']['moneda']}")
    
    st.markdown("---")
    st.subheader("5. Adjuntar Comprobante de Pago (Opcional)")
    
    comprobante_imagen = st.file_uploader(
        "Sube una captura del comprobante de pago",
        type=['png', 'jpg', 'jpeg'],
        help="Adjunta una imagen del comprobante bancario o transferencia"
    )
    
    if comprobante_imagen:
        st.success("✅ Comprobante cargado")
        st.image(comprobante_imagen, caption="Vista previa del comprobante", width=300)
    
    st.markdown("---")
    st.subheader("6. Generar Comprobante de Pago")
    
    generar_pdf = st.button("📄 Generar PDF de Comprobante", type="primary", use_container_width=True)
    
    if generar_pdf:
        if not cliente_nombre:
            st.error("❌ Ingresa el nombre completo del cliente")
            return
        
        if not cliente_telefono:
            st.error("❌ Ingresa el número celular del cliente")
            return
        
        if not folio:
            st.error("❌ Ingresa el folio del comprobante")
            return
        
        if not st.session_state.conceptos_comprobante:
            st.error("❌ Agrega al menos un concepto al comprobante")
            return
        
        with st.spinner("Generando comprobante de pago..."):
            try:
                datos_comprobante = {
                    'empresa': empresa_seleccionada,
                    'folio': folio,
                    'cliente': {
                        'nombre': cliente_nombre,
                        'telefono': cliente_telefono
                    },
                    'conceptos': st.session_state.conceptos_comprobante
                }
                
                if comprobante_imagen:
                    datos_comprobante['comprobante_imagen'] = comprobante_imagen
                
                pdf_bytes = generar_comprobante_pdf(datos_comprobante, config)
                
                st.success("✅ ¡Comprobante de pago generado correctamente!")
                
                nombre_archivo = f"Comprobante_{folio}_{datetime.now().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="📥 Descargar Comprobante PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error al generar el comprobante: {str(e)}")
                import traceback
                st.code(traceback.format_exc())


def main():
    st.sidebar.title("🔧 Menú Principal")
    st.sidebar.markdown("---")
    
    modulo = st.sidebar.radio(
        "Selecciona un módulo:",
        ["📄 Aplicar Membretes", "💼 Generar Cotizaciones", "💳 Comp. de Pago"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")
    
    
    if modulo == "📄 Aplicar Membretes":
        modulo_membretes()
    elif modulo == "💼 Generar Cotizaciones":
        modulo_cotizaciones()
    else:
        modulo_comprobantes()


if __name__ == "__main__":
    main()
