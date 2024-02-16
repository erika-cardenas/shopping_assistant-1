import csv
import json

def csv_to_json_list(csv_file):
    json_data = []
    count = 1

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            product = {
                "id": "id_"+str(count),
                "title": row["title"],
                "categories": [row["product_type"]],
                "priceInfo": {
                    "price": row["cost"],
                },
                "uri": row["image_link"],
                "attributes": {
                    "link": {"text":row["image_link"]},
                    "seller_name": {"text": row["seller_name"]},
                    "condition": {"text": row["condition"]},
                }
            }
            json_data.append(product)
            count+=1

    return json_data

if __name__ == "__main__":
    csv_file = "products_with_condition_stage5.csv"  # Replace with your CSV file name
    json_list = csv_to_json_list(csv_file)

    # Save to a JSON file (optional)
    with open("output_products.json", "w") as outfile:
        json.dump(json_list, outfile, indent=4)  # Indentation for readability
    with open('output_products.json', 'w') as outfile:
        for item in json_list:
            outfile.write(json.dumps(item))
            outfile.write('\n')
