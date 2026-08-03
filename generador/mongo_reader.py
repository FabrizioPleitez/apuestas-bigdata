from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["apuestas_bigdata"]
coleccion = db["balance_partidos"]


def obtener_conteos():
    """Devuelve un diccionario {partido_id: cantidad_apuestas} para mostrar en la página."""
    conteos = {}
    for doc in coleccion.find({}, {"partido_id": 1, "cantidad_apuestas": 1}):
        conteos[doc["partido_id"]] = doc.get("cantidad_apuestas", 0)
    return conteos