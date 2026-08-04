# Plataforma de Apuestas Deportivas en Tiempo Real

Proyecto Integrador — III Parcial — Big Data (IF350)
Autor: Esly Fabrizio Díaz Pleitez

Sistema de captura, ingesta, procesamiento y visualización del balance de apuestas deportivas en tiempo real, construido con Kafka, MongoDB, FastAPI y Streamlit.

## Arquitectura

Ver `diagrama-arquitectura.png` para el diagrama completo y `bitacora-decisiones.md` para el detalle de cada decisión técnica y sus trade-offs.

## Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.12+](https://www.python.org/downloads/)
- Git

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/FabrizioPleitez/apuestas-bigdata.git
cd apuestas-bigdata
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r generador/requirements.txt
pip install -r consumidor/requirements.txt
pip install -r dashboard/requirements.txt
```

### 4. Levantar la infraestructura (Kafka, MongoDB, Kafka UI)

```bash
docker compose up -d
docker compose ps   # confirmar que los 3 servicios estén "Up"
```

Kafka UI queda disponible en **http://localhost:8080**.

### 5. Aumentar las particiones del topic (para demostrar paralelismo)

El topic `apuestas` se crea con 1 partición por defecto la primera vez que se envía un mensaje. Para habilitar procesamiento paralelo con múltiples consumidores:

```bash
docker exec -it apuestas-bigdata-kafka-1 /opt/kafka/bin/kafka-topics.sh --alter --topic apuestas --partitions 3 --bootstrap-server localhost:9092
```

## Ejecución

Se necesitan varias terminales corriendo simultáneamente (con el entorno virtual activado en cada una):

### Terminal 1 — App generadora (backend + página web)

```bash
cd generador
uvicorn app:app --reload
```

Página principal: **http://127.0.0.1:8000/** (tabla de cuotas dinámicas, panel de apuesta, cálculo de ganancias)
Documentación interactiva de la API: **http://127.0.0.1:8000/docs**

### Terminal 2 y 3 — Consumidores (ejecutar el mismo comando en ambas para demostrar paralelismo)

```bash
cd consumidor
python consumer.py
```

Al correr dos instancias con el mismo `group.id`, Kafka reparte automáticamente las 3 particiones entre ambas. Si se detiene una (`Ctrl+C`), Kafka reasigna sus particiones a la que sigue activa (tolerancia a fallos), sin pérdida de eventos.

### Terminal 4 — Dashboard

```bash
cd dashboard
streamlit run app.py
```

Disponible en **http://localhost:8501**.

## Prueba de carga

Para simular un pico extremo (ej. 500,000 apuestas hacia un mismo partido):

```bash
cd scripts
python simular_pico.py
```

Resultado documentado en la última prueba: **63,217 apuestas/segundo, 0 errores de entrega, 500,000 eventos procesados sin pérdida.**

## Verificación manual de datos

```bash
cd scripts
python ver_balance.py
```

## Estructura del repositorio