import random
import csv

def update_product_costs(products_file, output_file):
    with open(products_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        header[4] = 'cost'  # Change 'value' header to 'cost'
        writer.writerow(header)

        products = {}  # To store products with their base cost
        for row in reader:
            product_id = row[1]
            if product_id not in products:
                products[product_id] = random.randint(5, 100)  # Store base cost

            base_cost = products[product_id]
            cost_variation = random.randint(-10, 10)
            final_cost = max(5, min(100, base_cost + cost_variation))  # Ensure cost remains in range
            row[4] = final_cost
            writer.writerow(row)

if __name__ == "__main__":
    products_file = 'products_with_sellers_stage3.csv'
    output_file = 'products_with_costs_stage4.csv'
    update_product_costs(products_file, output_file)
