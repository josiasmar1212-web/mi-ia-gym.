import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import random

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="MorphAI Ultimate", page_icon="🧬", layout="wide")

# Biblioteca Gigante de Ejercicios
BIBLIOTECA_EJERCICIOS = {
    "Pecho": ["Press Banca Barra", "Press Inclinado Mancuernas", "Aperturas Polea", "Fondos", "Push-ups", "Cruce de Poleas"],
    "Espalda": ["Dominadas", "Remo con Barra", "Jalón al Pecho", "Remo en Polea Baja", "Peso Muerto", "Pull-over Polea"],
    "Pierna": ["Sentadilla", "Prensa", "Extensiones", "Curl Femoral", "Zancadas", "Gemelos", "Hack Squat"],
    "Hombro": ["Press Militar", "Elevaciones Laterales", "Pájaros", "Press Arnold", "Facepull", "Remo al mentón"],
    "Brazos": ["Curl Bíceps Barra", "Martillo", "Extensión Tríceps", "Press Francés", "Curl Concentrado", "Dips"],
    "Core": ["Plancha", "Crunch Abdominal", "Elevación de Piernas", "Rueda Abdominal", "Lumbar"]
}

# --- ESTILO CSS MORPHAI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00d4ff; text-align: center; letter-spacing: 8px; margin-bottom: 0px; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #888; border-radius: 10px; padding: 10px; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #00d4ff; background-color: rgba(0, 212, 255, 0.1); }
    .timer-container { background: #111; padding: 20px; border-radius: 20px; border: 1px solid #00d4ff; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN ---
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "⚠️ Ve a PLANIFICAR para activar un protocolo."
if 'historial_sesion' not in st.session_state:
    st.session_state['historial_sesion'] = []

# --- CONEXIÓN GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_global = conn.read(worksheet="DATOS", ttl=0)
except:
    df_global = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps"])

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🧬 MODALIDAD")
    modo = st.radio("Entrenamiento:", ["🏋️ Gym/Fuerza", "🏃 Running", "🥊 Contacto"])
    st.divider()
    
    # --- TEMPORIZADOR DE DESCANSO ---
    st.markdown("### ⏱️ DESCANSO")
    t_descanso = st.number_input("Segundos:", 30, 300, 90, 30)
    if st.button("▶️ INICIAR TIMER"):
        placeholder = st.empty()
        for i in range(t_descanso, 0, -1):
            placeholder.metric("Tiempo restante", f"{i}s")
            time.sleep(1)
        placeholder.success("🔥 ¡DALE OTRA VEZ!")
        st.balloons()

# --- NAVEGACIÓN PRINCIPAL ---
tabs = st.tabs(["⚡ SESIÓN", "🧠 PLANIFICAR", "📊 ANALYTICS"])

# --- TAB 1: SESIÓN ---
with tabs[0]:
    st.markdown(f"""<div style="background:#111; padding:15px; border-radius:15px; border-left: 5px solid #00d4ff; margin-bottom:20px;">
        <small style="color:#00d4ff;">PROTOCOLO ACTUAL</small><br><b>{st.session_state['plan_activo']}</b>
    </div>""", unsafe_allow_html=True)

    if modo == "🏋️ Gym/Fuerza":
        with st.form("registro_pesas", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            grupo = col1.selectbox("Grupo Muscular", list(BIBLIOTECA_EJERCICIOS.keys()))
            ejer = col2.selectbox("Ejercicio", BIBLIOTECA_EJERCICIOS[grupo])
            
            c3, c4 = st.columns(2)
            p = c3.number_input("Peso (kg)", 0.0, 500.0, 40.0)
            r = c4.number_input("Reps", 1, 50, 10)
            if st.form_submit_button("REGISTRAR SERIE"):
                nueva_serie = {"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": ejer, "Peso": p, "Reps": r}
                st.session_state['historial_sesion'].append(nueva
