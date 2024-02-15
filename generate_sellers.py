import random
import csv

# Define the cities and their probability distribution
cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Phoenix"]
city_probabilities = [0.2, 0.15, 0.1, 0.08, 0.07]

# Function to generate a random seller name
def generate_seller_name():
  first_names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Henry", "Isabella", "Jack"]
  last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Garcia", "Rodriguez", "Wilson", "Lewis"]
  return random.choice(first_names) + " " + random.choice(last_names)

# Function to generate a random seller rating
def generate_seller_rating():
  # More values between 3 and 4
  return round(random.uniform(2.5, 4.5), 1)

# Generate seller data
sellers = []
for i in range(40):
  seller_id = i + 1
  seller_name = generate_seller_name()
  seller_location = random.choices(cities, weights=city_probabilities)[0]
  seller_rating = generate_seller_rating()
  sellers.append([seller_id, seller_name, seller_location, seller_rating])

# Write data to CSV file
with open("sellers.csv", "w", newline="") as csvfile:
  writer = csv.writer(csvfile)
  writer.writerow(["seller_id", "seller_name", "seller_location", "seller_rating"])
  writer.writerows(sellers)

print("Sellers table generated successfully!")
