from pymongo import MongoClient

client = MongoClient("mongodb+srv://test:testpassword@cluster1-io3ru.gcp.mongodb.net/test?retryWrites=true&w=majority")

# creates database 'mydatabase'
mydb = client["mydatabase"]

# create collections 'customers'
mycol = mydb["customers"]

mydict = {"name": "John", "address": "Highway 37"}

x = mycol.insert_one(mydict)

print(client.list_database_names())