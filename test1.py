from pymongo import MongoClient

dbclient = MongoClient("mongodb+srv://coenfoster:Fall2024@test-server.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000")
db = dbclient['test_db']
collection = db['test_collection']

cur = collection.find({})

for doc in cur:
    print(doc)