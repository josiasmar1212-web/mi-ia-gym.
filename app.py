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

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background-color: #1f2937; color: #00d4ff; border: 1px solid #00d4ff;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937; border-radius: 10px; padding: 10px; color: white; font-size: 11px;
    }
    .css-1kyx730 { background-color: #1f2937; border-radius: 15px; padding: 20px; border: 1px solid #333; }
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

# --- INICIALIZAR RUTINA SI NO EXISTE ---
if 'my_routine' not in st.session_state:
    st.session_state['my_routine'] = "Todavía no has definido tu rutina en la pestaña 📝 MANUAL"

st.title("🐗 GYM IA ELITE")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏋️ ENTRENO", "📈 PROGRESO", "📋 IA PLAN", "📝 MANUAL", "⏱️ TIMER"])

# --- TAB 1: REGISTRO + TU RUTINA AL PRINCIPIO ---
with tab1:
    # MOSTRAR LA RUTINA PERSONALIZADA AQUÍ
    st.markdown("### 📅 TU PLAN DE HOY")
    with st.expander("Ver mi rutina guardada", expanded=True):
        st.write(st.session_state['my_routine'])
    
    st.divider()
    
    if df_ejercicios is not None:
        with st.form("reg_form", clear_on_submit=True):
            st.subheader("Registrar Serie")
            f_musculo = st.selectbox("Grupo", df_ejercicios.iloc[:, 0].unique())
            f_ejer = st.selectbox("Ejercicio", df_ejercicios[df_ejercicios.iloc[:, 0] == f_musculo].iloc[:, 1].unique())
            c1, c2 = st.columns(2)
            f_peso = c1.number_input("Peso (kg)", 0.0, 500.0, 20.0)
            f_reps = c2.number_input("Reps", 1, 100, 10)
            f_sentir = st.select_slider("Estado", options=["😴", "⚡", "🔥"])
            
            if st.form_submit_button("GUARDAR EN DIARIO"):
                conn = st.connection("gsheets", type=GSheetsConnection)
                nueva_fila = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": f_ejer, "Peso": f_peso, "Reps": f_reps, "Estado": f_sentir}])
                df_final = pd.concat([df_historial, nueva_fila], ignore_index=True)
                conn.update(worksheet="DATOS", data=df_final)
                st.balloons(); st.success("¡Serie Guardada!"); time.sleep(1); st.rerun()

# --- TAB 4: MANUAL (DONDE ESCRIBES) ---
with tab4:
    st.subheader("📝 Diseñador de Rutina")
    new_routine = st.text_area("Escribe aquí tu plan semanal o diario:", 
                              value=st.session_state['my_routine'], 
                              height=300)
    if st.button("💾 GUARDAR Y MOSTRAR EN INICIO"):
        st.session_state['my_routine'] = new_routine
        st.success("¡Rutina actualizada! Ve a la pestaña 🏋️ ENTRENO para verla.")

# --- TAB 2, 3 y 5 (IGUALES QUE ANTES) ---
with tab2:
    if df_historial is not None and not df_historial.empty:
        ejer_sel = st.selectbox("Análisis:", df_historial["Ejercicio"].unique())
        df_f = df_historial[df_historial["Ejercicio"] == ejer_sel]
        st.plotly_chart(px.line(df_f, x="Fecha", y="Peso", markers=True, template="plotly_dark"), use_container_width=True)

with tab3:
    st.subheader("🤖 Generador IA")
    perfil = st.selectbox("Biotipo", ["Ectomorfo", "Endomorfo", "Mesomorfo"])
    if st.button("GENERAR"):
        st.info("Generando plan basado en biotipo...")
        st.write("- Lunes: Pecho/Tríceps | - Miércoles: Espalda/Bíceps | - Viernes: Pierna")

with tab5:
    seg = st.number_input("Descanso (s)", 30, 300, 90)
    if st.button("EMPEZAR"):
        bar = st.progress(0)
        for i in range(seg): time.sleep(1); bar.progress((i+1)/seg)
        st.warning("¡TIEMPO! 🚀")
