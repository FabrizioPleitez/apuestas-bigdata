import json
import time
from confluent_kafka import Consumer
from limpieza import limpiar
from mongo_client import construir_update, guardar_lote

TOPIC = "apuestas"
BATCH_SIZE = 1000
BATCH_TIMEOUT = 2.0

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumidores-apuestas',
    'auto.offset.reset': 'earliest',
}

consumer = Consumer(conf)
consumer.subscribe([TOPIC])

buffer_operaciones = []
ultimo_flush = time.time()

print("Consumidor iniciado. Esperando mensajes...")

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is not None:
            if msg.error():
                print(f"[Kafka] Error: {msg.error()}")
            else:
                apuesta = json.loads(msg.value().decode("utf-8"))
                apuesta_limpia = limpiar(apuesta)

                if apuesta_limpia is not None:
                    buffer_operaciones.append(construir_update(apuesta_limpia))
                else:
                    print(f"[Descartada] apuesta_id={apuesta.get('apuesta_id')} (inválida o duplicada)")

        tiempo_transcurrido = time.time() - ultimo_flush
        if len(buffer_operaciones) >= BATCH_SIZE or (buffer_operaciones and tiempo_transcurrido >= BATCH_TIMEOUT):
            guardar_lote(buffer_operaciones)
            print(f"[MongoDB] Guardadas {len(buffer_operaciones)} apuestas en lote")
            buffer_operaciones = []
            ultimo_flush = time.time()

except KeyboardInterrupt:
    print("Deteniendo consumidor...")

finally:
    if buffer_operaciones:
        guardar_lote(buffer_operaciones)
        print(f"[MongoDB] Guardado final: {len(buffer_operaciones)} apuestas")
    consumer.close()