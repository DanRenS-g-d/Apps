from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from openpyxl import Workbook
import time
import re

# Lista completa de URLs (se mantienen todas las originales)
urls = [
    "https://www.olimpica.com/supermercado/desayuno/alimento-para-perro?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/arepas?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/aves?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/bajo-en-azucar?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/bebidas-achocolatadas?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/bebidas-calientes?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/cafes?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/carnes-frias?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/cereales?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/chocolates-de-mesa?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/comidas-especiales?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/confiteria?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/cuidado-de-la-piel?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/cuidado-de-superficies?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/endulzantes?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/galletas?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/harinas?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/helados-y-paletas?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/huevos?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3&page=2",
    "https://www.olimpica.com/supermercado/desayuno/jugos?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/lacteos-y-derivados-refrigerados?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/mantequilla-y-margarina?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/mermeladas-y-untables?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/modificadores-de-leche?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/pan-empacado?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/panaderia-empacada?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/pancakes?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/pastas-alimenticias?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/refrescos-en-polvo?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3",
    "https://www.olimpica.com/supermercado/desayuno/salsas-aderezos-condimentos?initialMap=c,c&initialQuery=supermercado/desayuno&map=category-1,category-2,category-3"
]

# Configuración mejorada del navegador
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(options=options)

wb = Workbook()
del wb['Sheet']

def extract_product_name(element):
    """Extrae el nombre del producto usando todos los métodos posibles"""
    name_selectors = [
        (By.CSS_SELECTOR, ".vtex-product-summary-2-x-productBrand"),  # Selector principal
        (By.CSS_SELECTOR, ".vtex-store-components-3-x-productBrand"),  # Alternativo 1
        (By.CSS_SELECTOR, ".product-name"),                           # Alternativo 2
        (By.CSS_SELECTOR, ".product-title"),                          # Alternativo 3
        (By.CSS_SELECTOR, ".name"),                                   # Alternativo 4
        (By.XPATH, ".//span[contains(@class, 'product-name')]"),      # XPATH alternativo
        (By.XPATH, ".//h3[contains(@class, 'product-title')]"),       # XPATH alternativo 2
        (By.XPATH, ".//*[@itemprop='name']")                          # Por itemprop
    ]
    
    for by, selector in name_selectors:
        try:
            name_element = element.find_element(by, selector)
            return name_element.text.strip()
        except:
            continue
    
    # Últimos intentos con JavaScript
    js_attempts = [
        "return arguments[0].querySelector('[class*=\"name\"]')?.innerText",
        "return arguments[0].querySelector('[class*=\"title\"]')?.innerText",
        "return arguments[0].querySelector('h1, h2, h3, h4')?.innerText"
    ]
    
    for attempt in js_attempts:
        try:
            name = driver.execute_script(attempt, element)
            if name and name.strip():
                return name.strip()
        except:
            continue
    
    return "Nombre no disponible"

def extract_product_price(element):
    """Extrae el precio del producto usando todos los métodos posibles"""
    price_selectors = [
        # Selectores CSS
        (By.CSS_SELECTOR, ".vtex-product-price-1-x-sellingPriceValue"),
        (By.CSS_SELECTOR, ".vtex-product-price-1-x-sellingPrice"),
        (By.CSS_SELECTOR, ".vtex-product-price-1-x-currencyContainer"),
        (By.CSS_SELECTOR, ".price"),
        (By.CSS_SELECTOR, ".product-price"),
        (By.CSS_SELECTOR, ".item-price"),
        (By.CSS_SELECTOR, ".sales-price"),
        (By.CSS_SELECTOR, ".final-price"),
        
        # Selectores XPATH
        (By.XPATH, ".//*[contains(@class, 'price')]"),
        (By.XPATH, ".//*[contains(@class, 'currency')]"),
        (By.XPATH, ".//*[@itemprop='price']"),
        (By.XPATH, ".//span[contains(text(), '$')]"),
        (By.XPATH, ".//div[contains(@class, 'vtex-product-price-1-x-sellingPrice')]"),
        (By.XPATH, ".//div[contains(@class, 'price-container')]"),
        (By.XPATH, ".//span[contains(@class, 'amount')]")
    ]
    
    for by, selector in price_selectors:
        try:
            price_element = element.find_element(by, selector)
            price_text = price_element.text.strip()
            if price_text:
                return price_text
        except:
            continue
    
    # Intentos con JavaScript
    js_attempts = [
        "return arguments[0].querySelector('[class*=\"price\"]')?.innerText",
        "return arguments[0].querySelector('[class*=\"currency\"]')?.innerText",
        """
        const el = arguments[0];
        const priceEl = el.querySelector('[itemprop="price"]') || 
                       el.querySelector('[class*="price"]') || 
                       el.querySelector('span:contains("$")');
        return priceEl?.innerText || 'N/A';
        """,
        """
        const el = arguments[0];
        const priceText = el.innerText.match(/(\\$\\s*\\d{1,3}(?:\\.\\d{3})*(?:,\\d{2})?)/)?.[0];
        return priceText || 'N/A';
        """
    ]
    
    for attempt in js_attempts:
        try:
            price = driver.execute_script(attempt, element)
            if price and price != "N/A":
                return price
        except:
            continue
    
    return "Precio no disponible"

for url in urls:
    print(f"\n✅ Procesando URL: {url}")
    
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".vtex-product-summary-2-x-container, .product, .item"))
        )
    except Exception as e:
        print(f"⚠️ Error al cargar la página: {e}")
        continue

    # Scroll mejorado
    print("🔄 Realizando scroll para cargar productos...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    data = []
    try:
        # Múltiples selectores para encontrar contenedores de productos
        product_containers = driver.find_elements(By.CSS_SELECTOR, ".vtex-product-summary-2-x-container, .product, .item, .product-item, .product-wrapper")
        print(f"🔍 Encontrados {len(product_containers)} productos")
        
        for container in product_containers:
            try:
                nombre = extract_product_name(container)
                precio = extract_product_price(container)
                
                if nombre and nombre != "Nombre no disponible":
                    data.append((nombre, precio))
                    print(f"  ✅ {nombre} - {precio}")
                else:
                    print("  ⚠️ Producto sin nombre válido, ignorado")
                    
            except Exception as e:
                print(f"  ⚠️ Error procesando producto: {e}")
                continue
                
    except Exception as e:
        print(f"⚠️ Error al encontrar productos: {e}")

    # Crear hoja Excel con nombre seguro
    sheet_name = re.search(r"desayuno/([^?]+)", url)
    sheet_name = sheet_name.group(1) if sheet_name else f"Hoja{urls.index(url)+1}"
    sheet_name = re.sub(r'[\\/*?:[\]]', '', sheet_name)[:31]
    
    try:
        ws = wb.create_sheet(title=sheet_name)
        ws.append(["Nombre", "Precio"])
        for nombre, precio in data:
            ws.append([nombre, precio])
        print(f"📊 Total productos guardados: {len(data)}")
    except Exception as e:
        print(f"⚠️ Error creando hoja Excel: {e}")

driver.quit()
wb.save("productos_olimpica_desayuno_completo.xlsx")
print("\n✅ Extracción completada. Archivo guardado como 'productos_olimpica_desayuno_completo.xlsx'")
