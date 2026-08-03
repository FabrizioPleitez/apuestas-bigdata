from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from modelos import Apuesta, ApuestaEntrada, LoteRequest
from realismo import elegir_partido, elegir_resultado, generar_monto, generar_usuario_id, PARTIDOS, CUOTAS
from productor_kafka import enviar_apuesta, enviar_lote
from mongo_reader import obtener_conteos, obtener_cuotas_dinamicas

app = FastAPI(title="Apuestas Big Data - Generador")

@app.get("/conteos")
def conteos_por_partido():
    """Cuántas apuestas ha recibido cada partido (para la página principal)."""
    return obtener_conteos()

@app.get("/cuotas")
def cuotas_dinamicas():
    """Devuelve las cuotas dinámicas para cada partido."""
    return obtener_cuotas_dinamicas()

@app.get("/")
def pagina_principal():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/partidos")
def listar_partidos():
    """Lista los partidos con sus cuotas. Si el partido ya tiene apuestas
    reales, las cuotas se recalculan dinámicamente según el dinero apostado
    (igual que una casa real ajusta cuotas por volumen/riesgo); si no,
    se usan las cuotas iniciales estáticas de realismo.py."""
    cuotas_dinamicas = obtener_cuotas_dinamicas()
    resultado = []
    for p in PARTIDOS:
        estaticas = CUOTAS[p["partido_id"]]
        dinamicas = cuotas_dinamicas.get(p["partido_id"])

        if dinamicas:
            cuota_local = dinamicas.get(p["local"], estaticas["local"])
            cuota_visitante = dinamicas.get(p["visitante"], estaticas["visitante"])
            cuota_empate = dinamicas.get("EMPATE", estaticas["EMPATE"])
        else:
            cuota_local, cuota_visitante, cuota_empate = estaticas["local"], estaticas["visitante"], estaticas["EMPATE"]

        resultado.append({
            **p,
            "cuota_local": cuota_local,
            "cuota_visitante": cuota_visitante,
            "cuota_empate": cuota_empate,
        })
    return resultado


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