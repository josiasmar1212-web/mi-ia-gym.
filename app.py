himport streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import time
import plotly.express as px
import random

# --- 1. CONFIGURACIÓN Y ESTÉTICA ---
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
    .record-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 128, 255, 0.1));
        border: 1px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. MEMORIA DEL SISTEMA ---
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "Arnold Split (Predeterminado)"
if 'historial_sesion' not in st.session_state:
    st.session_state['historial_sesion'] = []
if 'records_personales' not in st.session_state:
    st.session_state['records_personales'] = {}

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
    df_global = pd.DataFrame(columns=["Fecha", "Ejercicio", "Peso", "Reps", "Tipo"])

# --- 4. SIDEBAR (CONTROLES) ---
with st.sidebar:
    st.markdown('<h2 style="color:#00d4ff;">🧬 MODALIDAD</h2>', unsafe_allow_html=True)
    especialidad = st.radio("Disciplina:", ["🏋️ Gym/Pesas", "🏃 Running", "🥊 Contacto"])
    
    st.divider()
    st.markdown("### ⏱️ REST TIMER")
    segundos = st.number_input("Segundos:", 30, 300, 90, 30)
    if st.button("INICIAR DESCANSO"):
        placeholder = st.empty()
        for i in range(segundos, 0, -1):
            placeholder.metric("Descansando...", f"{i}s")
            time.sleep(1)
        st.success("🔥 ¡VUELVE A LA CARGA!")
        st.balloons()

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
tabs = st.tabs(["⚡ ENTRENAR", "🧠 PLANIFICAR", "🏆 RÉCORDS", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR ---
with tabs[0]:
    st.info(f"Modo: {especialidad} | Plan: {st.session_state['plan_activo']}")
    
    with st.form("registro_form", clear_on_submit=True):
        if especialidad == "🏋️ Gym/Pesas":
            c1, c2 = st.columns(2)
            grupo = c1.selectbox("Músculo", list(BIBLIOTECA_GYM.keys()))
            ejer = c2.selectbox("Ejercicio", BIBLIOTECA_GYM[grupo])
            c3, c4 = st.columns(2)
            p = c3.number_input("Peso (kg)", 0.0, 500.0, 60.0)
            r = c4.number_input("Reps", 1, 50, 10)
            submit = st.form_submit_button("REGISTRAR SERIE")
            
            if submit:
                # Lógica de Récords
                if ejer not in st.session_state['records_personales'] or p > st.session_state['records_personales'][ejer]:
                    st.session_state['records_personales'][ejer] = p
                    st.balloons()
                    st.success(f"🎊 ¡NUEVO RÉCORD PERSONAL EN {ejer.upper()}!")
                
                st.session_state['historial_sesion'].append({
                    "Fecha": datetime.now().strftime("%d/%m/%Y"),
                    "Ejercicio": ejer, "Dato": f"{p}kg x {r}", "Tipo": "Gym"
                })

        elif especialidad == "🏃 Running":
            d = st.number_input("Distancia (km)", 0.1, 100.0, 5.0)
            t = st.text_input("Tiempo", "00:25:00")
            if st.form_submit_button("REGISTRAR CARRERA"):
                st.session_state['historial_sesion'].append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": "Running", "Dato": f"{d}km en {t}", "Tipo": "Run"})

        elif especialidad == "🥊 Contacto":
            rd = st.slider("Rounds", 1, 15, 3)
            int_c = st.select_slider("Intensidad", options=["Baja", "Media", "Alta", "Guerra"])
            if st.form_submit_button("REGISTRAR COMBATE"):
                st.session_state['historial_sesion'].append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": "Combate", "Dato": f"{rd} rounds ({int_c})", "Tipo": "Combat"})

    if st.session_state['historial_sesion']:
        st.dataframe(pd.DataFrame(st.session_state['historial_sesion']), use_container_width=True)
        if st.button("🚀 FINALIZAR Y GUARDAR"):
            st.session_state['historial_sesion'] = []
            st.success("Entrenamiento guardado.")
            st.rerun()

# --- TAB 2: RÉCORDS (HALL OF FAME) ---
with tabs[2]:
    st.subheader("🥇 Hall of Fame")
    if st.session_state['records_personales']:
        cols = st.columns(len(st.session_state['records_personales']))
        for i, (ejer, peso) in enumerate(st.session_state['records_personales'].items()):
            cols[i % 3].markdown(f"""
            <div class="record-card">
                <small style="color:#00d4ff;">{ejer}</small>
                <h2 style="margin:0;">{peso} kg</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Registra tus series para empezar a romper récords.")

# --- TAB 4: ANALYTICS ---
with tabs[3]:
    st.subheader("Análisis de Sobrecarga Progresiva")
    if not df_global.empty:
        ejer_sel = st.selectbox("Ejercicio:", df_global["Ejercicio"].unique())
        fig = px.line(df_global[df_global["Ejercicio"] == ejer_sel], x="Fecha", y="Peso", markers=True, template="plotly_dark")
        fig.update_traces(line_color='#00d4ff')
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 5: 1RM ---
with tabs[4]:
    st.subheader("Calculadora 1RM")
    p_rm = st.number_input("Peso (kg)", 1, 500, 100)
    r_rm = st.number_input("Reps", 1, 12, 5)
    calc_1rm = p_rm * (1 + 0.0333 * r_rm)
    st.metric("TU 1RM ESTIMADO", f"{round(calc_1rm, 1)} kg")
