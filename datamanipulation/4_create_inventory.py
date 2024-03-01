import csv
import random

def add_sellers_to_products(sellers_file, products_file, output_file):
    with open(sellers_file, 'r', newline='') as sfile, \
         open(products_file, 'r', newline='') as pfile, \
         open(output_file, 'w', newline='') as outfile:

        seller_reader = csv.reader(sfile)
        product_reader = csv.reader(pfile)
        next(seller_reader) # Skip seller header
        next(product_reader) # Skip product header

        sellers = list(seller_reader)  # Read all sellers into memory
        inventory_header =  ['item_id', 'item_title', 'seller_name', 'seller_rating', 'item_price', 'item_condition']  # Add seller_name to product header
        writer = csv.writer(outfile)
        writer.writerow(inventory_header)

        for product_row in product_reader:
            num_repeats = random.randint(3, 6)  # Repeat 1-5 times
            for _ in range(num_repeats):
                seller = random.choice(sellers) 
                condition, price = add_price_and_condition(product_row) 
                writer.writerow([product_row[0]] + [product_row[1]]+ [seller[1]] + [seller[3]] + [str(price)] + [condition])

new_cost_multipliers = [-10, -5, 0, 5, 10, 15, 20, 30]
gan_cost_multipliers = [-30, -25, -15, -10, -5, 0, 10, 5]
used_cost_multipliers = [-50, -45, -40, -30, -10, 0, 5, -55]

def add_price_and_condition(product_row):
    if product_row[4] == "":
        product_row[4] = 10
    base_cost = float(product_row[4])
    condition = generate_product_condition()
    if condition == "new":
        cost_variation = new_cost_multipliers[random.randint(0, 7)]
    if condition == "good as new":
        cost_variation = gan_cost_multipliers[random.randint(0, 7)]
    if condition == "used":
        cost_variation = used_cost_multipliers[random.randint(0, 7)]
    new_cost = round(base_cost + (cost_variation* base_cost/100),2)
    final_cost = max(0.5, new_cost ) # Ensure cost remains in range
    return condition, final_cost

def generate_product_condition():
    conditions = ['new', 'good as new', 'used']  
    condition_probabilities = [0.5, 0.3, 0.2] 
    condition = random.choices(conditions, weights=condition_probabilities)[0] 
    return condition


if __name__ == "__main__":
    sellers_file = 'datamanipulation/data/sellers.csv'
    products_file = 'datamanipulation/data/3_enriched_catalog.csv'
    output_file = 'datamanipulation/data/4_inventory.csv'
    add_sellers_to_products(sellers_file, products_file, output_file)
