from pymongo import MongoClient
import requests

dbclient = MongoClient("mongodb+srv://coenfoster:Fall2024@test-server.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
db = dbclient['test_db']
collection = db['test_collection']

# The API endpoint (e.g., getting stock prices for a particular ticker)
url = 'https://api.polygon.io/v1/open-close/AAPL/2024-10-9?adjusted=true&apiKey=48BvoIa2pAHuKw8SBb3gIwV64xtxrIvz'

# Parameters
params = {
    'adjusted': 'true',
}

# Making the GET request to the Polygon API
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    collection.insert_one(data)
    print(data)  # Prints the JSON data
else:
    print(f"Error: {response.status_code}")
