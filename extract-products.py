import json
import requests
import time

products_url = "https://your-shopify.com/products.json?page="
page = 1
product_len = 30
products = []

while product_len >= 30:
    response = requests.get(products_url + str(page))
    if response.status_code == 200:
        response_products = response.json()["products"]
        products = products + (response_products)
        product_len = len(response_products)
        print("Good " + str(page))
    else: 
        print("============= Error at page " + str(page))
    page += 1
    time.sleep(1)

with open('shopify-products.json', 'w') as f:
    json.dump({"products": products}, f)