import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import random

# --- CONFIGURACIÓN MORPHAI ---
st.set_page_config(page_title="MorphAI Pro", page_icon="🧬", layout="wide")

# Frases Motivadoras MorphAI
frases = [
    "La disciplina es el puente entre las metas y el logro.",
    "No te detengas cuando estés cansado, detente cuando hayas terminado.",
    "Tu cuerpo es el único lugar que tienes para vivir. Cuídalo.",
    "El dolor es debilidad abandonando el cuerpo.",
    "La morfosis no ocurre por suerte, ocurre por esfuerzo."
]

# Estilo MorphAI Pro
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
    .stApp {{ background-color: #050505; color: #FFFFFF; }}
    .main-title {{
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff; text-align: center; font-size: 3rem;
        letter-spacing: 10px; margin-bottom: 0px;
        text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.4);
    }}
    .frase-motivadora {{
        text-align: center; color: #888; font-style: italic;
        margin-bottom: 30px; font-size: 1.1rem;
    }}
    .sidebar-content {{ background-color: #111; padding: 20px; border-radius: 10px; }}
    </style>
    <h1 class="main-title">MORPHAI</h1>
    <p class="frase-motivadora">"{random.choice(frases)}"</p>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Opciones a un costado) ---
with st.sidebar:
    st.markdown("### 🧬 ESPECIALIDADES")
    especialidad = st.radio("Elige tu modalidad:", 
                            ["🏋️ Gimnasio / Arnold", "🏃 Running / Resistencia", "🥊 Deportes de Contacto"])
    
    st.divider()
    if especialidad == "🏃 Running / Resistencia":
        st.info("**MODO RUNNER ACTIVO**\nFoco: VO2 Max y Resistencia Aeróbica.")
    elif especialidad == "🥊 Deportes de Contacto":
        st.info("**MODO COMBATE ACTIVO**\nFoco: Explosividad (Plyos) y Cuello/Core.")

# --- DATOS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_historial = conn.read(worksheet="DATOS", ttl=0)
except:
    df_historial = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps"])

# --- NAVEGACIÓN ---
tabs = st.tabs(["⚡ SESIÓN", "🧠 PLANIFICAR", "📊 ANALYTICS"])

with tabs[0]: # SESIÓN
    if especialidad == "🏋️ Gimnasio / Arnold":
        st.subheader("Plan de Fuerza")
        # Aquí va tu código anterior de registro de pesas...
    elif especialidad == "🏃 Running / Resistencia":
        st.subheader("Registro de Carrera")
        c1, c2 = st.columns(2)
        distancia = c1.number_input("Distancia (km)", 0.0, 100.0, 5.0)
        tiempo = c2.text_input("Tiempo (mm:ss)", "25:00")
        if st.button("GUARDAR CARRERA"):
            st.success(f"Carrera de {distancia}km registrada.")
    elif especialidad == "🥊 Deportes de Contacto":
        st.subheader("Entrenamiento de Combate")
        rounds = st.slider("Rounds de Sparring/Saco", 1, 12, 3)
        intensidad = st.select_slider("Intensidad", options=["Técnica", "Sparring suave", "Guerra"])
        if st.button("GUARDAR SESIÓN COMBATE"):
            st.success(f"{rounds} rounds registrados.")

with tabs[1]: # PLANIFICAR
    st.write("### ⚙️ Configurar Protocolo")
    # Mantén aquí tus botones de Arnold Split y PPL

with tabs[2]: # ANALYTICS
    st.write("### 📈 Análisis de Rendimiento")
    if not df_historial.empty:
        ejercicio_grafico = st.selectbox("Selecciona para ver progreso:", df_historial["Ejercicio"].unique())
        df_filtrado = df_historial[df_historial["Ejercicio"] == ejercicio_grafico]
        
        fig = px.line(df_filtrado, x="Fecha", y="Peso", markers=True, 
                     line_shape='spline', template="plotly_dark")
        fig.update_traces(line_color='#00d4ff', marker=dict(size=10, color="white"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos en el Excel para mostrar Analytics aún.")
