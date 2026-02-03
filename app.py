import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import random

# --- CONFIGURACIÓN MorphAI (Sin jabalí, solo tecnología) ---
st.set_page_config(page_title="MorphAI", page_icon="🧬", layout="wide")

# CSS para estilo minimalista y profesional
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #ffffff; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #00d4ff; color: #000000; font-weight: 800; border: none;
    }
    .routine-card {
        background-color: #111111; border-radius: 12px; padding: 20px;
        border: 1px solid #00d4ff; margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #050505; }
    .stTabs [data-baseweb="tab"] { color: #888; font-weight: 600; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧬 MorphAI")
st.caption("Sistema de Transformación Física Asistida por IA")

# --- LÓGICA DE REINICIO (Si cierras o refrescas, esto se limpia) ---
if 'plan' not in st.session_state:
    st.session_state['plan'] = "Esperando configuración de MorphAI..."

tab1, tab2, tab3, tab4 = st.tabs(["🔥 ENTRENAR", "📋 PLANIFICAR", "📈 PROGRESO", "🧮 1RM"])

# --- TAB 1: ENTRENAR (Pestaña Principal) ---
with tab1:
    st.markdown(f"""
    <div class="routine-card">
        <small style='color: #00d4ff;'>PLAN ACTIVO</small>
        <p style='font-family: monospace;'>{st.session_state['plan']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 REGISTRAR SERIE"):
        with st.form("registro", clear_on_submit=True):
            ejercicio = st.text_input("Ejercicio", placeholder="Ej: Press Banca")
            c1, c2 = st.columns(2)
            peso = c1.number_input("Kg", 0.0, 500.0, 20.0)
            reps = c2.number_input("Reps", 1, 50, 10)
            if st.form_submit_button("GUARDAR EN HISTORIAL"):
                st.success("Dato guardado localmente")

# --- TAB 2: PLANIFICAR (Tu elección: Arnold Split) ---
with tab2:
    mode = st.radio("Método de entrada", ["🤖 IA Arnold Split", "📸 Análisis Visual (Foto)", "📝 Manual"])
    
    if mode == "🤖 IA Arnold Split":
        st.write("El Arnold Split es el sistema de volumen más efectivo para estética.")
        if st.button("GENERAR MORFOSIS: ARNOLD SPLIT"):
            st.session_state['plan'] = """
            **ARNOLD SPLIT SELECCIONADO:**
            - Día 1: Pecho / Espalda (Super-series)
            - Día 2: Hombro / Brazo (Bíceps y Tríceps)
            - Día 3: Pierna (Foco Cuádriceps y Femoral)
            - Repetir ciclo 2 veces por semana.
            """
            st.success("Rutina cargada. Ve a ENTRENAR.")

    elif mode == "📸 Análisis Visual (Foto)":
        st.write("Sube una foto para que la IA identifique debilidades musculares.")
        foto = st.file_uploader("Cargar imagen...", type=["jpg", "png"])
        if foto and st.button("ANALIZAR"):
