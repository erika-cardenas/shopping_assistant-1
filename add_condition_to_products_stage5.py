import csv
import random

def add_product_condition(products_file, output_file):
    conditions = ['new', 'good as new', 'used']  # Renamed 'states' to 'conditions'
    condition_probabilities = [0.6, 0.3, 0.1] 

    with open(products_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader) + ['condition']  # Changed 'state' to 'condition'
        writer.writerow(header)

        for row in reader:
            condition = random.choices(conditions, weights=condition_probabilities)[0] 
            writer.writerow(row + [condition])

if __name__ == "__main__":
    products_file = 'products_with_costs_stage4.csv'
    output_file = 'products_with_condition_stage5.csv'  # Update the output file name if needed
    add_product_condition(products_file, output_file)