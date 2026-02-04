import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import random

# --- 1. CONFIGURACIÓN Y ESTÉTICA PREMIUM ---
st.set_page_config(page_title="MorphAI Ultimate", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff; text-align: center; font-size: 3.5rem;
        letter-spacing: 12px; margin-bottom: 0px;
        text-shadow: 0px 0px 20px rgba(0, 212, 255, 0.4);
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px; padding: 25px;
        backdrop-filter: blur(10px); margin-bottom: 25px;
    }
    
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.8em;
        background: linear-gradient(90deg, #00d4ff, #0080ff);
        color: #000; font-weight: bold; border: none; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 0px 20px #00d4ff; }
    </style>
""", unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE MEMORIA (Blindada contra errores) ---
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "No configurado"

if 'historial_sesion' not in st.session_state:
    st.session_state['historial_sesion'] = []

BIBLIOTECA = {
    "Pecho": ["Press Banca", "Press Inclinado", "Aperturas", "Fondos"],
    "Espalda": ["Dominadas", "Remo Barra", "Jalón Pecho", "Peso Muerto"],
    "Pierna": ["Sentadilla", "Prensa", "Extensiones", "Curl Femoral"],
    "Hombro": ["Press Militar", "Laterales", "Pájaros"],
    "Brazos": ["Curl Bíceps", "Tríceps Polea", "Martillo"]
}

# --- 3. CONEXIÓN A DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_global = conn.read(worksheet="DATOS", ttl=0)
except Exception:
    df_global = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps", "Volumen"])

# --- 4. SIDEBAR: CONTROL DE MISIÓN ---
with st.sidebar:
    st.markdown('<h2 style="color:#00d4ff;">🧬 MORPH CONTROL</h2>', unsafe_allow_html=True)
    modo = st.selectbox("Especialidad:", ["🏋️ Fuerza/Hipertrofia", "🏃 Cardio/Resistencia", "🥊 Combate"])
    
    st.divider()
    st.markdown("### ⏱️ CRONÓMETRO DE DESCANSO")
    segundos = st.slider("Ajustar descanso:", 30, 300, 90, 30)
    if st.button("INICIAR CUENTA ATRÁS"):
        bar = st.progress(100)
        for i in range(segundos, 0, -1):
            time.sleep(1)
            bar.progress(int((i/segundos)*100))
        st.success("🔥 ¡SIGUIENTE SERIE!")
        st.balloons()

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; color:#555;">{datetime.now().strftime("%A, %d %B %Y")}</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAMIENTO", "🧠 PROTOCOLOS", "📊 ANALYTICS", "🥗 NUTRICIÓN"])

# TAB 1: SESIÓN ACTIVA
with tabs[0]:
    st.markdown(f"""<div class="glass-card">
        <p style="color:#00d4ff; margin:0;">MODO: {modo}</p>
        <h3 style="margin:0;">{st.session_state['plan_activo']}</h3>
    </div>""", unsafe_allow_html=True)
    
    with st.form("registro_pro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        grupo = col1.selectbox("Músculo", list(BIBLIOTECA.keys()))
        ejer = col2.selectbox("Ejercicio", BIBLIOTECA[grupo])
        
        c1, c2, c3 = st.columns(3)
        p = c1.number_input("Peso (kg)", 0.0, 500.0, 60.0)
        r = c2.number_input("Reps", 1, 100, 10)
        rpe = c3.select_slider("Esfuerzo (RPE)", options=range(5, 11), value=8)
        
        if st.
