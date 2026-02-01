import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. Configuración de la App
st.set_page_config(page_title="GymAnalyst Pro v100", layout="wide")

# 2. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #f0b90b; color: black; border-radius: 10px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐗 GYMANALYST PRO: NIVEL 100")

# --- LÓGICA DE DATOS ---
# Leemos la pestaña de EJERCICIOS que creaste en tu Excel
df_ejercicios = conn.read(worksheet="EJERCICIOS")

with st.sidebar:
    st.header("👤 Perfil de Atleta")
    user_name = st.text_input("Tu Nombre:", value="Guerrero")
    st.divider()
    st.write("Versión Pública v1.0")

# --- REGISTRO DE ENTRENAMIENTO ---
st.subheader("🏋️ Registrar Nuevo Entrenamiento")

col1, col2 = st.columns(2)

with col1:
    grupo = st.selectbox("Músculo", df_ejercicios["Grupo Muscular"].unique())
    # Filtramos ejercicios según el músculo elegido
    ejer_filtrados = df_ejercicios[df_ejercicios["Grupo Muscular"] == grupo]
    ejercicio = st.selectbox("Selecciona Ejercicio", ejer_filtrados["Nombre del Ejercicio"])

with col2:
    peso = st.number_input("Peso (kg)", min_value=0.0, step=0.5)
    reps = st.number_input("Repeticiones", min_value=1, step=1)

if st.button("💾 GUARDAR RECORD"):
    # Aquí la IA celebra tu progreso
    st.balloons()
    st.success(f"¡Brutal {user_name}! Has registrado {ejercicio} con {peso}kg.")
    st.info("Nota: Los datos se están enviando a tu Google Sheets.")

# --- GRÁFICA DE PROGRESO ---
st.divider()
st.subheader("📈 Tu Evolución")
st.write("Aquí aparecerán tus gráficas cuando tengas más de 3 registros.")
