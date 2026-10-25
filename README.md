# INNOVA-VT — Prototipo web

Aplicación educativa Streamlit para formular proyectos, proponer ecuaciones de búsqueda, registrar fuentes verificadas y exportar matrices e informe Word.

## Instalación

1. Instalar Python 3.10 o superior.
2. En la carpeta del proyecto ejecutar:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abrirá la aplicación en el navegador (normalmente `http://localhost:8501`).

## Alcance y límites

- No requiere claves API ni conexión a servicios privados.
- No consulta automáticamente Scopus, Google Scholar ni bases de patentes; enlaza a plataformas para búsqueda manual.
- El diccionario bilingüe es inicial y debe ampliarse; las ecuaciones requieren validación en cada buscador.
- Permite ingresar o importar CSV y editar matrices de artículos y patentes.
- Exporta DOCX, XLSX y JSON; no almacena cuentas ni proyectos en un servidor.
- En la versión actual, el archivo JSON es una copia de seguridad, pero no existe una función para restaurarlo dentro de la interfaz.
- No incluye todavía integración con IA generativa, autenticación, validación automática de DOI o análisis bibliométrico.

## Uso docente

Pida a cada grupo que justifique las palabras clave, documente fecha y filtros de cada búsqueda, verifique las fuentes originales y redacte una síntesis crítica de las brechas tecnológicas. Las matrices vacías no equivalen a un estado del arte realizado.
