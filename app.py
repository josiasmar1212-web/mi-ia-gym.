import streamlit as st
import pandas as pd
from datetime import datetime
import time
import plotly.express as px

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="MorphAI Social Pro v7", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    .stApp { background-color: #050505; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00ff88; text-align: center; font-size: 3.5rem; letter-spacing: 12px; margin-bottom: 0px; text-shadow: 0px 0px 20px rgba(0, 255, 136, 0.4); }
    .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin-bottom: 20px; }
    .timer-display { font-size: 6rem; text-align: center; font-family: 'Orbitron'; border-radius: 20px; padding: 30px; border: 4px solid #ff4b4b; color: #ff4b4b; margin: 20px 0; }
    .work-mode { border-color: #00ff88 !important; color: #00ff88 !important; box-shadow: 0px 0px 40px rgba(0, 255, 136, 0.4); }
    .routine-box { background: rgba(0, 255, 136, 0.05); border-left: 5px solid #00ff88; padding: 20px; margin: 15px 0; border-radius: 10px; }
    .quote-style { font-style: italic; text-align: center; color: #00ff88; font-size: 1.2rem; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS ---
if 'historial_sesion' not in st.session_state:
    st.session_state['historial_sesion'] = []
if 'records_social' not in st.session_state:
    st.session_state['records_social'] = {}
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "Arnold Split"

BIBLIOTECA_GYM = {
    "Pecho": ["Press Banca Plano", "Press Inclinado", "Aperturas Polea", "Fondos"],
    "Espalda": ["Dominadas", "Remo con Barra", "Jalón al Pecho", "Peso Muerto"],
    "Piernas": ["Sentadilla", "Prensa 45°", "Peso Muerto Rumano", "Sentadilla Búlgara"],
    "Hombros": ["Press Militar", "Elevaciones Laterales", "Face Pulls", "Press Arnold"],
    "Brazos": ["Curl Barra Z", "Press Francés", "Martillo", "Tríceps Polea"]
}

EJER_EXPLOSIVOS = {
    "Potencia Inferior": ["Saltos al Cajón", "Broad Jumps", "Sentadilla Explosiva", "Kettlebell Swings"],
    "Impacto Superior": ["Flexiones Pliométricas", "Lanzamiento Balón Pared", "Landmine Press"],
    "Rotación Combat": ["Woodchoppers", "Rotación Landmine", "Lanzamiento Lateral"]
}

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown('<h1 style="color:#00ff88; font-family:Orbitron;">PERFIL</h1>', unsafe_allow_html=True)
    usuario = st.text_input("Nombre del Atleta:", value="Atleta_Alpha").strip()
    st.divider()
    modalidad = st.radio("MODALIDAD ACTIVA:", ["🏋️ Pesas Pro", "🏃 Running Tech", "🥊 Contacto & Power"])
    st.divider()
    if st.button("🗑️ REINICIAR SESIÓN"):
        st.session_state['historial_sesion'] = []
        st.rerun()

# --- 4. CABECERA ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
frases = [
    "La disciplina es el puente entre tus metas y tus logros.",
    "El dolor es temporal, el orgullo de haberlo logrado es para siempre.",
    "No te detengas cuando estés cansado, detente cuando hayas terminado.",
    "Tu mente es tu músculo más fuerte. Entrénala bien."
]
st.markdown(f'<p class="quote-style">"{frases[int(time.time()) % len(frases)]}"</p>', unsafe_allow_html=True)

tabs = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "🏆 RÉCORDS", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR ---
with tabs[0]:
    if modalidad == "🏋️ Pesas Pro":
        with st.form("gym_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            grupo = col1.selectbox("Grupo Muscular", list(BIBLIOTECA_GYM.keys()))
            # FILTRADO DINÁMICO: Solo muestra ejercicios del grupo seleccionado
            ejer = col2.selectbox("Ejercicio Seleccionado", BIBLIOTECA_GYM[grupo])
            c3, c4 = st.columns(2)
            p = c3.number_input("Peso (kg)", 0.0, 500.0, 60.0)
            r = c4.number_input("Reps", 1, 50, 10)
            if st.form_submit_button("REGISTRAR SERIE"):
                st.session_state['historial_sesion'].append({"Usuario": usuario, "Fecha": datetime.now().strftime("%d/%m %H:%M"), "Actividad": ejer, "Dato": f"{p}kg x {r}", "Valor": p})

    elif modalidad == "🏃 Running Tech":
        with st.form("run_form", clear_on_submit=True):
            km = st.number_input("Kilómetros", 0.1, 50.0, 5.0)
            minutos = st.number_input("Minutos Totales", 1, 300, 25)
            per = st.selectbox("Periodo", ["Base", "Series", "Larga"])
            if st.form_submit_button("GUARDAR CARRERA"):
                ritmo = minutos / km
                st.session_state['historial_sesion'].append({"Usuario": usuario, "Fecha": datetime.now().strftime("%d/%m"), "Actividad": f"Running {per}", "Dato": f"{km}km ({int(ritmo)}:{int((ritmo%1)*60):02d} min/km)", "Valor": km})

    elif modalidad == "🥊 Contacto & Power":
        c1, c2, c3 = st.columns(3)
        n_rounds = c1.number_input("Rounds", 1, 15, 3)
        t_work = c2.number_input("Min Round", 1, 5, 3)
        t_rest = c3.number_input("Seg Descanso", 10, 60, 30)
        if st.button("🥊 INICIAR TEMPORIZADOR VERDE"):
            ph = st.empty()
            for r in range(1, n_rounds + 1):
                for t in range(t_work * 60, 0, -1):
                    ph.markdown(f'<div class="timer-display work-mode">ROUND {r}<br>{t//60:02d}:{t%60:02d}</div>', unsafe_allow_html=True)
                    time.sleep(1)
                if r < n_rounds:
                    for t in range(t_rest, 0, -1):
                        ph.markdown(f'<div class="timer-display">DESCANSO<br>00:{t:02d}</div>', unsafe_allow_html=True)
                        time.sleep(1)
            ph.success("¡ENTRENAMIENTO TERMINADO!")

    if st.session_state['historial_sesion']:
        st.markdown("### 📋 Tabla de Progreso (Sesión)")
        st.table(pd.DataFrame(st.session_state['historial_sesion']))

# --- TAB 2: PLANIFICAR ---
with tabs[1]:
    obj = st.selectbox("Objetivo IA:", ["Hipertrofia", "Fuerza", "Potencia Contacto"])
    if st.button("GENERAR RUTINA"):
        plan = {"Hipertrofia": "4x10 (90s descanso)", "Fuerza": "5x5 (3min descanso)", "Potencia Contacto": "3x6 Explosivo"}
        st.markdown(f'<div class="routine-box"><b>PLAN:</b> {plan[obj]}<br>Sigue el ritmo y no falles.</div>', unsafe_allow_html=True)

# --- TAB 4: ANALYTICS ---
with tabs[3]:
    if st.session_state['historial_sesion']:
        df = pd.DataFrame(st.session_state['historial_sesion'])
        fig = px.line(df[df["Usuario"] == usuario], x="Fecha", y="Valor", color="Actividad", template="plotly_dark")
        fig.update_traces(line_color='#00ff88')
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 5: 1RM ---
with tabs[4]:
    p1 = st.number_input("Peso", 1, 500, 100)
    r1 = st.number_input("Reps", 1, 12, 5)
    st.metric("1RM Estimado", f"{round(p1 * (1 + 0.0333 * r1), 1)} kg")
