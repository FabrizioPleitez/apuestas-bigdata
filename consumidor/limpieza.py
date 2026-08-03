# Guarda en memoria los IDs de apuestas ya procesadas, para detectar duplicados.
# (En un sistema real esto se manejaría con una ventana de tiempo o una base
# de datos, pero para el proyecto un set en memoria es suficiente y defendible.)
apuestas_procesadas = set()


def es_valida(apuesta: dict) -> bool:
    """Verifica que la apuesta tenga los campos mínimos y valores sensatos."""
    campos_requeridos = ["apuesta_id", "partido_id", "resultado_apostado", "monto"]

    for campo in campos_requeridos:
        if campo not in apuesta or apuesta[campo] in (None, ""):
            return False

    if not isinstance(apuesta["monto"], (int, float)) or apuesta["monto"] <= 0:
        return False

    return True


def es_duplicada(apuesta: dict) -> bool:
    """Verifica si ya procesamos esta apuesta antes (por su ID único)."""
    apuesta_id = apuesta.get("apuesta_id")
    if apuesta_id in apuestas_procesadas:
        return True
    apuestas_procesadas.add(apuesta_id)
    return False


def limpiar(apuesta: dict) -> dict | None:
    """Devuelve la apuesta si es válida y no duplicada, o None si debe descartarse."""
    if not es_valida(apuesta):
        return None
    if es_duplicada(apuesta):
        return None
    return apuesta