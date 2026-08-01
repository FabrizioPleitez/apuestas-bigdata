import random

# Lista fija de partidos de ejemplo, con un "peso" de popularidad.
# Peso más alto = partido más popular = recibe más apuestas.
PARTIDOS = [
    {"partido_id": "FRA-MAR-2026", "local": "France",    "visitante": "Morocco",   "peso": 30},
    {"partido_id": "ESP-BEL-2026", "local": "Spain",      "visitante": "Belgium",   "peso": 25},
    {"partido_id": "ARG-SUI-2026", "local": "Argentina",  "visitante": "Switzerland","peso": 28},
    {"partido_id": "NOR-ENG-2026", "local": "Norway",     "visitante": "England",   "peso": 12},
    {"partido_id": "BRA-JPN-2026", "local": "Brazil",     "visitante": "Japan",     "peso": 20},
    {"partido_id": "GER-CRO-2026", "local": "Germany",    "visitante": "Croatia",   "peso": 15},
    {"partido_id": "POR-KOR-2026", "local": "Portugal",   "visitante": "South Korea","peso": 18},
    {"partido_id": "MEX-CAN-2026", "local": "Mexico",     "visitante": "Canada",    "peso": 8},
]

RESULTADOS_POSIBLES = ["local", "visitante", "EMPATE"]

# Cuotas fijas de ejemplo por partido (favorito vs no favorito), formato americano.
CUOTAS = {
    "FRA-MAR-2026": {"local": -400, "visitante": 300,  "EMPATE": 220},
    "ESP-BEL-2026": {"local": -355, "visitante": 265,  "EMPATE": 240},
    "ARG-SUI-2026": {"local": -300, "visitante": 250,  "EMPATE": 230},
    "NOR-ENG-2026": {"local": 186,  "visitante": -235, "EMPATE": 260},
    "BRA-JPN-2026": {"local": -500, "visitante": 400,  "EMPATE": 280},
    "GER-CRO-2026": {"local": -180, "visitante": 155,  "EMPATE": 210},
    "POR-KOR-2026": {"local": -220, "visitante": 180,  "EMPATE": 225},
    "MEX-CAN-2026": {"local": -140, "visitante": 120,  "EMPATE": 250},
}


def elegir_partido():
    """Elige un partido al azar, ponderado por popularidad (peso)."""
    partido = random.choices(PARTIDOS, weights=[p["peso"] for p in PARTIDOS], k=1)[0]
    return partido["partido_id"]


def elegir_resultado(partido_id: str):
    """Elige un resultado apostado. Los favoritos reciben más apuestas."""
    cuotas = CUOTAS[partido_id]
    # Cuota más negativa (ej. -400) = más favorito = más probable que le apuesten
    pesos = {
        "local": 50 if cuotas["local"] < 0 else 20,
        "visitante": 50 if cuotas["visitante"] < 0 else 20,
        "EMPATE": 15,
    }
    resultado = random.choices(list(pesos.keys()), weights=list(pesos.values()), k=1)[0]

    equipo = {
        "local": next(p["local"] for p in PARTIDOS if p["partido_id"] == partido_id),
        "visitante": next(p["visitante"] for p in PARTIDOS if p["partido_id"] == partido_id),
        "EMPATE": "EMPATE",
    }[resultado]

    cuota = cuotas[resultado]
    return equipo, cuota


def generar_monto():
    """Simula montos variables: la mayoría apuestas pequeñas, algunas grandes."""
    if random.random() < 0.85:
        return round(random.uniform(5, 100), 2)   # apuesta común
    else:
        return round(random.uniform(100, 2000), 2)  # apuesta grande (minoría)


def generar_usuario_id():
    return f"u_{random.randint(1, 50000)}"