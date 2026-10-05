"""
app.py
Interfaz Streamlit de DemandIA Fresh.
Ejecutar con:  streamlit run app.py
"""

import plotly.graph_objects as go
import streamlit as st

from config import (AJUSTE_REACTIVO, ESTRATEGIAS, PASO_CANDIDATOS, UMBRAL_BAJAR,
                    UMBRAL_SUBIR, VENTANA_HISTORIAL, Parametros)
from metrics import calcular_metricas_finales, estrategia_ganadora
from simulation import ejecutar_multiples_corridas, ejecutar_simulacion

st.set_page_config(page_title="DemandIA Fresh", page_icon="🥐", layout="wide")

COLORES = {"Base": "#8d99ae", "Reactivo": "#f4a261", "Utilidad": "#2a9d8f"}
POR_DEFECTO = Parametros()

st.markdown(
    """
    <style>
    .hero {padding: 1.2rem 1.5rem; border-radius: 14px; margin-bottom: 1rem;
           background: linear-gradient(120deg, #1d3557 0%, #2a9d8f 100%);}
    .hero h1 {color: #ffffff; margin: 0; padding: 0; font-size: 2.2rem;}
    .hero .sub {color: #f1faee; font-size: 1.1rem; margin: .3rem 0 0 0;}
    .hero .desc {color: #cfe8e4; font-size: .9rem; margin: .2rem 0 0 0;}
    </style>
    <div class="hero">
      <h1>🥐 DemandIA Fresh</h1>
      <p class="sub">Inteligencia para producir lo necesario, vender más y desperdiciar menos.</p>
      <p class="desc">Simulador de agentes inteligentes para optimización de producción
      de alimentos perecibles.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- Barra lateral -----------------------------
with st.sidebar:
    st.header("⚙️ Configuración")
    st.subheader("Economía del negocio (S/)")
    precio_venta = st.number_input("Precio de venta por unidad", min_value=0.1,
                                   value=POR_DEFECTO.precio_venta, step=0.5)
    costo_produccion = st.number_input("Costo de producción por unidad", min_value=0.0,
                                       value=POR_DEFECTO.costo_produccion, step=0.5)
    costo_desperdicio = st.number_input("Costo por unidad desperdiciada", min_value=0.0,
                                        value=POR_DEFECTO.costo_desperdicio, step=0.5, help="Costo adicional generado por cada unidad que queda sin vender.")
    penalizacion = st.number_input("Penalización por venta perdida", min_value=0.0,
                                   value=POR_DEFECTO.penalizacion_venta_perdida, step=0.5, help="Costo asociado a no poder atender una unidad demandada.")

    st.subheader("Demanda y simulación")
    demanda_media = st.slider("Demanda promedio (unidades/día)", 20, 300,
                              POR_DEFECTO.demanda_media)
    produccion_base = st.number_input("Producción fija del modo base (unidades/día)",
                                      min_value=0, max_value=1000,
                                      value=POR_DEFECTO.produccion_base, step=5)
    dias = st.slider("Número de días", 7, 90, POR_DEFECTO.dias)
    seed = st.number_input("Semilla aleatoria", min_value=0,
                           value=POR_DEFECTO.seed, step=1)

    st.subheader("Validación")
    n_corridas = st.slider("Semillas para validar el resultado", 5, 100, 30)

p = Parametros(demanda_media=int(demanda_media), precio_venta=float(precio_venta),
               costo_produccion=float(costo_produccion),
               costo_desperdicio=float(costo_desperdicio),
               penalizacion_venta_perdida=float(penalizacion),
               produccion_base=int(produccion_base), dias=int(dias), seed=int(seed))

ejecutar = st.sidebar.button("🚀 Ejecutar simulación", type="primary",
                             use_container_width=True)


@st.cache_data(show_spinner="Comparando estrategias en varias semillas...")
def validar(p, n_corridas):
    return ejecutar_multiples_corridas(p, n_corridas)


# El resultado se guarda en session_state para que no desaparezca al interactuar.
# La primera vez se ejecuta con los valores por defecto.
if ejecutar or "resultado" not in st.session_state:
    st.session_state["resultado"] = {
        "p": p, "n_corridas": n_corridas,
        "df": ejecutar_simulacion(p),
        "validacion": validar(p, n_corridas),
    }

res = st.session_state["resultado"]
p_usado, df, validacion = res["p"], res["df"], res["validacion"]

# ----------------- FILTRADO METODOLÓGICO SOLICITADO POR EL PROFESOR -----------------
# Se descarta el Día 1 para el Reactivo (empieza Día 2) y Días 1 al 6 para Utilidad (empieza Día 7)
condicion_base = df["estrategia"] == "Base"
condicion_reactivo = (df["estrategia"] == "Reactivo") & (df["dia"] >= 2)
condicion_utilidad = (df["estrategia"] == "Utilidad") & (df["dia"] >= 7)

df_filtrado = df[condicion_base | condicion_reactivo | condicion_utilidad].copy()

# Recalculamos acumulados del DataFrame filtrado para gráficos coherentes
for estr in ESTRATEGIAS:
    mask = df_filtrado["estrategia"] == estr
    if mask.any():
        df_filtrado.loc[mask, "utilidad_acumulada"] = df_filtrado.loc[mask, "utilidad_neta"].cumsum()

# Calculamos métricas y ganador sobre el DataFrame filtrado
metricas = calcular_metricas_finales(df_filtrado)
ganador = estrategia_ganadora(metricas)

if p != p_usado or n_corridas != res["n_corridas"]:
    st.warning("Cambiaste parámetros: los resultados de abajo son de la configuración "
               "anterior. Pulsa **🚀 Ejecutar simulación** para actualizarlos.")

# ------------------------------- KPIs -------------------------------
st.subheader(f"Resultados — {p_usado.dias} días, semilla {p_usado.seed}")
mejor_utilidad = metricas["Utilidad neta acumulada"].max()
menor_desperdicio = metricas["Desperdicio total"].idxmin()
mejor_servicio = metricas["Nivel de servicio (%)"].idxmax()

k1, k2, k3, k4 = st.columns(4)
k1.metric("🏆 Estrategia ganadora", ganador)
k2.metric("Mayor utilidad acumulada", f"S/ {mejor_utilidad:,.0f}",
          delta=f"{mejor_utilidad - metricas.loc['Base', 'Utilidad neta acumulada']:,.0f} vs Base",
          help="La estrategia ganadora es la de mayor utilidad neta acumulada.")

k3.metric("Menor desperdicio", menor_desperdicio,
          delta=f"{metricas.loc[menor_desperdicio, 'Desperdicio total']:,.0f} unidades",
          delta_color="off")
k4.metric("Mayor nivel de servicio", mejor_servicio,
          delta=f"{metricas.loc[mejor_servicio, 'Nivel de servicio (%)']:.1f}%",
          delta_color="off")

# ------------------------- Tabla comparativa -------------------------
st.subheader("📊 Tabla comparativa")
tabla = metricas.copy()
tabla.insert(0, "Estrategia", [f"🏆 {e}" if e == ganador else e for e in tabla.index])
tabla = tabla[["Estrategia", "Utilidad neta acumulada", "Desperdicio total",
               "Ventas perdidas", "Nivel de servicio (%)", "Producción total",
               "Unidades vendidas"]].reset_index(drop=True)


def resaltar_ganador(fila):
    estilo = "background-color: #d8f3dc; color: #1b4332; font-weight: 600"
    return [estilo if "🏆" in fila["Estrategia"] else "" for _ in fila]


st.dataframe(
    tabla.style.apply(resaltar_ganador, axis=1).format({
        "Utilidad neta acumulada": "S/ {:,.0f}", "Desperdicio total": "{:,.0f}",
        "Ventas perdidas": "{:,.0f}", "Nivel de servicio (%)": "{:.1f}%",
        "Producción total": "{:,.0f}", "Unidades vendidas": "{:,.0f}"}),
    hide_index=True, width="stretch")
st.caption("Las tres estrategias enfrentan exactamente la misma demanda. "
           "Gana la de mayor utilidad neta acumulada (Reactivo desde Día 2, Utilidad desde Día 7).")

# ------------------------------ Gráficos ------------------------------
g1, g2 = st.columns(2)

with g1:
    fig1 = go.Figure()
    for estrategia in ESTRATEGIAS:
        d = df_filtrado[df_filtrado["estrategia"] == estrategia]
        fig1.add_trace(go.Scatter(x=d["dia"], y=d["utilidad_acumulada"], mode="lines",
                                  name=estrategia,
                                  line=dict(color=COLORES[estrategia], width=3)))
    fig1.update_layout(title="Utilidad acumulada por día", xaxis_title="Día",
                       yaxis_title="Utilidad acumulada (S/)", hovermode="x unified",
                       legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig1, width="stretch")

with g2:
    elegida = st.radio("Estrategia a mostrar", ESTRATEGIAS,
                       index=ESTRATEGIAS.index("Utilidad"), horizontal=True)
    d = df_filtrado[df_filtrado["estrategia"] == elegida]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=d["dia"], y=d["demanda"], mode="lines+markers",
                              name="Demanda real", line=dict(color="#264653")))
    fig2.add_trace(go.Scatter(x=d["dia"], y=d["produccion"], mode="lines+markers",
                              name=f"Producción ({elegida})",
                              line=dict(color=COLORES[elegida], dash="dash")))
    fig2.update_layout(title=f"Demanda real vs producción — {elegida}",
                       xaxis_title="Día", yaxis_title="Unidades",
                       hovermode="x unified", legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig2, width="stretch")

fig3 = go.Figure()
fig3.add_trace(go.Bar(x=list(ESTRATEGIAS), y=metricas["Desperdicio total"],
                      name="Desperdicio total",
                      marker_color=[COLORES[e] for e in ESTRATEGIAS],
                      text=metricas["Desperdicio total"], textposition="outside"))
fig3.update_layout(title="Desperdicio total por estrategia", yaxis_title="Unidades",
                   showlegend=False)
st.plotly_chart(fig3, width="stretch")

# --------------------- Explicación de cada estrategia ---------------------
with st.expander("🧠 ¿Cómo decide cada estrategia?"):
    st.markdown(f"""
**Base** — Siempre produce la misma cantidad ({p_usado.produccion_base} unidades por día).

**Reactivo simple** — Responde al comportamiento del día anterior mediante reglas IF-THEN (evaluado a partir del Día 2):
- Si vendió **≥ {UMBRAL_SUBIR:.0%}** de lo producido → produce **{AJUSTE_REACTIVO:.0%} más**.
- Si vendió **≤ {UMBRAL_BAJAR:.0%}** de lo producido → produce **{AJUSTE_REACTIVO:.0%} menos**.
- En otro caso → mantiene la producción.
- Límites: {p_usado.min_produccion} a {p_usado.max_produccion} unidades.

**Utilidad** — Evalúa varias cantidades posibles (de {p_usado.min_produccion} a
{p_usado.max_produccion}, de {PASO_CANDIDATOS} en {PASO_CANDIDATOS}) frente a las demandas de
los últimos {VENTANA_HISTORIAL} días, calcula la utilidad esperada de cada una y selecciona
aquella que **maximiza la utilidad esperada** (evaluado a partir del Día 7).

**Utilidad del día** = ventas × precio − producción × costo de producción
− desperdicio × costo de desperdicio − ventas perdidas × penalización.
""")

# ---------------------- Validación con varias semillas ----------------------
with st.expander(f"🔁 Validación con {res['n_corridas']} semillas distintas"):
    st.caption("La misma comparación repetida con semillas consecutivas a partir de la "
               "elegida. Sirve para ver si el ganador depende de una sola secuencia de demanda.")
    st.dataframe(validacion.style.format({
        "Utilidad media": "S/ {:,.0f}", "Desviación": "S/ {:,.0f}",
        "Mínima": "S/ {:,.0f}", "Máxima": "S/ {:,.0f}",
        "Corridas ganadas (%)": "{:.1f}%"}), width="stretch")

with st.expander("📅 Ver datos diarios"):
    st.dataframe(df_filtrado, hide_index=True, width="stretch")
