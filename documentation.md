# Proyecto Job Scraping

## Introducción
Este proyecto es una aplicación en Python que automatiza la extracción de ofertas de empleo desde distintos portales (LinkedIn, Indeed e Internshala) y permite guardar los resultados en un archivo Excel. Incluye una interfaz gráfica sencilla basada en Tkinter para introducir los criterios de búsqueda y coordinar el proceso de scraping.

## Tecnologías
- **Python 3**
- **Selenium** para la automatización del navegador.
- **BeautifulSoup** para el parseo de HTML.
- **pandas** y **openpyxl** para la generación de ficheros Excel.
- **Tkinter** para la interfaz gráfica.

La arquitectura sigue un esquema modular sencillo donde cada responsabilidad se encuentra en un archivo independiente.

## Estructura de archivos

```
job_scraper_project/
├── main.py
├── gui.py
├── scraper.py
├── excel_handler.py
├── requirements.txt
```

- **`main.py`**: punto de entrada de la aplicación. Inicializa el WebDriver y lanza la ventana de Tkinter (`JobScraperApp`).
- **`gui.py`**: define la clase `JobScraperApp` que gestiona la interfaz gráfica y orquesta las tareas de scraping en un hilo independiente.
- **`scraper.py`**: contiene todas las funciones de scraping específicas para cada sitio web. Implementa la inicialización del WebDriver y la lógica para LinkedIn Jobs, Indeed, Internshala y publicaciones de LinkedIn.
- **`excel_handler.py`**: utilitario para convertir la lista de resultados en un `DataFrame` y exportarlo a un archivo `.xlsx`.
- **`requirements.txt`**: dependencias del proyecto.
- **`ai_utils.py`**: funciones opcionales que usan la API de OpenAI para
  interpretar texto libre, clasificar y traducir datos extraídos.

## Diagrama de interconexión

```
[main.py] ----> [gui.JobScraperApp]
                    |
                    v
             [scraper.py] <-----> [excel_handler.py]
```
`main.py` crea el WebDriver y la GUI. La GUI llama a las funciones de `scraper.py` para obtener los datos y luego utiliza `excel_handler.py` para guardarlos en Excel.

## Integración con OpenAI

El módulo `ai_utils.py` permite usar la API de ChatGPT para analizar páginas con
estructura poco clara, identificar campos relevantes y traducir o normalizar los
resultados. Para activarlo es necesario instalar la dependencia `openai` y
configurar la variable de entorno `OPENAI_API_KEY`. Si no se provee esta clave,
la aplicación seguirá funcionando pero sin las capacidades de IA.
