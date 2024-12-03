import requests
from datetime import datetime
from pymongo import MongoClient

client = MongoClient("mongodb+srv://coenfoster:Fall2024@test-server.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
db = client['test_db']
collection = db['KO']

api_key = 'aKCyCKnVhCB8pJz9_vOpOfebGHWYT0XQ'
ticker = 'KO'
multiplier = 1
timespan = 'day'
start_date = '2020-01-01'
end_date = '2024-12-02'

url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}"
params = {
    "adjusted": "true",
    "sort": "asc",
    "limit": 50000,
    "apiKey": api_key
}

response = requests.get(url, params=params)
data = response.json()

# Check if 'results' is in the response data
if 'results' in data:
    # Add dates to the data by converting the timestamp
    for entry in data['results']:
        entry['date'] = datetime.fromtimestamp(entry['t'] / 1000).strftime('%Y-%m-%d')
    
    # Print data with dates
    for entry in data['results']:
        print(f"Date: {entry['date']}, Open: {entry['o']}, High: {entry['h']}, Low: {entry['l']}, Close: {entry['c']}")
    
    # Fetch all existing dates from the database
    existing_dates = {doc["date"] for doc in collection.find({}, {"date": 1, "_id": 0})}

    # Filter out entries with dates already in the database
    unique_entries = [
        entry for entry in data['results'] if entry["date"] not in existing_dates
    ]

    collection.insert_many(unique_entries)

else:
    print("Error in response:", data)