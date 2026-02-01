import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import plotly.express as px
import time

# 1. CONFIGURACIÓN ESTILO "APP ELITE"
st.set_page_config(page_title="Gym IA Elite", page_icon="🐗", layout="wide")

# CSS para forzar el modo oscuro y botones grandes
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #1f2937; color: #00d4ff; border: 1px solid #00d4ff;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937; border-radius: 10px; padding: 10px; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url_base = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/edit")[0]

@st.cache_data(ttl=5)
def leer_csv(pestana):
    url_csv = f"{url_base}/gviz/tq?tqx=out:csv&sheet={pestana}"
    try:
        response = requests.get(url_csv)
        return pd.read_csv(StringIO(response.text)).dropna(axis=1, how='all') if response.status_code == 200 else None
    except: return None

df_ejercicios = leer_csv("EJERCICIOS")
df_historial = leer_csv("DATOS")

st.title("🐗 GYM IA ELITE")

# --- MENÚ TÁCTIL ---
tab1, tab2, tab3, tab4 = st.tabs(["🏋️ ENTRENAR", "📈 PROGRESO", "📋 RUTINA", "⏱️ TIMER"])

with tab1:
    if df_ejercicios is not None:
        with st.form("reg_form", clear_on_submit=True):
            f_musculo = st.selectbox("Músculo", df_ejercicios.iloc[:, 0].unique())
            f_ejer = st.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
            c1, c2 = st.columns(2)
            f_peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0)
            f_reps = c2.number_input("Reps", 1, 100, 10)
            f_sentir = st.select_slider("Estado", options=["😴", "⚡", "🔥"])
            
            if st.form_submit_button("GUARDAR SERIE"):
                conn = st.connection("gsheets", type=GSheetsConnection)
                nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps, "Estado": f_sentir}])
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                conn.update(worksheet="DATOS", data=df_final)
                st.success("¡Registrado!")
                time.sleep(1); st.rerun()

with tab2:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Análisis de Fuerza:", df_historial["Ejercicio"].unique())
        df_f = df_historial[df_historial["Ejercicio"] == ejer_sel]
        fig = px.line(df_f, x="Fecha", y="Peso", markers=True, template="plotly_dark", color_discrete_sequence=['#00d4ff'])
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Tu Planificación")
    rutina = st.text_area("Editar Rutina:", value=st.session_state.get('r', 'Lunes: Pecho...'), height=250)
    if st.button("GUARDAR PLAN"): st.session_state['r'] = rutina

with tab4:
    seg = st.number_input("Segundos de descanso", 30, 300, 90)
    if st.button("INICIAR CUENTA ATRÁS"):
        bar = st.progress(0)
        for i in range(seg): time.sleep(1); bar.progress((i+1)/seg)
        st.write("¡DALE OTRA VEZ! 🚀")
