import streamlit as st
from pymongo import MongoClient

st.set_page_config(page_title="Balance de Apuestas", layout="wide")

client = MongoClient("mongodb://localhost:27017")
db = client["apuestas_bigdata"]
coleccion = db["balance_partidos"]

st.title("⚽ Balance de Apuestas — Casa de Apuestas Deportivas")

partidos = list(coleccion.find())
partido_ids = [p["partido_id"] for p in partidos]

if not partido_ids:
    st.warning("Todavía no hay datos. Dispara algunas apuestas desde el generador primero.")
else:
    seleccionado = st.selectbox("Selecciona un partido:", partido_ids)

    doc = coleccion.find_one({"partido_id": seleccionado})

    st.subheader(f"Partido: {doc['partido_id']}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Total apostado", f"${doc['total_apostado']:,.2f}")

    with col2:
        st.write("**Exposición por resultado:**")
        totales = doc["totales_por_resultado"]
        st.bar_chart(totales)

    st.write("**Detalle:**")
    for resultado, monto in totales.items():
        porcentaje = (monto / doc["total_apostado"]) * 100
        st.write(f"- {resultado}: ${monto:,.2f} ({porcentaje:.1f}%)")

    st.divider()
    st.caption("Actualiza la página para refrescar los datos más recientes.")