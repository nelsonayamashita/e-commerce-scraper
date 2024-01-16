import requests
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Constants
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'}


def submarino_scrape():
    submarino = "https://www.submarino.com.br/categoria/pet-shop/caes/alimentos/racao?limit=240&offset=0"
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    products = []

    # Here we're already querrying 240 itens
    driver.get(submarino)

    # Wait for the products to load
    element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class^='src__Wrapper-sc']"))
    WebDriverWait(driver, 10).until(element_present)

    # Find all elements in the page
    product_elements = driver.find_elements(By.CSS_SELECTOR, "h3[class^='product-name__Name']")
    price_elements = driver.find_elements(By.CSS_SELECTOR, "span[class*='price__PromotionalPrice']")

    for product, price in zip(product_elements, price_elements):
        products.append((product.text, price.text))

    driver.close()
    return products


def amazon_scrape():
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    products = []

    # Link for category "Ração para Cães"
    driver.get("https://www.amazon.com.br/s?rh=n%3A19654037011&fs=true&ref=lp_19654037011_sar")

    # Get the 10 first product pages
    for i in range(1, 11):
        product_elements = []
        price_elements = []
        
        print(f"Start scrapping page {i}")
        
        # Wait for the first product item to load
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='a-section a-spacing-small puis-padding-left-small puis-padding-right-small']"))
        WebDriverWait(driver, 10).until(element_present)
        
        # Find all products in the page
        product_elements = driver.find_elements(By.CSS_SELECTOR, "span[class='a-size-base-plus a-color-base a-text-normal']")
        price_elements = driver.find_elements(By.CSS_SELECTOR, "span[class='a-price']")
        
        for product, price in zip(product_elements, price_elements):
            products.append((product.text, price.text.replace('\n', '.')))
        
        # Find and click the next page button
        next_button = driver.find_element(By.CSS_SELECTOR, "a[class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[id='aod-background']")))
        next_button.click()
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='a-section a-spacing-small puis-padding-left-small puis-padding-right-small']"))

    driver.close()
    return products


def petlove_scrape():
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    # We'll loop trough the pages since the buttons didn't work well with selenium
    products = []

    for page in range(1, 11):
        print(f"Start scrapping page {page}")
        
        petlove = f"https://www.petlove.com.br/cachorro/racoes?page={page}"
        driver.get(petlove)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "ul[class=catalog-items]")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        product_list = soup.select("li[class=catalog-item]")

        for prod in product_list:
            name = prod.select_one("h2[class='product-name card-list-name']")
            price = prod.select_one("span[class='catalog-card-prices__price-per']")
            if price:
                products.append((name.text, price.text))
            else:
                products.append((name.text, "N/A"))
                
    driver.close()
    return products


def petz_scrape():
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    products = []

    # Get scroll height
    driver.get("https://www.petz.com.br/cachorro/racao")
    last_height = driver.execute_script("return document.body.scrollHeight")

    num_elements = 0
    new_height = 0
    while num_elements < 400:
        # Scroll down to bottom
        driver.execute_script(f"window.scrollTo({new_height}, document.body.scrollHeight);")

        # Wait to load page
        WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "section[id='listProductsShowcase']")))

        # Calculate new scroll height and compare with last scroll height
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_list = soup.select("div[class='ptz-card ptz-card-outlined ptz-card-product ptz-card-product-vertical ptz-card-product-vertical-lg']")
        new_height = driver.execute_script("return document.body.scrollHeight")
        num_elements = len(product_list)

        print(f"Current Scrapping {num_elements} elements")

    for prod in product_list:
        name = prod.select_one("p[class='ptz-card-label-left']")
        price = prod.select_one("p[class='ptz-card-price']")
        # Remove non-breaking space in Latin1 and children
        if price:
            price_clean = ' '.join([str(item) for item in price if item.name != 'span']).replace(u'\xa0', u' ')
            products.append((name.text, price_clean))
        else:
            products.append((name.text, "N/A"))

    driver.close()
    return products
