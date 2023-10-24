import wandb
import csv
import pandas as pd
from pymongo import MongoClient


#Load Wandb API
def load_wandb_api(key="3adfb8f826e5403777729f4ea9a3d5bc25485635"):
    wandb.login(key=key)
    api = wandb.Api(timeout=29)
    return api

#Load the collection from MongoDB server
def load_collection(client, db_name, collection_name):
    # Create or get a reference to the database
    db = client[db_name]  # Replace 'mydatabase' with your desired database name
    # Create or get a reference to the collection
    collection = db[collection_name]  # Replace 'mycollection' with your desired collection name
    return collection

#Structure the run data to get what we want before pushing to the database
def structure_loaded_data(run):
    rh = pd.DataFrame(run.history())
    df = rh[['_timestamp', 'neuron_weights',"neuron_hotkeys","rewards", "prompt", "best"]].copy()
    df['Date'] = pd.to_datetime(df['_timestamp'], unit='s')  # 's' stands for seconds
    # Forward fill missing values in 'column1'
    df[['neuron_weights','neuron_hotkeys']] = df[['neuron_weights','neuron_hotkeys']].ffill()
    df.loc[:,'run_id'] = pd.Series([run.id]*len(df)).copy()
    processed = df.dropna(subset = ['prompt', 'best'])
    return processed

# Connect to the MongoDB Server
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB server URI

#Loading Collection
collection = load_collection(client, 'bittensor', 'bittensor-netuid11-validators')

#Loading Wandb API
api = load_wandb_api()

# Define the filters to retrieve runs that match specific conditions
filters = {
    "tags": {"$in": ["netuid_11"]},
    "state":"running",
}

#Get all runs by filter
runs = api.runs("opentensor-dev/openvalidators", filters=filters)

data_frames= []

# Loop over the runs to collect data and retrieve their IDs
for run in runs:
    processed = structure_loaded_data(run)
    data_frames.append(processed)

# Concatenate the data frames in the list
combined_df = pd.concat(data_frames)

for index, row in combined_df.iterrows():
    timestamp = row['_timestamp']
    existing_doc = collection.find_one({'_timestamp': timestamp})

    if existing_doc:
        # Document with the same _timestamp already exists
        # You can choose to skip it or update it here
        pass
    else:
        # Document with _timestamp doesn't exist, insert it
        document_to_insert = {
            '_timestamp': timestamp,
            'neuron_weights': row['neuron_weights'],
            'neuron_hotkeys': row['neuron_hotkeys'],
            'rewards': row['rewards'],
            'prompt': row['prompt'],
            'best': row['best'], 
            'Date': row['Date'],
            'run_id': row['run_id']

            # Add other fields as needed
        }
        collection.insert_one(document_to_insert)

# Close the MongoDB connection
client.close()

# # Assuming you have a DataFrame named 'df'
# data = combined_df.to_dict(orient='records')

# # Insert data into the collection
# collection.insert_many(data)