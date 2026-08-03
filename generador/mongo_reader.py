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

def _prob_a_cuota_americana(p):
    """Convierte una probabilidad implícita (0-1) a cuota en formato americano."""
    if p <= 0.01:
        return 10000
    if p >= 0.99:
        return -10000
    if p >= 0.5:
        return round(-100 * p / (1 - p))
    else:
        return round(100 * (1 - p) / p)


def obtener_cuotas_dinamicas():
    """Calcula cuotas en vivo según el dinero real apostado en cada partido.
    Devuelve {partido_id: {nombre_equipo_o_EMPATE: cuota}}.
    Solo incluye partidos que ya tienen al menos una apuesta registrada.
    """
    cuotas_dinamicas = {}
    for doc in coleccion.find({}):
        total = doc.get("total_apostado", 0)
        if total <= 0:
            continue
        totales = doc.get("totales_por_resultado", {})
        cuotas_dinamicas[doc["partido_id"]] = {
            equipo: _prob_a_cuota_americana(monto / total)
            for equipo, monto in totales.items()
        }
    return cuotas_dinamicas