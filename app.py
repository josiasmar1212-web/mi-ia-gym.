
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- CONFIGURACIÓN DE ESCENA ---
st.set_page_config(page_title="MorphAI Elite", page_icon="🧬", layout="wide")

# Estilo MorphAI Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Orbitron:wght@700&display=swap');
    
    .stApp { background-color: #080808; color: #FFFFFF; }
    
    /* Título principal neón */
    .main-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-align: center;
        font-size: 2.5rem;
        letter-spacing: 8px;
        margin-bottom: 0px;
        text-shadow: 0px 0px 20px rgba(0, 212, 255, 0.4);
    }
    
    /* Tarjetas de Rutina Estilo Pizarra */
    .pizarra {
        background: #111111;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #222;
        border-left: 5px solid #00d4ff;
        margin-bottom: 25px;
    }
    
    /* Botones de Acción */
    .stButton>button {
        width: 100%; border-radius: 15px; height: 4em;
        background: linear-gradient(90deg, #00d4ff, #0080ff);
        color: #000; font-weight: bold; border: none;
        font-size: 1.1rem; transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 15px rgba(0, 212, 255, 0.6);
    }

    /* Input Styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #151515 !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#666; font-size: 0.8rem; margin-bottom: 30px;">ADVANCED MORPHOSIS INTERFACE</p>', unsafe_allow_html=True)

# --- SISTEMA DE DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_historial = conn.read(worksheet="DATOS", ttl=0)
except:
    df_historial = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps", "RPE"])

# Inicializar rutina si no existe
if 'plan_ia' not in st.session_state:
    st.session_state['plan_ia'] = "⚠️ NO HAY PLAN CARGADO.<br>Ve a la pestaña 🧠 PLANIFICAR."

# --- NAVEGACIÓN ---
tab1, tab2, tab3, tab4 = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "📊 PROGRESO", "🧮 1RM"])

# --- TAB 1: EL CENTRO DE ENTRENAMIENTO ---
with tab1:
    st.markdown(f"""
    <div class="pizarra">
        <p style="color: #00d4ff; font-weight: bold; margin-bottom: 5px;">📍 TU PLAN ACTIVO</p>
