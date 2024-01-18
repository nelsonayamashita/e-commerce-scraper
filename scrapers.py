from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def submarino_scrape(num_pages=13):
    '''
    Returns a tuple with name, currnet price, old price and number of ratings
    from Submarino e e-commerce.

        Parameters:
            num_pages (int): number of pages to be scraped.
        
        Returns:
            products (tuple): tuple with name, price, old price and number of ratings
            of all products found. 
    '''
    # Each page has 24 elements, we'll query all of them at once
    submarino = f"https://www.submarino.com.br/categoria/pet-shop/caes/alimentos/racao?limit={num_pages * 24}&offset=0"
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    products = []

    # Here we're already querrying all itens
    driver.get(submarino)

    # Wait for the products to load
    element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class^='src__Wrapper-sc']"))
    WebDriverWait(driver, 10).until(element_present)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    product_list = soup.select("a[class^='inStockCard__Link-sc']")
    
    pages = 0
    for (i, product) in enumerate(product_list):
        if i % 24 == 0:
            pages += 1
            print(f"Start scrapping page {pages}")

        name = product.select_one("h3[class^='product-name__Name']").text

        # It's possible that the product is out of stock or without any promotions
        # or without ratings
        price = product.select_one("span[class*='price__PromotionalPrice']")
        price = price.text if price else "NA"

        original_price = product.select_one("span[class*='price__Price-sc']")
        original_price = original_price.text if original_price else price # if there is no original price, current price is the original

        rating = product.select_one("span[class^='src__Count-sc']")
        rating = rating.text[:-11] if rating else "NA" # -11 to remove "avaliações"
        
        products.append((name, price, original_price, rating))

    driver.close()
    return products


def amazon_scrape(num_pages=10):
    '''
    Returns a tuple with name, currnet price, old price and number of ratings
    from Amazon e e-commerce.

        Parameters:
            num_pages (int): number of pages to be scraped.
        
        Returns:
            products (tuple): tuple with name, price, old price and number of ratings
            of all products found. 
    '''
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    products = []

    # Link for category "Ração para Cães"
    driver.get("https://www.amazon.com.br/s?rh=n%3A19654037011&fs=true&ref=lp_19654037011_sar")

    # Get the 10 first product pages
    for i in range(1, num_pages+1):
        product_elements = []
        price_elements = []
        
        print(f"Start scrapping page {i}")
        
        # Wait for the first product item to load
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='a-section a-spacing-small puis-padding-left-small puis-padding-right-small']"))
        WebDriverWait(driver, 10).until(element_present)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        product_list = soup.select("div[class^='s-widget-container s-spacing-small s-widget-container-height-small celwidget slot=MAIN template=SEARCH_RESULTS widgetId=search-results']")
        
        for product in product_list:
            name = product.select_one("span[class='a-size-base-plus a-color-base a-text-normal']").text
            
            price = product.select_one("span[class='a-offscreen']")
            price = price.text.replace("\xa0", " ") if price else "NA"
            
            original_price = product.select_one("span[data-a-strike='true']>span[aria-hidden='true']")
            original_price = original_price.text if original_price else price # if there is no original price, current price is the original
            
            rating = product.select_one("a[class='a-link-normal s-underline-text s-underline-link-text s-link-style']>span[class='a-size-base s-underline-text']")
            rating = rating.text.replace('.', '') if rating else "NA" # need to remove mile separator
            
            products.append((name, price, original_price, rating))
            
        
        # Find and click the next page button
        button_present = EC.visibility_of_element_located((By.CSS_SELECTOR, "a[class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']"))
        WebDriverWait(driver, 10).until(button_present)
        
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[id='aod-background']")))
        next_button = driver.find_element(By.CSS_SELECTOR, "a[class='s-pagination-item s-pagination-next s-pagination-button s-pagination-separator']")
        next_button.click()
        
    driver.close()
    return products


def petlove_scrape(num_pages=10):
    '''
    Returns a tuple with name, currnet price, old price and number of ratings
    from Petlove e e-commerce.

        Parameters:
            num_pages (int): number of pages to be scraped.
        
        Returns:
            products (tuple): tuple with name, price, old price and number of ratings
            of all products found. 
    '''
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    # We'll loop trough the pages since the buttons didn't work well with selenium
    products = []

    for page in range(1, num_pages+1):
        print(f"Start scrapping page {page}")
        
        petlove = f"https://www.petlove.com.br/cachorro/racoes?page={page}"
        driver.get(petlove)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "ul[class=catalog-items]")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        product_list = soup.select("li[class=catalog-item]")

        for prod in product_list:
            name = prod.select_one("h2[class='product-name card-list-name']").text

            price = prod.select_one("span[class='catalog-card-prices__price-per']")
            price = price.text if price else "NA"

            old_price = prod.select_one("s[class='catalog-card-prices__price-of']")
            old_price = old_price.text if old_price else price
            
            ratings = "NA" # can't get ratings in this site
            
            products.append((name, price, old_price, ratings))
                
    driver.close()
    return products


def petz_scrape(max_elements=400):
    '''
    Returns a tuple with name, currnet price, old price and number of ratings
    from Petz e e-commerce.

        Parameters:
            num_pages (int): number of elements to be scraped.
        
        Returns:
            products (tuple): tuple with name, price, old price and number of ratings
            of all products found. 
    '''
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    products = []

    # Get scroll height
    driver.get("https://www.petz.com.br/cachorro/racao")
    last_height = driver.execute_script("return document.body.scrollHeight")

    num_elements = 0
    new_height = 0
    while num_elements < max_elements:
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
        name = prod.select_one("p[class='ptz-card-label-left']").text
        price = prod.select_one("p[class='ptz-card-price']")
        
        # Remove non-breaking space in Latin1 and children
        price = ' '.join([str(item) for item in price if item.name != 'span']).replace('\xa0', ' ') if price else "NA"
        
        old_price = prod.select_one("span[class='ptz-card-price-older']")
        old_price = old_price.text.replace('\xa0', " ") if ((old_price) and len(old_price.text)) else price
        
        rating = "NA" # can't acces rating in this site
        
        products.append((name, price, old_price, rating))


    driver.close()
    return products


def magalu_scrape(num_pages=5):
    '''
    Returns a tuple with name, currnet price, old price and number of ratings
    from Magazine Luiza e e-commerce.

        Parameters:
            num_pages (int): number of pages to be scraped.
        
        Returns:
            products (tuple): tuple with name, price, old price and number of ratings
            of all products found. 
    '''
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)
    
    products = []
    
    for page in range(1, num_pages+1):
        driver.get(f"https://www.magazineluiza.com.br/racao-seca-para-cachorro/pet-shop/s/pe/prac/?page={page}")
        print(f"Start scrapping page {page}")

        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a[data-testid='product-card-container']")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        product_list = soup.select("a[data-testid='product-card-container']")
        
        for product in product_list:
            name = product.select_one("h2[data-testid='product-title']").text

            price = product.select_one("p[data-testid='price-value']")
            price = price.text.replace("\xa0", " ").replace(".", "") if price else "NA"

            original_price = product.select_one("p[data-testid='price-original']")
            original_price = original_price.text.replace("\xa0", " ").replace(".", "") if original_price else price # if there is no original price, current price is the original

            rating = product.select_one("div[data-testid='review']>span[format='count']")
            rating = rating.text if rating else "NA"

            products.append((name, price, original_price, rating))
    
    driver.close()
    return products


def meli_scrape(num_pages=10):
    '''
    Returns a tuple with name, currnet price, old price and number of ratings
    from Mercado Livre e-commerce.

        Parameters:
            num_pages (int): number of pages to be scraped.
        
        Returns:
            products (tuple): tuple with name, price, old price and number of ratings
            of all products found. 
    '''
    
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    products = []

    for page in range(1, num_pages + 1):
        # The site shows ~48 itens per page and uses the url to control that
        driver.get(f"https://lista.mercadolivre.com.br/animais/cachorros/alimento-petisco-suplemento/racao-cachorros/ração_Desde_{1+page*48}_NoIndex_True")
        print(f"Start scrapping page {page}")

        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='ui-search-result__wrapper']")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        product_list = soup.select("div[class='ui-search-result__wrapper']")
        
        for product in product_list:
            name = product.select_one("a[class='ui-search-item__group__element ui-search-link__title-card ui-search-link']").text

            price = product.select_one("span[aria-roledescription='Preço']")
            price = price.text.replace(".", "") if price else "NA"

            original_price = product.select_one("s[aria-roledescription='Preço']")
            original_price = original_price.text.replace(".", "") if original_price else price # if there is no original price, current price is the original

            rating = product.select_one("span[class='ui-search-reviews__amount']")
            rating = rating.text.strip("()") if rating else "NA" # removes parentheses from begining and ending eg: (445) -> 445

            products.append((name, price, original_price, rating))
    
    driver.close()
    return products