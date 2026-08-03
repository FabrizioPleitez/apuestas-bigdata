import sys
import os
import time
import json
import uuid
from confluent_kafka import Producer

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "generador"))
from realismo import generar_monto, generar_usuario_id, CUOTAS

TOPIC = "apuestas"
PARTIDO_ID = "FRA-MAR-2026"
EQUIPO_OBJETIVO = "Morocco"   # <-- a este equipo le mandamos todo el volumen
CANTIDAD = 300_000

conf = {
    'bootstrap.servers': 'localhost:9092',
    'linger.ms': 20,
    'batch.size': 65536,
    'compression.type': 'lz4',
    'acks': '1',
}
producer = Producer(conf)

errores_entrega = 0
suma_enviada = 0.0


def entregado(err, msg):
    global errores_entrega
    if err is not None:
        errores_entrega += 1


def generar_apuesta_dirigida():
    monto = generar_monto()
    cuota = CUOTAS[PARTIDO_ID]["visitante"]  # Morocco es el "visitante" en este partido
    return {
        "apuesta_id": str(uuid.uuid4()),
        "partido_id": PARTIDO_ID,
        "usuario_id": generar_usuario_id(),
        "resultado_apostado": EQUIPO_OBJETIVO,
        "monto": monto,
        "cuota": cuota,
        "timestamp": time.time(),
        "canal": "lote"
    }, monto


print(f"Simulando pico DIRIGIDO: {CANTIDAD} apuestas, todas hacia '{EQUIPO_OBJETIVO}' en {PARTIDO_ID}...")
inicio = time.time()

for i in range(CANTIDAD):
    apuesta, monto = generar_apuesta_dirigida()
    suma_enviada += monto
    producer.produce(
        TOPIC,
        key=PARTIDO_ID.encode("utf-8"),
        value=json.dumps(apuesta).encode("utf-8"),
        callback=entregado
    )
    if i % 20000 == 0:
        producer.poll(0)
        print(f"  ...{i} enviadas (${suma_enviada:,.2f} acumulado hacia {EQUIPO_OBJETIVO})")

producer.flush()

duracion = time.time() - inicio
print()
print("========== RESULTADOS ==========")
print(f"Equipo objetivo:      {EQUIPO_OBJETIVO}")
print(f"Total enviado:        {CANTIDAD}")
print(f"Suma total apostada:  ${suma_enviada:,.2f}")
print(f"Errores de entrega:   {errores_entrega}")
print(f"Tiempo total:         {duracion:.2f} segundos")
print(f"Throughput:           {CANTIDAD/duracion:.0f} apuestas/segundo")
print("=================================")