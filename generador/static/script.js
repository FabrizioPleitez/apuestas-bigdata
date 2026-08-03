let partidos = [];
let seleccionActual = null;

function formatearCuota(cuota) {
  return cuota > 0 ? `+${cuota}` : `${cuota}`;
}

async function cargarPartidos() {
  const [resPartidos, resConteos] = await Promise.all([
    fetch("/partidos"),
    fetch("/conteos")
  ]);
  partidos = await resPartidos.json();
  const conteos = await resConteos.json();

  const cuerpo = document.getElementById("cuerpo-tabla");
  cuerpo.innerHTML = "";

  partidos.forEach(p => {
    const cantidad = conteos[p.partido_id] || 0;
    const fila = document.createElement("tr");
   fila.innerHTML = `
      <td><div>${p.local}</div><div style="color:#8a8f98;font-size:12px;">${p.visitante}</div></td>
      <td class="odd"><div class="odd-box" data-partido="${p.partido_id}" data-lado="local">${formatearCuota(p.cuota_local)}</div></td>
      <td class="odd"><div class="odd-box" data-partido="${p.partido_id}" data-lado="EMPATE">${formatearCuota(p.cuota_empate)}</div></td>
      <td class="odd"><div class="odd-box" data-partido="${p.partido_id}" data-lado="visitante">${formatearCuota(p.cuota_visitante)}</div></td>
      <td>${cantidad} Más Apuestas</td>
    `;
    cuerpo.appendChild(fila);
  });

  document.querySelectorAll(".odd-box").forEach(box => {
    box.addEventListener("click", () => seleccionarCuota(box));
  });
}

function seleccionarCuota(box) {
  document.querySelectorAll(".odd-box").forEach(b => b.classList.remove("seleccionada"));
  box.classList.add("seleccionada");

  const partidoId = box.dataset.partido;
  const lado = box.dataset.lado;
  const partido = partidos.find(p => p.partido_id === partidoId);

  const equipoTexto = lado === "EMPATE" ? "EMPATE" : (lado === "local" ? partido.local : partido.visitante);

  seleccionActual = { partido_id: partidoId, resultado_apostado: equipoTexto };

  document.getElementById("betslip-partido").innerText = `${partido.local} vs ${partido.visitante}`;
  document.getElementById("betslip-seleccion").innerText = equipoTexto;
  document.getElementById("betslip-mensaje").innerText = "";
  document.getElementById("betslip").classList.remove("oculto");
}

document.getElementById("cerrar-betslip").addEventListener("click", () => {
  document.getElementById("betslip").classList.add("oculto");
});

document.getElementById("btn-apostar").addEventListener("click", async () => {
  if (!seleccionActual) return;
  const monto = parseFloat(document.getElementById("betslip-monto").value);

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
    document.getElementById("betslip-mensaje").innerText = "✓ Apuesta enviada a Kafka. Actualizando...";
    setTimeout(() => {
      cargarPartidos();
      document.getElementById("betslip-mensaje").innerText = "✓ Apuesta procesada";
    }, 2500); // espera a que el consumidor haga el flush del buffer (2s + margen)
  } else {
    document.getElementById("betslip-mensaje").innerText = "Error al enviar";
  }
});

cargarPartidos();