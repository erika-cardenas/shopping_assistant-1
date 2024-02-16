import csv
import random

def create_product_subset(products_file, output_file, num_products=30):
    cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Phoenix"]

    with open(products_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        writer.writerow(['title', 'city', 'product_type'])  # Add new columns

        products = list(reader)
        random.shuffle(products)  # Shuffle products for randomness

        for row in products[:num_products]:
            city = random.choice(cities)
            product_type = row[2]  # Assuming 'product_type' is at index 2
            title = row[1]
            writer.writerow( [title, city, product_type])

if __name__ == "__main__":
    products_file = 'output_stage1.csv'
    output_file = 'trending_list.csv'
    create_product_subset(products_file, output_file)
