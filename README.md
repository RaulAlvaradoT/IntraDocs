# Documentador - Sistema de Membretes y Cotizaciones

Sistema para agregar membretes a PDFs y generar cotizaciones profesionales.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

## Estructura del proyecto

- `membretes/` - Carpeta para almacenar los 5 membretes en PNG (tamaño carta)
- `logos/` - Carpeta para almacenar los logos de las empresas
- `data/` - Archivos de configuración (empresas, productos)
- `utils/` - Utilidades para PDF y cotizaciones
- `app.py` - Aplicación principal de Streamlit

## Configuración

1. Coloca tus membretes en PNG en la carpeta `membretes/` con nombres: membrete_1.png, membrete_2.png, etc.
2. Coloca los logos de tus empresas en la carpeta `logos/`
3. Edita `data/config.json` para configurar tus empresas y catálogo de productos
