import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURACIÓN DE PÁGINA Y DISEÑO OSCURO
st.set_page_config(page_title="GymAnalyst Pro", page_icon="🐗", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #FFD700; color: black; font-weight: bold; }
    h1 { color: #FFD700; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐗 GYMANALYST PRO")
st.write("---")

# CONEXIÓN A BASE DE DATOS
url = "TU_URL_DE_GOOGLE_SHEETS_AQUÍ" # <--- PEGA AQUÍ TU LINK DE GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# ENTRADA DE ENTRENAMIENTO
st.subheader("🏋️ Registro de Sesión")
col1, col2 = st.columns(2)

with col1:
    ejercicio = st.selectbox("Músculo / Ejercicio", ["Press Militar", "Sentadilla", "Press Banca", "Prensa", "Laterales"])
    p_ant = st.number_input("Peso Anterior (kg)", value=60.0)
with col2:
    p_act = st.number_input("Peso Hoy (kg)", value=60.0)

if st.button("ANALIZAR Y GUARDAR EN LA NUBE"):
    mejora = ((p_act - p_ant) / p_ant) * 100
    
    # Lógica de Medallas
    if 5 <= mejora <= 7:
        st.balloons()
        st.success(f"🏆 ¡MOMENTO ÉPICO! +{mejora:.1f}%")
    elif mejora > 7:
        st.warning(f"🐗🔥 NIVEL BESTIA: +{mejora:.1f}%")
    else:
        st.info(f"Progreso: +{mejora:.1f}%")

    # Aquí la IA enviaría los datos a Google Sheets automáticamente
    st.write("Datos listos para sincronizar...")
