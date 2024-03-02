import csv
import requests

def check_link(url):
    try:
        response = requests.get(url)
        return response.status_code != 404  # Return True if not a 404
    except requests.exceptions.RequestException:
        return False  # Handle connection errors

def main():
    with open('datamanipulation/data/input.csv', 'r', newline='') as infile, open('datamanipulation/data/1_removed_broken_links.csv', 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)  # Read the header row
        writer.writerow(header)  # Write the header to the output file

        for row in reader:
            link = row[6]  # Replace 'links_column_index' with the correct index
            if check_link(link):
                writer.writerow(row)

if __name__ == "__main__":
    main()
