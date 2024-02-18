import csv
import random

def add_sellers_to_products(sellers_file, products_file, output_file):
    with open(sellers_file, 'r', newline='') as sfile, \
         open(products_file, 'r', newline='') as pfile, \
         open(output_file, 'w', newline='') as outfile:

        seller_reader = csv.reader(sfile)
        product_reader = csv.reader(pfile)
        next(seller_reader) # Skip seller header
        sellers = list(seller_reader)  # Read all sellers into memory

        product_header = next(product_reader) + ['seller_name']  # Add seller_name to product header
        writer = csv.writer(outfile)
        writer.writerow(product_header)

        for product_row in product_reader:
            num_repeats = random.randint(1, 5)  # Repeat 1-5 times
            for _ in range(num_repeats):
                seller = random.choice(sellers)  
                writer.writerow(product_row + [seller[1]] + [seller[3]])

if __name__ == "__main__":
    sellers_file = 'csellers.csv'
    products_file = 'datamanipulation_v2/output_stage2.csv'
    output_file = 'datamanipulation_v2/products_with_sellers_stage3.csv'
    add_sellers_to_products(sellers_file, products_file, output_file)
