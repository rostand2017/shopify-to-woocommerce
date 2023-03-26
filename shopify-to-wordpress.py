import json
import csv
import os

header = [
    'ID','Type','SKU','Name','Published','Is featured?','Visibility in catalog','Short description','Description',
    'Date sale price starts','Date sale price ends','Tax status','Tax class','In stock?','Stock','Low stock amount',
    'Backorders allowed?','Sold individually?','Weight (unit)','Length (unit)','Width (unit)','Height (unit)',
    'Allow customer reviews?','Purchase Note','Sale price','Regular price','Categories','Tags','Shipping class',
    'Images','Download limit','Download expiry days','Parent','Grouped products','Upsells','Cross-sells','External URL',
    'Button text','Position',
    'Attribute 1 name','Attribute 1 value(s)','Attribute 1 visible','Attribute 1 global','Attribute 1 default',
    'Attribute 2 name','Attribute 2 value(s)','Attribute 2 visible','Attribute 2 global','Attribute 2 default',
    'Attribute 3 name','Attribute 3 value(s)','Attribute 3 visible','Attribute 3 global','Attribute 3 default',
]

def get_option_value(option_value, option_number, index = -1):
    if index == 0:
        return option_value.replace(" ", "").replace("/", ", ")
    options = option_value.replace(" ", "").split("/")
    return options[option_number - 1] if len(options) >= option_number else ""

def get_option_name(options, option_number):
    for (index, option) in enumerate(options):
        if index == option_number - 1:
            return option["name"]
    return ""

def get_variant_image(images, variant_id):
    for image in images:
        for _variant_id in image["variant_ids"]:
            if _variant_id == variant_id:
                return image
    return None

def get_product_type(index):
    return "variation" if index >= 1 else "variable"

def get_product_tva(index):
    return "parent" if index >= 1 else ""

def get_product_parent(index, parent_id):
    return "id:"+str(parent_id) if index >= 1 else ""

def get_product_title(top_product, product, index):
    if index == 0:
        return top_product["title"]
    return top_product["title"] + " - " + product["title"].strip().replace("/", ",")

def get_option_visibility(index):
    return "" if index >= 1 else 1

def get_default_option(index, option_value):
    if index >= 1:
        return ""
    options = option_value.split(",")
    if len(options) == 1:
        return options[0].strip()
    elif len(options) == 2:
        return options[1].strip()
    else:
        return options[2].strip()

def get_option_val(option_value, options, index, option_number):
    if index == 0:
        if(len(options) > option_number - 1):
            result = ''.join( val + "," for val in options[option_number - 1]["values"])
            return result[:-1].replace(",", ", ")
        else:
            return ""
    else:
        options = option_value.strip().split("/")
        return options[option_number - 1].strip() if len(options) >= option_number else ""
    
def get_parsed_description(description):
    return description.replace("\r", "\\r").replace("\n", "\\n")

def create_data_folder(fileName):
    if not os.path.exists(fileName):
        os.makedirs(fileName)

def add_new_row(writer, top_product, product, index, parent_id, start_id):
    option_name_1 = get_option_name(top_product["options"], 1)
    option_name_2 = get_option_name(top_product["options"], 2)
    option_name_3 = get_option_name(top_product["options"], 3)

    option_value_1 = get_option_val(product["title"], top_product["options"], index, 1)
    option_value_2 = get_option_val(product["title"], top_product["options"], index, 2)
    option_value_3 = get_option_val(product["title"], top_product["options"], index, 3)

    image = get_variant_image(top_product["images"], product["id"])
    image_src = image["src"] if image else ""
    image_position = image["position"] if image else ""

    product_type = get_product_type(index)
    tva_class = get_product_tva(index)
    parent = get_product_parent(index, parent_id)
    product_title = get_product_title(top_product, product, index)
    product_weight = product.get("weight")
    product_sku = str(start_id) + "-" + product["sku"] if index != 0 else ""
    product_description = get_parsed_description(top_product["body_html"])
    
    product_position = index + 1
    option_visibiliy_1 = get_option_visibility(index)
    option_visibiliy_2 = get_option_visibility(index)
    option_visibiliy_3 = get_option_visibility(index)

    option_default_1 = get_default_option(index, option_value_1)
    option_default_2 = get_default_option(index, option_value_2)
    option_default_3 = get_default_option(index, option_value_3)

    writer.writerow([
        start_id, product_type, product_sku, product_title, 1, 0, "visible", "",
        product_description, "", "", "taxable", tva_class, 1, 100, 5, 0, 0, product_weight, "",
        "", "", 1, "", product["price"], product["price"], top_product["product_type"],
        "", "", image_src, "", "", parent, "", "", "", "", "", product_position,
        option_name_1, option_value_1, option_visibiliy_1, 1, option_default_1,
        option_name_2, option_value_2, option_visibiliy_2, 1, option_default_2,
        option_name_3, option_value_3, option_visibiliy_3, 1, option_default_3,
    ])

def json_to_wordpress_csv(fileName, start_id = 0, products_per_file = 10):
    create_data_folder("data")
    with open(fileName + str(".json")) as product_file:
        products = json.load(product_file)
        products_len = len(products["products"])
        file_nb = products_len // products_per_file
        if products_len % products_per_file > 0:
            file_nb += 1
        from_index = 0
        for file_index in range(1, file_nb + 1):
            with open("data/" + fileName + "-" + str(file_index) + str(".csv"), "w", encoding='utf-8', newline='') as wordpress_product_file:
                writer = csv.writer(wordpress_product_file, delimiter=",", quoting = csv.QUOTE_NONNUMERIC)
                writer.writerow(header)
                for top_product_index in range(from_index, from_index + products_per_file):
                    if(top_product_index >= products_len):
                        break
                    top_product = products["products"][top_product_index]
                    parent_id = start_id
                    is_option_name = True

                    # insert the parent product
                    if len(top_product["variants"]) >= 1 :
                        product = top_product["variants"][0]
                        add_new_row(writer, top_product, product, 0, parent_id, start_id)
                        parent_id = start_id
                        start_id += 1
                    
                    # insert the child product
                    for (index, product) in enumerate(top_product["variants"]):
                        add_new_row(writer, top_product, product, index + 1, parent_id, start_id)
                        is_option_name = False
                        start_id += 1
                from_index += products_per_file


json_to_wordpress_csv("shopify-products", 145, 40)