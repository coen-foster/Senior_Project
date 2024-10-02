from polygon import RESTClient
from pymongo import MongoClient
import requests

dbclient = MongoClient("mongodb+srv://coenfoster:Fall2024@test-server.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
db = dbclient['test_db']
collection = db['test_collection']

# Your Polygon API key
api_key = '48BvoIa2pAHuKw8SBb3gIwV64xtxrIvz'

# The API endpoint (e.g., getting stock prices for a particular ticker)
url = 'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2023-08-29/2023-09-28?adjusted=true&sort=asc'

# Parameters
params = {
    'adjusted': 'true',
    'apiKey': api_key
}

# Making the GET request to the Polygon API
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    collection.insert_many(data['results'])
    print(data['results'])  # Prints the JSON data
else:
    print(f"Error: {response.status_code}")
