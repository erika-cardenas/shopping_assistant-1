import csv

def remove_columns(input_file, output_file, columns_to_remove):
    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader) 
        column_indexes = [header.index(col) for col in header if col not in columns_to_remove]  

        writer.writerow([header[i] for i in column_indexes])  # Write modified header

        for row in reader:
            writer.writerow([row[i] for i in column_indexes])  # Write rows without removed columns

if __name__ == "__main__":
    input_file = 'datamanipulation/data/1_removed_broken_links.csv'
    output_file = 'datamanipulation/data/2_removed_unnecessary_columns.csv'
    columns_to_remove = ['availability', 'link']

    remove_columns(input_file, output_file, columns_to_remove)
