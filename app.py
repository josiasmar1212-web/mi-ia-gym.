import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN Y ESTÉTICA DE VANGUARDIA ---
st.set_page_config(page_title="MorphAI Social Pro v8.5", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00ff88; text-align: center; font-size: 3.5rem; letter-spacing: 12px; text-shadow: 0px 0px 20px rgba(0, 255, 136, 0.4); margin-bottom:0px; }
    .quote-style { font-style: italic; text-align: center; color: #00ff88; font-size: 1.1rem; opacity: 0.8; margin-bottom: 30px; }
    .timer-display { font-size: 6rem; text-align: center; font-family: 'Orbitron'; border-radius: 25px; padding: 35px; border: 4px solid #ff4b4b; color: #ff4b4b; background: rgba(255, 75, 75, 0.05); }
    .work-mode { border-color: #00ff88 !important; color: #00ff88 !important; box-shadow: 0px 0px 40px rgba(0, 255, 136, 0.4); background: rgba(0, 255, 136, 0.05); }
    .rm-display { background: rgba(0, 255, 136, 0.1); border: 2px solid #00ff88; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; }
    .rm-val { font-family: 'Orbitron', sans-serif; color: #00ff88; font-size: 5rem; margin: 0; text-shadow: 0px 0px 15px rgba(0, 255, 136, 0.5); }
    .routine-box { background: rgba(255, 255, 255, 0.03); border-left: 5px solid #00ff88; padding: 20px; border-radius: 10px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# --- 2. BIBLIOTECAS DE ALTO RENDIMIENTO ---
if 'historial' not in st.session_state: st.session_state['historial'] = []

DATA_MASTER = {
    "🏋️ PESAS": {
        "Pecho": ["Press Banca Plano", "Press Inclinado", "Aperturas Polea", "Fondos Lastrados"],
        "Espalda": ["Dominadas Pro", "Remo Pendlay", "Jalón al Pecho", "Peso Muerto Convencional"],
        "Piernas": ["Sentadilla High Bar", "Prensa 45°", "Peso Muerto Rumano", "Sentadilla Búlgara"],
        "Hombros/Brazos": ["Press Militar", "Elevaciones Laterales", "Curl Barra Z", "Press Francés"]
    },
    "🥊 CONTACTO": {
        "Potencia": ["Saltos al Cajón", "Broad Jumps", "Sentadilla Explosiva", "Kettlebell Swings"],
        "Impacto": ["Flexiones Pliométricas", "Lanzamiento Balón Pared", "Landmine Punch"],
        "Core Combat": ["Woodchoppers", "Rotación Landmine", "Russian Twist Pesado"]
    }
}

# --- 3. NAVEGACIÓN ---
with st.sidebar:
    st.markdown('<h1 style="color:#00ff88; font-family:Orbitron;">SISTEMA</h1>', unsafe_allow_html=True)
    usuario = st.text_input("Atleta:", value="Atleta_Alpha").upper()
    modalidad = st.radio("MODALIDAD:", ["🏋️ Pesas", "🏃 Running", "🥊 Contacto"])
    if st.button("🚨 RESET"):
        st.session_state['historial'] = []
        st.rerun()

st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
st.markdown('<p class="quote-style">"Tu único límite es tu mente. Rómpelo."</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR ---
with tabs[0]:
    if modalidad == "🏋️ Pesas":
        with st.form("f_gym", clear_on_submit=True):
            c1, c2 = st.columns(2)
            grupo = c1.selectbox("Músculo", list(DATA_MASTER["🏋️ PESAS"].keys()))
            ejer = c2.selectbox("Ejercicio", DATA_MASTER["🏋️ PESAS"][grupo])
            c3, c4, c5 = st.columns(3)
            p = c3.number_input("Peso (kg)", 0.0, 500.0, 60.0)
            r = c4.number_input("Reps", 1, 50, 10)
            rpe = c5.slider("RPE (1-10)", 1, 10, 8)
            if st.form_submit_button("GUARDAR SET"):
                st.session_state['historial'].append({"Fecha": datetime.now().strftime("%H:%M"), "Actividad": ejer, "Dato": f"{p}kg x {r} (RPE {rpe})", "Valor": p*r})

    elif modalidad == "🏃 Running":
        with st.form("f_run", clear_on_submit=True):
            c1, c2 = st.columns(2)
            dist = c1.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            bpm = c2.number_input("BPM Medio", 60, 220, 145)
            mins = st.number_input("Minutos Totales", 1, 500, 25)
            if st.form_submit_button("GUARDAR RUN"):
                pace = mins / dist
                st.session_state['historial'].append({"Fecha": datetime.now().strftime("%d/%m"), "Actividad": "Running", "Dato": f"{dist}km @ {int(pace)}:{int((pace%1)*60):02d} min/km", "Valor": dist})

    elif modalidad == "🥊 Contacto":
        st.subheader("⏱️ Temporizador Rounds (Verde)")
        tc1, tc2, tc3 = st.columns(3)
        rds = tc1.number_input("Rounds", 1, 15, 3)
        tw = tc2.number_input("Trabajo (min)", 1, 5, 3)
        tr = tc3.number_input("Descanso (seg)", 10, 60, 30)
        if st.button("🔔 INICIAR COMBATE"):
            ph = st.empty()
            for r in range(1, rds + 1):
                for t in range(tw * 60, 0, -1):
                    ph.markdown(f'<div class="timer-display work-mode">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                if r < rds:
                    for t in range(tr, 0, -1):
                        ph.markdown(f'<div class="timer-display">DESCANSAR<br>00:{t:02d}</div>', unsafe_allow_html=True)
                        time.sleep(1)
            ph.success("SESIÓN COMPLETADA")

    if st.session_state['historial']:
        st.table(pd.DataFrame(st.session_state['historial']).tail(5))

# --- TAB 2: PLANIFICAR ---
with tabs[1]:
    st.subheader("🧠 Generador de Rutinas")
    objetivo = st.selectbox("Meta", ["Hipertrofia", "Fuerza", "Potencia"])
    if st.button("GENERAR"):
        config = {"Hipertrofia": "4x10-12 (90s descanso)", "Fuerza": "5x3-5 (3min descanso)", "Potencia": "3x6 Explosivo"}
        st.markdown(f'<div class="routine-box"><b>PLAN:</b> {config[objetivo]}<br>Series, repeticiones y descansos optimizados.</div>', unsafe_allow_html=True)

# --- TAB 4: 1RM (EL PANEL NEÓN QUE QUERÍAS) ---
with tabs[3]:
    st.markdown('<div class="rm-display">', unsafe_allow_html=True)
    st.markdown('<p style="color:#00ff88; letter-spacing:5px;">ESTIMACIÓN FUERZA MÁXIMA</p>', unsafe_allow_html=True)
    c_rm1, c_rm2 = st.columns(2)
    p_in = c_rm1.number_input("Peso (kg)", 1.0, 500.0, 100.0)
    r_in = c_rm2.number_input("Reps", 1, 12, 5)
    rm = p_in / (1.0278 - (0.0278 * r_in))
    st.markdown(f'<h1 class="rm-val">{round(rm, 1)} KG</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("📊 Estadísticas de Carga")
    z1, z2, z3 = st.columns(3)
    z1.metric("FUERZA (90%)", f"{round(rm*0.9, 1)} kg")
    z2.metric("MASA (80%)", f"{round(rm*0.8, 1)} kg")
    z3.metric("VELOCIDAD (70%)", f"{round(rm*0.7, 1)} kg")

# --- TAB 3: ANALYTICS ---
with tabs[2]:
    if st.session_state['historial']:
        df = pd.DataFrame(st.session_state['historial'])
        fig = px.line(df, x="Fecha", y="Valor", color="Actividad", template="plotly_dark", title="Progreso de Volumen")
        fig.update_traces(line_color='#00ff88')
        st.plotly_chart(fig, use_container_width=True)
