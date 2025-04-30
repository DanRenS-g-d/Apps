# 🛒 Buscador Semántico de Supermercado

Este proyecto es una app construida con **Streamlit** que permite buscar los productos más baratos en supermercados colombianos usando **búsqueda semántica con inteligencia artificial**.

## 🚀 ¿Qué hace?

- Ejecuta scrapers para Ara, Olímpica, D1, Éxito e Ísimo
- Fusiona los datos automáticamente
- Permite ingresar una lista de productos (como "leche", "arroz", etc.)
- Encuentra los productos más baratos según similitud semántica
- Descarga los resultados como archivo Excel

## 🧠 Tecnologías usadas

- Python
- Streamlit
- SentenceTransformers (para embeddings semánticos)
- Ollama (opcional)
- Pandas
- Selenium (en scrapers)

## ▶️ Cómo usar

1. Clona el repositorio
2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la app:

```bash
streamlit run semantic_app.py
```

## 📁 Estructura

```
semantic_app.py              → Interfaz de usuario
busqueda_semantica.py        → Motor de búsqueda
ExcelFuse.py                 → Fusiona datos de supermercados
scraper_*.py                 → Scrapers individuales
requirements.txt             → Dependencias
```

## 📌 Notas

- Los datos se generan automáticamente.
- El archivo `unified_supermarket_data.xlsx` no se incluye en el repo, se crea al ejecutar la app.