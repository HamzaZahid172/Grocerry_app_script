import warnings
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
from selenium.common.exceptions import NoSuchElementException 
import re
import urllib.request
import json


chromedriver_path = r'/home/hamza/Desktop/Selenium_project/chromedriver_linux64/chromedriver'
warnings.filterwarnings("ignore")
options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
wait = WebDriverWait(driver, 10)
driver.get('https://grocerapp.pk/sitemap')

def check_exists_by_css(driver,css_selector):
    try:
        output = driver.find_element_by_css_selector(css_selector)
        return output.text
    except NoSuchElementException:
        return " "

def check_exists_by_css_click(driver,css_selector):
    try:
        output = driver.find_element_by_css_selector(css_selector)
        return output
    except NoSuchElementException:
        return "0"
def check_exists_by_css_selector(driver,css_selector):
    try:
        output = driver.find_element_by_css_selector(css_selector)
        return css_selector
    except NoSuchElementException:
        return "0"

time.sleep(25)
button = check_exists_by_css_click(driver,'button[class="No thanks"]')
if button != '0':
    button.click()
time.sleep(5)
soup = BeautifulSoup(driver.page_source, 'html.parser')

#Get all Catgory url
all_category = []
for category_part in soup.select('a[class*="jss325 jss354 jss360 jss569 jss571"]'):
    if(category_part['href'].find('cid') != -1):
        all_category.append('https://grocerapp.pk'+category_part['href'])
driver.close()
all_category = list(set(all_category))
print(all_category)

#Get all Product_url
all_product = []
store = {}
for cat_url in all_category:
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    print(cat_url)
    driver.get(cat_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(25)
    button = check_exists_by_css_click(driver,'button[class="No thanks"]')
    if button != '0':
        button.click()
    time.sleep(5)
    if(check_exists_by_css(driver,'main>div>div:nth-child(2)>div>p').find("Couldn't") != -1):
        print('Product is not exist')
    else:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_exist = check_exists_by_css_selector(driver,'main>div>div:nth-child(2)>div>div>div>div:nth-child(2)>div>a')
        selector = ""
        if product_exist != "0" :
            selector = product_exist
        else:
            selector = check_exists_by_css_selector(driver,'main>div>div:nth-child(3)>div>div:nth-child(2)>div>a')
            if selector != "0" :
                selector = selector
            else:
                selector = check_exists_by_css_selector(driver,'main>div>div:nth-child(3)>div>div>div>div:nth-child(2)>div>a')


        for product_part in soup.select(selector):
            all_product.append("https://grocerapp.pk"+product_part['href'])
            print("https://grocerapp.pk"+product_part['href'])
        print(all_product)
    driver.close()
store['product_url'] = all_product
Data = pd.DataFrame(store)
Data.to_excel('Product_url.xlsx' ,index=None)
#extraction
product_name = []
actual_price = []
promotional_price = []
quantity = []
image_url = []
product_id =[]
product_detail = []
product_url = []
category = []
brand = []
sku = []
currency = []
offer = []

for pro_url in all_product:
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    print(pro_url)
    driver.get(pro_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(25)
    button = check_exists_by_css_click(driver,'button[class="No thanks"]')
    if button != '0':
        button.click()
    time.sleep(5)
    if(check_exists_by_css(driver,'main>div>div:nth-child(2)>div>p').find("Couldn't") != -1 or check_exists_by_css(driver,'main>div:nth-child(2)>div h3').find("Oops!") != -1):
        print('Product is not exist')
    else:
        output_json = driver.find_element_by_css_selector('head> script[type="application/ld+json"]')
        text = output_json.get_attribute('innerHTML')
        df = json.loads(text)
        product_name.append(df['name'])
        product_id.append(df['productID'])
        product_url.append(df['url'])
        category.append(df['category'])
        brand.append(df['brand'])
        sku.append(df['sku'])
        currency.append(df['offers'][0]['priceCurrency'])
        offer.append(check_exists_by_css(driver,'main>div>div:nth-child(3)>div>div:nth-child(1)'))
        
        actual_price.append(check_exists_by_css(driver,'main>div>div:nth-child(3)>div>div:nth-child(2)>div:nth-child(2)>div:nth-child(2)>div span'))
        promotional_price.append(check_exists_by_css(driver,'main>div>div:nth-child(3)>div>div:nth-child(2)>div:nth-child(2)>div:nth-child(2)>div p'))
        quantity.append(df['offers'][0]['eligibleQuantity'])
        product_detail.append(df['description'])
        image_url.append(df['image'])
    # img[class="jss323 jss324 jss825 jss819 lazyloaded"]
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # for img in soup.select('div[data-index="0"] img'):
    #     image.append(urllib.request.urlretrieve(img['src'], "product_imag.jpg"))
    driver.close()
    
complete_data = {}
complete_data['url'] = product_url
complete_data['product_name'] = product_name
complete_data['product_id'] = product_id
complete_data['sku'] = sku
complete_data['category'] = category
complete_data['brand'] = brand
complete_data['actual_price'] = actual_price
complete_data['promotional_price'] = promotional_price
complete_data['currency'] = currency
complete_data['quantity'] = quantity 
complete_data['product_detail'] = product_detail
complete_data['image_url'] = image_url
complete_data['offer'] = offer

Data = pd.DataFrame(complete_data)
Data.to_excel('Final_Output.xlsx' ,index=None)
print("Complete Now Thanks You")
