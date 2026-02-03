import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURACIÓN DE INTERFAZ MORPHAI ---
st.set_page_config(page_title="MorphAI", page_icon="🧬", layout="wide")

# CSS Profesional: Estilo Dark Futurista (Sin rastro del jabalí)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Títulos estilo MorphAI */
    .morph-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-align: center;
        letter-spacing: 5px;
        text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.5);
    }
    
    /* Tarjetas de Plan Activo */
    .plan-card {
        background: linear-gradient(180deg, #111 0%, #050505 100%);
        border: 1px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0px 0px 20px rgba(0, 212, 255, 0.1);
    }

    /* Botones Neón */
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.5em;
        background-color: transparent; color: #00d4ff;
        border: 2px solid #00d4ff; font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00d4ff; color: #000;
        box-shadow: 0px 0px 20px #00d4ff;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111; border-radius: 8px 8px 0 0; padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown('<h1 class="morph-title">MORPHAI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#555;">SISTEMA INTEGRADO DE MORFOSIS FÍSICA</p>', unsafe_allow_html=True)

# --- CONEXIÓN DE DATOS (Manejador de Errores) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_historial = conn.read(worksheet="DATOS", ttl=0)
except:
    df_historial = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps", "RPE"])

# --- LÓGICA DE REINICIO DE SESIÓN ---
# En Streamlit, la sesión se reinicia al refrescar. 
if 'rutina_sesion' not in st.session_state:
    st.session_state['rutina_sesion'] = "SISTEMA LISTO. GENERA TU PLAN EN 'PLANIFICAR'."

# --- NAVEGACIÓN ---
tab1, tab2, tab3, tab4 = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "📊 DATOS", "🧮 1RM"])

# --- TAB 1: ENTRENAR (EL CORAZÓN DE LA APP) ---
with tab1:
    st.markdown('<div class="plan-card">', unsafe_allow_html=True)
    st.subheader("Plan de Operaciones:")
    st.markdown(st.session_state['rutina_sesion'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.expander("📝 REGISTRAR SERIE"):
        with st.form("form_registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            ejer = col1.text_input("Ejercicio", placeholder="Ej: Press Arnold")
            peso = col2.number_input("Peso (kg)", 0.0, 500.0, 20.0, step=0.5)
            
            col3, col4 = st.columns(2)
            reps = col3.number_input("Reps", 1, 50, 10
