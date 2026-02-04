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
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)

# --- MEMORIA DE SESIÓN (Persistencia) ---
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "⚠️ Ve a PLANIFICAR para activar un protocolo."
if 'historial_sesion' not in st.session_state:
