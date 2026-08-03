from pymongo import MongoClient, UpdateOne

client = MongoClient("mongodb://localhost:27017")
db = client["apuestas_bigdata"]
coleccion = db["balance_partidos"]


def construir_update(apuesta: dict) -> UpdateOne:
    """Construye una operación de actualización para una apuesta.
    Usa $inc para sumar de forma atómica, sin condiciones de carrera."""
    partido_id = apuesta["partido_id"]
    resultado = apuesta["resultado_apostado"]
    monto = apuesta["monto"]

    return UpdateOne(
        {"partido_id": partido_id},
        {
            "$inc": {
                f"totales_por_resultado.{resultado}": monto,
                "total_apostado": monto,
                "cantidad_apuestas": 1,
            }
        },
        upsert=True  # si el partido no existe todavía, lo crea
    )


def guardar_lote(operaciones: list[UpdateOne]):
    """Ejecuta muchas actualizaciones de golpe (bulk write)."""
    if not operaciones:
        return
    coleccion.bulk_write(operaciones)


def obtener_balance(partido_id: str):
    """Consulta el balance actual de un partido (usado luego por el dashboard)."""
    return coleccion.find_one({"partido_id": partido_id})