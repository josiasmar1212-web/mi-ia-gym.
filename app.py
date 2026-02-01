import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px
import time
import random

# Configuración
st.set_page_config(page_title="Gym Pro Elite", page_icon="🐗", layout="wide")

# --- MOTIVACIÓN ---
frases = [
    "«La fuerza no viene de la capacidad física, sino de una voluntad indomable.» - Gandhi",
    "«Si quieres algo que nunca has tenido, debes estar dispuesto a hacer algo que nunca has hecho.»",
    "«El único lugar donde el éxito viene antes que el trabajo es en el diccionario.»",
    "«No te detengas cuando estés cansado, detente cuando hayas terminado.»",
    "«La disciplina es hacer lo que hay que hacer, incluso cuando no quieres hacerlo.»"
]

# --- CONEXIÓN ---
url_base = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/edit")[0]

@st.cache_data(ttl=5)
def leer_csv(pestana):
    url_csv = f"{url_base}/gviz/tq?tqx=out:csv&sheet={pestana}"
    try:
        response = requests.get(url_csv)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            return df.dropna(axis=1, how='all')
        return None
    except:
        return None

df_ejercicios = leer_csv("EJERCICIOS")
df_historial = leer_csv("DATOS")

# --- INTERFAZ ---
st.title("🐗 GYM COMMAND CENTER")
st.caption(random.choice(frases))

tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Entrenar", "📈 Progreso", "🧮 1RM", "⏱️ Descanso"])

with tab1:
    st.subheader("Registrar Serie")
    if df_ejercicios is not None:
        fecha_sel = st.date_input("Fecha del entreno", datetime.now())
        musculo = st.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
        ejercicio = st.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == musculo].iloc[:, 1].unique())
        
        c1, c2 = st.columns(2)
        peso_reg = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0, 0.5)
        reps_reg = c2.number_input("Reps", 1, 100, 10)

        if st.button("💾 GUARDAR ENTRENAMIENTO"):
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                nueva_fila = pd.DataFrame([{"Fecha": fecha_sel.strftime("%d/%m/%Y"), 
                                            "Ejercicio": ejercicio, "Peso": peso_reg, "Reps": reps_reg}])
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                conn.update(worksheet="DATOS", data=df_final)
                st.balloons()
                st.success(f"¡{ejercicio} guardado!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:
    if df_historial is not None and not df_historial.empty:
        ejer_graf = st.selectbox("Analizar progreso de:", df_historial["Ejercicio"].unique())
        fig = px.line(df_historial[df_historial["Ejercicio"] == ejer_graf], 
                     x="Fecha", y="Peso", markers=True, title=f"Evolución {ejer_graf}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Registra datos para ver tu evolución.")

with tab3:
    st.subheader("Calculadora 1RM")
    p = st.number_input("Peso levantado", 1.0, 500.0, 60.0)
    r = st.number_input("Reps hechas", 1, 20, 5)
    one_rm = p * (1 + r/30)
    st.metric("Tu 1RM Estimado", f"{round(one_rm, 1)} kg")
    st.info("RPE: Recuerda que tu 1RM varía según tu cansancio diario.")

with tab4:
    st.subheader("⏱️ Temporizador de Descanso")
    segundos = st.slider("Segundos de descanso", 30, 180, 90, step=30)
    if st.button(f"INICIAR {segundos}s"):
        barra = st.progress(0)
        for i in range(segundos):
            time.sleep(1)
            barra.progress((i + 1) / segundos)
        st.write("🔔 ¡TIEMPO! A por la siguiente serie.")
        st.balloons()
