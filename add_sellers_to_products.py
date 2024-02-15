import csv
import random

def add_sellers_to_products(sellers_file, products_file, output_file):
    with open(sellers_file, 'r', newline='') as sfile, \
         open(products_file, 'r', newline='') as pfile, \
         open(output_file, 'w', newline='') as outfile:

        seller_reader = csv.reader(sfile)
        product_reader = csv.reader(pfile)

        sellers = list(seller_reader)  # Read all sellers into memory
        next(sellers)  # Skip seller header

        product_header = next(product_reader) + ['seller_name']  # Add seller_name to product header
        writer = csv.writer(outfile)
        writer.writerow(product_header)

        for product_row in product_reader:
            num_repeats = random.randint(1, 5)  # Repeat 1-5 times
            for _ in range(num_repeats):
                seller = random.choice(sellers)[0]  # Randomly choose a seller
                writer.writerow(product_row + [seller])

if __name__ == "__main__":
    sellers_file = 'sellers.csv'
    products_file = 'output_stage2.csv'
    output_file = 'products_with_sellers.csv'
    add_sellers_to_products(sellers_file, products_file, output_file)
