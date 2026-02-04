import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="MorphAI Ultimate", page_icon="🧬", layout="wide")

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
    .rm-display {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff; padding: 30px; border-radius: 20px; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. ESTADO DE SESIÓN ---
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "Arnold Split"
if 'historial_sesion' not in st.session_state:
    st.session_state['historial_sesion'] = []
if 'records_personales' not in st.session_state:
    st.session_state['records_personales'] = {"Press Banca": 100, "Sentadilla": 140}

BIBLIOTECA_GYM = {
    "Pecho": ["Press Banca", "Press Inclinado", "Aperturas"],
    "Espalda": ["Dominadas", "Remo Barra", "Jalón Pecho"],
    "Pierna": ["Sentadilla", "Prensa", "Peso Muerto"],
    "Hombro/Brazos": ["Press Militar", "Curl Bíceps", "Tríceps"]
}

# --- 3. DATOS Y CONEXIÓN ---
# Datos de ejemplo para que el gráfico no aparezca vacío
data_ejemplo = {
    "Fecha": ["01/02/2026", "02/02/2026", "03/02/2026", "04/02/2026"],
    "Ejercicio": ["Press Banca", "Press Banca", "Running", "Sentadilla"],
    "Valor": [80, 85, 5, 120]
}
df_visual = pd.DataFrame(data_ejemplo)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<h2 style="color:#00d4ff;">🧬 CONTROL</h2>', unsafe_allow_html=True)
    modalidad = st.radio("Selecciona Disciplina:", ["🏋️ Pesas", "🏃 Running", "🥊 Contacto"])
    st.divider()
    if st.button("RESET SESIÓN"):
        st.session_state['historial_sesion'] = []
        st.rerun()

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
t1, t2, t3, t4, t5 = st.tabs(["⚡ ENTRENAR", "🧠 PLANES", "🏆 RÉCORDS", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR (CORREGIDO) ---
with t1:
    st.markdown(f'<div class="glass-card">MODO: {modalidad}</div>', unsafe_allow_html=True)
    
    with st.form("form_entreno", clear_on_submit=True):
        if modalidad == "🏋️ Pesas":
            c1, c2 = st.columns(2)
            grupo = c1.selectbox("Grupo", list(BIBLIOTECA_GYM.keys()))
            ejer = c2.selectbox("Ejercicio", BIBLIOTECA_GYM[grupo])
            c3, c4 = st.columns(2)
            p = c3.number_input("Peso (kg)", 0, 500, 60)
            r = c4.number_input("Reps", 1, 50, 10)
            if st.form_submit_button("REGISTRAR"):
                st.session_state['historial_sesion'].append({"Fecha": "Hoy", "Ejercicio": ejer, "Dato": f"{p}kg x {r}"})

        elif modalidad == "🏃 Running":
            c1, c2 = st.columns(2)
            km = c1.number_input("Kilómetros", 0.1, 50.0, 5.0)
            tipo_r = c2.selectbox("Periodo", ["Fondo", "Series", "Recuperación"])
            minutos = st.number_input("Minutos Totales", 1, 300, 25)
            # Cálculo de ritmo
            ritmo = minutos / km
            st.info(f"Ritmo: {int(ritmo)}:{int((ritmo%1)*60):02d} min/km")
            if st.form_submit_button("GUARDAR RUN"):
                st.session_state['historial_sesion'].append({"Fecha": "Hoy", "Ejercicio": f"Run {tipo_r}", "Dato": f"{km}km en {minutos}min"})

        elif modalidad == "🥊 Contacto":
            rd = st.slider("Rounds", 1, 15, 3)
            estilo = st.selectbox("Tipo", ["Sparring", "Saco", "Manoplas"])
            if st.form_submit_button("GUARDAR CONTACTO"):
                st.session_state['historial_sesion'].append({"Fecha": "Hoy", "Ejercicio": f"Box/MMA ({estilo})", "Dato": f"{rd} Rounds"})

    if st.session_state['historial_sesion']:
        st.table(pd.DataFrame(st.session_state['historial_sesion']))

# --- TAB 2: PLANES ---
with t2:
    st.subheader("Planes de Entrenamiento")
    if st.button("ESTABLECER ARNOLD SPLIT"):
        st.session_state['plan_activo'] = "Arnold Split"
        st.success("Plan Arnold Activado")

# --- TAB 3: RÉCORDS ---
with t3:
    st.subheader("🥇 Récords Personales")
    for e, v in st.session_state['records_personales'].items():
        st.write(f"**{e}**: {v} kg")

# --- TAB 4: ANALYTICS (EL GRÁFICO) ---
with t4:
    st.subheader("Progreso Visual")
    fig = px.line(df_visual, x="Fecha", y="Valor", color="Ejercicio", markers=True, template="plotly_dark")
    fig.update_traces(line_color='#00d4ff')
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 5: 1RM ---
with t5:
    st.subheader("Calculadora 1RM")
    p_rm = st.number_input("Peso", 1, 500, 100, key="p_rm")
    r_rm = st.number_input("Reps", 1, 12, 5, key="r_rm")
    res_1rm = p_rm * (1 + 0.0333 * r_rm)
    
    st.markdown(f'<div class="rm-display"><h1>{round(res_1rm,1)} kg</h1><p>1RM ESTIMADO</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("90% Fuerza", f"{round(res_1rm*0.9,1)} kg")
    c2.metric("80% Masa", f"{round(res_1rm*0.8,1)} kg")
    c3.metric("70% Resistencia", f"{round(res_1rm*0.7,1)} kg")
