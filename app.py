import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import random

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
st.set_page_config(page_title="MorphAI Pro", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff; text-align: center; font-size: 3rem;
        letter-spacing: 10px; margin-bottom: 10px;
        text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.4);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. INICIALIZACIÓN DE MEMORIA ---
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "Arnold Split (Predeterminado)"
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

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<h2 style="color:#00d4ff;">🧬 MORPH CONTROL</h2>', unsafe_allow_html=True)
    segundos = st.slider("Temporizador Descanso:", 30, 180, 90, 30)
    if st.button("INICIAR DESCANSO"):
        placeholder = st.empty()
        for i in range(segundos, 0, -1):
            placeholder.metric("Descansando...", f"{i}s")
            time.sleep(1)
        st.success("¡A POR LA SIGUIENTE!")
        st.balloons()

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "🧠 PROTOCOLOS", "📊 PROGRESO"])

# TAB 1: ENTRENAR (Aquí estaba el error, ahora corregido)
with tabs[0]:
    st.markdown(f'<div class="glass-card"><b>PLAN:</b> {st.session_state["plan_activo"]}</div>', unsafe_allow_html=True)
    
    with st.form("registro_serie", clear_on_submit=True):
        col1, col2 = st.columns(2)
        grupo = col1.selectbox("Músculo", list(BIBLIOTECA.keys()))
        ejer = col2.selectbox("Ejercicio", BIBLIOTECA[grupo])
        
        c1, c2 = st.columns(2)
        peso = c1.number_input("Peso (kg)", 0.0, 500.0, 60.0)
        reps = c2.number_input("Reps", 1, 50, 10)
        
        submitted = st.form_submit_button("GUARDAR SERIE")
        if submitted:
            nueva_serie = {
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Ejercicio": ejer, "Peso": peso, "Reps": reps, "Volumen": peso * reps
            }
            st.session_state['historial_sesion'].append(nueva_serie)
            st.toast(f"{ejer} registrado")

    if st.session_state['historial_sesion']:
        st.markdown("### 📝 Sesión Actual")
        df_hoy = pd.DataFrame(st.session_state['historial_sesion'])
        st.table(df_hoy)
        if st.button("🚀 FINALIZAR Y SINCRONIZAR"):
            st.success("Entrenamiento enviado a la nube.")
            st.session_state['historial_sesion'] = []
            st.rerun()

# TAB 2: PROTOCOLOS
with tabs[1]:
    st.subheader("Seleccionar Estrategia")
    if st.button("ACTIVAR ARNOLD SPLIT"):
        st.session_state['plan_activo'] = "Arnold Split (Antagonistas)"
        st.rerun()
    if st.button("ACTIVAR PUSH/PULL/LEGS"):
        st.session_state['plan_activo'] = "PPL (Frecuencia 2)"
        st.rerun()

# TAB 3: PROGRESO
with tabs[2]:
    if not df_global.empty:
        ejer_sel = st.selectbox("Ejercicio:", df_global["Ejercicio"].unique())
        df_vis = df_global[df_global["Ejercicio"] == ejer_sel]
        fig = px.line(df_vis, x="Fecha", y="Peso", markers=True, template="plotly_dark")
        fig.update_traces(line_color='#00d4ff')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sincroniza tu primera sesión para ver las gráficas.")
