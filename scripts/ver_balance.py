from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["apuestas_bigdata"]
coleccion = db["balance_partidos"]

for doc in coleccion.find():
    print(doc)