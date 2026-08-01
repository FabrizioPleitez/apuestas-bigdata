from fastapi import FastAPI
from modelos import Apuesta, ApuestaEntrada, LoteRequest
from realismo import elegir_partido, elegir_resultado, generar_monto, generar_usuario_id, PARTIDOS
from productor_kafka import enviar_apuesta, enviar_lote

app = FastAPI(title="Apuestas Big Data - Generador")


@app.get("/partidos")
def listar_partidos():
    """Lista los partidos disponibles (útil para pruebas con Postman)."""
    return PARTIDOS


@app.post("/apuesta")
def crear_apuesta_individual(entrada: ApuestaEntrada):
    """Envía una apuesta individual a Kafka."""
    apuesta = Apuesta(
        partido_id=entrada.partido_id,
        usuario_id=generar_usuario_id(),
        resultado_apostado=entrada.resultado_apostado,
        monto=entrada.monto,
        cuota=0,  # se podría cruzar con CUOTAS si se desea el valor exacto
        canal="individual"
    )
    enviar_apuesta(apuesta.model_dump())
    return {"status": "enviado", "apuesta": apuesta}


@app.post("/apuesta/lote")
def disparar_lote(request: LoteRequest):
    """Genera y envía muchas apuestas de golpe (simulación de pico)."""
    apuestas = []
    for _ in range(request.cantidad):
        partido_id = request.partido_id or elegir_partido()
        equipo, cuota = elegir_resultado(partido_id)
        apuesta = Apuesta(
            partido_id=partido_id,
            usuario_id=generar_usuario_id(),
            resultado_apostado=equipo,
            monto=generar_monto(),
            cuota=cuota,
            canal="lote"
        )
        apuestas.append(apuesta.model_dump())

    enviar_lote(apuestas)
    return {"status": "enviado", "cantidad": len(apuestas)}