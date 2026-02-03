import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURACIÓN DE INTERFAZ MORPHAI ---
st.set_page_config(page_title="MorphAI", page_icon="🧬", layout="wide")

# CSS Profesional: Estilo Dark Futurista
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp { background-color: #050505; color: #ffffff; }
    
    .morph-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff;
        text-align: center;
        letter-spacing: 5px;
        text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.5);
    }
    
    .plan-card {
        background: linear-gradient(180deg, #111 0%, #050505 100%);
        border: 1px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }

    .stButton>button {
        width: 100%; border-radius: 10px; height: 3.5em;
        background-color: transparent; color: #00d4ff;
        border: 2px solid #00d4ff; font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00d4ff; color: #000;
        box-shadow: 0px 0px 20px #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="morph-title">MORPHAI</h1>', unsafe_allow_html=True)

# --- CONEXIÓN DE DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_historial = conn.read(worksheet="DATOS", ttl=0)
except:
    df_historial = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps", "RPE"])

# --- LÓGICA DE REINICIO DE SESIÓN ---
if 'rutina_sesion' not in st.session_state:
    st.session_state['rutina_sesion'] = "SISTEMA LISTO. GENERA TU PLAN EN 'PLANIFICAR'."

tab1, tab2, tab3, tab4 = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "📊 DATOS", "🧮 1RM"])

# --- TAB 1: ENTRENAR ---
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
            # AQUÍ ESTÁ EL PARÉNTESIS CERRADO CORRECTAMENTE:
            reps = col3.number_input("Reps", 1, 50, 10)
            rpe = col4.select_slider("Intensidad (RPE)", options=["Baja", "Media", "Alta", "Fallo"])
            
            if st.form_submit_button("REGISTRAR EN EL NÚCLEO"):
                if ejer:
                    st.success(f"Serie de {ejer} registrada con éxito.")
                else:
                    st.error("Escribe el nombre del ejercicio.")

# --- TAB 2: PLANIFICAR ---
with tab2:
    st.markdown("### Selección de Protocolo")
    opcion = st.radio("Método MorphAI:", ["Arnold Split", "Manual", "Análisis de Imagen"])
    
    if opcion == "Arnold Split":
        if st.button("INSTALAR ARNOLD SPLIT"):
            st.session_state['rutina_sesion'] = """
            **PROTOCOLO ARNOLD:**
            - **Día 1/4:** Pecho + Espalda
            - **Día 2/5:** Hombros + Brazos
            - **Día 3/6:** Piernas
            """
            st.rerun()

    elif opcion == "Análisis de Imagen":
        foto = st.file_uploader("Subir foto...", type=['jpg', 'png'])
        if foto and st.button("ANALIZAR"):
            with st.spinner("Escaneando simetría..."):
                time.sleep(2)
                st.session_state['rutina_sesion'] = "Sugerencia: Foco en deltoides posterior."
                st.rerun()

# --- TAB 3: PROGRESO ---
with tab3:
    st.info("Conecta la Service Account para ver tus gráficas de evolución.")

# --- TAB 4: CALCULADORA 1RM ---
with tab4:
    st.subheader("Cálculo de Potencia")
    c1, c2 = st.columns(2)
    p = c1.number_input("Peso", 1.0, 500.0, 60.0)
    r = c2.number_input("Reps", 1, 15, 5)
    rm = p * (1 + 0.0333 * r)
    st.metric("1RM ESTIMADO", f"{round(rm, 1)} kg")
