import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Energy AI Assistant (Demo)", layout="wide")

st.title("⚡ Asistente inteligente de consumo energético")
st.caption("Demo conceptual · No funcional · Datos simulados")

# -----------------------------
# 1. Subida de contrato
# -----------------------------
st.header("1️⃣ Subida de contrato")

contract = st.file_uploader(
    "Sube tu contrato eléctrico (PDF/TXT)",
    type=["pdf", "txt"]
)

if contract:
    st.success("Contrato recibido ✅")
    st.text_area(
        "Vista anonimizada (demo)",
        "Cliente: [ANONIMIZADO]\nCUPS: [OCULTO]\nTarifa con horas reducidas de 00:00 a 08:00\nRecargo: +10%",
        height=120
    )

# Reglas contractuales simuladas
contract_rules = {
    "recargo_pct": 10,
    "horas_baratas": list(range(0, 8))
}

# -----------------------------
# Precios horarios simulados
# -----------------------------
hours = list(range(24))
prices = np.random.uniform(0.08, 0.25, 24)

prices_df = pd.DataFrame({
    "Hora": hours,
    "Precio mercado (€/kWh)": prices,
})

prices_df["Precio efectivo (€/kWh)"] = prices_df["Precio mercado (€/kWh)"] * (1 + contract_rules["recargo_pct"]/100)

# st.subheader("📈 Precios horarios (simulados)")
# st.dataframe(prices_df, use_container_width=True)
# st.info("ℹ️ Datos simulados. En producción se obtendrían diariamente de OMIE y se cachearían ante fallos.")

# -----------------------------
# 2. Definición de tareas (contador + columnas dinámicas)
# -----------------------------
st.header("2️⃣ Definir tareas")

# Estado persistente
if "num_tasks" not in st.session_state:
    st.session_state.num_tasks = 1

# Controles de contador
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    if st.button("➕ Añadir tarea"):
        st.session_state.num_tasks += 1
with c2:
    if st.button("➖ Quitar tarea") and st.session_state.num_tasks > 1:
        st.session_state.num_tasks -= 1
with c3:
    st.metric("Nº de tareas", st.session_state.num_tasks)

# Construir tareas en columnas: 1 tarea = 1 columna
task_cols = st.columns(st.session_state.num_tasks)
tasks = []

for i, col in enumerate(task_cols, start=1):
    with col:
        st.subheader(f"🧺 Tarea {i}")

        task = st.selectbox(
            "Tarea",
            ["Lavavajillas", "Lavadora", "Horno"],
            key=f"task_{i}"
        )

        duration = st.number_input(
            "Duración (min)",
            30, 240, 90,
            step=15,
            key=f"duration_{i}"
        )

        availability = st.slider(
            "Disponibilidad horaria",
            0, 23, (8, 22),
            key=f"availability_{i}"
        )

        tasks.append({
            "id": i,
            "task": task,
            "duration": int(duration),
            "availability": availability
        })

with st.expander("📋 Ver tareas (demo)"):
    st.write(tasks)

# -----------------------------
# 3. Recuperación (RAG demo) - por tarea
# -----------------------------
st.header("3️⃣ Recuperación de franjas óptimas (RAG)")

rag_results = []

for t in tasks:
    a0, a1 = t["availability"]

    available = prices_df[
        (prices_df["Hora"] >= a0) &
        (prices_df["Hora"] <= a1)
    ].copy()

    cheapest = available.sort_values("Precio efectivo (€/kWh)").head(3)

    rag_results.append({
        "task_id": t["id"],
        "task": t["task"],
        "duration": t["duration"],
        "availability": t["availability"],
        "candidates": cheapest
    })

# Mostrar resultados por tarea
for r in rag_results:
    st.subheader(f"Franjas candidatas más económicas — Tarea {r['task_id']}: {r['task']}")
    st.table(r["candidates"])

# -----------------------------
# 4. Generación de recomendación - por tarea (demo)
# -----------------------------
st.header("4️⃣ Recomendación generada")

all_recommendations = []

for r in rag_results:
    cands = r["candidates"]

    if cands.empty or len(cands) < 1:
        rec = f"❌ No hay horas candidatas para **{r['task']}** con la disponibilidad {r['availability']}."
        all_recommendations.append(rec)
        continue

    best_hour = int(cands.iloc[0]["Hora"])
    alt_hour = int(cands.iloc[1]["Hora"]) if len(cands) > 1 else None

    best_price = float(cands.iloc[0]["Precio efectivo (€/kWh)"])
    alt_price = float(cands.iloc[1]["Precio efectivo (€/kWh)"]) if len(cands) > 1 else None

    recommendation = f"""
### ✅ {r['task']} (Tarea {r['task_id']})

✅ **Recomendación principal**  
Ejecuta **{r['task']}** a las **{best_hour}:00 h**  
💶 Precio efectivo estimado: **{best_price:.3f} €/kWh**

"""

    if alt_hour is not None:
        recommendation += f"""
🔁 **Alternativa**  
Si no puedes, la siguiente mejor opción es a las **{alt_hour}:00 h**  
💶 Precio efectivo estimado: **{alt_price:.3f} €/kWh**

"""

    recommendation += f"""
🧾 **Justificación**  
Basado en precios horarios (simulados) + condiciones del contrato (recargo {contract_rules['recargo_pct']}%).  
Ventana de disponibilidad: **{r['availability'][0]}–{r['availability'][1]}**.
"""

    all_recommendations.append(recommendation)

# Pintar todas las recomendaciones
for rec in all_recommendations:
    st.markdown(rec)

# -----------------------------
# 5. Accesibilidad (demo)
# -----------------------------
with st.expander("♿ Accesibilidad", expanded=False):

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🔊 Escuchar recomendación (demo)"):
            st.info("Salida por voz simulada (Text-to-Speech)")

    with col_b:
        st.image(
            "avatar.png"  
        )