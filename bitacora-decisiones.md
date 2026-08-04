# Bitácora de Decisiones Técnicas
### Plataforma de Apuestas Deportivas en Tiempo Real — Big Data (IF350)
**Autor:** Esly Fabrizio Díaz Pleitez

---

## 1. Introducción

Este documento registra, en primera persona, las decisiones técnicas que tomé a lo largo del desarrollo del proyecto, el razonamiento detrás de cada una, los errores reales que enfrenté durante la implementación y cómo los resolví, y el historial de commits explicado. La intención es poder defender oralmente cualquier parte del sistema, incluyendo por qué elegí una alternativa sobre otra.

---

## 2. Decisiones de arquitectura y su justificación

### 2.1 Particionamiento de Kafka: un topic vs. varios
Decidí usar un único topic `apuestas`, particionado por `partido_id` (usado como key del mensaje), en lugar de crear un topic distinto por cada partido. Descarté un topic por partido porque con muchos partidos simultáneos el overhead de gestionar cientos de topics no escala. Al usar `partido_id` como key, Kafka garantiza que todos los eventos de un mismo partido lleguen en orden a la misma partición, indispensable para calcular el balance correctamente, mientras distintas particiones permiten paralelismo real.

### 2.2 Modelo de almacenamiento: MongoDB en vez de un modelo relacional
Elegí MongoDB porque los eventos de apuesta no llegan con un esquema estrictamente fijo y el volumen de escritura es alto (confirmado: hasta 71,357 escrituras/segundo). El operador `$inc` permite agregaciones atómicas sin condiciones de carrera, y `upsert=True` evita inicializar cada partido de antemano.

### 2.3 Procesamiento por lotes (bulk writes) en el consumidor
En vez de escribir a MongoDB por cada evento individual, el consumidor acumula operaciones en un buffer y las ejecuta con `bulk_write` cada 1000 eventos o cada 2 segundos (lo que ocurra primero). En un sistema de alto volumen, el cuello de botella real es la base de datos si se escribe una fila a la vez, no Kafka.

### 2.4 Paralelismo de consumidores sin usar Spark
Logré el procesamiento distribuido corriendo varias instancias del mismo `consumer.py`, compartiendo el mismo `group.id` (`consumidores-apuestas`), en vez de usar PySpark. Al ser un proyecto individual, prioricé minimizar la complejidad operativa: Kafka reparte automáticamente las particiones entre las instancias del grupo.

### 2.5 Cliente de Kafka: confluent-kafka sobre kafka-python
Elegí `confluent-kafka` (basado en `librdkafka` en C) por mejor rendimiento y mejor control fino de `batch.size`, `linger.ms` y `compression.type`, necesarios para la prueba de carga masiva.

### 2.6 Distribución no uniforme de datos (realismo)
Implementé pesos de popularidad por partido y de favoritismo por resultado en vez de distribución uniforme, para reflejar que hay partidos populares/ignorados y favoritos/no favoritos, tal como exige el enunciado.

### 2.7 Cuotas dinámicas basadas en volumen real
Implementé un cálculo que convierte la proporción real de dinero apostado en cada resultado en una cuota americana equivalente, para que el mercado simulado ajuste sus propias cuotas por exposición de riesgo, igual que una casa de apuestas real. Las cuotas estáticas de `realismo.py` se mantienen solo para la lógica interna de generación de datos sintéticos.

### 2.8 Particiones ampliadas a 3 y validación de tolerancia a fallos
El topic `apuestas` se creó inicialmente con 1 partición por defecto. Decidí ampliarlo a 3 particiones (`kafka-topics.sh --alter --partitions 3`) para poder demostrar paralelismo real entre consumidores, ya que con 1 sola partición un segundo consumidor del mismo grupo queda inactivo sin trabajo asignado. Con 3 particiones y 2 consumidores corriendo, confirmé en Kafka UI que Kafka repartió automáticamente 2 particiones a un consumidor y 1 al otro. Además, simulé la caída de un nodo (`Ctrl+C` a uno de los consumidores) mientras se generaba tráfico nuevo, y verifiqué que: (1) el consumidor sobreviviente siguió procesando sin interrupción, y (2) Kafka reasignó automáticamente las 3 particiones al consumidor restante (rebalance), sin pérdida de eventos. Esto valida directamente el requisito de la Fase 4 sobre responder a una modificación no anticipada en caliente (simular la caída de un nodo).

---

## 3. Registro de commits

| Fecha | Commit | Descripción | Por qué se hizo |
|---|---|---|---|
| 26/07/2026 | `d78096d` | Initial commit. Se creó el repositorio `apuestas-bigdata` en GitHub (público, con `.gitignore` de Python y README inicial). | Todo proyecto necesita un punto de partida versionado desde el día uno. |
| 26/07/2026 | `997a302` | chore: estructura inicial del proyecto y docker-compose con Kafka, Kafka UI y MongoDB. | Antes de escribir lógica de negocio, necesitaba una infraestructura reproducible. |
| 01/08/2026 | `04d31fb` | feat: app generadora con endpoints individual y lote, conectada a Kafka. | Verifiqué con Swagger UI y Kafka UI que ambos endpoints entregaban mensajes reales al topic. |
| 03/08/2026 | `1104c8e` | feat: consumidor funcionando con limpieza, agregación por lotes y persistencia en MongoDB; fix listeners Kafka. | Agrupa el consumidor terminado y el arreglo de errores reales de infraestructura (ver sección 5). |
| 03/08/2026 | `0acd167` | test: prueba de pico con 500000 apuestas - 63217 apuestas/segundo, 0 errores de entrega. | Registré el resultado apenas lo obtuve, evidencia central de la rúbrica. |
| 03/08/2026 | `0d75d87` | feat: página principal servida por FastAPI con tabla de cuotas, betslip funcional y contador de apuestas en tiempo real. | La app generadora dejó de ser solo una API de pruebas y pasó a tener una interfaz real. |
| 03/08/2026 | `be517d6` | feat: rediseño de la página principal estilo casa de apuestas real. | Iteré el diseño visual para que la demostración se vea profesional. |
| 03/08/2026 | `cf01780` | feat: cuotas dinámicas basadas en volumen real y calculadora de ganancias. | Quería que las cuotas reflejaran el dinero real apostado, no valores fijos. |
| *(pendiente)* | — | fix/test: ampliación del topic a 3 particiones, prueba de paralelismo con 2 consumidores y simulación de caída de nodo. | Necesario para demostrar escalabilidad y tolerancia a fallos con evidencia real en Kafka UI. |
| *(pendiente)* | — | docs: diagrama de arquitectura completo, README actualizado y bitácora de decisiones. | Cierre de la documentación para la entrega final. |

---

## 4. Ejemplos de prompts técnicos utilizados

**Productor de Kafka:**
> "Escribe un productor de Kafka en Python usando confluent-kafka, configurado con linger.ms=20, batch.size=65536 y compression.type=lz4 para maximizar throughput en un escenario de picos de carga. La key del mensaje debe ser el partido_id para garantizar orden dentro de cada partición."

**Consumidor con procesamiento por lotes:**
> "Escribe un consumidor de Kafka en Python que lea del topic apuestas con group.id compartido, valide cada evento, descarte duplicados por apuesta_id, y acumule las escrituras a MongoDB en un buffer que se vacíe con bulk_write cada 1000 operaciones o cada 2 segundos, usando UpdateOne con $inc y upsert=True."

**Configuración de Docker Compose:**
> "Genera un docker-compose.yml con Apache Kafka en modo KRaft para un único broker de desarrollo, exponiendo un listener PLAINTEXT accesible desde el host y un listener interno separado para otros contenedores de la misma red Docker."

**Cálculo de cuotas dinámicas:**
> "Escribe una función que convierta una probabilidad implícita en una cuota de apuestas en formato americano: si p >= 0.5, cuota = -100*p/(1-p); si p < 0.5, cuota = 100*(1-p)/p."

**Script de prueba de carga:**
> "Escribe un script que envíe 500,000 eventos JSON a un topic de Kafka, midiendo throughput y errores de entrega con un callback de producción."

---

## 5. Errores encontrados y cómo los resolví

**5.1 Librerías no reconocidas por Pylance (pydantic, pymongo).**
Síntoma: "Import could not be resolved" pese a que `pip show` confirmaba la instalación. Causa: los `pip install` se corrieron antes de activar el entorno virtual, instalando en el Python global. Solución: activar el venv primero y reinstalar ahí.

**5.2 `app.py` en la carpeta equivocada.**
Causa: el archivo se creó en la raíz en vez de dentro de `generador/`, rompiendo los imports relativos. Solución: mover el archivo y correr `uvicorn` desde dentro de `generador/`.

**5.3 `Failed to resolve 'kafka:9092'` desde Windows.**
Causa: el listener de Kafka solo se anunciaba con el hostname interno de Docker. Solución: configurar un listener PLAINTEXT (`localhost:9092`) para clientes externos y uno INTERNAL (`kafka:29092`) para servicios dentro de Docker.

**5.4 `COORDINATOR_NOT_AVAILABLE` al correr el consumidor.**
Causa: con un solo broker, Kafka no podía crear el topic interno `__consumer_offsets` (factor de replicación por defecto = 3). Solución: `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1` y reiniciar con `docker compose down -v`.

**5.5 `UNKNOWN_TOPIC_OR_PART` tras el `docker compose down -v`.**
Causa: el flag `-v` borró el volumen de Kafka, eliminando el topic existente. Solución: generar tráfico nuevo para que Kafka recreara el topic automáticamente.

**5.6 Pylance marcando import de `realismo` en `scripts/simular_pico.py`.**
Causa: el script modifica `sys.path` en tiempo de ejecución, algo que Pylance no puede anticipar estáticamente. Confirmé que el script corría bien; falso positivo aceptado.

**5.7 El contador de "Más Apuestas" no se actualizaba.**
Causa: el consumidor llevaba corriendo con código viejo (antes de agregar `cantidad_apuestas` al `$inc`). Solución: reiniciar el proceso del consumidor para tomar el código actualizado.

**5.8 `ReferenceError: ddocument is not defined` en script.js.**
Causa: error de tipeo (doble "d"). Solución: revisar la consola del navegador (F12) para ubicar la línea exacta y corregir.

**5.9 Solo 1 miembro activo en el grupo de consumidores pese a correr 2 instancias.**
Causa: el topic `apuestas` tenía únicamente 1 partición, por lo que Kafka no tenía trabajo que asignarle a un segundo consumidor. Solución: ampliar el topic a 3 particiones con `kafka-topics.sh --alter --partitions 3` y reiniciar la segunda instancia del consumidor para forzar su ingreso al rebalance.

---

## 6. Resultados medidos

- Throughput del generador (pico de 500,000 apuestas hacia un mismo partido): **63,217 apuestas/segundo**, 0 errores de entrega, 7.91 segundos en total.
- Prueba de carga dirigida (300,000 apuestas forzadas hacia Morocco en FRA-MAR-2026): **71,357 apuestas/segundo**, 0 errores de entrega.
- Balance invertido correctamente tras la prueba dirigida: Morocco pasó de 23.5% a 52.2% del dinero apostado, reflejado en el dashboard y en las cuotas dinámicas.
- Con 3 particiones y 2 consumidores activos: Kafka repartió automáticamente 2 particiones a un consumidor y 1 al otro (confirmado en Kafka UI).
- Simulación de caída de nodo: al detener uno de los dos consumidores en plena carga, el consumidor restante absorbió el tráfico sin interrupción, y Kafka reasignó las 3 particiones al único consumidor activo en cuestión de segundos (rebalance automático), sin pérdida de eventos.

---

