let partidos = [];
let seleccionActual = null;

const coloresAvatar = ["#3a9e5f", "#e0733f", "#3f7fe0", "#d6b23f", "#8a5fd6", "#3fb0ac", "#4a90c9", "#c9403f"];

function formatearCuota(cuota) {
  return cuota > 0 ? `+${cuota}` : `${cuota}`;
}

function claseParaCuota(cuota) {
  if (cuota === 0) return "draw";
  return cuota < 0 ? "fav" : "dog";
}

async function cargarPartidos() {
  const [resPartidos, resConteos] = await Promise.all([
    fetch("/partidos", { cache: "no-store" }),
    fetch("/conteos", { cache: "no-store" })
  ]);
  partidos = await resPartidos.json();
  const conteos = await resConteos.json();

  document.getElementById("count-mundial").innerText = partidos.length;

  const lista = document.getElementById("lista-partidos");
  lista.innerHTML = "";

  partidos.forEach((p, i) => {
    const cantidad = conteos[p.partido_id] || 0;
    const colorLocal = coloresAvatar[i % coloresAvatar.length];
    const colorVisitante = coloresAvatar[(i + 3) % coloresAvatar.length];

    const fila = document.createElement("div");
    fila.className = "game-row";
    fila.innerHTML = `
      <div class="game-teams">
        <div class="team"><span class="avatar" style="background:${colorLocal}">${p.local[0]}</span>${p.local}</div>
        <div class="team"><span class="avatar" style="background:${colorVisitante}">${p.visitante[0]}</span>${p.visitante}</div>
      </div>
      <div style="display:flex;align-items:center;">
        <div class="odds-group">
          <div class="odd-btn ${claseParaCuota(p.cuota_local)}" data-partido="${p.partido_id}" data-lado="local">${formatearCuota(p.cuota_local)}</div>
          <div class="odd-btn draw" data-partido="${p.partido_id}" data-lado="EMPATE">${formatearCuota(p.cuota_empate)}</div>
          <div class="odd-btn ${claseParaCuota(p.cuota_visitante)}" data-partido="${p.partido_id}" data-lado="visitante">${formatearCuota(p.cuota_visitante)}</div>
        </div>
        <div class="odd-count">${cantidad} apuestas</div>
      </div>
    `;
    lista.appendChild(fila);
  });

  document.querySelectorAll(".odd-btn").forEach(box => {
    box.addEventListener("click", () => seleccionarCuota(box));
  });
}

function seleccionarCuota(box) {
  document.querySelectorAll(".odd-btn").forEach(b => b.classList.remove("seleccionada"));
  box.classList.add("seleccionada");

  const partidoId = box.dataset.partido;
  const lado = box.dataset.lado;
  const partido = partidos.find(p => p.partido_id === partidoId);
  const equipoTexto = lado === "EMPATE" ? "EMPATE" : (lado === "local" ? partido.local : partido.visitante);
  const cuota = lado === "EMPATE" ? partido.cuota_empate : (lado === "local" ? partido.cuota_local : partido.cuota_visitante);

  seleccionActual = { partido_id: partidoId, resultado_apostado: equipoTexto, cuota: cuota };

  document.getElementById("panel-partido").innerText = `${partido.local} vs ${partido.visitante}`;
  document.getElementById("panel-seleccion").innerText = equipoTexto;
  document.getElementById("panel-mensaje").innerText = "";
  document.getElementById("panel-vacio").classList.add("oculto");
  document.getElementById("panel-lleno").classList.remove("oculto");
  calcularPago();
}

function calcularPago() {
  if (!seleccionActual) return;
  const monto = parseFloat(document.getElementById("panel-monto").value) || 0;
  const cuota = seleccionActual.cuota;

  const ganancia = cuota > 0 ? monto * (cuota / 100) : monto * (100 / Math.abs(cuota));
  const total = monto + ganancia;

  document.getElementById("panel-ganancia").innerText = `$${ganancia.toFixed(2)}`;
  document.getElementById("panel-pago-total").innerText = `$${total.toFixed(2)}`;
}

document.querySelectorAll(".quick-amounts button").forEach(btn => {
  btn.addEventListener("click", () => {
    const input = document.getElementById("panel-monto");
    input.value = (parseFloat(input.value) || 0) + parseFloat(btn.dataset.add);
    calcularPago();
  });
});

document.getElementById("panel-monto").addEventListener("input", calcularPago);

document.getElementById("btn-apostar").addEventListener("click", async () => {
  if (!seleccionActual) return;
  const monto = parseFloat(document.getElementById("panel-monto").value);

  const respuesta = await fetch("/apuesta", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      partido_id: seleccionActual.partido_id,
      resultado_apostado: seleccionActual.resultado_apostado,
      monto: monto
    })
  });

  if (respuesta.ok) {
    document.getElementById("panel-mensaje").innerText = "✓ Enviada a Kafka. Actualizando...";
    setTimeout(() => {
      cargarPartidos();
      document.getElementById("panel-mensaje").innerText = "✓ Apuesta procesada";
    }, 2500);
  } else {
    document.getElementById("panel-mensaje").innerText = "Error al enviar";
  }
});

cargarPartidos();