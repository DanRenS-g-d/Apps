from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Configuración del navegador
options = Options()
options.add_argument("--headless=new")  # Ejecutar en modo sin interfaz gráfica
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")

# Ruta al chromedriver CORREGIDA
service = Service("C:\\Users\\User\\Desktop\\Tesis\\Scripts de Python Olimpica\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# URL de la página
url = "https://productosbajocosto.com/lista-precios-productos-tiendas-d1/"

# Función para extraer datos de la tabla
def extract_table_data():
    """Extrae los datos de la tabla actual"""
    data = []
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.tablepress"))
        )
        rows = driver.find_elements(By.CSS_SELECTOR, "table.tablepress tbody tr")
        for row in rows:
            try:
                columns = row.find_elements(By.TAG_NAME, "td")
                titulo = columns[0].text.strip() if len(columns) > 0 else "N/A"
                precio = columns[1].text.strip() if len(columns) > 1 else "N/A"
                subcategoria = columns[2].text.strip() if len(columns) > 2 else "N/A"
                categoria = columns[3].text.strip() if len(columns) > 3 else "N/A"
                data.append({
                    "Título": titulo,
                    "Precio": precio,
                    "Subcategoría": subcategoria,
                    "Categoría": categoria
                })
            except Exception as e:
                print(f"⚠️ Error al procesar una fila: {e}")
                continue
    except Exception as e:
        print(f"⚠️ Error al extraer datos de la tabla: {e}")
    return data

# Función para hacer clic en el botón "Siguiente"
def click_next_button():
    """Intenta hacer clic en el botón 'Siguiente'"""
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dt-paging-button.next"))
        )
        if "disabled" in next_button.get_attribute("class"):
            return False
        next_button.click()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"⚠️ Error al hacer clic en el botón 'Siguiente': {e}")
        return False

# Lista para almacenar todos los datos
all_data = []

try:
    driver.get(url)
    time.sleep(3)
    while True:
        print("🔄 Extrayendo datos de la tabla...")
        table_data = extract_table_data()
        all_data.extend(table_data)
        print(f"✅ Página procesada, productos extraídos: {len(table_data)}")
        if not click_next_button():
            print("🚫 No hay más páginas disponibles.")
            break
except Exception as e:
    print(f"⚠️ Error durante el scraping: {e}")
finally:
    driver.quit()

# Guardar los datos en un archivo Excel
df = pd.DataFrame(all_data)
df.to_excel("productos_d1_tabla.xlsx", index=False)
print("✅ Datos guardados en 'productos_d1_tabla.xlsx'")
