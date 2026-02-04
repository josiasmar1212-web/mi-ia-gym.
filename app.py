import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import random

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="MorphAI Omni-Sport", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title {
        font-family: 'Orbitron', sans-serif;
        color: #00d4ff; text-align: center; font-size: 3rem;
        letter-spacing: 10px; margin-bottom: 0px;
        text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.4);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. BIBLIOTECAS Y MEMORIA ---
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "Arnold Split (Predeterminado)"
if 'historial_sesion' not in st.session_state:
    st.session_state['historial_sesion'] = []

BIBLIOTECA_GYM = {
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
except:
    df_global = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps", "Volumen", "Tipo"])

# --- 4. SIDEBAR (MODALIDADES Y TIMER) ---
with st.sidebar:
    st.markdown('<h2 style="color:#00d4ff;">🧬 MODALIDAD</h2>', unsafe_allow_html=True)
    especialidad = st.radio("Disciplina:", ["🏋️ Gym/Pesas", "🏃 Running/Resistencia", "🥊 Deporte de Contacto"])
    
    st.divider()
    st.markdown("### ⏱️ REST TIMER")
    segundos = st.number_input("Segundos:", 30, 300, 90, 30)
    if st.button("INICIAR DESCANSO"):
        placeholder = st.empty()
        for i in range(segundos, 0, -1):
            placeholder.metric("Descansando...", f"{i}s")
            time.sleep(1)
        st.success("🔥 ¡GO!")
        st.balloons()

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR (MULTIDISCIPLINA) ---
with tabs[0]:
    st.markdown(f'<div class="glass-card"><b>MODO ACTIVO:</b> {especialidad}</div>', unsafe_allow_html=True)

    if especialidad == "🏋️ Gym/Pesas":
        with st.form("gym_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            grupo = c1.selectbox("Músculo", list(BIBLIOTECA_GYM.keys()))
            ejer = c2.selectbox("Ejercicio", BIBLIOTECA_GYM[grupo])
            c3, c4 = st.columns(2)
            p = c3.number_input("Peso (kg)", 0.0, 500.0, 60.0)
            r = c4.number_input("Reps", 1, 50, 10)
            if st.form_submit_button("REGISTRAR SERIE"):
                st.session_state['historial_sesion'].append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": ejer, "Dato": f"{p}kg x {r}", "Volumen": p*r, "Tipo": "Gym"})
                st.toast("Serie guardada")

    elif especialidad == "🏃 Running/Resistencia":
        with st.form("run_form", clear_on_submit=True):
            dist = st.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            tiempo = st.text_input("Tiempo (HH:MM:SS)", "00:25:00")
            if st.form_submit_button("REGISTRAR CARRERA"):
                st.session_state['historial_sesion'].append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": "Carrera", "Dato": f"{dist}km en {tiempo}", "Volumen": dist, "Tipo": "Run"})
                st.toast("Carrera guardada")

    elif especialidad == "🥊 Deporte de Contacto":
        with st.form("combat_form", clear_on_submit=True):
            rounds = st.slider("Rounds", 1, 15, 3)
            tipo_c = st.selectbox("Tipo", ["Sparring", "Saco", "Manoplas", "Técnica"])
            if st.form_submit_button("REGISTRAR COMBATE"):
                st.session_state['historial_sesion'].append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": f"Combate ({tipo_c})", "Dato": f"{rounds} rounds", "Volumen": rounds, "Tipo": "Combat"})
                st.toast("Sesión de contacto guardada")

    # Resumen y Sincronización
    if st.session_state['historial_sesion']:
        st.write("### 📝 Sesión de hoy")
        st.dataframe(pd.DataFrame(st.session_state['historial_sesion']), use_container_width=True)
        if st.button("🚀 FINALIZAR Y SUBIR"):
            st.success("Entrenamiento enviado a la nube (Simulado).")
            st.session_state['historial_sesion'] = []
            st.rerun()

# --- TAB 2: PLANIFICAR ---
with tabs[1]:
    st.subheader("Configurar Protocolo IA")
    col1, col2 = st.columns(2)
    if col1.button("ARNOLD SPLIT"):
        st.session_state['plan_activo'] = "Arnold Split (Antagonistas)"
        st.rerun()
    if col2.button("PUSH PULL LEGS"):
        st.session_state['plan_activo'] = "PPL (Frecuencia 2)"
        st.rerun()

# --- TAB 3: ANALYTICS ---
with tabs[2]:
    st.subheader("Evolución del Rendimiento")
    if not df_global.empty:
        ejer_sel = st.selectbox("Filtrar por Ejercicio/Actividad:", df_global["Ejercicio"].unique())
        fig = px.line(df_global[df_global["Ejercicio"] == ejer_sel], x="Fecha", y="Peso", markers=True, template="plotly_dark")
        fig.update_traces(line_color='#00d4ff')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sincroniza datos para ver tus gráficas de progreso.")

# --- TAB 4: CALCULADORA 1RM ---
with tabs[3]:
    st.subheader("Cálculo de Fuerza Máxima (1RM)")
    col_p, col_r = st.columns(2)
    peso_rm = col_p.number_input("Peso levantado (kg)", 1.0, 500.0, 80.0)
    reps_rm = col_r.number_input("Repeticiones realizadas", 1, 12, 5)
    # Fórmula de Epley
    one_rm = peso_rm * (1 + 0.0333 * reps_rm)
    
    st.markdown(f"""
    <div style="background: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; padding: 30px; border-radius: 20px; text-align: center;">
        <h1 style="color: #00d4ff; margin: 0;">{round(one_rm, 1)} kg</h1>
        <p style="color: #ccc;">TU 1RM ESTIMADO</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("### 📊 Porcentajes de Carga")
    c1, c2, c3 = st.columns(3)
    c1.metric("90% (Fuerza)", f"{round(one_rm*0.9, 1)} kg")
    c2.metric("80% (Hipertrofia)", f"{round(one_rm*0.8, 1)} kg")
    c3.metric("70% (Resistencia)", f"{round(one_rm*0.7, 1)} kg")
