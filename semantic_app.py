import streamlit as st
import subprocess
import datetime
import os
import pandas as pd

st.set_page_config(page_title="Buscador Semántico", layout="centered")

st.title("🛒 Buscador Semántico de Productos de Supermercado")
st.write("Pega abajo la lista de productos. Se buscarán los más baratos según la base de datos actual.")

productos = st.text_area("📋 Lista de productos", height=400, placeholder="Ej: arroz, leche, pan integral...")

if st.button("🔍 Buscar productos más baratos"):
    if not productos.strip():
        st.warning("⚠️ Debes ingresar al menos un producto.")
    else:
        # Guardar la lista en productos.txt
        with open("productos.txt", "w", encoding="utf-8") as f:
            f.write(productos.strip())

        with st.spinner("🔎 Ejecutando scrapers y análisis..."):
            try:
                # Ejecutar scrapers y fusión
                subprocess.run(["python", "scraper_ara.py"], check=True)
                subprocess.run(["python", "scraper_d1.py"], check=True)
                subprocess.run(["python", "scraper_olimpica.py"], check=True)
                subprocess.run(["python", "scraper_exito.py"], check=True)
                subprocess.run(["python", "scraper_isimo.py"], check=True)
                subprocess.run(["python", "ExcelFuse.py"], check=True)

                # Ejecutar el buscador
                subprocess.run(["python", "busqueda_semantica.py"], check=True)

                # Buscar el archivo más reciente
                archivos = [f for f in os.listdir() if f.startswith("productos_mas_baratos_") and f.endswith(".xlsx")]
                if archivos:
                    archivo_final = max(archivos, key=os.path.getctime)

                    # Mostrar en pantalla
                    df = pd.read_excel(archivo_final)
                    st.success("✅ Búsqueda completada. Resultados abajo.")
                    st.dataframe(df)

                    # Opción de descarga
                    with open(archivo_final, "rb") as f:
                        st.download_button("⬇️ Descargar archivo Excel", f, file_name=archivo_final)
                else:
                    st.error("❌ No se encontró el archivo de resultados.")
            except subprocess.CalledProcessError:
                st.error("❌ Hubo un error ejecutando alguno de los scripts.")
