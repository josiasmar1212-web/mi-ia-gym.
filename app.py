import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- CONFIGURACIÓN DE ESCENA PROFESIONAL ---
st.set_page_config(page_title="MorphAI Pro", page_icon="🧬", layout="wide")

# CSS Avanzado para Estilo Dark Premium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Orbitron:wght@700&display=swap');
    
    .stApp { background-color: #050505; color: #FFFFFF; }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff; text-align: center; font-size: 2.8rem;
        letter-spacing: 10px; margin-bottom: 0px;
        text-shadow: 0px 0px 20px rgba(0, 212, 255, 0.4);
    }

    /* Tarjetas Estilo Glassmorphism */
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    .plan-header {
        color: #00d4ff; font-weight: bold; font-size: 0.9rem;
        text-transform: uppercase; letter-spacing: 2px;
    }

    /* Botones Pro */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.8em;
        background: linear-gradient(90deg, #00d4ff, #0080ff);
        color: #000; font-weight: bold; border: none;
        transition: 0.4s; font-family: 'Inter', sans-serif;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0px 10px 20px rgba(0, 212, 255, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#555; margin-bottom:40px;">FUTURE OF PHYSICAL PERFORMANCE</p>', unsafe_allow_html=True)

# --- GESTIÓN DE DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_historial = conn.read(worksheet="DATOS", ttl=0)
except:
    df_historial = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps"])

if 'plan_ia' not in st.session_state:
    st.session_state['plan_ia'] = "⚠️ NO DATA DETECTED.<br>Configura tu protocolo en PLANIFICAR."

# --- NAVEGACIÓN TÁCTIL ---
tabs = st.tabs(["⚡ SESIÓN", "🧠 CEREBRO", "📈 ANALYTICS", "🧮 1RM"])

with tabs[0]: # SESIÓN
    st.markdown(f"""
    <div class="metric-card">
        <p class="plan-header">📍 Protocolo Activo</p>
        <div style="font-size: 1.1rem; line-height: 1.6;">{st.session_state['plan_ia']}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📝 REGISTRAR RENDIMIENTO"):
        with st.form("pro_form", clear_on_submit=True):
            col1, col2 = st.columns([2, 1])
            ejer = col1.text_input("Ejercicio", placeholder="Ej: Press Militar")
            peso = col2.number_input("Kg", 0.0, 500.0, 60.0)
            reps = st.slider("Repeticiones", 1, 30, 10)
            if st.form_submit_button("SINCRONIZAR SERIE"):
                st.toast("Dato enviado al núcleo 🧬")

with tabs[1]: # CEREBRO (Generador)
    st.markdown("### 🧬 Generador de Morfosis")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("INSTALAR ARNOLD SPLIT"):
            st.session_state['plan_ia'] = "<b>ARNOLD PROTOCOL:</b><br>• Pecho/Espalda<br>• Hombro/Brazo<br>• Pierna"
            st.rerun()
    with c2:
        if st.button("INSTALAR PPL"):
            st.session_state['plan_ia'] = "<b>PUSH PULL LEGS:</b><br>• Empuje<br>• Tracción<br>• Tren Inferior"
            st.rerun()

with tabs[2]: # ANALYTICS
    if not df_historial.empty:
        ejer_sel = st.selectbox("Analizar Evolución", df_historial["Ejercicio"].unique())
        fig = px.line(df_historial[df_historial["Ejercicio"]==ejer_sel], 
                     x="Fecha", y="Peso", markers=True, template="plotly_dark")
        fig.update_traces(line_color='#00d4ff', marker_color='#ffffff')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sin registros detectados en la nube.")

with tabs[3]: # 1RM
    st.markdown("### Calculadora de Potencia")
    px1 = st.number_input("Peso Máximo", 1.0, 500.0, 100.0)
    rx1 = st.number_input("Reps al Fallo", 1, 15, 5)
    rm_calc = px1 * (1 + 0.0333 * rx1)
    st.markdown(f"""<div class="metric-card" style="text-align:center;">
    <h1 style="color:#00d4ff; margin:0;">{round(rm_calc, 1)} KG</h1>
    <p style="color:#666;">CAPACIDAD MÁXIMA TEÓRICA</p></div>""", unsafe_allow_html=True)
