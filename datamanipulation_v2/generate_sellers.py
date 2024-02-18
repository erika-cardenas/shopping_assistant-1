import random
import csv

# Define the cities and their probability distribution
cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Phoenix"]
city_probabilities = [0.2, 0.15, 0.1, 0.08, 0.07]

# Function to generate a random seller name
def generate_seller_name():
  seller_names = [
    "The Graphic Garage", 
    "Canvas Couture", 
    "Print Pop",
    "Novelty Niche", 
    "Fandom Finds",
    "Retro Remix", 
    "Quirk & Co.", 
    "Expression Essentials", 
    "Meme Mart",
    "Wearable Wit",
    "Cult Classic Closet",
    "Abstract Avenue",
    "Pixel Paradise",
    "Minimalist Manifesto", 
    "Statement Supply",
    "Urban Edge",
    "Nostalgic Threads",
    "DIY Dreams",
    "The Bold Bazaar",
    "Geek Chic Boutique",
    "Custom Culture",
    "Artisan Alley",
    "Pop Art Provisions",
    "Vintage Vault",
    "Indie Ink",
    "Gamer Gear",
    "Eclectic Emporium",
    "Sarcasm Society",
    "Cosmic Creations", 
    "Wanderlust Wardrobe",
    "Gadget Guru",
    "Mood Merch",
    "Hashtag Hustle",
    "Boho Bazaar",
    "Zen Zone",
    "Mystic Market",
    "Rebel Threads",
    "Self-Love Supply",
    "Motivation Merch",
    "Dreamer's Den",
    "Vinyl Vault",
    "Retro Rhapsody", 
    "90s Nostalgia",
    "Offbeat Outfitters",
    "Misfit Merch",
    "Ironic Icons",
    "Meta Merch",
    "Inside Joke Emporium" 
]

  return random.choice(seller_names)

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
