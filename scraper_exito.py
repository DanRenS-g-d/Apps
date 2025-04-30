from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import openpyxl

# Lista de URLs de ejemplo
urls = [
    "https://www.exito.com/mercado"
    
]

# Configurar opciones del navegador
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-infobars")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.page_load_strategy = "eager"

# Inicializar driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Funciones de extracción
def extract_product_name(element):
    try:
        name_element = element.find_element(By.CSS_SELECTOR, 'h3.styles_name__qQJiK')
        return name_element.text.strip()
    except:
        return "Nombre no disponible"

def extract_product_price(element):
    try:
        price_element = element.find_element(By.CSS_SELECTOR, 'p.ProductPrice_container__price__XmMWA')
        return price_element.text.strip()
    except:
        return "Precio no disponible"

# Función para intentar presionar el botón "Siguiente"
def click_next_button():
    try:
        # Esperar a que el botón "Siguiente" esté presente y visible
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.Pagination_nextPreviousLink__f7_2J[aria-label="Próxima Pagina"]'))
        )
    except:
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-fs-pagination-seguiente="true"]'))
            )
        except:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Siguiente')]"))
                )
            except:
                print("🚫 No se encontró el botón 'Siguiente'.")
                return False

    # Intentar hacer clic en el botón
    try:
        # Desplazar el botón a una posición visible
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)

        # Verificar si el botón está bloqueado por otro elemento
        overlapping_element = driver.execute_script("""
            var elem = arguments[0];
            var rect = elem.getBoundingClientRect();
            return document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
        """, next_button)

        if overlapping_element != next_button:
            print(f"⚠️ El botón está bloqueado por: {overlapping_element.tag_name}. Intentando forzar el clic...")

        # Forzar el clic con JavaScript
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(3)  # Esperar a que la nueva página cargue
        return True
    except Exception as e:
        print(f"⚠️ Error al hacer clic en el botón 'Siguiente': {e}")
        return False

# Crear libro de Excel
workbook = openpyxl.Workbook()
hojas_creadas = False  # Bandera para saber si se creó al menos una hoja

for url in urls:
    print(f"\n✅ Procesando URL: {url}")
    driver.get(url)
    time.sleep(5)

    pagina = 1
    while True:
        print(f"🔄 Escaneando productos en la página {pagina}...")

        # Scroll
        SCROLL_PAUSE_TIME = 2
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        try:
            product_elements = driver.find_elements(By.CSS_SELECTOR, 'div.productCard_productInfo__yn2lK')
        except Exception as e:
            print(f"⚠️ Error al buscar productos: {e}")
            break

        if not product_elements:
            print("⚠️ No se encontraron productos en esta página.")
            break

        hoja_nombre = url.split("/")[-1][:31]
        hoja = workbook.create_sheet(title=hoja_nombre) if not hojas_creadas else workbook[hoja_nombre]
        if not hojas_creadas:
            hoja.append(["Nombre", "Precio"])
            hojas_creadas = True

        for product in product_elements:
            nombre = extract_product_name(product)
            precio = extract_product_price(product)
            hoja.append([nombre, precio])

        # Intentar presionar el botón "Siguiente"
        if not click_next_button():
            print("🚫 No se encontró el botón 'Siguiente'. Finalizando paginación.")
            break

        pagina += 1

# Si no se creó ninguna hoja útil, dejar la hoja por defecto con un mensaje
if not hojas_creadas:
    hoja = workbook.active
    hoja.title = "Sin datos"
    hoja.append(["No se encontraron productos en ninguna URL."])
else:
    # Eliminar hoja por defecto solo si ya se crearon otras
    default_sheet = workbook["Sheet"]
    workbook.remove(default_sheet)

# Guardar archivo
nombre_archivo = "productos_exito.xlsx"
workbook.save(nombre_archivo)
print(f"\n✅ Archivo guardado como: {nombre_archivo}")

driver.quit()