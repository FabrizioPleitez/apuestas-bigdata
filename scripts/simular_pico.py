import sys
import os
import time
import json
import uuid
from confluent_kafka import Producer

# Permite importar los módulos de la carpeta generador/ desde scripts/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "generador"))
from realismo import elegir_resultado, generar_monto, generar_usuario_id

TOPIC = "apuestas"
PARTIDO_ID = "FRA-MAR-2026"  # partido más popular de la lista (peso=30)
CANTIDAD = 500_000

conf = {
    'bootstrap.servers': 'localhost:9092',
    'linger.ms': 20,
    'batch.size': 65536,
    'compression.type': 'lz4',
    'acks': '1',
}
producer = Producer(conf)

errores_entrega = 0


def entregado(err, msg):
    global errores_entrega
    if err is not None:
        errores_entrega += 1


def generar_apuesta():
    equipo, cuota = elegir_resultado(PARTIDO_ID)
    return {
        "apuesta_id": str(uuid.uuid4()),
        "partido_id": PARTIDO_ID,
        "usuario_id": generar_usuario_id(),
        "resultado_apostado": equipo,
        "monto": generar_monto(),
        "cuota": cuota,
        "timestamp": time.time(),
        "canal": "lote"
    }


print(f"Simulando pico: {CANTIDAD} apuestas para el partido {PARTIDO_ID}...")
inicio = time.time()

for i in range(CANTIDAD):
    apuesta = generar_apuesta()
    producer.produce(
        TOPIC,
        key=PARTIDO_ID.encode("utf-8"),
        value=json.dumps(apuesta).encode("utf-8"),
        callback=entregado
    )
    if i % 10000 == 0:
        producer.poll(0)
        print(f"  ...{i} enviadas")

producer.flush()

duracion = time.time() - inicio
print()
print("========== RESULTADOS ==========")
print(f"Total enviado:      {CANTIDAD}")
print(f"Errores de entrega: {errores_entrega}")
print(f"Tiempo total:       {duracion:.2f} segundos")
print(f"Throughput:         {CANTIDAD/duracion:.0f} apuestas/segundo")
print("=================================")