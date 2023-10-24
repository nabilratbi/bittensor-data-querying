import pymongo

# Connect to the MongoDB server
client = pymongo.MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB server URI

# Access the database and collection
db = client['bittensor']  # Replace 'mydatabase' with your database name
collection = db['bittensor-netuid11-validators']  # Replace 'mycollection' with your collection name

# Specify the specific hotkey you want to search for
specific_hotkey = "5GhUc4TojnC1HnhDft4gwPvRC9kVCMq1KjbYERpneCcVr38q"

# Find documents in the collection with the specified hotkey
results = collection.find({"neuron_hotkeys": specific_hotkey})

# Iterate through the matching documents
for doc in results:
    print(doc)


# Close the MongoDB connection
client.close()
