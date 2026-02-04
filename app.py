import streamlit as st
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
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }
    .record-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 128, 255, 0.1));
        border: 1px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center;
    }
    .rm-display {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff; padding: 30px; border-radius: 20px; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. MEMORIA DEL SISTEMA ---
if 'plan_activo' not in st.session_state:
    st.session_state['plan_activo'] = "Arnold Split (Antagonistas)"
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

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown('<h2 style="color:#00d4ff;">🧬 MODALIDAD</h2>', unsafe_allow_html=True)
    especialidad = st.radio("Disciplina:", ["🏋️ Gym/Pesas", "🏃 Running", "🥊 Contacto"])
    st.divider()
    st.markdown("### ⏱️ TIMER")
    segundos = st.number_input("Descanso (s):", 30, 300, 90, 30)
    if st.button("INICIAR"):
        placeholder = st.empty()
        for i in range(segundos, 0, -1):
            placeholder.metric("Descansando...", f"{i}s")
            time.sleep(1)
        st.success("🔥 ¡DALE!")
        st.balloons()

# --- 5. CUERPO PRINCIPAL ---
st.markdown('<h1 class="main-title">MORPHAI</h1>', unsafe_allow_html=True)
tabs = st.tabs(["⚡ ENTRENAR", "🧠 PLANES", "🏆 RÉCORDS", "📊 ANALYTICS", "🧮 1RM"])

# --- TAB 1: ENTRENAR ---
with tabs[0]:
    st.markdown(f'<div class="glass-card"><b>PLAN ACTUAL:</b> {st.session_state["plan_activo"]}</div>', unsafe_allow_html=True)
    with st.form("main_form", clear_on_submit=True):
        if especialidad == "🏋️ Gym/Pesas":
            c1, c2 = st.columns(2)
            grupo = c1.selectbox("Músculo", list(BIBLIOTECA_GYM.keys()))
            ejer = c2.selectbox("Ejercicio", BIBLIOTECA_GYM[grupo])
            c3, c4 = st.columns(2)
            p = c3.number_input("Peso (kg)", 0.0, 500.0, 60.0)
            r = c4.number_input("Reps", 1, 50, 10)
            if st.form_submit_button("REGISTRAR SERIE"):
                if ejer not in st.session_state['records_personales'] or p > st.session_state['records_personales'][ejer]:
                    st.session_state['records_personales'][ejer] = p
                    st.toast(f"🏆 ¡Nuevo récord en {ejer}!")
                st.session_state['historial_sesion'].append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": ejer, "Dato": f"{p}kg x {r}", "Tipo": "Gym"})

        elif especialidad == "🏃 Running":
            d = st.number_input("Km", 0.1, 100.0, 5.0)
            t = st.text_input("HH:MM:SS", "00:25:00")
            if st.form_submit_button("GUARDAR CARRERA"):
                st.session_state['historial_sesion'].append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": "Running", "Dato": f"{d}km en {t}", "Tipo": "Run"})

        elif especialidad == "🥊 Contacto":
            rd = st.slider("Rounds", 1, 15, 3)
            if st.form_submit_button("GUARDAR SESIÓN"):
                st.session_state['historial_sesion'].append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Ejercicio": "Combate", "Dato": f"{rd} rounds", "Tipo": "Combat"})

    if st.session_state['historial_sesion']:
        st.dataframe(pd.DataFrame(st.session_state['historial_sesion']), use_container_width=True)
        if st.button("🚀 FINALIZAR SESIÓN"):
            st.session_state['historial_sesion'] = []
            st.success("Sesión completada.")
            st.rerun()

# --- TAB 2: PLANES ---
with tabs[1]:
    st.subheader("Estrategias de Entrenamiento")
    col_p1, col_p2 = st.columns(2)
    if col_p1.button("ACTIVAR ARNOLD SPLIT"):
        st.session_state['plan_activo'] = "Arnold Split (Antagonistas)"
        st.rerun()
    if col_p2.button("ACTIVAR PUSH/PULL/LEGS"):
        st.session_state['plan_activo'] = "PPL (Frecuencia 2)"
        st.rerun()

# --- TAB 3: RÉCORDS ---
with tabs[2]:
    st.subheader("🥇 Hall of Fame (Tus Marcas)")
    if st.session_state['records_personales']:
        cols = st.columns(3)
        for i, (ejer, peso) in enumerate(st.session_state['records_personales'].items()):
            cols[i % 3].markdown(f"""
            <div class="record-card">
                <small style="color:#00d4ff;">{ejer}</small>
                <h2 style="margin:0;">{peso} kg</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Registra tus marcas en la pestaña de ENTRENAR para que aparezcan aquí.")

# --- TAB 4: ANALYTICS ---
with tabs[3]:
    st.subheader("Análisis de Progreso")
    if not df_global.empty:
        ejer_sel = st.selectbox("Selecciona actividad:", df_global["Ejercicio"].unique())
        fig = px.line(df_global[df_global["Ejercicio"] == ejer_sel], x="Fecha", y="Peso", markers=True, template="plotly_dark")
        fig.update_traces(line_color='#00d4ff')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Los gráficos aparecerán cuando sincronices datos con Google Sheets.")

# --- TAB 5: 1RM ---
with tabs[4]:
    st.subheader("Calculadora de Fuerza Máxima")
    c_rm1, c_rm2 = st.columns(2)
    peso_rm = c_rm1.number_input("Peso (kg)", 1.0, 500.0, 100.0, key="rm_p")
    reps_rm = c_rm2.number_input("Repeticiones", 1, 12, 5, key="rm_r")
    
    one_rm = peso_rm * (1 + 0.0333 * reps_rm)
    
    st.markdown(f"""
    <div class="rm-display">
        <h1 style="color: #00d4ff; margin: 0; font-size: 4rem;">{round(one_rm, 1)} kg</h1>
        <p style="color: #ccc; letter-spacing: 2px;">TU 1RM ESTIMADO</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("### 📊 Porcentajes de Carga")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("90% (Fuerza Pura)", f"{round(one_rm*0.9, 1)} kg")
    col_b.metric("80% (Hipertrofia)", f"{round(one_rm*0.8, 1)} kg")
    col_c.metric("70% (Resistencia)", f"{round(one_rm*0.7, 1)} kg")
