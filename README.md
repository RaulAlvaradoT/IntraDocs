# Documentador - Sistema de Membretes, Cotizaciones y Comprobantes de Pago

Sistema integral para agregar membretes a PDFs, generar cotizaciones profesionales y crear comprobantes de pago.

## Características

### 📄 Aplicar Membretes
- Agrega membretes personalizados a documentos PDF existentes
- Soporte para múltiples membretes en formato PNG
- Vista previa antes de aplicar

### 💼 Generar Cotizaciones
- Selección de división/empresa emisora
- Gestión de datos del cliente
- Catálogo de productos y servicios
- Productos personalizados
- Cálculo automático de subtotales, descuentos e IVA
- Generación de PDF profesional con logo

### 💳 Comprobantes de Pago
- Selección de división/empresa emisora
- Datos del cliente (nombre y teléfono)
- Múltiples conceptos de pago
- Adjuntar captura del comprobante de pago
- Cálculo automático de totales
- Generación de PDF con formato profesional

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

## Estructura del proyecto

- `membretes/` - Carpeta para almacenar los membretes en PNG (tamaño carta)
- `logos/` - Carpeta para almacenar los logos de las empresas
- `data/` - Archivos de configuración (empresas, productos)
- `utils/` - Utilidades para PDF, cotizaciones y comprobantes
- `app.py` - Aplicación principal de Streamlit

## Configuración

1. Coloca tus membretes en PNG en la carpeta `membretes/` con nombres descriptivos
2. Coloca los logos de tus empresas en la carpeta `logos/`
3. Edita `data/config.json` para configurar tus empresas y catálogo de productos

## Divisiones/Empresas Configuradas

El sistema soporta múltiples divisiones empresariales, cada una con su propia información:
- Instituto de Atención Integral y Desarrollo Humano A.C.
- Academia INTRA
- Javier Enrique Martínez Becerra
