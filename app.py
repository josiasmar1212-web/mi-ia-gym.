import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- CONFIGURACIÓN MorphAI ---
st.set_page_config(page_title="MorphAI Elite", page_icon="🧬", layout="wide")

# Estilo MorphAI Premium (CSS Limpio)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    .stApp { background-color: #080808; color: #FFFFFF; }
    .main-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-align: center;
        letter-spacing: 5px;
        text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.4);
    }
    .pizarra {
        background: #111;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #222;
        border-left: 5px solid #00d4ff;
    }
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(90deg, #00d4ff, #0080ff);
        color: #000; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)

# --- SISTEMA DE DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_historial = conn.read(worksheet="DATOS", ttl=0)
except:
    # Datos de ejemplo por si falla la conexión
    df_historial = pd.DataFrame([
        {"Fecha": "01/02/2026", "Ejercicio": "Press Banca", "Peso": 60},
        {"Fecha": "02/02/2026", "Ejercicio": "Press Banca", "Peso": 62.5}
    ])

# --- MEMORIA DEL SISTEMA (Persistencia) ---
if 'plan_ia' not in st.session_state:
    st.session_state['plan_ia'] = "⚠️ NO HAY PLAN CARGADO.<br>Ve a la pestaña 🧠 PLANIFICAR."

tab1, tab2, tab3, tab4 = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "📊 PROGRESO", "🧮 1RM"])

# --- TAB 1: ENTRENAR ---
with tab1:
    # Aquí estaba el error de la f-string, ya está arreglado:
    st.markdown(f"""
    <div class="pizarra">
        <p style="color: #00d4ff; margin-bottom: 5px;">📍 PLAN ACTUAL:</p>
        <div style="font-size: 1.1rem; line-height: 1.4;">
            {st.session_state['plan_ia']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📝 Registrar Serie")
    with st.form("form_final", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        ejer = c1.text_input("Ejercicio")
        peso = c2.number_input("Kg", 0.0, 500.0, 40.0)
        reps = st.number_input("Reps", 1, 100, 10)
        if st.form_submit_button("GUARDAR EN EL NÚCLEO"):
            st.toast("Serie guardada temporalmente")

# --- TAB 2: PLANIFICAR (Generador) ---
with tab2:
    st.write("### 🧬 Protocolos Disponibles")
    col1, col2 = st.columns(2)
    
    if col1.button("INSTALAR ARNOLD SPLIT"):
        st.session_state['plan_ia'] = "<b>ARNOLD SPLIT:</b><br>- L/J: Pecho & Espalda<br>- M/V: Hombros & Brazos<br>- X/S: Piernas"
        st.rerun()
        
    if col2.button("INSTALAR PPL"):
        st.session_state['plan_ia'] = "<b>PUSH/PULL/LEGS:</b><br>- Empuje (Push)<br>- Tracción (Pull)<br>- Pierna (Legs)"
        st.rerun()

# --- TAB 3: PROGRESO (Gráfico que no desaparece) ---
with tab3:
    st.subheader("📈 Análisis de Evolución")
    if not df_historial.empty:
        ejer_sel = st.selectbox("Selecciona Ejercicio", df_historial["Ejercicio"].unique())
        df_plot = df_historial[df_historial["Ejercicio"] == ejer_sel]
        
        # Gráfico Pro de Plotly
        fig = px.line(df_plot, x="Fecha", y="Peso", markers=True, 
                     title=f"Progreso en {ejer_sel}",
                     template="plotly_dark")
        fig.update_traces(line_color='#00d4ff')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Esperando datos para generar gráficas...")

# --- TAB 4: 1RM ---
with tab4:
    st.subheader("Calculadora de Potencia")
    ca, cb = st.columns(2)
    p = ca.number_input("Peso", 1.0, 500.0, 80.0, key="ca")
    r = cb.number_input("Reps", 1, 20, 5, key="cb")
    rm = p * (1 + 0.0333 * r)
    st.metric("1RM ESTIMADO", f"{round(rm, 1)} KG")
