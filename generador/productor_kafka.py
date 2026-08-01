import json
from confluent_kafka import Producer

TOPIC = "apuestas"

conf = {
    'bootstrap.servers': 'localhost:9092',
    'linger.ms': 20,           # espera un poco para agrupar mensajes (batching)
    'batch.size': 65536,       # tamaño de lote en bytes
    'compression.type': 'lz4', # comprime para reducir tráfico
    'acks': '1',
}

producer = Producer(conf)


def _entregado(err, msg):
    if err is not None:
        print(f"[Kafka] Error entregando mensaje: {err}")


def enviar_apuesta(apuesta: dict):
    """Envía una sola apuesta a Kafka. La key es el partido_id (garantiza orden por partido)."""
    producer.produce(
        TOPIC,
        key=apuesta["partido_id"].encode("utf-8"),
        value=json.dumps(apuesta).encode("utf-8"),
        callback=_entregado
    )
    producer.poll(0)  # procesa callbacks pendientes sin bloquear


def enviar_lote(apuestas: list[dict]):
    """Envía muchas apuestas de golpe (simulación de pico)."""
    for apuesta in apuestas:
        producer.produce(
            TOPIC,
            key=apuesta["partido_id"].encode("utf-8"),
            value=json.dumps(apuesta).encode("utf-8"),
            callback=_entregado
        )
        producer.poll(0)
    producer.flush()  # espera a que todo el lote se entregue antes de continuar